# b17: WGRV1 ΔΣ=42
"""tests/test_nestor_bundle_domain.py — one domain across three surfaces.

Nestor keys every pair by a ``(source_lang, target_lang)`` tuple and
will not serve across domains. A query in one domain against a store
written in another does not error and does not report a reachability
problem — it answers::

    ✓ clear — no decision on record for '<question>'

which is indistinguishable from a genuinely empty record. That is the
failure this module exists to prevent, and it is worse than the
unreachable state §1 is built around: unreachable is a state Grove can
render, and this is a clean, confident, wrong answer with nothing for a
caller to notice.

It has now happened twice on the same store. The bundle was first
written ``question→finding``, which ``nestor decision check`` could not
see; that was diagnosed and the fix landed as ``grove→grove``, which
``nestor decision check`` also cannot see, for exactly the same reason.
Both tags matched each other, so the rule everyone was checking
(``docs/decision-memory.md`` N8 — the domain rides in both tags
identically) was satisfied both times. Matching each other was never
sufficient; they have to match the domain the *readers* query.

Three surfaces read or write that domain, and all three must agree:

1. ``grove.nestor_client.DECISION_DOMAIN`` — Grove's own reader.
2. ``.mcp.json`` — the ``nestor serve`` argv for the session store.
3. ``nestor/session-decisions.json`` — the shipped bundle, top-level
   and per-pair.

``DECISION_DOMAIN`` is the single source of truth; the other two are
checked against it. Its value is ``decision`` because that is also the
CLI's own default for ``nestor decision check``, so an operator typing
the bare command with no flags lands in the same domain Grove does.
That last property is the one that was missing before: the MCP path
carried an explicit ``--source-lang``/``--target-lang`` and worked,
while the human at the keyboard got "clear".

Stdlib only, no ``nestor`` binary, no network — a wrong domain imports
cleanly and only shows up at query time, so this pin has to be
structural to run everywhere. ``NestorBundleQueryableTests`` adds the
end-to-end check when the binary happens to be installed.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from grove.nestor_client import DECISION_DOMAIN  # noqa: E402

BUNDLE = os.path.join(ROOT, "nestor", "session-decisions.json")
MCP_JSON = os.path.join(ROOT, ".mcp.json")
SERVER = "nestor-grove-session"


def _load(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _serve_args() -> list[str]:
    entry = _load(MCP_JSON)["mcpServers"][SERVER]
    return list(entry["args"])


def _flag(args: list[str], name: str) -> str:
    """Return the value following ``name`` in an argv list."""
    idx = args.index(name)
    return args[idx + 1]


class BundleDomainTests(unittest.TestCase):
    """The shipped bundle is keyed to the domain Grove queries."""

    def setUp(self) -> None:
        self.bundle = _load(BUNDLE)

    def test_top_level_domain_matches_reader(self) -> None:
        domain = self.bundle["domain"]
        self.assertEqual(
            domain["source_lang"],
            DECISION_DOMAIN,
            "bundle source_lang must match grove.nestor_client.DECISION_DOMAIN "
            "or decision_check silently returns 'no decision on record'.",
        )
        self.assertEqual(
            domain["target_lang"],
            DECISION_DOMAIN,
            "bundle target_lang must match grove.nestor_client.DECISION_DOMAIN.",
        )

    def test_every_pair_carries_the_same_domain(self) -> None:
        """N8: the domain rides in both tags, identically, on every row.

        A bundle whose top-level domain is right but whose rows disagree
        imports without complaint and is then partially invisible — the
        worst version, because a spot-check on one question passes.
        """
        pairs = self.bundle["pairs"]
        self.assertTrue(pairs, "bundle carries no pairs to check")
        for pair in pairs:
            with self.subTest(pair=pair.get("id")):
                self.assertEqual(pair["source_lang"], DECISION_DOMAIN)
                self.assertEqual(pair["target_lang"], DECISION_DOMAIN)

    def test_domain_tags_are_identical(self) -> None:
        """Guards the original ``question→finding`` shape directly."""
        domain = self.bundle["domain"]
        self.assertEqual(
            domain["source_lang"],
            domain["target_lang"],
            "a decision's domain rides in BOTH language tags identically "
            "(docs/decision-memory.md N8); a bundle written as "
            "question→finding imports fine and is then unqueryable.",
        )


class McpEntryDomainTests(unittest.TestCase):
    """``.mcp.json``'s serve argv agrees with the reader and the bundle."""

    def test_serve_argv_pins_the_reader_domain(self) -> None:
        args = _serve_args()
        self.assertEqual(_flag(args, "--source-lang"), DECISION_DOMAIN)
        self.assertEqual(_flag(args, "--target-lang"), DECISION_DOMAIN)

    def test_serve_argv_agrees_with_the_bundle(self) -> None:
        """The MCP path must not be able to work while the CLI path fails.

        This is the divergence that hid the bug: the serve entry carried
        an explicit domain and answered correctly, so an agent asking
        through MCP saw the record while an operator asking through the
        CLI was told there was none.
        """
        args = _serve_args()
        domain = _load(BUNDLE)["domain"]
        self.assertEqual(_flag(args, "--source-lang"), domain["source_lang"])
        self.assertEqual(_flag(args, "--target-lang"), domain["target_lang"])

    def test_serve_entry_points_at_the_committed_bundle_paths(self) -> None:
        """The store and ledger the entry names are the ones the README
        tells you to build, so a correct bundle cannot be served from a
        path nothing populates."""
        args = _serve_args()
        self.assertEqual(_flag(args, "--db"), "nestor/grove-session.db")
        self.assertEqual(
            _flag(args, "--ledger"), "nestor/grove-session.db.ledger.jsonl"
        )


@unittest.skipIf(
    shutil.which("nestor") is None,
    "nestor binary not installed in this environment "
    "(pip install '.[nestor]') — the structural pins above run everywhere "
    "and are the primary defense; this is the end-to-end confirmation.",
)
class NestorBundleQueryableTests(unittest.TestCase):
    """End-to-end: the shipped bundle answers the *bare* CLI invocation.

    The structural pins cannot prove that ``DECISION_DOMAIN`` is the
    value the CLI actually defaults to — only that all three surfaces
    agree on whatever it is. If a future Nestor changes its default,
    this is the test that notices.
    """

    def test_bare_decision_check_finds_a_known_commitment(self) -> None:
        question = _load(BUNDLE)["pairs"][0]["source_text"]
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ)
            env["NESTOR_DB"] = os.path.join(tmp, "pin.db")
            subprocess.run(
                ["nestor", "import", "--apply", "--verifier", "pin", BUNDLE],
                check=True,
                capture_output=True,
                env=env,
                timeout=120,
            )
            # No --from / --to. That is the whole point: this is what an
            # operator types, and it must not answer "no decision on record".
            done = subprocess.run(
                ["nestor", "decision", "check", question],
                check=True,
                capture_output=True,
                text=True,
                env=env,
                timeout=120,
            )
        self.assertNotIn(
            "no decision on record",
            done.stdout,
            "the bare `nestor decision check` must see the shipped bundle; "
            f"got:\n{done.stdout}",
        )


if __name__ == "__main__":
    unittest.main()
