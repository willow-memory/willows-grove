"""widgets/nav_bar.py — NavBar: horizontal nav strip + NavChanged message.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.css.query import NoMatches
from textual.message import Message
from textual.widgets import Static

from widgets.file_menu import FileMenuModal


NAV_TARGETS: list[str] = [
    "home", "chat", "projects", "knowledge",
    "providers", "settings", "help",
]


class NavChanged(Message):
    def __init__(self, target: str) -> None:
        super().__init__()
        self.target = target


class NavItem(Static):
    """Single clickable nav item."""

    DEFAULT_CSS = """
    NavItem {
        width: auto;
        padding: 0 1;
        color: #8b949e;
    }
    NavItem:hover {
        color: #c9d1d9;
        background: #21262d;
    }
    NavItem.-active {
        color: #58a6ff;
        text-style: bold;
    }
    """

    def __init__(self, target: str, **kwargs) -> None:
        super().__init__(target.capitalize(), markup=False, **kwargs)
        self._target = target

    def on_click(self) -> None:
        self.post_message(NavChanged(self._target))


class NavLogo(Static):
    """Top-left logo — click to open File menu."""

    DEFAULT_CSS = """
    NavLogo {
        width: auto;
        padding: 0 1;
        color: #3fb950;
    }
    NavLogo:hover {
        color: #58a6ff;
        background: #21262d;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("[bold]◆[/]", markup=True, **kwargs)

    def on_click(self) -> None:
        async def _handle(action: str | None) -> None:
            if action == "quit":
                self.app.exit()
            elif action and action != "quit":
                self.app.notify(f"{action.capitalize()}: coming soon", timeout=2)

        self.app.push_screen(FileMenuModal(), _handle)


class NavBar(Horizontal):
    """Single-row nav strip with clickable items."""

    DEFAULT_CSS = """
    NavBar {
        height: 1;
        background: #161b22;
        padding: 0 0;
    }
    NavBar #nav-logo {
        width: auto;
        padding: 0 1;
        color: #3fb950;
    }
    NavBar #nav-vitals {
        width: 1fr;
        padding: 0 1;
        color: #8b949e;
        text-align: right;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._active = "home"

    def compose(self) -> ComposeResult:
        yield NavLogo(id="nav-logo")
        for target in NAV_TARGETS:
            yield NavItem(target, id=f"nav-{target}")
        yield Static("", id="nav-vitals", markup=True)

    def on_mount(self) -> None:
        self._update_active()

    def highlight(self, target: str) -> None:
        self._active = target
        self._update_active()

    def set_vitals(self, text: str) -> None:
        try:
            self.query_one("#nav-vitals", Static).update(text)
        except NoMatches:
            pass

    def _update_active(self) -> None:
        for target in NAV_TARGETS:
            try:
                item = self.query_one(f"#nav-{target}", NavItem)
                if target == self._active:
                    item.add_class("-active")
                else:
                    item.remove_class("-active")
            except NoMatches:
                pass
