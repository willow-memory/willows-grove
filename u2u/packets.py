# u2u/packets.py
# b17: U2UP1
"""U2U packet format — U2U-WIRE-1. Signed JSON, newline-delimited."""

import json
import time
from enum import Enum
from typing import Any

from u2u.identity import Identity


class PacketType(str, Enum):
    KNOCK = "KNOCK"
    NOTE  = "NOTE"
    ASK   = "ASK"
    REPLY = "REPLY"
    ALERT = "ALERT"
    SHARE = "SHARE"


class PacketError(Exception):
    pass


class PacketMalformed(PacketError):
    """Inputs to ``Packet.validate`` were so malformed that signature
    verification could not be attempted — e.g. missing header, non-hex
    signature or pubkey, wrong-length pubkey, non-JSON-serialisable payload.

    Distinct from a well-formed packet whose signature is simply wrong;
    that case returns ``False`` from ``validate``. See INVARIANTS.md §5:
    signature verification must not conflate error paths, so the listener
    can log ``signature invalid`` vs ``packet malformed`` distinctly and
    a broken peer is not indistinguishable from an attacker replaying a
    bad signature.
    """
    pass


class Packet:
    @staticmethod
    def build(
        ptype: PacketType,
        from_addr: str,
        to_addr: str,
        payload: dict[str, Any],
        identity: Identity,
        ttl: int = 86400,
        thread_id: str | None = None,
    ) -> dict:
        now = int(time.time())
        payload_json = json.dumps(payload, sort_keys=True)
        header = {
            "version": "u2u-1",
            "type": ptype.value,
            "from": from_addr,
            "to": to_addr,
            "sent_at": now,
            "expires_at": now + ttl,
            "thread_id": thread_id,
        }
        signing_input = (json.dumps(header, sort_keys=True) + payload_json).encode()
        header["sig"] = identity.sign(signing_input)
        return {"header": header, "payload": payload}

    @staticmethod
    def validate(packet: dict, sender_public_key_hex: str) -> bool:
        """Verify a packet's Ed25519 signature.

        INVARIANTS.md §5 forbids collapsing distinct error paths. Three cases:

            (a) signature is valid                          -> return True
            (b) inputs well-formed, signature invalid       -> return False
            (c) inputs malformed (verification unstartable) -> raise PacketMalformed

        An expired packet is a legitimate drop (well-formed, non-forensic)
        and returns ``False`` — not a raise.

        Callers MUST distinguish (b) from (c) in their logs; ``u2u/listener.py``
        catches ``PacketMalformed`` and logs ``packet malformed`` while ``False``
        continues to log ``signature invalid``.
        """
        # ── (c) preflight: packet shape ───────────────────────────────────────
        if not isinstance(packet, dict):
            raise PacketMalformed("packet is not a dict")
        header_in = packet.get("header")
        if not isinstance(header_in, dict):
            raise PacketMalformed("packet has no header dict")
        header = dict(header_in)
        if "sig" not in header:
            raise PacketMalformed("header has no sig")
        sig_hex = header.pop("sig")
        if not isinstance(sig_hex, str):
            raise PacketMalformed("sig is not a string")
        if "payload" not in packet:
            raise PacketMalformed("packet has no payload")

        # ── well-formed but expired → False (not a raise) ─────────────────────────
        now = int(time.time())
        if header.get("expires_at", 0) < now:
            return False

        # ── (c) preflight: pubkey and sig hex ──────────────────────────────────
        if not isinstance(sender_public_key_hex, str) or not sender_public_key_hex:
            raise PacketMalformed("verification key missing or not a string")
        try:
            pub_bytes = bytes.fromhex(sender_public_key_hex)
        except ValueError as e:
            raise PacketMalformed(f"verification key is not hex: {e}") from e
        try:
            sig_bytes = bytes.fromhex(sig_hex)
        except ValueError as e:
            raise PacketMalformed(f"sig is not hex: {e}") from e

        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        from cryptography.exceptions import InvalidSignature
        try:
            pub = Ed25519PublicKey.from_public_bytes(pub_bytes)
        except (ValueError, Exception) as e:
            # Ed25519 raises ValueError for wrong-length; some backends raise
            # UnsupportedAlgorithm. Either way, verification cannot be attempted.
            if isinstance(e, InvalidSignature):
                raise
            raise PacketMalformed(f"pubkey bytes rejected: {e}") from e

        try:
            payload_json = json.dumps(packet["payload"], sort_keys=True)
            signing_input = (json.dumps(header, sort_keys=True) + payload_json).encode()
        except (TypeError, ValueError) as e:
            raise PacketMalformed(f"packet not JSON-serialisable: {e}") from e

        try:
            pub.verify(sig_bytes, signing_input)
        except InvalidSignature:
            return False  # (b) well-formed, sig wrong
        return True  # (a)

    @staticmethod
    def serialize(packet: dict) -> bytes:
        return (json.dumps(packet, separators=(",", ":")) + "\n").encode()

    @staticmethod
    def deserialize(data: bytes) -> dict:
        try:
            return json.loads(data.strip())
        except json.JSONDecodeError as e:
            raise PacketError(f"invalid packet JSON: {e}") from e
