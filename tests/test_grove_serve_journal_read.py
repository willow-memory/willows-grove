# b17: WGRV1 ΔΣ=42
"""Integration tests for grove_serve.py's GET /api/journal/recent (C11 RIGHT).

Same harness shape as tests/test_grove_serve_journal.py: starts the real
Starlette + uvicorn app on an ephemeral loopback port in a background
thread, hits the new route with stdlib urllib, patches the reader at the
module level so the wiring is exercised end-to-end without depending on
a live willow-mcp.
"""
from __future__ import annotations

import contextlib
import json
import os
import socket
import sys
import threading
import time
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _free_port() -> int:
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_until_up(url: str, timeout: float = 5.0) -> None:
    deadline = time.monotonic() + timeout
    last_err: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=0.5) as resp:
                if resp.status == 200:
                    return
        except (urllib.error.URLError, ConnectionError, OSError) as e:
            last_err = e
            time.sleep(0.05)
    raise RuntimeError(f"grove_serve did not come up at {url}: {last_err!r}")


class _ServerHarness:
    """Runs uvicorn in a background thread; shuts it down on exit."""

    def __init__(self) -> None:
        self.port = _free_port()
        self.host = "127.0.0.1"
        self._server = None
        self._thread: threading.Thread | None = None

    def __enter__(self) -> "_ServerHarness":
        import uvicorn

        import grove_serve

        config = uvicorn.Config(
            grove_serve.build_app(),
            host=self.host,
            port=self.port,
            log_level="error",
            access_log=False,
        )
        self._server = uvicorn.Server(config)
        self._thread = threading.Thread(target=self._server.run, daemon=True)
        self._thread.start()
        _wait_until_up(f"http://{self.host}:{self.port}/health")
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._server is not None:
            self._server.should_exit = True
        if self._thread is not None:
            self._thread.join(timeout=3.0)

    def url(self, path: str) -> str:
        return f"http://{self.host}:{self.port}{path}"


def _get_json(url: str) -> tuple[int, object]:
    req = urllib.request.Request(url, method="GET", headers={"accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw)
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8")
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, {"raw": raw}


class JournalRecentRouteTests(unittest.TestCase):
    def test_returns_list_from_reader(self) -> None:
        import grove_serve

        atoms = [
            {"id": "A", "ts": "t1", "sender": "watcher", "text": "one", "domain": "journal"},
            {"id": "B", "ts": "t0", "sender": "watcher", "text": "two", "domain": "journal"},
        ]

        def _fake_read(limit=50, since_id=None):  # noqa: ARG001
            return atoms

        with _ServerHarness() as srv, patch.object(
            grove_serve.journal_reader, "read_recent", _fake_read
        ):
            status, body = _get_json(srv.url("/api/journal/recent"))
        self.assertEqual(status, 200)
        self.assertIsInstance(body, list)
        self.assertEqual(body, atoms)

    def test_empty_reader_returns_empty_list_200(self) -> None:
        """D7: unreachable willow-mcp is a legible state, not an error."""
        import grove_serve

        with _ServerHarness() as srv, patch.object(
            grove_serve.journal_reader, "read_recent", lambda **_kw: []
        ):
            status, body = _get_json(srv.url("/api/journal/recent"))
        self.assertEqual(status, 200)
        self.assertEqual(body, [])

    def test_limit_capped_at_200(self) -> None:
        import grove_serve

        captured: dict = {}

        def _capture(limit=50, since_id=None):
            captured["limit"] = limit
            captured["since_id"] = since_id
            return []

        with _ServerHarness() as srv, patch.object(
            grove_serve.journal_reader, "read_recent", _capture
        ):
            _get_json(srv.url("/api/journal/recent?limit=1000"))
        self.assertEqual(captured["limit"], 200)

    def test_limit_default_when_missing(self) -> None:
        import grove_serve

        captured: dict = {}

        def _capture(limit=50, since_id=None):
            captured["limit"] = limit
            return []

        with _ServerHarness() as srv, patch.object(
            grove_serve.journal_reader, "read_recent", _capture
        ):
            _get_json(srv.url("/api/journal/recent"))
        self.assertEqual(captured["limit"], 50)

    def test_limit_invalid_falls_back_to_default(self) -> None:
        import grove_serve

        captured: dict = {}

        def _capture(limit=50, since_id=None):
            captured["limit"] = limit
            return []

        with _ServerHarness() as srv, patch.object(
            grove_serve.journal_reader, "read_recent", _capture
        ):
            _get_json(srv.url("/api/journal/recent?limit=notanumber"))
        self.assertEqual(captured["limit"], 50)

    def test_since_passed_through(self) -> None:
        import grove_serve

        captured: dict = {}

        def _capture(limit=50, since_id=None):
            captured["limit"] = limit
            captured["since_id"] = since_id
            return []

        with _ServerHarness() as srv, patch.object(
            grove_serve.journal_reader, "read_recent", _capture
        ):
            _get_json(srv.url("/api/journal/recent?since=ABCD1234&limit=10"))
        self.assertEqual(captured["limit"], 10)
        self.assertEqual(captured["since_id"], "ABCD1234")


if __name__ == "__main__":
    unittest.main()
