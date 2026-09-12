# b17: GRPPT · ΔΣ=42
"""Pins `scripts/check_persona_provenance.py` (Grove v0.9 PR 12).

INVARIANTS.md §11 (persona provenance) and §10 (CI proves the invariants).

A provenance checker with no failing-case test is a lie. Every property
the checker enforces is exercised here through a synthetic git repo
that fails, verifying the checker (a) fails loudly and (b) names the
specific commit.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "check_persona_provenance.py"


def _git(
    cwd: Path, *args: str, check: bool = True, env: dict | None = None
) -> subprocess.CompletedProcess:
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
    # Clear GITHUB_BASE_REF so the local `master` fallback runs. Everything
    # else is inherited: a PATH scrubbed to POSIX directories has no git and
    # no python on the Windows leg, and HOME is redirected so no user git
    # config reaches the synthetic repo.
    env = {k: v for k, v in os.environ.items() if k != "GITHUB_BASE_REF"}
    env["HOME"] = str(cwd.parent)
    return subprocess.run(
        [sys.executable, str(rerooted)],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


#: The roster a synthetic repo stands up for itself. It deliberately does NOT
#: match the real fleet: `quill` exists only here, so a test that accepts it
#: proves the checker read this file rather than a set copied into the script.
SYNTHETIC_ROSTER = {
    "_meta": {"schema": "fleet-personas/v1", "note": "test fixture"},
    "heimdallr": {"trust": "ENGINEER"},
    "hanuman": {"trust": "ENGINEER"},
    "loki": {"trust": "ENGINEER"},
    "willow": {"trust": "OPERATOR"},
    "quill": {"trust": "ENGINEER"},
}


def _write_roster(repo: Path, roster: dict) -> Path:
    path = repo / "governance" / "fleet_personas.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(roster, indent=2), encoding="utf-8")
    return path


@pytest.fixture
def synthetic_repo(tmp_path: Path) -> Path:
    """A fresh git repo with a `master` branch and a working branch.

    It carries its own `governance/fleet_personas.json`, because the checker
    reads the roster from the repo it is checking rather than from a literal
    copied into the script.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "master")
    _git(repo, "config", "user.email", "heimdallr@fleet.willow")
    _git(repo, "config", "user.name", "Heimdallr")
    _write_roster(repo, SYNTHETIC_ROSTER)
    (repo / "seed.py").write_text("# seed\n", encoding="utf-8")
    _git(repo, "add", "seed.py")
    _git(repo, "commit", "-q", "-m", "seed\n\nPersona: heimdallr")
    _git(repo, "checkout", "-q", "-b", "work")
    return repo


def _commit(
    repo: Path, message: str, filename: str = "notes.py", content: str = "# noted\n"
) -> str:
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
    _commit(
        synthetic_repo,
        "chore: scratch",
        filename="notes.scratch",
        content="not tracked\n",
    )
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
        "persona-provenance dirty on the real tree:\n" + result.stdout + result.stderr
    )


def test_the_roster_file_is_what_is_read(synthetic_repo: Path) -> None:
    """`quill` is in this repo's roster and in no fleet literal anywhere. If it
    passes, the checker read the file."""
    _commit(synthetic_repo, "feat: something\n\nPersona: quill")
    result = _run_checker(synthetic_repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_a_name_absent_from_the_roster_is_still_drift(synthetic_repo: Path) -> None:
    _commit(synthetic_repo, "feat: something\n\nPersona: nobody")
    result = _run_checker(synthetic_repo)
    assert result.returncode != 0
    assert "names no fleet member" in result.stdout + result.stderr


def test_meta_is_not_a_persona(synthetic_repo: Path) -> None:
    """§11 says so outright, and `_meta` is a key like any other in the JSON."""
    _commit(synthetic_repo, "feat: something\n\nPersona: _meta")
    result = _run_checker(synthetic_repo)
    assert result.returncode != 0


def test_an_unreadable_roster_fails_closed(synthetic_repo: Path) -> None:
    """A checker that cannot read its own subject must not pass everything.

    Appendix B: a gate that cannot check its subject is not a weaker gate; it
    is no gate.
    """
    (synthetic_repo / "governance" / "fleet_personas.json").unlink()
    _commit(synthetic_repo, "feat: something\n\nPersona: heimdallr")
    result = _run_checker(synthetic_repo)
    assert result.returncode != 0
    assert "could not read the fleet roster" in result.stdout + result.stderr


def test_a_roster_with_no_personas_is_refused(synthetic_repo: Path) -> None:
    """An empty roster would reject every trailer; say why rather than
    reporting each honest commit as drift."""
    _write_roster(synthetic_repo, {"_meta": {"schema": "fleet-personas/v1"}})
    _commit(synthetic_repo, "feat: something\n\nPersona: heimdallr")
    result = _run_checker(synthetic_repo)
    assert result.returncode != 0
    assert "no personas found" in result.stdout + result.stderr


def test_schmidt_is_accepted_by_the_real_roster() -> None:
    """The drift that motivated this: `schmidt` reached
    governance/fleet_personas.json and never the literal in the script, so a
    commit naming a real fleet member was reported as drift."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("_persona_probe", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    personas, problem = module.load_fleet_personas()
    assert problem is None
    assert "schmidt" in personas
    assert "_meta" not in personas
