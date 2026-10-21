"""Grove signs and verifies through the one script's ``sign.py`` (flatten-2 F14).

The bytes: RFC 8032 section 7.1 test 1, signed by ``Identity``. The verifier:
the pinned one refuses a non-canonical ``s`` and a small-order key as a wrong
signature (INVARIANTS.md §5 (b)), a wrong-length key as malformed, and an
unreachable one script as ``unreachable``, never as either. The identity FILE
is unchanged (raw hex private key, JSON, 0600). Every key here is a throwaway,
except the published RFC test vector.
"""

from __future__ import annotations

import json
import stat
from unittest import mock

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from grove import onescript_sign
from u2u.identity import Identity
from u2u.packets import Packet, PacketMalformed, PacketType

RFC_SECRET = "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"
RFC_PUBLIC = "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a"
RFC_SIG = (
    "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e06522490155"
    "5fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"
)


def _ident():
    return Identity(Ed25519PrivateKey.from_private_bytes(bytes.fromhex(RFC_SECRET)))


def _packet(ident=None):
    ident = ident or Identity(Ed25519PrivateKey.generate())
    with mock.patch("time.time", return_value=1700000000.0):
        return ident, Packet.build(
            PacketType.NOTE, "alice", "bob", {"a": 1}, ident, ttl=10**10
        )


def test_identity_bytes_are_rfc8032():
    ident = _ident()
    assert ident.public_key_hex == RFC_PUBLIC
    assert ident.sign(b"") == RFC_SIG
    assert ident.verify(b"", RFC_SIG, RFC_PUBLIC) is True
    assert ident.verify(b"x", RFC_SIG, RFC_PUBLIC) is False
    assert ident.verify(b"", RFC_SIG, "zz") is False  # not hex: wrong, as before
    assert (
        ident.verify(b"", RFC_SIG, "00" * 31) is False
    )  # wrong length: wrong, as before


def test_identity_file_is_unchanged(tmp_path):
    p = tmp_path / "id" / "identity.json"
    made = Identity.generate(p)
    assert stat.S_IMODE(p.stat().st_mode) == 0o600
    body = json.loads(p.read_text())
    assert (
        sorted(body) == ["private_key", "version"]
        and len(bytes.fromhex(body["private_key"])) == 32
    )
    assert Identity.load(p).public_key_hex == made.public_key_hex


def test_generate_takes_its_key_from_the_one_script_and_says_so(tmp_path):
    made = Identity.generate(tmp_path / "id.json")
    assert made.generated_by == "onescript"


def test_generate_with_no_one_script_falls_back_locally_and_says_so(tmp_path, nowhere):
    p = tmp_path / "id.json"
    made = Identity.generate(p)
    assert made.generated_by == "local"
    assert stat.S_IMODE(p.stat().st_mode) == 0o600
    body = json.loads(p.read_text())
    assert sorted(body) == ["private_key", "version"] and body["version"] == 1
    assert Identity.load(p).public_key_hex == made.public_key_hex


def test_non_canonical_s_is_a_wrong_signature_not_a_pass_or_a_raise():
    ident, pk = _packet()
    assert Packet.validate(json.loads(json.dumps(pk)), ident.public_key_hex) is True
    raw = bytes.fromhex(pk["header"]["sig"])
    s = int.from_bytes(raw[32:], "little") + onescript_sign.sign().L
    bad = json.loads(json.dumps(pk))
    bad["header"]["sig"] = (raw[:32] + s.to_bytes(32, "little")).hex()
    assert Packet.validate(bad, ident.public_key_hex) is False


@pytest.mark.parametrize(
    "key",
    [
        "01" + "00" * 31,  # the identity point
        "ec" + "ff" * 30 + "7f",  # order 2
        "ed" + "ff" * 30 + "7f",  # non-canonical (y = p)
    ],
)
def test_small_order_and_non_canonical_keys_are_a_wrong_signature(key):
    _, pk = _packet()
    assert Packet.validate(pk, key) is False


def test_wrong_length_key_is_malformed_as_before():
    _, pk = _packet()
    with pytest.raises(PacketMalformed, match="pubkey bytes rejected"):
        Packet.validate(pk, "00" * 31)


@pytest.fixture
def nowhere(tmp_path, monkeypatch):
    monkeypatch.delenv("WILLOW_BOT_ROOT", raising=False)
    monkeypatch.setenv("ONESCRIPT_HOME", str(tmp_path / "nowhere"))
    monkeypatch.setattr(onescript_sign, "_sign", None)


def test_unreachable_names_onescript_home(nowhere):
    with pytest.raises(onescript_sign.Unreachable) as e:
        onescript_sign.sign()
    assert "ONESCRIPT_HOME" in str(e.value)


def test_signing_and_verifying_say_unreachable_never_malformed_or_wrong(nowhere):
    ident = _ident()
    with pytest.raises(onescript_sign.Unreachable):
        ident.sign(b"m")
    with pytest.raises(onescript_sign.Unreachable):
        ident.verify(b"", RFC_SIG, RFC_PUBLIC)
    packet = {
        "header": {"sig": "00" * 64, "sent_at": 1, "expires_at": 2},
        "payload": {"a": 1},
    }
    with mock.patch("time.time", return_value=1.5):
        with pytest.raises(onescript_sign.Unreachable):
            Packet.validate(packet, "00" * 32)
    assert not issubclass(onescript_sign.Unreachable, PacketMalformed)
