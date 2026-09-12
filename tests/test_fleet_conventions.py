# b17: WGRV1 ΔΣ=42
"""tests/test_fleet_conventions.py — this tree, held to the fleet's published
conventions.

G2-conventions-grove (fleet loop plan, Wave 2; decision 4). Every repo in
the fleet carries this file, and its rules are READ from the fleet's one
published document — `reconciler conventions --json` (willow-reconciler,
PyPI) — never restated here. A rule that lived in each repo's own test
file would drift one repo at a time, which is exactly how the incidents the
document's `sources` name happened: each repo's release wiring was locally
reasonable and fleet-wide inconsistent.

The document is vendored at `tests/fleet_conventions.json` so this file
runs with no dependency beyond the stdlib, and pinned by hash so a silent
local edit cannot pass for a re-sync: the pin fails with the instruction to
re-sync from the reconciler (or to record the decision not to). When the
reconciler happens to be importable, the vendored copy is also held equal
to the live document.

What the rules do and do not bite on, in *this* tree, today:

* **pr-title guard.** The rule requires `.github/workflows/pr-title.yml`
  once `release-please.yml` arms auto-merge on the release PR. This repo
  has no `release-please.yml` — it gains release-please in the plan's
  Wave 4 (C4-grove-release) — so `_arms_automerge` is False and the rule is
  vacuous here. The real-tree test asserts exactly that, so the day the
  workflow lands the assertion flips and the test has to be rewritten to
  the reference shape (armed, and guarded). The plant proves the helper
  fires regardless.
* **hidden set and reasoning comments.** Both read
  `release-please-config.json`, which is likewise absent until Wave 4. The
  real-tree tests skip with that reason; their plants still run.
* **numbered pile.** The rule requires `.github/workflows/trailers.yml`
  once a repo keeps a numbered idea pile. This repo keeps one at
  `docs/ideas.md` (E3-piles, fleet plan Wave 3) and carries the workflow
  (E3-trailers), so the rule bites here and the real-tree test asserts
  both.
* **CONTRIBUTING names the test command.** `CONTRIBUTING.md` names the
  command a contributor runs (the one `README.md` also names and CI runs),
  and that is what `TEST_COMMAND` pins. It was absent when this file first
  landed (PR 59 carried the test as a strict `xfail` naming the follow-up);
  E3-trailers added it.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

#: The vendored copy of `reconciler conventions --json`, byte-for-byte as
#: willow-reconciler 0.6.0 writes it (indent=2, trailing newline).
VENDORED = REPO_ROOT / "tests" / "fleet_conventions.json"

#: sha256 of `VENDORED` as saved from willow-reconciler 0.6.0 on 2026-09-12.
VENDORED_SHA256 = "8c2ba122a7100141200d8c76ad086339f984446ab7e90dd9c27a092dbf7f5335"
VENDORED_FROM = "willow-reconciler 0.6.0"

RULES = json.loads(VENDORED.read_text(encoding="utf-8"))

RELEASE_PLEASE = ".github/workflows/release-please.yml"
RELEASE_CONFIG = "release-please-config.json"
CONTRIBUTING = "CONTRIBUTING.md"
#: This repo's numbered idea pile, in the shape `reconciler run` reads.
PILE = "docs/ideas.md"
ARMS_AUTOMERGE = "gh pr merge --auto"
#: The command CONTRIBUTING.md names under "Build and test", README.md names
#: under "Getting started as a tester", and `.github/workflows/tests.yml`
#: runs (with `--tb=short` added there).
TEST_COMMAND = (
    "python3 -m pytest -x -q --ignore=tests/e2e --ignore=tests/e2e_ollama "
    "--ignore=tests/e2e_willow_mcp"
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _arms_automerge(root: Path) -> bool:
    workflow = root / RELEASE_PLEASE
    return workflow.exists() and ARMS_AUTOMERGE in workflow.read_text(encoding="utf-8")


def _missing_when_armed(root: Path, required: list[str]) -> list[str]:
    if not _arms_automerge(root):
        return []
    return [f for f in required if not (root / f).exists()]


def _config_hidden_types(config_text: str) -> set[str]:
    sections = json.loads(config_text)["packages"]["."]["changelog-sections"]
    return {s["type"] for s in sections if s.get("hidden")}


def _config_missing_comments(config_text: str, required: list[str]) -> list[str]:
    package = json.loads(config_text)["packages"]["."]
    return [c for c in required if c not in package]


def _missing_when_pile_exists(root: Path, required: list[str]) -> list[str]:
    if not (root / PILE).exists():
        return []
    return [f for f in required if not (root / f).exists()]


def _names_test_command(contributing_text: str) -> bool:
    return TEST_COMMAND in contributing_text


# ── the document itself ──────────────────────────────────────────────────────


def test_the_vendored_document_is_the_published_one():
    """The pin. A vendored copy that drifts from what the reconciler
    publishes is a restated rule set wearing the document's name."""
    assert RULES["schema"] == "willow-fleet-conventions/1"
    assert _sha256(VENDORED.read_bytes()) == VENDORED_SHA256, (
        f"tests/fleet_conventions.json no longer hashes to the copy saved from "
        f"{VENDORED_FROM}: re-sync from `reconciler conventions --json` "
        "(willow-reconciler >=0.6.0) and update VENDORED_SHA256/VENDORED_FROM, "
        "or record the decision"
    )


def test_the_pin_fires_on_a_planted_one_byte_change():
    """Planted: the vendored bytes with one byte flipped — the smallest
    edit a local hand could make. The pin must not match."""
    data = bytearray(VENDORED.read_bytes())
    assert _sha256(bytes(data)) == VENDORED_SHA256
    at = data.index(b'"chore"') + 1
    data[at] = ord("C")
    assert _sha256(bytes(data)) != VENDORED_SHA256


def test_the_vendored_document_equals_the_live_one_when_the_reconciler_is_here():
    """Optional: when willow-reconciler is importable, the vendored copy is
    the live document, not merely a document with the right hash."""
    conventions = pytest.importorskip("reconciler.conventions")
    assert RULES == conventions.conventions()


# ── the real tree ────────────────────────────────────────────────────────────


def test_pr_title_guard_is_present_wherever_automerge_is_armed():
    """Vacuous in this tree, and asserted to be: there is no
    `release-please.yml` here until C4-grove-release (fleet plan Wave 4),
    so nothing arms auto-merge and the guard is not yet required. When that
    workflow lands this assertion flips, and this test must be rewritten to
    the reference shape — armed, and `pr-title.yml` present."""
    assert _arms_automerge(REPO_ROOT) is False
    assert (
        _missing_when_armed(
            REPO_ROOT, RULES["required_when_release_please_arms_automerge"]
        )
        == []
    )


def _release_config_text() -> str:
    config = REPO_ROOT / RELEASE_CONFIG
    if not config.exists():
        pytest.skip(
            f"no {RELEASE_CONFIG} in this tree until C4-grove-release (fleet "
            "plan Wave 4); vacuous here — the plant below still runs"
        )
    return config.read_text(encoding="utf-8")


def test_the_configs_hidden_set_equals_the_published_set():
    assert _config_hidden_types(_release_config_text()) == set(RULES["hidden_types"])


def test_the_config_carries_every_required_reasoning_comment():
    assert (
        _config_missing_comments(
            _release_config_text(), RULES["required_config_comments"]
        )
        == []
    )


def test_contributing_names_the_test_command():
    assert RULES["contributing_must_name_test_command"] is True
    contributing = REPO_ROOT / CONTRIBUTING
    assert contributing.exists(), f"{CONTRIBUTING} is not in this tree"
    assert _names_test_command(contributing.read_text(encoding="utf-8"))


def test_the_test_command_this_file_pins_is_the_one_the_readme_names():
    """README.md names the same command under "Getting started as a
    tester". Two documents naming the command must name the same one, or
    the pin above is holding CONTRIBUTING.md to a line the README
    contradicts."""
    assert _names_test_command((REPO_ROOT / "README.md").read_text(encoding="utf-8"))


def test_trailers_workflow_is_present_because_a_pile_exists():
    """The rule bites here: `docs/ideas.md` is a numbered pile, so the
    `reconciler verify` gate must run in CI (E3-trailers, fleet plan Wave
    3). A pile without the gate is a doc whose join keys nothing checks."""
    assert (REPO_ROOT / PILE).exists()
    assert (
        _missing_when_pile_exists(REPO_ROOT, RULES["required_when_pile_exists"]) == []
    )


# ── the plants ───────────────────────────────────────────────────────────────


def _tree(
    tmp_path: Path, label: str, *, arms: bool, files: tuple[str, ...] = ()
) -> Path:
    root = tmp_path / label
    (root / ".github" / "workflows").mkdir(parents=True)
    body = "jobs:\n  release-please:\n    steps:\n      - run: |\n"
    body += f'          {ARMS_AUTOMERGE} "$pr"\n' if arms else "          gh pr list\n"
    (root / RELEASE_PLEASE).write_text(body, encoding="utf-8")
    for f in files:
        (root / f).parent.mkdir(parents=True, exist_ok=True)
        (root / f).write_text("# planted\n", encoding="utf-8")
    return root


def test_the_armed_tree_check_fires_on_a_planted_tree_missing_the_guard(tmp_path):
    required = RULES["required_when_release_please_arms_automerge"]
    assert _missing_when_armed(_tree(tmp_path, "bare", arms=True), required) == required
    assert (
        _missing_when_armed(
            _tree(tmp_path, "guarded", arms=True, files=tuple(required)), required
        )
        == []
    )
    assert _missing_when_armed(_tree(tmp_path, "manual", arms=False), required) == []


def test_the_hidden_set_check_catches_a_planted_config_that_unhides_ci():
    planted = json.dumps(
        {
            "packages": {
                ".": {
                    "changelog-sections": [
                        {"type": "feat", "section": "Added"},
                        {"type": "docs", "section": "Docs", "hidden": True},
                        {"type": "test", "section": "Tests", "hidden": True},
                        {"type": "ci", "section": "CI"},
                        {"type": "chore", "section": "Chores", "hidden": True},
                    ],
                    "$comment-what-cuts-a-release": "kept",
                }
            }
        }
    )
    assert _config_hidden_types(planted) == {"chore", "docs", "test"}
    assert _config_hidden_types(planted) != set(RULES["hidden_types"])
    assert _config_missing_comments(planted, RULES["required_config_comments"]) == [
        "$comment-hidden-rule"
    ]


def test_the_pile_check_fires_on_a_planted_tree_with_a_pile_and_no_verify_gate(
    tmp_path,
):
    required = RULES["required_when_pile_exists"]
    with_pile = _tree(tmp_path, "pile", arms=False, files=(PILE,))
    assert _missing_when_pile_exists(with_pile, required) == required
    gated = _tree(tmp_path, "gated", arms=False, files=(PILE, *required))
    assert _missing_when_pile_exists(gated, required) == []


def test_the_contributing_check_catches_a_planted_contributing_without_the_command():
    assert not _names_test_command("# Contributing\n\nRun the tests before pushing.\n")
    assert _names_test_command(f"```sh\n{TEST_COMMAND}\n```\n")
