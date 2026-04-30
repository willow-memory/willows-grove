"""widgets/projects_nav.py — data layer and widget classes for Projects ContextPanel nav.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from pathlib import Path

from textual.message import Message


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
