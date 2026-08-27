# b17: WGRV1 ΔΣ=42
"""Thin Grove-side reader for willow-mcp's ``kb_journal`` atoms (C11 RIGHT).

The mirror image of ``grove/journal_writer.py``. Autonomous-continuity C11
seals the chat card as *the operator says (LEFT) → resident watcher writes
kb_journal → the chat card reads kb_journal (RIGHT) → the operator sees
Willow's answer*. Gate 5 lands the resident watcher; this module is the
honest reader Grove ships *before* that: it tails ``kb_journal`` today, so
the moment a resident watcher's writes appear there they show up on the
chat card without a code change on this side.

Three ways of reaching willow-mcp, tried in order (D7 degradation, same
shape as ``grove/journal_writer.py`` and ``grove/nestor_client.py``):

  a. **Direct import** — if ``willow_mcp.server`` is importable in this
     process, call ``kb_journal_read(...)`` in-process when that function
     exists in willow-mcp; otherwise return ``None`` and fall through.
     (The willow-mcp branch that lands ``kb_journal_read`` is the same
     one that lands the resident watcher — Gate 5.)
  b. **HTTP** — if ``WILLOW_MCP_URL`` is set, GET
     ``{WILLOW_MCP_URL}/tools/kb_journal_read`` and parse the returned
     atoms.
  c. **No-op** — log one INFO per process (not per call, per V-anti-noise)
     and return ``[]``. Grove renders "no messages yet" and the operator
     is not staring at an error state — absence is a legible state (D7).

**Read-only, verbatim.** Atom text goes to the caller unchanged — the
sender's own bytes, no paraphrase, no truncation, no normalize. This
mirrors ``journal_writer``'s discipline for the LEFT side and
Nestor's V5 refusal-verbatim: the words in kb_journal are load-bearing
and must not be reshaped by Grove.

Sync only, no asyncio, matching the rest of ``grove/*.py``.
"""
from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional

from grove.errors import Unreachable

log = logging.getLogger(__name__)

_APP_ID = "willow-grove"
_LIMIT_CAP = 200  # matches the grove_serve route cap; the reader guards it too
_UNREACHABLE_LOGGED = False


def _log_unreachable_once(reason: str) -> None:
    """One INFO per process — not per call.

    Read-back absence is a *state*, not an error (D7). ``journal_writer``
    uses WARNING because a failed write loses the operator's turn; a
    failed read just means "nothing to show yet", so INFO is honest.
    """
    global _UNREACHABLE_LOGGED
    if _UNREACHABLE_LOGGED:
        return
    _UNREACHABLE_LOGGED = True
    log.info("journal_reader: willow-mcp not reachable (%s) — empty read-back (D7).", reason)


def _reset_log_once_for_tests() -> None:
    """Test helper — clear the log-once latch so a fresh test starts fresh.

    Kept intentionally undocumented in the public surface (leading `_`).
    """
    global _UNREACHABLE_LOGGED
    _UNREACHABLE_LOGGED = False


def _extract_ts_from_tags(tags: Any) -> str:
    """Pull ``ts:<iso>`` out of a tag list, if the writer put one there.

    ``journal_writer`` tags every atom ``ts:<iso>`` so the atom carries
    its own wall-clock stamp independent of the storage layer's
    ``created_at``. Fallback to empty string when absent — the UI
    renders no stamp rather than inventing one.
    """
    if not isinstance(tags, (list, tuple)):
        return ""
    for tag in tags:
        if isinstance(tag, str) and tag.startswith("ts:"):
            return tag[len("ts:"):]
    return ""


def _extract_sender_from_tags(tags: Any) -> str:
    """Pull ``sender:<who>`` out of a tag list — writer discipline mirror."""
    if not isinstance(tags, (list, tuple)):
        return ""
    for tag in tags:
        if isinstance(tag, str) and tag.startswith("sender:"):
            return tag[len("sender:"):]
    return ""


def _normalize_atom(raw: Any) -> Optional[dict[str, Any]]:
    """Map a willow-mcp atom (dict) to Grove's chat-shape dict.

    Fields we return:
      * ``id``     — atom id, string
      * ``ts``     — ISO 8601 UTC string, empty if none available
      * ``sender`` — 'operator' / 'watcher' / whatever the writer set
      * ``text``   — the atom's content, verbatim
      * ``domain`` — 'journal' (kept for the caller's benefit; the writer
                     stamps it, we surface it)

    Returns ``None`` on a shape we don't recognize — a malformed atom
    is not our problem to translate.
    """
    if not isinstance(raw, dict):
        return None
    atom_id = raw.get("id")
    if not isinstance(atom_id, str) or not atom_id:
        return None
    # willow-mcp's enrich_atom emits "content" for the human text and
    # "source" for the writer's attribution. journal_writer set both.
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
    """Accept the two shapes we see in the wild: bare list, or ``{"atoms": [...]}``.

    Any other shape yields ``[]`` — the caller sees "no messages yet",
    which is a legible D7 state.
    """
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


def _try_import_read(limit: int, since_id: Optional[str]) -> Optional[list[dict[str, Any]]]:
    """Attempt (a): call ``willow_mcp.server.kb_journal_read`` in-process.

    Returns the normalized atom list on success, or ``None`` if the module
    is not importable / the read function is not present / the call raises.
    Gate 5 lands ``kb_journal_read`` in willow-mcp alongside the resident
    watcher; until then this returns ``None`` and the reader falls to (b).

    Raises ``Unreachable`` when willow-mcp returns a ``{"error": ...}``
    dict — reached-but-rejected is the *unreachable* three-state
    (INVARIANTS.md §1), not empty. Mirrors ``journal_writer.py:198-200``
    so writer and reader agree on the shape of an in-process error
    response across the C11 seam. An honest empty result (a list with
    zero atoms) still returns ``[]``.
    """
    try:
        from willow_mcp import server as _wms  # type: ignore
    except Exception:  # noqa: BLE001 — any import failure means path (a) is unavailable
        return None
    fn = getattr(_wms, "kb_journal_read", None)
    if fn is None:
        return None
    try:
        result = fn(app_id=_APP_ID, limit=limit, since_id=since_id)
    except TypeError:
        # A pre-Gate-5 signature might not accept `since_id`; try without.
        try:
            result = fn(app_id=_APP_ID, limit=limit)
        except Exception as err:  # noqa: BLE001
            log.warning("journal_reader: in-process kb_journal_read raised: %s", err)
            return None
    except Exception as err:  # noqa: BLE001
        log.warning("journal_reader: in-process kb_journal_read raised: %s", err)
        return None
    if isinstance(result, dict) and "error" in result:
        # Reachable but rejected — INVARIANTS.md §1 three-state: this is
        # the *unreachable* case, distinct from empty. Mirror
        # journal_writer.py:198-200 so writer and reader agree on the
        # in-process error shape across the C11 seam.
        raise Unreachable(str(result.get("error")))
    atoms = _atoms_from_payload(result)
    # (b) fallback also filters since_id, but if the in-process function
    # ignored our since_id we still owe the caller a correct answer.
    return _apply_since(atoms, since_id)


def _try_http_read(url: str, limit: int, since_id: Optional[str]) -> Optional[list[dict[str, Any]]]:
    """Attempt (b): GET ``{url}/tools/kb_journal_read``.

    Sync-only — stdlib ``urllib.request`` (no httpx dep). Returns the
    normalized atom list on 2xx, or ``None`` on any transport / decode
    failure so the caller degrades to (c).
    """
    query = {"app_id": _APP_ID, "limit": str(limit)}
    if since_id:
        query["since_id"] = since_id
    endpoint = url.rstrip("/") + "/tools/kb_journal_read?" + urllib.parse.urlencode(query)
    req = urllib.request.Request(  # noqa: S310 — endpoint is operator-configured, loopback by default
        endpoint,
        method="GET",
        headers={"accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=3.0) as resp:  # noqa: S310
            raw = resp.read().decode("utf-8")
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as err:
        log.info("journal_reader: HTTP kb_journal_read transport error: %s", err)
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as err:
        log.info("journal_reader: HTTP kb_journal_read bad body: %s", err)
        return None
    atoms = _atoms_from_payload(parsed)
    return _apply_since(atoms, since_id)


def _apply_since(atoms: list[dict[str, Any]], since_id: Optional[str]) -> list[dict[str, Any]]:
    """Trim atoms strictly newer than ``since_id``.

    The reader hands its answer back newest-first, so ``since_id`` is the
    id of an atom the caller has already seen — atoms *at or before* it
    in that order are already-known. We keep only atoms that appear
    before ``since_id`` in the list (i.e. strictly newer).

    If ``since_id`` is not found (server rotation, or a stale cursor from
    a page reload), we return all atoms — better to over-show once than
    to silently drop the whole read-back.
    """
    if not since_id:
        return atoms
    for i, atom in enumerate(atoms):
        if atom.get("id") == since_id:
            return atoms[:i]
    return atoms


def read_recent(
    limit: int = 50,
    since_id: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Return recent ``kb_journal`` atoms, newest first.

    Args:
        limit: max atoms to return; clamped to ``[1, 200]``. Non-int
            input silently falls back to the default (50) — same
            posture as the ``grove_serve`` route above this.
        since_id: if given, return only atoms strictly newer than
            this id (i.e. atoms that appear before it in
            newest-first order).

    Returns:
        Zero-or-more atom dicts, each ``{"id", "ts", "sender", "text",
        "domain"}``. Empty list is a legible three-state "empty"
        (INVARIANTS.md §1) — willow-mcp reached, nothing new.

    Raises:
        Unreachable: when neither the in-process nor the HTTP path
            reaches willow-mcp. The endpoint layer translates this into
            a 503 + ``state="unreachable"`` payload.
    """
    if not isinstance(limit, int) or limit <= 0:
        limit = 50
    if limit > _LIMIT_CAP:
        limit = _LIMIT_CAP
    since = since_id if (isinstance(since_id, str) and since_id) else None

    tried: list[str] = ["import"]
    atoms = _try_import_read(limit, since)
    if atoms is None:
        url = os.environ.get("WILLOW_MCP_URL", "").strip()
        if url:
            tried.append("http")
            atoms = _try_http_read(url, limit, since)

    if atoms is None:
        _log_unreachable_once(f"tried={tried}")
        raise Unreachable(f"willow-mcp not reachable (tried={tried})")

    return atoms[:limit]


__all__ = ["read_recent"]
