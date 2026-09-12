# b17: DDER · ΔΣ=42
"""Pins INVARIANTS.md §7 (consent flows are real, not automatic).

`GROVE_MCP_AUTO_APPROVE` was removed pre-PR-6 — there is no auto-approve
env-var escape hatch left in the code (`grove/mcp_auth.py`,
`grove/mcp_local.py`). Docs that still instruct an operator not to set it
misrepresent it as a live knob. This pins that the dead env var is gone
from the docs that used to mention it.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

DEAD_ENVVAR = "GROVE_MCP_AUTO_APPROVE"

DOCS_TO_CHECK = [
    REPO_ROOT / "skills" / "grove-serve.md",
    REPO_ROOT / "docs" / "runbooks" / "grove.md",
]


def _docs_naming_the_dead_envvar(docs: list[Path], root: Path) -> list[str]:
    """Every shipped doc in `docs` whose text still names the dead knob,
    as a path relative to `root`. A doc that is absent is skipped: the
    dead knob cannot be referenced from a doc that isn't shipped, and the
    clean v0.9 tree omits the pre-v0.9 runbook + skill files that once
    carried these references — the honesty pin is satisfied by absence."""
    offenders = []
    for doc in docs:
        if not doc.exists():
            continue
        if DEAD_ENVVAR in doc.read_text(encoding="utf-8"):
            # Repo form, forward slashes, on every platform: the sweep names a
            # path in the tree, not a path on this filesystem.
            offenders.append(doc.relative_to(root).as_posix())
    return offenders


def test_docs_do_not_reference_dead_auto_approve_envvar() -> None:
    offenders = _docs_naming_the_dead_envvar(DOCS_TO_CHECK, REPO_ROOT)
    assert not offenders, (
        f"{DEAD_ENVVAR} no longer exists in code (INVARIANTS.md §7) but is "
        f"still referenced as a live knob in: {offenders}"
    )


def test_the_dead_envvar_sweep_fires_on_a_planted_runbook(tmp_path) -> None:
    """Planted: a runbook that still tells the operator not to set the
    dead knob, beside one that never names it and one that does not
    exist. The sweep must name exactly the first, relative to the tree."""
    runbook = tmp_path / "docs" / "runbooks" / "grove.md"
    runbook.parent.mkdir(parents=True)
    runbook.write_text(f"Never set {DEAD_ENVVAR}=1 in production.\n", encoding="utf-8")
    clean = tmp_path / "skills" / "grove-serve.md"
    clean.parent.mkdir()
    clean.write_text("Approval is a human act at the served page.\n", encoding="utf-8")
    absent = tmp_path / "docs" / "gone.md"

    assert _docs_naming_the_dead_envvar([runbook, clean, absent], tmp_path) == [
        "docs/runbooks/grove.md"
    ]
