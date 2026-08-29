#!/usr/bin/env python3
"""scripts/check_changelog_bullet.py — changelog-bullet CI check (INVARIANTS.md §3).

Enforces the clause of §3 that `check_docs_drift.py` does not: "Every
code-changing PR appends a bullet to `CHANGELOG.md`'s `[Unreleased]`
section under `### Changed`, `### Added`, `### Fixed`, or `### Removed`."
`check_docs_drift.py`'s `check_changelog_pr_citations` only validates
bullets that already exist (that each cites its PR) — it never checks
that a code-changing PR *added* one. PR #8 (merged, 22 files, 1151
insertions) is the proof: it landed no bullet and CI stayed green.

This is a standalone script rather than an extension of
`check_docs_drift.py` because the two checks differ in shape: docs-drift
walks the whole tree's current text for citation/witness drift and does
not touch git history at all, while this check must walk a *commit
range* (base branch -> HEAD) the way `check_persona_provenance.py`
already does for §11. Reusing that shape (base-ref resolution, git
plumbing helpers, a tracked-extension set) is more honest than bolting
git-range logic onto a checker that otherwise never shells out to git.

Algorithm, mirroring `check_persona_provenance.py`'s vocabulary:

1. Resolve the base ref exactly as `check_persona_provenance.py` does:
   `origin/$GITHUB_BASE_REF` in CI, else a local `master`/`main`
   fallback. No base found -> degrade cleanly (exit 0), same as that
   checker would on a bare push-to-master run with no PR context.
2. Diff `base...HEAD` (`git diff --name-only`) to get the changed-file
   set for the whole range in one shot — this check cares about the PR
   as a unit, not commit-by-commit provenance, so there is no need to
   walk individual commits.
3. A file counts as "tracked code" using the same `TRACKED_EXTS` set as
   §11's checker, MINUS `CHANGELOG.md` itself and MINUS `.md` files in
   general — §3's clause is about code-changing PRs needing a changelog
   entry, not doc-changing ones, so treating `.md` edits as "code" would
   make every docs PR need to cite itself, which is exactly the
   false-positive §3 warns against implicitly via Keep a Changelog's
   convention (changelogs describe user/behavior-visible change, not
   prose). Concretely: `TRACKED_EXTS - {".md"}` = `.py .js .sh .yml
   .yaml .sql .json .html`.
4. If no tracked-code file changed in the range, exit 0 — a docs-only
   PR is not required to add a bullet (false-positive case 1).
5. If the only changed file is `CHANGELOG.md` itself, exit 0 — a PR
   that only edits the changelog must not be required to cite itself
   (false-positive case 2; also covered by step 3 since `.md` is
   excluded from "tracked code", but called out explicitly here since
   it's a named requirement).
6. Otherwise, require that `CHANGELOG.md` changed in the range AND that
   the diff added at least one new bullet line (`+- `) under the
   `[Unreleased]` section, under one of `### Changed` / `### Added` /
   `### Fixed` / `### Removed`. A `CHANGELOG.md` edit that only touches
   other sections (e.g. freezing a release) does not satisfy this.

False-positive case 3 (no base to diff against) is handled by step 1:
`_resolve_base` returns `None` instead of raising when it cannot find
`origin/$GITHUB_BASE_REF` nor a local `master`/`main`, and `main()`
treats that as "nothing to check" rather than an error — this mirrors
how a push-to-master CI run has no PR range to enforce §3 against.

Exits 0 when clean or degraded; non-zero and prints the drift — naming
the offending code file(s), not just "missing bullet" — when not.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHANGELOG_NAME = "CHANGELOG.md"

# Same set `check_persona_provenance.py` uses for "tracked code" under §11,
# minus Markdown — a docs-only (.md) change is not "code" for §3's purposes,
# and CHANGELOG.md itself living in this set would make every changelog-only
# PR falsely required to cite itself.
TRACKED_CODE_EXTS = {".py", ".js", ".sh", ".yml", ".yaml", ".sql", ".json", ".html"}

UNRELEASED_HEADING_RE = re.compile(r"^##\s*\[Unreleased\]\s*$", re.MULTILINE)
NEXT_RELEASE_HEADING_RE = re.compile(r"^##\s*\[", re.MULTILINE)
SUBSECTION_RE = re.compile(r"^###\s*(Changed|Added|Fixed|Removed)\s*$", re.MULTILINE)


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def _resolve_base() -> str | None:
    """Pick the base ref for the diff range, or None if there is none.

    Mirrors `check_persona_provenance.py`'s `_resolve_base`, but returns
    None instead of raising — a push-to-master run with no PR context
    has nothing to diff against, and that is not a violation of §3.
    """
    if env := os.environ.get("GITHUB_BASE_REF"):
        ref = f"origin/{env}"
        try:
            _git("rev-parse", "--verify", ref)
            return ref
        except subprocess.CalledProcessError:
            return None
    for candidate in ("master", "main"):
        try:
            _git("rev-parse", "--verify", candidate)
            return candidate
        except subprocess.CalledProcessError:
            continue
    return None


def _merge_base(base: str) -> str:
    """The commit where HEAD diverged from `base` — the true diff floor."""
    return _git("merge-base", base, "HEAD").strip()


def _changed_files(merge_base: str) -> list[str]:
    """Files changed on HEAD relative to where it diverged from base."""
    out = _git("diff", "--name-only", f"{merge_base}..HEAD")
    return [line.strip() for line in out.splitlines() if line.strip()]


def _is_tracked_code(path: str) -> bool:
    return Path(path).suffix.lower() in TRACKED_CODE_EXTS


RELEASE_VERSION_HEADING_RE = re.compile(r"^##\s*\[\d+\.\d+\.\d+\]", re.MULTILINE)


def _unreleased_block(text: str) -> str | None:
    """Return the `[Unreleased]` section body, or None if absent."""
    m = UNRELEASED_HEADING_RE.search(text)
    if not m:
        return None
    rest = text[m.end():]
    nxt = NEXT_RELEASE_HEADING_RE.search(rest)
    return rest[: nxt.start()] if nxt else rest


def _newest_release_block(text: str) -> str | None:
    """Return the body of the newest `## [X.Y.Z]` section, or None.

    A release-cut commit moves everything out of `[Unreleased]` into a
    fresh release section and leaves `[Unreleased]` empty. Any code it
    carries — including the release tooling itself — is documented in
    that new section, which is correct: the change ships in that
    release, not the next one. Reading only `[Unreleased]` would fail
    such a commit for documenting itself in the right place. This check
    was written by a release that then tripped over exactly that.
    """
    m = RELEASE_VERSION_HEADING_RE.search(text)
    if not m:
        return None
    rest = text[m.end():]
    nxt = NEXT_RELEASE_HEADING_RE.search(rest)
    return rest[: nxt.start()] if nxt else rest


def _named_subsection_bullets(text: str) -> set[str]:
    """Bullets under `[Unreleased]` OR the newest released section,
    restricted to the four named Keep-a-Changelog subsections
    (`### Changed/Added/Fixed/Removed`).

    The newest release section counts so that a release-cut commit — one
    that empties `[Unreleased]` into a fresh `## [X.Y.Z]` — can document
    its own changes in the release they actually ship in.

    A bullet parked under some other heading (e.g. a grandfathered
    `### Previous work` section) does not count — §3 names the four
    subsections explicitly.
    """
    blocks = [_unreleased_block(text), _newest_release_block(text)]
    lines: list[str] = []
    for block in blocks:
        if block is not None:
            lines.extend(block.splitlines())
    if not lines:
        return set()
    bullets: set[str] = set()
    in_named_subsection = False
    for line in lines:
        stripped = line.strip()
        if SUBSECTION_RE.match(line) or (
            stripped.startswith("### ") and stripped[4:].strip() in {"Changed", "Added", "Fixed", "Removed"}
        ):
            in_named_subsection = True
            continue
        if stripped.startswith("### "):
            in_named_subsection = False
            continue
        if in_named_subsection and stripped.startswith("- "):
            bullets.add(stripped)
    return bullets


def _added_bullet_lines(merge_base: str) -> list[str]:
    """Bullets present in HEAD's CHANGELOG.md `[Unreleased]` (under a named
    subsection) that were not present at the merge-base — i.e. what this
    range added. Compares full-file snapshots at both revisions rather
    than parsing the unified diff, since a 0-context diff hunk carries no
    heading to anchor "which section is this bullet under".
    """
    try:
        head_text = _git("show", f"HEAD:{CHANGELOG_NAME}")
    except subprocess.CalledProcessError:
        return []
    try:
        base_text = _git("show", f"{merge_base}:{CHANGELOG_NAME}")
    except subprocess.CalledProcessError:
        base_text = ""

    head_bullets = _named_subsection_bullets(head_text)
    base_bullets = _named_subsection_bullets(base_text)
    return sorted(head_bullets - base_bullets)


def main() -> int:
    base = _resolve_base()
    if base is None:
        print("changelog-bullet: no base branch found — nothing to check")
        return 0

    merge_base = _merge_base(base)
    changed = _changed_files(merge_base)
    if not changed:
        print(f"changelog-bullet: no commits on HEAD past {base}")
        return 0

    code_files = sorted(f for f in changed if _is_tracked_code(f))
    if not code_files:
        print("changelog-bullet: no tracked-code files changed — docs-only, exempt")
        return 0

    bullets = _added_bullet_lines(merge_base)
    if bullets:
        print(
            f"changelog-bullet: clean ({len(bullets)} [Unreleased] bullet(s) "
            f"added for {len(code_files)} code file(s) changed)"
        )
        return 0

    print(
        "changelog-bullet: 1 drift(s) found — code-changing PR added no "
        "CHANGELOG.md [Unreleased] bullet (INVARIANTS.md §3)",
        file=sys.stderr,
    )
    for f in code_files:
        print(f"  {f}: tracked-code change with no matching CHANGELOG.md bullet", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
