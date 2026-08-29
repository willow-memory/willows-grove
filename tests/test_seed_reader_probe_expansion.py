# b17: WGRV1 ΔΣ=42
"""tests/test_seed_reader_probe_expansion.py — probe path resolution.

INVARIANTS.md §9 ("Seed reads real canon"): the reader's
``locate_seed_dir()`` walks the ``$WILLOW_HOME/seed`` → in-repo
``governance/seed`` probe order (D7/D10 discipline, mirrors
``grove/persona_roster.py``). This suite pins each rung so a future
refactor that changes the search order (or forgets to fall back) fails
loudly, not silently.

The absence case is asserted here too: with the in-repo fallback
pointed at an empty tmp dir and no ``$WILLOW_HOME`` seed dir on disk,
``locate_seed_dir()`` returns None, ``load_movements()`` returns the
six-movement D16 stub, and the "seed not found" INFO line fires exactly
once per process (C3 continuity: /seed/ survives absence). Every test
that means to exercise this "no seed dir on any probe path" case must
patch ``seed_reader._IN_REPO_SEED_PATH`` to an empty dir first —
otherwise, now that a real canon lives in this repo at
``governance/seed/``, the fallback would silently resolve and the
absence case would no longer be reachable in tests.

Stdlib only. Restores WILLOW_HOME / HOME / USERPROFILE in every case,
and restores ``_IN_REPO_SEED_PATH`` via ``addCleanup``.
"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


from grove import seed_reader  # noqa: E402


# The real in-repo canon this repo now ships (relocated from the
# archived charter repository per governance/README.md).
REAL_SEED = seed_reader._REPO_ROOT / "governance" / "seed"
REAL_CANON = REAL_SEED / "canon"


class _EnvSandbox:
    """Force-set WILLOW_HOME / HOME / USERPROFILE, restore on exit."""

    def __init__(
        self,
        willow_home: Path | str | None,
        home: Path | str | None,
    ) -> None:
        self.willow_home = willow_home
        self.home = home
        self._saved: dict[str, str | None] = {}

    def __enter__(self) -> "_EnvSandbox":
        for name in ("WILLOW_HOME", "HOME", "USERPROFILE"):
            self._saved[name] = os.environ.get(name)
        if self.willow_home is None:
            os.environ.pop("WILLOW_HOME", None)
        else:
            os.environ["WILLOW_HOME"] = str(self.willow_home)
        if self.home is not None:
            os.environ["HOME"] = str(self.home)
            os.environ["USERPROFILE"] = str(self.home)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        for name, val in self._saved.items():
            if val is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = val


class SeedReaderProbeExpansionTests(unittest.TestCase):
    def setUp(self) -> None:
        # Reset log-once so each test is independent.
        seed_reader._logged_absent = False

        # Default every test to an empty in-repo fallback, isolated from
        # this repo's real governance/seed/ canon. Tests that want the
        # real fallback restore it explicitly (see below).
        self._fallback_tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._fallback_tmp.cleanup)
        no_fallback_dir = Path(self._fallback_tmp.name) / "no-fallback" / "seed"
        self._fallback_patch = mock.patch.object(
            seed_reader, "_IN_REPO_SEED_PATH", no_fallback_dir
        )
        self._fallback_patch.start()
        self.addCleanup(self._fallback_patch.stop)

    # ── WILLOW_HOME → per-node seed dir ───────────────────────────────────
    def test_willow_home_resolves_to_willow_home_seed_dir(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            wh = root / "wh"
            preferred = wh / "seed"
            preferred.mkdir(parents=True)
            with _EnvSandbox(willow_home=wh, home=None):
                located = seed_reader.locate_seed_dir()
            self.assertEqual(located, preferred)

    # ── in-repo fallback → the real canon this repo ships ────────────────
    def test_in_repo_fallback_resolves_to_real_canon(self) -> None:
        """With the fallback patch removed, the second probe rung is this
        repo's real ``governance/seed/`` — the canon relocated in from the
        archived charter repository."""
        self._fallback_patch.stop()
        try:
            with _EnvSandbox(willow_home=None, home="/nonexistent-probe-home"):
                located = seed_reader.locate_seed_dir()
            self.assertEqual(located, REAL_SEED)
            self.assertTrue((located / "canon").is_dir())
            for name in (
                "00-the-covenant.md",
                "01-be-the-other.md",
                "02-the-discipline.md",
                "03-the-person.md",
                "04-the-language.md",
                "05-the-world.md",
            ):
                self.assertTrue((located / "canon" / name).is_file())
        finally:
            self._fallback_patch.start()

    def test_load_movements_from_in_repo_fallback_matches_real_canon(self) -> None:
        self._fallback_patch.stop()
        try:
            with _EnvSandbox(willow_home=None, home="/nonexistent-probe-home"):
                movements = seed_reader.load_movements()
        finally:
            self._fallback_patch.start()
        self.assertEqual([m["n"] for m in movements], [1, 2, 3, 4, 5, 6])
        # Every body is the raw text of the corresponding canon file.
        for idx, name in enumerate((
            "00-the-covenant.md",
            "01-be-the-other.md",
            "02-the-discipline.md",
            "03-the-person.md",
            "04-the-language.md",
            "05-the-world.md",
        )):
            expected = (REAL_CANON / name).read_text(encoding="utf-8")
            self.assertEqual(
                movements[idx]["body"],
                expected,
                f"movement {idx + 1} body does not match {name} verbatim",
            )

    # ── $WILLOW_HOME wins over the in-repo fallback on collision ──────────
    def test_willow_home_wins_over_in_repo_fallback(self) -> None:
        self._fallback_patch.stop()
        try:
            with tempfile.TemporaryDirectory() as td:
                wh = Path(td) / "wh"
                preferred = wh / "seed"
                preferred.mkdir(parents=True)
                with _EnvSandbox(willow_home=wh, home=None):
                    located = seed_reader.locate_seed_dir()
                self.assertEqual(located, preferred)
                self.assertNotEqual(located, REAL_SEED)
        finally:
            self._fallback_patch.start()

    # ── no seed anywhere → stub + log-once ──────────────────────────────
    def test_no_seed_dir_returns_none_and_stub_load_movements_logs_once(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            willow_home = root / "willow-home"  # never created
            home = root / "home"                 # empty
            home.mkdir()
            with _EnvSandbox(willow_home=willow_home, home=home):
                # No seed anywhere: locate_seed_dir returns None silently.
                self.assertIsNone(seed_reader.locate_seed_dir())
                # And load_movements returns the D16 stub + logs once.
                with self.assertLogs("grove.seed_reader", level="INFO") as cap:
                    m1 = seed_reader.load_movements()
                    m2 = seed_reader.load_movements()
        self.assertEqual(len(m1), 6)
        self.assertEqual(m1, m2)
        self.assertEqual([m["n"] for m in m1], [1, 2, 3, 4, 5, 6])
        for m in m1:
            self.assertTrue(m["body"].strip())
        info_lines = [ln for ln in cap.output if ln.startswith("INFO:")]
        self.assertEqual(
            len(info_lines), 1, f"expected one INFO log line, got {cap.output}"
        )


if __name__ == "__main__":
    unittest.main()
