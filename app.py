#!/usr/bin/env python3
"""
app.py — Willow Grove (Textual dashboard).
b17: WGRV1  ΔΣ=42

Run: python3 app.py
"""
import os
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Footer, Header, Label, Rule, Static, TabbedContent, TabPane

from panes.overview  import OverviewPane
from panes.chat      import ChatPane, sender_color
from panes.tasks     import TasksPane, fetch_backfill_progress, fetch_tasks
from panes.agents    import AgentsPane
from panes.routing   import RoutingPane
from panes.knowledge import KnowledgePane
from panes.providers import ProvidersPane
from panes.skills    import SkillsPane
from panes.health    import HealthPane
from panes.logs      import LogsPane
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
            embed = f"  embed [yellow]{pct:.1f}%[/]"
        else:
            embed = "  embed [green]done[/]"
        model = os.environ.get("WILLOW_MODEL", "claude-sonnet-4-6")
        self.update(f" [dim]model:[/] {model}  {pg}{embed}")


class GroveRightPanel(Container):
    def compose(self) -> ComposeResult:
        yield Label("TASKS", id="rp-tasks-label")
        yield Static("", id="rp-task-counts")
        yield Rule()
        yield Label("AGENTS", id="rp-agents-label")
        yield Static("", id="rp-agents-list")

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
        except Exception:
            pass


class WillowGrove(App):
    CSS = """
    Screen { background: #0d1117; }

    Header {
        background: #161b22;
        color: #58a6ff;
        text-style: bold;
    }
    Footer { background: #161b22; }

    VitalsBar {
        height: 1;
        background: #161b22;
        border-bottom: solid #30363d;
        padding: 0 1;
        color: #8b949e;
    }

    #main-area { height: 1fr; }

    #tabs-area {
        width: 1fr;
        height: 1fr;
    }

    TabbedContent { height: 1fr; }
    TabPane       { height: 1fr; padding: 0; }

    GroveRightPanel {
        width: 30;
        background: #161b22;
        border-left: solid #30363d;
        padding: 1 1;
    }

    GroveRightPanel #rp-tasks-label {
        color: #58a6ff;
        text-style: bold;
        padding: 0 0 1 0;
    }

    GroveRightPanel #rp-task-counts {
        padding: 0 0 0 1;
        color: #8b949e;
    }

    GroveRightPanel #rp-agents-label {
        color: #58a6ff;
        text-style: bold;
        padding: 0 0 1 0;
    }

    GroveRightPanel #rp-agents-list {
        padding: 0 0 0 1;
        color: #8b949e;
        height: 1fr;
    }

    Rule { margin: 1 0; color: #30363d; }

    WillowHero {
        height: 8;
        content-align: center middle;
        color: #3fb950;
        text-style: bold;
    }

    #overview-title, #sysinfo-title, #tasks-title, #agents-title,
    #routing-title, #kb-title, #prov-title,
    #skills-title, #health-title, #logs-title {
        color: #58a6ff;
        padding: 1 2;
        text-style: bold;
    }

    StatusRow {
        padding: 0 4;
        height: 1;
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
    """

    BINDINGS = [
        Binding("q", "quit",    "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("1", "switch_tab('tab-overview')",  "Overview",  show=False),
        Binding("2", "switch_tab('tab-chat')",      "Chat",      show=False),
        Binding("3", "switch_tab('tab-tasks')",     "Tasks",     show=False),
        Binding("4", "switch_tab('tab-agents')",    "Agents",    show=False),
        Binding("5", "switch_tab('tab-routing')",   "Routing",   show=False),
        Binding("6", "switch_tab('tab-knowledge')", "Knowledge", show=False),
        Binding("7", "switch_tab('tab-providers')", "Providers", show=False),
        Binding("8", "switch_tab('tab-skills')",    "Skills",    show=False),
        Binding("9", "switch_tab('tab-health')",    "Health",    show=False),
        Binding("0", "switch_tab('tab-logs')",      "Logs",      show=False),
    ]

    TITLE     = "Willow Grove"
    SUB_TITLE = f"local-first AI stack — {WILLOW_ROOT}"

    def compose(self) -> ComposeResult:
        yield Header()
        yield VitalsBar()
        with Horizontal(id="main-area"):
            with Vertical(id="tabs-area"):
                with TabbedContent():
                    with TabPane("Overview",  id="tab-overview"):
                        yield OverviewPane(id="overview-pane")
                    with TabPane("Chat",      id="tab-chat"):
                        yield ChatPane(id="chat-pane")
                    with TabPane("Tasks",     id="tab-tasks"):
                        yield TasksPane(id="tasks-pane")
                    with TabPane("Agents",    id="tab-agents"):
                        yield AgentsPane(id="agents-pane")
                    with TabPane("Routing",   id="tab-routing"):
                        yield RoutingPane(id="routing-pane")
                    with TabPane("Knowledge", id="tab-knowledge"):
                        yield KnowledgePane(id="knowledge-pane")
                    with TabPane("Providers", id="tab-providers"):
                        yield ProvidersPane(id="providers-pane")
                    with TabPane("Skills",    id="tab-skills"):
                        yield SkillsPane(id="skills-pane")
                    with TabPane("Health",    id="tab-health"):
                        yield HealthPane(id="health-pane")
                    with TabPane("Logs",      id="tab-logs"):
                        yield LogsPane(id="logs-pane")
            yield GroveRightPanel(id="right-panel")
        yield Footer()

    def on_mount(self) -> None:
        self._do_refresh()
        self.set_interval(30, self._do_refresh)

    def _do_refresh(self) -> None:
        for pane_id, pane_cls in [
            ("#overview-pane",  OverviewPane),
            ("#providers-pane", ProvidersPane),
            ("#skills-pane",    SkillsPane),
            ("#logs-pane",      LogsPane),
        ]:
            try:
                self.query_one(pane_id, pane_cls).refresh_data()
            except Exception:
                pass

    def action_refresh(self) -> None:
        self._do_refresh()
        try:
            self.query_one(VitalsBar)._refresh()
            self.query_one(GroveRightPanel)._refresh()
        except Exception:
            pass
        self.notify("Refreshed")

    def action_switch_tab(self, tab_id: str) -> None:
        try:
            self.query_one(TabbedContent).active = tab_id
        except Exception:
            pass


if __name__ == "__main__":
    WillowGrove().run()
