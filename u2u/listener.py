# u2u/listener.py
# b17: U2UL1
"""U2U TCP listener — asyncio server, port 8550 by default."""

import asyncio
import logging
from contextlib import asynccontextmanager

from u2u import dispatcher
from u2u.consent import ConsentGate, ConsentResult
from u2u.identity import Identity
from u2u.packets import Packet, PacketError, PacketMalformed, PacketType

log = logging.getLogger("u2u.listener")

DEFAULT_PORT = 8550
_MAX_PACKET_BYTES = 16_384


class U2UListener:
    def __init__(self, host: str, port: int, identity: Identity, consent: ConsentGate):
        self.host    = host
        self.port    = port
        self._ident  = identity
        self._consent = consent
        self._server  = None

    @asynccontextmanager
    async def serve(self):
        self._server = await asyncio.start_server(
            self._handle, self.host, self.port,
            limit=_MAX_PACKET_BYTES,
        )
        log.info("U2U listening on %s:%s", self.host, self.port)
        async with self._server:
            yield self

    async def _handle(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        peer = writer.get_extra_info("peername")
        try:
            raw = await asyncio.wait_for(reader.readline(), timeout=10.0)
            if len(raw) > _MAX_PACKET_BYTES:
                log.warning("oversized packet from %s — dropped", peer)
                return
            packet = Packet.deserialize(raw)
            await self._process(packet, peer)
        except (PacketError, asyncio.TimeoutError) as e:
            log.warning("bad packet from %s: %s", peer, e)
        finally:
            writer.close()

    def _verification_key(self, packet: dict, sender_addr: str, ptype: PacketType) -> str:
        """The ONLY key this packet is allowed to be checked against.

        A known contact is always verified against its stored key — never
        against a key the packet supplies. That is what makes wire-driven key
        rotation impossible: a KNOCK bearing a new key simply fails to verify
        and is dropped, rather than replacing the trusted one.

        An unknown peer may only introduce itself with a KNOCK, and that KNOCK
        must be self-verifying: signed by the very key in its own payload. That
        proves possession of the private half, nothing more — admitting the key
        still requires operator approval downstream.
        """
        contact = self._consent.get_contact(sender_addr)
        if contact is not None:
            return contact.public_key_hex
        if ptype == PacketType.KNOCK:
            payload = packet.get("payload")
            if isinstance(payload, dict):
                key = payload.get("public_key")
                if isinstance(key, str):
                    return key
        return ""

    async def _process(self, packet: dict, peer):
        header      = packet.get("header")
        if not isinstance(header, dict):
            log.warning("packet without header from %s — dropped", peer)
            return
        sender_addr = header.get("from", "")
        ptype_str   = header.get("type", "")

        try:
            ptype = PacketType(ptype_str)
        except ValueError:
            log.warning("unknown packet type %r from %s", ptype_str, peer)
            return

        # ── AUTHENTICATE FIRST ──────────────────────────────────────────────────
        # Nothing below this point may be decided from, or dispatched on,
        # unverified header data. Consent used to be evaluated here instead,
        # which meant an attacker-chosen "from" address selected the policy and
        # the PENDING branch handed an entirely unverified packet to handlers.
        #
        # INVARIANTS.md §5 additionally forbids collapsing the error paths of
        # verification. Packet.validate distinguishes three cases:
        #   True                  → signature valid
        #   False                 → well-formed, signature invalid
        #   raise PacketMalformed → inputs so malformed verification could
        #                           not even be attempted
        # Each is logged distinctly so a broken peer is not indistinguishable
        # from an attacker replaying a bad signature.
        key = self._verification_key(packet, sender_addr, ptype)
        if not key:
            log.warning(
                "no verification key for %s from %s — dropped",
                ptype_str, sender_addr,
            )
            return
        try:
            ok = Packet.validate(packet, key)
        except PacketMalformed as e:
            log.warning(
                "packet malformed for %s from %s — dropped: %s",
                ptype_str, sender_addr, e,
            )
            return
        if not ok:
            log.warning(
                "signature invalid for %s from %s — dropped",
                ptype_str, sender_addr,
            )
            return

        # ── THEN AUTHORISE ──────────────────────────────────────────────────────────
        result = self._consent.check(sender_addr, ptype, header.get("thread_id"))
        if result == ConsentResult.DENY:
            log.debug("denied %s from %s", ptype_str, sender_addr)
            if ptype == PacketType.NOTE:
                dispatcher.dispatch({
                    "header": {**header, "_denied": True},
                    "payload": {},
                })
            return
        if result == ConsentResult.PENDING:
            log.info("KNOCK pending approval from %s", sender_addr)
            dispatcher.dispatch({
                "header": {**header, "_pending": True},
                "payload": packet.get("payload", {}),
            })
            return

        dispatcher.dispatch(packet)
        log.info("dispatched %s from %s", ptype_str, sender_addr)
