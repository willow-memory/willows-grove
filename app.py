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
from textual.widgets import Footer, Header, TabbedContent, TabPane

from panes.overview  import OverviewPane
from panes.chat      import ChatPane
from panes.tasks     import TasksPane
from panes.agents    import AgentsPane
from panes.routing   import RoutingPane
from panes.knowledge import KnowledgePane
from panes.providers import ProvidersPane
from panes.skills    import SkillsPane
from panes.health    import HealthPane
from panes.logs      import LogsPane

WILLOW_ROOT = Path(os.environ.get("WILLOW_ROOT", Path.home() / "github" / "willow-1.9"))


class WillowGrove(App):
    CSS = """
    Screen { background: #0d1117; }

    Header {
        background: #161b22;
        color: #58a6ff;
        text-style: bold;
    }
    Footer { background: #161b22; }

    TabbedContent { height: 1fr; }
    TabPane       { height: 1fr; padding: 0; }

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

    Rule { margin: 1 0; color: #30363d; }

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
    ]

    TITLE     = "Willow Grove"
    SUB_TITLE = f"local-first AI stack — {WILLOW_ROOT}"

    def compose(self) -> ComposeResult:
        yield Header()
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
        self.notify("Refreshed")

    def action_switch_tab(self, tab_id: str) -> None:
        try:
            self.query_one(TabbedContent).active = tab_id
        except Exception:
            pass


if __name__ == "__main__":
    WillowGrove().run()
