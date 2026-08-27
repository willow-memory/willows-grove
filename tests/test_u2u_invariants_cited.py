# tests/test_u2u_invariants_cited.py
# b17: U2UC1  ΔΣ=42
"""Anchor-citation witness for INVARIANTS.md §5 (trust order).

Finding m30-u2u-anchor-citations: every code comment on the lines that
implement or restate the signature-before-consent discipline must cite
INVARIANTS.md §5 by anchor, not by line number. Before this fix,
`u2u/consent.py` and `bridge/app.py._admit_contact` described the ordering
in prose without ever naming the anchor a reader could jump to, so the
citation trail broke at exactly the two places (the gate itself, and the
bridge's re-KNOCK admission) the section calls out by name.

This does not re-test the trust order itself — `tests/test_u2u_consent_order.py`
and `tests/test_u2u_trust.py` already own that. It only pins the citation.
"""

import os

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ANCHOR = "INVARIANTS.md §5"

CITED_FILES = [
    "u2u/listener.py",
    "u2u/consent.py",
    "bridge/app.py",
]


@pytest.mark.parametrize("relpath", CITED_FILES)
def test_file_cites_section_5_anchor(relpath):
    path = os.path.join(REPO_ROOT, relpath)
    with open(path, "r", encoding="utf-8") as f:
        contents = f.read()
    assert ANCHOR in contents, (
        f"{relpath} implements/describes the §5 trust order (signature -> "
        f"consent -> dispatch) but no comment or docstring in the file cites "
        f"{ANCHOR!r} by anchor."
    )


def test_bridge_admit_contact_cites_anchor_near_definition():
    """The re-KNOCK admission story §5 tells is _admit_contact itself —
    the citation must sit on/near that function, not merely somewhere else
    in the module."""
    path = os.path.join(REPO_ROOT, "bridge/app.py")
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    def_idx = next(
        i for i, line in enumerate(lines) if "def _admit_contact(" in line
    )
    # Look at a window spanning a leading comment above the def and the
    # function's own docstring below it.
    window = "".join(lines[max(0, def_idx - 5): def_idx + 12])
    assert ANCHOR in window, (
        "bridge/app.py:_admit_contact has no INVARIANTS.md §5 citation in "
        "its leading comment or docstring."
    )
