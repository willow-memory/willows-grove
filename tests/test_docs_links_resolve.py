# b17: WGRV1 ΔΣ=42
"""tests/test_docs_links_resolve.py — every doc link resolves, for everyone.

``tests/test_architecture_links_resolve.py`` pinned the canonical
architecture reference when its three dead links were repaired (PR 21).
That change deliberately did not widen the audit, on the grounds that a
sweep belongs with the change that fixes what it finds — otherwise the
test is born failing or born excusing. This is that change, so this is
that sweep.

Two properties, and the second is the one that was invisible.

**Resolution.** A relative link in a document must point at a file this
repository actually contains. Eight did not: five to a real document in
`rudi193-cmd/safe-app-store` reached by a path that assumed a sibling
checkout, two to `docs/synthesis/*` which ``docs/INDEX.md`` records as
out-of-tree by design, and one to ``docs/generated/`` — extractor output
that nothing in this tree produces.

**No escaping the repository root.** This is the subtle one. Three more
links — ``../../../willow-mcp/...`` from two design docs — *resolved
cleanly* while the audit ran, because a sibling checkout of willow-mcp
happened to exist beside this repo at the time. On a fresh clone, and in
CI, they are dead. A link whose validity depends on what else the reader
has cloned is not a link; it is a coincidence, and a file-existence check
alone will cheerfully bless it.

That is why the escape rule is asserted separately rather than folded
into resolution: resolution asks *is it there*, and the answer varies by
machine. Escape asks *could it ever be reliably there*, and the answer is
a property of the link itself. Only the second is portable, and the first
undercounted the problem by three until the second was written.

Both properties hold with no allowance list, because every link was
fixed rather than excused. Cross-repo references are absolute URLs when
the target is public and reachable (`willow-memory/willow-mcp`,
`rudi193-cmd/safe-app-store`), and named-not-linked when it is not — a
URL into a private archive 404s for nearly every reader, which is the
same dead end wearing a better suit.

Overlaps ``test_architecture_links_resolve.py`` on one file by design:
that module also asserts the CAR names rather than links the two
documents ``INDEX.md`` marks absent-by-design, which is a different
property from "the links it does have resolve".

Stdlib only. Reads files, touches no network — an absolute URL is not
fetched, because a link into an archived repository is legitimate history
and a network check would buy flakiness for nothing.
"""
from __future__ import annotations

import os
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

#: Markdown links whose target is a path rather than a URL or a bare anchor.
_RELATIVE_LINK_RE = re.compile(r"\[[^\]]*\]\((?!https?:|mailto:|#)([^)]+)\)")


def _docs() -> list[pathlib.Path]:
    """Every Markdown document this repository ships."""
    return sorted(ROOT.glob("docs/**/*.md")) + sorted(ROOT.glob("*.md"))


def _relative_links(doc: pathlib.Path) -> list[str]:
    text = doc.read_text(encoding="utf-8", errors="replace")
    out = []
    for raw in _RELATIVE_LINK_RE.findall(text):
        target = raw.split("#", 1)[0].strip()
        if target:
            out.append(target)
    return out


def _rel(path: pathlib.Path) -> str:
    return os.path.relpath(path, ROOT)


class SweepSanityTests(unittest.TestCase):
    """The house self-check: an audit that matches nothing is a green no-op."""

    def test_the_sweep_finds_documents(self) -> None:
        docs = _docs()
        self.assertGreaterEqual(
            len(docs), 20,
            f"found only {len(docs)} markdown docs — the glob has stopped "
            "matching and this file is no longer auditing anything",
        )

    def test_the_sweep_finds_links(self) -> None:
        total = sum(len(_relative_links(d)) for d in _docs())
        self.assertGreaterEqual(
            total, 20,
            f"found only {total} relative links across the docs — the pattern "
            "has stopped matching and this file is no longer auditing anything",
        )


class DocsLinkResolutionTests(unittest.TestCase):
    """Every relative link points at a file this repository contains."""

    def test_every_relative_link_resolves(self) -> None:
        broken = []
        for doc in _docs():
            for target in _relative_links(doc):
                if not (doc.parent / target).exists():
                    broken.append(f"{_rel(doc)} -> {target}")
        self.assertEqual(
            sorted(broken), [],
            "documents link to files this repository does not contain. Point "
            "at an absolute URL when the target is public and reachable; name "
            "it with its location, unlinked, when it is not (a URL into a "
            f"private archive 404s for nearly every reader): {sorted(broken)}",
        )


class DocsLinkEscapeTests(unittest.TestCase):
    """No relative link may leave the repository.

    A link that climbs out of the tree can only work when the reader
    happens to have the right sibling checked out beside this repo. It
    passes a file-existence check on the machine that wrote it and fails
    silently everywhere else — which is exactly how three of these
    survived the first sweep.
    """

    def test_no_relative_link_escapes_the_repo(self) -> None:
        escaping = []
        for doc in _docs():
            for target in _relative_links(doc):
                resolved = (doc.parent / target).resolve()
                if ROOT not in resolved.parents and resolved != ROOT:
                    escaping.append(f"{_rel(doc)} -> {target}")
        self.assertEqual(
            sorted(escaping), [],
            "relative links climb out of the repository. They resolve only "
            "when a sibling checkout happens to sit beside this one, so they "
            "are dead on a fresh clone and in CI while looking healthy to "
            "whoever wrote them. Use an absolute URL for cross-repo "
            f"references: {sorted(escaping)}",
        )


if __name__ == "__main__":
    unittest.main()
