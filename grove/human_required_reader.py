# b17: WGRV1 ΔΣ=42
"""grove/human_required_reader.py — the live human-required queue.

What waits on the human is filed with willow-mcp's ``human_required_enqueue``
(the steward's keep-current, app-grant and ingress steps, the desk, Loki,
Hanuman) into willow-mcp's own store. The Postgres table
``public.human_required_queue`` that ``grove_reader.human_required_queue``
reads is not where any of them file: it last took an item in June. This
reader asks willow-mcp, so the desk and ``grove_human_required`` see the
queue the fleet actually writes.

Three states (INVARIANTS.md §1), never collapsed:

* ``populated`` — open items, priority first (urgent, high, normal, low),
  then newest.
* ``empty`` — willow-mcp answered and nothing is open.
* ``unreachable`` — willow-mcp couldn't be asked, or refused (the
  ``willow-grove`` app needs ``human_loop_read`` in its manifest); the reason
  says which, in willow-mcp's own words.

Read-only: it lists; resolving an item is the human's, elsewhere.
"""

from __future__ import annotations

from typing import Any

from grove import willow_mcp_client as _wmc
from grove.errors import Unreachable

_APP_ID = "willow-grove"
#: How many the desk shows at most.
_LIMIT_CAP = 100
#: How many it asks willow-mcp for: the whole open queue, as willow-mcp's own
#: gates panel does. willow-mcp answers newest first, so asking for only
#: what is shown dropped the OLDEST open items before they were sorted, the
#: urgent ones from 09-23 among them (139 open, 100 asked, 2026-10-31).
_FETCH_CAP = 500
_PRIORITY = {"urgent": 0, "high": 1, "normal": 2, "low": 3}
_FIELDS = (
    "id",
    "kind",
    "title",
    "summary",
    "priority",
    "status",
    "source_agent",
    "source_ref",
    "created_at",
)


def read_open(limit: int = 50) -> dict[str, Any]:
    """``{"items": [...], "stats": {...}, "open": n, "shown": m}`` for the
    open queue: every open item sorted, the first ``limit`` returned. ``open``
    is willow-mcp's own count when it gives one, so a long queue never reads
    as the length of the page. Raises :class:`Unreachable` with willow-mcp's
    reason when it can't be read."""
    if not isinstance(limit, int) or limit <= 0:
        limit = 50
    limit = min(limit, _LIMIT_CAP)
    payload = _wmc.call_tool(
        "human_required_list",
        {"app_id": _APP_ID, "status": "open", "limit": _FETCH_CAP},
    )
    if payload is None:
        why = _wmc.get_client().last_error()
        raise Unreachable("willow-mcp not reachable" + (f": {why}" if why else ""))
    if isinstance(payload, dict) and payload.get("error"):
        raise Unreachable(f"willow-mcp refused: {payload['error']}"[:400])
    raw = payload.get("items") if isinstance(payload, dict) else payload
    if not isinstance(raw, list):
        raise Unreachable("willow-mcp answered in a shape this reader can't read")
    items = [
        {k: r.get(k) for k in _FIELDS}
        for r in raw
        if isinstance(r, dict) and r.get("status") == "open"
    ]
    items.sort(key=lambda r: str(r.get("created_at") or ""), reverse=True)
    items.sort(key=lambda r: _PRIORITY.get(str(r.get("priority") or "normal"), 2))
    stats = (
        payload.get("stats")
        if isinstance(payload, dict) and isinstance(payload.get("stats"), dict)
        else {}
    )
    counted = stats.get("open")
    open_n = (
        counted if isinstance(counted, int) and counted >= len(items) else len(items)
    )
    shown = items[:limit]
    return {"items": shown, "stats": stats, "open": open_n, "shown": len(shown)}
