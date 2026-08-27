# b17: WGRV1 ΔΣ=42
"""Pin INVARIANTS.md §10 — the ollama/willow-mcp CI steps fail loud.

Grove v0.9 PR 12 — Loki finding #36 (m36-hashfiles-guard-fails-loud).

``.github/workflows/tests.yml`` used to gate the "Run Ollama-backed
watcher e2e" and "Run willow-mcp mock e2e" steps behind
``if: ${{ hashFiles('DIR/test_*.py', ...) != '' }}``. That guard only
ever looks at *filenames*. It goes silently false — and the step
silently no-ops, taking the §10 CI witness with it — not only when a
future PR drains ``tests/e2e_ollama/`` or ``tests/e2e_willow_mcp/``
back down to a bare ``.gitkeep`` (which is fine), but also when tests
are renamed off the ``test_*.py`` convention while real ``def test_``
bodies stay inside (which is not fine — nothing would ever say so).

The fix removes the hashFiles-only guard from both steps (unconditional
``run:``) and routes the pytest invocation through
``scripts/run_test_dir_or_fail.sh``, which decides on directory
*contents* instead: no .py files -> clean no-op; .py files with no
``def test_`` anywhere -> loud failure; otherwise -> run pytest for
real.

This test pins two things:

1. Static: neither step in the workflow yaml carries a hashFiles-only
   ``if:`` guard any more, and both route through the new wrapper
   script (so the empty-vs-renamed distinction is actually handled,
   not just deleted).
2. Behavioral: the wrapper script itself draws that distinction
   correctly against synthetic directories.

Must fail on the unfixed tree: the workflow still carries the
hashFiles guard verbatim, and ``scripts/run_test_dir_or_fail.sh``
does not exist yet.
"""
from __future__ import annotations

import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "tests.yml"
WRAPPER = REPO_ROOT / "scripts" / "run_test_dir_or_fail.sh"

STEP_NAMES = [
    "Run Ollama-backed watcher e2e (PR 8+)",
    "Run willow-mcp mock e2e (PR 10+)",
]


def _extract_step(text: str, step_name: str) -> str:
    """Return the raw yaml text of one `- name: <step_name>` step block.

    Steps are indented six spaces under `steps:`. Slicing from this
    step's `- name:` line up to the next one (or end of file for the
    last step) isolates just that step's `if:`/`run:` body without
    needing a full yaml parser (pyyaml isn't a declared dependency
    here, and the guard we're pinning is a plain text substring
    anyway).
    """
    marker = f"      - name: {step_name}\n"
    start = text.find(marker)
    assert start != -1, f"workflow no longer has a step named {step_name!r}"
    body_start = start + len(marker)
    next_step = text.find("\n      - name:", body_start)
    body = text[body_start:] if next_step == -1 else text[body_start:next_step]
    return body


def _workflow_text() -> str:
    assert WORKFLOW.exists(), f"missing workflow file: {WORKFLOW}"
    return WORKFLOW.read_text(encoding="utf-8")


@pytest.mark.parametrize("step_name", STEP_NAMES)
def test_step_no_longer_carries_hashfiles_only_guard(step_name):
    """Neither target step's `if:` gates on hashFiles(...) any more.

    On the unfixed tree each step has exactly
    ``if: ${{ hashFiles('DIR/test_*.py', ...) != '' }}`` — a filename
    glob that silently skips the step whenever the glob stops matching,
    whether the directory is legitimately empty or the tests were
    merely renamed. The fix drops the guard entirely (unconditional
    run) and puts the empty/renamed distinction inside
    scripts/run_test_dir_or_fail.sh instead.
    """
    body = _extract_step(_workflow_text(), step_name)
    assert "hashFiles(" not in body, (
        f"{step_name!r} still gates on hashFiles(...) — a renamed test file "
        "would silently no-op this step again (docs/INVARIANTS.md §10)."
    )
    assert "if:" not in body, (
        f"{step_name!r} still carries an `if:` guard; the fix runs it "
        "unconditionally and pushes the empty/renamed distinction into "
        "scripts/run_test_dir_or_fail.sh."
    )


@pytest.mark.parametrize("step_name", STEP_NAMES)
def test_step_routes_through_fail_loud_wrapper(step_name):
    """The step's `run:` now calls the content-aware wrapper script.

    Merely deleting the guard without replacing it would make the step
    fail outright on a genuinely empty `.gitkeep` scaffold (pytest
    exits 5, "no tests ran"). The fix must route through a wrapper that
    tells a clean scaffold apart from tests hidden by a bad rename.
    """
    body = _extract_step(_workflow_text(), step_name)
    assert "run_test_dir_or_fail.sh" in body, (
        f"{step_name!r} must invoke scripts/run_test_dir_or_fail.sh so an "
        "empty scaffold stays a no-op while a bad rename still fails loud."
    )


def _make_executable_copy(tmp_path: Path) -> Path:
    assert WRAPPER.exists(), (
        "scripts/run_test_dir_or_fail.sh is missing — the m36 fix has not "
        "landed."
    )
    dest = tmp_path / "run_test_dir_or_fail.sh"
    dest.write_bytes(WRAPPER.read_bytes())
    dest.chmod(dest.stat().st_mode | stat.S_IEXEC)
    return dest


def _run_wrapper(script: Path, target_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(script), str(target_dir), "-q", "--tb=short"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_wrapper_is_a_noop_on_gitkeep_only_scaffold(tmp_path):
    """A directory with nothing but `.gitkeep` stays a clean no-op."""
    script = _make_executable_copy(tmp_path)
    scaffold = tmp_path / "scaffold_only"
    scaffold.mkdir()
    (scaffold / ".gitkeep").write_text("", encoding="utf-8")

    result = _run_wrapper(script, scaffold)

    assert result.returncode == 0, (
        f"a .gitkeep-only scaffold must exit 0, got {result.returncode}: "
        f"{result.stdout}\n{result.stderr}"
    )


def test_wrapper_fails_loud_when_py_files_have_no_tests(tmp_path):
    """.py files present but none define `def test_` -> loud failure.

    This is the exact scenario a hashFiles('test_*.py') guard used to
    hide: the file could be renamed off the test_*.py convention (or
    simply stripped of its test bodies) and the CI step would silently
    stop meaning anything.
    """
    script = _make_executable_copy(tmp_path)
    renamed = tmp_path / "renamed_off_convention"
    renamed.mkdir()
    (renamed / "watcher_ollama_checks.py").write_text(
        "def helper():\n    return 1\n", encoding="utf-8"
    )

    result = _run_wrapper(script, renamed)

    assert result.returncode != 0, (
        "a directory with .py files but no `def test_` must fail loudly, "
        f"got exit 0: {result.stdout}"
    )


def test_wrapper_runs_real_tests_when_present(tmp_path):
    """A directory with an actual `def test_` gets handed to pytest."""
    script = _make_executable_copy(tmp_path)
    real = tmp_path / "has_tests"
    real.mkdir()
    (real / "test_trivial.py").write_text(
        "def test_trivially_true():\n    assert True\n", encoding="utf-8"
    )

    result = _run_wrapper(script, real)

    assert result.returncode == 0, (
        f"a directory with a passing def test_ must exit 0 via pytest: "
        f"{result.stdout}\n{result.stderr}"
    )
    assert "1 passed" in result.stdout, (
        f"expected pytest to actually collect and run the test: {result.stdout}"
    )
