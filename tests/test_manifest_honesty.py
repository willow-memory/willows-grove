# b17: WGRV1  ΔΣ=42
"""Manifest-honesty tests — INVARIANTS.md §6.

INVARIANTS.md §6 ("Manifests describe code, not aspirations") requires every
capability described in ``safe-app-manifest.json`` to reflect a property the
code demonstrably has. The u2u transport signs (Ed25519) but does not encrypt
(``u2u/packets.py:74-75`` writes JSON onto a bare TCP socket, and the
``cryptography`` dependency is imported only for signing). The manifest must
therefore not claim confidentiality for ``dm_conversations``, and every
capability description containing the word "Encrypted" must sit next to a
disclaimer that names the limit.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "safe-app-manifest.json"


def _load_manifest() -> dict:
    with MANIFEST_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _find_stream(manifest: dict, stream_id: str) -> dict:
    for stream in manifest.get("data_streams", []):
        if stream.get("id") == stream_id:
            return stream
    raise AssertionError(f"data_stream {stream_id!r} not found in manifest")


def test_dm_conversations_names_the_limit() -> None:
    """dm_conversations description must state u2u is NOT encrypted.

    INVARIANTS.md §6: a manifest describes code. The transport is
    signed-not-encrypted; consumers reading the manifest must see that.
    """
    manifest = _load_manifest()
    dm = _find_stream(manifest, "dm_conversations")
    blob = f"{dm.get('purpose', '')} {dm.get('description', '')}"
    assert "NOT encrypted" in blob, (
        "dm_conversations must contain the phrase 'NOT encrypted' — "
        f"got purpose={dm.get('purpose')!r} description={dm.get('description')!r}"
    )


def test_dm_conversations_does_not_claim_end_to_end_encrypted() -> None:
    """The phrase 'End-to-end encrypted' must not appear for dm_conversations.

    INVARIANTS.md §6: the manifest is not the place for aspirations. Real
    encryption is a Gate 6 conversation (see docs/design/u2u-security-limits.md).
    """
    manifest = _load_manifest()
    dm = _find_stream(manifest, "dm_conversations")
    blob = f"{dm.get('purpose', '')} {dm.get('description', '')}"
    assert "End-to-end encrypted" not in blob, (
        "dm_conversations must not carry the withdrawn 'End-to-end encrypted' "
        "phrasing — see CODE_REVIEW.md P0"
    )


def test_no_bare_encrypted_claim_in_any_capability_description() -> None:
    """Every 'Encrypted' mention must sit next to a disclaimer.

    INVARIANTS.md §6: the word "Encrypted" alone claims a property. If any
    data_stream description contains it, a disclaimer ("NOT encrypted",
    "cleartext", or "Gate 6") must sit inside the same purpose+description
    blob so a reader cannot come away thinking encryption is a shipped
    property.
    """
    manifest = _load_manifest()
    for stream in manifest.get("data_streams", []):
        blob = f"{stream.get('purpose', '')} {stream.get('description', '')}"
        if "Encrypted" not in blob and "encrypt" not in blob:
            continue
        disclaimers = ("NOT encrypted", "not encrypted", "cleartext", "Gate 6")
        assert any(d in blob for d in disclaimers), (
            f"data_stream {stream.get('id')!r} mentions encryption without a "
            "disclaimer — INVARIANTS.md §6 requires the claim to match the code. "
            f"blob={blob!r}"
        )
