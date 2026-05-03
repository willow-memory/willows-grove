"""widgets/projects_nav.py — data layer and widget classes for Projects ContextPanel nav.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from pathlib import Path

from textual import work
from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Label, Rule, Static


# (card_id, label, nav_target)
_NAV_ROWS: list[tuple[str, str, str]] = [
    ("tasks",   "Tasks",   "#pane-tasks"),
    ("agents",  "Agents",  "#pane-agents"),
    ("routing", "Routing", "#pane-routing"),
    ("skills",  "Skills",  "#pane-skills"),
    ("logs",    "Logs",    "#pane-logs"),
]

_ROW_COLORS: dict[str, str] = {
    "green":  "#3fb950",
    "yellow": "#d29922",
    "dim":    "#8b949e",
    "":       "#8b949e",
}


def _fetch_nav_counts() -> dict[str, dict]:
    """Return live counts for all 5 nav rows. Never raises.

    Returns {card_id: {"count": str, "state": str}}.
    """
    out: dict[str, dict] = {cid: {"count": "—", "state": "dim"} for cid, _, _ in _NAV_ROWS}

    # Tasks — running count
    try:
        from panes.tasks import fetch_tasks
        t = fetch_tasks()
        running = t.get("running", 0)
        out["tasks"] = {"count": str(running), "state": "yellow" if running > 0 else "dim"}
    except Exception:
        pass

    try:
        import grove_reader as _gr
    except Exception:
        _gr = None  # type: ignore

    # Agents — active count
    if _gr is not None:
        try:
            agents = _gr.grove_agents()
            count = len(agents)
            out["agents"] = {"count": str(count), "state": "green" if count > 0 else "dim"}
        except Exception:
            pass

    # Routing — recent decision count
    if _gr is not None:
        try:
            decisions = _gr.routing_decisions()
            out["routing"] = {"count": str(len(decisions)), "state": "dim"}
        except Exception:
            pass

    # Skills — count .md files in ~/.willow/skills/
    try:
        skills_dir = Path.home() / ".willow" / "skills"
        if skills_dir.exists():
            count = len(list(skills_dir.glob("*.md")))
            out["skills"] = {"count": str(count), "state": "dim"}
        else:
            out["skills"] = {"count": "—", "state": "dim"}
    except Exception:
        pass

    # Logs — always live
    out["logs"] = {"count": "live", "state": "dim"}

    return out


class _NavRefreshed(Message):
    def __init__(self, data: dict[str, dict]) -> None:
        super().__init__()
        self.data: dict[str, dict] = data


class ProjectsNavRow(Widget):
    """Single focusable nav row: dot + label + count badge."""

    can_focus = True

    BINDINGS = [("enter", "activate", "Open")]

    DEFAULT_CSS = """
    ProjectsNavRow {
        height: 1;
        width: 1fr;
        padding: 0 1;
    }
    ProjectsNavRow:focus {
        background: #21262d;
    }
    """

    def __init__(self, card_id: str, label: str, nav_target: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._card_id    = card_id
        self._label      = label
        self._nav_target = nav_target
        self._count      = "—"
        self._state      = "dim"

    def compose(self) -> ComposeResult:
        yield Static("", id=f"pnrt-{self._card_id}", markup=True)

    def on_mount(self) -> None:
        self._redraw()

    def _redraw(self) -> None:
        from textual.css.query import NoMatches
        color = _ROW_COLORS.get(self._state, "#8b949e")
        dot   = f"[{color}]●[/]"
        text  = f"{dot} {self._label:<12} [{color}]{self._count}[/]"
        try:
            self.query_one(f"#pnrt-{self._card_id}", Static).update(text)
        except NoMatches:
            pass

    def update_row(self, count: str, state: str) -> None:
        self._count = count
        self._state = state
        self._redraw()

    def action_activate(self) -> None:
        from widgets.card_grid import CardActivated
        self.post_message(CardActivated(self._card_id, self._nav_target))

    def on_click(self) -> None:
        self.action_activate()


class ProjectsNav(Widget):
    """Left-panel navigator for the Projects target. Polls counts every 10s."""

    DEFAULT_CSS = """
    ProjectsNav {
        width: 1fr;
        height: 1fr;
        padding: 1 0;
    }
    ProjectsNav #pn-header {
        color: #58a6ff;
        text-style: bold;
        padding: 0 1;
    }
    ProjectsNav Rule {
        margin: 0;
        color: #30363d;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("PROJECTS", id="pn-header")
        yield Rule()
        for card_id, label, nav in _NAV_ROWS:
            yield ProjectsNavRow(card_id, label, nav, id=f"pnrow-{card_id}")

    def on_mount(self) -> None:
        self._fetch()
        self.set_interval(10, self._fetch)

    @work(thread=True)
    def _fetch(self) -> None:
        data = _fetch_nav_counts()
        self.post_message(_NavRefreshed(data))

    def on__nav_refreshed(self, event: _NavRefreshed) -> None:
        from textual.css.query import NoMatches
        for card_id, _, _ in _NAV_ROWS:
            row_data = event.data.get(card_id, {})
            try:
                row = self.query_one(f"#pnrow-{card_id}", ProjectsNavRow)
                row.update_row(
                    row_data.get("count", "—"),
                    row_data.get("state", "dim"),
                )
            except NoMatches:
                pass
