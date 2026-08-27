# tests/test_u2u_packet_validate_distinct.py
# b17: U2UPD1  ΔΣ=42
"""Packet.validate distinguishes three error paths — INVARIANTS.md §5.

Signature verification must not conflate error paths. A well-formed packet
whose signature is simply wrong (an attacker replay, a corrupt bit) is a
DIFFERENT condition from a packet whose inputs are so malformed that
verification could not even be attempted (a broken peer, a truncated
transport, a non-hex pubkey). Collapsing both to a single ``False`` —
as ``Packet.validate`` did behind a bare ``except Exception`` — makes the
listener's ``invalid sig`` log line ambiguous and hides wire-format
regressions behind attacker-shaped noise.

Three cases pinned here, one test each:

    (a) signature is valid                          -> returns True
    (b) inputs well-formed, signature invalid       -> returns False (no raise)
    (c) inputs malformed (verification unstartable) -> raises PacketMalformed

Against the unfixed tree (``u2u/packets.py`` with the bare
``except Exception: return False``) this module fails to import —
``PacketMalformed`` is not yet defined — and case (c) collapses to
``False`` rather than raising. Both are witnesses that the fix is missing.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from u2u.identity import Identity
from u2u.packets import Packet, PacketMalformed, PacketType


PEER = "peer@10.0.0.9:8550"
ME = "me@10.0.0.1:8550"


# ── fixtures ─────────────────────────────────────────────────


@pytest.fixture
def peer_id(tmp_path):
    return Identity.generate(tmp_path / "peer_id.json")


def _note(identity):
    return Packet.build(PacketType.NOTE, PEER, ME, {"body": "hi"}, identity)


def _flip_first_hex(hex_str: str) -> str:
    """Flip the first hex nibble of a hex string. Result is still valid hex
    (case b), only the underlying bytes have changed."""
    return ("1" if hex_str[0] == "0" else "0") + hex_str[1:]


# ── (a) valid signature returns True ──────────────────────────────────────


def test_valid_signature_returns_true(peer_id):
    """A well-formed packet signed by ``peer_id`` verifies against
    ``peer_id.public_key_hex``. This is case (a) — the only truthy return."""
    packet = _note(peer_id)
    result = Packet.validate(packet, peer_id.public_key_hex)
    assert result is True, "a valid signature must return exactly True"


# ── (b) inputs well-formed, signature invalid ── returns False, no raise ──────────


def test_inverted_signature_returns_false_without_raising(peer_id):
    """Flipping the first hex nibble of the signature keeps the sig valid hex
    (so verification can attempt), but the bytes no longer verify. Case (b):
    ``Packet.validate`` must return False and MUST NOT raise
    ``PacketMalformed`` — the listener logs this path as ``signature invalid``.
    """
    packet = _note(peer_id)
    packet["header"]["sig"] = _flip_first_hex(packet["header"]["sig"])

    try:
        result = Packet.validate(packet, peer_id.public_key_hex)
    except PacketMalformed as exc:
        pytest.fail(
            f"case (b) — a well-formed packet with a bad signature — "
            f"must return False, not raise PacketMalformed ({exc})"
        )
    assert result is False, "a tampered signature must return exactly False"


# ── (c) malformed inputs ── raises PacketMalformed ────────────────────────────


def test_malformed_pubkey_raises_packet_malformed(peer_id):
    """A non-hex verification key means ``bytes.fromhex`` fails before
    ``Ed25519PublicKey.from_public_bytes`` is even reached. Verification
    could not be attempted at all. Case (c): ``Packet.validate`` must raise
    ``PacketMalformed`` — the listener logs this path as ``packet malformed``.

    On the unfixed tree the bare ``except Exception: return False`` swallows
    the ``ValueError`` from ``bytes.fromhex`` and collapses this case into
    case (b). This assertion is the invariant witness.
    """
    packet = _note(peer_id)
    with pytest.raises(PacketMalformed):
        Packet.validate(packet, "zzzz-not-hex-at-all")


def test_malformed_pubkey_wrong_length_raises_packet_malformed(peer_id):
    """Companion witness: a syntactically-hex but wrong-length pubkey trips
    ``Ed25519PublicKey.from_public_bytes`` (expects 32 raw bytes). Same
    invariant — verification could not be attempted — same result: raise.
    """
    packet = _note(peer_id)
    with pytest.raises(PacketMalformed):
        # 4 hex chars = 2 bytes; Ed25519 requires 32.
        Packet.validate(packet, "aabb")
