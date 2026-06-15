"""panes/chat_commands.py — Wave B `:` mod command parser + dispatch.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import shlex

import grove_reader
from panes.chat_admin import can_archive_channel, normalize_channel_name
from panes.chat_persona import (
    get_reply_override,
    normalize_agent,
    normalize_reply_channel,
    set_reply_override,
)

COMMAND_HINT = (
    "create NAME · archive · agent NAME|clear · takeover · reply CHANNEL · "
    "rename NEW · desc TEXT · read · channels archived · unarchive NAME · help"
)

_HELP_LINES = [
    "create NAME      new text channel",
    "archive          archive active channel (d d)",
    "agent NAME       bind persona to active channel",
    "agent clear      clear persona binding",
    "takeover         you own the channel (clear agent binding)",
    "reply CHANNEL    route agent replies elsewhere (reply clear to reset)",
    "rename NEW       rename active channel",
    "desc TEXT        set channel description",
    "read             mark active channel read",
    "channels archived  list archived channels",
    "unarchive NAME   restore archived channel",
    "help             this list",
    "",
    "Keys: a bind member · A takeover · m members",
]


def parse_mod_command(line: str) -> tuple[str, list[str]]:
    """Parse `:verb args…` into (verb, args). Empty verb if blank."""
    raw = (line or "").strip()
    if raw.startswith(":"):
        raw = raw[1:].strip()
    if not raw:
        return "", []
    try:
        parts = shlex.split(raw)
    except ValueError:
        parts = raw.split()
    if not parts:
        return "", []
    return parts[0].lower(), parts[1:]


def execute_mod_command(line: str, *, active_channel: str) -> dict:
    """Run a mod command. Returns {ok, message, open_channel?, refresh?}."""
    verb, args = parse_mod_command(line)
    if not verb:
        return {"ok": False, "message": "empty command — try :help"}

    if verb == "help":
        return {
            "ok": True,
            "message": "\n".join(_HELP_LINES),
            "show_panel": True,
            "panel_title": "Mod commands",
        }

    if verb == "create":
        if not args:
            return {"ok": False, "message": "usage: create NAME"}
        result = grove_reader.grove_create_text_channel(args[0])
        if not result.get("ok"):
            return {"ok": False, "message": result.get("error", "create failed")}
        ch = result["channel"]
        return {
            "ok": True,
            "message": f"created #{ch['name']}",
            "open_channel": ch["name"],
            "refresh": True,
        }

    if verb == "archive":
        if not active_channel:
            return {"ok": False, "message": "no active channel"}
        if not can_archive_channel(active_channel):
            return {"ok": False, "message": f"cannot archive {active_channel}"}
        result = grove_reader.grove_archive_channel(active_channel)
        if not result.get("ok"):
            return {"ok": False, "message": result.get("error", "archive failed")}
        return {
            "ok": True,
            "message": f"archived #{active_channel}",
            "open_channel": "general",
            "refresh": True,
        }

    if verb == "agent":
        if not active_channel:
            return {"ok": False, "message": "no active channel"}
        agent = None if not args or args[0].lower() == "clear" else args[0]
        result = grove_reader.grove_set_channel_agent(active_channel, agent)
        if not result.get("ok"):
            return {"ok": False, "message": result.get("error", "agent bind failed")}
        if agent:
            return {
                "ok": True,
                "message": f"agent → {result.get('agent')}",
                "refresh_persona": True,
            }
        return {"ok": True, "message": "agent cleared", "refresh_persona": True}

    if verb == "takeover":
        if not active_channel:
            return {"ok": False, "message": "no active channel"}
        if active_channel.startswith("dm:"):
            return {"ok": False, "message": "not a group channel"}
        result = grove_reader.grove_set_channel_agent(active_channel, None)
        if not result.get("ok"):
            return {"ok": False, "message": result.get("error", "takeover failed")}
        set_reply_override(active_channel, None)
        return {
            "ok": True,
            "message": "channel taken over",
            "refresh_persona": True,
            "clear_waiting": True,
        }

    if verb == "reply":
        if not active_channel:
            return {"ok": False, "message": "no active channel"}
        if not args or args[0].lower() == "clear":
            set_reply_override(active_channel, None)
            return {
                "ok": True,
                "message": "reply routing cleared",
                "refresh_persona": True,
            }
        target = normalize_reply_channel(args[0])
        if not target:
            return {"ok": False, "message": "usage: reply CHANNEL or reply clear"}
        set_reply_override(active_channel, target)
        return {
            "ok": True,
            "message": f"replies → #{target}",
            "refresh_persona": True,
        }

    if verb == "rename":
        if not active_channel:
            return {"ok": False, "message": "no active channel"}
        if not args:
            return {"ok": False, "message": "usage: rename NEW-NAME"}
        result = grove_reader.grove_rename_channel(active_channel, args[0])
        if not result.get("ok"):
            return {"ok": False, "message": result.get("error", "rename failed")}
        new_name = result.get("name", args[0])
        return {
            "ok": True,
            "message": f"renamed → #{new_name}",
            "open_channel": new_name,
            "refresh": True,
        }

    if verb == "desc":
        if not active_channel:
            return {"ok": False, "message": "no active channel"}
        if not args:
            return {"ok": False, "message": "usage: desc your description"}
        text = " ".join(args)
        result = grove_reader.grove_set_channel_description(active_channel, text)
        if not result.get("ok"):
            return {"ok": False, "message": result.get("error", "desc failed")}
        return {"ok": True, "message": "description updated", "refresh": True}

    if verb == "read":
        if not active_channel:
            return {"ok": False, "message": "no active channel"}
        result = grove_reader.grove_mark_channel_read(active_channel)
        if not result.get("ok"):
            return {"ok": False, "message": result.get("error", "read failed")}
        last_id = result.get("last_id", 0)
        return {
            "ok": True,
            "message": f"marked read · id {last_id}",
            "mark_read_id": last_id,
            "refresh": True,
        }

    if verb == "channels":
        if not args or args[0].lower() != "archived":
            return {"ok": False, "message": "usage: channels archived"}
        rows = grove_reader.grove_list_archived_channels()
        if not rows:
            return {
                "ok": True,
                "message": "no archived channels",
                "show_panel": True,
                "panel_title": "Archived channels",
            }
        names = ", ".join(f"#{r['name']}" for r in rows[:12])
        extra = f" (+{len(rows) - 12} more)" if len(rows) > 12 else ""
        return {
            "ok": True,
            "message": f"archived: {names}{extra}",
            "show_panel": True,
            "panel_title": "Archived channels",
        }

    if verb == "unarchive":
        if not args:
            return {"ok": False, "message": "usage: unarchive NAME"}
        name = normalize_channel_name(args[0])
        if not name:
            return {"ok": False, "message": "invalid channel name"}
        result = grove_reader.grove_unarchive_channel(name)
        if not result.get("ok"):
            return {"ok": False, "message": result.get("error", "unarchive failed")}
        return {
            "ok": True,
            "message": f"unarchived #{name}",
            "open_channel": name,
            "refresh": True,
        }

    return {"ok": False, "message": f"unknown command: {verb} — :help"}
