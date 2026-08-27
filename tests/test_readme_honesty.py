# b17: WGRV1  ΔΣ=42
"""README-honesty tests — INVARIANTS.md §6.

The README's u2u description must match the code. The withdrawn wording
described u2u as an "Encrypted LAN transport" / "encrypted transport"; the
transport is signed but not encrypted (``u2u/packets.py:74-75`` — plaintext
JSON over TCP). These tests pin the corrected wording so a future edit that
re-introduces the encryption claim fails loudly.

The same honesty rule applies to ``grove_serve.py``. It was previously
described as a "LAN command server (HMAC-signed)" / "LAN HTTP command
server", but the module (`grove_serve.py` docstring) is a loopback-only
Starlette served-page skeleton bound to 127.0.0.1:8766 — no HMAC, no
command-server surface. The row must not carry those withdrawn claims.
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


def _grove_serve_row_lines(readme: str) -> list[str]:
    """Return the two markdown table rows that describe ``grove_serve.py``.

    Two rows are subject to the honesty rule:

    * the Entry-points table row keyed on ``python3 grove_serve.py``, and
    * the Architecture table row keyed on ``grove_serve.py`` (no ``python3``).

    Both are pipe-delimited table rows (start with ``|``); prose mentions
    (e.g. the Notes bullet on ``grove_serve.py``) are intentionally excluded
    — the finding is about capability claims made in the two capability
    tables, not about every incidental filename mention.
    """
    rows: list[str] = []
    for line in readme.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if "grove_serve.py" in line:
            rows.append(line)
    return rows


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


def test_grove_serve_rows_do_not_claim_hmac_or_command_server() -> None:
    """``grove_serve.py`` rows must not claim HMAC or command-server behavior.

    INVARIANTS.md §6: capability descriptions describe code. ``grove_serve.py``
    is a loopback-only Starlette served-page skeleton on 127.0.0.1:8766 (see
    its module docstring — ``DEFAULT_HOST = "127.0.0.1"``, ``DEFAULT_PORT =
    8766``, two placeholder routes). There is no HMAC in the module
    (`grep hmac grove_serve.py` returns zero matches) and there is no
    command-server surface. Both withdrawn phrasings — the ``HMAC`` claim on
    the Entry-points row and the ``command server`` capability label on both
    rows — must not reappear.

    We assert against the two table rows found by ``_grove_serve_row_lines``
    (Entry-points row keyed on ``python3 grove_serve.py``; Architecture row
    keyed on ``grove_serve.py``). Both rows must be present, and neither may
    contain the banned substrings.
    """
    readme = _load_readme()
    rows = _grove_serve_row_lines(readme)

    entry_rows = [line for line in rows if "python3 grove_serve.py" in line]
    arch_rows = [
        line for line in rows if "python3 grove_serve.py" not in line
    ]
    assert entry_rows, (
        "expected the Entry-points table row for `python3 grove_serve.py` "
        "in README.md"
    )
    assert arch_rows, (
        "expected the Architecture table row for `grove_serve.py` in "
        "README.md"
    )

    banned = ("HMAC", "command server")
    for line in rows:
        for phrase in banned:
            assert phrase not in line, (
                f"README.md grove_serve.py row still carries withdrawn "
                f"capability claim {phrase!r}: {line!r} — grove_serve.py is a "
                f"loopback-only served-page host on 127.0.0.1:8766, not a "
                f"command server, and there is no HMAC in the module."
            )
