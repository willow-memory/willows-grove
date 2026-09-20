#!/usr/bin/env python3
# b17: GRPPR · ΔΣ=42
"""scripts/check_persona_provenance.py — persona-provenance CI check (§11).

Enforces INVARIANTS.md §11: every commit on the current branch that
changes tracked code carries a `Persona:` trailer naming a valid fleet
persona. Merge commits are exempt (they carry no work). Commits that
only touch untracked files are exempt by nature. release-please's own
release commit — author `willow-ci[bot]`, subject
`chore(<branch>): release X.Y.Z` — is the one further exemption, added
in PR 78 and pinned below by the RELEASE_PLEASE_* constants; both
axes must match, so nothing else in `willow-ci`'s future job set can
ride the exemption in.

Base branch:
- CI: `$GITHUB_BASE_REF` (set by GitHub Actions on pull_request events).
- Locally: falls back to `master`, then `main`.

Fleet personas: read from `governance/fleet_personas.json`, which is the
roster §11 names as the source. That file is in this repo, so CI always
has it. It used to be a frozenset copied into this script instead —
justified by a sibling repo not always being present in CI, which the
in-repo copy already solved — and the two drifted: `schmidt` reached the
roster and never the literal.

Join keys (§11, optional): a commit may also carry `Gap-Id: <12 hex>` —
the backlog gap it lands the fix for — and `Idea-Id: <slug>`. Neither is
required. When present the value must parse, because the willow-bot
steward reads these trailers off merged commits and calls `gap_resolve`
on the cited gap; a malformed id would resolve nothing and say nothing.
Shape only — the checker does not ask the backlog whether the id exists.

Exits 0 when every code-changing non-merge commit carries a valid
trailer; non-zero and lists each drift on failure.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# The roster INVARIANTS.md §11 names as the source: "The trailer's value is a
# key from `governance/fleet_personas.json` (verbatim, lowercase)".
FLEET_ROSTER = REPO_ROOT / "governance" / "fleet_personas.json"


def load_fleet_personas(path: Path = FLEET_ROSTER) -> tuple[frozenset[str], str | None]:
    """Read the closed set of persona keys from the roster.

    This used to be a frozenset copied into this file. Two copies of a list
    drift, and this pair had: `schmidt` was added to the roster and never to
    the literal, so a commit honestly naming a roster member was reported as
    drift. §11 names the JSON as the source, so read the JSON.

    `_meta` is not a persona and is refused — §11 says so outright.

    Returns (personas, unreadable_reason). A checker that cannot read its own
    subject has to fail closed rather than pass everything: Appendix B, *a gate
    that cannot check its subject is not a weaker gate; it is no gate*.
    """
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as err:
        return frozenset(), f"could not read the fleet roster {path}: {err}"
    if not isinstance(raw, dict):
        return frozenset(), f"{path}: expected an object of persona keys"
    names = {key.lower() for key in raw if key != "_meta"}
    if not names:
        return (
            frozenset(),
            f"{path}: no personas found — refusing to validate against an empty roster",
        )
    return frozenset(names), None


# File extensions §11 considers "tracked code" — a commit that only touches
# files outside this set (worktree scaffolding, generated artifacts) is
# exempt. Matches INVARIANTS.md §11 verbatim.
TRACKED_EXTS = {".py", ".js", ".sh", ".md", ".yml", ".yaml", ".sql", ".json", ".html"}

# Match a `Persona: <name>` trailer line (RFC-5322-ish trailer block).
# Whitespace-tolerant; case-insensitive on the key.
TRAILER_RE = re.compile(
    r"^\s*Persona\s*:\s*([A-Za-z0-9_-]+)\s*$", re.MULTILINE | re.IGNORECASE
)

# The release-please release commit is the ONE exemption from §11's
# "every non-merge tracked-code commit carries a Persona: trailer" rule,
# ratified for this repo in PR 78 (INVARIANTS.md §11, bounded exemption).
# The exemption is deliberately bounded on TWO axes at once — author AND
# subject shape — so a commit that matches only one still fails closed:
#   1. Author is the willow-ci GitHub App (login `willow-ci[bot]`, whose
#      commits carry `name = willow-ci[bot]` and an email of the form
#      `<app-id>+willow-ci[bot]@users.noreply.github.com`).
#   2. Subject is release-please's exact pattern `chore(<branch>): release
#      X.Y.Z` (release-please templates the default branch into the scope).
# The narrowness matters. `willow-ci` may run other jobs in the future;
# an author-only exemption would silently bypass §11 for any of them. A
# subject-only exemption would let any author push a commit with the
# release-please subject and pass. Both together name exactly the release
# PR release-please cuts, and nothing else.
RELEASE_PLEASE_AUTHOR_NAME = "willow-ci[bot]"
RELEASE_PLEASE_AUTHOR_EMAIL_RE = re.compile(
    r"^\d+\+willow-ci\[bot\]@users\.noreply\.github\.com$", re.IGNORECASE
)
RELEASE_PLEASE_SUBJECT_RE = re.compile(r"^chore(?:\([^)]+\))?: release \d+\.\d+\.\d+$")

# Join-key trailers. Captured loosely (anything after the colon) so a
# malformed value is reported as drift rather than silently unmatched;
# the shape check is separate.
JOIN_KEY_RE = re.compile(
    r"^\s*(Gap-Id|Idea-Id)\s*:\s*(.*?)\s*$", re.MULTILINE | re.IGNORECASE
)

# A gap `_id` as gap_log mints it: twelve lowercase hex characters
# (e.g. e278ec952b9c). An Idea-Id is the reconciler's derived slug,
# `<corpus>-<docslug>-<localnum|rowhash>`; only the character class is
# pinned here since the reconciler owns the scheme.
JOIN_KEY_SHAPES = {
    "gap-id": re.compile(r"^[0-9a-f]{12}$"),
    "idea-id": re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$"),
}


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


def _author(sha: str) -> tuple[str, str]:
    """Return (name, email) of the commit author."""
    out = _git("log", "-1", "--format=%an%n%ae", sha)
    lines = out.splitlines()
    name = lines[0] if lines else ""
    email = lines[1] if len(lines) > 1 else ""
    return name, email


def _subject(sha: str) -> str:
    return _git("log", "-1", "--format=%s", sha).strip()


def _is_release_please_commit(sha: str) -> bool:
    """The bounded §11 exemption for release-please's own release commit.

    Both conditions must hold — see the RELEASE_PLEASE_* constants above.
    """
    name, email = _author(sha)
    author_ok = name == RELEASE_PLEASE_AUTHOR_NAME or bool(
        RELEASE_PLEASE_AUTHOR_EMAIL_RE.match(email)
    )
    subject_ok = bool(RELEASE_PLEASE_SUBJECT_RE.match(_subject(sha)))
    return author_ok and subject_ok


def _touches_tracked_code(files: list[str]) -> bool:
    for path in files:
        if Path(path).suffix.lower() in TRACKED_EXTS:
            return True
    return False


def _personas_from_message(message: str) -> list[str]:
    return [m.group(1).lower() for m in TRAILER_RE.finditer(message)]


def _join_keys_from_message(message: str) -> list[tuple[str, str]]:
    """Every `Gap-Id:` / `Idea-Id:` trailer as (key-lowercased, raw value)."""
    return [(m.group(1).lower(), m.group(2)) for m in JOIN_KEY_RE.finditer(message)]


def check_join_keys(sha: str, message: str) -> list[str]:
    """Drift strings for malformed join-key trailers; empty when absent or clean.

    Absence is not drift — the trailer is optional. Presence with a value
    that does not parse is, because the steward resolves gaps by this id and
    a bad id would resolve nothing silently.
    """
    drifts: list[str] = []
    for key, value in _join_keys_from_message(message):
        shape = JOIN_KEY_SHAPES[key]
        if not shape.match(value):
            label = "Gap-Id" if key == "gap-id" else "Idea-Id"
            expected = (
                "twelve lowercase hex characters (a gap `_id`)"
                if key == "gap-id"
                else "a slug of [A-Za-z0-9._-]"
            )
            drifts.append(
                f"{sha[:12]}: `{label}: {value or '<empty>'}` does not parse — "
                f"expected {expected}"
            )
    return drifts


def check_commit(sha: str, personas_allowed: frozenset[str]) -> list[str]:
    """Return a list of drift strings for this commit (empty if clean)."""
    if _is_merge(sha):
        return []
    files = _touched_files(sha)
    if not _touches_tracked_code(files):
        return []
    if _is_release_please_commit(sha):
        return []
    message = _commit_message(sha)
    personas = _personas_from_message(message)
    if not personas:
        short = _git("log", "-1", "--format=%s", sha).strip()
        return [f"{sha[:12]}: no `Persona:` trailer — '{short}'"]
    drifts: list[str] = []
    for persona in personas:
        if persona not in personas_allowed:
            drifts.append(
                f"{sha[:12]}: `Persona: {persona}` names no fleet member — "
                f"expected one of {sorted(personas_allowed)}"
            )
    drifts.extend(check_join_keys(sha, message))
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
    personas_allowed, roster_problem = load_fleet_personas()
    if roster_problem:
        # Fail closed. Validating every trailer against an empty set would pass
        # nothing; validating against no set at all would pass everything, and
        # the second is the dangerous one.
        print(f"persona-provenance: {roster_problem}", file=sys.stderr)
        return 1
    all_drifts: list[str] = []
    for sha in commits:
        all_drifts.extend(check_commit(sha, personas_allowed))
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
