"""widgets/nav_bar.py — NavBar with 1–7 targets + vitals line.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.css.query import NoMatches
from textual.message import Message
from textual.widgets import Static

from grove.theme_textual import ACCENT, BG, HEALTHY, INPUT_BG, PRIMARY, SECONDARY

NAV_TARGETS: list[str] = [
    "home", "chat", "projects", "knowledge",
    "providers", "settings", "help",
]

NAV_LABELS: dict[str, str] = {
    "home": "Home",
    "chat": "Chat",
    "projects": "Projects",
    "knowledge": "Knowledge",
    "providers": "Providers",
    "settings": "Settings",
    "help": "Help",
}


class NavChanged(Message):
    def __init__(self, target: str) -> None:
        super().__init__()
        self.target = target


class NavItem(Static):
    """Single clickable nav item."""

    DEFAULT_CSS = f"""
    NavItem {{
        width: auto;
        padding: 0 1;
        color: {SECONDARY};
    }}
    NavItem:hover {{
        color: {PRIMARY};
        background: {BG};
    }}
    NavItem.-active {{
        color: {ACCENT};
        text-style: bold;
    }}
    """

    def __init__(self, index: int, target: str, **kwargs) -> None:
        label = NAV_LABELS.get(target, target.title())
        super().__init__(f"{index} {label}", markup=False, **kwargs)
        self._target = target

    def on_click(self) -> None:
        self.post_message(NavChanged(self._target))


class NavLogo(Static):
    """Home shortcut."""

    DEFAULT_CSS = f"""
    NavLogo {{
        width: auto;
        padding: 0 1;
        color: {HEALTHY};
    }}
    NavLogo:hover {{
        color: {ACCENT};
        background: {BG};
    }}
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("[bold]◆[/]", markup=True, **kwargs)

    def on_click(self) -> None:
        self.post_message(NavChanged("home"))


class NavBar(Horizontal):
    """Nav strip: logo + 1–7 targets + vitals."""

    DEFAULT_CSS = f"""
    NavBar {{
        height: 1;
        background: {INPUT_BG};
    }}
    NavBar #nav-links {{
        width: auto;
    }}
    NavBar #nav-vitals {{
        width: 1fr;
        padding: 0 1;
        color: {SECONDARY};
        text-align: right;
    }}
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._active = "home"

    def compose(self) -> ComposeResult:
        with Horizontal(id="nav-links"):
            yield NavLogo(id="nav-logo")
            for i, target in enumerate(NAV_TARGETS, start=1):
                yield NavItem(i, target, id=f"nav-{target}")
        yield Static("", id="nav-vitals", markup=True)

    def on_mount(self) -> None:
        self._update_active()

    def highlight(self, target: str) -> None:
        if target in NAV_TARGETS:
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
