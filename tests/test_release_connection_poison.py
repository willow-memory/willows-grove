# b17: WGRV1 ΔΣ=42
"""tests/test_release_connection_poison.py — poisoned connections must not
recirculate through the pool.

Loki v0.9 finding #38 (minor, cross-cutting-hazards): `grove_db.release_connection`
wraps `conn.rollback()` in a bare `except Exception: pass`, then unconditionally
hands the connection back to the pool via `putconn()`. A connection whose
rollback failed (e.g. the server already closed it, or it is stuck mid-abort)
is left in an unknown transactional state. Returning that connection to the
pool means the *next* caller to borrow it inherits the bad state — a
connection-poisoning hazard, not a handled failure.

Fix: when `conn.rollback()` raises, `release_connection` must NOT call
`putconn()` on that connection. It should close the connection directly and
let the pool open a fresh one on the next `getconn()`.

This test monkeypatches `conn.rollback` to raise and asserts:
  1. the pool's `putconn` was never called with the poisoned connection,
  2. the connection was closed directly instead.

Pre-fix, `putconn` IS called with the poisoned connection (assertion 1
fails) — this test fails on the unfixed code.

Stdlib only. No live database.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import grove_db  # noqa: E402


class _PoisonedConn:
    """A connection whose rollback() always raises."""

    def __init__(self) -> None:
        self.closed = False

    def rollback(self) -> None:
        raise RuntimeError("simulated: server already dropped this connection")

    def close(self) -> None:
        self.closed = True


class _FakePool:
    """Records every putconn() call so we can assert what was returned to it."""

    def __init__(self) -> None:
        self.putconn_calls: list[object] = []

    def putconn(self, conn) -> None:
        self.putconn_calls.append(conn)


def test_poisoned_connection_is_not_returned_to_pool(monkeypatch) -> None:
    fake_pool = _FakePool()
    monkeypatch.setattr(grove_db, "_get_pool", lambda: fake_pool)

    conn = _PoisonedConn()

    # release_connection must not itself raise even though rollback() does.
    grove_db.release_connection(conn)

    assert conn not in fake_pool.putconn_calls, (
        "release_connection returned a connection to the pool after its "
        "rollback() raised — the next borrower inherits an unknown "
        "transactional state (Loki finding #38)."
    )
    assert fake_pool.putconn_calls == [], (
        f"pool.putconn must not be called at all on the poisoned-rollback "
        f"path; got calls={fake_pool.putconn_calls!r}"
    )
    assert conn.closed, (
        "release_connection must close a connection whose rollback() failed "
        "instead of silently discarding it, so the underlying socket is not "
        "leaked."
    )
