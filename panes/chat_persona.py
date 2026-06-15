"""panes/chat_persona.py — persona channel helpers (bind, reply routing, dispatch).
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import json
import logging

import grove_db
import soil

_log = logging.getLogger("grove.chat")

REPLY_SOIL_COLLECTION = "willow-dashboard/persona_reply"


def normalize_agent(name: str) -> str:
    return (name or "").strip().lstrip("@").lower()


def normalize_reply_channel(raw: str) -> str | None:
    if not raw:
        return None
    name = raw.strip().lstrip("#").lower()
    if not name or name.startswith("dm:"):
        return None
    return name


def get_reply_override(source_channel: str) -> str | None:
    if not source_channel:
        return None
    try:
        rec = soil.get(REPLY_SOIL_COLLECTION, source_channel) or {}
        target = (rec.get("reply_channel") or "").strip()
        return target or None
    except Exception as exc:
        _log.warning("chat_persona.get_reply_override: %s", exc)
        return None


def set_reply_override(source_channel: str, reply_channel: str | None) -> None:
    if not source_channel:
        return
    try:
        soil.put(
            REPLY_SOIL_COLLECTION,
            source_channel,
            {"reply_channel": reply_channel or ""},
        )
    except Exception as exc:
        _log.warning("chat_persona.set_reply_override: %s", exc)


def effective_reply_channel(source_channel: str, *, override: str | None = None) -> str:
    if override:
        return override
    routed = get_reply_override(source_channel)
    return routed or source_channel


def build_dispatch_payload(*, agent: str, prompt: str, reply_channel: str) -> dict:
    return {
        "to": normalize_agent(agent),
        "prompt": prompt,
        "reply_channel": reply_channel,
    }


def grove_dispatch_to_agent(
    agent: str,
    prompt: str,
    *,
    source_channel: str,
    reply_channel: str | None = None,
    sender: str | None = None,
) -> dict:
    """Post JSON dispatch to #dispatch. Returns {ok, reply_channel?, error?}."""
    import grove_reader

    who = sender or grove_reader.dashboard_grove_sender()
    target = effective_reply_channel(source_channel, override=reply_channel)
    agent_norm = normalize_agent(agent)
    if not agent_norm:
        return {"ok": False, "error": "no agent"}
    if not prompt.strip():
        return {"ok": False, "error": "empty prompt"}
    conn = None
    try:
        conn = grove_db.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM grove.channels WHERE name = 'dispatch' LIMIT 1")
        row = cur.fetchone()
        if not row:
            return {"ok": False, "error": "dispatch channel missing"}
        payload = json.dumps(
            build_dispatch_payload(
                agent=agent_norm,
                prompt=prompt,
                reply_channel=target,
            )
        )
        cur.execute(
            "INSERT INTO grove.messages (channel_id, sender, content)"
            " VALUES (%s, %s, %s)",
            (row[0], who, payload),
        )
        conn.commit()
        return {"ok": True, "agent": agent_norm, "reply_channel": target}
    except Exception as exc:
        _log.warning("grove_dispatch_to_agent: %s", exc)
        return {"ok": False, "error": str(exc)}
    finally:
        if conn is not None:
            grove_db.release_connection(conn)
