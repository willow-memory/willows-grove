# b17: WGRV1 ΔΣ=42
"""Read-only helper over ``public.tasks`` — the Kart escalation seam.

The autonomous-continuity doc (`docs/design/autonomous-continuity.md`,
C6–C8) names Kart as the seam every small-to-big handoff crosses: an
agent that hits its authority ceiling files a task on ``public.tasks``
with the ``authority_needed`` it needs from a larger tier, and the
operator (in v1, no auto-drain) picks the drain-tier from the dispatch
rail. C12 says the tri-modal switch on the desk filters that same queue
by lens (governance / pm / pa).

This module is the read side of that seam only. Writes to
``public.tasks`` are governance acts and belong to the queue producers
(Kart, the fleet agents themselves) — never to Grove. The autonomous-
continuity ladder pins Grove at L0 for this table: read-only.

Shape tolerance (D7 — *absence is a state, not a failure*):

The premise doc's Kart section names ``origin``, ``urgency``,
``authority_needed``, ``context_refs`` and ``proposed_action`` as the
fields the rail wants; the willow_20 schema shipped in `schema.sql`
predates that vocabulary and lands only ``id``, ``task``, ``status``,
``submitted_by``, ``cmd``, ``result``, ``created_at``, ``updated_at``.
Both shapes coexist while the fleet catches up. This reader probes
``information_schema.columns`` on connect and *drops* any predicate or
select expression whose column is missing — the rail renders what the
row does carry, and a single info log fires once per absent column so
the drift is visible without spamming.

Style mirrors ``grove/persona_roster.py``: one small synchronous
module, no async, ``[]`` when the source is absent, log-once on
degradation.
"""
from __future__ import annotations

import logging
import os
from typing import Any, Optional

log = logging.getLogger(__name__)

# ---- Log-once state ---------------------------------------------------------
# Reset by tests via ``kart_reader._logged_reset()``.
_logged_missing_dsn = False
_logged_missing_table = False
_logged_missing_columns: set[str] = set()


def _logged_reset() -> None:
    """Test hook: clear every log-once flag so a fresh run re-emits them."""
    global _logged_missing_dsn, _logged_missing_table
    _logged_missing_dsn = False
    _logged_missing_table = False
    _logged_missing_columns.clear()


# ---- Column vocabulary ------------------------------------------------------
# Fields the rail wants, in a stable render order. Every one is optional at
# the schema level; the reader emits whichever the live table carries.
_OPTIONAL_COLS: tuple[str, ...] = (
    "id",
    "origin",
    "kind",
    "urgency",
    "authority_needed",
    "context_refs",
    "proposed_action",
    "status",
    "created_at",
    "updated_at",
    # Legacy shape (v1 schema) — surfaced verbatim when present so the rail
    # can degrade to ``task`` / ``cmd`` for the proposed-action slot.
    "task",
    "cmd",
    "submitted_by",
)


# ---- DSN + column discovery -------------------------------------------------
def _dsn() -> Optional[str]:
    """Return the willow_20 DSN, or ``None`` (log-once) when unset."""
    global _logged_missing_dsn
    dsn = os.environ.get("WILLOW_DB_URL", "").strip()
    if dsn:
        return dsn
    if not _logged_missing_dsn:
        log.info(
            "kart_reader: WILLOW_DB_URL is not set — dispatch rail runs as "
            "no-op ([]) per D7."
        )
        _logged_missing_dsn = True
    return None


def _existing_columns(cur) -> set[str]:
    """Return the set of columns ``public.tasks`` actually carries.

    An empty set means the table itself is missing — a log-once ``[]``
    return is the correct answer at every call site.
    """
    cur.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema = 'public' AND table_name = 'tasks'"
    )
    return {row[0] for row in cur.fetchall()}


def _log_missing_columns(missing: set[str]) -> None:
    """Info-log once per column name we asked for and did not find."""
    for name in sorted(missing):
        if name in _logged_missing_columns:
            continue
        log.info(
            "kart_reader: public.tasks has no %r column — predicate skipped "
            "and the field is omitted from returned rows (D7).",
            name,
        )
        _logged_missing_columns.add(name)


# ---- Query builders ---------------------------------------------------------
def _order_by(present: set[str]) -> str:
    """Prefer ``urgency DESC, created_at ASC``; degrade to what exists."""
    parts: list[str] = []
    if "urgency" in present:
        parts.append("urgency DESC")
    if "created_at" in present:
        parts.append("created_at ASC")
    if not parts and "id" in present:
        parts.append("id ASC")
    return " ORDER BY " + ", ".join(parts) if parts else ""


def _select_columns(present: set[str]) -> list[str]:
    """The vocabulary columns the live table actually has, in stable order."""
    return [c for c in _OPTIONAL_COLS if c in present]


def _where_status_queued(present: set[str]) -> tuple[str, list[Any]]:
    """Filter to queued rows when ``status`` exists; otherwise no-op."""
    if "status" not in present:
        return "", []
    return " WHERE status = %s", ["queued"]


# ---- Lens predicates --------------------------------------------------------
def _lens_predicate(lens: Optional[str], present: set[str]) -> tuple[str, list[Any]]:
    """Return the additional WHERE fragment + params for ``lens``.

    Missing predicate columns are dropped (log-once); the remaining
    predicates OR together within the lens block. If nothing remains for
    this lens, the fragment is empty and the queue is returned
    unfiltered — the rail still renders, just wider than the operator
    asked for.
    """
    lens = (lens or "").strip().lower()

    if lens == "governance":
        wanted = {"authority_needed", "origin"}
        _log_missing_columns(wanted - present)
        clauses: list[str] = []
        params: list[Any] = []
        if "authority_needed" in present:
            clauses.append("authority_needed IN (%s)")
            params.append("L4")
        if "origin" in present:
            clauses.append("origin LIKE %s")
            params.append("nestor%")
            clauses.append("origin LIKE %s")
            params.append("governance%")
        if not clauses:
            return "", []
        return " AND (" + " OR ".join(clauses) + ")", params

    if lens == "pm":
        wanted = {"authority_needed"}
        _log_missing_columns(wanted - present)
        if "authority_needed" not in present:
            return "", []
        return " AND authority_needed IN (%s, %s)", ["L2", "L3"]

    if lens == "pa":
        wanted = {"authority_needed", "origin"}
        _log_missing_columns(wanted - present)
        clauses: list[str] = []
        params: list[Any] = []
        if "authority_needed" in present:
            clauses.append("authority_needed IN (%s)")
            params.append("L1")
        if "origin" in present:
            clauses.append("origin = %s")
            params.append("operator")
        if not clauses:
            return "", []
        return " AND (" + " OR ".join(clauses) + ")", params

    # Unknown lens (including None, "" — the "no filter" path).
    return "", []


# ---- Public API -------------------------------------------------------------
def _run(lens: Optional[str], limit: int) -> list[dict]:
    """Shared execution path for ``read_queue`` and ``read_by_lens``.

    Opens one short-lived psycopg2 connection, checks the live column
    set, builds the SELECT from what exists, and returns dict rows.
    Every failure mode (missing DSN, missing table, missing column) is a
    log-once ``[]`` — no crash reaches the rail.
    """
    global _logged_missing_table

    dsn = _dsn()
    if dsn is None:
        return []

    try:
        import psycopg2  # local import — kart_reader is a leaf module
    except ImportError:  # pragma: no cover - psycopg2 is a hard install dep
        log.warning("kart_reader: psycopg2 not importable — []")
        return []

    try:
        conn = psycopg2.connect(dsn)
    except Exception as err:  # noqa: BLE001 — network / auth failures are runtime
        log.warning("kart_reader: connect failed (%s) — []", err)
        return []

    try:
        with conn.cursor() as cur:
            present = _existing_columns(cur)
            if not present:
                if not _logged_missing_table:
                    log.info(
                        "kart_reader: public.tasks not present in this "
                        "database — [] per D7."
                    )
                    _logged_missing_table = True
                return []

            select_cols = _select_columns(present)
            if not select_cols:
                # Vocabulary drift so total we cannot name a single column.
                return []

            status_frag, status_params = _where_status_queued(present)
            lens_frag, lens_params = _lens_predicate(lens, present)

            sql = (
                f"SELECT {', '.join(select_cols)} FROM public.tasks"
                + status_frag
                + lens_frag
                + _order_by(present)
                + " LIMIT %s"
            )
            params = status_params + lens_params + [int(limit)]
            cur.execute(sql, params)
            return [dict(zip(select_cols, row)) for row in cur.fetchall()]
    finally:
        try:
            conn.close()
        except Exception:  # noqa: BLE001 — best-effort close
            pass


def read_queue(limit: int = 50) -> list[dict]:
    """Return up to ``limit`` queued Kart tasks, urgency-then-age ordered.

    No lens filter — the rail's raw queue. Missing status / urgency /
    created_at columns degrade to a plain LIMIT with no ORDER BY (see
    graceful-tolerance note in the module docstring).
    """
    return _run(lens=None, limit=limit)


def read_by_lens(lens: str, limit: int = 50) -> list[dict]:
    """Return queued tasks filtered by the tri-modal lens (C12).

    ``lens`` is one of ``"governance"``, ``"pm"``, ``"pa"``. Anything
    else (including ``None`` and the empty string) is treated as no
    filter — the rail still renders, just wider than the operator asked
    for. See ``_lens_predicate`` for the per-lens semantics.
    """
    return _run(lens=lens, limit=limit)


__all__ = ["read_queue", "read_by_lens"]
