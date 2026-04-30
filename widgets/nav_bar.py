"""widgets/nav_bar.py — NavBar: horizontal nav strip + NavChanged message.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Button, Static


NAV_TARGETS: list[str] = [
    "home", "chat", "projects", "knowledge",
    "providers", "health", "settings", "help",
]


class NavChanged(Message):
    def __init__(self, target: str) -> None:
        self.target = target
        super().__init__()


class NavBar(Horizontal):
    """Single-row nav strip. Emits NavChanged on click or highlight()."""

    DEFAULT_CSS = """
    NavBar {
        height: 1;
        background: #161b22;
        border-bottom: solid #30363d;
        padding: 0 1;
    }
    NavBar Button {
        height: 1;
        min-width: 0;
        border: none;
        background: transparent;
        color: #8b949e;
        padding: 0 1;
    }
    NavBar Button:hover {
        background: #21262d;
        color: #c9d1d9;
    }
    NavBar Button.-active-nav {
        color: #58a6ff;
        text-style: bold;
    }
    NavBar #nav-logo {
        color: #3fb950;
        text-style: bold;
        padding: 0 2 0 0;
    }
    NavBar #nav-vitals {
        width: 1fr;
        text-align: right;
        color: #8b949e;
        padding: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Button("◆", id="nav-logo")
        for target in NAV_TARGETS:
            yield Button(target.capitalize(), id=f"nav-{target}")
        yield Static("", id="nav-vitals")

    def on_mount(self) -> None:
        self.highlight("home")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id or ""
        if btn_id == "nav-logo":
            self.highlight("home")
            self.post_message(NavChanged("home"))
        elif btn_id.startswith("nav-"):
            target = btn_id[4:]
            if target in NAV_TARGETS:
                self.highlight(target)
                self.post_message(NavChanged(target))

    def highlight(self, target: str) -> None:
        """Update visual active state without emitting NavChanged."""
        for t in NAV_TARGETS:
            try:
                btn = self.query_one(f"#nav-{t}", Button)
                if t == target:
                    btn.add_class("-active-nav")
                else:
                    btn.remove_class("-active-nav")
            except Exception:
                pass

    def set_vitals(self, text: str) -> None:
        try:
            self.query_one("#nav-vitals", Static).update(text)
        except Exception:
            pass
