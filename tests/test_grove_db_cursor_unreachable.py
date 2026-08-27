# b17: WGRV1 ΔΣ=42
"""tests/test_grove_db_cursor_unreachable.py — INVARIANTS.md §1 pin for cursor_load.

`grove_db.cursor_load` is a state reader: it returns the caller's stored
cursor dict, or `{}` when the agent has never persisted one. Per
INVARIANTS.md §1 (the three-state contract), a bare `{}` MUST NOT mean
"unreachable" — when the database cannot be read, the reader raises
`grove.errors.Unreachable` instead of collapsing the failure into the
empty return.

Pre-fix, `cursor_load` catches every `Exception`, calls `conn.rollback()`,
and returns `{}`. That makes a real DB failure indistinguishable from
"this agent has no cursors stored" — the exact anti-pattern §1 names.

This test drives `cursor_load` against a fake connection whose cursor's
`execute()` raises `psycopg2.OperationalError` (the standard "database
unreachable" psycopg2 signal). We assert:

  1. `Unreachable` is raised (the invariant),
  2. `conn.rollback()` was called (transactional hygiene preserved).

Stdlib only. No live database.
"""
from __future__ import annotations

import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import psycopg2  # noqa: E402

import grove_db  # noqa: E402
from grove.errors import Unreachable  # noqa: E402


class _FakeCursor:
    """Every SQL statement raises psycopg2.OperationalError."""

    def execute(self, *_args, **_kwargs):
        raise psycopg2.OperationalError(
            "connection to server was lost (simulated by test)"
        )

    def fetchone(self):  # pragma: no cover — execute() must have raised first
        raise AssertionError(
            "cursor_load reached fetchone() after execute() raised — "
            "the reader is masking a DB failure."
        )

    def close(self):
        pass


class _FakeConn:
    """Minimal psycopg2-conn stand-in whose cursor always raises."""

    def __init__(self) -> None:
        self.rolled_back = False
        self.committed = False

    def cursor(self):
        return _FakeCursor()

    def rollback(self) -> None:
        self.rolled_back = True

    def commit(self) -> None:  # pragma: no cover — execute() raises first
        self.committed = True


class CursorLoadUnreachableTest(unittest.TestCase):
    """§1: cursor_load MUST raise Unreachable on DB failure — never return {}."""

    def test_operational_error_raises_unreachable_not_empty_dict(self) -> None:
        conn = _FakeConn()

        with self.assertRaises(Unreachable) as ctx:
            grove_db.cursor_load(conn, "test-agent")

        # §1: the reason string is the operator's evidence — keep it factual.
        self.assertTrue(
            str(ctx.exception).strip(),
            "Unreachable must carry a non-empty reason (INVARIANTS.md §1).",
        )

        # Transactional hygiene: the pooled connection must not be left mid-txn.
        self.assertTrue(
            conn.rolled_back,
            "cursor_load must roll back the connection on failure so the pool "
            "does not hand out a mid-transaction handle to the next caller.",
        )

        # The failing path must never commit — no fake success telegraphed upstream.
        self.assertFalse(
            conn.committed,
            "cursor_load must not commit on the failure path.",
        )


if __name__ == "__main__":
    unittest.main()
