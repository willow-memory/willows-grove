# b17: WGRV1 ΔΣ=42
"""Regression pin for Loki finding M8 (Grove v0.9 PR 12).

INVARIANTS.md §1 — reached-but-rejected over MCP must raise ``Unreachable``,
not collapse into ``[]``.
"""
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


class JournalReaderMcpErrorTests(unittest.TestCase):
    def setUp(self) -> None:
        journal_reader._reset_log_once_for_tests()
        willow_mcp_client._reset_client_for_tests()
        self._saved_url = os.environ.pop("WILLOW_MCP_URL", None)

    def tearDown(self) -> None:
        willow_mcp_client._reset_client_for_tests()
        if self._saved_url is not None:
            os.environ["WILLOW_MCP_URL"] = self._saved_url

    def test_mcp_error_shape_raises_unreachable(self) -> None:
        calls: list[dict] = []

        def _fake_call(name, arguments):
            calls.append({"name": name, "arguments": arguments})
            return {"error": "sim"}

        with patch.object(willow_mcp_client, "call_tool", side_effect=_fake_call):
            with self.assertRaises(Unreachable) as ctx:
                journal_reader.read_recent()

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["name"], "kb_journal_read")
        self.assertIn("sim", ctx.exception.reason)

    def test_mcp_empty_list_returns_empty_list(self) -> None:
        with patch.object(willow_mcp_client, "call_tool", return_value=[]):
            result = journal_reader.read_recent()
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
