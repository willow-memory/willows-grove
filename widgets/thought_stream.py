"""widgets/thought_stream.py — ThoughtStream: live agent message feed + SessionStats.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from textual import work
from textual.message import Message
from textual.widgets import RichLog, Static

import grove_reader


_SESSION_ANCHOR = Path.home() / ".willow" / "session_anchor.json"


def _load_known_agents() -> frozenset[str]:
    """Return agent names to watch in ThoughtStream.

    Priority:
    1. GROVE_KNOWN_AGENTS env var  — comma-separated list, always wins
    2. DB heartbeat senders         — discovered dynamically from grove.messages
    3. Empty set                    — show nothing rather than crash
    """
    env = os.environ.get("GROVE_KNOWN_AGENTS", "").strip()
    if env:
        return frozenset(n.strip().lower() for n in env.split(",") if n.strip())
    try:
        return frozenset(a["sender"].lower() for a in grove_reader.grove_agents())
    except Exception:
        return frozenset()


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


class _StreamFetched(Message):
    def __init__(self, msgs: list[dict]) -> None:
        super().__init__()
        self.msgs = msgs


class _AgentsRefreshed(Message):
    def __init__(self, agents: frozenset[str]) -> None:
        super().__init__()
        self.agents = agents


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
        self._known_agents: frozenset[str] = frozenset()

    def on_mount(self) -> None:
        self._refresh_agents()
        self.set_interval(10,  self._fetch)
        self.set_interval(60,  self._refresh_agents)

    @work(thread=True)
    def _refresh_agents(self) -> None:
        self.post_message(_AgentsRefreshed(_load_known_agents()))

    @work(thread=True)
    def _fetch(self) -> None:
        if not self._known_agents:
            return
        try:
            msgs = grove_reader.grove_messages_all_agents(
                known_agents=self._known_agents,
                last_id=self._last_id,
                limit=20,
            )
        except Exception:
            msgs = []
        self.post_message(_StreamFetched(msgs))

    def on__agents_refreshed(self, event: _AgentsRefreshed) -> None:
        self._known_agents = event.agents
        if self._known_agents and self._last_id == 0:
            self._fetch()

    def on__stream_fetched(self, event: _StreamFetched) -> None:
        for m in event.msgs:
            sender  = m.get("sender", "?")
            content = m.get("content", "")
            if len(content) > 60:
                content = content[:59] + "…"
            self.write(f"[dim cyan]{sender}[/]  {content}")
            self._last_id = max(self._last_id, m.get("id", 0))


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
