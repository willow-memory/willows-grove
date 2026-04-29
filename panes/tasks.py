"""panes/tasks.py — Kart task queue pane.
b17: WGRV1  ΔΣ=42
"""
import os
import sys
from pathlib import Path

from textual.containers import Container
from textual.widgets import DataTable, Label, ProgressBar

from widgets.status_row import StatusRow


def _pg_conn():
    import psycopg2
    return psycopg2.connect(
        dbname=os.environ.get("WILLOW_PG_DB",   "willow_19"),
        user=os.environ.get("WILLOW_PG_USER", os.environ.get("USER", "")),
    )


def status_color(status: str) -> str:
    s = status.lower()
    if s in ("complete", "completed"):  return "green"
    if s == "running":                  return "yellow"
    if s in ("failed", "error"):        return "red"
    return "dim"


def fetch_tasks() -> dict:
    result = {"pending": 0, "running": 0, "done": 0, "rows": []}
    try:
        conn = _pg_conn()
        cur  = conn.cursor()
        cur.execute("""
            SELECT
                COUNT(*) FILTER (WHERE status IN ('pending','queued'))              AS pending,
                COUNT(*) FILTER (WHERE status = 'running')                          AS running,
                COUNT(*) FILTER (WHERE status IN ('complete','completed','failed','error')) AS done
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
        conn.close()
    except Exception:
        pass
    return result


def fetch_backfill_progress() -> dict | None:
    try:
        sys.path.insert(0, str(Path.home() / "github" / "willow-1.9"))
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
        yield Label("", id="backfill-label")
        yield ProgressBar(total=100, show_eta=False, id="backfill-bar")
        table = DataTable(id="tasks-table", cursor_type="row")
        table.add_columns("ID", "Status", "Command", "Time")
        yield table

    def on_mount(self) -> None:
        self.set_interval(10, self.refresh_data)
        self.refresh_data()

    def refresh_data(self) -> None:
        data  = fetch_tasks()
        table = self.query_one("#tasks-table", DataTable)
        table.clear()
        self.query_one("#stat-running", StatusRow).set_status(None,              str(data["running"]))
        self.query_one("#stat-pending", StatusRow).set_status(data["pending"]==0, str(data["pending"]))
        self.query_one("#stat-done",    StatusRow).set_status(None,              str(data["done"]))
        for row in data["rows"]:
            color = status_color(row["status"])
            table.add_row(
                str(row["id"]),
                f"[{color}]{row['status']}[/]",
                row["cmd"][:60],
                row["ts"],
            )

        bp = fetch_backfill_progress()
        bar   = self.query_one("#backfill-bar",   ProgressBar)
        label = self.query_one("#backfill-label", Label)
        if bp:
            pct   = bp.get("pct", 0)
            done  = bp.get("atoms_done", 0)
            total = bp.get("total", 0)
            eta   = bp.get("eta_human", "?")
            rate  = bp.get("rate_per_sec", 0)
            label.update(f"  Embed Backfill — {pct:.1f}%  {done:,}/{total:,}  {rate:.1f}/s  ETA {eta}")
            bar.update(progress=pct)
            bar.display = True
            label.display = True
        else:
            bar.display = False
            label.display = False
