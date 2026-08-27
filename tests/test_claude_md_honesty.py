# b17: WGRV1  ΔΣ=42
"""CLAUDE.md honesty tests — INVARIANTS.md §6.

INVARIANTS.md §6 ("Manifests describe code, not aspirations") is the origin
case for the u2u honesty rule: ``u2u/packets.py:74-75`` writes plaintext
JSON onto a bare TCP socket, so no operator-facing surface may describe
u2u as an encrypted transport. README.md and ``safe-app-manifest.json``
already carry pinned honesty tests; CLAUDE.md is the third surface an
agent reads on cold-start and the previous rows there advertised u2u as
"encrypted DM transport", "Encrypted LAN transport", and "encrypted
human-to-human DMs".

These tests pin the corrected CLAUDE.md rows so a future edit that
re-introduces the encryption claim fails loudly. The full aspiration —
Gate 6 confidentiality — lives in ``docs/design/u2u-security-limits.md``
and is not the manifest's or CLAUDE.md's job to promise.

The module-absence tests below (Grove v0.9 PR 12, Loki finding #24) extend
the same honesty rule to CLAUDE.md: the withdrawn CLAUDE.md carried two
rows keyed on ``grove_standalone`` — the Entry-points row
``python3 -m grove_standalone`` (CLAUDE.md:53) and the Architecture row
``grove_standalone.py`` (CLAUDE.md:67). Neither module exists in the tree.
The rows must be gone and stay gone.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CLAUDE_MD_PATH = REPO_ROOT / "CLAUDE.md"

_U2U_TOKEN = re.compile(r"\bu2u\b", re.IGNORECASE)


def _load_claude_md() -> str:
    return CLAUDE_MD_PATH.read_text(encoding="utf-8")


def _u2u_lines(text: str) -> list[str]:
    """Return every line that names u2u (case-preserved).

    Any line that names u2u in CLAUDE.md is describing it as a system,
    transport, or capability — there is no incidental mention. A bare
    word-boundary match keeps the check exhaustive: if a line mentions
    u2u, it is in scope for the honesty rule.
    """
    return [line for line in text.splitlines() if _U2U_TOKEN.search(line)]


def test_claude_md_has_u2u_lines() -> None:
    """Sanity — CLAUDE.md must describe u2u for the honesty checks to bite."""
    lines = _u2u_lines(_load_claude_md())
    assert lines, "expected at least one line describing u2u in CLAUDE.md"


def test_u2u_lines_do_not_claim_encrypted() -> None:
    """No u2u line may carry 'encrypted' or 'Encrypted'.

    INVARIANTS.md §6: CLAUDE.md describes the code. u2u is signed, not
    encrypted — ``u2u/packets.py:74-75`` writes plaintext JSON over a bare
    TCP socket. The corrected aspiration (Gate 6) lives in
    ``docs/design/u2u-security-limits.md``, not in operator-facing rows.
    """
    offenders: list[str] = []
    for line in _u2u_lines(_load_claude_md()):
        if "encrypted" in line or "Encrypted" in line:
            offenders.append(line)
    assert not offenders, (
        "CLAUDE.md u2u line(s) still claim encryption — u2u is signed, not "
        "encrypted (see docs/design/u2u-security-limits.md and "
        f"INVARIANTS.md §6): {offenders!r}"
    )


def test_u2u_description_names_the_honest_property() -> None:
    """At least one u2u line must name the actual property.

    Either the line says 'signed' (the property u2u does provide) or it
    points readers at ``docs/design/u2u-security-limits.md`` (where the
    full truth lives). Without one of the two, a reader who consults only
    CLAUDE.md has no way to learn what u2u actually is.
    """
    lines = _u2u_lines(_load_claude_md())
    positive = [
        line
        for line in lines
        if "signed" in line.lower() or "u2u-security-limits.md" in line
    ]
    assert positive, (
        "no CLAUDE.md line describing u2u names 'signed' or references "
        "docs/design/u2u-security-limits.md — INVARIANTS.md §6 requires the "
        "honest property to be visible where u2u is described."
    )


# ---------------------------------------------------------------------------
# Module-absence phantoms — Grove v0.9 PR 12, Loki finding #24
# ---------------------------------------------------------------------------


def test_claude_md_does_not_reference_phantom_grove_standalone() -> None:
    """CLAUDE.md must not name the phantom ``grove_standalone`` module.

    Loki finding #24 (Grove v0.9 PR 12): the withdrawn CLAUDE.md carried
    two rows keyed on ``grove_standalone`` — the Entry-points row
    ``python3 -m grove_standalone`` (CLAUDE.md:53) and the Architecture
    row ``grove_standalone.py`` (CLAUDE.md:67). Neither module exists in
    the tree: no ``grove_standalone.py`` file, no ``grove_standalone/``
    package. INVARIANTS.md §6 forbids CLAUDE.md — the third cold-start
    surface — from describing code that does not ship.

    A bare substring check is deliberate: the phantom is the *name*
    ``grove_standalone``, and any row (entry-point or architecture) that
    revives it is an honesty violation.
    """
    claude_md = _load_claude_md()
    assert "grove_standalone" not in claude_md, (
        "CLAUDE.md still names the phantom `grove_standalone` module — "
        "no such file or package exists in the tree (Grove v0.9 PR 12, "
        "Loki finding #24; INVARIANTS.md §6)."
    )
