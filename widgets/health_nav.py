"""widgets/health_nav.py — Health subsystem status left-panel.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import os
from pathlib import Path

from textual import work
from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static

_SOIL_STORE = Path(os.environ.get("WILLOW_STORE_ROOT", Path.home() / ".willow" / "store"))


def _fetch_health_status() -> dict:
    """Pure function — never raises. Returns status dict for pg, ollama, kart, soil."""
    status: dict = {}

    # pg
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname=os.environ.get("WILLOW_PG_DB", "willow_19"),
            user=os.environ.get("WILLOW_PG_USER", os.environ.get("USER", "")),
            connect_timeout=2,
        )
        conn.close()
        status["pg"] = {"ok": True, "label": "up"}
    except Exception:
        status["pg"] = {"ok": False, "label": "down"}

    # ollama
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:11434", timeout=2)
        status["ollama"] = {"ok": True, "label": "up"}
    except Exception:
        status["ollama"] = {"ok": False, "label": "down"}

    # kart — count pending+running tasks
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname=os.environ.get("WILLOW_PG_DB", "willow_19"),
            user=os.environ.get("WILLOW_PG_USER", os.environ.get("USER", "")),
            connect_timeout=2,
        )
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM public.tasks WHERE status IN ('pending','running')")
        count = cur.fetchone()[0]
        conn.close()
        status["kart"] = {"ok": True, "label": f"{count} pending"}
    except Exception:
        status["kart"] = {"ok": False, "label": "down"}

    # soil
    ok = _SOIL_STORE.is_dir()
    status["soil"] = {"ok": ok, "label": "ok" if ok else "missing"}

    return status


class _HealthStatusFetched(Message):
    def __init__(self, health: dict) -> None:
        super().__init__()
        self.health = health


class HealthNav(Widget):
    DEFAULT_CSS = """
    HealthNav {
        width: 1fr;
        height: 1fr;
        padding: 1 1;
    }
    HealthNav #hn-header {
        color: #58a6ff;
        text-style: bold;
        padding: 0 0 1 0;
    }
    HealthNav #hn-status {
        height: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("HEALTH", id="hn-header")
        yield Static("", id="hn-status", markup=True)

    def on_mount(self) -> None:
        self._fetch()
        self.set_interval(15, self._fetch)

    @work(thread=True)
    def _fetch(self) -> None:
        health = _fetch_health_status()
        self.post_message(_HealthStatusFetched(health))

    def on__health_status_fetched(self, event: _HealthStatusFetched) -> None:
        from textual.css.query import NoMatches
        h = event.health
        lines = []
        for key in ("pg", "ollama", "kart", "soil"):
            entry = h.get(key, {"ok": False, "label": "?"})
            dot = "[green]●[/]" if entry["ok"] else "[red]●[/]"
            lines.append(f"{dot} [dim]{key}[/]  {entry['label']}")
        text = "\n".join(lines)
        try:
            self.query_one("#hn-status", Static).update(text)
        except NoMatches:
            pass
