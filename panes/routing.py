"""panes/routing.py — Live routing decision feed pane.
b17: WGRV1  ΔΣ=42
"""
from textual.containers import Container
from textual.widgets import DataTable, Label

import grove_reader
from panes.chat import sender_color


def confidence_color(conf: float) -> str:
    if conf >= 0.85:  return "green"
    if conf >= 0.6:   return "yellow"
    return "red"


def fetch_routing(limit: int = 20) -> list[dict]:
    try:
        return grove_reader.routing_decisions(limit=limit)
    except Exception:
        return []


class RoutingPane(Container):
    def compose(self):
        yield Label("  Routing — live decision feed", id="routing-title")
        table = DataTable(id="routing-table", cursor_type="row")
        table.add_columns("Time", "Prompt", "→ Target", "Conf")
        yield table

    def on_mount(self) -> None:
        self.set_interval(5, self.refresh_data)
        self.refresh_data()

    def refresh_data(self) -> None:
        table = self.query_one("#routing-table", DataTable)
        table.clear()
        for d in fetch_routing():
            ts      = d.get("ts")
            ts_str  = ts.strftime("%H:%M") if hasattr(ts, "strftime") else str(ts)[:5]
            snippet = (d.get("prompt_snippet") or "")[:50]
            target  = d.get("routed_to") or "?"
            conf    = float(d.get("confidence", 1.0))
            color   = sender_color(target)
            c_color = confidence_color(conf)
            table.add_row(
                ts_str,
                snippet,
                f"[{color} bold]{target}[/]",
                f"[{c_color}]{conf:.0%}[/]",
            )
