"""widgets/thought_stream.py — ThoughtStream: live agent message feed + SessionStats.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from textual.widgets import RichLog, Static

import grove_reader


KNOWN_AGENTS: frozenset[str] = frozenset([
    "hanuman", "heimdallr", "ganesha", "vishwakarma", "loki", "jeles",
])

_SESSION_ANCHOR = Path.home() / ".willow" / "session_anchor.json"


def is_agent_sender(sender: str, agents: frozenset[str] = KNOWN_AGENTS) -> bool:
    return sender.lower() in agents


def parse_session_stats(data: dict | None) -> str:
    if not data:
        return "[dim]no session data[/]"
    parts: list[str] = []
    written_at = data.get("written_at")
    if written_at:
        try:
            start = datetime.fromisoformat(written_at.replace("Z", "+00:00"))
            now   = datetime.now(tz=timezone.utc)
            delta = now - start.astimezone(timezone.utc)
            mins  = int(delta.total_seconds() // 60)
            parts.append(f"active {mins}m")
        except Exception:
            pass
    flags = data.get("open_flags")
    if flags is not None:
        color = "yellow" if flags > 0 else "green"
        parts.append(f"[{color}]{flags} flags[/{color}]")
    return "  ".join(parts) if parts else "[dim]session active[/]"


class ThoughtStream(RichLog):
    """Live feed of agent messages from grove.messages. Polls every 10s."""

    DEFAULT_CSS = """
    ThoughtStream {
        height: 6;
        border: round #30363d;
        margin: 1 0 0 0;
        padding: 0 1;
        overflow-y: auto;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(highlight=False, markup=True, wrap=True, **kwargs)
        self._last_id: int = 0

    def on_mount(self) -> None:
        self.set_interval(10, self._poll)
        self._poll()

    def _poll(self) -> None:
        try:
            msgs = grove_reader.grove_messages_all_agents(
                known_agents=KNOWN_AGENTS,
                last_id=self._last_id,
                limit=20,
            )
            for m in msgs:
                sender  = m.get("sender", "?")
                content = m.get("content", "")
                if len(content) > 60:
                    content = content[:59] + "…"
                self.write(f"[dim cyan]{sender}[/]  {content}")
                self._last_id = max(self._last_id, m.get("id", 0))
        except Exception:
            pass


class SessionStats(Static):
    """Session stats line: active time + open flag count. Refreshes every 30s."""

    DEFAULT_CSS = """
    SessionStats {
        height: 1;
        color: #8b949e;
        padding: 0 1;
        margin-top: 1;
    }
    """

    def on_mount(self) -> None:
        self.set_interval(30, self._refresh)
        self._refresh()

    def _refresh(self) -> None:
        try:
            data = json.loads(_SESSION_ANCHOR.read_text())
        except Exception:
            data = None
        self.update(parse_session_stats(data))
