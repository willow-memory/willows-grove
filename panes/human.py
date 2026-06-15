"""panes/human.py — Human-required queue: consent, attestation, review, onboarding.
b17: WGRV1  ΔΣ=42

The one surface where the human is *required* to act. Items here pause automation
until acknowledged. First-class because a human+agent workspace that hides its own
consent gates is not honestly collaborative — it just looks like one.
"""
from __future__ import annotations

from contextlib import suppress
from datetime import datetime, timezone

from rich.markup import escape as _e
from textual import work
from textual.binding import Binding
from textual.containers import Container
from textual.message import Message
from textual.widgets import DataTable, Label

import grove_reader
from grove.theme_textual import ACCENT, DEGRADED, HEALTHY, PRIMARY, SECONDARY

_PRIORITY_COLOR = {
    "critical": DEGRADED,
    "high": DEGRADED,
    "normal": PRIMARY,
    "low": SECONDARY,
}


def fetch_human_queue(limit: int = 30) -> list[dict]:
    try:
        return grove_reader.human_required_queue(limit=limit, open_only=True)
    except Exception:
        return []


def _age(ts) -> str:
    """Compact age of an item, e.g. 12m / 5h / 3d."""
    if not hasattr(ts, "tzinfo") or ts.tzinfo is None:
        return "—"
    secs = int((datetime.now(timezone.utc) - ts).total_seconds())
    if secs < 3600:
        return f"{max(secs, 0) // 60}m"
    if secs < 86400:
        return f"{secs // 3600}h"
    return f"{secs // 86400}d"


class _HumanFetched(Message):
    def __init__(self, items: list[dict]) -> None:
        super().__init__()
        self.items = items


class HumanPane(Container):
    BINDINGS = [Binding("r", "refresh_data", "Refresh")]

    DEFAULT_CSS = f"""
    HumanPane {{
        height: 1fr;
        padding: 0 1;
    }}
    HumanPane #human-title {{
        color: {ACCENT};
        text-style: bold;
        margin-bottom: 1;
    }}
    HumanPane #human-table {{
        height: 1fr;
    }}
    """

    def compose(self):
        yield Label(
            "  Human — required actions (consent · attestation · review)",
            id="human-title",
        )
        table = DataTable(id="human-table", cursor_type="row")
        table.add_columns(
            ("Pri", "pri"),
            ("Kind", "kind"),
            ("Title", "title"),
            ("From", "from"),
            ("Age", "age"),
        )
        yield table

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        self._fetch()

    @work(thread=True, exit_on_error=False)
    def _fetch(self) -> None:
        self.post_message(_HumanFetched(fetch_human_queue(limit=30)))

    def on__human_fetched(self, event: _HumanFetched) -> None:
        try:
            self._apply(event.items)
        except Exception as exc:
            with suppress(Exception):
                self.query_one("#human-title", Label).update(f"  Human — error: {exc}")

    def _apply(self, items: list[dict]) -> None:
        table = self.query_one("#human-table", DataTable)
        table.clear()
        title = self.query_one("#human-title", Label)
        if not items:
            title.update(f"  Human — required actions  [{HEALTHY}]✓ queue clear[/]")
            table.add_row("", "", "nothing awaiting you", "", "")
            return
        title.update(f"  Human — required actions  [{ACCENT}]{len(items)} open[/]")
        for it in items:
            pri = (it.get("priority") or "normal").lower()
            color = _PRIORITY_COLOR.get(pri, PRIMARY)
            kind = _e((it.get("kind") or "?").replace("_", " "))
            title_txt = _e((it.get("title") or "")[:48])
            src = _e(it.get("source_agent") or "—")
            age = _age(it.get("created_at"))
            table.add_row(
                f"[{color} bold]{pri[:4]}[/]",
                f"[{SECONDARY}]{kind}[/]",
                title_txt,
                f"[dim]{src}[/]",
                age,
            )
