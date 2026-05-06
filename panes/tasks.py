"""panes/tasks.py — Kart task queue pane + SOIL open-flags panel.
b17: WGRV1  ΔΣ=42
"""
import os
import sys
from pathlib import Path

from rich.markup import escape as _e
from textual import work
from textual.containers import Container
from textual.widgets import DataTable, Label

import grove_db
from widgets.status_row import StatusRow

_SEVERITY_COLOR = {"critical": "red", "high": "yellow", "medium": "cyan", "low": "dim"}


def status_color(status: str) -> str:
    s = status.lower()
    if s in ("complete", "completed"):  return "green"
    if s == "running":                  return "yellow"
    if s in ("failed", "error"):        return "red"
    return "dim"


def fetch_tasks() -> dict:
    result = {"pending": 0, "running": 0, "done": 0, "rows": []}
    conn = None
    try:
        conn = grove_db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT
                COUNT(*) FILTER (WHERE status IN ('pending','queued'))                       AS pending,
                COUNT(*) FILTER (WHERE status = 'running')                                   AS running,
                COUNT(*) FILTER (WHERE status IN ('complete','completed','failed','error'))   AS done
            FROM public.tasks
        """)
        row = cur.fetchone()
        result["pending"] = row[0] or 0
        result["running"] = row[1] or 0
        result["done"]    = row[2] or 0
        cur.execute("""
            SELECT id, status, cmd, created_at
            FROM public.tasks
            ORDER BY id DESC LIMIT 50
        """)
        result["rows"] = [
            {"id": r[0], "status": r[1], "cmd": r[2] or "", "ts": str(r[3])[:16]}
            for r in cur.fetchall()
        ]
    except Exception:
        pass
    finally:
        if conn is not None:
            grove_db.release_connection(conn)
    return result


def fetch_flags() -> list[dict]:
    """Return open flags from hanuman/flags SOIL collection, sorted critical→low."""
    _SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    try:
        willow_root = os.environ.get("WILLOW_ROOT", str(Path.home() / "github" / "willow-1.9"))
        sys.path.insert(0, willow_root)
        from core.willow_store import WillowStore
        store = WillowStore()
        records = store.list("hanuman/flags")
        open_flags = [r for r in records if r.get("flag_state") == "open"]
        open_flags.sort(key=lambda r: _SEVERITY_ORDER.get(r.get("severity", "low"), 9))
        return open_flags
    except Exception:
        return []


def fetch_backfill_progress() -> dict | None:
    try:
        willow_root = os.environ.get("WILLOW_ROOT", str(Path.home() / "github" / "willow-1.9"))
        sys.path.insert(0, willow_root)
        from core.willow_store import WillowStore
        store = WillowStore()
        return store.get("hanuman/tasks", "embed_backfill_progress")
    except Exception:
        return None


class TasksPane(Container):
    def compose(self):
        yield Label("  Tasks", id="tasks-title")
        yield StatusRow("Running", id="stat-running")
        yield StatusRow("Pending", id="stat-pending")
        yield StatusRow("Done   ", id="stat-done")
        table = DataTable(id="tasks-table", cursor_type="row")
        table.add_columns("ID", "Status", "Command", "Time")
        yield table
        yield Label("  Open Flags", id="flags-title")
        flags_table = DataTable(id="flags-table", cursor_type="row")
        flags_table.add_columns("Sev", "ID", "Title", "Atom")
        yield flags_table

    def on_mount(self) -> None:
        self.set_interval(10, self.refresh_data)
        self.refresh_data()

    @work(thread=True, exit_on_error=False)
    def refresh_data(self) -> None:
        data  = fetch_tasks()
        bp    = fetch_backfill_progress()
        flags = fetch_flags()
        self.app.call_from_thread(self._apply_data, data, bp, flags)

    def _apply_data(self, data: dict, bp: dict | None, flags: list[dict]) -> None:
        table = self.query_one("#tasks-table", DataTable)
        table.clear()
        self.query_one("#stat-running", StatusRow).set_status(None,               str(data["running"]))
        self.query_one("#stat-pending", StatusRow).set_status(data["pending"] == 0, str(data["pending"]))
        self.query_one("#stat-done",    StatusRow).set_status(None,               str(data["done"]))

        # Backfill progress as a synthetic running row at the top
        if bp and bp.get("table") != "done":
            pct     = bp.get("pct", 0)
            done    = bp.get("atoms_done", 0)
            total   = bp.get("total", 0)
            eta     = bp.get("eta_human", "?")
            rate    = bp.get("rate_recent") or bp.get("rate_per_sec", 0)
            updated = str(bp.get("updated_at", ""))[:16]
            cmd = f"embed_backfill  {pct:.1f}%  {done:,}/{total:,}  {rate:.2f}/s  ETA {eta}"
            table.add_row("BACKFILL", "[yellow]running[/]", cmd, updated)

        for row in data["rows"]:
            color = status_color(row["status"])
            table.add_row(
                str(row["id"]),
                f"[{color}]{_e(row['status'])}[/]",
                _e(row["cmd"][:60]),
                row["ts"],
            )

        flags_table = self.query_one("#flags-table", DataTable)
        flags_table.clear()
        for flag in flags:
            sev   = flag.get("severity", "low")
            color = _SEVERITY_COLOR.get(sev, "dim")
            flags_table.add_row(
                f"[{color}]{_e(sev)}[/]",
                _e(str(flag.get("id", ""))[:20]),
                _e(str(flag.get("title", ""))[:55]),
                _e(str(flag.get("atom_id", ""))[:16]),
            )
