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

    #overview-title, #sysinfo-title, #prov-title,
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
    """

    BINDINGS = [
        Binding("q", "quit",    "Quit"),
        Binding("r", "refresh", "Refresh"),
    ]

    TITLE     = "Willow Grove"
    SUB_TITLE = f"local-first AI stack — {WILLOW_ROOT}"

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent():
            with TabPane("Overview",  id="tab-overview"):
                yield OverviewPane(id="overview-pane")
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


if __name__ == "__main__":
    WillowGrove().run()
