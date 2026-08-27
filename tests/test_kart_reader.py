# b17: WGRV1 ΔΣ=42
"""Tests for grove.kart_reader — D7 shape tolerance + lens filtering (C12).

The CI job (`.github/workflows/tests.yml`) stands up a real Postgres via the
`pgvector/pgvector:pg15` service and hands us a DSN in ``WILLOW_DB_URL``.
kart_reader targets ``public.tasks`` by fully-qualified name, so these tests
manipulate that real table's shape in place:

* **Minimal (v1) shape** — the base schema shipped by ``schema.sql``:
  ``id``, ``task``, ``status``, ``submitted_by``, ``cmd``, ``result``,
  ``created_at``, ``updated_at``. No ``authority_needed``, no ``urgency``,
  no ``origin``. Asserts ``read_queue()`` still returns rows without
  crashing and logs one info line naming the absent column; the lens
  filters degrade to no-predicate.
* **Full shape** — the premise-doc shape, added on top with
  ``ALTER TABLE ... ADD COLUMN IF NOT EXISTS``. Asserts each lens
  returns only its share. Columns are dropped at teardown so no drift
  leaks into whatever runs after.

Third case (no DB): ``WILLOW_DB_URL`` unset → ``[]`` + single info log.

stdlib unittest only; the DB tests are skipped when Postgres is not
reachable so a local ``python -m unittest`` still works.
"""
from __future__ import annotations

import os
import sys
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from grove import kart_reader
from grove.errors import Unreachable


def _has_dsn() -> bool:
    return bool(os.environ.get("WILLOW_DB_URL", "").strip())


def _connect():
    """Open a management connection to the CI DB using WILLOW_DB_URL."""
    import psycopg2
    conn = psycopg2.connect(os.environ["WILLOW_DB_URL"])
    conn.autocommit = True
    return conn


def _exec(sql: str, params: list | None = None) -> None:
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or [])
    finally:
        conn.close()


def _clear_tasks() -> None:
    """Empty ``public.tasks`` — every test wants a clean queue."""
    _exec("DELETE FROM public.tasks")


# Columns the premise-doc shape needs on top of the base schema. Added at
# setUp with ``ADD COLUMN IF NOT EXISTS`` so re-runs after a failed drop stay
# green, and dropped at tearDown so the base shape survives.
_EXTRA_COLS: tuple[tuple[str, str], ...] = (
    ("origin",           "TEXT"),
    ("kind",             "TEXT"),
    ("urgency",          "TEXT"),
    ("authority_needed", "TEXT"),
    ("context_refs",     "JSONB"),
    ("proposed_action",  "TEXT"),
)


def _add_full_shape() -> None:
    for name, sqltype in _EXTRA_COLS:
        _exec(f"ALTER TABLE public.tasks ADD COLUMN IF NOT EXISTS {name} {sqltype}")


def _drop_full_shape() -> None:
    for name, _ in _EXTRA_COLS:
        _exec(f"ALTER TABLE public.tasks DROP COLUMN IF EXISTS {name}")


@unittest.skipUnless(_has_dsn(), "WILLOW_DB_URL required for kart_reader DB tests")
class MinimalShapeTests(unittest.TestCase):
    """The v1 schema — no ``authority_needed``, no ``urgency``, no ``origin``.

    This is what schema.sql ships with: the reader must not crash, must
    return the queued rows, and must log the missing columns just once.
    """

    def setUp(self) -> None:
        kart_reader._logged_reset()
        # Guarantee the base shape — if a previous run failed mid-flight
        # and left the extras behind, drop them here.
        _drop_full_shape()
        _clear_tasks()

    def tearDown(self) -> None:
        _clear_tasks()

    def test_read_queue_returns_rows_and_logs_missing_columns_once(self) -> None:
        _exec(
            "INSERT INTO public.tasks (task, status, submitted_by) "
            "VALUES (%s, %s, %s), (%s, %s, %s), (%s, %s, %s)",
            [
                "reply to Ada",      "queued", "operator",
                "roll build",        "queued", "hanuman",
                "already resolved",  "complete", "loki",
            ],
        )

        with self.assertLogs(kart_reader.log, level="INFO") as caplog:
            queued = kart_reader.read_queue()
            # Second call — governance lens with no authority_needed column;
            # the missing-column log must not fire a second time (log-once).
            governance = kart_reader.read_by_lens("governance")

        # Two queued rows come back; the 'complete' one does not.
        self.assertEqual(len(queued), 2)
        for row in queued:
            self.assertEqual(row.get("status"), "queued")

        # Governance lens degrades cleanly — no predicate columns present,
        # so the queue is returned unfiltered (still just the queued rows).
        self.assertGreaterEqual(len(governance), 2)

        # authority_needed absence must be logged exactly once across both
        # calls (the log-once discipline).
        auth_msgs = [
            r.getMessage()
            for r in caplog.records
            if "authority_needed" in r.getMessage()
        ]
        self.assertEqual(
            len(auth_msgs), 1,
            f"authority_needed missing-log must fire once, saw {auth_msgs}",
        )


@unittest.skipUnless(_has_dsn(), "WILLOW_DB_URL required for kart_reader DB tests")
class FullShapeTests(unittest.TestCase):
    """The premise-doc shape — every field the rail wants (C6-C8 + C12)."""

    def setUp(self) -> None:
        kart_reader._logged_reset()
        _add_full_shape()
        _clear_tasks()

    def tearDown(self) -> None:
        _clear_tasks()
        _drop_full_shape()

    def _seed(self) -> None:
        rows = [
            # (task, origin, authority, urgency, status, action)
            ("t1", "operator",   "L1", "operator-visible",  "queued", "reply to Ada"),
            ("t2", "hanuman",    "L2", "background",        "queued", "roll build"),
            ("t3", "skirnir",    "L3", "operator-visible",  "queued", "publish forecast"),
            ("t4", "nestor",     "L4", "operator-blocking", "queued", "amend Article II"),
            ("t5", "governance", "L4", "operator-blocking", "queued", "seat rotation"),
            # a done row must NEVER appear in any lens
            ("t6", "loki",       "L1", "background",        "complete", "already resolved"),
        ]
        for task, origin, auth, urg, status, action in rows:
            _exec(
                "INSERT INTO public.tasks "
                "(task, origin, authority_needed, urgency, status, proposed_action) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                [task, origin, auth, urg, status, action],
            )

    def test_governance_lens_returns_only_l4_or_governance_origins(self) -> None:
        self._seed()
        rows = kart_reader.read_by_lens("governance")
        self.assertTrue(rows, "governance lens returned no rows")
        origins = {r["origin"] for r in rows}
        self.assertIn("nestor", origins)
        self.assertIn("governance", origins)
        # Nothing from the L1/L2/L3 non-governance producers leaks in.
        for row in rows:
            self.assertTrue(
                row["authority_needed"] == "L4"
                or (row["origin"] or "").startswith(("nestor", "governance"))
            )

    def test_pm_lens_returns_l2_and_l3_only(self) -> None:
        self._seed()
        rows = kart_reader.read_by_lens("pm")
        self.assertTrue(rows)
        auths = {r["authority_needed"] for r in rows}
        self.assertEqual(auths, {"L2", "L3"})

    def test_pa_lens_returns_l1_or_operator_only(self) -> None:
        self._seed()
        rows = kart_reader.read_by_lens("pa")
        self.assertTrue(rows)
        for row in rows:
            self.assertTrue(
                row["authority_needed"] == "L1" or row["origin"] == "operator"
            )
        origins = [r["origin"] for r in rows]
        self.assertIn("operator", origins)
        # The completed loki row must not appear even though it's L1 — the
        # status filter is upstream of the lens.
        self.assertNotIn("loki", origins)

    def test_read_queue_excludes_done_rows(self) -> None:
        self._seed()
        rows = kart_reader.read_queue()
        self.assertEqual(len(rows), 5, "one 'complete' row must be excluded")
        for row in rows:
            self.assertEqual(row["status"], "queued")


class UnsetDsnTests(unittest.TestCase):
    """DSN missing → Unreachable + single log (INVARIANTS.md §1)."""

    def setUp(self) -> None:
        kart_reader._logged_reset()

    def test_unset_dsn_raises_unreachable_and_logs_once(self) -> None:
        env = {k: v for k, v in os.environ.items() if k != "WILLOW_DB_URL"}
        with mock.patch.dict(os.environ, env, clear=True):
            with self.assertLogs(kart_reader.log, level="INFO") as caplog:
                with self.assertRaises(Unreachable) as ctx1:
                    kart_reader.read_queue()
                with self.assertRaises(Unreachable):
                    kart_reader.read_by_lens("governance")
                with self.assertRaises(Unreachable):
                    kart_reader.read_by_lens("pa")

        self.assertIn("WILLOW_DB_URL", ctx1.exception.reason)
        dsn_msgs = [r for r in caplog.records if "WILLOW_DB_URL" in r.getMessage()]
        self.assertEqual(
            len(dsn_msgs), 1,
            f"missing-DSN log must fire exactly once, saw {len(dsn_msgs)}",
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
