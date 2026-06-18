"""widgets/context_panel.py — left rail; DeskPane on Home only.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Static

from grove.theme_textual import BORDER
from panes.home import DeskPane


class ContextPanel(Container):
    """Context-specific left column — Desk on Home; hidden elsewhere (wave 2)."""

    DEFAULT_CSS = f"""
    ContextPanel {{
        width: 26;
        height: 1fr;
        border-right: solid {BORDER};
    }}
    ContextPanel.-hidden {{
        display: none;
    }}
    """

    def compose(self) -> ComposeResult:
        yield DeskPane(id="ctx-desk")
        yield Static("", id="ctx-empty", markup=True)

    def show_target(self, target: str) -> None:
        if target == "home":
            self.remove_class("-hidden")
        else:
            self.add_class("-hidden")
