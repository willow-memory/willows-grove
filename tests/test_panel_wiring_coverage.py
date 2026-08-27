# b17: WGRV1 ΔΣ=42
"""tests/test_panel_wiring_coverage.py — meta-pin for INVARIANTS.md §4.

§4 promises that ``tests/test_panel_wiring.py`` pins the endpoint /
reader / Web Component wire shape for **every row** of the §4 coverage
table. That table names six rows:

    /api/personas, /api/envelopes, /api/dispatch,
    /api/journal/recent, POST /api/journal, POST /api/nestor/decide.

The wire-shape file itself is therefore a §4 witness. This module
asserts the wire-shape file carries a WiringTests class for each row
and — per §1 — that every class defines the three-state test methods
appropriate for its verb: populated/empty/unreachable for the GET
rows, populated/unreachable for the write row (a successful write is
always populated, so there is no distinct empty case).

Against the pre-fix tree this file fails: ``PersonasWiringTests`` and
``JournalWriterWiringTests`` are absent from ``tests/test_panel_wiring.py``.
Once those two classes land the assertions pass.

Stdlib only. No harness, no server — the pin is purely structural.
"""
from __future__ import annotations

import importlib
import inspect
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


class PanelWiringCoverageTests(unittest.TestCase):
    """INVARIANTS.md §4 — every row has a WiringTests class in
    ``tests/test_panel_wiring.py`` with the three-state test methods
    §1 mandates for its verb."""

    def setUp(self) -> None:
        # Force a fresh import so a stale cached module from an earlier
        # test run cannot mask a missing class.
        if "tests.test_panel_wiring" in sys.modules:
            del sys.modules["tests.test_panel_wiring"]
        self.module = importlib.import_module("tests.test_panel_wiring")

    def _get_class(self, name: str) -> type:
        cls = getattr(self.module, name, None)
        self.assertIsNotNone(
            cls,
            f"{name} must exist in tests/test_panel_wiring.py "
            "(INVARIANTS.md §4 wire-shape coverage).",
        )
        self.assertTrue(
            inspect.isclass(cls) and issubclass(cls, unittest.TestCase),
            f"{name} must be a unittest.TestCase subclass.",
        )
        return cls

    def _test_method_names(self, cls: type) -> list[str]:
        return [
            name
            for name, _ in inspect.getmembers(cls, predicate=inspect.isfunction)
            if name.startswith("test_")
        ]

    def _assert_has_test_matching(self, cls: type, substr: str) -> None:
        names = self._test_method_names(cls)
        self.assertTrue(
            any(substr in n for n in names),
            f"{cls.__name__} must define a test method whose name contains "
            f"{substr!r} — the {substr} branch of INVARIANTS.md §1. "
            f"Found methods: {names}.",
        )

    # ---- GET /api/personas ----
    def test_personas_wiring_class_has_three_state_methods(self) -> None:
        cls = self._get_class("PersonasWiringTests")
        for branch in ("populated", "empty", "unreachable"):
            self._assert_has_test_matching(cls, branch)

    # ---- POST /api/journal ----
    def test_journal_writer_wiring_class_has_populated_and_unreachable(self) -> None:
        cls = self._get_class("JournalWriterWiringTests")
        # A successful write is always populated per INVARIANTS.md §1 —
        # writes have no distinct empty case, so only two branches are
        # required here.
        for branch in ("populated", "unreachable"):
            self._assert_has_test_matching(cls, branch)

    # ---- The four pre-existing rows must still be pinned — they were
    # the delivered baseline the finding cites; regressing any of them
    # would break §4 coverage just as badly as the missing rows did.
    def test_existing_wiring_classes_still_present(self) -> None:
        for name in (
            "EnvelopesWiringTests",
            "NestorDecideWiringTests",
            "DispatchWiringTests",
            "JournalRecentWiringTests",
        ):
            self._get_class(name)


if __name__ == "__main__":
    unittest.main()
