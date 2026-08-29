"""tests/test_version_changelog_sync.py — the fallback version tells the truth.

`pyproject.toml`'s `[tool.hatch.version]` derives the real version from
the git tag, and carries a `fallback-version` for the cases where no tag
is reachable: a fresh shallow clone, a release-tarball build, a CI
checkout without `fetch-tags`. Its own comment says "Keep in sync with
CHANGELOG.md's latest released version."

Nothing enforced that. A release that bumps the changelog and forgets
the fallback ships a wheel claiming the *previous* version to anyone
building without tags — and the failure is silent, because a wrong
version number builds and installs perfectly well.

Same class as INVARIANTS.md §3's changelog clause, which was also
written-but-unenforced until `scripts/check_changelog_bullet.py`. A
documented rule with no witness is a rule the tree does not actually
hold.

This test reads both files and asserts they agree.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = REPO_ROOT / "pyproject.toml"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"

# `fallback-version = "0.10.0"` — the literal, not the derived version.
_FALLBACK_RE = re.compile(r'^\s*fallback-version\s*=\s*"([^"]+)"', re.MULTILINE)
# `## [0.10.0] — 2026-08-29` — a released section. `[Unreleased]` is
# deliberately not matched: it is not a released version.
_RELEASED_RE = re.compile(r"^##\s*\[(\d+\.\d+\.\d+)\]", re.MULTILINE)


def _fallback_version() -> str | None:
    m = _FALLBACK_RE.search(PYPROJECT.read_text(encoding="utf-8"))
    return m.group(1) if m else None


def _released_versions() -> list[str]:
    return _RELEASED_RE.findall(CHANGELOG.read_text(encoding="utf-8"))


class VersionChangelogSyncTests(unittest.TestCase):
    def test_the_patterns_still_match(self) -> None:
        """Guard against a regex that silently stops matching — the failure
        mode that turns this file into a green no-op."""
        self.assertIsNotNone(
            _fallback_version(),
            f"no fallback-version found in {PYPROJECT} — the pattern has "
            "stopped matching, and this whole file is now vacuous",
        )
        self.assertTrue(
            _released_versions(),
            f"no released `## [X.Y.Z]` section found in {CHANGELOG}",
        )

    def test_fallback_matches_latest_released_changelog_version(self) -> None:
        fallback = _fallback_version()
        latest = _released_versions()[0]
        self.assertEqual(
            fallback,
            latest,
            f"pyproject.toml fallback-version is {fallback!r} but CHANGELOG.md's "
            f"latest released section is {latest!r}. A tagless build would "
            "claim the wrong version, silently. Bump the fallback in the same "
            "commit that cuts the release section.",
        )

    def test_unreleased_section_is_not_read_as_a_release(self) -> None:
        """`[Unreleased]` must never satisfy the check — otherwise the sync
        would 'pass' on a tree whose latest real release is anything at all."""
        self.assertNotIn("Unreleased", _released_versions())


if __name__ == "__main__":
    unittest.main()
