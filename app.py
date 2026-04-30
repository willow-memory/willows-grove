#!/usr/bin/env python3
"""
app.py — Willow Grove (Textual dashboard).
b17: WGRV1  ΔΣ=42

Run: python3 app.py
"""
import json
import logging
import os
from pathlib import Path

logging.basicConfig(
    filename=Path.home() / ".willow" / "grove_error.log",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logging.captureWarnings(True)

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.css.query import NoMatches
from textual.widgets import Footer, Label, Rule, Static

from panes.chat      import ChatPane, ChannelList, sender_color
from widgets.projects_nav    import ProjectsNav
from widgets.knowledge_nav  import KnowledgeAtomSelected, KnowledgeNav
from widgets.providers_nav  import ProviderRowSelected, ProvidersNav
from widgets.health_nav     import HealthNav
from widgets.settings_nav   import SettingsNav
from widgets.help_nav       import HelpSectionSelected, HelpNav
from panes.settings         import SettingsPane
from panes.help             import HelpPane
from panes.tasks     import TasksPane, fetch_backfill_progress, fetch_tasks
from panes.agents    import AgentsPane
from panes.routing   import RoutingPane
from panes.knowledge import KnowledgePane
from panes.providers import ProvidersPane
from panes.skills    import SkillsPane
from panes.health    import HealthPane
from panes.logs      import LogsPane
from panes.home      import DeskPane, HomeGrid, ProjectsGrid

from widgets.nav_bar        import NavBar, NavChanged, NAV_TARGETS
from widgets.hero_scene     import HeroScene
from widgets.chat_strip     import ChatStrip
from widgets.thought_stream import ThoughtStream, SessionStats
from widgets.card_grid      import CardActivated

import grove_reader

WILLOW_ROOT = Path(os.environ.get("WILLOW_ROOT", Path.home() / "github" / "willow-1.9"))


def _pg_ok() -> bool:
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname=os.environ.get("WILLOW_PG_DB", "willow_19"),
            user=os.environ.get("WILLOW_PG_USER", os.environ.get("USER", "")),
            connect_timeout=2,
        )
        conn.close()
        return True
    except Exception:
        return False


class VitalsBar(Static):
    def on_mount(self) -> None:
        self.set_interval(15, self._refresh)
        self._refresh()

    def _refresh(self) -> None:
        pg    = "[green]pg:up[/]" if _pg_ok() else "[red]pg:down[/]"
        bp    = fetch_backfill_progress()
        if bp and bp.get("table") != "done":
            pct   = bp.get("pct", 0)
            embed = f"embed [yellow]{pct:.1f}%[/]"
        else:
            embed = "embed [green]done[/]"
        model = os.environ.get("WILLOW_MODEL", "claude-sonnet-4-6")
        text  = f"[dim]{model}[/]  {pg}  {embed}"
        self.update(text)
        try:
            self.app.query_one(NavBar).set_vitals(text)
        except NoMatches:
            pass


class GroveRightPanel(Container):
    def compose(self) -> ComposeResult:
        yield Label("TASKS", id="rp-tasks-label")
        yield Static("", id="rp-task-counts")
        yield Rule()
        yield Label("AGENTS", id="rp-agents-label")
        yield Static("", id="rp-agents-list")
        yield Rule()
        yield Label("THOUGHTS", id="rp-thoughts-label")
        yield ThoughtStream(id="rp-thought-stream")
        yield SessionStats(id="rp-session-stats")

    def on_mount(self) -> None:
        self.set_interval(10, self._refresh)
        self._refresh()

    def _refresh(self) -> None:
        data = fetch_tasks()
        self._safe_update(
            "#rp-task-counts",
            f"[yellow]{data['running']}[/] running\n"
            f"[dim]{data['pending']}[/] pending\n"
            f"[green]{data['done']}[/] done",
        )
        lines = []
        try:
            for a in grove_reader.grove_agents():
                sender   = a["sender"]
                age_secs = a.get("age_secs", 9999)
                dot = "[green]●[/]" if age_secs < 120 else "[yellow]●[/]" if age_secs < 900 else "[dim]●[/]"
                color = sender_color(sender)
                lines.append(f"{dot} [{color}]{sender}[/]")
        except Exception:
            pass
        self._safe_update("#rp-agents-list", "\n".join(lines) or "[dim]no agents[/]")

    def _safe_update(self, selector: str, text: str) -> None:
        try:
            self.query_one(selector, Static).update(text)
        except NoMatches:
            pass


class ContextPanel(Vertical):
    """Left column — swaps content based on active nav target."""

    def compose(self) -> ComposeResult:
        yield DeskPane(id="ctx-home")
        yield ChannelList(id="ctx-chat")
        yield ProjectsNav(id="ctx-projects")
        yield KnowledgeNav(id="ctx-knowledge")
        yield ProvidersNav(id="ctx-providers")
        yield HealthNav(id="ctx-health")
        yield SettingsNav(id="ctx-settings")
        yield HelpNav(id="ctx-help")

    def on_mount(self) -> None:
        self._show_target("home")

    def on_nav_changed(self, event: NavChanged) -> None:
        self._show_target(event.target)

    def _show_target(self, target: str) -> None:
        ctx_map = {
            "home":      "#ctx-home",
            "chat":      "#ctx-chat",
            "projects":  "#ctx-projects",
            "knowledge": "#ctx-knowledge",
            "providers": "#ctx-providers",
            "health":    "#ctx-health",
            "settings":  "#ctx-settings",
            "help":      "#ctx-help",
        }
        for widget_id in ctx_map.values():
            try:
                self.query_one(widget_id).display = False
            except NoMatches:
                pass
        active_id = ctx_map.get(target)
        if active_id:
            try:
                self.query_one(active_id).display = True
            except NoMatches:
                pass


# Content panes indexed by nav target
_CONTENT_PANES: dict[str, str] = {
    "home":      "#pane-home",
    "chat":      "#pane-chat",
    "projects":  "#pane-projects",
    "knowledge": "#pane-knowledge",
    "providers": "#pane-providers",
    "health":    "#pane-health",
    "settings":  "#pane-settings",
    "help":      "#pane-help",
}

# Internal panes reachable via Projects — not in top nav
_INTERNAL_PANES: list[str] = [
    "#pane-tasks", "#pane-agents", "#pane-routing",
    "#pane-skills", "#pane-logs",
]


class WillowGrove(App):
    CSS = """
    Screen { background: #0d1117; }

    Footer { background: #161b22; }

    #vitals-source { display: none; }

    #main-area { height: 1fr; }

    ContextPanel {
        width: 26;
        background: #161b22;
        border-right: solid #30363d;
    }

    #content-area {
        width: 1fr;
        height: 1fr;
    }

    GroveRightPanel {
        width: 30;
        background: #161b22;
        border-left: solid #30363d;
        padding: 0 1;
    }

    GroveRightPanel #rp-tasks-label,
    GroveRightPanel #rp-agents-label,
    GroveRightPanel #rp-thoughts-label {
        color: #58a6ff;
        text-style: bold;
        padding: 0 0 1 0;
    }

    GroveRightPanel #rp-task-counts,
    GroveRightPanel #rp-agents-list {
        padding: 0 0 0 1;
        color: #8b949e;
    }

    GroveRightPanel #rp-agents-list { height: auto; }

    Rule { margin: 1 0; color: #30363d; }

    WillowHero {
        height: 8;
        content-align: center middle;
        color: #3fb950;
        text-style: bold;
    }

    #pane-settings, #pane-help {
        padding: 2;
        color: #8b949e;
    }

    DataTable {
        height: 1fr;
        margin: 0 2;
    }

    #skill-detail {
        height: 12;
        margin: 1 2;
        border: round #30363d;
        padding: 1;
        color: #8b949e;
    }

    Log {
        margin: 0 2;
        height: 1fr;
        border: round #30363d;
    }

    ChatPane #channel-sidebar {
        width: 26;
        background: #161b22;
        border-right: solid #30363d;
    }

    ChatPane #sidebar-label {
        padding: 1 1 0 1;
        color: #8b949e;
        text-style: bold;
    }

    ChatPane #channel-title {
        background: #161b22;
        color: #58a6ff;
        border-bottom: solid #30363d;
    }

    ChatPane #msg-log {
        height: 1fr;
        padding: 1 2;
    }

    StatusRow {
        padding: 0 4;
        height: 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit",            "Quit"),
        Binding("r", "refresh",         "Refresh"),
        Binding("1", "nav('home')",      "Home",      show=False),
        Binding("2", "nav('chat')",      "Chat",      show=False),
        Binding("3", "nav('projects')",  "Projects",  show=False),
        Binding("4", "nav('knowledge')", "Knowledge", show=False),
        Binding("5", "nav('providers')", "Providers", show=False),
        Binding("6", "nav('health')",    "Health",    show=False),
        Binding("7", "nav('settings')",  "Settings",  show=False),
        Binding("8", "nav('help')",      "Help",      show=False),
    ]

    TITLE     = "Willow Grove"
    SUB_TITLE = f"local-first AI stack — {WILLOW_ROOT}"

    def compose(self) -> ComposeResult:
        yield NavBar(id="nav-bar")
        yield HeroScene(id="hero-scene")
        with Horizontal(id="main-area"):
            yield ContextPanel(id="context-panel")
            with Vertical(id="content-area"):
                yield HomeGrid(id="pane-home")
                yield ChatPane(id="pane-chat")
                yield ProjectsGrid(id="pane-projects")
                yield KnowledgePane(id="pane-knowledge")
                yield ProvidersPane(id="pane-providers")
                yield HealthPane(id="pane-health")
                yield SettingsPane(id="pane-settings")
                yield HelpPane(id="pane-help")
                # internal panes — reachable via Projects, not top nav
                yield TasksPane(id="pane-tasks")
                yield AgentsPane(id="pane-agents")
                yield RoutingPane(id="pane-routing")
                yield SkillsPane(id="pane-skills")
                yield LogsPane(id="pane-logs")
            yield GroveRightPanel(id="right-panel")
        yield ChatStrip(id="chat-strip")
        yield VitalsBar(id="vitals-source")
        yield Footer()

    def on_mount(self) -> None:
        self._hide_all_content_panes()
        self._show_content_pane("home")
        self._do_refresh()
        self.set_interval(30, self._do_refresh)

    def _hide_all_content_panes(self) -> None:
        for pane_id in list(_CONTENT_PANES.values()) + _INTERNAL_PANES:
            try:
                self.query_one(pane_id).display = False
            except NoMatches:
                pass

    def _show_content_pane(self, target: str) -> None:
        pane_id = _CONTENT_PANES.get(target)
        if pane_id:
            try:
                self.query_one(pane_id).display = True
            except NoMatches:
                pass

    def on_nav_changed(self, event: NavChanged) -> None:
        self._hide_all_content_panes()
        self._show_content_pane(event.target)

    def _do_refresh(self) -> None:
        for pane_id, pane_cls in [
            ("#pane-providers", ProvidersPane),
            ("#pane-skills",    SkillsPane),
            ("#pane-logs",      LogsPane),
        ]:
            try:
                self.query_one(pane_id, pane_cls).refresh_data()
            except NoMatches:
                pass

    def _show_internal_pane(self, pane_id: str) -> None:
        """Hide all content + internal panes, then show the requested internal pane."""
        self._hide_all_content_panes()
        try:
            self.query_one(pane_id).display = True
        except NoMatches:
            pass

    def on_knowledge_atom_selected(self, event: KnowledgeAtomSelected) -> None:
        try:
            self.query_one(KnowledgePane).display_atom(event.atom_id)
        except NoMatches:
            pass

    def on_provider_row_selected(self, event: ProviderRowSelected) -> None:
        try:
            self.query_one(ProvidersPane).select_provider(event.name)
        except NoMatches:
            pass

    def on_help_section_selected(self, event: HelpSectionSelected) -> None:
        try:
            self.query_one(HelpPane).jump_to_section(event.section)
        except NoMatches:
            pass

    def on_card_activated(self, event: CardActivated) -> None:
        target = event.nav_target
        if not target:
            return
        if target.startswith("#"):
            self._show_internal_pane(target)
        else:
            self.action_nav(target)

    def action_refresh(self) -> None:
        self._do_refresh()
        try:
            self.query_one(GroveRightPanel)._refresh()
        except NoMatches:
            pass
        self.notify("Refreshed")

    def action_nav(self, target: str) -> None:
        try:
            self.query_one(NavBar).highlight(target)
        except NoMatches:
            pass
        self.post_message(NavChanged(target))


if __name__ == "__main__":
    WillowGrove().run()
