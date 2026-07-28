"""tests/test_u2u_trust.py — u2u trust layer: authenticate before you authorise.

b17: U2UT1  ΔΣ=42

Two properties are under test here, and both were violated:

1. AUTHENTICATION PRECEDES AUTHORISATION. The listener must verify a packet's
   Ed25519 signature before consulting consent, for every packet type. A packet
   that does not verify must never reach ``dispatcher.dispatch`` — not on the
   ALLOW path, not on the PENDING path, not as a ``_denied`` notification.

2. CONSENT IS ENFORCED, NOT ADVISORY. No packet type is allowed unconditionally,
   new contacts start with nothing granted, and a REPLY only lands if it answers
   an outstanding request.
"""

import asyncio
import dataclasses
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from u2u import dispatcher
from u2u.consent import ConsentGate, ConsentResult
from u2u.contacts import Contact, ContactStore
from u2u.identity import Identity
from u2u.listener import U2UListener
from u2u.packets import Packet, PacketType

ALL_TYPES = list(PacketType)
CONSENT_FIELDS = ("consent_note", "consent_ask", "consent_alert", "consent_share")

PEER = "attacker@10.0.0.9:8550"
ME = "me@10.0.0.1:8550"


# ── fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def store(tmp_path):
    return ContactStore(tmp_path / "contacts.json")


@pytest.fixture
def gate(store):
    return ConsentGate(store)


@pytest.fixture
def peer_id(tmp_path):
    """The identity the far end actually signs with."""
    return Identity.generate(tmp_path / "peer_id.json")


@pytest.fixture
def other_id(tmp_path):
    """An unrelated identity — used as 'the key we already trust'."""
    return Identity.generate(tmp_path / "other_id.json")


@pytest.fixture
def my_id(tmp_path):
    return Identity.generate(tmp_path / "my_id.json")


@pytest.fixture
def dispatched():
    """Capture everything handed to dispatcher.dispatch, for every type."""
    dispatcher.clear()
    seen = []

    def handler(packet, _seen=seen):
        _seen.append(packet)

    for ptype in ALL_TYPES:
        dispatcher.register(ptype, handler)
    yield seen
    dispatcher.clear()


@pytest.fixture
def listener(gate, my_id):
    return U2UListener(host="127.0.0.1", port=0, identity=my_id, consent=gate)


# ── helpers ───────────────────────────────────────────────────────────────────


def feed(listener, packet):
    """Drive one inbound packet through the listener's processing path."""
    asyncio.run(listener._process(packet, ("10.0.0.9", 40001)))


def build(ptype, identity, payload=None, thread_id=None, from_addr=PEER):
    if payload is None:
        payload = (
            {"public_key": identity.public_key_hex}
            if ptype == PacketType.KNOCK
            else {"subject": "", "body": "hello"}
        )
    return Packet.build(ptype, from_addr, ME, payload, identity, thread_id=thread_id)


def forge(packet):
    """Break the signature while leaving it well-formed hex of the right length."""
    sig = packet["header"]["sig"]
    packet["header"]["sig"] = ("1" if sig[0] == "0" else "0") + sig[1:]
    return packet


def grant_all(store, addr):
    # Deliberately NOT via ContactStore.set_consent: this helper underpins the
    # parametrised matrices, and those must fail against the pre-change code for
    # security reasons, not because a new API is missing.
    contact = store.get(addr)
    for f in CONSENT_FIELDS:
        setattr(contact, f, True)
    store.save()
    return contact


def make_peer_state(store, state, trusted_key):
    """Put `PEER` into the contact store in one of four states."""
    if state == "unknown":
        return None
    contact = store.add(PEER, trusted_key)
    if state == "known_all_on":
        grant_all(store, PEER)
    elif state == "blocked":
        grant_all(store, PEER)
        store.block(PEER)
    return contact


PEER_STATES = ["unknown", "known_all_off", "known_all_on", "blocked"]


# ── 1. Contact defaults are opt-IN ────────────────────────────────────────────


def test_contact_consent_defaults_are_all_false():
    """A contact with no consent arguments grants nothing.

    NOTE: ``Contact()`` with *no* arguments is a TypeError — ``addr`` and
    ``public_key_hex`` are mandatory, before and after this change, and
    deliberately kept that way. The property that matters is that every
    ``consent_*`` field DEFAULTS to False, asserted here both on the dataclass
    field defaults and on a constructed instance.
    """
    defaults = {
        f.name: f.default
        for f in dataclasses.fields(Contact)
        if f.name.startswith("consent_")
    }
    assert defaults == dict.fromkeys(CONSENT_FIELDS, False)

    contact = Contact(addr=PEER, public_key_hex="ab" * 32)
    for field in CONSENT_FIELDS:
        assert getattr(contact, field) is False, f"{field} defaults to True"
    assert contact.blocked is False


def test_consent_fields_constant_tracks_the_dataclass():
    """CONSENT_FIELDS drives set_consent's validation — it must not drift."""
    from u2u.contacts import CONSENT_FIELDS as declared

    actual = tuple(
        f.name for f in dataclasses.fields(Contact) if f.name.startswith("consent_")
    )
    assert tuple(declared) == actual == CONSENT_FIELDS


def test_newly_added_contact_grants_nothing(store, peer_id, gate):
    store.add(PEER, peer_id.public_key_hex)
    for ptype in (PacketType.NOTE, PacketType.ASK, PacketType.ALERT, PacketType.SHARE):
        assert gate.check(PEER, ptype) == ConsentResult.DENY


def test_set_consent_is_the_only_way_to_grant(store, gate, peer_id):
    store.add(PEER, peer_id.public_key_hex)
    assert gate.check(PEER, PacketType.NOTE) == ConsentResult.DENY

    assert store.set_consent(PEER, consent_note=True) is True

    assert gate.check(PEER, PacketType.NOTE) == ConsentResult.ALLOW
    # Granting one flag grants only that flag.
    assert gate.check(PEER, PacketType.ASK) == ConsentResult.DENY


def test_set_consent_rejects_unknown_flags(store, peer_id):
    store.add(PEER, peer_id.public_key_hex)
    with pytest.raises(ValueError):
        store.set_consent(PEER, consent_everything=True)


def test_set_consent_does_not_create_contacts(store):
    assert store.set_consent(PEER, consent_note=True) is False
    assert store.get(PEER) is None


def test_stored_consent_flags_survive_a_reload(store, tmp_path, peer_id):
    """Existing contacts.json files carry explicit flags — changing the
    dataclass defaults must not silently re-grade contacts already on disk."""
    store.add(PEER, peer_id.public_key_hex)
    store.set_consent(PEER, consent_note=True, consent_share=True)

    reloaded = ContactStore(tmp_path / "contacts.json").get(PEER)
    assert reloaded.consent_note is True
    assert reloaded.consent_share is True
    assert reloaded.consent_ask is False


# ── 2. A forged signature never reaches a handler ─────────────────────────────


@pytest.mark.parametrize("ptype", ALL_TYPES, ids=lambda p: p.value)
@pytest.mark.parametrize("state", PEER_STATES)
def test_forged_signature_never_dispatches(
    listener, store, dispatched, peer_id, other_id, ptype, state
):
    """Every packet type, every peer state: a bad signature is dropped silently.

    'Silently' includes the ``_denied`` NOTE notification — that too is a
    dispatch, and dispatching anything derived from an unauthenticated header
    hands attacker-controlled data to handlers.
    """
    # A known peer is trusted with `other_id`'s key; the packet is signed by
    # `peer_id` AND then has its signature broken.
    make_peer_state(store, state, other_id.public_key_hex)
    packet = forge(build(ptype, peer_id))

    feed(listener, packet)

    assert dispatched == [], (
        f"forged {ptype.value} from a {state} peer reached dispatcher.dispatch"
    )


def test_unsigned_knock_from_unknown_peer_cannot_inject_trust(
    listener, store, peer_id
):
    """The P0-A exploit, end to end.

    The bridge's KNOCK handler admits the key carried in the packet. Before this
    change a KNOCK from an unknown address was dispatched as PENDING with NO
    signature check at all, so a single unauthenticated TCP packet installed an
    attacker-chosen key as trusted.
    """
    dispatcher.clear()
    try:
        def admit(packet):
            # Mirrors bridge.app._grove_knock's admission behaviour.
            addr = packet["header"]["from"]
            key = packet.get("payload", {}).get("public_key", "")
            if key and store.get(addr) is None:
                store.add(addr, key)

        dispatcher.register(PacketType.KNOCK, admit)

        feed(listener, forge(build(PacketType.KNOCK, peer_id)))

        assert store.get(PEER) is None, (
            "an unverified KNOCK installed a public key in the contact store"
        )
    finally:
        dispatcher.clear()


def test_authentic_knock_from_unknown_peer_is_pending_not_allowed(
    listener, store, dispatched, peer_id
):
    """REGRESSION GUARD (passes before and after): a correctly self-signed KNOCK
    still needs operator approval — PENDING, never ALLOW — and the key it
    carries is not written to the contact store by the listener."""
    feed(listener, build(PacketType.KNOCK, peer_id))

    assert len(dispatched) == 1
    assert dispatched[0]["header"]["_pending"] is True
    assert store.get(PEER) is None


def test_denied_note_notification_requires_a_valid_signature(
    listener, store, dispatched, peer_id
):
    """The ``_denied`` UX signal survives — but only for authenticated packets."""
    store.add(PEER, peer_id.public_key_hex)  # consent_note defaults False

    feed(listener, build(PacketType.NOTE, peer_id))

    assert len(dispatched) == 1
    assert dispatched[0]["header"]["_denied"] is True
    assert dispatched[0]["payload"] == {}


# ── 3. Key rotation cannot happen over the wire ───────────────────────────────


def test_blocked_contact_knock_replay_leaves_block_and_key_intact(
    store, peer_id, other_id
):
    """Block a contact, then replay a KNOCK bearing a new key.

    ``ContactStore.add`` used to re-run the ``Contact(...)`` constructor over an
    existing address, resetting blocked to False and re-granting consent, which
    is exactly what the bridge's 'update key silently' branch did on a re-KNOCK.
    """
    trusted = other_id.public_key_hex
    store.add(PEER, trusted)
    grant_all(store, PEER)
    store.block(PEER)

    with pytest.raises(ValueError):
        store.add(PEER, peer_id.public_key_hex)

    contact = store.get(PEER)
    assert contact.blocked is True
    assert contact.public_key_hex == trusted


def test_blocked_contact_knock_replay_is_dropped_by_the_listener(
    listener, store, dispatched, peer_id, other_id
):
    """REGRESSION GUARD (passes before and after): the same replay at the wire.

    A KNOCK signed by a NEW key is verified against the STORED key, so it never
    verifies and never reaches a handler. This already held before the change —
    consent short-circuited blocked peers to DENY — but it held for the wrong
    reason, as an authorisation accident rather than an authentication result.
    Kept so the reordering cannot regress it."""
    trusted = other_id.public_key_hex
    store.add(PEER, trusted)
    store.block(PEER)

    feed(listener, build(PacketType.KNOCK, peer_id))  # self-signed, new key

    assert dispatched == []
    contact = store.get(PEER)
    assert contact.blocked is True
    assert contact.public_key_hex == trusted


def test_knock_with_new_key_from_active_contact_is_dropped(
    listener, store, dispatched, peer_id, other_id
):
    """REGRESSION GUARD (passes before and after): not just blocked contacts —
    an unblocked, fully-trusted contact's key cannot be replaced by a
    self-signed KNOCK either."""
    trusted = other_id.public_key_hex
    store.add(PEER, trusted)
    grant_all(store, PEER)

    feed(listener, build(PacketType.KNOCK, peer_id))

    assert dispatched == []
    assert store.get(PEER).public_key_hex == trusted


def test_update_key_mutates_only_the_key(store, peer_id, other_id):
    store.add(PEER, other_id.public_key_hex, name="peer")
    grant_all(store, PEER)
    store.block(PEER)
    before = store.get(PEER)
    added, name = before.added, before.name

    assert store.update_key(PEER, peer_id.public_key_hex) is True

    after = store.get(PEER)
    assert after.public_key_hex == peer_id.public_key_hex
    assert after.blocked is True
    assert all(getattr(after, f) is True for f in CONSENT_FIELDS)
    assert (after.added, after.name) == (added, name)


def test_update_key_does_not_create_contacts(store, peer_id):
    assert store.update_key(PEER, peer_id.public_key_hex) is False
    assert store.get(PEER) is None


def test_update_key_survives_a_reload(store, tmp_path, peer_id, other_id):
    store.add(PEER, other_id.public_key_hex)
    store.block(PEER)
    store.update_key(PEER, peer_id.public_key_hex)

    reloaded = ContactStore(tmp_path / "contacts.json").get(PEER)
    assert reloaded.public_key_hex == peer_id.public_key_hex
    assert reloaded.blocked is True


# ── 3b. The bridge's admission path ───────────────────────────────────────────


@pytest.fixture
def bridge(store):
    """A GroveMatrixBridge shell with only the state _admit_contact touches.

    __init__ opens a Matrix client and resolves a local IP; the admission logic
    needs neither, so the object is built without it.
    """
    from bridge.app import GroveMatrixBridge

    obj = object.__new__(GroveMatrixBridge)
    obj.contacts = store
    return obj


def test_bridge_admits_a_new_contact(bridge, store, peer_id):
    assert bridge._admit_contact(PEER, peer_id.public_key_hex) is True
    contact = store.get(PEER)
    assert contact.public_key_hex == peer_id.public_key_hex
    assert all(getattr(contact, f) is False for f in CONSENT_FIELDS)


def test_bridge_reknock_with_the_same_key_is_a_noop(bridge, store, peer_id):
    bridge._admit_contact(PEER, peer_id.public_key_hex)
    grant_all(store, PEER)

    assert bridge._admit_contact(PEER, peer_id.public_key_hex) is True

    contact = store.get(PEER)
    assert all(getattr(contact, f) is True for f in CONSENT_FIELDS)


def test_bridge_refuses_silent_key_rotation_on_reknock(
    bridge, store, peer_id, other_id
):
    """The 'update key silently' branch — the P0-A trust reset.

    A re-KNOCK from an active contact bearing a different key must change
    nothing: not the key, not blocked, not a single consent flag.
    """
    trusted = other_id.public_key_hex
    bridge._admit_contact(PEER, trusted)
    grant_all(store, PEER)
    store.block(PEER)

    assert bridge._admit_contact(PEER, peer_id.public_key_hex) is False

    contact = store.get(PEER)
    assert contact.public_key_hex == trusted
    assert contact.blocked is True
    assert all(getattr(contact, f) is True for f in CONSENT_FIELDS)


def test_bridge_ignores_a_knock_with_no_key(bridge, store):
    assert bridge._admit_contact(PEER, "") is False
    assert store.get(PEER) is None


# ── 4. The consent matrix ─────────────────────────────────────────────────────

# state -> {packet type -> expected result}. REPLY is DENY everywhere here
# because no request is outstanding; correlation is tested separately.
EXPECTED = {
    "unknown": {
        PacketType.KNOCK: ConsentResult.PENDING,
        PacketType.NOTE:  ConsentResult.DENY,
        PacketType.ASK:   ConsentResult.DENY,
        PacketType.REPLY: ConsentResult.DENY,
        PacketType.ALERT: ConsentResult.DENY,
        PacketType.SHARE: ConsentResult.DENY,
    },
    "known_all_off": {
        PacketType.KNOCK: ConsentResult.ALLOW,
        PacketType.NOTE:  ConsentResult.DENY,
        PacketType.ASK:   ConsentResult.DENY,
        PacketType.REPLY: ConsentResult.DENY,
        PacketType.ALERT: ConsentResult.DENY,
        PacketType.SHARE: ConsentResult.DENY,
    },
    "known_all_on": {
        PacketType.KNOCK: ConsentResult.ALLOW,
        PacketType.NOTE:  ConsentResult.ALLOW,
        PacketType.ASK:   ConsentResult.ALLOW,
        PacketType.REPLY: ConsentResult.DENY,
        PacketType.ALERT: ConsentResult.ALLOW,
        PacketType.SHARE: ConsentResult.ALLOW,
    },
    "blocked": dict.fromkeys(ALL_TYPES, ConsentResult.DENY),
}


@pytest.mark.parametrize("ptype", ALL_TYPES, ids=lambda p: p.value)
@pytest.mark.parametrize("state", PEER_STATES)
def test_consent_matrix(store, gate, other_id, state, ptype):
    make_peer_state(store, state, other_id.public_key_hex)
    assert gate.check(PEER, ptype) == EXPECTED[state][ptype]


# ── 5. REPLY must answer an outstanding request ───────────────────────────────


def test_reply_without_a_thread_is_denied(store, gate, other_id):
    make_peer_state(store, "known_all_on", other_id.public_key_hex)
    assert gate.check(PEER, PacketType.REPLY) == ConsentResult.DENY
    assert gate.check(PEER, PacketType.REPLY, "no-such-thread") == ConsentResult.DENY
    assert gate.check(PEER, PacketType.REPLY, None) == ConsentResult.DENY


def test_reply_to_an_outstanding_thread_is_allowed_exactly_once(
    store, gate, other_id
):
    make_peer_state(store, "known_all_on", other_id.public_key_hex)
    gate.open_thread("t-1", PEER)

    assert gate.check(PEER, PacketType.REPLY, "t-1") == ConsentResult.ALLOW
    # Replay of the same REPLY: the thread was consumed.
    assert gate.check(PEER, PacketType.REPLY, "t-1") == ConsentResult.DENY


def test_reply_thread_is_bound_to_the_peer_we_asked(store, gate, other_id):
    make_peer_state(store, "known_all_on", other_id.public_key_hex)
    gate.open_thread("t-2", "someone-else@10.0.0.5:8550")

    assert gate.check(PEER, PacketType.REPLY, "t-2") == ConsentResult.DENY
    assert "t-2" in gate.open_threads()  # not consumed by the wrong peer


def test_reply_with_all_consent_off_still_needs_a_thread(store, gate, other_id):
    """A REPLY label must not be a bypass for a contact granted nothing."""
    make_peer_state(store, "known_all_off", other_id.public_key_hex)
    gate.open_thread("t-3", PEER)
    assert gate.check(PEER, PacketType.REPLY, "t-3") == ConsentResult.ALLOW
    assert gate.check(PEER, PacketType.REPLY, "t-3") == ConsentResult.DENY


def test_blocked_peer_cannot_use_an_outstanding_thread(store, gate, other_id):
    make_peer_state(store, "blocked", other_id.public_key_hex)
    gate.open_thread("t-4", PEER)
    assert gate.check(PEER, PacketType.REPLY, "t-4") == ConsentResult.DENY


def test_reply_threads_expire(store, other_id):
    gate = ConsentGate(store, thread_ttl=-1)
    make_peer_state(store, "known_all_on", other_id.public_key_hex)
    gate.open_thread("t-5", PEER)
    assert gate.check(PEER, PacketType.REPLY, "t-5") == ConsentResult.DENY


def test_reply_over_the_wire_needs_both_signature_and_thread(
    listener, store, gate, dispatched, peer_id
):
    store.add(PEER, peer_id.public_key_hex)

    # Authentic REPLY, no outstanding thread -> dropped.
    feed(listener, build(PacketType.REPLY, peer_id, thread_id="t-9"))
    assert dispatched == []

    # Same packet once the request is outstanding -> delivered, then replay dies.
    gate.open_thread("t-9", PEER)
    packet = build(PacketType.REPLY, peer_id, thread_id="t-9")
    feed(listener, packet)
    assert len(dispatched) == 1
    feed(listener, packet)
    assert len(dispatched) == 1
