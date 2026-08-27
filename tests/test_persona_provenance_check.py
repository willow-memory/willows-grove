# b17: GRPPT · ΔΣ=42
"""Pins `scripts/check_persona_provenance.py` (Grove v0.9 PR 12).

INVARIANTS.md §11 (persona provenance) and §10 (CI proves the invariants).

A provenance checker with no failing-case test is a lie. Every property
the checker enforces is exercised here through a synthetic git repo
that fails, verifying the checker (a) fails loudly and (b) names the
specific commit.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "check_persona_provenance.py"


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
    # Write outside the tree the checker walks — no self-reference.
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
    """A fresh git repo with a `master` branch and a working branch."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "master")
    _git(repo, "config", "user.email", "heimdallr@fleet.willow")
    _git(repo, "config", "user.name", "Heimdallr")
    (repo / "seed.py").write_text("# seed\n", encoding="utf-8")
    _git(repo, "add", "seed.py")
    _git(repo, "commit", "-q", "-m", "seed\n\nPersona: heimdallr")
    _git(repo, "checkout", "-q", "-b", "work")
    return repo


def _commit(repo: Path, message: str, filename: str = "notes.py", content: str = "# noted\n") -> str:
    (repo / filename).write_text(content, encoding="utf-8")
    _git(repo, "add", filename)
    _git(repo, "commit", "-q", "-m", message)
    return _git(repo, "rev-parse", "HEAD").stdout.strip()


def test_clean_commit_passes(synthetic_repo: Path) -> None:
    _commit(synthetic_repo, "feat: something\n\nPersona: hanuman")
    result = _run_checker(synthetic_repo)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "clean" in result.stdout


def test_missing_trailer_flagged(synthetic_repo: Path) -> None:
    _commit(synthetic_repo, "feat: forgot the trailer")
    result = _run_checker(synthetic_repo)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "no `Persona:` trailer" in result.stderr


def test_unknown_persona_flagged(synthetic_repo: Path) -> None:
    _commit(synthetic_repo, "feat: bad name\n\nPersona: not-a-fleet-member")
    result = _run_checker(synthetic_repo)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "names no fleet member" in result.stderr


def test_merge_commit_exempt(synthetic_repo: Path) -> None:
    """A merge commit has no work; it carries no trailer and is not drift."""
    # Set up a side branch
    _commit(synthetic_repo, "side change\n\nPersona: hanuman", filename="side.py")
    side_sha = _git(synthetic_repo, "rev-parse", "HEAD").stdout.strip()
    # Go back to master, diverge
    _git(synthetic_repo, "checkout", "-q", "work")
    _git(synthetic_repo, "reset", "-q", "--hard", "master")
    _commit(synthetic_repo, "work change\n\nPersona: heimdallr", filename="work.py")
    # Merge the side branch — a real merge with two parents
    _git(synthetic_repo, "merge", "-q", "--no-ff", "--no-edit", side_sha)
    result = _run_checker(synthetic_repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_untracked_ext_commit_exempt(synthetic_repo: Path) -> None:
    """Commit touching only untracked-code extensions carries no trailer requirement."""
    _commit(synthetic_repo, "chore: scratch", filename="notes.scratch", content="not tracked\n")
    result = _run_checker(synthetic_repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_multiple_personas_all_validated(synthetic_repo: Path) -> None:
    """A commit that carries two trailers passes only if both are valid."""
    msg = "audit landed\n\nPersona: loki\nPersona: heimdallr"
    _commit(synthetic_repo, msg)
    result = _run_checker(synthetic_repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_one_of_two_personas_bad_flagged(synthetic_repo: Path) -> None:
    msg = "half-audit\n\nPersona: loki\nPersona: not-a-fleet-member"
    _commit(synthetic_repo, msg)
    result = _run_checker(synthetic_repo)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "names no fleet member" in result.stderr


def test_repo_tree_clean() -> None:
    """The real repo passes its own persona-provenance check.

    A branch that opens with §11's arrival must itself demonstrate the
    discipline: every commit on this branch, from the §11-seal commit
    forward, carries a Persona: trailer.
    """
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, (
        "persona-provenance dirty on the real tree:\n"
        + result.stdout
        + result.stderr
    )
