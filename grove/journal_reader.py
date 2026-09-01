# b17: WGRV1 ΔΣ=42
"""Thin Grove-side reader for willow-mcp's ``kb_journal`` atoms (C11 RIGHT).

The mirror image of ``grove/journal_writer.py``. Autonomous-continuity C11
seals the chat card as *the operator says (LEFT) → resident watcher writes
kb_journal → the chat card reads kb_journal (RIGHT) → the operator sees
Willow's answer*. This module tails ``kb_journal`` via MCP so resident
watcher writes appear on the chat card without a code change on this side.

One transport — MCP ``tools/call`` via ``grove/willow_mcp_client.py``:

  a. **Streamable HTTP** when ``WILLOW_MCP_URL`` is set
     (``{WILLOW_MCP_URL}/mcp``).
  b. **stdio child** otherwise — a long-lived ``willow-mcp`` process on the
     same seat.

If neither is reachable, log one INFO per process (V-anti-noise) and raise
``Unreachable`` so the endpoint layer answers 503 + ``state="unreachable"``.
An honest empty list means willow-mcp was reached and had nothing new.

**Read-only, verbatim.** Atom text goes to the caller unchanged — the
sender's own bytes, no paraphrase, no truncation, no normalize.

Sync only, no asyncio, matching the rest of ``grove/*.py``.
"""
from __future__ import annotations

import logging
import os
from typing import Any, Optional

from grove.errors import Unreachable
from grove import willow_mcp_client as _wmc

log = logging.getLogger(__name__)

_APP_ID = "willow-grove"
_LIMIT_CAP = 200
_UNREACHABLE_LOGGED = False


def _log_unreachable_once(reason: str) -> None:
    global _UNREACHABLE_LOGGED
    if _UNREACHABLE_LOGGED:
        return
    _UNREACHABLE_LOGGED = True
    log.info("journal_reader: willow-mcp not reachable (%s) — empty read-back (D7).", reason)


def _reset_log_once_for_tests() -> None:
    global _UNREACHABLE_LOGGED
    _UNREACHABLE_LOGGED = False


def _extract_ts_from_tags(tags: Any) -> str:
    if not isinstance(tags, (list, tuple)):
        return ""
    for tag in tags:
        if isinstance(tag, str) and tag.startswith("ts:"):
            return tag[len("ts:"):]
    return ""


def _extract_sender_from_tags(tags: Any) -> str:
    if not isinstance(tags, (list, tuple)):
        return ""
    for tag in tags:
        if isinstance(tag, str) and tag.startswith("sender:"):
            return tag[len("sender:"):]
    return ""


def _normalize_atom(raw: Any) -> Optional[dict[str, Any]]:
    if not isinstance(raw, dict):
        return None
    atom_id = raw.get("id")
    if not isinstance(atom_id, str) or not atom_id:
        return None
    text = raw.get("content", raw.get("text", ""))
    if not isinstance(text, str):
        text = str(text)
    sender = raw.get("source") or ""
    if not isinstance(sender, str):
        sender = str(sender)
    tags = raw.get("tags")
    if not sender:
        sender = _extract_sender_from_tags(tags)
    ts = raw.get("ts") or raw.get("created_at") or _extract_ts_from_tags(tags)
    if ts is not None and not isinstance(ts, str):
        ts = str(ts)
    domain = raw.get("domain", "journal")
    if not isinstance(domain, str):
        domain = "journal"
    return {
        "id": atom_id,
        "ts": ts or "",
        "sender": sender or "",
        "text": text,
        "domain": domain,
    }


def _atoms_from_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        candidates = payload
    elif isinstance(payload, dict):
        raw_list = payload.get("atoms") or payload.get("results") or []
        candidates = raw_list if isinstance(raw_list, list) else []
    else:
        return []
    out: list[dict[str, Any]] = []
    for raw in candidates:
        atom = _normalize_atom(raw)
        if atom is not None:
            out.append(atom)
    return out


def _apply_since(atoms: list[dict[str, Any]], since_id: Optional[str]) -> list[dict[str, Any]]:
    if not since_id:
        return atoms
    for i, atom in enumerate(atoms):
        if atom.get("id") == since_id:
            return atoms[:i]
    return atoms


def _try_mcp_read(limit: int, since_id: Optional[str]) -> Optional[list[dict[str, Any]]]:
    """Call ``kb_journal_read`` over MCP; ``None`` when transport fails."""
    args: dict[str, Any] = {"app_id": _APP_ID, "limit": limit}
    if since_id:
        args["since_id"] = since_id
    result = _wmc.call_tool("kb_journal_read", args)
    if result is None:
        return None
    if isinstance(result, dict) and "error" in result:
        raise Unreachable(str(result.get("error")))
    atoms = _atoms_from_payload(result)
    return _apply_since(atoms, since_id)


def read_recent(
    limit: int = 50,
    since_id: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Return recent ``kb_journal`` atoms, newest first."""
    if not isinstance(limit, int) or limit <= 0:
        limit = 50
    if limit > _LIMIT_CAP:
        limit = _LIMIT_CAP
    since = since_id if (isinstance(since_id, str) and since_id) else None

    tried = ["mcp"]
    if os.environ.get("WILLOW_MCP_URL", "").strip():
        tried.append("http")
    elif _wmc.get_client().available():
        tried.append("stdio")

    atoms = _try_mcp_read(limit, since)

    if atoms is None:
        _log_unreachable_once(f"tried={tried}")
        raise Unreachable(f"willow-mcp not reachable (tried={tried})")

    return atoms[:limit]


__all__ = ["read_recent"]
