"""Grove's two canonical-bytes sites, pinned byte for byte (flatten-2 F7).

``grove_db._frank_ledger_append`` and ``u2u.packets`` hash/sign
``json.dumps(..., sort_keys=True)`` (default separators, ASCII-escaped): the
one script's ``sorted_spaced_ascii`` family. The expected values were taken
from the code BEFORE it imported that family (D-e: bytes already persisted or
signed never change). Literals on purpose.
"""

from __future__ import annotations

from unittest import mock

import pytest

CASES = {
    "ascii": {"b": 1, "a": "x"},
    "nonascii": {"name": "héllo ☃ 日本", "k": "\U0001d11e", "e": ""},
    "nested": {"z": {"y": [1, 2, {"b": None, "a": True}], "x": ""}, "a": [], "n": -0.5},
    "empty": {},
}

# Ed25519 is deterministic: the signature over the signing input pins its bytes.
PACKET_SIG = {
    "ascii": "13b54b37ad62a3394d55efca28a7bba22e8a9b33f2a4f21187fb98dbcf204c1b1c82583fc7750878c0f5c25b9a8627f9cc268c4f7a82964efb5d52f752c85708",
    "nonascii": "1255c89243866d833187b724eb4d11e6e4dfbb9d6b5139a637e78e49031cacdc3326ce4e29e6c9ff3dd7997fbf871ceb54946c44986a388c235845af7f9fb701",
    "nested": "2722c36f47d1e3450315d3c66218f5c990faae1f4989a1f8ce2743649352f2ff0f33ff3980e260d9737dfefa4853dce8c1aee7191faf6503cb5e191b5f98a809",
    "empty": "91a1ff96a9bf7dc529d1e1249eb1b0b8144db6dfa0d08f82bd92238882ff1fe75a0725f660108c0eaf3f4f73ec5a68bca3c9e7cca55c9749a233302f7f5f310e",
}
# hash written for prev_hash "prevhash", event_type "grove_agent_message"
FRANK_HASH = {
    "ascii": "d2883fb41f76ecc90b7d4c5367ff9b0eded45a511bd66dbe4b9728a88886fa7d",
    "nonascii": "afc4d5c60da1a9ffbe406c034207a600d88e30af99e9b2bb2fe21e319f51f906",
    "nested": "99b4f90ca36681599c5fb64936d210be1fa242f5c8ff470851fe1e6c71bf8658",
    "empty": "ecfaa45d3e4ee98e51bf44c32bd7f982ef77af1ca82f0c0ba27b11b9e75ebebd",
}


@pytest.mark.parametrize("case", sorted(CASES))
def test_u2u_packet_signing_input_is_pinned(case):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    from u2u.identity import Identity
    from u2u.packets import Packet, PacketType

    ident = Identity(Ed25519PrivateKey.from_private_bytes(bytes(range(32))))
    with mock.patch("time.time", return_value=1700000000.0):
        pk = Packet.build(
            PacketType.NOTE, "alice☃", "bob", CASES[case], ident, ttl=60, thread_id="t é"
        )
        assert Packet.validate(pk, ident.public_key_hex)
    assert pk["header"]["sig"] == PACKET_SIG[case]


class _Cur:
    def __init__(self):
        self.calls = []

    def execute(self, sql, params=None):
        self.calls.append((sql, params))

    def fetchone(self):
        return ("prevhash",)


class _Conn:
    def __init__(self):
        self.c = _Cur()

    def cursor(self):
        return self.c

    def commit(self):
        pass

    def close(self):
        pass


@pytest.mark.parametrize("case", sorted(CASES))
def test_frank_ledger_hash_is_pinned(case):
    import psycopg2

    import grove_db

    conn = _Conn()
    with mock.patch.object(psycopg2, "connect", lambda *a, **kw: conn):
        grove_db._frank_ledger_append("grove_agent_message", CASES[case])
    inserts = [c for c in conn.c.calls if c[0].startswith("INSERT")]
    assert inserts[0][1][5] == FRANK_HASH[case]
