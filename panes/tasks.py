"""panes/tasks.py — Kart task queue from Postgres.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from contextlib import suppress

from rich.markup import escape as _e
from textual import work
from textual.binding import Binding
from textual.containers import Container
from textual.message import Message
from textual.widgets import DataTable, Label, Static

import grove_db
from grove.theme_textual import ACCENT, DEGRADED, HEALTHY, IDLE, PRIMARY, SECONDARY


def status_color(status: str) -> str:
    s = status.lower()
    if s in ("complete", "completed"):
        return HEALTHY
    if s == "running":
        return DEGRADED
    if s in ("failed", "error"):
        return "red"
    return SECONDARY


def fetch_tasks() -> dict:
    result = {"pending": 0, "running": 0, "done": 0, "rows": []}
    conn = None
    try:
        conn = grove_db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT
                COUNT(*) FILTER (WHERE status IN ('pending','queued')) AS pending,
                COUNT(*) FILTER (WHERE status = 'running') AS running,
                COUNT(*) FILTER (WHERE status IN ('complete','completed','failed','error')) AS done
            FROM public.tasks
        """)
        row = cur.fetchone()
        result["pending"] = row[0] or 0
        result["running"] = row[1] or 0
        result["done"] = row[2] or 0
        cur.execute("""
            SELECT id, status, cmd, created_at
            FROM public.tasks
            ORDER BY id DESC LIMIT 50
        """)
        result["rows"] = [
            {
                "id": r[0],
                "status": r[1],
                "cmd": r[2] or "",
                "ts": str(r[3])[:16],
            }
            for r in cur.fetchall()
        ]
    except Exception:
        pass
    finally:
        if conn is not None:
            grove_db.release_connection(conn)
    return result


class _TasksFetched(Message):
    def __init__(self, data: dict) -> None:
        super().__init__()
        self.data = data


class TasksPane(Container):
    BINDINGS = [Binding("r", "refresh_data", "Refresh")]

    DEFAULT_CSS = f"""
    TasksPane {{
        height: 1fr;
        padding: 0 1;
    }}
    TasksPane #tasks-title {{
        color: {ACCENT};
        text-style: bold;
        margin-bottom: 1;
    }}
    TasksPane #tasks-stats {{
        height: 1;
        margin-bottom: 1;
    }}
    TasksPane #tasks-table {{
        height: 1fr;
    }}
    """

    def compose(self):
        yield Label("  Tasks — Kart queue", id="tasks-title")
        yield Static("", id="tasks-stats", markup=True)
        table = DataTable(id="tasks-table", cursor_type="row")
        table.add_columns(
            ("ID", "id"),
            ("Status", "status"),
            ("Command", "cmd"),
            ("Time", "time"),
        )
        yield table

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        self._fetch()

    @work(thread=True, exit_on_error=False)
    def _fetch(self) -> None:
        self.post_message(_TasksFetched(fetch_tasks()))

    def on__tasks_fetched(self, event: _TasksFetched) -> None:
        try:
            self._apply(event.data)
        except Exception as exc:
            with suppress(Exception):
                self.query_one("#tasks-stats", Static).update(
                    f"[red]{_e(str(exc))}[/]"
                )

    def _apply(self, data: dict) -> None:
        stats = (
            f"[{PRIMARY}]{data['running']}[/] running  "
            f"[{DEGRADED}]{data['pending']}[/] pending  "
            f"[{IDLE}]{data['done']}[/] done"
        )
        self.query_one("#tasks-stats", Static).update(stats)
        table = self.query_one("#tasks-table", DataTable)
        table.clear()
        if not data["rows"]:
            table.add_row("", "idle", "no tasks in queue", "")
            return
        for row in data["rows"]:
            color = status_color(row["status"])
            table.add_row(
                str(row["id"]),
                f"[{color}]{_e(row['status'])}[/]",
                _e(row["cmd"][:60]),
                row["ts"],
            )
