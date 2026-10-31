# b17: WGRV1 ΔΣ=42
"""Thin Grove-side wrapper over willow-mcp's ``kb_journal`` write path (C11 LEFT).

Autonomous-continuity C11 sealed the chat card's LEFT side (operator → Willow)
as a write into ``kb_journal`` via the resident local watcher. This module is
that write — the smallest possible seam between Grove's ``POST /api/journal``
route and the willow-mcp organ that stores the atom.

One transport — MCP ``tools/call`` via ``grove/willow_mcp_client.py``:

  a. **Streamable HTTP** when ``WILLOW_MCP_URL`` is set
     (``{WILLOW_MCP_URL}/mcp``).
  b. **stdio child** otherwise — a long-lived ``willow-mcp`` process on the
     same seat.

If neither is reachable, log one WARNING per process (V-anti-noise) and raise
``Unreachable`` so the endpoint layer answers 503 + ``state="unreachable"``.

**Operator words are load-bearing.** ``write_operator_turn`` never
paraphrases, edits, or normalizes ``text`` before writing — it goes to
``kb_journal`` verbatim. This mirrors V5's discipline for Nestor's refusals:
the operator's own utterance is the one thing this module refuses to touch.

Sync only, no asyncio, matching the rest of ``grove/*.py``.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Optional

from grove.errors import Unreachable
from grove import onescript_reach
from grove import willow_mcp_client as _wmc

log = logging.getLogger(__name__)

_APP_ID = "willow-grove"
_UNREACHABLE_LOGGED = False


def _log_unreachable_once(reason: str) -> None:
    """One WARNING per process — not per call."""
    global _UNREACHABLE_LOGGED
    if _UNREACHABLE_LOGGED:
        return
    _UNREACHABLE_LOGGED = True
    log.warning(
        "journal_writer: willow-mcp not reachable (%s) — running as no-op (D7).", reason
    )


def _reset_log_once_for_tests() -> None:
    """Test helper — clear the log-once latch so a fresh test starts fresh."""
    global _UNREACHABLE_LOGGED
    _UNREACHABLE_LOGGED = False


def _now_iso() -> str:
    """Journal ``ts``, in the one script's ``seconds_z`` format, from its one
    clock (flatten-2 F8: "Using the onescript at every path."). ``$ONESCRIPT_NOW``
    pins it. With no one script reachable this raises Grove's ``Unreachable``
    with the reach's why (the route answers 503 + ``unreachable``); there is no
    copy to fall back to."""
    try:
        return onescript_reach.module("clock").seconds_z()
    except onescript_reach.Unreachable as e:
        raise Unreachable(str(e)) from e


def _build_tags(sender: str, ts: str, domain: Optional[str]) -> list[str]:
    tags = ["journal", f"sender:{sender}", f"ts:{ts}"]
    if domain:
        tags.append(f"domain:{domain}")
    return tags


def _try_mcp_write(
    text: str, sender: str, ts: str, domain: Optional[str] = None
) -> Optional[dict[str, Any]]:
    """Call ``kb_journal`` over MCP; ``None`` when transport fails."""
    result = _wmc.call_tool(
        "kb_journal",
        {
            "app_id": _APP_ID,
            "content": text,
            "source": sender,
            "tags": _build_tags(sender, ts, domain),
        },
    )
    if result is None:
        return None
    if isinstance(result, dict):
        return result
    return None


def write_operator_turn(
    text: str,
    *,
    sender: str = "operator",
    domain: Optional[str] = None,
) -> dict[str, Any]:
    """Write one operator turn to ``kb_journal`` — the chat card's LEFT side."""
    if not isinstance(text, str) or not text:
        raise ValueError("journal_writer: text must be a non-empty string")
    if not isinstance(sender, str) or not sender:
        raise ValueError("journal_writer: sender must be a non-empty string")

    ts = _now_iso()
    tried = ["mcp"]
    if os.environ.get("WILLOW_MCP_URL", "").strip():
        tried.append("http")
    elif _wmc.get_client().available():
        tried.append("stdio")

    result = _try_mcp_write(text, sender, ts, domain)

    if result is None:
        _log_unreachable_once(f"tried={tried}")
        why = _wmc.get_client().last_error()
        raise Unreachable(
            f"willow-mcp not reachable (tried={tried})" + (f": {why}" if why else "")
        )

    if isinstance(result, dict) and "error" in result:
        raise Unreachable(str(result.get("error")))

    atom_id = result.get("id") if isinstance(result, dict) else None
    if not isinstance(atom_id, str) or not atom_id:
        raise Unreachable("kb_journal returned no atom id")

    return {"ok": True, "id": atom_id, "ts": ts}


__all__ = ["write_operator_turn"]
