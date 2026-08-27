# b17: GRRAT · ΔΣ=42
"""Pins `scripts/check_ratification.py` (Grove v0.9 PR 12).

INVARIANTS.md §12 (ratification) and §10 (CI proves the invariants).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "check_ratification.py"


def _run(body: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--body", body],
        capture_output=True,
        text=True,
        check=False,
    )


def test_clean_ratification_passes() -> None:
    body = (
        'Ratified-by: sean — "go ahead with §12"\n'
        "\n"
        "Rest of the PR body follows.\n"
    )
    r = _run(body)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "clean" in r.stdout


def test_ascii_dash_variant_passes() -> None:
    body = 'Ratified-by: sean - "run it, keep the reorder"\n'
    r = _run(body)
    assert r.returncode == 0, r.stdout + r.stderr


def test_curly_quotes_variant_passes() -> None:
    body = 'Ratified-by: sean — “go ahead with §12”\n'
    r = _run(body)
    assert r.returncode == 0, r.stdout + r.stderr


def test_missing_line_flagged() -> None:
    body = "Just a PR description with no ratification line.\n"
    r = _run(body)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "does not match" in r.stderr


def test_empty_body_flagged() -> None:
    r = _run("")
    assert r.returncode == 1, r.stdout + r.stderr
    assert "empty" in r.stderr


def test_ratification_below_other_lines_flagged() -> None:
    body = (
        "Summary of the changes.\n"
        "\n"
        'Ratified-by: sean — "go"\n'
    )
    r = _run(body)
    assert r.returncode == 1, r.stdout + r.stderr


def test_no_quote_flagged() -> None:
    body = "Ratified-by: sean — go ahead\n"
    r = _run(body)
    assert r.returncode == 1, r.stdout + r.stderr


def test_empty_identifier_flagged() -> None:
    body = 'Ratified-by:  — "go"\n'
    r = _run(body)
    assert r.returncode == 1, r.stdout + r.stderr
