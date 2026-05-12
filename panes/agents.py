"""panes/agents.py — Fleet Agent View pane (FAV P0).
b17: WGRV1  ΔΣ=42
"""
from rich.markup import escape as _e
from textual import work
from textual.containers import Container, Vertical
from textual.message import Message
from textual.widgets import DataTable, Label

import grove_reader
from panes.chat import sender_color


_STATE_COLOR = {
    "running": "green",
    "idle":    "yellow",
    "stale":   "dim",
    "blocked": "red bold",
    "unknown": "dim",
    "gone":    "dim",
}


def age_str(secs: int) -> str:
    if secs < 60:    return f"{secs}s"
    if secs < 3600:  return f"{secs // 60}m"
    return f"{secs // 3600}h"


# kept for backward compat with existing tests
def agent_state(age_secs: int) -> tuple[str, str]:
    if age_secs < 120:   return "running", "green"
    if age_secs < 900:   return "idle",    "yellow"
    if age_secs < 3600:  return "stale",   "dim"
    return "gone", "dim"


class _FleetFetched(Message):
    def __init__(self, rows: list[dict]) -> None:
        super().__init__()
        self.rows = rows


class AgentsPane(Container):
    DEFAULT_CSS = """
    AgentsPane #agents-peek {
        height: 3;
        padding: 0 1;
        color: $text-muted;
    }
    """

    def compose(self):
        yield Label("  Fleet", id="agents-title")
        with Vertical():
            table = DataTable(id="agents-table", cursor_type="row")
            table.add_columns("!", "Agent", "State", "Age", "Peek")
            yield table
        yield Label("", id="agents-peek")

    def on_mount(self) -> None:
        self._focused = False
        self.set_interval(5, self._maybe_fetch)
        self._fetch()

    def on_focus(self) -> None:
        self._focused = True

    def on_blur(self) -> None:
        self._focused = False

    def _maybe_fetch(self) -> None:
        self._fetch()

    @work(thread=True, exit_on_error=False)
    def _fetch(self) -> None:
        rows = grove_reader.grove_agent_fleet_rows(limit=50)
        self.post_message(_FleetFetched(rows))

    def on__fleet_fetched(self, event: _FleetFetched) -> None:
        from textual.css.query import NoMatches
        try:
            table = self.query_one("#agents-table", DataTable)
        except NoMatches:
            return

        self._fleet_rows = event.rows
        table.clear()
        for r in event.rows:
            sender   = r["sender"]
            state    = r.get("ui_state", "unknown")
            blocked  = r.get("blocked", False)
            age      = age_str(r.get("age_secs", 0))
            peek     = _e((r.get("peek") or "")[:80])
            color    = sender_color(sender)
            sc       = _STATE_COLOR.get(state, "dim")
            attn     = "[red bold]![/]" if blocked else " "
            table.add_row(
                attn,
                f"[{color} bold]{_e(sender)}[/]",
                f"[{sc}]{_e(state)}[/]",
                age,
                peek,
            )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        from textual.css.query import NoMatches
        rows = getattr(self, "_fleet_rows", [])
        idx = event.cursor_row
        if 0 <= idx < len(rows):
            r = rows[idx]
            peek_full = _e((r.get("peek") or "—")[:300])
            blocked_note = "  [red bold]BLOCKED — needs reply[/]" if r.get("blocked") else ""
            try:
                self.query_one("#agents-peek", Label).update(
                    f"[dim]{_e(r['sender'])}:[/] {peek_full}{blocked_note}"
                )
            except NoMatches:
                pass
