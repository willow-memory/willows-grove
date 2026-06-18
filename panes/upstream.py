"""panes/upstream.py — Upstream Steward inbox (read-only; 2.0 writes SOIL).
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from rich.markup import escape as _e
from textual import work
from textual.binding import Binding
from textual.containers import Container, VerticalScroll
from textual.message import Message
from textual.widgets import Label, Static

import grove_db
from grove.apps.think_map import store as think_store
from grove.apps.upstream_steward import fetch_status, list_pending
from grove.theme_textual import ACCENT, PRIMARY, SECONDARY
from panes.think_map import ThinkMapNavigate


def render_upstream(status: dict, pending: list[dict]) -> str:
    lines: list[str] = []
    n = status.get("pending_count", 0)
    lines.append(f"[bold {ACCENT}]UPSTREAM[/]")
    if n == 0:
        lines.append(f"  [dim {SECONDARY}]no drafts pending — steward idle or not running[/]")
    else:
        urgent = status.get("urgent_count", 0)
        lines.append(
            f"  [{PRIMARY}]{n} draft{'s' if n != 1 else ''}[/]"
            + (f"  [{ACCENT}]{urgent} urgent[/]" if urgent else "")
        )
    last = status.get("last_poll")
    if last:
        lines.append(f"  [dim {SECONDARY}]last poll {_e(str(last)[:19])}[/]")
    digest = status.get("digest_line")
    if digest:
        lines.append(f"  [dim {SECONDARY}]{_e(digest[:120])}[/]")
    lines.append("")
    if pending:
        lines.append(f"[bold {ACCENT}]PENDING[/]")
        for rec in pending[:12]:
            row = {
                "work_id": rec.get("work_id") or rec.get("_id") or "",
                "title": (rec.get("title") or rec.get("subject") or "")[:60],
                "repo": rec.get("repo") or "",
                "lane": rec.get("lane") or "draft",
            }
            title = _e(row.get("title") or row.get("work_id", ""))
            repo = _e(row.get("repo") or "")
            lane = _e(row.get("lane", "draft"))
            wid = _e(str(row.get("work_id", "")))
            lines.append(
                f"  [{PRIMARY}]{title}[/] [dim {SECONDARY}]{repo} · {lane} · {wid}[/]"
            )
    lines.append("")
    lines.append(f"[dim {SECONDARY}]Approve on 2.0:[/]")
    lines.append("  [dim]willow.sh upstream pending[/]")
    lines.append("  [dim]willow.sh upstream approve WORK_ID[/]")
    lines.append("[dim]m — open first pending in Think Map[/]")
    lines.append("[dim]Notify channel: #upstream[/]")
    return "\n".join(lines)


class _UpstreamFetched(Message):
    def __init__(self, text: str) -> None:
        super().__init__()
        self.text = text


class UpstreamPane(Container):
    """Read-only view of upstream_steward SOIL — human gate stays on 2.0 CLI."""

    BINDINGS = [
        Binding("r", "refresh_data", "Refresh"),
        Binding("m", "map_first_pending", "Map this", show=False),
    ]

    DEFAULT_CSS = f"""
    UpstreamPane {{
        height: 1fr;
        padding: 0 1;
    }}
    UpstreamPane #upstream-title {{
        color: {ACCENT};
        text-style: bold;
        margin-bottom: 1;
    }}
    UpstreamPane #upstream-body {{
        height: 1fr;
    }}
    """

    def compose(self):
        yield Label("  Upstream — drafts awaiting you", id="upstream-title")
        with VerticalScroll(id="upstream-body"):
            yield Static("[dim]loading…[/]", id="upstream-content", markup=True)

    def on_mount(self) -> None:
        grove_db.ensure_upstream_channel()
        self.set_interval(60.0, self.refresh_data)
        self.refresh_data()

    def refresh_data(self) -> None:
        self._fetch()

    @work(thread=True, exit_on_error=False)
    def _fetch(self) -> None:
        status = fetch_status()
        pending = list_pending()
        text = render_upstream(status, pending)
        self.post_message(_UpstreamFetched(text))

    def on__upstream_fetched(self, event: _UpstreamFetched) -> None:
        self.query_one("#upstream-content", Static).update(event.text)

    def action_map_first_pending(self) -> None:
        pending = list_pending()
        if not pending:
            return
        m = think_store.create_from_upstream(pending[0])
        think_store.set_active_map(m["id"])
        self.post_message(ThinkMapNavigate(m["id"]))
