# b17: WGRV1 ΔΣ=42
"""Tests for grove.journal_writer — degradation, MCP transport, empty-text guard."""
from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from grove import journal_writer, willow_mcp_client
from grove.errors import Unreachable


class WriteOperatorTurnTests(unittest.TestCase):
    def setUp(self) -> None:
        journal_writer._reset_log_once_for_tests()
        willow_mcp_client._reset_client_for_tests()
        self._saved_url = os.environ.pop("WILLOW_MCP_URL", None)

    def tearDown(self) -> None:
        willow_mcp_client._reset_client_for_tests()
        if self._saved_url is not None:
            os.environ["WILLOW_MCP_URL"] = self._saved_url

    def _force_unreachable(self) -> patch:
        return patch.object(willow_mcp_client, "call_tool", return_value=None)

    def test_empty_text_raises_valueerror(self) -> None:
        with self.assertRaises(ValueError):
            journal_writer.write_operator_turn("")

    def test_non_string_text_raises_valueerror(self) -> None:
        with self.assertRaises(ValueError):
            journal_writer.write_operator_turn(None)  # type: ignore[arg-type]

    def test_no_backend_raises_unreachable(self) -> None:
        with self._force_unreachable():
            self.assertNotIn("WILLOW_MCP_URL", os.environ)
            with self.assertRaises(Unreachable) as ctx:
                journal_writer.write_operator_turn("hello")
        self.assertIn("not reachable", ctx.exception.reason)

    def test_no_backend_logs_once_across_many_calls(self) -> None:
        with self._force_unreachable():
            with self.assertLogs(journal_writer.log, level="WARNING") as cap:
                with self.assertRaises(Unreachable):
                    journal_writer.write_operator_turn("first")
                first_count = len(cap.records)
                with self.assertRaises(Unreachable):
                    journal_writer.write_operator_turn("second")
                with self.assertRaises(Unreachable):
                    journal_writer.write_operator_turn("third")
                total_count = len(cap.records)
        self.assertEqual(first_count, 1, cap.output)
        self.assertEqual(total_count, 1, cap.output)

    def test_mcp_success_returns_atom_id(self) -> None:
        captured: dict[str, object] = {}

        def _fake_call(name, arguments):
            captured["name"] = name
            captured["arguments"] = arguments
            return {"id": "AB12CD34", "domain": "journal"}

        with patch.object(willow_mcp_client, "call_tool", side_effect=_fake_call):
            result = journal_writer.write_operator_turn("hello willow", sender="operator")

        self.assertTrue(result.get("ok"), result)
        self.assertEqual(result.get("id"), "AB12CD34")
        self.assertIn("ts", result)
        self.assertEqual(captured["name"], "kb_journal")
        args = captured["arguments"]
        self.assertEqual(args["content"], "hello willow")
        self.assertEqual(args["source"], "operator")
        self.assertEqual(args["app_id"], "willow-grove")

    def test_mcp_transport_error_raises_unreachable(self) -> None:
        with self._force_unreachable(), self.assertRaises(Unreachable):
            journal_writer.write_operator_turn("hi")

    def test_verbatim_operator_text_is_preserved(self) -> None:
        captured: dict[str, object] = {}
        weird = "  Hello,\n\tWillow — here's *unedited* text.  "

        def _fake_call(_name, arguments):
            captured["arguments"] = arguments
            return {"id": "XX99YY00", "domain": "journal"}

        with patch.object(willow_mcp_client, "call_tool", side_effect=_fake_call):
            result = journal_writer.write_operator_turn(weird)
        self.assertTrue(result.get("ok"))
        self.assertEqual(captured["arguments"]["content"], weird)

    def test_reachable_but_error_raises_unreachable_with_reason(self) -> None:
        with patch.object(
            willow_mcp_client, "call_tool", return_value={"error": "schema_unusable"}
        ), self.assertRaises(Unreachable) as ctx:
            journal_writer.write_operator_turn("hello")
        self.assertEqual(ctx.exception.reason, "schema_unusable")


if __name__ == "__main__":
    unittest.main()
