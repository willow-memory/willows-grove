#!/usr/bin/env python3
# b17: GRPPR · ΔΣ=42
"""scripts/check_persona_provenance.py — persona-provenance CI check (§11).

Enforces INVARIANTS.md §11: every commit on the current branch that
changes tracked code carries a `Persona:` trailer naming a valid fleet
persona. Merge commits are exempt (they carry no work). Commits that
only touch untracked files are exempt by nature.

Base branch:
- CI: `$GITHUB_BASE_REF` (set by GitHub Actions on pull_request events).
- Locally: falls back to `master`, then `main`.

Fleet personas: the closed set below mirrors
`willow-memory/willow/fleet_personas.json`. willow-memory is a sibling
repo not always present in CI; the set is hardcoded and reviewed on any
change to the fleet roster.

Exits 0 when every code-changing non-merge commit carries a valid
trailer; non-zero and lists each drift on failure.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# The closed set of fleet persona keys. Sourced from
# willow-memory/willow/fleet_personas.json — verbatim, lowercase.
# Any commit whose Persona: trailer names a value outside this set is drift.
FLEET_PERSONAS = frozenset({
    "willow",
    "heimdallr",
    "hanuman",
    "opus",
    "ada",
    "steve",
    "kart",
    "shiva",
    "ganesha",
    "skirnir",
    "loki",
    "vishwakarma",
    "jeles",
    "binder",
    "publius",
    "schmidt",
    "nestor",
})

# File extensions §11 considers "tracked code" — a commit that only touches
# files outside this set (worktree scaffolding, generated artifacts) is
# exempt. Matches INVARIANTS.md §11 verbatim.
TRACKED_EXTS = {".py", ".js", ".sh", ".md", ".yml", ".yaml", ".sql", ".json", ".html"}

# Match a `Persona: <name>` trailer line (RFC-5322-ish trailer block).
# Whitespace-tolerant; case-insensitive on the key.
TRAILER_RE = re.compile(r"^\s*Persona\s*:\s*([A-Za-z0-9_-]+)\s*$", re.MULTILINE | re.IGNORECASE)


def _git(*args: str) -> str:
    """Run a git command from REPO_ROOT and return stdout."""
    return subprocess.run(
        ["git", *args],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def _resolve_base() -> str:
    """Pick the base ref for the commit range."""
    if env := os.environ.get("GITHUB_BASE_REF"):
        return f"origin/{env}"
    for candidate in ("master", "main"):
        try:
            _git("rev-parse", "--verify", candidate)
            return candidate
        except subprocess.CalledProcessError:
            continue
    raise SystemExit("check_persona_provenance: no base branch found (master/main)")


def _commit_range(base: str) -> list[str]:
    """Return the list of commit SHAs on HEAD that are not on `base`."""
    out = _git("log", f"{base}..HEAD", "--format=%H")
    return [sha for sha in out.splitlines() if sha]


def _commit_message(sha: str) -> str:
    return _git("log", "-1", "--format=%B", sha)


def _is_merge(sha: str) -> bool:
    """A merge commit has two or more parents."""
    parents = _git("log", "-1", "--format=%P", sha).strip().split()
    return len(parents) >= 2


def _touched_files(sha: str) -> list[str]:
    out = _git("show", "--name-only", "--format=", sha)
    return [line.strip() for line in out.splitlines() if line.strip()]


def _touches_tracked_code(files: list[str]) -> bool:
    for path in files:
        if Path(path).suffix.lower() in TRACKED_EXTS:
            return True
    return False


def _personas_from_message(message: str) -> list[str]:
    return [m.group(1).lower() for m in TRAILER_RE.finditer(message)]


def check_commit(sha: str) -> list[str]:
    """Return a list of drift strings for this commit (empty if clean)."""
    if _is_merge(sha):
        return []
    files = _touched_files(sha)
    if not _touches_tracked_code(files):
        return []
    message = _commit_message(sha)
    personas = _personas_from_message(message)
    if not personas:
        short = _git("log", "-1", "--format=%s", sha).strip()
        return [f"{sha[:12]}: no `Persona:` trailer — '{short}'"]
    drifts: list[str] = []
    for persona in personas:
        if persona not in FLEET_PERSONAS:
            drifts.append(
                f"{sha[:12]}: `Persona: {persona}` names no fleet member — "
                f"expected one of {sorted(FLEET_PERSONAS)}"
            )
    return drifts


def main() -> int:
    try:
        base = _resolve_base()
    except SystemExit as err:
        print(str(err), file=sys.stderr)
        return 1
    commits = _commit_range(base)
    if not commits:
        print(f"persona-provenance: no commits on HEAD past {base}")
        return 0
    all_drifts: list[str] = []
    for sha in commits:
        all_drifts.extend(check_commit(sha))
    if all_drifts:
        print(
            f"persona-provenance: {len(all_drifts)} drift(s) across "
            f"{len(commits)} commit(s) past {base}",
            file=sys.stderr,
        )
        for line in all_drifts:
            print("  " + line, file=sys.stderr)
        return 1
    print(f"persona-provenance: clean ({len(commits)} commit(s) past {base})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
