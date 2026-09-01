# b17: WGRV1 ΔΣ=42
"""tests/test_architecture_links_resolve.py — the canonical reference resolves.

``docs/ARCHITECTURE.md`` is the canonical architecture reference (CAR) for
this repository. It carried three links that went nowhere, and all three
pointed at exactly the cross-repo material nothing else documents — so a
reader who followed them to understand how Grove meets the rest of the
fleet arrived at a 404 and had no other route:

* ``../../<legacy-monolith>/docs/db/WILLOW_SCHEMA.md`` — a real document, reached
  by a path that only resolves when the archived monolith checkout sits beside this repo. The
  2026-08-10 move put every repo under its own org folder, so the relative
  hop stopped working while the file it named stayed perfectly readable.
  A dead link caused by layout, not by absence.
* ``CROSS_REPO_BRIDGE.md`` and ``extractor/GROVE_DOCS_EXTRACTOR_SPEC.md`` —
  linked as local siblings, never in this tree, and never in its history.
  ``docs/INDEX.md`` already recorded them under *"Not in this tree (by
  design)"*: they live at the archived ``rudi193-cmd/safe-app-willow-grove``
  because they cover work outside what shipped as 0.9.0.

The second pair is the more interesting failure. The decision was made,
written down, and correct — in ``INDEX.md``. ``ARCHITECTURE.md`` simply
never learned about it and went on linking as though the files were local.
Two documents in the same directory disagreed about what exists, and the
one a newcomer reads first was the wrong one.

This module asserts every relative link in the CAR resolves on disk. It
deliberately does not check absolute URLs: a link to an archived or
private repository is a legitimate historical reference, and reaching out
over the network to prove it would make this test flaky and slow for no
gain. What it prevents is the specific regression above — a *local* link
that promises a file this repository does not have.

Scope is this one document on purpose. Three other docs carry dead
relative links today (``design/autonomous-continuity.md``,
``design/willow-grove-premise.md``, ``runbooks/grove.md``); widening the
audit to them belongs with the change that resolves them, not with a test
that would have to be born failing or born excusing.

Follows the house pattern of ``tests/test_documented_entrypoints_exist.py``:
the audit is paired with a self-check that the parser found anything at
all, because a regex that silently stops matching turns an audit into a
green no-op.

Stdlib only. Reads one file, touches no network.
"""
from __future__ import annotations

import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC_PATH = os.path.join(ROOT, "docs", "ARCHITECTURE.md")
DOC_DIR = os.path.dirname(DOC_PATH)

#: Markdown links whose target is a path rather than a URL or an anchor.
_RELATIVE_LINK_RE = re.compile(r"\[[^\]]*\]\((?!https?:|mailto:|#)([^)]+)\)")


def _relative_targets() -> list[str]:
    with open(DOC_PATH, encoding="utf-8") as fh:
        text = fh.read()
    targets = []
    for raw in _RELATIVE_LINK_RE.findall(text):
        target = raw.split("#", 1)[0].strip()
        if target:
            targets.append(target)
    return targets


class ArchitectureLinksTests(unittest.TestCase):
    def test_doc_exists(self) -> None:
        self.assertTrue(os.path.isfile(DOC_PATH), f"missing {DOC_PATH}")

    def test_the_audit_actually_finds_links(self) -> None:
        """Guard against the pattern silently matching nothing — the failure
        mode that turns this whole file into a green no-op."""
        targets = _relative_targets()
        self.assertGreaterEqual(
            len(targets), 3,
            "found almost no relative links in docs/ARCHITECTURE.md — the "
            "pattern has stopped matching and this file is no longer "
            f"auditing anything (found: {targets})",
        )
        self.assertIn("../schema.sql", targets)

    def test_every_relative_link_resolves(self) -> None:
        missing = sorted(
            {t for t in _relative_targets()
             if not os.path.exists(os.path.join(DOC_DIR, t))}
        )
        self.assertEqual(
            missing, [],
            "docs/ARCHITECTURE.md is the canonical architecture reference; a "
            "relative link that does not resolve sends a reader to nothing "
            f"with no other route to the same material: {missing}",
        )

    def test_absent_by_design_docs_are_not_linked_as_local(self) -> None:
        """The two documents INDEX.md records as out-of-tree must not be
        linked as if they were siblings.

        Naming them and saying where they live is correct. Linking them is
        how ARCHITECTURE.md came to disagree with INDEX.md about what this
        repository contains.
        """
        targets = _relative_targets()
        for absent in ("CROSS_REPO_BRIDGE.md",
                       "extractor/GROVE_DOCS_EXTRACTOR_SPEC.md"):
            with self.subTest(absent=absent):
                self.assertNotIn(
                    absent, targets,
                    f"{absent} is recorded in docs/INDEX.md under 'Not in this "
                    "tree (by design)' and lives at the archived "
                    "rudi193-cmd/safe-app-willow-grove — name it, do not link it",
                )


if __name__ == "__main__":
    unittest.main()
