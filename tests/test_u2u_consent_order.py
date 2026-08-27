# tests/test_u2u_consent_order.py
# b17: U2UO1  ΔΣ=42
"""Trust order — signature → consent → dispatch (INVARIANTS.md §5).

These tests exist as the invariant's named witness: every u2u packet has its
signature verified before consent is consulted; consent decisions never render
on unverified data. The order is signature → consent → dispatch, in exactly
that sequence.

Where `tests/test_u2u_trust.py` sweeps the whole matrix, this file pins the
invariant with the same names the code comments cite. Everything below fails
against the pre-fix code (CODE_REVIEW.md P0 "consent is checked before the
signature" and "consent is advisory, not enforced").
"""

import asyncio
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from u2u import dispatcher
from u2u.consent import ConsentGate, ConsentResult
from u2u.contacts import CONSENT_FIELDS, ContactStore
from u2u.identity import Identity
from u2u.listener import U2UListener
from u2u.packets import Packet, PacketType

PEER = "peer@10.0.0.9:8550"
ME = "me@10.0.0.1:8550"
ALL_TYPES = list(PacketType)


# ── fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def store(tmp_path):
    return ContactStore(tmp_path / "contacts.json")


@pytest.fixture
def gate(store):
    return ConsentGate(store)


@pytest.fixture
def peer_id(tmp_path):
    return Identity.generate(tmp_path / "peer_id.json")


@pytest.fixture
def other_id(tmp_path):
    return Identity.generate(tmp_path / "other_id.json")


@pytest.fixture
def my_id(tmp_path):
    return Identity.generate(tmp_path / "my_id.json")


@pytest.fixture
def dispatched():
    dispatcher.clear()
    seen: list[dict] = []
    for ptype in ALL_TYPES:
        dispatcher.register(ptype, seen.append)
    yield seen
    dispatcher.clear()


@pytest.fixture
def consent_calls(gate, monkeypatch):
    """Record every call to `ConsentGate.check`. Used to prove the check is
    NEVER reached when the signature is invalid — the ordering assertion."""
    calls: list[tuple] = []
    original = gate.check

    def spy(sender_addr, ptype, thread_id=None):
        calls.append((sender_addr, ptype, thread_id))
        return original(sender_addr, ptype, thread_id)

    monkeypatch.setattr(gate, "check", spy)
    return calls


@pytest.fixture
def listener(gate, my_id):
    return U2UListener(host="127.0.0.1", port=0, identity=my_id, consent=gate)


# ── helpers ───────────────────────────────────────────────────────────────────


def feed(listener, packet):
    asyncio.run(listener._process(packet, ("10.0.0.9", 40001)))


def build_knock(identity, from_addr=PEER, payload_key=None):
    key = payload_key if payload_key is not None else identity.public_key_hex
    return Packet.build(
        PacketType.KNOCK, from_addr, ME, {"public_key": key}, identity,
    )


def build_note(identity, from_addr=PEER):
    return Packet.build(
        PacketType.NOTE, from_addr, ME, {"body": "hi"}, identity,
    )


def build_reply(identity, thread_id, from_addr=PEER):
    return Packet.build(
        PacketType.REPLY, from_addr, ME, {"body": "answer"}, identity,
        thread_id=thread_id,
    )


def forge_sig(packet):
    sig = packet["header"]["sig"]
    packet["header"]["sig"] = ("1" if sig[0] == "0" else "0") + sig[1:]
    return packet


# ── 1. Bad signature: consent is NEVER consulted, handler NEVER called ────────


def test_bad_signature_never_consults_consent_or_dispatches(
    listener, store, dispatched, consent_calls, peer_id
):
    """The ordering assertion in its purest form.

    A packet with a valid header shape but a broken signature must:
      (a) never reach `dispatcher.dispatch`, and
      (b) never reach `ConsentGate.check`.

    Before the P0 fix consent was consulted first and PENDING dispatched an
    entirely unverified KNOCK — this test would have failed on (a) and (b).
    """
    store.add(PEER, peer_id.public_key_hex, name="known")
    forged = forge_sig(build_note(peer_id))

    feed(listener, forged)

    assert dispatched == [], "forged packet reached dispatcher.dispatch"
    assert consent_calls == [], (
        "ConsentGate.check was called on an unauthenticated packet — the "
        "authorisation gate saw attacker-chosen data before authentication"
    )


def test_pending_consent_does_not_dispatch_unverified_data(
    listener, store, dispatched, peer_id, other_id
):
    """PENDING was the specific dispatch hole named in CODE_REVIEW P0.

    An unknown peer sends a KNOCK whose signature does NOT match the payload
    key it carries. Consent for an unknown peer's KNOCK is PENDING — before
    the fix that branch handed the packet to handlers unchecked. The fix
    verifies against the payload key first: signature mismatch fails, packet
    is dropped, no PENDING dispatch happens.
    """
    # Sign with peer_id, but claim to bear other_id's key.
    packet = build_knock(peer_id, payload_key=other_id.public_key_hex)

    feed(listener, packet)

    assert dispatched == [], (
        "a KNOCK whose payload key does not match the signature was "
        "dispatched — an attacker could install an arbitrary trusted key"
    )
    assert store.get(PEER) is None


def test_knock_payload_key_mismatch_to_signature_dropped(
    listener, store, dispatched, peer_id, other_id
):
    """Same shape as above, stated as its own witness for the invariant.

    The KNOCK payload's `public_key` MUST verify against the sig on that same
    KNOCK. If they disagree, the packet is dropped before dispatch.
    """
    packet = build_knock(peer_id, payload_key=other_id.public_key_hex)
    feed(listener, packet)
    assert dispatched == []


# ── 2. update_key preserves state (the "silent trust reset" P0) ───────────────


def test_update_key_preserves_blocked(store, peer_id, other_id):
    """A key rotation must NOT clear the `blocked` flag.

    Before the fix, the bridge's "update key silently" branch called
    `contacts.add()`, which reconstructed the `Contact` dataclass with
    `blocked=False`. The blocked flag is the operator's veto over a contact;
    a key rotation must never touch it.
    """
    store.add(PEER, other_id.public_key_hex)
    store.block(PEER)

    assert store.update_key(
        PEER, peer_id.public_key_hex, require_confirmation=False
    ) is True

    assert store.get(PEER).blocked is True
    assert store.get(PEER).public_key_hex == peer_id.public_key_hex


def test_update_key_preserves_all_consent_flags(store, peer_id, other_id):
    """A key rotation must NOT re-grant (or revoke) any consent flag."""
    store.add(PEER, other_id.public_key_hex)
    # Grant every flag directly (NOT via set_consent — we're pinning the
    # rotation itself, not the setter).
    contact = store.get(PEER)
    for f in CONSENT_FIELDS:
        setattr(contact, f, True)
    store.save()

    assert store.update_key(
        PEER, peer_id.public_key_hex, require_confirmation=False
    ) is True

    after = store.get(PEER)
    for f in CONSENT_FIELDS:
        assert getattr(after, f) is True, f"{f} was reset by update_key()"


def test_update_key_refuses_without_confirmation(store, peer_id, other_id, caplog):
    """The default `require_confirmation=True` refuses and logs.

    `add()` remains the only path to create a new contact; `update_key()`
    is the only path to rotate an existing contact — and it defaults closed.
    """
    store.add(PEER, other_id.public_key_hex)

    with caplog.at_level("WARNING", logger="u2u.contacts"):
        assert store.update_key(PEER, peer_id.public_key_hex) is False

    assert store.get(PEER).public_key_hex == other_id.public_key_hex
    assert any(
        "REFUSED key rotation" in rec.message for rec in caplog.records
    ), "the refusal was not logged clearly"


# ── 3. REPLY correlation (CODE_REVIEW P0: consent is advisory) ────────────────


def test_reply_with_unknown_thread_id_denied(store, gate, peer_id):
    """A REPLY that does not correlate to an outstanding request is DENY.

    Before the fix REPLY returned ALLOW unconditionally, so any contact could
    deliver arbitrary payloads by labelling them REPLY — the specific defect
    called out in CODE_REVIEW.md "P0 — consent is advisory, not enforced".
    """
    store.add(PEER, peer_id.public_key_hex)
    # Grant every consent flag so DENY here can only come from correlation.
    contact = store.get(PEER)
    for f in CONSENT_FIELDS:
        setattr(contact, f, True)
    store.save()

    assert gate.check(PEER, PacketType.REPLY, "no-such-thread") == ConsentResult.DENY
    assert gate.check(PEER, PacketType.REPLY, None) == ConsentResult.DENY
    assert gate.check(PEER, PacketType.REPLY, "") == ConsentResult.DENY


def test_reply_with_registered_thread_id_allowed(store, gate, peer_id):
    store.add(PEER, peer_id.public_key_hex)
    gate.open_thread("thread-A", PEER)
    assert gate.check(PEER, PacketType.REPLY, "thread-A") == ConsentResult.ALLOW


def test_reply_thread_expires_after_ttl(store, peer_id):
    """A registered thread_id must not stay outstanding forever.

    The exact TTL is configurable; this pins the property that expiration
    happens. A negative TTL forces every open thread to already be past
    cutoff — asserting that expiration is enforced rather than best-effort.
    """
    gate = ConsentGate(store, thread_ttl=-1)
    store.add(PEER, peer_id.public_key_hex)
    gate.open_thread("thread-B", PEER)

    assert gate.check(PEER, PacketType.REPLY, "thread-B") == ConsentResult.DENY


# ── 4. End-to-end: the full order at the wire ─────────────────────────────────


def test_full_order_signature_then_consent_then_dispatch(
    listener, store, dispatched, consent_calls, peer_id
):
    """One green-path packet: everything runs in the right order and the
    handler sees the fully-authenticated, fully-authorised payload.
    """
    store.add(PEER, peer_id.public_key_hex)
    contact = store.get(PEER)
    contact.consent_note = True
    store.save()

    feed(listener, build_note(peer_id))

    # The consent gate WAS consulted — after signature verification passed.
    assert consent_calls == [(PEER, PacketType.NOTE, None)]
    # The dispatch happened — after both.
    assert len(dispatched) == 1
    assert dispatched[0]["header"]["type"] == "NOTE"
    assert dispatched[0]["payload"] == {"body": "hi"}
