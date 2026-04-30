"""panes/home.py — Placeholder panes for Home, HomeGrid, and Projects.
b17: WGRV1  ΔΣ=42
"""
from textual.widgets import Static


DESK_PLACEHOLDER = (
    "[ The Desk ]\n\n"
    "  ⚡ Needs Attention\n"
    "  ▶ In Progress\n"
    "  ✓ Done Today\n"
    "  📅 Calendar\n\n"
    "  Phase 2 fills this with live data."
)

HOMEGRID_PLACEHOLDER = (
    "[ Home Grid ]\n\n"
    "  Card grid launcher — Phase 3.\n\n"
    "  Each card opens an app or shows a live data feed.\n"
    "  Cards defined in cards.py are loaded here."
)

PROJECTS_PLACEHOLDER = (
    "[ Projects ]\n\n"
    "  Click a card to open the pane:\n\n"
    "  [Tasks]      [Agents]     [Routing]\n"
    "  [Skills]     [Logs]\n\n"
    "  Phase 3 adds live card grid from cards.py."
)


class DeskPane(Static):
    """Left column for Home. Phase 2 fills with live calendar/tasks/email."""

    DEFAULT_CSS = """
    DeskPane {
        width: 1fr;
        height: 1fr;
        padding: 1 2;
        color: #8b949e;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(DESK_PLACEHOLDER, **kwargs)


class HomeGrid(Static):
    """Center area for Home. Phase 3 replaces with live Textual card grid."""

    DEFAULT_CSS = """
    HomeGrid {
        width: 1fr;
        height: 1fr;
        padding: 1 2;
        color: #8b949e;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(HOMEGRID_PLACEHOLDER, **kwargs)


class ProjectsGrid(Static):
    """Center area for Projects nav. Phase 3 replaces with live card grid."""

    DEFAULT_CSS = """
    ProjectsGrid {
        width: 1fr;
        height: 1fr;
        padding: 1 2;
        color: #8b949e;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(PROJECTS_PLACEHOLDER, **kwargs)
