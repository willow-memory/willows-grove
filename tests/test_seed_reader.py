"""tests/test_seed_reader.py — unit tests for grove.seed_reader.
b17: WGRV1  ΔΣ=42

Covers three shapes:

* Seed dir absent on every probe path → six-movement D16 stub, log-once.
* Seed dir present with six ``NN-*.md`` canon files → parsed movements
  in order.
* Seed dir present with a single ``seed.py`` (SEED9 shape) → parsed
  movements via docstring extraction.

The seed reader now falls back to the in-repo canon at
``governance/seed/`` (see ``grove/seed_reader.py``), so every test here
that means to exercise "no seed dir on any probe path" points the
in-repo fallback (``seed_reader._IN_REPO_SEED_PATH``) at an empty tmp
dir first — otherwise it would silently pick up this repo's real
canon and the absence case would no longer be reachable in tests
(INVARIANTS.md §1: absence must stay a tested, reachable state).
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


class _EnvSandbox:
    """Push WILLOW_HOME to a scratch path, isolate HOME/USERPROFILE too.

    ``_candidate_dirs()`` only consults ``$WILLOW_HOME`` and the in-repo
    fallback now, but HOME/USERPROFILE are still isolated defensively so
    nothing on the real filesystem leaks in via an unrelated code path.
    """

    def __init__(self, willow_home: Path | None, home: Path) -> None:
        self.willow_home = willow_home
        self.home = home
        self._prev_willow_home: str | None = None
        self._prev_home: str | None = None
        self._prev_userprofile: str | None = None

    def __enter__(self) -> "_EnvSandbox":
        self._prev_willow_home = os.environ.get("WILLOW_HOME")
        self._prev_home = os.environ.get("HOME")
        self._prev_userprofile = os.environ.get("USERPROFILE")
        if self.willow_home is None:
            os.environ.pop("WILLOW_HOME", None)
        else:
            os.environ["WILLOW_HOME"] = str(self.willow_home)
        os.environ["HOME"] = str(self.home)
        # Path.home() consults USERPROFILE on some hosts.
        os.environ["USERPROFILE"] = str(self.home)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        for name, val in (
            ("WILLOW_HOME", self._prev_willow_home),
            ("HOME", self._prev_home),
            ("USERPROFILE", self._prev_userprofile),
        ):
            if val is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = val


class SeedReaderTests(unittest.TestCase):
    def setUp(self) -> None:
        # Reset log-once so each test's log assertion is independent.
        seed_reader._logged_absent = False

        # Point the in-repo fallback at an empty tmp dir by default, so
        # these tests exercise only the $WILLOW_HOME override and stay
        # isolated from this repo's real governance/seed/ canon. Tests
        # that specifically want the fallback path patch this themselves.
        self._fallback_tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._fallback_tmp.cleanup)
        no_fallback_dir = Path(self._fallback_tmp.name) / "no-fallback" / "seed"
        self._fallback_patch = mock.patch.object(
            seed_reader, "_IN_REPO_SEED_PATH", no_fallback_dir
        )
        self._fallback_patch.start()
        self.addCleanup(self._fallback_patch.stop)

    # ── absence ──────────────────────────────────────────────────────────
    def test_absent_seed_dir_returns_stub_and_logs_once(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            willow_home = root / "willow-home"   # never created
            home = root / "home"                  # empty
            home.mkdir()
            with _EnvSandbox(willow_home=willow_home, home=home):
                with self.assertLogs("grove.seed_reader", level="INFO") as cap:
                    m1 = seed_reader.load_movements()
                    # Second call: no additional log line (log-once).
                    m2 = seed_reader.load_movements()

        self.assertEqual(len(m1), 6)
        self.assertEqual(m1, m2)
        self.assertEqual([m["n"] for m in m1], [1, 2, 3, 4, 5, 6])
        for m in m1:
            self.assertIn("slug", m)
            self.assertIn("title", m)
            self.assertIn("body", m)
            self.assertTrue(m["body"].strip())
        # Exactly one log line — the log-once guard.
        info_lines = [ln for ln in cap.output if ln.startswith("INFO:")]
        self.assertEqual(len(info_lines), 1, cap.output)

    # ── canon/ shape ─────────────────────────────────────────────────────
    def test_canon_dir_with_six_md_files_parses_in_order(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            home = root / "home"
            seed = root / "willow-home" / "seed"
            canon = seed / "canon"
            canon.mkdir(parents=True)

            titles = [
                ("00-the-covenant.md",     "# The Covenant\n\nAgreement inherited."),
                ("01-be-the-other.md",     "# Be The Other\n\nA partner refuses."),
                ("02-the-discipline.md",   "# The Discipline\n\nVerify, don't assert."),
                ("03-the-person.md",       "# The Person\n\nThe one you serve."),
                ("04-the-language.md",     "# The Language\n\nGerald has no write authority."),
                ("05-the-world.md",        "# The World\n\nThe fleet is parts with edges."),
            ]
            for name, body in titles:
                (canon / name).write_text(body, encoding="utf-8")

            with _EnvSandbox(willow_home=root / "willow-home", home=home):
                movements = seed_reader.load_movements()

        self.assertEqual([m["n"] for m in movements], [1, 2, 3, 4, 5, 6])
        # Slugs come from the source file stems.
        self.assertEqual(movements[0]["slug"], "the-covenant")
        self.assertEqual(movements[5]["slug"], "the-world")
        # Bodies are the raw markdown, verbatim.
        self.assertIn("Agreement inherited.", movements[0]["body"])
        self.assertIn("The fleet is parts with edges.", movements[5]["body"])
        # Titles humanized from stem.
        self.assertIn("Covenant", movements[0]["title"])

    # ── seed.py shape ────────────────────────────────────────────────────
    def test_seed_py_single_file_parses_movements(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            home = root / "home"
            seed = root / "willow-home" / "seed"
            seed.mkdir(parents=True)

            # Minimal SEED9-shape seed.py — six movement_N_<slug> defs
            # with docstrings whose first line carries the load-bearing
            # sentence. No canon/ dir, no top-level NN-*.md files.
            content = '''"""seed.py stub."""

def movement_0_covenant(ui):
    """The Covenant — who you are, the agreement, the keys, the box."""
    return {}


def movement_1_other(ui):
    """Be the Other — choose the voice that will refuse to be a mirror."""
    return {}


def movement_2_discipline(ui, ident):
    """The Discipline — the install itself, gate by gate, verified not asserted."""
    return "", []


def movement_3_person(ui, provider, api_key, name_str):
    """The Person — Willow meets you; nothing is remembered without a yes."""
    return []


def movement_4_language(ui):
    """The Language — the myth arrives. Gerald, ΔΣ=42, the witness."""
    return None


def movement_5_world(ui):
    """The World — the fleet around you; opt in to only what you need."""
    return {}
'''
            (seed / "seed.py").write_text(content, encoding="utf-8")

            with _EnvSandbox(willow_home=root / "willow-home", home=home):
                movements = seed_reader.load_movements()

        self.assertEqual([m["n"] for m in movements], [1, 2, 3, 4, 5, 6])
        # Slugs come from the underscore→dash rewrite of the function name suffix.
        slugs = [m["slug"] for m in movements]
        self.assertEqual(slugs[0], "covenant")
        self.assertEqual(slugs[1], "other")
        self.assertEqual(slugs[5], "world")
        # First non-blank docstring line as body.
        self.assertIn("The Covenant", movements[0]["body"])
        self.assertIn("Be the Other", movements[1]["body"])
        self.assertIn("The World", movements[5]["body"])

    def test_locate_seed_dir_prefers_willow_home_when_set(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            home = root / "home"
            wh = root / "wh"
            preferred = wh / "seed"
            preferred.mkdir(parents=True)
            with _EnvSandbox(willow_home=wh, home=home):
                located = seed_reader.locate_seed_dir()
            self.assertEqual(located, preferred)

    def test_locate_seed_dir_falls_back_to_in_repo_canon_when_unset(self) -> None:
        """With no ``$WILLOW_HOME`` and no fallback patch, the reader finds
        this repo's real canon at ``governance/seed/`` — the "reliable
        fallback" the relocation exists to provide."""
        self._fallback_patch.stop()  # restore the real in-repo path
        try:
            with tempfile.TemporaryDirectory() as td:
                home = Path(td) / "home"
                home.mkdir()
                with _EnvSandbox(willow_home=None, home=home):
                    located = seed_reader.locate_seed_dir()
            self.assertEqual(located, seed_reader._IN_REPO_SEED_PATH)
            self.assertTrue((located / "canon").is_dir())
        finally:
            self._fallback_patch.start()


if __name__ == "__main__":
    unittest.main()
