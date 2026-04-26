#!/usr/bin/env python3
"""
app.py — Willow Grove (Textual dashboard).
b17: WGRV1  ΔΣ=42

Run: python3 app.py
"""
import json
import os
import urllib.request
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import (
    DataTable, Footer, Header, Label, Log,
    Static, TabbedContent, TabPane,
)

from widgets.status_row import StatusRow
from panes.providers import ProvidersPane
from panes.skills    import SkillsPane
from panes.health    import HealthPane
from panes.logs      import LogsPane

# ── Paths ──────────────────────────────────────────────────────────────────────
WILLOW_ROOT    = Path(os.environ.get("WILLOW_ROOT", Path.home() / "github" / "willow-1.9"))
SESSION_ANCHOR = Path.home() / ".willow" / "session_anchor.json"

# ── Helpers ────────────────────────────────────────────────────────────────────

def _http_get(url: str, timeout: int = 2) -> dict | None:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read())
    except Exception:
        return None


def _pg_conn():
    import psycopg2
    return psycopg2.connect(
        dbname=os.environ.get("WILLOW_PG_DB", "willow_19"),
        user=os.environ.get("WILLOW_PG_USER", os.environ.get("USER", "")),
    )


def _ollama_status() -> tuple[bool, list[str]]:
    data = _http_get("http://localhost:11434/api/tags")
    if not data:
        return False, []
    models = [m["name"] for m in data.get("models", [])]
    return True, models


def _litellm_status() -> bool:
    return _http_get("http://localhost:4000/health") is not None


def _pg_status() -> tuple[bool, int]:
    try:
        conn = _pg_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM knowledge")
        count = cur.fetchone()[0]
        conn.close()
        return True, count
    except Exception:
        return False, 0


def _open_tasks() -> int:
    try:
        conn = _pg_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM tasks WHERE status = 'pending'")
        count = cur.fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0


def _last_handoff() -> str:
    try:
        data = json.loads(SESSION_ANCHOR.read_text())
        return data.get("handoff_title", "—")
    except Exception:
        return "—"


# ── Overview tab ───────────────────────────────────────────────────────────────

class OverviewPane(Container):
    def compose(self) -> ComposeResult:
        yield Label("  Willow System Overview", id="overview-title")
        yield StatusRow("Postgres     ", id="stat-pg")
        yield StatusRow("Ollama       ", id="stat-ollama")
        yield StatusRow("LiteLLM      ", id="stat-litellm")
        yield StatusRow("Open tasks   ", id="stat-tasks")
        yield StatusRow("Last handoff ", id="stat-handoff")

    def refresh_data(self) -> None:
        pg_up, atoms = _pg_status()
        self.query_one("#stat-pg", StatusRow).set_status(
            pg_up, f"{atoms:,} KB atoms" if pg_up else "NOT CONNECTED"
        )
        ollama_up, models = _ollama_status()
        self.query_one("#stat-ollama", StatusRow).set_status(
            ollama_up, f"{len(models)} models" if ollama_up else "unreachable"
        )
        lt_up = _litellm_status()
        self.query_one("#stat-litellm", StatusRow).set_status(
            lt_up, "localhost:4000" if lt_up else "not running — willow litellm-start"
        )
        tasks = _open_tasks()
        self.query_one("#stat-tasks", StatusRow).set_status(
            tasks == 0, str(tasks)
        )
        handoff = _last_handoff()
        self.query_one("#stat-handoff", StatusRow).set_status(None, handoff)


# ── Main app ───────────────────────────────────────────────────────────────────

class WillowGrove(App):
    CSS = """
    Screen { background: #0d1117; }

    #overview-title, #prov-title, #skills-title, #health-title, #logs-title {
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

    TabbedContent { height: 1fr; }
    TabPane { height: 1fr; padding: 0; }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
    ]

    TITLE = "Willow Grove"
    SUB_TITLE = f"local-first AI stack — {WILLOW_ROOT}"

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent():
            with TabPane("Overview", id="tab-overview"):
                yield OverviewPane(id="overview-pane")
            with TabPane("Providers", id="tab-providers"):
                yield ProvidersPane(id="providers-pane")
            with TabPane("Skills", id="tab-skills"):
                yield SkillsPane(id="skills-pane")
            with TabPane("Health", id="tab-health"):
                yield HealthPane(id="health-pane")
            with TabPane("Logs", id="tab-logs"):
                yield LogsPane(id="logs-pane")
        yield Footer()

    def on_mount(self) -> None:
        self._do_refresh()
        self.set_interval(30, self._do_refresh)

    def _do_refresh(self) -> None:
        try:
            self.query_one("#overview-pane", OverviewPane).refresh_data()
        except Exception:
            pass
        try:
            self.query_one("#providers-pane", ProvidersPane).refresh_data()
        except Exception:
            pass
        try:
            self.query_one("#skills-pane", SkillsPane).refresh_data()
        except Exception:
            pass
        try:
            self.query_one("#logs-pane", LogsPane).refresh_data()
        except Exception:
            pass

    def action_refresh(self) -> None:
        self._do_refresh()
        self.notify("Refreshed")


if __name__ == "__main__":
    WillowGrove().run()
