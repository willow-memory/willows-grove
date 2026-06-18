"""panes/routing.py — Live routing decision feed.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from contextlib import suppress

from rich.markup import escape as _e
from textual import work
from textual.binding import Binding
from textual.containers import Container
from textual.message import Message
from textual.widgets import DataTable, Label

import grove_reader
from grove.theme_textual import ACCENT, SECONDARY
from panes.chat_format import sender_color


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
    BINDINGS = [Binding("r", "refresh_data", "Refresh")]

    DEFAULT_CSS = f"""
    RoutingPane {{
        height: 1fr;
        padding: 0 1;
    }}
    RoutingPane #routing-title {{
        color: {ACCENT};
        text-style: bold;
        margin-bottom: 1;
    }}
    RoutingPane #routing-table {{
        height: 1fr;
    }}
    """

    def compose(self):
        yield Label("  Routing — live decision feed", id="routing-title")
        table = DataTable(id="routing-table", cursor_type="row")
        table.add_columns(
            ("Time", "time"),
            ("Prompt", "prompt"),
            ("Rule", "rule"),
            ("Target", "target"),
            ("ms", "ms"),
        )
        yield table

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        self._fetch()

    @work(thread=True, exit_on_error=False)
    def _fetch(self) -> None:
        self.post_message(_RoutingFetched(fetch_routing(limit=20)))

    def on__routing_fetched(self, event: _RoutingFetched) -> None:
        try:
            self._apply(event.decisions)
        except Exception as exc:
            with suppress(Exception):
                self.query_one("#routing-title", Label).update(
                    f"  Routing — error: {exc}"
                )

    def _apply(self, decisions: list[dict]) -> None:
        table = self.query_one("#routing-table", DataTable)
        table.clear()
        if not decisions:
            table.add_row("", "no decisions yet", "", "", "")
            return
        for d in decisions:
            ts = d.get("ts")
            ts_str = ts.strftime("%H:%M") if hasattr(ts, "strftime") else str(ts)[:5]
            snippet = _e((d.get("prompt_snippet") or "")[:40])
            rule = _e(d.get("rule_matched") or "—")
            target = d.get("routed_to") or "?"
            color = sender_color(target)
            latency_ms = d.get("latency_ms")
            ms_str = str(latency_ms) if latency_ms is not None else "—"
            table.add_row(
                ts_str,
                snippet,
                f"[dim {SECONDARY}]{rule}[/]",
                f"[{color} bold]{_e(target)}[/]",
                ms_str,
            )
