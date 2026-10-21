"""Grove reaches the canonical-bytes encodings through the one reach
(flatten-2 F7). The bytes are pinned in ``test_canon_goldens.py``; this holds
the reach: found, and said plainly when it is not. An unreachable one script is
neither a malformed packet nor a wrong signature (INVARIANTS.md §5), and it is
never a reason to hash a second way."""

from __future__ import annotations

from unittest import mock

import pytest

from grove import onescript_canon


def test_family_is_the_one_scripts_named_encoding():
    enc = onescript_canon.family("sorted_spaced_ascii")
    assert enc.version == "wgrv-canon-g/v1"
    assert enc({"b": 1, "a": "é"}) == '{"a": "\\u00e9", "b": 1}'


@pytest.fixture
def nowhere(tmp_path, monkeypatch):
    monkeypatch.delenv("WILLOW_BOT_ROOT", raising=False)
    monkeypatch.setenv("ONESCRIPT_HOME", str(tmp_path / "nowhere"))
    monkeypatch.setattr(onescript_canon, "_canon", None)


def test_unreachable_names_onescript_home(nowhere):
    with pytest.raises(onescript_canon.Unreachable) as e:
        onescript_canon.family("sorted_spaced_ascii")
    assert "ONESCRIPT_HOME" in str(e.value)


def test_packet_validate_says_unreachable_not_malformed(nowhere):
    from u2u.packets import Packet, PacketMalformed

    packet = {
        "header": {"sig": "00" * 64, "sent_at": 1, "expires_at": 2},
        "payload": {"a": 1},
    }
    with mock.patch("time.time", return_value=1.5):
        with pytest.raises(onescript_canon.Unreachable):
            Packet.validate(packet, "00" * 32)
    assert not issubclass(onescript_canon.Unreachable, PacketMalformed)


def test_frank_ledger_append_without_the_one_script_raises_ledger_write_failed(nowhere):
    import psycopg2

    import grove_db
    from grove.errors import LedgerWriteFailed

    class Cur:
        def execute(self, *a, **k):
            pass

        def fetchone(self):
            return None

    class Conn:
        def cursor(self):
            return Cur()

        def commit(self):
            pass

        def close(self):
            pass

    with mock.patch.object(psycopg2, "connect", lambda *a, **k: Conn()):
        with pytest.raises(LedgerWriteFailed) as e:
            grove_db._frank_ledger_append("grove_agent_message", {"a": 1})
    assert "ONESCRIPT_HOME" in str(e.value)
