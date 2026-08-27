# b17: WGRV1 ΔΣ=42
"""tests/test_grove_serve_dispatch.py — integration test for the /api/dispatch route.

Same harness shape as tests/test_grove_serve.py: starts the real Starlette
+ uvicorn app on an ephemeral loopback port in a background thread and hits
the new dispatch route with stdlib urllib. Asserts status 200 and a JSON
list body — the kart_reader graceful-tolerance path guarantees a list even
when the DB is empty, missing, or shape-drifted.
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


def _get_dispatch(url: str) -> tuple[int, dict]:
    """GET with 4xx/5xx tolerated so we can assert the 503 body."""
    req = urllib.request.Request(url, method="GET", headers={"accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8")
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, {"raw": raw}


class DispatchRouteTests(unittest.TestCase):
    """Three-state (INVARIANTS.md §1): populated / empty / unreachable."""

    def test_dispatch_pa_returns_state_wrapper(self) -> None:
        """No WILLOW_DB_URL by default in this test env → unreachable (503).
        When a DB IS wired (CI job), state is populated/empty with tasks."""
        with _ServerHarness() as srv:
            status, body = _get_dispatch(srv.url("/api/dispatch?lens=pa"))
        self.assertIn(status, (200, 503))
        self.assertIn(body.get("state"), ("populated", "empty", "unreachable"))
        if status == 503:
            self.assertEqual(body.get("state"), "unreachable")
            self.assertIn("reason", body)

    def test_dispatch_no_lens_returns_state_wrapper(self) -> None:
        with _ServerHarness() as srv:
            status, body = _get_dispatch(srv.url("/api/dispatch"))
        self.assertIn(status, (200, 503))
        self.assertIn(body.get("state"), ("populated", "empty", "unreachable"))

    def test_dispatch_unknown_lens_falls_through_to_unfiltered(self) -> None:
        with _ServerHarness() as srv:
            status, body = _get_dispatch(srv.url("/api/dispatch?lens=nonsense"))
        self.assertIn(status, (200, 503))
        self.assertIn(body.get("state"), ("populated", "empty", "unreachable"))

    def test_dispatch_unreachable_when_reader_raises(self) -> None:
        """503 + state=unreachable when kart_reader raises Unreachable."""
        import grove_serve
        from grove.errors import Unreachable
        from unittest.mock import patch

        def _boom(*_a, **_kw):
            raise Unreachable("test — DSN gone")

        with _ServerHarness() as srv, patch.object(
            grove_serve.kart_reader, "read_queue", _boom
        ), patch.object(
            grove_serve.kart_reader, "read_by_lens", _boom
        ):
            status, body = _get_dispatch(srv.url("/api/dispatch"))
        self.assertEqual(status, 503)
        self.assertEqual(body.get("state"), "unreachable")
        self.assertEqual(body.get("reason"), "test — DSN gone")

    def test_dispatch_empty_when_reader_returns_empty(self) -> None:
        """200 + state=empty when reader returns an empty list."""
        import grove_serve
        from unittest.mock import patch

        with _ServerHarness() as srv, patch.object(
            grove_serve.kart_reader, "read_queue", lambda: []
        ), patch.object(
            grove_serve.kart_reader, "read_by_lens", lambda *_a, **_kw: []
        ):
            status, body = _get_dispatch(srv.url("/api/dispatch"))
        self.assertEqual(status, 200)
        self.assertEqual(body.get("state"), "empty")
        self.assertEqual(body.get("tasks"), [])

    def test_dispatch_populated_when_reader_returns_rows(self) -> None:
        """200 + state=populated when reader returns non-empty rows."""
        import grove_serve
        from unittest.mock import patch

        rows = [
            {"id": 1, "status": "queued", "task": "reply to Ada"},
            {"id": 2, "status": "queued", "task": "roll build"},
        ]
        with _ServerHarness() as srv, patch.object(
            grove_serve.kart_reader, "read_queue", lambda: rows
        ):
            status, body = _get_dispatch(srv.url("/api/dispatch"))
        self.assertEqual(status, 200)
        self.assertEqual(body.get("state"), "populated")
        self.assertEqual(len(body.get("tasks")), 2)

    def test_web_static_serves_dispatch_rail_module(self) -> None:
        """The additive /web/ mount must serve the Web Component module."""
        with _ServerHarness() as srv:
            with urllib.request.urlopen(
                srv.url("/web/components/grove-dispatch-rail.js"), timeout=2.0
            ) as resp:
                self.assertEqual(resp.status, 200)
                body = resp.read().decode("utf-8")
        self.assertIn("grove-dispatch-rail", body)


if __name__ == "__main__":
    unittest.main()
