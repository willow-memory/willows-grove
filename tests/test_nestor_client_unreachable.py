# b17: WGRV1 ΔΣ=42
"""Regression: INVARIANTS.md §1 for the Nestor client's read-side helpers.

Loki v0.9 M6 finding: ``evidence_for``, ``warrant_for``, and ``refusal``
used to return a bare ``None`` on the unreachable branch (Nestor binary
not on PATH), collapsing "could-not-reach-the-source" into the same
sentinel as "reachable but no data". §1 forbids that collapse — every
reader raises ``Unreachable`` on the unreached state, and only on that
state.

The test drives each method under two scenarios:

* ``shutil.which`` returns ``None`` (the real "binary absent" probe path
  that ``available()`` reads) — every method MUST raise ``Unreachable``.
* ``_call`` is monkeypatched to return ``None`` while ``available()`` is
  forced true (the reachable-but-empty branch) — every method MUST
  return ``None``, keeping the empty state distinct from unreachable.

On the unfixed tree ``evidence_for`` / ``warrant_for`` / ``refusal``
bypass ``available()`` and just ``return self._call(...)``, which yields
``None`` when the binary is missing — so the "raises Unreachable"
assertions fail. On the fixed tree they probe first and raise, matching
``decision_check``'s existing shape.
"""
from __future__ import annotations

import pytest

from grove import nestor_client
from grove.errors import Unreachable
from grove.nestor_client import NestorClient


def test_evidence_for_raises_unreachable_when_binary_absent(monkeypatch):
    monkeypatch.setattr(nestor_client.shutil, "which", lambda _exe: None)
    nc = NestorClient()
    assert nc.available() is False
    with pytest.raises(Unreachable):
        nc.evidence_for("p42")
    nc.close()


def test_warrant_for_raises_unreachable_when_binary_absent(monkeypatch):
    monkeypatch.setattr(nestor_client.shutil, "which", lambda _exe: None)
    nc = NestorClient()
    assert nc.available() is False
    with pytest.raises(Unreachable):
        nc.warrant_for("p42")
    nc.close()


def test_refusal_raises_unreachable_when_binary_absent(monkeypatch):
    monkeypatch.setattr(nestor_client.shutil, "which", lambda _exe: None)
    nc = NestorClient()
    assert nc.available() is False
    with pytest.raises(Unreachable):
        nc.refusal("merge", branch="main")
    nc.close()


def test_call_returning_none_while_reachable_is_still_empty_not_unreachable(monkeypatch):
    """The reachable-but-no-data branch must stay ``None``; §1 reserves
    ``Unreachable`` for the source-not-reached state.

    Monkeypatches ``NestorClient._call`` to return ``None`` while
    ``available()`` is forced true — all three helpers must return
    ``None`` here, not raise. This half of the contract is what prevents
    the fix from over-shooting into raising on every empty response.
    """
    monkeypatch.setattr(nestor_client.shutil, "which", lambda _exe: "/usr/local/bin/nestor")
    monkeypatch.setattr(NestorClient, "_call", lambda self, method, params: None)
    nc = NestorClient()
    assert nc.available() is True
    assert nc.evidence_for("p42") is None
    assert nc.warrant_for("p42") is None
    assert nc.refusal("merge") is None
    nc.close()
