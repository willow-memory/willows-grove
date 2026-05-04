"""widgets/file_menu.py — File menu modal launched from the top-left logo.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Static


class FileMenuAction(Message):
    def __init__(self, action: str) -> None:
        super().__init__()
        self.action = action


class FileMenuItem(Static):
    DEFAULT_CSS = """
    FileMenuItem {
        width: 1fr;
        padding: 0 2;
        color: #c9d1d9;
    }
    FileMenuItem:hover {
        background: #21262d;
        color: #58a6ff;
    }
    FileMenuItem.-separator {
        color: #30363d;
        padding: 0 1;
    }
    """

    def __init__(self, label: str, action: str | None = None, **kwargs) -> None:
        super().__init__(label, markup=False, **kwargs)
        self._action = action
        if action is None:
            self.add_class("-separator")

    def on_click(self, event) -> None:
        event.stop()
        if self._action:
            self.post_message(FileMenuAction(self._action))


class FileMenuModal(ModalScreen):
    DEFAULT_CSS = """
    FileMenuModal {
        align: left top;
        background: transparent;
    }
    FileMenuModal #file-menu {
        width: 20;
        height: auto;
        background: #161b22;
        border: solid #30363d;
        margin: 1 0 0 0;
        padding: 0;
    }
    FileMenuModal #menu-rule {
        color: #30363d;
        padding: 0 1;
    }
    FileMenuModal #menu-rule-2 {
        color: #30363d;
        padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
    ]

    def compose(self) -> ComposeResult:
        with Container(id="file-menu"):
            yield FileMenuItem("New",    "new")
            yield FileMenuItem("Save",   "save")
            yield FileMenuItem("Import", "import")
            yield FileMenuItem("Export", "export")
            yield FileMenuItem("Print",  "print")
            yield Static("──────────────────", id="menu-rule", markup=False)
            yield FileMenuItem("Quit",   "quit")

    def on_click(self) -> None:
        self.dismiss(None)

    def on_file_menu_action(self, event: FileMenuAction) -> None:
        self.dismiss(event.action)
