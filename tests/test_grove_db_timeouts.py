# b17: WGRV1 ΔΣ=42
"""tests/test_grove_db_timeouts.py — bounded Postgres connect timeouts.

CLAUDE.md pins "If Postgres is down, surface it and stop." grove_db.py's
three psycopg2 entry points (pool DSN at :54, LISTEN at :102, ledger
writer at :344) opened connections with no connect_timeout, so a
stuck-but-reachable Postgres hung the whole surface instead of
surfacing.

Loki v0.9 finding #21 (cross-cutting-hazards, major): every psycopg2
connection Grove opens must be bounded by `connect_timeout=` — a
positive integer, configurable via `GROVE_PG_CONNECT_TIMEOUT`.

These tests monkeypatch `psycopg2.connect` and assert the kwarg is
passed. `listen_connection` and `_frank_ledger_append` are the two
psycopg2.connect call sites; both must pass the timeout. Pre-fix, both
call `psycopg2.connect(dsn)` / `psycopg2.connect(dbname=..., user=...)`
with no `connect_timeout=` at all, so `captured["connect_timeout"]`
is absent and every assertion below fails.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class _FakeConn:
    """Minimal stand-in for a psycopg2 connection."""

    autocommit = False

    def __init__(self) -> None:
        self.closed = False

    def cursor(self):
        return _FakeCursor()

    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass

    def close(self) -> None:
        self.closed = True


class _FakeCursor:
    def execute(self, *a, **k):
        return None

    def fetchone(self):
        return None

    def fetchall(self):
        return []

    def close(self):
        pass


def _install_fake_connect(monkeypatch):
    """Replace psycopg2.connect with a capturing stub. Returns the capture list."""
    import psycopg2

    captured: list[dict] = []

    def fake_connect(*args, **kwargs):
        captured.append({"args": args, "kwargs": kwargs})
        return _FakeConn()

    monkeypatch.setattr(psycopg2, "connect", fake_connect)
    return captured


def test_listen_connection_passes_connect_timeout(monkeypatch):
    captured = _install_fake_connect(monkeypatch)

    import grove_db

    grove_db.listen_connection()

    assert captured, "psycopg2.connect was not called"
    kw = captured[-1]["kwargs"]
    assert "connect_timeout" in kw, (
        f"listen_connection must pass connect_timeout kwarg; got kwargs={kw}"
    )
    assert isinstance(kw["connect_timeout"], int), (
        f"connect_timeout must be int, got {type(kw['connect_timeout']).__name__}"
    )
    assert kw["connect_timeout"] > 0, (
        f"connect_timeout must be a positive int, got {kw['connect_timeout']}"
    )


def test_listen_connection_respects_env_override(monkeypatch):
    monkeypatch.setenv("GROVE_PG_CONNECT_TIMEOUT", "3")
    captured = _install_fake_connect(monkeypatch)

    import grove_db

    grove_db.listen_connection()

    assert captured, "psycopg2.connect was not called"
    kw = captured[-1]["kwargs"]
    assert kw.get("connect_timeout") == 3, (
        f"GROVE_PG_CONNECT_TIMEOUT=3 must propagate to connect_timeout kwarg, "
        f"got {kw.get('connect_timeout')!r}"
    )


def test_frank_ledger_append_passes_connect_timeout(monkeypatch):
    captured = _install_fake_connect(monkeypatch)

    import grove_db

    # _frank_ledger_append swallows LedgerWriteFailed at higher call sites,
    # but here we call it directly and let it raise/return however it likes;
    # we only care that psycopg2.connect was reached with the timeout kwarg.
    try:
        grove_db._frank_ledger_append("test_event", {"probe": "connect_timeout"})
    except Exception:
        # Fake conn's cursor returns None on fetchone; the INSERT is fine.
        # Any exception here does not disprove that psycopg2.connect was called.
        pass

    assert captured, "psycopg2.connect was not called by _frank_ledger_append"
    kw = captured[-1]["kwargs"]
    assert "connect_timeout" in kw, (
        f"_frank_ledger_append must pass connect_timeout kwarg; got kwargs={kw}"
    )
    assert isinstance(kw["connect_timeout"], int) and kw["connect_timeout"] > 0, (
        f"connect_timeout must be a positive int, got {kw.get('connect_timeout')!r}"
    )
