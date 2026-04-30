"""widgets/nav_bar.py — NavBar: horizontal nav strip + NavChanged message.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from textual.app import ComposeResult
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


class NavBar(Static):
    """Single-row nav strip rendered as one line of markup."""

    DEFAULT_CSS = """
    NavBar {
        height: 1;
        background: #161b22;
        color: #8b949e;
        padding: 0 1;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("", markup=True, **kwargs)
        self._active = "home"
        self._vitals = ""

    def on_mount(self) -> None:
        self._redraw()

    def highlight(self, target: str) -> None:
        self._active = target
        self._redraw()

    def set_vitals(self, text: str) -> None:
        self._vitals = text
        self._redraw()

    def _redraw(self) -> None:
        logo = "[bold green]◆[/]"
        items = []
        for target in NAV_TARGETS:
            label = target.capitalize()
            if target == self._active:
                items.append(f"[bold #58a6ff]{label}[/]")
            else:
                items.append(f"[#8b949e]{label}[/]")
        nav_part = f"{logo}  " + "  ".join(items)
        if self._vitals:
            line = f"{nav_part}  [dim]{self._vitals}[/]"
        else:
            line = nav_part
        self.update(line)
