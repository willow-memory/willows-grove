# b17: WGRV1 ΔΣ=42
"""tests/test_frank_ledger_error_surfaces.py — FRANK ledger errors surface.

grove_db.py's schema comment calls the frank_ledger "tamper-evident";
INVARIANTS.md §1 pins the three-state contract, and CLAUDE.md pins
"If Postgres is down, surface it and stop." The pre-fix
`_frank_ledger_append` wrapped its whole body in
`except Exception as e: print(f"[frank-ledger] write error: {e}",
flush=True)`. Every failure — including a UniqueViolation on the
anti-fork guard partial index — was buried to stdout, invisible to
callers and to the operator dashboard.

Loki v0.9 finding #23 (cross-cutting-hazards, major): the ledger
writer's error path must (a) log via the module's `logging.Logger` (not
bare `print`), and (b) raise a distinct exception
(`grove.errors.LedgerWriteFailed`) so callers can react. The best-effort
semantics stay at the call site, not inside the ledger primitive.

Pre-fix, this test fails on two assertions at once: no `LedgerWriteFailed`
is raised (the error is swallowed) AND no ERROR-level record reaches
`caplog` (the error is `print()`ed).
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class _RaisingCursor:
    """Cursor whose every `execute` raises psycopg2.errors.UniqueViolation.

    This mirrors the anti-fork guard tripping on the `frank_ledger_no_fork`
    partial unique index — the exact failure the audit says must not be
    swallowed.
    """

    def execute(self, *a, **k):
        import psycopg2.errors

        raise psycopg2.errors.UniqueViolation(
            "duplicate key value violates unique constraint "
            "\"frank_ledger_no_fork\""
        )

    def fetchone(self):
        return None

    def close(self):
        pass


class _FakeConn:
    autocommit = False

    def cursor(self):
        return _RaisingCursor()

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass


def _install_fake_connect(monkeypatch):
    import psycopg2

    def fake_connect(*args, **kwargs):
        return _FakeConn()

    monkeypatch.setattr(psycopg2, "connect", fake_connect)


def test_ledger_write_error_raises_and_logs(monkeypatch, caplog, capsys):
    _install_fake_connect(monkeypatch)

    import grove_db

    # LedgerWriteFailed is Grove's new bounded-error vocabulary for a
    # ledger-write failure — analogous to Unreachable for readers.
    from grove.errors import LedgerWriteFailed

    caplog.set_level(logging.ERROR)

    raised: Exception | None = None
    try:
        grove_db._frank_ledger_append(
            "grove_agent_message",
            {"probe": "anti-fork guard tripped"},
        )
    except LedgerWriteFailed as e:
        raised = e
    except Exception as e:
        raised = e

    # (1) The failure must escape as a real exception, not evaporate to stdout.
    assert isinstance(raised, LedgerWriteFailed), (
        "ledger write failure must raise grove.errors.LedgerWriteFailed; "
        f"got {type(raised).__name__ if raised else 'no exception (silently swallowed)'}"
    )

    # (2) The failure must be logged at ERROR level via the module's logger,
    #     not printed to stdout.
    error_records = [r for r in caplog.records if r.levelno >= logging.ERROR]
    assert error_records, (
        "ledger write failure must emit an ERROR-level log record via "
        "logging.getLogger(__name__), not print() to stdout"
    )

    # (3) The message must name the failure so an operator can find it.
    joined = " ".join(r.getMessage() for r in error_records).lower()
    assert "ledger" in joined or "frank" in joined, (
        f"ERROR log must reference the ledger; got messages: "
        f"{[r.getMessage() for r in error_records]!r}"
    )
