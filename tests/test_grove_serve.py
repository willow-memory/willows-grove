"""tests/test_grove_serve.py — integration tests for grove_serve.py.
b17: WGRV1  ΔΣ=42

Starts the real Starlette + uvicorn app on an ephemeral loopback port in a
background thread, then hits `/health` and `/` with stdlib `urllib`. Stdlib
only (no httpx/requests) so the test lands green anywhere the repo's own
requirements resolve.
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


class GroveServeIntegrationTests(unittest.TestCase):
    def test_health_returns_ok_true(self) -> None:
        with _ServerHarness() as srv:
            with urllib.request.urlopen(srv.url("/health"), timeout=2.0) as resp:
                self.assertEqual(resp.status, 200)
                body = json.loads(resp.read().decode("utf-8"))
        self.assertIs(body.get("ok"), True)
        self.assertIn("commit", body)
        self.assertIsInstance(body["commit"], str)
        self.assertGreater(len(body["commit"]), 0)

    def test_index_serves_proof_of_life_page(self) -> None:
        with _ServerHarness() as srv:
            with urllib.request.urlopen(srv.url("/"), timeout=2.0) as resp:
                self.assertEqual(resp.status, 200)
                html = resp.read().decode("utf-8")
        # Proof-of-life marker + the Postgres DB context in the footer.
        self.assertIn("the grove is here", html)
        self.assertIn("willow_20", html)


if __name__ == "__main__":
    unittest.main()
