# b17: WGRV1 ΔΣ=42
"""Tests for grove.journal_reader — degradation, HTTP, since_id, limit cap.

Sync stdlib unittest, matching the other grove tests. No pytest-specific
constructs so the file lands green wherever the repo's own requirements
resolve.
"""
from __future__ import annotations

import json
import os
import sys
import unittest
from unittest.mock import patch


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from grove import journal_reader  # noqa: E402


class _FakeHTTPResponse:
    """Minimal urllib response stand-in for a mocked read."""

    def __init__(self, body: bytes) -> None:
        self._body = body

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> "_FakeHTTPResponse":
        return self

    def __exit__(self, *exc) -> None:
        return None


def _atoms_payload(atoms: list) -> bytes:
    return json.dumps({"atoms": atoms}).encode("utf-8")


class ReadRecentTests(unittest.TestCase):
    def setUp(self) -> None:
        journal_reader._reset_log_once_for_tests()
        self._saved_url = os.environ.pop("WILLOW_MCP_URL", None)

    def tearDown(self) -> None:
        if self._saved_url is not None:
            os.environ["WILLOW_MCP_URL"] = self._saved_url

    def _force_no_import(self) -> patch:
        """Make attempt (a) fail — pretend the in-process reader is absent."""
        return patch.object(journal_reader, "_try_import_read", return_value=None)

    # ---- (c) degradation ----
    def test_no_backend_returns_empty_list(self) -> None:
        with self._force_no_import():
            self.assertNotIn("WILLOW_MCP_URL", os.environ)
            result = journal_reader.read_recent()
        self.assertEqual(result, [])

    def test_no_backend_logs_once_across_many_calls(self) -> None:
        """One INFO per process, not one per call (V-anti-noise)."""
        with self._force_no_import():
            with self.assertLogs(journal_reader.log, level="INFO") as cap:
                journal_reader.read_recent()
                first_count = len(cap.records)
                journal_reader.read_recent()
                journal_reader.read_recent()
                total_count = len(cap.records)
        self.assertEqual(first_count, 1, cap.output)
        self.assertEqual(total_count, 1, cap.output)

    # ---- (b) HTTP path ----
    def test_http_success_returns_normalized_atoms(self) -> None:
        os.environ["WILLOW_MCP_URL"] = "http://127.0.0.1:9999"
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
        body = _atoms_payload(raw_atoms)
        captured: dict = {}

        def _fake_urlopen(req, timeout=None):  # noqa: ARG001
            captured["url"] = req.full_url
            captured["method"] = req.get_method()
            return _FakeHTTPResponse(body)

        with self._force_no_import(), patch.object(
            journal_reader.urllib.request, "urlopen", _fake_urlopen
        ):
            result = journal_reader.read_recent(limit=10)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "AAA111")
        self.assertEqual(result[0]["text"], "hello from the watcher")
        self.assertEqual(result[0]["sender"], "watcher")
        self.assertEqual(result[0]["ts"], "2026-08-27T10:00:00Z")
        self.assertEqual(result[0]["domain"], "journal")
        # Sanity: request hit the right endpoint and carried the limit.
        self.assertIn("/tools/kb_journal_read?", captured["url"])
        self.assertIn("limit=10", captured["url"])
        self.assertIn("app_id=willow-grove", captured["url"])
        self.assertEqual(captured["method"], "GET")

    def test_http_transport_error_returns_empty(self) -> None:
        import urllib.error as _urlerr

        os.environ["WILLOW_MCP_URL"] = "http://127.0.0.1:9"

        def _boom(_req, timeout=None):
            raise _urlerr.URLError("connection refused")

        with self._force_no_import(), patch.object(
            journal_reader.urllib.request, "urlopen", _boom
        ):
            result = journal_reader.read_recent()
        self.assertEqual(result, [])

    def test_http_bare_list_shape_accepted(self) -> None:
        os.environ["WILLOW_MCP_URL"] = "http://127.0.0.1:9999"
        raw = [
            {"id": "X1", "content": "one", "source": "watcher"},
            {"id": "X2", "content": "two", "source": "watcher"},
        ]
        body = json.dumps(raw).encode("utf-8")

        with self._force_no_import(), patch.object(
            journal_reader.urllib.request, "urlopen",
            lambda _r, timeout=None: _FakeHTTPResponse(body),
        ):
            result = journal_reader.read_recent()
        self.assertEqual([a["id"] for a in result], ["X1", "X2"])

    # ---- since_id ----
    def test_since_id_filters_to_strictly_newer(self) -> None:
        os.environ["WILLOW_MCP_URL"] = "http://127.0.0.1:9999"
        # newest-first: NEW appears before OLD; passing OLD as since_id
        # should return only NEW.
        raw = [
            {"id": "NEW", "content": "new one", "source": "watcher"},
            {"id": "OLD", "content": "old one", "source": "watcher"},
        ]
        body = _atoms_payload(raw)
        captured: dict = {}

        def _fake_urlopen(req, timeout=None):  # noqa: ARG001
            captured["url"] = req.full_url
            return _FakeHTTPResponse(body)

        with self._force_no_import(), patch.object(
            journal_reader.urllib.request, "urlopen", _fake_urlopen
        ):
            result = journal_reader.read_recent(since_id="OLD")

        self.assertEqual([a["id"] for a in result], ["NEW"])
        # since_id also went out on the wire so a smart server could
        # filter server-side.
        self.assertIn("since_id=OLD", captured["url"])

    def test_since_id_unknown_returns_all(self) -> None:
        """Stale cursor (server rotation, page reload) shouldn't drop the read."""
        os.environ["WILLOW_MCP_URL"] = "http://127.0.0.1:9999"
        raw = [
            {"id": "A", "content": "a", "source": "watcher"},
            {"id": "B", "content": "b", "source": "watcher"},
        ]
        body = _atoms_payload(raw)
        with self._force_no_import(), patch.object(
            journal_reader.urllib.request, "urlopen",
            lambda _r, timeout=None: _FakeHTTPResponse(body),
        ):
            result = journal_reader.read_recent(since_id="NEVER_SEEN")
        self.assertEqual([a["id"] for a in result], ["A", "B"])

    # ---- limit ----
    def test_limit_capped_at_200(self) -> None:
        os.environ["WILLOW_MCP_URL"] = "http://127.0.0.1:9999"
        captured: dict = {}

        def _fake_urlopen(req, timeout=None):  # noqa: ARG001
            captured["url"] = req.full_url
            return _FakeHTTPResponse(_atoms_payload([]))

        with self._force_no_import(), patch.object(
            journal_reader.urllib.request, "urlopen", _fake_urlopen
        ):
            journal_reader.read_recent(limit=10_000)

        # The wire request carries the capped value, not the caller's 10_000.
        self.assertIn("limit=200", captured["url"])
        self.assertNotIn("limit=10000", captured["url"])

    def test_limit_bad_input_falls_back_to_default(self) -> None:
        os.environ["WILLOW_MCP_URL"] = "http://127.0.0.1:9999"
        captured: dict = {}

        def _fake_urlopen(req, timeout=None):  # noqa: ARG001
            captured["url"] = req.full_url
            return _FakeHTTPResponse(_atoms_payload([]))

        with self._force_no_import(), patch.object(
            journal_reader.urllib.request, "urlopen", _fake_urlopen
        ):
            journal_reader.read_recent(limit=-5)  # type: ignore[arg-type]
        self.assertIn("limit=50", captured["url"])

    def test_limit_trims_returned_atoms(self) -> None:
        os.environ["WILLOW_MCP_URL"] = "http://127.0.0.1:9999"
        raw = [{"id": f"A{i}", "content": str(i), "source": "watcher"} for i in range(5)]
        body = _atoms_payload(raw)
        with self._force_no_import(), patch.object(
            journal_reader.urllib.request, "urlopen",
            lambda _r, timeout=None: _FakeHTTPResponse(body),
        ):
            result = journal_reader.read_recent(limit=2)
        self.assertEqual(len(result), 2)

    # ---- verbatim discipline ----
    def test_atom_text_preserved_verbatim(self) -> None:
        os.environ["WILLOW_MCP_URL"] = "http://127.0.0.1:9999"
        weird = "  Hello,\n\tWillow — *unedited*  "
        raw = [{"id": "V", "content": weird, "source": "watcher"}]
        body = _atoms_payload(raw)
        with self._force_no_import(), patch.object(
            journal_reader.urllib.request, "urlopen",
            lambda _r, timeout=None: _FakeHTTPResponse(body),
        ):
            result = journal_reader.read_recent()
        self.assertEqual(result[0]["text"], weird)

    # ---- (a) direct-import path (simulated) ----
    def test_direct_import_path_when_present(self) -> None:
        """A willow_mcp.server with kb_journal_read reaches path (a)."""
        import types

        raw = [{"id": "IMP", "content": "in-process", "source": "watcher"}]

        def _fake_kb_journal_read(app_id, limit=50, since_id=None):  # noqa: ARG001
            return {"atoms": raw}

        fake_server = types.ModuleType("willow_mcp.server")
        fake_server.kb_journal_read = _fake_kb_journal_read  # type: ignore[attr-defined]
        fake_pkg = types.ModuleType("willow_mcp")
        fake_pkg.server = fake_server  # type: ignore[attr-defined]

        with patch.dict(sys.modules, {"willow_mcp": fake_pkg, "willow_mcp.server": fake_server}):
            result = journal_reader.read_recent()
        self.assertEqual([a["id"] for a in result], ["IMP"])
        self.assertEqual(result[0]["sender"], "watcher")

    def test_direct_import_absent_function_falls_through(self) -> None:
        """willow_mcp present but no kb_journal_read → no crash, falls to (b)/(c)."""
        import types

        fake_server = types.ModuleType("willow_mcp.server")  # no kb_journal_read attribute
        fake_pkg = types.ModuleType("willow_mcp")
        fake_pkg.server = fake_server  # type: ignore[attr-defined]

        with patch.dict(sys.modules, {"willow_mcp": fake_pkg, "willow_mcp.server": fake_server}):
            # No WILLOW_MCP_URL, so (b) is skipped and we land at (c) → [].
            result = journal_reader.read_recent()
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
