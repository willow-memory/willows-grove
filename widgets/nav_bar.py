"""widgets/nav_bar.py — NavBar: horizontal nav strip + NavChanged message.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.css.query import NoMatches
from textual.message import Message
from textual.widgets import Static


NAV_TARGETS: list[str] = [
    "home", "chat", "projects", "knowledge",
    "providers", "health", "settings", "help",
]


class NavChanged(Message):
    def __init__(self, target: str) -> None:
        super().__init__()
        self.target = target


class NavItem(Static):
    """Single clickable nav label. Posts NavChanged on click."""

    DEFAULT_CSS = """
    NavItem {
        height: 1;
        padding: 0 1;
        color: #8b949e;
    }
    NavItem:hover {
        background: #21262d;
        color: #c9d1d9;
    }
    NavItem.-active-nav {
        color: #58a6ff;
        text-style: bold;
    }
    NavItem#nav-logo {
        color: #3fb950;
        text-style: bold;
        padding: 0 2;
    }
    """

    def __init__(self, label: str, target: str, **kwargs) -> None:
        super().__init__(label, **kwargs)
        self._target = target

    def on_click(self) -> None:
        self.post_message(NavChanged(self._target))


class NavBar(Horizontal):
    """Single-row nav strip. Emits NavChanged on click or highlight()."""

    DEFAULT_CSS = """
    NavBar {
        height: 1;
        background: #161b22;
        padding: 0 0;
    }
    NavBar #nav-vitals {
        width: 1fr;
        text-align: right;
        color: #8b949e;
        padding: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield NavItem("◆", "home", id="nav-logo")
        for target in NAV_TARGETS:
            yield NavItem(target.capitalize(), target, id=f"nav-{target}")
        yield Static("", id="nav-vitals")

    def on_mount(self) -> None:
        self.highlight("home")

    def on_nav_changed(self, event: NavChanged) -> None:
        self.highlight(event.target)

    def highlight(self, target: str) -> None:
        """Update visual active state without emitting NavChanged."""
        for t in NAV_TARGETS:
            try:
                item = self.query_one(f"#nav-{t}", NavItem)
                if t == target:
                    item.add_class("-active-nav")
                else:
                    item.remove_class("-active-nav")
            except NoMatches:
                pass  # widget not yet mounted

    def set_vitals(self, text: str) -> None:
        try:
            self.query_one("#nav-vitals", Static).update(text)
        except NoMatches:
            pass  # widget not yet mounted
