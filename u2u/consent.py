# u2u/consent.py
# b17: U2UG1
"""U2U consent gate — allow/deny/pending logic.

Consent is an authorisation decision, not an authentication one. Callers MUST
have verified the packet signature before asking this gate anything: a
ConsentResult about an unauthenticated packet is a statement about a name the
attacker chose. `u2u.listener` enforces that ordering. See INVARIANTS.md §5
(trust order: signature → consent → dispatch).
"""

import time
from enum import Enum

from u2u.contacts import ContactStore
from u2u.packets import PacketType


class ConsentResult(str, Enum):
    ALLOW   = "allow"
    DENY    = "deny"
    PENDING = "pending"


_TYPE_TO_FIELD = {
    PacketType.NOTE:  "consent_note",
    PacketType.ASK:   "consent_ask",
    PacketType.ALERT: "consent_alert",
    PacketType.SHARE: "consent_share",
}

# How long an outstanding request stays answerable, in seconds.
DEFAULT_THREAD_TTL = 86_400


class ConsentGate:
    def __init__(self, store: ContactStore, thread_ttl: int = DEFAULT_THREAD_TTL):
        self._store = store
        self._thread_ttl = thread_ttl
        # thread_id -> (peer addr we asked, opened_at epoch seconds)
        self._threads: dict[str, tuple[str, float]] = {}

    def get_contact(self, addr: str):
        return self._store.get(addr)

    # ── outstanding requests ───────────────────────────────────────────────

    def open_thread(self, thread_id: str, addr: str) -> None:
        """Record that we sent `addr` a request carrying `thread_id`.

        Only a thread opened here can authorise an inbound REPLY, and only
        once. Call this whenever you send an ASK (or any packet you expect a
        REPLY to). Threads are in-memory and do not survive a restart — an
        unanswered request after a restart must be re-sent.
        """
        if thread_id:
            self._threads[thread_id] = (addr, time.time())

    def close_thread(self, thread_id: str) -> None:
        self._threads.pop(thread_id, None)

    def open_threads(self) -> list[str]:
        self._expire_threads()
        return list(self._threads)

    def _expire_threads(self) -> None:
        cutoff = time.time() - self._thread_ttl
        for tid in [t for t, (_, at) in self._threads.items() if at < cutoff]:
            del self._threads[tid]

    def _consume_thread(self, thread_id, addr: str) -> bool:
        """Claim `thread_id` for `addr`. True only if it was outstanding for
        that exact peer; the thread is consumed so a REPLY cannot be replayed."""
        if not thread_id or not isinstance(thread_id, str):
            return False
        self._expire_threads()
        entry = self._threads.get(thread_id)
        if entry is None or entry[0] != addr:
            return False
        del self._threads[thread_id]
        return True

    # ── the gate ──────────────────────────────────────────────────────

    def check(
        self,
        sender_addr: str,
        ptype: PacketType,
        thread_id: str | None = None,
    ) -> ConsentResult:
        """Decide what to do with an ALREADY-AUTHENTICATED packet.

        Not a pure predicate: a REPLY that matches an outstanding thread
        consumes that thread, so asking twice about the same REPLY yields
        ALLOW then DENY. That is the replay defence, not a bug.
        """
        contact = self._store.get(sender_addr)

        if contact is None:
            # An unknown peer may only ask to be introduced.
            return ConsentResult.PENDING if ptype == PacketType.KNOCK else ConsentResult.DENY

        if contact.blocked:
            return ConsentResult.DENY

        if ptype == PacketType.KNOCK:
            # Already a known, unblocked contact — a re-KNOCK is a no-op
            # handshake. It grants nothing on its own: the listener verified
            # the signature against the STORED key, so a KNOCK can never
            # introduce a new one.
            return ConsentResult.ALLOW

        if ptype == PacketType.REPLY:
            # A REPLY is only meaningful as an answer to something we asked.
            # Previously REPLY was allowed unconditionally, which let any
            # contact deliver arbitrary payloads with consent flags off simply
            # by labelling them REPLY.
            return (
                ConsentResult.ALLOW
                if self._consume_thread(thread_id, sender_addr)
                else ConsentResult.DENY
            )

        field = _TYPE_TO_FIELD.get(ptype)
        if field is None or not getattr(contact, field, False):
            return ConsentResult.DENY

        return ConsentResult.ALLOW
