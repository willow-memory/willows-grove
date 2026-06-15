"""panes/chat_admin.py — channel create/archive helpers (pure + thin DB).
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import re

PROTECTED_CHANNELS = frozenset({
    "general", "dispatch", "architecture", "handoffs", "fleet", "alerts", "upstream",
})

_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,47}$")


def normalize_channel_name(raw: str) -> str | None:
    """Strip #, lowercase, spaces→hyphens; reject invalid / reserved / dm: names."""
    if not raw or not raw.strip():
        return None
    lowered = raw.strip().lower()
    if lowered.startswith("dm:"):
        return None
    name = lowered.lstrip("#")
    name = re.sub(r"\s+", "-", name)
    name = re.sub(r"[^a-z0-9_-]", "", name)
    name = name.strip("-_")
    if not name or name.startswith("dm"):
        return None
    if not _NAME_RE.match(name):
        return None
    if name in PROTECTED_CHANNELS:
        return None
    return name


def can_archive_channel(name: str) -> bool:
    if not name or name in PROTECTED_CHANNELS:
        return False
    return True
