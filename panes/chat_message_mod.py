"""panes/chat_message_mod.py — message mod helpers (flags display + toggles).
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from grove.theme_textual import SECONDARY, UNREAD

MOD_FLAGS = frozenset({"urgent", "needs-reply", "starred", "resolved", "read"})


def flag_prefix(flags: set[str] | frozenset[str] | None) -> tuple[str, str]:
    """Compact mod markers left of message body (plain + markup)."""
    if not flags:
        return "", ""
    tags: list[str] = []
    if "urgent" in flags:
        tags.append("!")
    if "needs-reply" in flags:
        tags.append("?")
    if "starred" in flags:
        tags.append("*")
    if "resolved" in flags:
        tags.append("v")
    if not tags:
        return "", ""
    plain = "".join(tags) + " "
    markup = f"[{UNREAD}]{''.join(tags)}[/] "
    return plain, markup


def flag_status_label(flags: set[str] | frozenset[str] | None) -> str:
    if not flags:
        return ""
    parts = []
    for name in ("urgent", "needs-reply", "starred", "resolved"):
        if name in flags:
            parts.append(name)
    return ", ".join(parts)
