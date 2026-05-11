"""panes/routing.py — Live routing decision feed pane.
b17: WGRV1  ΔΣ=42
"""
from rich.markup import escape as _e
from textual import work
from textual.containers import Container
from textual.message import Message
from textual.widgets import DataTable, Label

import grove_reader
from panes.chat import sender_color


def fetch_routing(limit: int = 20) -> list[dict]:
    try:
        return grove_reader.routing_decisions(limit=limit)
    except Exception:
        return []


class _RoutingFetched(Message):
    def __init__(self, decisions: list[dict]) -> None:
        super().__init__()
        self.decisions = decisions


class RoutingPane(Container):
    def compose(self):
        yield Label("  Routing — live decision feed", id="routing-title")
        table = DataTable(id="routing-table", cursor_type="row")
        table.add_columns("Time", "Prompt", "Rule", "→ Target", "ms")
        yield table

    def on_mount(self) -> None:
        self.set_interval(5, self._fetch)
        self._fetch()

    @work(thread=True, exit_on_error=False)
    def _fetch(self) -> None:
        self.post_message(_RoutingFetched(fetch_routing(limit=20)))

    def on__routing_fetched(self, event: _RoutingFetched) -> None:
        from textual.css.query import NoMatches
        try:
            table = self.query_one("#routing-table", DataTable)
        except NoMatches:
            return
        table.clear()
        for d in event.decisions:
            ts         = d.get("ts")
            ts_str     = ts.strftime("%H:%M") if hasattr(ts, "strftime") else str(ts)[:5]
            snippet    = (d.get("prompt_snippet") or "")[:40]
            rule       = d.get("rule_matched") or "—"
            target     = d.get("routed_to") or "?"
            latency_ms = d.get("latency_ms")
            ms_str     = str(latency_ms) if latency_ms is not None else "—"
            color      = sender_color(target)
            table.add_row(
                ts_str,
                snippet,
                f"[dim]{rule}[/]",
                f"[{color} bold]{target}[/]",
                ms_str,
            )
