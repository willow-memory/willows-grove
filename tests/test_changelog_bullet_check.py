# b17: GRCLB · ΔΣ=42
"""Pins `scripts/check_changelog_bullet.py` (closes an unenforced clause of
INVARIANTS.md §3).

§3 requires every code-changing PR to append a bullet to `CHANGELOG.md`'s
`[Unreleased]` section. `check_docs_drift.py` only validates bullets that
already exist (that each cites its PR) — it never checks that a
code-changing PR added one in the first place. This test module pins the
checker that closes that gap, following the same synthetic-git-repo
pattern as `tests/test_persona_provenance_check.py`.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "check_changelog_bullet.py"

CHANGELOG_SEED = """\
# Changelog

## [Unreleased]

### Added

- Nothing yet.

## [0.1.0] - 2026-01-01

### Added

- Initial release.
"""


def _git(cwd: Path, *args: str, check: bool = True, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=check,
        env=env,
    )


def _run_checker(cwd: Path) -> subprocess.CompletedProcess:
    """Run the checker with REPO_ROOT rerouted to `cwd`."""
    body = SCRIPT.read_text(encoding="utf-8").replace(
        "REPO_ROOT = Path(__file__).resolve().parent.parent",
        f"REPO_ROOT = Path({str(cwd)!r})",
    )
    rerooted = cwd.parent / f"_check_{cwd.name}.py"
    rerooted.write_text(body, encoding="utf-8")
    # Clear GITHUB_BASE_REF so the local `master` fallback runs.
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": str(cwd.parent)}
    return subprocess.run(
        [sys.executable, str(rerooted)],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


@pytest.fixture
def synthetic_repo(tmp_path: Path) -> Path:
    """A fresh git repo with a `master` branch (carrying CHANGELOG.md) and a
    working branch that commits diverge from.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "master")
    _git(repo, "config", "user.email", "heimdallr@fleet.willow")
    _git(repo, "config", "user.name", "Heimdallr")
    (repo / "CHANGELOG.md").write_text(CHANGELOG_SEED, encoding="utf-8")
    (repo / "seed.py").write_text("# seed\n", encoding="utf-8")
    _git(repo, "add", "CHANGELOG.md", "seed.py")
    _git(repo, "commit", "-q", "-m", "seed")
    _git(repo, "checkout", "-q", "-b", "work")
    return repo


def _write(repo: Path, filename: str, content: str) -> None:
    path = repo / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _commit(repo: Path, message: str) -> None:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", message)


def test_code_change_with_bullet_passes(synthetic_repo: Path) -> None:
    _write(synthetic_repo, "feature.py", "# a feature\n")
    _write(
        synthetic_repo,
        "CHANGELOG.md",
        CHANGELOG_SEED.replace(
            "- Nothing yet.", "- Nothing yet.\n- Added the new feature (#42)."
        ),
    )
    _commit(synthetic_repo, "feat: add feature, changelog it")
    result = _run_checker(synthetic_repo)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "clean" in result.stdout


def test_code_change_without_bullet_fails(synthetic_repo: Path) -> None:
    _write(synthetic_repo, "feature.py", "# a feature, no changelog\n")
    _commit(synthetic_repo, "feat: add feature, forget changelog")
    result = _run_checker(synthetic_repo)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "feature.py" in result.stderr
    assert "no matching CHANGELOG.md bullet" in result.stderr


def test_docs_only_change_without_bullet_passes(synthetic_repo: Path) -> None:
    _write(synthetic_repo, "docs/notes.md", "# some prose\n")
    _commit(synthetic_repo, "docs: add notes")
    result = _run_checker(synthetic_repo)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "docs-only" in result.stdout


def test_changelog_only_change_does_not_need_self_citation(synthetic_repo: Path) -> None:
    """A PR that only edits CHANGELOG.md (e.g. freezing a release) must not
    be required to cite itself — it touches no tracked-code file at all.
    """
    _write(
        synthetic_repo,
        "CHANGELOG.md",
        CHANGELOG_SEED.replace("- Nothing yet.", "- Nothing yet.\n- Housekeeping tidy."),
    )
    _commit(synthetic_repo, "chore: tidy changelog wording")
    result = _run_checker(synthetic_repo)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "docs-only" in result.stdout


def test_empty_range_passes(synthetic_repo: Path) -> None:
    """No commits past base (HEAD == base) — nothing to check."""
    result = _run_checker(synthetic_repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_no_base_branch_degrades_cleanly(tmp_path: Path) -> None:
    """A repo with no master/main and no GITHUB_BASE_REF (e.g. a bare push
    with no PR context) must degrade cleanly rather than error out.
    """
    repo = tmp_path / "lonely"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "solo")
    _git(repo, "config", "user.email", "heimdallr@fleet.willow")
    _git(repo, "config", "user.name", "Heimdallr")
    (repo / "seed.py").write_text("# seed\n", encoding="utf-8")
    _git(repo, "add", "seed.py")
    _git(repo, "commit", "-q", "-m", "seed")
    result = _run_checker(repo)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "no base branch found" in result.stdout


def test_code_change_with_bullet_in_wrong_subsection_fails(synthetic_repo: Path) -> None:
    """A bullet added outside Changed/Added/Fixed/Removed (e.g. under a
    grandfathered 'Previous work' heading) does not satisfy §3.
    """
    seed_with_other = CHANGELOG_SEED.replace(
        "## [0.1.0]",
        "### Previous work (pre-v0.9)\n\n- old stuff\n\n## [0.1.0]",
    )
    _write(synthetic_repo, "CHANGELOG.md", seed_with_other)
    _commit(synthetic_repo, "seed with previous-work section")
    _write(synthetic_repo, "feature.py", "# a feature\n")
    _write(
        synthetic_repo,
        "CHANGELOG.md",
        seed_with_other.replace(
            "- old stuff", "- old stuff\n- sneaked in, not under a real heading"
        ),
    )
    _commit(synthetic_repo, "feat: add feature, bullet in wrong place")
    result = _run_checker(synthetic_repo)
    assert result.returncode == 1, result.stdout + result.stderr


def test_repo_tree_current_state() -> None:
    """Run the real checker against the real repo's current working tree.

    Informational: master's own last merge (PR #8) landed no bullet, so
    the checker is expected to report that as drift when run across a
    range that includes it — that is proof the checker works, not a bug.
    This test only asserts the checker runs and produces a verdict; it
    does not assert a particular pass/fail outcome since that depends on
    which commits are present relative to the local base.
    """
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode in (0, 1), result.stdout + result.stderr
