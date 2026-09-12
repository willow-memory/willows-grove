# b17: WGRV1 ΔΣ=42
"""tests/test_ci_workflows_declare_permissions.py — every workflow limits its token.

CodeQL on PR #60 ("Workflow does not contain permissions"): the new
`.github/workflows/trailers.yml` declared no `permissions:` block, so its
`GITHUB_TOKEN` got the repository's default scope. It had been ported
verbatim from willow-reconciler's workflow, which has the same gap, and
`tests.yml` here had it too — only `release.yml` declared least privilege.
An omission inherited by copying is a class, not an instance, so this file
holds every workflow under `.github/workflows/` to a top-level
`permissions:` block. Job-level blocks that widen a scope beside it (the
way `release.yml`'s publish job takes `id-token: write`) are the correct
shape and are not what this checks.

Line-level parse, no PyYAML dependency, in the house style of the other
`tests/test_ci_*` workflow pins. A top-level key is a line that starts at
column 0 with `permissions:`; an indented one is a job's or a step's.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"

_TOP_LEVEL_PERMISSIONS_RE = re.compile(r"^permissions:\s*(\S.*)?$", re.MULTILINE)


def _declares_top_level_permissions(text: str) -> bool:
    """True if `text` carries a `permissions:` key at column 0 — a block
    (`permissions:` followed by indented scopes) or an inline value
    (`permissions: read-all`)."""
    return _TOP_LEVEL_PERMISSIONS_RE.search(text) is not None


def _workflows_without_permissions(workflows_dir: Path) -> list[str]:
    return sorted(
        path.name
        for path in list(workflows_dir.glob("*.yml"))
        + list(workflows_dir.glob("*.yaml"))
        if not _declares_top_level_permissions(path.read_text(encoding="utf-8"))
    )


def test_the_sweep_finds_workflows() -> None:
    """The house self-check: a sweep that finds nothing is a green no-op."""
    found = list(WORKFLOWS.glob("*.yml")) + list(WORKFLOWS.glob("*.yaml"))
    assert len(found) >= 3, (
        f"expected at least three workflows under {WORKFLOWS}, found {found}"
    )


def test_every_workflow_declares_a_top_level_permissions_block() -> None:
    missing = _workflows_without_permissions(WORKFLOWS)
    assert missing == [], (
        "these workflows declare no top-level `permissions:` block, so their "
        "GITHUB_TOKEN gets the repository default rather than least privilege "
        f"(`contents: read` is the floor; widen per job where a job needs it): {missing}"
    )


def test_the_permissions_scan_fires_on_a_planted_workflow_without_one(tmp_path) -> None:
    """Planted: the trailers.yml as CodeQL found it — no `permissions:`
    anywhere — beside one with a job-level block only (not a top-level
    declaration, so still reported), one with a top-level block, and one
    with the inline `read-all` form. The scan must name exactly the first
    two."""
    (tmp_path / "bare.yml").write_text(
        "name: Bare\non:\n  push:\n    branches: [master]\njobs:\n  x:\n    runs-on: ubuntu-latest\n",
        encoding="utf-8",
    )
    (tmp_path / "job-only.yml").write_text(
        "name: JobOnly\non: [push]\njobs:\n  x:\n    permissions:\n      contents: read\n"
        "    runs-on: ubuntu-latest\n",
        encoding="utf-8",
    )
    (tmp_path / "block.yml").write_text(
        "name: Block\non: [push]\npermissions:\n  contents: read\njobs:\n  x:\n    runs-on: ubuntu-latest\n",
        encoding="utf-8",
    )
    (tmp_path / "inline.yaml").write_text(
        "name: Inline\non: [push]\npermissions: read-all\njobs:\n  x:\n    runs-on: ubuntu-latest\n",
        encoding="utf-8",
    )
    assert _workflows_without_permissions(tmp_path) == ["bare.yml", "job-only.yml"]
