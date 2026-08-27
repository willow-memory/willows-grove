# b17: WGRV1 ΔΣ=42
"""tests/test_seed_reader_probe_expansion.py — probe path resolution.

INVARIANTS.md §9 ("Seed reads real canon"): the reader's
``locate_seed_dir()`` walks the WILLOW_HOME → ~/willow-memory →
~/.willow probe order. This suite pins each rung so a future refactor
that changes the search order (or forgets to fall back) fails loudly,
not silently.

The absence case is asserted here too: no seed dir on any probe path
means ``locate_seed_dir()`` returns None, ``load_movements()`` returns
the six-movement D16 stub, and the "seed not found" INFO line fires
exactly once per process (C3 continuity: /seed/ survives absence).

Stdlib only. Restores WILLOW_HOME / HOME / USERPROFILE in every case.
"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


from grove import seed_reader  # noqa: E402


REAL_CANON = Path("/home/user/willow-memory/willow/seed/canon")
REAL_SEED = REAL_CANON.parent  # /home/user/willow-memory/willow/seed


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

    # ── WILLOW_HOME → real canon (only when the box has it) ──────────────
    def test_willow_home_resolves_to_real_seed_with_canon(self) -> None:
        if not REAL_CANON.is_dir():
            self.skipTest(
                f"real canon not present at {REAL_CANON}; probe test only"
                " runs on a box with the fleet_charter mirror"
            )
        with _EnvSandbox(willow_home="/home/user", home=None):
            located = seed_reader.locate_seed_dir()
        # The reader returns the seed dir; canon/ lives inside it.
        self.assertIsNotNone(located)
        assert located is not None  # narrow type for mypy-style readers
        self.assertEqual(located, REAL_SEED)
        # And canon/ is where load_movements() will find the six files.
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

    def test_load_movements_from_willow_home_matches_real_canon(self) -> None:
        if not REAL_CANON.is_dir():
            self.skipTest("real canon not present; test requires the mirror")
        with _EnvSandbox(willow_home="/home/user", home=None):
            movements = seed_reader.load_movements()
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

    # ── unset WILLOW_HOME → home-dir probe fallback ──────────────────────
    def test_unset_willow_home_falls_back_to_home_dir_probe(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            home = root / "home"
            preferred = home / "willow-memory" / "willow" / "seed"
            preferred.mkdir(parents=True)
            with _EnvSandbox(willow_home=None, home=home):
                located = seed_reader.locate_seed_dir()
        self.assertEqual(located, preferred)

    def test_unset_willow_home_home_probe_also_finds_dot_willow(self) -> None:
        """The third probe rung — ~/.willow/seed — is reached when the
        second (~/willow-memory/willow/seed) is absent.
        """
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            home = root / "home"
            # Only the ~/.willow/seed rung is populated.
            dot_seed = home / ".willow" / "seed"
            dot_seed.mkdir(parents=True)
            with _EnvSandbox(willow_home=None, home=home):
                located = seed_reader.locate_seed_dir()
        self.assertEqual(located, dot_seed)

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
