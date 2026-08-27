# b17: WGRV1 ΔΣ=42
"""Tests for grove.fleet_presence — mocked seam + absent-seam no-op."""
from __future__ import annotations

import types

from grove import fleet_presence as gfp


class _FakeFP:
    def __init__(self):
        self.calls = []
        self._roster = [{"app_id": "willow", "summary": "primary interface", "counts": {}}]

    def announce(self, app_id, summary, counts):
        self.calls.append(("announce", app_id, summary, counts))
        return True

    def roster(self):
        self.calls.append(("roster",))
        return list(self._roster)

    def withdraw(self, app_id):
        self.calls.append(("withdraw", app_id))
        return True


def _install(monkeypatch, fake=None):
    fake = fake or _FakeFP()
    monkeypatch.setattr(gfp, "_fp", fake)
    monkeypatch.setattr(gfp, "_import_error", None)
    monkeypatch.setattr(gfp, "_logged_missing", False)
    return fake


def test_announce_grove_calls_seam(monkeypatch):
    fake = _install(monkeypatch)
    ok = gfp.announce_grove("seat live", {"cards": 3})
    assert ok is True
    assert fake.calls == [("announce", "grove", "seat live", {"cards": 3})]


def test_roster_returns_atoms(monkeypatch):
    _install(monkeypatch)
    out = gfp.roster()
    assert out and out[0]["app_id"] == "willow"


def test_withdraw_calls_seam(monkeypatch):
    fake = _install(monkeypatch)
    assert gfp.withdraw() is True
    assert ("withdraw", "grove") in fake.calls


def test_absent_seam_is_noop(monkeypatch, caplog):
    monkeypatch.setattr(gfp, "_fp", None)
    monkeypatch.setattr(gfp, "_import_error", ImportError("fleet_presence not installed"))
    monkeypatch.setattr(gfp, "_logged_missing", False)
    caplog.set_level("INFO")
    assert gfp.announce_grove("x", {}) is False
    assert gfp.roster() == []
    assert gfp.withdraw() is False
    # log-once discipline
    info_msgs = [r for r in caplog.records if "not installed" in r.message]
    assert len(info_msgs) == 1, "seam-missing log must fire exactly once"


def test_announce_swallows_seam_exception(monkeypatch):
    class _Bad:
        def announce(self, *a, **k):
            raise RuntimeError("db locked")
    _install(monkeypatch, fake=_Bad())
    assert gfp.announce_grove("x", {}) is False


def test_roster_swallows_seam_exception(monkeypatch):
    class _Bad:
        def roster(self):
            raise RuntimeError("db locked")
    _install(monkeypatch, fake=_Bad())
    assert gfp.roster() == []


def test_withdraw_missing_function_is_noop(monkeypatch):
    fake = types.SimpleNamespace(announce=lambda *a, **k: True, roster=lambda: [])
    _install(monkeypatch, fake=fake)
    assert gfp.withdraw() is False
