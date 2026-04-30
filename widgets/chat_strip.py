"""widgets/chat_strip.py — ChatStrip: persistent 1-line bottom bar.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from textual.css.query import NoMatches
from textual.widgets import Static

import grove_reader


def truncate_content(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1] + "…"


def format_strip_line(channel: str, sender: str, content: str, width: int) -> str:
    prefix = f"#{channel}  {sender}: "
    suffix = "  ▶ open"
    max_content = width - len(prefix) - len(suffix)
    if max_content < 4:
        return truncate_content(f"{prefix}{content}{suffix}", width)
    return f"{prefix}{truncate_content(content, max_content)}{suffix}"


class ChatStrip(Static):
    """Always-visible 1-line chat context bar at the bottom of the screen."""

    DEFAULT_CSS = """
    ChatStrip {
        height: 1;
        background: #161b22;
        border-top: solid #30363d;
        padding: 0 1;
        color: #8b949e;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("", **kwargs)
        self._channel = ""
        self._sender  = ""
        self._content = ""

    def on_mount(self) -> None:
        self.set_interval(10, self._poll)
        self._poll()

    def _poll(self) -> None:
        try:
            channels = grove_reader.grove_channels()
            if not channels:
                return
            ch = channels[0]["name"]
            msgs = grove_reader.grove_messages(ch, limit=1)
            if msgs:
                m = msgs[-1]
                self._channel = ch
                self._sender  = m.get("sender", "?")
                self._content = m.get("content", "")
                self._redraw()
        except Exception:
            pass

    def update_channel(self, channel: str) -> None:
        """Called by app when Chat pane changes active channel."""
        self._channel = channel
        self._redraw()

    def _redraw(self) -> None:
        width = self.size.width or 80
        line = format_strip_line(
            self._channel or "general",
            self._sender  or "—",
            self._content or "",
            width,
        )
        self.update(line)
