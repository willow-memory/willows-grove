"""panes/chat_format.py — pure formatters for Discord-style Grove chat.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import os
from datetime import datetime

from rich.markup import escape as _e

from grove.theme import agent_color_index
from grove.theme_textual import ACCENT, PRIMARY, SECONDARY, UNREAD, xterm256

_COLLAPSE_MINUTES = 5
_BODY_INDENT = "    "
_TEXT_PRIORITY = {"general": 0, "architecture": 1, "handoffs": 2, "fleet": 3}
_TEXT_TYPES = frozenset({"group", "broadcast", "persona"})
_TYPED_CONTENT_PREFIXES = ("[image:", "[audio:", "[file:", "[code:")


def sender_color(name: str) -> str:
    return xterm256(agent_color_index(name))


def dm_channel_name(peer: str) -> str:
    peer = peer.strip().lstrip("@").lower()
    return f"dm:{peer}"


def dm_display_name(channel_name: str) -> str:
    if channel_name.startswith("dm:"):
        return f"@{channel_name[3:]}"
    return channel_name


def is_direct_channel(ch: dict) -> bool:
    return ch.get("channel_type") == "direct" or ch.get("name", "").startswith("dm:")


def peer_from_dm(channel_name: str) -> str | None:
    if channel_name.startswith("dm:"):
        return channel_name[3:]
    return None


def partition_channels(channels: list[dict]) -> tuple[list[dict], list[dict]]:
    """Split into text channels and direct messages (Discord sidebar)."""
    text: list[dict] = []
    dms: list[dict] = []
    for ch in channels:
        if is_direct_channel(ch):
            dms.append(ch)
        else:
            text.append(ch)

    def text_key(c: dict) -> tuple:
        n = c["name"]
        return (_TEXT_PRIORITY.get(n, 99), n)

    def dm_key(c: dict) -> tuple:
        return (-int(c.get("unread", 0)), dm_display_name(c["name"]).lower())

    return sorted(text, key=text_key), sorted(dms, key=dm_key)


def sort_channels(channels: list[dict]) -> list[dict]:
    """Flat list: text channels then DMs."""
    text, dms = partition_channels(channels)
    return text + dms


def _as_datetime(ts) -> datetime | None:
    if ts is None:
        return None
    if isinstance(ts, datetime):
        return ts
    s = str(ts).replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def _within_collapse_window(prev_ts, cur_ts, minutes: int = _COLLAPSE_MINUTES) -> bool:
    prev = _as_datetime(prev_ts)
    cur = _as_datetime(cur_ts)
    if prev is None or cur is None:
        return False
    return abs((cur - prev).total_seconds()) <= minutes * 60


def format_ts(ts) -> str:
    if ts is None:
        return ""
    if isinstance(ts, datetime):
        return ts.strftime("%H:%M")
    s = str(ts)
    return s[11:16] if len(s) >= 16 else s[:5]


def render_content(content: str) -> str:
    for prefix in _TYPED_CONTENT_PREFIXES:
        if content.startswith(prefix):
            kind = prefix[1:-1].upper()
            inner = content[len(prefix):]
            if inner.endswith("]"):
                inner = inner[:-1]
            path = inner.strip()
            ack = "✓" if os.path.exists(path) else "not found"
            return f"{kind}: {path} [{ack}]"
    return content


def _align_header(sender: str, ts: str, width: int) -> tuple[str, str]:
    width = max(24, width)
    gap = max(1, width - len(sender) - len(ts))
    pad = " " * gap
    color = sender_color(sender)
    plain = f"{sender}{pad}{ts}"
    markup = f"[bold {color}]{_e(sender)}[/]{pad}[{SECONDARY}]{ts}[/]"
    return plain, markup


def format_message_block(
    sender: str,
    content: str,
    created_at,
    *,
    width: int = 72,
    prev_sender: str | None = None,
    prev_ts=None,
    flags: set[str] | frozenset[str] | None = None,
) -> tuple[str, str]:
    from panes.chat_message_mod import flag_prefix

    ts = format_ts(created_at)
    body = render_content(content or "")
    f_plain, f_markup = flag_prefix(flags)
    collapsed = prev_sender == sender and _within_collapse_window(prev_ts, created_at)
    if collapsed:
        plain = f"{_BODY_INDENT}{f_plain}{body}"
        markup = f"{_BODY_INDENT}{f_markup}[{PRIMARY}]{_e(body)}[/]"
        return plain, markup

    header_plain, header_markup = _align_header(sender, ts, width)
    plain = f"{header_plain}\n{_BODY_INDENT}{f_plain}{body}"
    markup = f"{header_markup}\n{_BODY_INDENT}{f_markup}[{PRIMARY}]{_e(body)}[/]"
    return plain, markup


def format_message_rows(msgs: list[dict], width: int = 72) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    prev_sender: str | None = None
    prev_ts = None
    for m in msgs:
        plain, markup = format_message_block(
            m.get("sender", "?"),
            m.get("content", ""),
            m.get("created_at"),
            width=width,
            prev_sender=prev_sender,
            prev_ts=prev_ts,
            flags=m.get("flags"),
        )
        rows.append((plain, markup))
        prev_sender = m.get("sender", "?")
        prev_ts = m.get("created_at")
    return rows


def _build_channel_label(ch: dict, *, active: bool = False) -> str:
    unread = ch.get("unread", 0)
    prefix = "▌" if active else " "
    agent_name = ch.get("agent_name")
    agent_part = f" [{SECONDARY}]{_e(agent_name)}[/]" if agent_name else ""

    if is_direct_channel(ch):
        label_core = f"{prefix}{dm_display_name(ch['name'])}"
    else:
        label_core = f"{prefix}# {ch['name']}"

    pad = max(1, 16 - len(label_core.replace("▌", " ")))
    unread_part = f"{' ' * pad}[{UNREAD}]{unread}●[/]" if unread else ""
    color = ACCENT if active else PRIMARY
    return f"[{color}]{_e(label_core)}[/]{agent_part}{unread_part}"


def format_channel_title(ch: dict, *, reply_override: str | None = None) -> str:
    """Header above transcript."""
    name = ch.get("name", "")
    agent_name = ch.get("agent_name")
    if is_direct_channel(ch):
        title = f"▌{dm_display_name(name)}"
        if agent_name:
            title += f"  [{SECONDARY}]· {_e(agent_name)}[/]"
        return title
    if agent_name:
        title = f"▌# {_e(name)}  [{SECONDARY}]· {_e(agent_name)}[/]"
    else:
        title = f"▌# {_e(name)}"
    if reply_override and reply_override != name:
        title += f"  [{SECONDARY}]→ #{_e(reply_override)}[/]"
    return title


def composer_placeholder(ch: dict | None) -> str:
    if not ch:
        return "Loading…"
    if is_direct_channel(ch):
        return f"Message {dm_display_name(ch['name'])}…"
    return f"Message #{ch['name']}…"


def member_presence_glyph(age_secs: int) -> str:
    if age_secs < 120:
        return "●"
    if age_secs < 900:
        return "◐"
    return "○"


def format_member_row(sender: str, age_secs: int, *, bound: bool = False) -> str:
    from grove.theme_textual import DEGRADED, HEALTHY, IDLE

    glyph = member_presence_glyph(age_secs)
    if age_secs < 120:
        dot = f"[{HEALTHY}]{glyph}[/]"
    elif age_secs < 900:
        dot = f"[{DEGRADED}]{glyph}[/]"
    else:
        dot = f"[{IDLE}]{glyph}[/]"
    color = sender_color(sender)
    marker = f" [{ACCENT}]▶[/]" if bound else ""
    return f" {dot} [bold {color}]{_e(sender)}[/]{marker}"
