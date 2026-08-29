"""tests/test_documented_entrypoints_exist.py — docs promise, disk delivers.

docs/grove-served-page.md is the operator guide. It names concrete files
under `scripts/` and `deploy/` — the launchers and unit templates an
operator is told to run or install. The v0.9 clean-build port left four
of them behind in the old repo while the doc kept promising them (see
the incident this test is written against: `grove-serve-run`,
`grove-watcher-run`, `grove-serve.service.template`,
`grove-watcher.service.template` were all documented and all absent).

Nothing on-tree stopped that drift. This test greps the doc for every
`scripts/*` and `deploy/*` reference and asserts each path exists on
disk — and, for `scripts/*` entries, that the file is executable. It
follows the house pattern of `tests/test_state_vocabulary_audit.py`:
a self-check guards against the regex silently finding nothing, which
would turn this file into a green no-op instead of a real audit.
"""
from __future__ import annotations

import os
import re
import stat
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC_PATH = os.path.join(ROOT, "docs", "grove-served-page.md")

# Matches `scripts/<name>` or `deploy/<name>` tokens embedded in prose,
# code fences, or markdown links — e.g. "./scripts/grove-serve-run",
# "`deploy/grove-serve.service.template`",
# "[`scripts/grove-serve-run`](../scripts/grove-serve-run)".
# Path segment: no whitespace, backticks, parens, or markdown/punctuation
# that would terminate the reference.
_REF_RE = re.compile(r"\b(scripts|deploy)/([A-Za-z0-9_.-]+)")


def _referenced_paths() -> set[str]:
    with open(DOC_PATH, encoding="utf-8") as fh:
        text = fh.read()
    return {f"{d}/{name}" for d, name in _REF_RE.findall(text)}


class DocumentedEntrypointsExistTests(unittest.TestCase):
    def test_doc_exists(self) -> None:
        self.assertTrue(os.path.isfile(DOC_PATH), f"missing {DOC_PATH}")

    def test_the_audit_actually_finds_references(self) -> None:
        """Guard against the regex silently matching nothing — the failure
        mode that turns this whole file into a green no-op."""
        refs = _referenced_paths()
        self.assertTrue(refs, "found no scripts/* or deploy/* references in "
                         f"{DOC_PATH} — the pattern has stopped matching")
        self.assertIn("scripts/grove-serve-run", refs)
        self.assertIn("deploy/grove-serve.service.template", refs)
        self.assertIn("scripts/grove-watcher-run", refs)
        self.assertIn("deploy/grove-watcher.service.template", refs)

    def test_every_documented_path_exists(self) -> None:
        missing = sorted(
            rel for rel in _referenced_paths()
            if not os.path.exists(os.path.join(ROOT, rel))
        )
        self.assertEqual(
            missing,
            [],
            f"{DOC_PATH} references paths that do not exist on disk: "
            f"{missing}. The doc is the spec — either ship the file or "
            "correct the doc.",
        )

    def test_documented_scripts_are_executable(self) -> None:
        not_executable = []
        for rel in sorted(_referenced_paths()):
            if not rel.startswith("scripts/"):
                continue
            full = os.path.join(ROOT, rel)
            if not os.path.isfile(full):
                continue  # caught by test_every_documented_path_exists
            mode = os.stat(full).st_mode
            if not (mode & stat.S_IXUSR):
                not_executable.append(rel)
        self.assertEqual(
            not_executable,
            [],
            f"documented scripts are not executable (chmod +x): {not_executable}",
        )


if __name__ == "__main__":
    unittest.main()
