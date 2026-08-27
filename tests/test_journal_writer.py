# b17: WGRV1 ΔΣ=42
"""Tests for grove.journal_writer — degradation, HTTP, and empty-text guard.

Sync stdlib unittest, matching the other grove tests. No pytest-specific
constructs so the file lands green wherever the repo's own requirements
resolve.
"""
from __future__ import annotations

import io
import json
import logging
import os
import sys
import unittest
from unittest.mock import patch


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from grove import journal_writer  # noqa: E402
from grove.errors import Unreachable  # noqa: E402


class _FakeHTTPResponse:
    """Minimal urllib response stand-in for a mocked write."""

    def __init__(self, body: bytes) -> None:
        self._body = body

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> "_FakeHTTPResponse":
        return self

    def __exit__(self, *exc) -> None:
        return None


class WriteOperatorTurnTests(unittest.TestCase):
    def setUp(self) -> None:
        journal_writer._reset_log_once_for_tests()
        # Make sure a stray env doesn't accidentally reach a real willow-mcp.
        self._saved_url = os.environ.pop("WILLOW_MCP_URL", None)

    def tearDown(self) -> None:
        if self._saved_url is not None:
            os.environ["WILLOW_MCP_URL"] = self._saved_url

    def _force_no_import(self) -> patch:
        """Make attempt (a) fail — pretend willow_mcp is not importable."""
        return patch.object(journal_writer, "_try_import_write", return_value=None)

    # ---- guard ----
    def test_empty_text_raises_valueerror(self) -> None:
        with self.assertRaises(ValueError):
            journal_writer.write_operator_turn("")

    def test_non_string_text_raises_valueerror(self) -> None:
        with self.assertRaises(ValueError):
            journal_writer.write_operator_turn(None)  # type: ignore[arg-type]

    # ---- three-state: unreachable (INVARIANTS.md §1) ----
    def test_no_backend_raises_unreachable(self) -> None:
        with self._force_no_import():
            # WILLOW_MCP_URL unset from setUp — path (b) is skipped too.
            self.assertNotIn("WILLOW_MCP_URL", os.environ)
            with self.assertRaises(Unreachable) as ctx:
                journal_writer.write_operator_turn("hello")
        self.assertIn("not reachable", ctx.exception.reason)

    def test_no_backend_logs_once_across_many_calls(self) -> None:
        """One WARNING per process, not one per call (V-anti-noise)."""
        with self._force_no_import():
            with self.assertLogs(journal_writer.log, level="WARNING") as cap:
                # First call must emit exactly one WARNING; second must be silent.
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

    # ---- three-state: populated (successful write) ----
    # A successful write is always populated — see test_http_success_returns_atom_id
    # below (kept in the HTTP-path block).

    # ---- HTTP path (b) ----
    def test_http_success_returns_atom_id(self) -> None:
        os.environ["WILLOW_MCP_URL"] = "http://127.0.0.1:9999"
        body = json.dumps({"id": "AB12CD34", "domain": "journal"}).encode("utf-8")

        captured: dict[str, object] = {}

        def _fake_urlopen(req, timeout=None):  # noqa: ARG001
            captured["url"] = req.full_url
            captured["method"] = req.get_method()
            captured["body"] = req.data
            return _FakeHTTPResponse(body)

        with self._force_no_import(), patch.object(
            journal_writer.urllib.request, "urlopen", _fake_urlopen
        ):
            result = journal_writer.write_operator_turn("hello willow", sender="operator")

        self.assertTrue(result.get("ok"), result)
        self.assertEqual(result.get("id"), "AB12CD34")
        self.assertIn("ts", result)
        # Sanity: the request went to the right endpoint with the raw text.
        self.assertEqual(captured["url"], "http://127.0.0.1:9999/tools/kb_journal")
        self.assertEqual(captured["method"], "POST")
        payload = json.loads(captured["body"].decode("utf-8"))
        self.assertEqual(payload["content"], "hello willow")
        self.assertEqual(payload["source"], "operator")
        self.assertEqual(payload["app_id"], "willow-grove")

    def test_http_transport_error_raises_unreachable(self) -> None:
        """Transport error on the HTTP path → Unreachable (INVARIANTS.md §1)."""
        import urllib.error as _urlerr

        os.environ["WILLOW_MCP_URL"] = "http://127.0.0.1:9"

        def _boom(_req, timeout=None):
            raise _urlerr.URLError("connection refused")

        with self._force_no_import(), patch.object(
            journal_writer.urllib.request, "urlopen", _boom
        ):
            with self.assertRaises(Unreachable):
                journal_writer.write_operator_turn("hi")

    def test_verbatim_operator_text_is_preserved(self) -> None:
        """Operator words are load-bearing — no trim, no normalize (V5)."""
        os.environ["WILLOW_MCP_URL"] = "http://127.0.0.1:9999"
        body = json.dumps({"id": "XX99YY00", "domain": "journal"}).encode("utf-8")
        captured: dict[str, object] = {}

        def _fake_urlopen(req, timeout=None):  # noqa: ARG001
            captured["body"] = req.data
            return _FakeHTTPResponse(body)

        weird = "  Hello,\n\tWillow — here's *unedited* text.  "
        with self._force_no_import(), patch.object(
            journal_writer.urllib.request, "urlopen", _fake_urlopen
        ):
            result = journal_writer.write_operator_turn(weird)
        self.assertTrue(result.get("ok"))
        payload = json.loads(captured["body"].decode("utf-8"))
        self.assertEqual(payload["content"], weird)

    def test_reachable_but_error_raises_unreachable_with_reason(self) -> None:
        """Reached but rejected — INVARIANTS.md §1 treats this as unreachable
        (the source could not answer with the shape we asked for), and the
        endpoint layer surfaces the rejection reason to the operator."""
        os.environ["WILLOW_MCP_URL"] = "http://127.0.0.1:9999"
        body = json.dumps({"error": "schema_unusable"}).encode("utf-8")
        with self._force_no_import(), patch.object(
            journal_writer.urllib.request, "urlopen",
            lambda _r, timeout=None: _FakeHTTPResponse(body),
        ):
            with self.assertRaises(Unreachable) as ctx:
                journal_writer.write_operator_turn("hello")
        self.assertEqual(ctx.exception.reason, "schema_unusable")


if __name__ == "__main__":
    unittest.main()
