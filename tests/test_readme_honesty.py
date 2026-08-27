# b17: WGRV1  ΔΣ=42
"""README-honesty tests — INVARIANTS.md §6.

The README's u2u description must match the code. The withdrawn wording
described u2u as an "Encrypted LAN transport" / "encrypted transport"; the
transport is signed but not encrypted (``u2u/packets.py:74-75`` — plaintext
JSON over TCP). These tests pin the corrected wording so a future edit that
re-introduces the encryption claim fails loudly.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
README_PATH = REPO_ROOT / "README.md"


def _load_readme() -> str:
    return README_PATH.read_text(encoding="utf-8")


def _u2u_row_lines(readme: str) -> list[str]:
    """Return every line that mentions ``u2u/`` (case-preserved).

    We check every mention rather than assuming a single table row: any line
    that names ``u2u/`` and describes it is subject to the honesty rule.
    """
    return [line for line in readme.splitlines() if "u2u/" in line]


def test_u2u_lines_do_not_claim_encrypted_transport() -> None:
    """Withdrawn phrasings must not reappear on any u2u/ row.

    INVARIANTS.md §6: the README describes code. u2u is not an encrypted
    transport; it is a signed one. See docs/design/u2u-security-limits.md.
    """
    lines = _u2u_row_lines(_load_readme())
    assert lines, "expected at least one line mentioning u2u/ in README.md"
    banned = ("encrypted transport", "Encrypted LAN transport")
    for line in lines:
        for phrase in banned:
            assert phrase not in line, (
                f"README.md u2u/ line still carries withdrawn phrasing {phrase!r}: "
                f"{line!r}"
            )


def test_u2u_readme_row_carries_corrected_phrasing() -> None:
    """The corrected u2u/ row must be present in README.md.

    Pins the exact honesty-corrected wording (see PR 7 of Grove v0.9). If a
    future edit rewrites this row, either it preserves the two load-bearing
    substrings below or this test fails and the author is forced to think
    about the encryption claim again.
    """
    readme = _load_readme()
    required_substrings = (
        "signed (Ed25519) human-to-human DMs",
        "cleartext on the LAN",
        "Encryption is planned for Gate 6",
    )
    for needle in required_substrings:
        assert needle in readme, (
            f"README.md is missing the corrected u2u/ substring {needle!r} — "
            "PR 7 of Grove v0.9 (INVARIANTS.md §6) requires it."
        )
