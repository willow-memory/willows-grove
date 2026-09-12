# b17: WGRV1 ΔΣ=42
"""tests/test_ci_floor.py — the fleet CI floor, held in shape.

Fleet plan decision 5 (docs/ideas.md item 30): every repo's `tests.yml` has
a Linux job whose Python matrix is derived from `pyproject.toml`'s
`Programming Language :: Python :: 3.X` classifiers, a Windows job on the
floor and ceiling of that list, a lint job with ruff pinned to an exact
version, and an aggregate `test` job that needs every leg, runs
`if: always()`, and fails when any needed result is not `success`. Each
of those is a thing that drifts silently: a classifier added without a
matrix row means a Python the package claims and CI never runs; an
unpinned ruff means the gate's rules change under the tree; a leg left out
of `needs:` means a red leg that blocks nothing; and a gate that reads
`skipped` as "not failed" is the exact hole the aggregate job exists to
close. So each is pinned here, and each pin is planted.

Line-level parse of the workflow, no PyYAML dependency, in the house style
of the other `tests/test_ci_*` pins; `tomllib` (stdlib on 3.11+) for the
classifiers. The gate's verdict is `scripts/ci_gate.py`, imported by path
and fed a planted `needs`.
"""

from __future__ import annotations

import importlib.util
import re
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "tests.yml"
PYPROJECT = REPO_ROOT / "pyproject.toml"
GATE_SCRIPT = REPO_ROOT / "scripts" / "ci_gate.py"

LINUX_JOB = "test-suite"
WINDOWS_JOB = "test-windows"
LINT_JOB = "lint"
GATE_JOB = "test"

_CLASSIFIER_RE = re.compile(r"^Programming Language :: Python :: (3\.\d+)$")
_JOB_KEY_RE = re.compile(r"^  ([A-Za-z_][A-Za-z0-9_-]*):\s*$", re.MULTILINE)
_MATRIX_RE = re.compile(r"^\s+python-version:\s*\[([^\]]*)\]\s*$", re.MULTILINE)
_RUFF_PIN_RE = re.compile(
    r"pip install\s+(?:\"|')?ruff==(\d+\.\d+\.\d+)(?:\"|')?\s*$", re.MULTILINE
)
_RUFF_UNPINNED_RE = re.compile(r"pip install\s+(?:\"|')?ruff(?!==\d)", re.MULTILINE)
_NEEDS_RE = re.compile(r"^\s+needs:\s*\[([^\]]*)\]\s*$", re.MULTILINE)
_ALWAYS_RE = re.compile(r"^\s+if:\s*always\(\)\s*$", re.MULTILINE)


def _classifier_minors(pyproject_text: str) -> list[str]:
    """Every `3.X` the classifiers list, in order — the versions the package
    claims to support, which is what CI has to run."""
    classifiers = tomllib.loads(pyproject_text)["project"]["classifiers"]
    out = []
    for entry in classifiers:
        m = _CLASSIFIER_RE.match(entry)
        if m:
            out.append(m.group(1))
    return out


def _job_names(workflow_text: str) -> list[str]:
    """Top-level job keys (two-space indent under `jobs:`), in order."""
    jobs_at = workflow_text.find("\njobs:\n")
    assert jobs_at != -1, "workflow has no `jobs:` block"
    return _JOB_KEY_RE.findall(workflow_text[jobs_at:])


def _job_block(workflow_text: str, job: str) -> str:
    """The text of one job: from its key to the next two-space-indented key."""
    m = re.search(rf"^  {re.escape(job)}:\s*$", workflow_text, re.MULTILINE)
    assert m, f"workflow has no job named {job!r}"
    rest = workflow_text[m.end() :]
    nxt = _JOB_KEY_RE.search(rest)
    return rest[: nxt.start()] if nxt else rest


def _matrix_versions(workflow_text: str, job: str) -> list[str]:
    """The `python-version: [...]` list of one job, quotes stripped."""
    m = _MATRIX_RE.search(_job_block(workflow_text, job))
    if m is None:
        return []
    return [v.strip().strip("\"'") for v in m.group(1).split(",") if v.strip()]


def _ruff_pin(workflow_text: str) -> str | None:
    """The exact `ruff==X.Y.Z` the lint job installs, or None when ruff is
    installed unpinned (or not at all)."""
    block = _job_block(workflow_text, LINT_JOB)
    m = _RUFF_PIN_RE.search(block)
    return m.group(1) if m else None


def _ruff_installed_unpinned(workflow_text: str) -> bool:
    return _RUFF_UNPINNED_RE.search(_job_block(workflow_text, LINT_JOB)) is not None


def _gate_needs(workflow_text: str) -> list[str]:
    m = _NEEDS_RE.search(_job_block(workflow_text, GATE_JOB))
    if m is None:
        return []
    return [v.strip() for v in m.group(1).split(",") if v.strip()]


def _gate_runs_always(workflow_text: str) -> bool:
    return _ALWAYS_RE.search(_job_block(workflow_text, GATE_JOB)) is not None


def _gate_uses_the_script(workflow_text: str) -> bool:
    """The gate's verdict is scripts/ci_gate.py fed `toJSON(needs)` — not an
    `if:` expression, so the verdict can be planted below."""
    block = _job_block(workflow_text, GATE_JOB)
    return "scripts/ci_gate.py" in block and "toJSON(needs)" in block


def _legs_the_gate_misses(workflow_text: str) -> list[str]:
    """Every job in the workflow, other than the gate itself, that the gate
    does not `needs:`."""
    needed = set(_gate_needs(workflow_text))
    return [j for j in _job_names(workflow_text) if j != GATE_JOB and j not in needed]


def _load_gate():
    spec = importlib.util.spec_from_file_location("ci_gate", GATE_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ── the real tree ────────────────────────────────────────────────────────────


def _workflow() -> str:
    assert WORKFLOW.exists(), f"missing {WORKFLOW}"
    return WORKFLOW.read_text(encoding="utf-8")


def test_the_classifiers_name_at_least_two_minors():
    """The self-check: a derivation from an empty list pins nothing."""
    minors = _classifier_minors(PYPROJECT.read_text(encoding="utf-8"))
    assert len(minors) >= 2, f"pyproject.toml classifiers name {minors}"


def test_the_linux_matrix_equals_the_classifiers():
    classifiers = _classifier_minors(PYPROJECT.read_text(encoding="utf-8"))
    assert _matrix_versions(_workflow(), LINUX_JOB) == classifiers, (
        f"{LINUX_JOB}'s python-version matrix must be exactly the minors "
        f"pyproject.toml's classifiers list ({classifiers}) — a claimed "
        "Python that CI does not run is a claim, not a test"
    )


def test_the_windows_leg_runs_the_floor_and_the_ceiling():
    classifiers = _classifier_minors(PYPROJECT.read_text(encoding="utf-8"))
    assert _matrix_versions(_workflow(), WINDOWS_JOB) == [
        classifiers[0],
        classifiers[-1],
    ]


def test_ruff_is_pinned_to_an_exact_version():
    text = _workflow()
    assert not _ruff_installed_unpinned(text), "the lint job installs ruff unpinned"
    pin = _ruff_pin(text)
    assert pin is not None, "the lint job does not install ruff==X.Y.Z"


def test_the_gate_needs_every_leg_runs_always_and_uses_the_script():
    text = _workflow()
    assert GATE_JOB in _job_names(text)
    assert _legs_the_gate_misses(text) == [], (
        "the aggregate `test` job must need every other job in the workflow; "
        "a leg it does not need is a leg that can go red and block nothing"
    )
    assert _gate_runs_always(text), (
        "the gate must run `if: always()` or a failed leg skips it"
    )
    assert _gate_uses_the_script(text), (
        "the gate's verdict must be scripts/ci_gate.py over toJSON(needs)"
    )
    assert GATE_SCRIPT.exists()


def test_the_gate_script_is_green_only_when_every_leg_succeeded():
    gate = _load_gate()
    ok, _ = gate.verdict(
        {j: {"result": "success"} for j in (LINUX_JOB, WINDOWS_JOB, LINT_JOB)}
    )
    assert ok


# ── the plants ───────────────────────────────────────────────────────────────

_PLANTED_WORKFLOW = """name: Planted
on: [push]
permissions:
  contents: read
jobs:
  test-suite:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.13"]
    steps:
      - run: echo linux
  test-windows:
    runs-on: windows-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.13"]
    steps:
      - run: echo windows
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: pip install ruff
      - run: ruff check .
  extra-leg:
    runs-on: ubuntu-latest
    steps:
      - run: echo nobody needs me
  test:
    needs: [test-suite, lint]
    runs-on: ubuntu-latest
    steps:
      - if: ${{ needs.test-suite.result != 'success' }}
        run: exit 1
"""

_PLANTED_PYPROJECT = """[project]
name = "planted"
classifiers = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
]
"""


def test_the_matrix_pin_fires_on_a_planted_workflow_missing_a_classifier():
    """Planted: classifiers 3.11/3.12/3.13, a Linux matrix that skips 3.12.
    The derivation must read exactly the three minors (the bare `3`
    classifier is not a version) and the comparison must fail."""
    assert _classifier_minors(_PLANTED_PYPROJECT) == ["3.11", "3.12", "3.13"]
    assert _matrix_versions(_PLANTED_WORKFLOW, LINUX_JOB) == ["3.11", "3.13"]
    assert _matrix_versions(_PLANTED_WORKFLOW, LINUX_JOB) != _classifier_minors(
        _PLANTED_PYPROJECT
    )
    assert _matrix_versions(_PLANTED_WORKFLOW, "extra-leg") == [], (
        "a job with no matrix reads as none"
    )


def test_the_ruff_pin_fires_on_a_planted_unpinned_install():
    """Planted: `pip install ruff` with no `==`. Unpinned must be reported
    and the pin read as absent; a planted `ruff==0.1.2` reads back exactly."""
    assert _ruff_installed_unpinned(_PLANTED_WORKFLOW)
    assert _ruff_pin(_PLANTED_WORKFLOW) is None
    pinned = _PLANTED_WORKFLOW.replace(
        "pip install ruff\n", "pip install ruff==0.1.2\n"
    )
    assert not _ruff_installed_unpinned(pinned)
    assert _ruff_pin(pinned) == "0.1.2"
    ranged = _PLANTED_WORKFLOW.replace(
        "pip install ruff\n", 'pip install "ruff>=0.1"\n'
    )
    assert _ruff_installed_unpinned(ranged) and _ruff_pin(ranged) is None


def test_the_gate_shape_pins_fire_on_a_planted_gate_that_misses_a_leg():
    """Planted: a gate that needs two of four legs, has no `if: always()`,
    and decides with an `if:` expression instead of the script."""
    assert _job_names(_PLANTED_WORKFLOW) == [
        "test-suite",
        "test-windows",
        "lint",
        "extra-leg",
        "test",
    ]
    assert _gate_needs(_PLANTED_WORKFLOW) == ["test-suite", "lint"]
    assert _legs_the_gate_misses(_PLANTED_WORKFLOW) == ["test-windows", "extra-leg"]
    assert not _gate_runs_always(_PLANTED_WORKFLOW)
    assert not _gate_uses_the_script(_PLANTED_WORKFLOW)


def test_the_gate_script_fires_on_a_planted_needs_with_one_leg_skipped():
    """Planted: every leg green except one that was skipped — the exact
    shape GitHub produces when a dependency fails and `needs:` skips the
    dependent — and the same with cancelled, failure, and a missing
    result. Each must be red; only all-success is green; a gate that needs
    nothing is red too, because it gates nothing."""
    gate = _load_gate()
    green = {j: {"result": "success"} for j in (LINUX_JOB, WINDOWS_JOB, LINT_JOB)}
    assert gate.verdict(green)[0]
    for bad in ("skipped", "cancelled", "failure"):
        planted = dict(green, lint={"result": bad})
        ok, lines = gate.verdict(planted)
        assert not ok, f"a {bad} leg must make the gate red"
        assert any(line.startswith("RED lint") for line in lines)
    assert not gate.verdict(dict(green, lint={}))[0], "a missing result is red"
    assert not gate.verdict({})[0], "needing nothing is red"
    assert gate.main(["ci_gate", '{"lint": {"result": "skipped"}}']) == 1
    assert gate.main(["ci_gate", '{"lint": {"result": "success"}}']) == 0
    assert gate.main(["ci_gate", "not json"]) == 2
