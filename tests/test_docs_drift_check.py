# b17: GRDDT · ΔΣ=42
"""Pins `scripts/check_docs_drift.py` (Grove v0.9 PR 11).

INVARIANTS.md §3 (doc discipline) and §10 (CI proves the invariants).

A drift checker with no failing-case test is a lie — it might exit 0
because the tree is clean, or because the check never runs. Every
property the checker enforces is exercised here through a synthetic
tree that fails, verifying the checker (a) fails loudly and (b) names
the specific drift.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "check_docs_drift.py"


def _run_against(tree: Path) -> subprocess.CompletedProcess:
    """Run the drift checker with REPO_ROOT swapped for `tree`.

    The script hardcodes REPO_ROOT relative to its own file location, so
    we invoke it as a subprocess with an on-the-fly copy of the script
    that reroots to the synthetic tree.
    """
    body = SCRIPT.read_text(encoding="utf-8").replace(
        "REPO_ROOT = Path(__file__).resolve().parent.parent",
        f"REPO_ROOT = Path({str(tree)!r})",
    )
    # Write the rerooted script OUTSIDE the tree it scans, or its own
    # docstring citations (INVARIANTS.md §3, §10) become dangling
    # references in a tree that only has §1.
    rerooted = tree.parent / f"_check_{tree.name}.py"
    rerooted.write_text(body, encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(rerooted)],
        capture_output=True,
        text=True,
        check=False,
    )


def _seed_clean_tree(tree: Path) -> None:
    """Seed a minimal tree that the drift checker considers clean."""
    (tree / "docs").mkdir(parents=True, exist_ok=True)
    (tree / "scripts").mkdir(parents=True, exist_ok=True)
    (tree / "tests").mkdir(parents=True, exist_ok=True)
    (tree / "docs" / "INVARIANTS.md").write_text(
        "# Grove invariants\n"
        "\n"
        "## §1 — Only invariant\n"
        "\n"
        "Body. Witness: `tests/test_ok.py`.\n"
        "\n",
        encoding="utf-8",
    )
    (tree / "CHANGELOG.md").write_text(
        "# Changelog\n"
        "\n"
        "## [Unreleased]\n"
        "\n"
        "### Added\n"
        "- Ok bullet (PR 42).\n"
        "\n",
        encoding="utf-8",
    )
    (tree / "tests" / "test_ok.py").write_text("# ok\n", encoding="utf-8")


def test_clean_tree_exits_zero(tmp_path: Path) -> None:
    _seed_clean_tree(tmp_path)
    result = _run_against(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "clean" in result.stdout


def test_dangling_citation_flagged(tmp_path: Path) -> None:
    """Property 1: cite a §N with no such section → drift."""
    _seed_clean_tree(tmp_path)
    # Build the dangling citation via concatenation so this very file
    # does not trigger the real-tree check on §99.
    dangling = "# See INVARIANTS.md " + chr(0xA7) + "99 — never existed\n"
    (tmp_path / "grove_noise.py").write_text(dangling, encoding="utf-8")
    result = _run_against(tmp_path)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "99" in result.stderr
    assert "grove_noise.py" in result.stderr


def test_changelog_bullet_without_pr_flagged(tmp_path: Path) -> None:
    """Property 2: [Unreleased] bullet with no PR/#N citation → drift."""
    _seed_clean_tree(tmp_path)
    (tmp_path / "CHANGELOG.md").write_text(
        "# Changelog\n"
        "\n"
        "## [Unreleased]\n"
        "\n"
        "### Added\n"
        "- A bullet with no citation.\n"
        "\n",
        encoding="utf-8",
    )
    result = _run_against(tmp_path)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "lacks a PR citation" in result.stderr


def test_section_without_witness_flagged(tmp_path: Path) -> None:
    """Property 3: §N with no named witness → drift."""
    _seed_clean_tree(tmp_path)
    (tmp_path / "docs" / "INVARIANTS.md").write_text(
        "# Grove invariants\n"
        "\n"
        "## §1 — Only invariant\n"
        "\n"
        "Body with no witness path.\n"
        "\n",
        encoding="utf-8",
    )
    result = _run_against(tmp_path)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "names no test/workflow/script witness" in result.stderr


def test_witness_path_missing_flagged(tmp_path: Path) -> None:
    """Property 3b: §N names a path that does not exist → drift."""
    _seed_clean_tree(tmp_path)
    (tmp_path / "docs" / "INVARIANTS.md").write_text(
        "# Grove invariants\n"
        "\n"
        "## §1 — Only invariant\n"
        "\n"
        "Body. Witness: `tests/test_does_not_exist.py`.\n"
        "\n",
        encoding="utf-8",
    )
    result = _run_against(tmp_path)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "does not exist on disk" in result.stderr


def test_previous_work_section_grandfathered(tmp_path: Path) -> None:
    """Historical `### Previous work` bullets predate the citation rule."""
    _seed_clean_tree(tmp_path)
    (tmp_path / "CHANGELOG.md").write_text(
        "# Changelog\n"
        "\n"
        "## [Unreleased]\n"
        "\n"
        "### Added\n"
        "- Recent bullet (PR 42).\n"
        "\n"
        "### Previous work (pre-v0.9)\n"
        "\n"
        "- Historical bullet with no PR citation.\n"
        "- Another historical bullet also uncited.\n"
        "\n",
        encoding="utf-8",
    )
    result = _run_against(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr


def test_repo_tree_is_clean() -> None:
    """The real repo passes its own drift check.

    This is the whole point of §10 — the tree that ships the check
    passes the check. Any drift introduced by a later PR fails here
    first, before CI.
    """
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, (
        "docs-drift dirty on the real tree:\n"
        + result.stdout
        + result.stderr
    )
