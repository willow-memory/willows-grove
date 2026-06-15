"""panes/chat_modals.py — in-context modals for chat admin.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Input, Label, Static

from grove.theme_textual import ACCENT, BG, BORDER, PRIMARY, SECONDARY


class _PanelBox(Container):
    can_focus = True


class ChannelCreateModal(ModalScreen[str | None]):
    """Prompt for a new text channel name (no #). Esc cancels."""

    DEFAULT_CSS = f"""
    ChannelCreateModal {{
        align: center middle;
    }}
    ChannelCreateModal #create-box {{
        width: 44;
        height: auto;
        border: solid {BORDER};
        background: {BG};
        padding: 1 2;
    }}
    ChannelCreateModal Label {{
        color: {PRIMARY};
        margin-bottom: 1;
    }}
    ChannelCreateModal Input {{
        border: tall {BORDER};
    }}
    ChannelCreateModal Input:focus {{
        border: tall {ACCENT};
    }}
    """

    def compose(self) -> ComposeResult:
        with Container(id="create-box"):
            yield Label("New text channel  [dim](letters, numbers, hyphen)[/]", markup=True)
            yield Input(placeholder="e.g. my-project", id="create-name")

    def on_mount(self) -> None:
        self.query_one("#create-name", Input).focus()

    @on(Input.Submitted, "#create-name")
    def _submit(self, event: Input.Submitted) -> None:
        value = event.value.strip()
        self.dismiss(value if value else None)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)
            event.prevent_default()
            event.stop()


class CommandPanelModal(ModalScreen[None]):
    """Plain-text mod command output (:help, :channels archived, …). Esc closes."""

    BINDINGS = [
        Binding("escape", "dismiss", "Close", show=False),
        Binding("enter", "dismiss", "Close", show=False),
        Binding("q", "dismiss", "Close", show=False),
    ]

    DEFAULT_CSS = f"""
    CommandPanelModal {{
        align: center middle;
    }}
    CommandPanelModal #panel-box {{
        width: 62;
        max-height: 20;
        border: solid {BORDER};
        background: {BG};
        padding: 1 2;
    }}
    CommandPanelModal #panel-title {{
        color: {ACCENT};
        text-style: bold;
        margin-bottom: 1;
    }}
    CommandPanelModal #panel-body {{
        height: auto;
        max-height: 14;
    }}
    CommandPanelModal #panel-hint {{
        color: {SECONDARY};
        margin-top: 1;
    }}
    """

    def __init__(self, title: str, body: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._title = title
        self._body = body

    def compose(self) -> ComposeResult:
        with _PanelBox(id="panel-box"):
            yield Static(Text(self._title, style="bold"), id="panel-title")
            with VerticalScroll(id="panel-body"):
                yield Static(Text(self._body))
            yield Static(Text("Esc · Enter · q — close", style="dim"), id="panel-hint")

    def on_mount(self) -> None:
        self.query_one("#panel-box", _PanelBox).focus()
