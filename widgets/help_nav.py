"""widgets/help_nav.py — Help section nav left-panel.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static


class HelpSectionSelected(Message):
    """Posted when the user selects a help section."""

    def __init__(self, section: str) -> None:
        super().__init__()
        self.section = section


class HelpNavRow(Widget):
    can_focus = True
    BINDINGS = [Binding("enter", "activate", "Go")]

    DEFAULT_CSS = """
    HelpNavRow {
        height: 1;
        width: 1fr;
        padding: 0 1;
    }
    HelpNavRow:hover {
        color: #c9d1d9;
        background: #21262d;
    }
    HelpNavRow:focus {
        background: #21262d;
    }
    """

    def __init__(self, section: str, label: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._section = section
        self._label = label

    def compose(self) -> ComposeResult:
        yield Static(self._label, id=f"hnr-{self._section}-label")

    def action_activate(self) -> None:
        self.post_message(HelpSectionSelected(self._section))

    def on_click(self) -> None:
        self.action_activate()


class HelpNav(Widget):
    DEFAULT_CSS = """
    HelpNav {
        width: 1fr;
        height: 1fr;
        padding: 1 0;
    }
    HelpNav #hn-header {
        color: #58a6ff;
        text-style: bold;
        padding: 0 1;
    }
    """

    _SECTIONS: list[tuple[str, str]] = [
        ("overview",   "Overview"),
        ("navigation", "Navigation"),
        ("shortcuts",  "Shortcuts"),
        ("privacy",    "Privacy & Consent"),
    ]

    def compose(self) -> ComposeResult:
        yield Static("HELP", id="hn-header")
        for section, label in self._SECTIONS:
            yield HelpNavRow(section, label, id=f"hnr-row-{section}")
