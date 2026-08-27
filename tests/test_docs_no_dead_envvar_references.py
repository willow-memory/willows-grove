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


def test_docs_do_not_reference_dead_auto_approve_envvar() -> None:
    offenders = []
    for doc in DOCS_TO_CHECK:
        text = doc.read_text(encoding="utf-8")
        if DEAD_ENVVAR in text:
            offenders.append(str(doc.relative_to(REPO_ROOT)))

    assert not offenders, (
        f"{DEAD_ENVVAR} no longer exists in code (INVARIANTS.md §7) but is "
        f"still referenced as a live knob in: {offenders}"
    )
