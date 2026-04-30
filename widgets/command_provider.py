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
