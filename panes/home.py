"""panes/home.py — DeskPane (live), HomeGrid, ProjectsGrid.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

from textual import work
from textual.containers import Container
from textual.message import Message
from textual.widgets import Static


@dataclass
class DeskData:
    unread_channels: list[dict] = field(default_factory=list)
    mentions:        list[dict] = field(default_factory=list)
    open_flags:      int         = 0
    running_tasks:   int         = 0
    pending_tasks:   int         = 0
    done_today:      int         = 0
    backfill:        dict | None = None
    agents:          list[dict]  = field(default_factory=list)
    sysinfo:         dict        = field(
        default_factory=lambda: {"cpu": 0, "mem": 0, "disk": 0, "temp": 0}
    )


def agent_dot(age_secs: int) -> str:
    if age_secs < 120:
        return "[green]●[/]"
    if age_secs < 900:
        return "[yellow]●[/]"
    return "[dim]●[/]"


def format_age(age_secs: int) -> str:
    if age_secs < 3600:
        return f"{age_secs // 60}m ago"
    return f"{age_secs // 3600}h ago"


def mini_bar(pct: float) -> str:
    filled = min(5, int(pct / 100 * 5))
    return "█" * filled + "░" * (5 - filled)


def render_desk(data: DeskData) -> str:
    _H = "[bold #58a6ff]"
    _V = "[#c9d1d9]"
    _D = "[dim]"
    _Y = "[yellow]"
    _E = "[/]"
    lines: list[str] = []

    # ── ATTENTION ────────────────────────────────────────────────────────────
    attn: list[str] = []
    for ch in data.unread_channels:
        name = ch["name"][:14]
        attn.append(f"  {_V}# {name:<14} {ch['unread']}{_E}")
    for m in data.mentions:
        attn.append(f"  {_Y}@←{m['sender']}{_E}")
    if data.open_flags > 0:
        attn.append(f"  {_Y}{data.open_flags} open flags{_E}")
    if attn:
        lines.append(f"{_H}⚡ ATTENTION{_E}")
        lines.extend(attn)
        lines.append("")

    # ── RUNNING ──────────────────────────────────────────────────────────────
    lines.append(f"{_H}▶ RUNNING{_E}")
    if data.running_tasks == 0 and data.pending_tasks == 0:
        lines.append(f"  {_D}idle{_E}")
    else:
        lines.append(f"  {_V}{data.running_tasks} running  {data.pending_tasks} pending{_E}")
    if data.backfill and data.backfill.get("table") != "done":
        pct = data.backfill.get("pct", 0)
        bar = mini_bar(pct)
        lines.append(f"  {_D}embed {bar} {pct:.0f}%{_E}")
    lines.append("")

    # ── DONE TODAY ───────────────────────────────────────────────────────────
    if data.done_today > 0:
        noun = "tasks" if data.done_today != 1 else "task"
        lines.append(f"{_H}✓ DONE TODAY{_E}")
        lines.append(f"  {_V}{data.done_today} {noun} complete{_E}")
        lines.append("")

    # ── SYSTEM ───────────────────────────────────────────────────────────────
    lines.append(f"{_H}⚙ SYSTEM{_E}")
    if not data.agents:
        lines.append(f"  {_D}no agents{_E}")
    else:
        for a in data.agents[:4]:
            dot     = agent_dot(a.get("age_secs", 9999))
            sender  = a["sender"][:12]
            age_str = format_age(a.get("age_secs", 0))
            lines.append(f"  {dot} {_V}{sender:<12}{_E} {_D}{age_str}{_E}")
    cpu = data.sysinfo.get("cpu", 0)
    mem = data.sysinfo.get("mem", 0)
    lines.append(f"  {_D}cpu {cpu}%  mem {mem}%{_E}")
    temp = data.sysinfo.get("temp", 0)
    if temp > 0:
        lines.append(f"  {_D}temp {temp}°C{_E}")

    return "\n".join(lines)


def fetch_desk_data(sender_name: str) -> DeskData:
    """Fetch all DeskData fields. Never raises — returns safe defaults on failure."""
    import json
    from datetime import date
    from pathlib import Path

    data = DeskData()

    # unread channels
    try:
        import grove_reader
        all_ch = grove_reader.grove_channels()
        data.unread_channels = [c for c in all_ch if c.get("unread", 0) > 0]
    except Exception:
        pass

    # @mentions — scan general + architecture
    try:
        import grove_reader
        target = f"@{sender_name}".lower()
        found: list[dict] = []
        for ch_name in ("general", "architecture"):
            for m in grove_reader.grove_messages(ch_name, limit=50):
                if target in m.get("content", "").lower():
                    found.append({
                        "channel": ch_name,
                        "sender": m.get("sender", "?"),
                        "snippet": m.get("content", "")[:20],
                    })
        data.mentions = found
    except Exception:
        pass

    # open flags from session anchor
    try:
        anchor = json.loads(
            (Path.home() / ".willow" / "session_anchor.json").read_text()
        )
        data.open_flags = anchor.get("open_flags", 0)
    except Exception:
        pass

    # kart task counts + done today
    try:
        from panes.tasks import fetch_tasks
        tasks = fetch_tasks()
        data.running_tasks = tasks.get("running", 0)
        data.pending_tasks = tasks.get("pending", 0)
        today = date.today().isoformat()
        data.done_today = sum(
            1 for r in tasks.get("rows", [])
            if r.get("status", "").lower() in ("complete", "completed")
            and r.get("ts", "").startswith(today)
        )
    except Exception:
        pass

    # backfill progress
    try:
        from panes.tasks import fetch_backfill_progress
        data.backfill = fetch_backfill_progress()
    except Exception:
        pass

    # active agents
    try:
        import grove_reader
        data.agents = grove_reader.grove_agents()
    except Exception:
        pass

    # sysinfo
    try:
        from panes.overview import fetch_sysinfo
        data.sysinfo = fetch_sysinfo()
    except Exception:
        pass

    return data




class _DeskRefreshed(Message):
    def __init__(self, data: DeskData) -> None:
        super().__init__()
        self.data = data


class DeskPane(Container):
    """Left column for Home — live Desk widget. Refreshes every 15s."""

    DEFAULT_CSS = """
    DeskPane {
        width: 1fr;
        height: 1fr;
        padding: 1 1;
    }
    DeskPane Static {
        width: 1fr;
        height: 1fr;
        color: #c9d1d9;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._sender = (
            os.environ.get("GROVE_SENDER")
            or os.environ.get("GROVE_NAME")
            or os.environ.get("USER", "sean")
        )

    def compose(self):
        yield Static("", id="desk-content", markup=True)

    def on_mount(self) -> None:
        self._fetch()
        self.set_interval(15, self._fetch)

    @work(thread=True)
    def _fetch(self) -> None:
        data = fetch_desk_data(self._sender)
        self.post_message(_DeskRefreshed(data))

    def on__desk_refreshed(self, event: _DeskRefreshed) -> None:
        try:
            from textual.css.query import NoMatches
            self.query_one("#desk-content", Static).update(render_desk(event.data))
        except NoMatches:
            pass


class HomeGrid(Container):
    """Center area for Home — live card grid backed by SOIL + built-ins."""

    DEFAULT_CSS = """
    HomeGrid {
        width: 1fr;
        height: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        from widgets.card_grid import CardGrid
        yield CardGrid([])  # on_mount calls reload() to populate from SOIL + built-ins

    def on_mount(self) -> None:
        from widgets import card_store
        from widgets.card_grid import CardGrid
        from textual.css.query import NoMatches
        card_store.seed_catalog()
        try:
            self.query_one(CardGrid).reload()
        except NoMatches:
            pass

    def on_card_activated(self, event) -> None:
        if getattr(event, "nav_target", None) == "+":
            from widgets.card_builder_modal import CardBuilderModal
            self.app.push_screen(CardBuilderModal())

    def refresh_cards(self) -> None:
        from widgets.card_grid import CardGrid
        from textual.css.query import NoMatches
        try:
            self.query_one(CardGrid).reload()
        except NoMatches:
            pass


class ProjectsGrid(Container):
    """Center area for Projects — launcher tiles for internal panes."""

    DEFAULT_CSS = """
    ProjectsGrid {
        width: 1fr;
        height: 1fr;
        layout: grid;
        grid-size: 3;
        grid-gutter: 1 1;
        padding: 1 1;
    }
    """

    def compose(self) -> ComposeResult:
        from widgets.card_grid import CardCell, LAUNCHER_CARDS
        for card_id, label, nav in LAUNCHER_CARDS:
            yield CardCell(
                card_id, label,
                nav_target=nav,
                value="→",
                state="blue",
                id=f"cell-{card_id}",
            )
