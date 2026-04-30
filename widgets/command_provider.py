"""widgets/command_provider.py — Willow command palette provider.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from typing import Callable


_NAV_COMMANDS = [
    ("Go to Home",      "home go home",        "home"),
    ("Go to Chat",      "chat messages grove",  "chat"),
    ("Go to Projects",  "projects tasks",       "projects"),
    ("Go to Knowledge", "knowledge kb atoms",   "knowledge"),
    ("Go to Providers", "providers models api", "providers"),
    ("Go to Health",    "health status vitals", "health"),
    ("Go to Settings",  "settings consent",     "settings"),
    ("Go to Help",      "help docs",            "help"),
]

_ACTION_COMMANDS = [
    ("Refresh", "refresh reload", "refresh"),
    ("Quit",    "quit exit",      "quit"),
]


def _nav_hits() -> list[dict]:
    """Return nav hit dicts — one per top-level tab."""
    return [
        {"display": label, "text": text, "target": target}
        for label, text, target in _NAV_COMMANDS
    ]


def _action_hits() -> list[dict]:
    """Return action hit dicts (refresh, quit)."""
    return [
        {"display": label, "text": text, "action": action}
        for label, text, action in _ACTION_COMMANDS
    ]


def _channel_hits(fetch_fn: Callable) -> list[dict]:
    """Return channel hit dicts. fetch_fn() must return list[dict] with 'name' key."""
    try:
        channels = fetch_fn()
        return [
            {
                "display": f"Open #{ch['name']}",
                "text":    f"open {ch['name']}",
                "channel": ch["name"],
            }
            for ch in channels
        ]
    except Exception:
        return []


from functools import partial

from textual.command import Hit, Hits, Provider


class WillowCommandProvider(Provider):
    """Supplies nav, action, and channel hits to the Willow command palette."""

    _channel_data: list[dict]

    async def startup(self) -> None:
        """Fetch channels once when the palette opens."""
        try:
            import grove_reader
            self._channel_data = _channel_hits(grove_reader.grove_channels)
        except Exception:
            self._channel_data = []

    async def search(self, query: str) -> Hits:
        """Yield hits matching query across nav targets, actions, and channels."""
        matcher = self.matcher(query)

        for hit in _nav_hits():
            score = matcher.match(hit["text"])
            if score > 0:
                target = hit["target"]
                yield Hit(
                    score=score,
                    match_display=hit["display"],
                    command=partial(self.app.action_nav, target),
                )

        for hit in _action_hits():
            score = matcher.match(hit["text"])
            if score > 0:
                action_name = hit["action"]
                yield Hit(
                    score=score,
                    match_display=hit["display"],
                    command=getattr(self.app, f"action_{action_name}"),
                )

        for hit in getattr(self, "_channel_data", []):
            score = matcher.match(hit["text"])
            if score > 0:
                channel = hit["channel"]
                yield Hit(
                    score=score,
                    match_display=hit["display"],
                    command=partial(self._open_channel, channel),
                )

    async def _open_channel(self, channel: str) -> None:
        from panes.chat import ChatPane
        self.app.action_nav("chat")
        try:
            self.app.query_one(ChatPane)._open_channel(channel)
        except Exception:
            pass
