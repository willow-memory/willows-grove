#!/usr/bin/env python3
"""
app.py — Willow Grove (Textual dashboard).
b17: WGRV1  ΔΣ=42

Run: python3 app.py
"""
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.reactive import reactive
from textual.widgets import (
    DataTable, Footer, Header, Label, Log,
    Static, TabbedContent, TabPane,
)
from textual import work

# ── Paths ──────────────────────────────────────────────────────────────────────
WILLOW_ROOT = Path(os.environ.get("WILLOW_ROOT", Path.home() / "github" / "willow-1.9"))
WILLOW_STORE = Path(os.environ.get("WILLOW_STORE_ROOT", Path.home() / ".willow" / "store"))
WILLOW_LOGS = Path.home() / ".willow" / "logs"
SESSION_ANCHOR = Path.home() / ".willow" / "session_anchor.json"
SKILLS_DIR = WILLOW_ROOT / "willow" / "fylgja" / "skills"

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


def _read_providers() -> list[dict]:
    col_dir = WILLOW_STORE / "willow" / "providers"
    if not col_dir.exists():
        return []
    providers = []
    try:
        import sqlite3
        db = col_dir / "store.db"
        if db.exists():
            conn = sqlite3.connect(str(db), check_same_thread=False)
            rows = conn.execute(
                "SELECT data FROM records WHERE deleted = 0"
            ).fetchall()
            conn.close()
            for row in rows:
                try:
                    providers.append(json.loads(row[0]))
                except Exception:
                    pass
    except Exception:
        pass
    return providers


def _read_skills() -> list[dict]:
    skills = []
    if not SKILLS_DIR.exists():
        return skills
    for path in sorted(SKILLS_DIR.glob("*.md")):
        name = path.stem
        description = ""
        try:
            text = path.read_text()
            in_front = False
            for line in text.splitlines():
                if line.strip() == "---":
                    in_front = not in_front
                    continue
                if in_front and line.startswith("description:"):
                    description = line[len("description:"):].strip().strip('"')
                    break
        except Exception:
            pass
        skills.append({"name": name, "description": description, "path": str(path)})
    return skills


def _tail_log(lines: int = 50) -> list[str]:
    try:
        logs = sorted(WILLOW_LOGS.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not logs:
            return ["No log files found in ~/.willow/logs/"]
        return logs[0].read_text().splitlines()[-lines:]
    except Exception as e:
        return [f"Log read error: {e}"]


# ── Status widget ──────────────────────────────────────────────────────────────

class StatusRow(Static):
    """One-line status indicator: [●] label  value"""

    def __init__(self, label: str, **kwargs):
        super().__init__(**kwargs)
        self._label = label
        self._value = "…"
        self._ok: bool | None = None

    def set_status(self, ok: bool | None, value: str) -> None:
        self._ok = ok
        self._value = value
        color = "green" if ok else ("red" if ok is False else "yellow")
        dot = "●" if ok else ("○" if ok is False else "◌")
        self.update(f"[{color}]{dot}[/] [bold]{self._label}[/]  {value}")


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


# ── Providers tab ──────────────────────────────────────────────────────────────

class ProvidersPane(Container):
    BINDINGS = [
        Binding("e", "enable_selected", "Enable"),
        Binding("d", "disable_selected", "Disable"),
    ]

    def compose(self) -> ComposeResult:
        yield Label("  Providers  (e=enable  d=disable)", id="prov-title")
        table = DataTable(id="prov-table", cursor_type="row")
        table.add_columns("Provider", "Status", "Type", "Models")
        yield table

    def refresh_data(self) -> None:
        table = self.query_one("#prov-table", DataTable)
        table.clear()
        providers = _read_providers()
        if not providers:
            table.add_row("No provider data", "run willow providers list", "", "")
            return
        for p in providers:
            status = "[green]ON[/]" if p.get("enabled") else "[red]OFF[/]"
            ptype = "local" if p.get("local") else "cloud"
            models = ", ".join(p.get("models", [])[:2])
            table.add_row(p["name"], status, ptype, models)

    def action_enable_selected(self) -> None:
        table = self.query_one("#prov-table", DataTable)
        row = table.cursor_row
        if row < 0:
            return
        name = str(table.get_cell_at((row, 0)))
        os.system(f"willow providers enable {name} &")
        self.refresh_data()

    def action_disable_selected(self) -> None:
        table = self.query_one("#prov-table", DataTable)
        row = table.cursor_row
        if row < 0:
            return
        name = str(table.get_cell_at((row, 0)))
        if name == "ollama":
            self.app.notify("Ollama cannot be disabled — it's the default provider.", severity="warning")
            return
        os.system(f"willow providers disable {name} &")
        self.refresh_data()


# ── Skills tab ─────────────────────────────────────────────────────────────────

class SkillsPane(Container):
    def compose(self) -> ComposeResult:
        yield Label(f"  Skills — {SKILLS_DIR}", id="skills-title")
        table = DataTable(id="skills-table", cursor_type="row")
        table.add_columns("Name", "Description")
        yield table
        yield Static("", id="skill-detail")

    def refresh_data(self) -> None:
        table = self.query_one("#skills-table", DataTable)
        table.clear()
        for s in _read_skills():
            desc = s["description"][:80] + "…" if len(s["description"]) > 80 else s["description"]
            table.add_row(s["name"], desc)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        skills = _read_skills()
        if event.cursor_row < len(skills):
            skill = skills[event.cursor_row]
            try:
                content = Path(skill["path"]).read_text()[:500]
            except Exception:
                content = "(unreadable)"
            self.query_one("#skill-detail", Static).update(
                f"\n[bold]{skill['name']}[/]\n{skill['description']}\n\n{content}"
            )


# ── Health tab ─────────────────────────────────────────────────────────────────

class HealthPane(Container):
    BINDINGS = [Binding("r", "run_health", "Run boot check")]

    def compose(self) -> ComposeResult:
        yield Label("  Health  (r=run boot check)", id="health-title")
        yield Log(id="health-log", auto_scroll=True)

    def action_run_health(self) -> None:
        log = self.query_one("#health-log", Log)
        log.clear()
        log.write_line("Running willow health boot…")
        script = WILLOW_ROOT / "willow" / "fylgja" / "skills" / "scripts" / "system_health.py"
        import subprocess
        try:
            result = subprocess.run(
                ["python3", str(script), "--check", "boot",
                 "--willow-dir", str(Path.home() / ".willow"),
                 "--repo", str(WILLOW_ROOT)],
                capture_output=True, text=True, timeout=30
            )
            for line in (result.stdout + result.stderr).splitlines():
                color = "green" if "HEALTHY" in line else ("red" if "CRITICAL" in line else ("yellow" if "WARN" in line else ""))
                log.write_line(f"[{color}]{line}[/]" if color else line)
        except Exception as e:
            log.write_line(f"[red]Error: {e}[/]")


# ── Logs tab ───────────────────────────────────────────────────────────────────

class LogsPane(Container):
    def compose(self) -> ComposeResult:
        yield Label("  Logs — ~/.willow/logs/ (most recent)", id="logs-title")
        yield Log(id="log-view", auto_scroll=True)

    def refresh_data(self) -> None:
        log = self.query_one("#log-view", Log)
        log.clear()
        for line in _tail_log(80):
            log.write_line(line)


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
