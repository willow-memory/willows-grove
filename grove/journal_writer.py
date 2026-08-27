# b17: WGRV1 ΔΣ=42
"""Thin Grove-side wrapper over willow-mcp's ``kb_journal`` write path (C11 LEFT).

Autonomous-continuity C11 sealed the chat card's LEFT side (operator → Willow)
as a write into ``kb_journal`` via the resident local watcher. This module is
that write — the smallest possible seam between Grove's ``POST /api/journal``
route and the willow-mcp organ that stores the atom.

Three ways of reaching willow-mcp, tried in order (D7 degradation, same shape
as ``grove/nestor_client.py``):

  a. **Direct import** — if ``willow_mcp.server`` is importable in this
     process, call ``kb_journal(...)`` in-process. This is the resident case
     — Grove and willow-mcp share the same seat.
  b. **HTTP** — if ``WILLOW_MCP_URL`` is set, POST the same payload to
     ``{WILLOW_MCP_URL}/tools/kb_journal`` and parse the returned atom.
  c. **No-op** — log one WARNING per process (not per call, per V-anti-noise)
     and return ``{"ok": False, "reason": "willow-mcp not reachable"}``.
     Grove renders "kb_journal unreachable" and the operator retries.

**Operator words are load-bearing.** ``write_operator_turn`` never
paraphrases, edits, or normalizes ``text`` before writing — it goes to
``kb_journal`` verbatim. This mirrors V5's discipline for Nestor's refusals:
the operator's own utterance is the one thing this module refuses to touch.

Sync only, no asyncio, matching the rest of ``grove/*.py``.
"""
from __future__ import annotations

import datetime as _dt
import json
import logging
import os
import urllib.error
import urllib.request
from typing import Any, Optional

log = logging.getLogger(__name__)

_APP_ID = "willow-grove"
_UNREACHABLE_LOGGED = False


def _log_unreachable_once(reason: str) -> None:
    """One WARNING per process — not per call.

    The operator does not need N identical log lines every keystroke; one is
    the signal, N is noise. Matches ``nestor_client.py``'s log-once posture.
    """
    global _UNREACHABLE_LOGGED
    if _UNREACHABLE_LOGGED:
        return
    _UNREACHABLE_LOGGED = True
    log.warning("journal_writer: willow-mcp not reachable (%s) — running as no-op (D7).", reason)


def _reset_log_once_for_tests() -> None:
    """Test helper — clear the log-once latch so a fresh test starts fresh.

    Kept intentionally undocumented in the public surface (leading `_`).
    """
    global _UNREACHABLE_LOGGED
    _UNREACHABLE_LOGGED = False


def _now_iso() -> str:
    """Timezone-aware UTC ISO 8601 with a trailing ``Z``.

    ``datetime.utcnow`` is deprecated and returns a naive stamp; use the aware
    form and swap ``+00:00`` for ``Z`` so the string reads as UTC on sight.
    """
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _build_tags(sender: str, ts: str, domain: Optional[str]) -> list[str]:
    """Compose the tag list for one kb_journal atom.

    Additive discipline: the base tag surface (``journal``, ``sender:*``,
    ``ts:*``) is unchanged; the optional ``domain:<domain>`` tag is appended
    only when a caller supplies it (the resident watcher, per Q2 of the
    Gate 5 lock — a domain tag on the atom, not persona routing).
    """
    tags = ["journal", f"sender:{sender}", f"ts:{ts}"]
    if domain:
        tags.append(f"domain:{domain}")
    return tags


def _try_import_write(text: str, sender: str, ts: str, domain: Optional[str] = None) -> Optional[dict[str, Any]]:
    """Attempt (a): call ``willow_mcp.server.kb_journal`` in-process.

    Returns the raw ``{"id": ..., "domain": ...}`` on success, or ``None`` if
    the module is not importable / the call raises. Every failure mode
    degrades silently to (b)/(c); willow-mcp's own errors (postgres down,
    schema unusable) surface as an ``{"error": ...}`` dict which we treat as
    "reachable but rejected" — not our concern to translate, but we do report
    it as the reason so the operator sees the truth.
    """
    try:
        from willow_mcp import server as _wms  # type: ignore
    except Exception:  # noqa: BLE001 — any import failure means path (a) is unavailable
        return None
    tags = _build_tags(sender, ts, domain)
    try:
        return _wms.kb_journal(app_id=_APP_ID, content=text, source=sender, tags=tags)
    except Exception as err:  # noqa: BLE001
        log.warning("journal_writer: in-process kb_journal raised: %s", err)
        return None


def _try_http_write(url: str, text: str, sender: str, ts: str, domain: Optional[str] = None) -> Optional[dict[str, Any]]:
    """Attempt (b): POST to ``{url}/tools/kb_journal``.

    Sync-only — uses stdlib ``urllib.request`` to avoid a hard dep on httpx.
    Returns the parsed JSON body on 2xx, or ``None`` on any transport /
    decode failure.
    """
    endpoint = url.rstrip("/") + "/tools/kb_journal"
    payload = {
        "app_id": _APP_ID,
        "content": text,
        "source": sender,
        "tags": _build_tags(sender, ts, domain),
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(  # noqa: S310 — endpoint is operator-configured, loopback by default
        endpoint,
        data=body,
        method="POST",
        headers={"content-type": "application/json", "accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=3.0) as resp:  # noqa: S310
            raw = resp.read().decode("utf-8")
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as err:
        log.warning("journal_writer: HTTP kb_journal transport error: %s", err)
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError as err:
        log.warning("journal_writer: HTTP kb_journal bad body: %s", err)
        return None


def write_operator_turn(
    text: str,
    *,
    sender: str = "operator",
    domain: Optional[str] = None,
) -> dict[str, Any]:
    """Write one operator turn to ``kb_journal`` — the chat card's LEFT side.

    The atom carries ``domain='journal'``, ``sender=<sender>``, ``text=<text>``,
    ``ts=<ISO 8601 UTC>`` (encoded as content + source + tag fields to match
    willow-mcp's ``kb_journal`` field surface). ``text`` is written verbatim —
    no paraphrase, no strip, no normalize (V5-style discipline).

    The optional ``domain`` argument (additive; introduced with Gate 5's
    resident watcher, Q2 lock) is appended as a ``domain:<value>`` tag on the
    atom. Existing callers see no behavior change; only new call sites that
    pass a value participate. ``None`` and empty string omit the tag.

    Returns:
        On success: ``{"ok": True, "id": "<atom id>", "ts": "<iso>"}``.
        On degradation: ``{"ok": False, "reason": "<why>"}``.

    Raises:
        ValueError: if ``text`` is empty or not a string.
    """
    if not isinstance(text, str) or not text:
        raise ValueError("journal_writer: text must be a non-empty string")
    if not isinstance(sender, str) or not sender:
        raise ValueError("journal_writer: sender must be a non-empty string")

    ts = _now_iso()

    result = _try_import_write(text, sender, ts, domain)
    tried = ["import"]
    if result is None:
        url = os.environ.get("WILLOW_MCP_URL", "").strip()
        if url:
            tried.append("http")
            result = _try_http_write(url, text, sender, ts, domain)

    if result is None:
        reason = "willow-mcp not reachable"
        _log_unreachable_once(f"tried={tried}")
        return {"ok": False, "reason": reason}

    if isinstance(result, dict) and "error" in result:
        # Reachable but rejected — surface the truth, do not paper over it.
        return {"ok": False, "reason": str(result.get("error"))}

    atom_id = None
    if isinstance(result, dict):
        atom_id = result.get("id")
    if not isinstance(atom_id, str) or not atom_id:
        return {"ok": False, "reason": "kb_journal returned no atom id"}

    return {"ok": True, "id": atom_id, "ts": ts}


__all__ = ["write_operator_turn"]
