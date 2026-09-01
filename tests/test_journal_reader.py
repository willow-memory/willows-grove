# b17: WGRV1 ΔΣ=42
"""Tests for grove.journal_reader — degradation, MCP transport, since_id, limit cap."""
from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from grove import journal_reader, willow_mcp_client
from grove.errors import Unreachable


class ReadRecentTests(unittest.TestCase):
    def setUp(self) -> None:
        journal_reader._reset_log_once_for_tests()
        willow_mcp_client._reset_client_for_tests()
        self._saved_url = os.environ.pop("WILLOW_MCP_URL", None)

    def tearDown(self) -> None:
        willow_mcp_client._reset_client_for_tests()
        if self._saved_url is not None:
            os.environ["WILLOW_MCP_URL"] = self._saved_url

    def _force_unreachable(self) -> patch:
        return patch.object(willow_mcp_client, "call_tool", return_value=None)

    def test_no_backend_raises_unreachable(self) -> None:
        with self._force_unreachable():
            self.assertNotIn("WILLOW_MCP_URL", os.environ)
            with self.assertRaises(Unreachable) as ctx:
                journal_reader.read_recent()
        self.assertIn("willow-mcp", ctx.exception.reason)

    def test_no_backend_logs_once_across_many_calls(self) -> None:
        with self._force_unreachable():
            with self.assertLogs(journal_reader.log, level="INFO") as cap:
                with self.assertRaises(Unreachable):
                    journal_reader.read_recent()
                first_count = len(cap.records)
                with self.assertRaises(Unreachable):
                    journal_reader.read_recent()
                with self.assertRaises(Unreachable):
                    journal_reader.read_recent()
                total_count = len(cap.records)
        self.assertEqual(first_count, 1, cap.output)
        self.assertEqual(total_count, 1, cap.output)

    def test_backend_reachable_but_no_atoms_returns_empty_list(self) -> None:
        with patch.object(willow_mcp_client, "call_tool", return_value=[]):
            result = journal_reader.read_recent()
        self.assertEqual(result, [])

    def test_mcp_success_returns_normalized_atoms(self) -> None:
        raw_atoms = [
            {
                "id": "AAA111",
                "content": "hello from the watcher",
                "source": "watcher",
                "tags": ["journal", "sender:watcher", "ts:2026-08-27T10:00:00Z"],
                "domain": "journal",
            },
            {
                "id": "BBB222",
                "content": "operator: help",
                "source": "operator",
                "tags": ["journal", "sender:operator", "ts:2026-08-27T09:00:00Z"],
                "domain": "journal",
            },
        ]
        captured: dict = {}

        def _fake_call(name, arguments):
            captured["name"] = name
            captured["arguments"] = arguments
            return raw_atoms

        with patch.object(willow_mcp_client, "call_tool", side_effect=_fake_call):
            result = journal_reader.read_recent(limit=10)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "AAA111")
        self.assertEqual(result[0]["text"], "hello from the watcher")
        self.assertEqual(result[0]["sender"], "watcher")
        self.assertEqual(result[0]["ts"], "2026-08-27T10:00:00Z")
        self.assertEqual(captured["name"], "kb_journal_read")
        self.assertEqual(captured["arguments"]["limit"], 10)
        self.assertEqual(captured["arguments"]["app_id"], "willow-grove")

    def test_mcp_transport_error_raises_unreachable(self) -> None:
        with self._force_unreachable(), self.assertRaises(Unreachable):
            journal_reader.read_recent()

    def test_mcp_bare_list_shape_accepted(self) -> None:
        raw = [
            {"id": "X1", "content": "one", "source": "watcher"},
            {"id": "X2", "content": "two", "source": "watcher"},
        ]
        with patch.object(willow_mcp_client, "call_tool", return_value=raw):
            result = journal_reader.read_recent()
        self.assertEqual([a["id"] for a in result], ["X1", "X2"])

    def test_since_id_filters_to_strictly_newer(self) -> None:
        raw = [
            {"id": "NEW", "content": "new one", "source": "watcher"},
            {"id": "OLD", "content": "old one", "source": "watcher"},
        ]
        captured: dict = {}

        def _fake_call(_name, arguments):
            captured["arguments"] = arguments
            return raw

        with patch.object(willow_mcp_client, "call_tool", side_effect=_fake_call):
            result = journal_reader.read_recent(since_id="OLD")

        self.assertEqual([a["id"] for a in result], ["NEW"])
        self.assertEqual(captured["arguments"]["since_id"], "OLD")

    def test_since_id_unknown_returns_all(self) -> None:
        raw = [
            {"id": "A", "content": "a", "source": "watcher"},
            {"id": "B", "content": "b", "source": "watcher"},
        ]
        with patch.object(willow_mcp_client, "call_tool", return_value=raw):
            result = journal_reader.read_recent(since_id="NEVER_SEEN")
        self.assertEqual([a["id"] for a in result], ["A", "B"])

    def test_limit_capped_at_200(self) -> None:
        captured: dict = {}

        def _fake_call(_name, arguments):
            captured["arguments"] = arguments
            return []

        with patch.object(willow_mcp_client, "call_tool", side_effect=_fake_call):
            journal_reader.read_recent(limit=10_000)

        self.assertEqual(captured["arguments"]["limit"], 200)

    def test_limit_bad_input_falls_back_to_default(self) -> None:
        captured: dict = {}

        def _fake_call(_name, arguments):
            captured["arguments"] = arguments
            return []

        with patch.object(willow_mcp_client, "call_tool", side_effect=_fake_call):
            journal_reader.read_recent(limit=-5)  # type: ignore[arg-type]
        self.assertEqual(captured["arguments"]["limit"], 50)

    def test_limit_trims_returned_atoms(self) -> None:
        raw = [{"id": f"A{i}", "content": str(i), "source": "watcher"} for i in range(5)]
        with patch.object(willow_mcp_client, "call_tool", return_value=raw):
            result = journal_reader.read_recent(limit=2)
        self.assertEqual(len(result), 2)

    def test_atom_text_preserved_verbatim(self) -> None:
        weird = "  Hello,\n\tWillow — *unedited*  "
        raw = [{"id": "V", "content": weird, "source": "watcher"}]
        with patch.object(willow_mcp_client, "call_tool", return_value=raw):
            result = journal_reader.read_recent()
        self.assertEqual(result[0]["text"], weird)

    def test_mcp_error_shape_raises_unreachable(self) -> None:
        with patch.object(
            willow_mcp_client, "call_tool", return_value={"error": "sim"}
        ), self.assertRaises(Unreachable) as ctx:
            journal_reader.read_recent()
        self.assertIn("sim", ctx.exception.reason)

    def test_mcp_empty_list_returns_empty_list(self) -> None:
        with patch.object(willow_mcp_client, "call_tool", return_value=[]):
            result = journal_reader.read_recent()
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
