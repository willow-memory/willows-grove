"""panes/agents.py — Fleet agent view from Grove heartbeats.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from contextlib import suppress

from rich.markup import escape as _e
from textual import on, work
from textual.binding import Binding
from textual.containers import Container
from textual.message import Message
from textual.widgets import DataTable, Label, Static

import grove_reader
from grove.theme_textual import ACCENT, DEGRADED, HEALTHY, IDLE, PRIMARY, SECONDARY
from panes.chat_format import sender_color

_STATE_COLOR = {
    "running": HEALTHY,
    "idle": DEGRADED,
    "stale": IDLE,
    "blocked": "red",
    "unknown": SECONDARY,
    "gone": IDLE,
}


def age_str(secs: int) -> str:
    if secs < 60:
        return f"{secs}s"
    if secs < 3600:
        return f"{secs // 60}m"
    return f"{secs // 3600}h"


class _FleetFetched(Message):
    def __init__(self, rows: list[dict]) -> None:
        super().__init__()
        self.rows = rows


class AgentsPane(Container):
    BINDINGS = [Binding("r", "refresh_data", "Refresh")]

    DEFAULT_CSS = f"""
    AgentsPane {{
        height: 1fr;
        padding: 0 1;
    }}
    AgentsPane #agents-title {{
        color: {ACCENT};
        text-style: bold;
        margin-bottom: 1;
    }}
    AgentsPane #agents-table {{
        height: 1fr;
    }}
    AgentsPane #agents-peek {{
        height: 3;
        padding: 0 1;
        color: {SECONDARY};
        border-top: solid {SECONDARY};
    }}
    """

    def compose(self):
        yield Label("  Fleet — agent heartbeats", id="agents-title")
        table = DataTable(id="agents-table", cursor_type="row")
        table.add_columns(
            ("!", "attn"),
            ("Agent", "agent"),
            ("State", "state"),
            ("Age", "age"),
            ("Peek", "peek"),
        )
        yield table
        yield Static("[dim]Select a row for full peek[/]", id="agents-peek", markup=True)

    def on_mount(self) -> None:
        self._fleet_rows: list[dict] = []
        self.refresh_data()

    def refresh_data(self) -> None:
        self._fetch()

    @work(thread=True, exit_on_error=False)
    def _fetch(self) -> None:
        rows = grove_reader.grove_agent_fleet_rows(limit=50)
        self.post_message(_FleetFetched(rows))

    def on__fleet_fetched(self, event: _FleetFetched) -> None:
        try:
            self._apply(event.rows)
        except Exception as exc:
            with suppress(Exception):
                self.query_one("#agents-peek", Static).update(f"[red]{_e(str(exc))}[/]")

    def _apply(self, rows: list[dict]) -> None:
        self._fleet_rows = rows
        table = self.query_one("#agents-table", DataTable)
        table.clear()
        if not rows:
            table.add_row("", "no agents", "on bus", "", "")
            return
        for r in rows:
            sender = r["sender"]
            state = r.get("ui_state", "unknown")
            age = age_str(r.get("age_secs", 0))
            peek = _e((r.get("peek") or "")[:56])
            color = sender_color(sender)
            sc = _STATE_COLOR.get(state, SECONDARY)
            attn = "!" if r.get("blocked") else " "
            table.add_row(
                attn,
                f"[{color} bold]{_e(sender)}[/]",
                f"[{sc}]{_e(state)}[/]",
                age,
                peek,
            )

    @on(DataTable.RowHighlighted, "#agents-table")
    def _on_row(self, event: DataTable.RowHighlighted) -> None:
        idx = event.cursor_row
        if idx < 0 or idx >= len(self._fleet_rows):
            return
        r = self._fleet_rows[idx]
        peek_full = _e((r.get("peek") or "—")[:300])
        blocked = "  [red bold]needs reply[/]" if r.get("blocked") else ""
        with suppress(Exception):
            self.query_one("#agents-peek", Static).update(
                f"[{PRIMARY}]{_e(r['sender'])}:[/] {peek_full}{blocked}"
            )
