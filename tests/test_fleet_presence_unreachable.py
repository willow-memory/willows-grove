# b17: WGRV1 ΔΣ=42
"""Regression pin for Loki M7 — ``grove.fleet_presence.roster`` honors
INVARIANTS.md §1 three-state.

Loki M7 finding: ``roster()`` returned ``[]`` in three cases — add-on
not importable, ``_fp.roster()`` raised, or store empty — collapsing
absent-seam and error-on-fetch into the same empty list. §1 forbids
this: a bare ``[]`` MUST NOT mean "unreachable" anywhere in the tree.

Fix: raise ``grove.errors.Unreachable`` when ``fleet_presence`` is not
importable, and re-raise ``Unreachable`` (wrapping the underlying
exception via ``raise ... from err``) when ``_fp.roster()`` raises.
Only the actually-empty case still returns ``[]``.

These tests are designed to fail on the pre-fix reader (which returns
``[]`` in the unreachable branches) and pass once the reader raises.
"""
from __future__ import annotations

import pytest

from grove import fleet_presence as gfp
from grove.errors import Unreachable


def test_roster_raises_unreachable_when_seam_not_importable(monkeypatch):
    """Absent add-on is unreachable, not empty (§1)."""
    monkeypatch.setattr(gfp, "_fp", None)
    monkeypatch.setattr(
        gfp, "_import_error", ImportError("fleet_presence not installed")
    )
    monkeypatch.setattr(gfp, "_logged_missing", False)

    with pytest.raises(Unreachable) as excinfo:
        gfp.roster()

    # The reason must name the seam so operators know what's absent.
    assert "fleet_presence" in excinfo.value.reason


def test_roster_wraps_seam_exception_as_unreachable(monkeypatch):
    """A seam that raises is unreachable, not empty (§1)."""

    class _Bad:
        def roster(self):
            raise RuntimeError("shared store down")

    monkeypatch.setattr(gfp, "_fp", _Bad())
    monkeypatch.setattr(gfp, "_import_error", None)
    monkeypatch.setattr(gfp, "_logged_missing", False)

    with pytest.raises(Unreachable) as excinfo:
        gfp.roster()

    # Reason preserves the underlying error text for the operator.
    assert "shared store down" in excinfo.value.reason
    # Wrapped via ``raise Unreachable(...) from err`` — cause preserved.
    assert isinstance(excinfo.value.__cause__, RuntimeError)


def test_roster_returns_empty_list_when_seam_reachable_and_empty(monkeypatch):
    """Only the actually-empty case still returns ``[]`` (§1).

    Pins the other side of the three-state contract — the fix must not
    over-broaden the raise into the reached-and-empty case.
    """

    class _Empty:
        def roster(self):
            return []

    monkeypatch.setattr(gfp, "_fp", _Empty())
    monkeypatch.setattr(gfp, "_import_error", None)
    monkeypatch.setattr(gfp, "_logged_missing", False)

    assert gfp.roster() == []
