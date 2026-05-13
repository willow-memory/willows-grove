"""panes/home.py — DeskPane (live), HomeGrid, ProjectsGrid.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import select
from dataclasses import dataclass, field

from rich.markup import escape as _e
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
        ch_short = str(m.get("channel", "?"))[:16]
        attn.append(f"  {_Y}#{_e(ch_short)} ← {_e(m['sender'])}{_E}")
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
            lines.append(f"  {dot} {_V}{_e(sender):<12}{_E} {_D}{age_str}{_E}")
    cpu = data.sysinfo.get("cpu", 0)
    mem = data.sysinfo.get("mem", 0)
    lines.append(f"  {_D}cpu {cpu}%  mem {mem}%{_E}")
    temp = data.sysinfo.get("temp", 0)
    if temp > 0:
        lines.append(f"  {_D}temp {temp}°C{_E}")

    return "\n".join(lines)


def fetch_desk_data() -> DeskData:
    """Fetch all DeskData fields. Never raises — returns safe defaults on failure."""
    import json
    from concurrent.futures import ThreadPoolExecutor
    from datetime import date
    from pathlib import Path

    data = DeskData()

    def _fetch_unread():
        try:
            import grove_reader
            import soil as _soil
            cursor_records = _soil.all_records("willow-dashboard/cursors")
            last_seen_ids = {r["_id"]: r.get("last_id", 0) for r in cursor_records}
            active_rec = _soil.get("willow-dashboard/active", "channel")
            active_channel = active_rec.get("name", "") if active_rec else ""
            all_ch = grove_reader.grove_channels(last_seen_ids=last_seen_ids)
            return [
                c for c in all_ch
                if c.get("unread", 0) > 0 and c["name"] != active_channel
            ]
        except Exception:
            return []

    def _fetch_mentions():
        try:
            import grove_reader
            return grove_reader.grove_inbox_bundle(merge_limit=20)
        except Exception:
            return []

    def _fetch_flags():
        try:
            anchor = json.loads(
                (Path.home() / ".willow" / "session_anchor.json").read_text()
            )
            return anchor.get("open_flags", 0)
        except Exception:
            return 0

    def _fetch_tasks():
        try:
            from panes.tasks import fetch_tasks
            tasks = fetch_tasks()
            running = tasks.get("running", 0)
            pending = tasks.get("pending", 0)
            today = date.today().isoformat()
            done_today = sum(
                1 for r in tasks.get("rows", [])
                if r.get("status", "").lower() in ("complete", "completed")
                and r.get("ts", "").startswith(today)
            )
            return running, pending, done_today
        except Exception:
            return 0, 0, 0

    def _fetch_backfill():
        try:
            from panes.tasks import fetch_backfill_progress
            return fetch_backfill_progress()
        except Exception:
            return None

    def _fetch_agents():
        try:
            import grove_reader
            return grove_reader.grove_agents()
        except Exception:
            return []

    def _fetch_sysinfo():
        try:
            from panes.overview import fetch_sysinfo
            return fetch_sysinfo()
        except Exception:
            return {"cpu": 0, "mem": 0, "disk": 0, "temp": 0}

    with ThreadPoolExecutor(max_workers=7) as pool:
        f_unread   = pool.submit(_fetch_unread)
        f_mentions = pool.submit(_fetch_mentions)
        f_flags    = pool.submit(_fetch_flags)
        f_tasks    = pool.submit(_fetch_tasks)
        f_backfill = pool.submit(_fetch_backfill)
        f_agents   = pool.submit(_fetch_agents)
        f_sysinfo  = pool.submit(_fetch_sysinfo)

    data.unread_channels          = f_unread.result()
    data.mentions                 = f_mentions.result()
    data.open_flags               = f_flags.result()
    data.running_tasks, data.pending_tasks, data.done_today = f_tasks.result()
    data.backfill                 = f_backfill.result()
    data.agents                   = f_agents.result()
    data.sysinfo                  = f_sysinfo.result()

    return data




class _DeskRefreshed(Message):
    def __init__(self, data: DeskData) -> None:
        super().__init__()
        self.data = data


class DeskPane(Container):
    """Left column for Home — live Desk widget. Refreshes every 5s + on NOTIFY."""

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
        self._listening = False

    def compose(self):
        yield Static("", id="desk-content", markup=True)

    def on_mount(self) -> None:
        self._fetch()
        self.set_interval(5, self._fetch)
        self._start_notify_listener()

    @work(thread=True, exit_on_error=False)
    def _fetch(self) -> None:
        data = fetch_desk_data()
        self.post_message(_DeskRefreshed(data))

    @work(thread=True, exit_on_error=False)
    def _start_notify_listener(self) -> None:
        import grove_db
        self._listening = True
        try:
            conn = grove_db.listen_connection()
            cur  = conn.cursor()
            cur.execute("LISTEN grove_channel")
            while self._listening:
                if select.select([conn], [], [], 1.0)[0]:
                    conn.poll()
                    if conn.notifies:
                        conn.notifies.clear()
                        self._fetch()
        except Exception:
            pass

    def on_unmount(self) -> None:
        self._listening = False

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
        event.stop()
        nav = getattr(event, "nav_target", None) or ""
        if nav == "+":
            from widgets.card_builder_modal import CardBuilderModal
            self.app.push_screen(CardBuilderModal())
        else:
            from widgets.card_expand_modal import CardExpandModal
            from widgets.card_grid import BUILTIN_CARDS, LAUNCHER_CARDS
            _labels = {cid: lbl for cid, lbl in BUILTIN_CARDS}
            _labels.update({cid: lbl for cid, lbl, _ in LAUNCHER_CARDS})
            label = _labels.get(event.card_id, event.card_id)
            self.app.push_screen(CardExpandModal(event.card_id, label))

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
