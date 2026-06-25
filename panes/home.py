"""panes/home.py — DeskPane + dense HomeGrid (wave 2).
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from rich.markup import escape as _e
from textual import work
from textual.app import ComposeResult
from textual.containers import Container
from textual.message import Message
from textual.widgets import Static

import grove_db
import grove_reader
from grove.apps.card_builder.values import resolve_subtitle
from grove.apps.hero_stats import read_sysinfo
from grove.theme_textual import ACCENT, DEGRADED, HEALTHY, IDLE, INPUT_BG, PRIMARY, SECONDARY, UNREAD
from widgets.card_store import PLUS_CARD, PLUS_CARD_ID, load_home_cards, seed_catalog


@dataclass
class DeskData:
    running_tasks: int = 0
    pending_tasks: int = 0
    done_today: int = 0
    agents: list[dict] = field(default_factory=list)
    sysinfo: dict = field(default_factory=lambda: {"cpu": 0, "mem": 0, "disk": 0, "temp": 0})


def _agent_dot(age_secs: int) -> str:
    if age_secs < 120:
        return f"[{HEALTHY}]●[/]"
    if age_secs < 900:
        return f"[{DEGRADED}]◐[/]"
    return f"[{IDLE}]○[/]"


def _format_age(age_secs: int) -> str:
    if age_secs < 3600:
        return f"{age_secs // 60}m ago"
    return f"{age_secs // 3600}h ago"


def fetch_desk_data() -> DeskData:
    """Live desk fields from Grove + tasks + host. Never raises."""
    data = DeskData()
    conn = None
    try:
        conn = grove_db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT
                COUNT(*) FILTER (WHERE status IN ('pending','queued')) AS pending,
                COUNT(*) FILTER (WHERE status = 'running') AS running
            FROM public.tasks
        """)
        row = cur.fetchone()
        data.pending_tasks = row[0] or 0
        data.running_tasks = row[1] or 0
        today = date.today().isoformat()
        cur.execute("""
            SELECT COUNT(*) FROM public.tasks
            WHERE status IN ('complete','completed')
              AND created_at::date = %s::date
        """, (today,))
        data.done_today = cur.fetchone()[0] or 0
    except Exception:
        pass
    finally:
        if conn is not None:
            grove_db.release_connection(conn)
    try:
        data.agents = grove_reader.grove_agents()[:6]
    except Exception:
        pass
    try:
        data.sysinfo, _ = read_sysinfo()
    except Exception:
        pass
    return data


def render_desk(data: DeskData) -> str:
    """Plain section labels — RUNNING / SYSTEM only."""
    lines: list[str] = []

    lines.append(f"[bold {ACCENT}]RUNNING[/]")
    if data.running_tasks == 0 and data.pending_tasks == 0:
        lines.append(f"  [dim {SECONDARY}]idle[/]")
    else:
        lines.append(
            f"  [{PRIMARY}]{data.running_tasks} running  {data.pending_tasks} pending[/]"
        )
    lines.append("")

    if data.done_today > 0:
        lines.append(f"[bold {ACCENT}]DONE TODAY[/]")
        noun = "tasks" if data.done_today != 1 else "task"
        lines.append(f"  [{PRIMARY}]{data.done_today} {noun}[/]")
        lines.append("")

    lines.append(f"[bold {ACCENT}]SYSTEM[/]")
    if not data.agents:
        lines.append(f"  [dim {SECONDARY}]no agents on the bus[/]")
    else:
        for a in data.agents[:4]:
            dot = _agent_dot(a.get("age_secs", 9999))
            sender = a.get("sender", "")[:12]
            age_str = _format_age(a.get("age_secs", 0))
            lines.append(f"  {dot} [{PRIMARY}]{_e(sender):<12}[/] [dim {SECONDARY}]{age_str}[/]")
    cpu = data.sysinfo.get("cpu", 0)
    mem = data.sysinfo.get("mem", 0)
    lines.append(f"  [dim {SECONDARY}]cpu {cpu}%  mem {mem}%[/]")
    return "\n".join(lines)


class _DeskRefreshed(Message):
    def __init__(self, text: str) -> None:
        super().__init__()
        self.text = text


class DeskPane(Container):
    """Left column on Home — live RUNNING / SYSTEM."""

    DEFAULT_CSS = """
    DeskPane {
        width: 1fr;
        height: 1fr;
        padding: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("[dim]loading desk…[/]", id="desk-content", markup=True)

    def on_mount(self) -> None:
        self.set_interval(5.0, self._fetch)
        self._fetch()

    @work(thread=True, exit_on_error=False)
    def _fetch(self) -> None:
        text = render_desk(fetch_desk_data())
        self.post_message(_DeskRefreshed(text))

    def on__desk_refreshed(self, event: _DeskRefreshed) -> None:
        self.query_one("#desk-content", Static).update(event.text)


class CardActivated(Message):
    """Home grid cell clicked — nav target or #pane-* internal id."""

    def __init__(self, card_id: str, nav_target: str) -> None:
        super().__init__()
        self.card_id = card_id
        self.nav_target = nav_target


# Category → (glyph, left-border-color, css-class-suffix)
_CAT: dict[str, tuple[str, str, str]] = {
    "work":      ("◈", ACCENT,    "work"),
    "dev":       ("⚙", HEALTHY,   "dev"),
    "knowledge": ("◇", UNREAD,    "knowledge"),
    "tasks":     ("▸", PRIMARY,   "tasks"),
    "system":    ("·", SECONDARY, "system"),
    "custom":    ("◆", SECONDARY, "custom"),
}
_CAT_DEFAULT = ("·", SECONDARY, "custom")


class _CardCell(Static):
    """Launcher card — glyph + label + dim subline, category-accented left border."""

    DEFAULT_CSS = f"""
    _CardCell {{
        height: 6;
        border: round {SECONDARY};
        padding: 1 1 0 1;
        content-align: left top;
    }}
    _CardCell:hover {{
        border: round {ACCENT};
        background: {INPUT_BG};
    }}
    _CardCell.plus-card {{
        border: round {ACCENT};
        content-align: center middle;
    }}
    _CardCell.cat-work      {{ border: round {ACCENT};    background: #2d1f40; }}
    _CardCell.cat-dev       {{ border: round {HEALTHY};   background: #1a2e1a; }}
    _CardCell.cat-knowledge {{ border: round {UNREAD};    background: #2e2800; }}
    _CardCell.cat-tasks     {{ border: round {PRIMARY};   background: #2a2a2a; }}
    _CardCell.cat-system    {{ border: round {SECONDARY}; background: #242424; }}
    _CardCell.cat-custom    {{ border: round {SECONDARY}; background: #242424; }}
    """

    def __init__(
        self,
        card_id: str,
        label: str,
        sub: str,
        nav_target: str,
        *,
        category: str = "custom",
        plus: bool = False,
        **kwargs,
    ) -> None:
        glyph, glyph_color, cat_slug = _CAT.get(category, _CAT_DEFAULT)
        css_classes = f"cat-{cat_slug}"
        if plus:
            css_classes = "plus-card"
        self._label = label
        self._glyph_line = f"[{glyph_color}]{glyph}[/] [bold {ACCENT}]{label}[/]"
        super().__init__(
            f"{self._glyph_line}\n[dim {SECONDARY}]{sub}[/]",
            markup=True,
            classes=css_classes,
            **kwargs,
        )
        self.card_id = card_id
        self._nav_target = nav_target

    def set_subline(self, sub: str) -> None:
        self.update(f"{self._glyph_line}\n[dim {SECONDARY}]{_e(sub)}[/]")

    def on_click(self) -> None:
        if self._nav_target:
            self.post_message(CardActivated(self.card_id, self._nav_target))


class HomeGrid(Container):
    """Center Home band — SOIL-backed card grid + built-ins + add card."""

    DEFAULT_CSS = """
    HomeGrid {
        width: 1fr;
        height: 1fr;
        layout: grid;
        grid-size: 3;
        grid-gutter: 1 1;
        padding: 1;
    }
    """

    def on_mount(self) -> None:
        seed_catalog()
        self.refresh_cards()
        self.set_interval(15.0, self._refresh_card_subs)
        self._refresh_card_subs()

    def refresh_cards(self) -> None:
        """Rebuild grid cells from card store."""
        for cell in list(self.query(_CardCell)):
            cell.remove()
        for card in load_home_cards():
            card_id = card["id"]
            sub = resolve_subtitle(card)
            self.mount(
                _CardCell(
                    card_id,
                    card["label"],
                    sub,
                    card.get("nav_target") or "",
                    category=card.get("category", "custom"),
                    id=f"cell-{card_id}",
                )
            )
        plus = PLUS_CARD
        self.mount(
            _CardCell(
                plus["id"],
                plus["label"],
                plus.get("subtitle") or "Add card",
                plus["nav_target"],
                category="system",
                plus=True,
                id=f"cell-{PLUS_CARD_ID}",
            )
        )

    @work(thread=True, exit_on_error=False)
    def _refresh_card_subs(self) -> None:
        from grove.apps.user_board import board_summary, fetch_user_board

        subs: dict[str, str] = {}
        for card in load_home_cards():
            if card["id"] == "user-todos":
                try:
                    board = fetch_user_board(limit=1)
                    desk_sub = board_summary(board)
                    from grove.apps.upstream_steward import steward_summary
                    up = steward_summary()
                    if up:
                        desk_sub = f"{desk_sub} · {up}"
                    subs[card["id"]] = desk_sub
                except Exception:
                    subs[card["id"]] = "your command center"
            else:
                subs[card["id"]] = resolve_subtitle(card)
        self.post_message(_CardSubsUpdated(subs))

    def on__card_subs_updated(self, event: "_CardSubsUpdated") -> None:
        from textual.css.query import NoMatches
        for card_id, sub in event.subs.items():
            try:
                self.query_one(f"#cell-{card_id}", _CardCell).set_subline(sub)
            except NoMatches:
                pass


class _CardSubsUpdated(Message):
    def __init__(self, subs: dict[str, str]) -> None:
        super().__init__()
        self.subs = subs
