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


class DispatchRouteTests(unittest.TestCase):
    def test_dispatch_pa_returns_json_list(self) -> None:
        with _ServerHarness() as srv:
            with urllib.request.urlopen(srv.url("/api/dispatch?lens=pa"), timeout=2.0) as resp:
                self.assertEqual(resp.status, 200)
                body = json.loads(resp.read().decode("utf-8"))
        self.assertIsInstance(body, list)

    def test_dispatch_no_lens_returns_json_list(self) -> None:
        with _ServerHarness() as srv:
            with urllib.request.urlopen(srv.url("/api/dispatch"), timeout=2.0) as resp:
                self.assertEqual(resp.status, 200)
                body = json.loads(resp.read().decode("utf-8"))
        self.assertIsInstance(body, list)

    def test_dispatch_unknown_lens_falls_through_to_unfiltered(self) -> None:
        with _ServerHarness() as srv:
            with urllib.request.urlopen(srv.url("/api/dispatch?lens=nonsense"), timeout=2.0) as resp:
                self.assertEqual(resp.status, 200)
                body = json.loads(resp.read().decode("utf-8"))
        self.assertIsInstance(body, list)

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
