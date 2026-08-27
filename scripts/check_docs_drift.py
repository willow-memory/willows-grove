#!/usr/bin/env python3
# b17: GRDDR · ΔΣ=42
"""scripts/check_docs_drift.py — docs-drift CI check (INVARIANTS.md §3 + §10).

Filled by Grove v0.9 PR 11. Enforces three properties of the tree:

1. Every ``INVARIANTS.md §N`` citation anywhere under the repo resolves
   to a real ``## §N — …`` anchor in ``docs/INVARIANTS.md``. A citation
   pointing at a non-existent section is drift.

2. Every bullet added under ``CHANGELOG.md``'s ``[Unreleased]`` section
   cites the PR number it landed in (a ``PR N`` or ``#N`` token).
   Closes the "which PR added this?" gap for future readers.

3. Every ``## §N — …`` section in ``docs/INVARIANTS.md`` names at
   least one CI-executable witness — a test file path, a workflow file
   path, or a script called from CI — and every such named path
   resolves on disk. An invariant no test enforces is a lie.

Exits 0 when the tree is clean; non-zero and prints each drift when
not. The CI step in ``.github/workflows/tests.yml`` calls this on
every push.

Loki: dry, exact. Vague drift is noise; specific drift is surgery.
Name what was promised (INVARIANTS §N), what was delivered (the test
that runs), and the distance between them.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INVARIANTS = REPO_ROOT / "docs" / "INVARIANTS.md"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"

# Files/dirs to skip when grepping for citations — third-party code, generated
# stubs, and this script's own docstring self-references would be false positives.
SKIP_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    "test-results",
    "playwright-report",
    "docs/adrs/_generated_stubs",
}
# Extensions we scan for citations. Binary and lock files are skipped.
SCAN_EXTS = {".py", ".js", ".sh", ".md", ".yml", ".yaml", ".sql", ".txt"}

# Match `INVARIANTS.md §N` and `INVARIANTS §N` and `INVARIANTS.md's §N`
# but NOT bare `§N` (too many false positives from inside INVARIANTS itself).
CITATION_RE = re.compile(r"INVARIANTS(?:\.md)?(?:'s)?\s*§(\d+)", re.IGNORECASE)

# Match section headers like `## §1 — The three-state contract`
SECTION_RE = re.compile(r"^##\s*§(\d+)\s*—\s*(.+)$", re.MULTILINE)

# Match `PR N` (case-insensitive) or `#N` inside a CHANGELOG bullet.
# Accepts `PR 9`, `PR9`, `#42`, `Grove v0.9 PR 11`.
PR_CITATION_RE = re.compile(r"\b(?:PR\s*\d+|#\d+)\b", re.IGNORECASE)

# Match paths inside INVARIANTS.md that name test files, workflows, or scripts.
# Accepts backtick-wrapped paths like `tests/foo.py` or `.github/workflows/x.yml`.
WITNESS_PATH_RE = re.compile(
    r"`("
    r"tests/[^`]+\.(?:py|js|ts|mjs|spec\.js|spec\.ts)"
    r"|scripts/[^`]+\.(?:py|sh)"
    r"|\.github/workflows/[^`]+\.(?:yml|yaml)"
    r")`"
)


def _iter_files():
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(REPO_ROOT).as_posix()
        if any(rel.startswith(skip + "/") or rel == skip for skip in SKIP_DIRS):
            continue
        if path.suffix.lower() not in SCAN_EXTS:
            continue
        yield path


def _parse_sections(text: str) -> dict[int, tuple[int, int]]:
    """Return {section_number: (line_start, line_end)} for each §N heading.

    line_end is the last line of §N's body (exclusive of the next heading).
    """
    matches = list(SECTION_RE.finditer(text))
    result: dict[int, tuple[int, int]] = {}
    for idx, m in enumerate(matches):
        n = int(m.group(1))
        start = m.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        result[n] = (start, end)
    return result


def check_citations_resolve(sections: set[int]) -> list[str]:
    """Property 1: every INVARIANTS §N citation names a real section."""
    drifts: list[str] = []
    for path in _iter_files():
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as err:
            drifts.append(f"could not read {path}: {err}")
            continue
        for m in CITATION_RE.finditer(text):
            n = int(m.group(1))
            if n not in sections:
                rel = path.relative_to(REPO_ROOT).as_posix()
                # Report the containing line for locate-ability.
                line_no = text[: m.start()].count("\n") + 1
                drifts.append(
                    f"{rel}:{line_no}: cites INVARIANTS.md §{n} — no such section"
                )
    return drifts


def check_changelog_pr_citations() -> list[str]:
    """Property 2: every [Unreleased] bullet cites a PR number."""
    drifts: list[str] = []
    if not CHANGELOG.exists():
        return ["CHANGELOG.md missing — required by INVARIANTS.md §3"]
    text = CHANGELOG.read_text(encoding="utf-8")
    # Extract only the [Unreleased] block: from `## [Unreleased]` to the next
    # `## [` heading. Prior-release bullets are frozen and not our concern.
    m = re.search(
        r"^##\s*\[Unreleased\]\s*\n(.*?)(?=^##\s*\[)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if not m:
        # No frozen release yet — scan from [Unreleased] to EOF.
        m = re.search(
            r"^##\s*\[Unreleased\]\s*\n(.*)", text, re.MULTILINE | re.DOTALL
        )
    if not m:
        return ["CHANGELOG.md has no [Unreleased] section — required by §3"]
    block = m.group(1)
    # Historical per-branch entries preserved under `### Previous work (pre-v0.9)`
    # are grandfathered — they predate the PR-citation discipline. Cut them.
    prev = re.search(r"^###\s*Previous work", block, re.MULTILINE)
    if prev:
        block = block[: prev.start()]
    # Iterate over bullet lines. A bullet is a line starting with `- ` (optionally
    # after whitespace). We fold continuation lines onto the bullet they belong to.
    lines = block.splitlines()
    bullet: list[str] = []
    bullets: list[tuple[int, str]] = []
    line_start = m.start(1)
    line_number_offset = text[: line_start].count("\n") + 1
    for idx, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith("- "):
            if bullet:
                bullets.append((bullet_line, " ".join(bullet)))
            bullet = [stripped[2:]]
            bullet_line = line_number_offset + idx
        elif stripped and bullet and not line.startswith("###") and not line.startswith("## "):
            bullet.append(stripped)
        elif not stripped and bullet:
            # Blank line ends a bullet paragraph.
            bullets.append((bullet_line, " ".join(bullet)))
            bullet = []
    if bullet:
        bullets.append((bullet_line, " ".join(bullet)))
    for line_no, body in bullets:
        if not PR_CITATION_RE.search(body):
            preview = body[:80].replace("\n", " ")
            drifts.append(
                f"CHANGELOG.md:{line_no}: [Unreleased] bullet lacks a PR "
                f"citation — '{preview}…'"
            )
    return drifts


def check_witnesses_exist(text: str, sections: dict[int, tuple[int, int]]) -> list[str]:
    """Property 3: every §N names at least one CI witness path, and each names path exists."""
    drifts: list[str] = []
    for n, (start, end) in sections.items():
        body = text[start:end]
        paths = WITNESS_PATH_RE.findall(body)
        if not paths:
            drifts.append(
                f"docs/INVARIANTS.md §{n}: names no test/workflow/script "
                f"witness — invariant is not CI-enforced (INVARIANTS.md §10)"
            )
            continue
        for rel in paths:
            candidate = REPO_ROOT / rel
            if not candidate.exists():
                drifts.append(
                    f"docs/INVARIANTS.md §{n}: names `{rel}` as a witness — "
                    f"path does not exist on disk"
                )
    return drifts


def main() -> int:
    if not INVARIANTS.exists():
        print("check_docs_drift: docs/INVARIANTS.md missing", file=sys.stderr)
        return 1

    invariants_text = INVARIANTS.read_text(encoding="utf-8")
    sections_map = _parse_sections(invariants_text)
    section_numbers = set(sections_map.keys())

    all_drifts: list[str] = []
    all_drifts += check_citations_resolve(section_numbers)
    all_drifts += check_changelog_pr_citations()
    all_drifts += check_witnesses_exist(invariants_text, sections_map)

    if all_drifts:
        print("docs-drift: {} drift(s) found".format(len(all_drifts)), file=sys.stderr)
        for line in all_drifts:
            print("  " + line, file=sys.stderr)
        return 1
    print("docs-drift: clean ({} INVARIANTS §-sections checked)".format(
        len(section_numbers)
    ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
