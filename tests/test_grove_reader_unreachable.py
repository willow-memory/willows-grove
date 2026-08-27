# b17: WGRV1 ΔΣ=42
"""tests/test_grove_reader_unreachable.py — INVARIANTS.md §1 regression for grove_reader.

Loki B1 (Unreachable ≠ empty) audit: every reader in ``grove_reader.py``
MUST raise ``grove.errors.Unreachable`` when its Postgres source cannot be
reached — never collapse to a bare ``[]`` / ``{}`` / ``None``. See
``docs/INVARIANTS.md §1``.

Harness: monkeypatch ``grove_db.get_connection`` to return a ``_FakeConn``
whose every ``cursor().execute()`` raises ``psycopg2.OperationalError``.
Each targeted reader is invoked; every one must raise ``Unreachable``.

On the unfixed tree each call returns ``[]`` / ``{}`` / ``None`` from the
offending top-level ``except Exception`` block, so ``assertRaises`` fails
and this test is red. After the §1 fix (each of the 16 sites raises
``Unreachable``) this test goes green.

Stdlib unittest only — no live Postgres required.
"""
from __future__ import annotations

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import psycopg2  # noqa: E402

import grove_db  # noqa: E402
import grove_reader  # noqa: E402
from grove.errors import Unreachable  # noqa: E402


class _FakeCursor:
    """A cursor whose every ``execute`` raises ``OperationalError``.

    ``fetchall`` / ``fetchone`` return sentinel-empty values so that any
    reader that (incorrectly) swallowed the execute failure and fell
    through would still surface an empty result — which is exactly the
    §1 violation the tests are pinning against.
    """

    description = ()

    def execute(self, *args, **kwargs):  # noqa: D401 — mimic psycopg2 cursor API
        raise psycopg2.OperationalError("simulated postgres outage")

    def fetchall(self):
        return []

    def fetchone(self):
        return None

    def close(self):
        pass


class _FakeConn:
    def cursor(self):
        return _FakeCursor()

    def rollback(self):
        pass

    def commit(self):
        pass

    def close(self):
        pass


class GroveReaderUnreachableTests(unittest.TestCase):
    """Pin §1: every listed reader raises Unreachable when Postgres is down."""

    def setUp(self):
        self._orig_get = grove_db.get_connection
        self._orig_release = grove_db.release_connection
        grove_db.get_connection = lambda: _FakeConn()
        grove_db.release_connection = lambda conn: None

    def tearDown(self):
        grove_db.get_connection = self._orig_get
        grove_db.release_connection = self._orig_release

    # 16 targeted readers, one assertion each.

    def test_grove_messages_bus_addressed_to_raises_unreachable(self):
        with self.assertRaises(Unreachable):
            grove_reader.grove_messages_bus_addressed_to("alice")

    def test_grove_own_channel_since_raises_unreachable(self):
        with self.assertRaises(Unreachable):
            grove_reader.grove_own_channel_since("auto")

    def test_grove_member_roster_raises_unreachable(self):
        with self.assertRaises(Unreachable):
            grove_reader.grove_member_roster()

    def test_grove_agents_raises_unreachable(self):
        with self.assertRaises(Unreachable):
            grove_reader.grove_agents()

    def test_grove_latest_message_for_sender_raises_unreachable(self):
        with self.assertRaises(Unreachable):
            grove_reader.grove_latest_message_for_sender("alice")

    def test_grove_agent_fleet_rows_raises_unreachable(self):
        with self.assertRaises(Unreachable):
            grove_reader.grove_agent_fleet_rows()

    def test_coordinator_heartbeat_raises_unreachable(self):
        with self.assertRaises(Unreachable):
            grove_reader.coordinator_heartbeat()

    def test_grove_list_archived_channels_raises_unreachable(self):
        with self.assertRaises(Unreachable):
            grove_reader.grove_list_archived_channels()

    def test_grove_channels_raises_unreachable(self):
        with self.assertRaises(Unreachable):
            grove_reader.grove_channels()

    def test_grove_messages_raises_unreachable(self):
        with self.assertRaises(Unreachable):
            grove_reader.grove_messages("auto")

    def test_grove_attention_flagged_raises_unreachable(self):
        with self.assertRaises(Unreachable):
            grove_reader.grove_attention_flagged()

    def test_grove_messages_all_agents_raises_unreachable(self):
        with self.assertRaises(Unreachable):
            grove_reader.grove_messages_all_agents(frozenset(["alice"]))

    def test_grove_mentions_for_handles_raises_unreachable(self):
        with self.assertRaises(Unreachable):
            grove_reader.grove_mentions_for_handles(["alice"])

    def test_routing_decisions_willow_raises_unreachable(self):
        with self.assertRaises(Unreachable):
            grove_reader._routing_decisions_willow()

    def test_routing_decisions_public_raises_unreachable(self):
        with self.assertRaises(Unreachable):
            grove_reader._routing_decisions_public()

    def test_human_required_queue_raises_unreachable(self):
        with self.assertRaises(Unreachable):
            grove_reader.human_required_queue()


if __name__ == "__main__":
    unittest.main()
