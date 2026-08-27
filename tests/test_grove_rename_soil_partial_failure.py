# b17: WGRV1 ΔΣ=42
"""tests/test_grove_rename_soil_partial_failure.py — SOIL migration failure
must surface, not be swallowed into a fake "ok".

Loki v0.9 finding #38 (minor, cross-cutting-hazards): `grove_reader.
_migrate_soil_channel_cursors` catches every exception itself and only
logs a warning, so `grove_rename_channel` always reports `{"ok": True, ...}`
after the Postgres row rename commits — even when the SOIL cursor
migration (moving the channel's read-cursor bookkeeping to the new name)
silently failed. The caller has no way to know the rename was only a
partial success.

Fix: `grove_rename_channel` must detect a `_migrate_soil_channel_cursors`
failure and return a dict that signals partial failure (`ok: False` with
an error naming the SOIL step) instead of `{"ok": True}`.

This test monkeypatches `_migrate_soil_channel_cursors` to raise, drives
`grove_rename_channel` against a fake DB connection/pool (no live
Postgres), and asserts the return dict does NOT claim unqualified success.

Pre-fix, `grove_rename_channel` returns `{"ok": True, "name": new_name}`
regardless — this test fails on the unfixed code.

Stdlib only. No live database.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import grove_db  # noqa: E402
import grove_reader  # noqa: E402


class _FakeCursor:
    """Simulates: target name free, rename UPDATE hits exactly one row."""

    def __init__(self) -> None:
        self._next = None

    def execute(self, sql, params=None):
        sql_norm = " ".join(sql.split())
        if sql_norm.startswith("SELECT id FROM grove.channels"):
            self._next = "select"
        elif sql_norm.startswith("UPDATE grove.channels"):
            self._next = "update"
        else:
            self._next = None

    def fetchone(self):
        if self._next == "select":
            return None  # target name does not already exist
        if self._next == "update":
            return (1,)  # exactly one row renamed
        return None

    def close(self):
        pass


class _FakeConn:
    def __init__(self) -> None:
        self.committed = False

    def cursor(self):
        return _FakeCursor()

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        pass


def test_rename_reports_partial_failure_when_soil_migration_fails(monkeypatch) -> None:
    fake_conn = _FakeConn()
    monkeypatch.setattr(grove_db, "get_connection", lambda: fake_conn)
    monkeypatch.setattr(grove_db, "release_connection", lambda c: None)

    def _boom(old_name, new_name):
        raise RuntimeError("simulated: SOIL store unreachable")

    monkeypatch.setattr(grove_reader, "_migrate_soil_channel_cursors", _boom)

    result = grove_reader.grove_rename_channel("old-channel", "new-channel")

    # The Postgres rename itself must still have committed — this is a
    # partial-success case, not a full rollback.
    assert fake_conn.committed, (
        "the channel row rename must commit even though SOIL migration "
        "failed afterward; this is a partial-success case."
    )

    assert result.get("ok") is not True, (
        f"grove_rename_channel must not report unqualified success when "
        f"SOIL cursor migration failed; got {result!r}"
    )
    assert result.get("error"), (
        f"grove_rename_channel must surface an error describing the SOIL "
        f"migration failure; got {result!r}"
    )
    assert "soil" in result["error"].lower(), (
        f"the error should name SOIL cursor migration as the failed step; "
        f"got {result['error']!r}"
    )
