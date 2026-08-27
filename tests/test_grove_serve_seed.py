"""tests/test_grove_serve_seed.py — integration tests for /seed/ routes.
b17: WGRV1  ΔΣ=42

Runs the real Starlette + uvicorn app on an ephemeral loopback port and
hits ``GET /seed/`` (six-card landing), ``GET /seed/3`` (one movement),
and ``GET /seed/99`` (out-of-range → 404). Stdlib only.
"""
from __future__ import annotations

import contextlib
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


class GroveServeSeedIntegrationTests(unittest.TestCase):
    def test_seed_index_lists_six_movements(self) -> None:
        with _ServerHarness() as srv:
            with urllib.request.urlopen(srv.url("/seed/"), timeout=3.0) as resp:
                self.assertEqual(resp.status, 200)
                self.assertIn("text/html", resp.headers.get("content-type", ""))
                body = resp.read().decode("utf-8")
        for n in range(1, 7):
            self.assertIn(f'href="/seed/{n}"', body)
        # Return link to the main grove page.
        self.assertIn('href="/"', body)

    def test_seed_movement_three_returns_movement_page(self) -> None:
        from grove import seed_reader

        movements = seed_reader.load_movements()
        third_title = str(movements[2]["title"])

        with _ServerHarness() as srv:
            with urllib.request.urlopen(srv.url("/seed/3"), timeout=3.0) as resp:
                self.assertEqual(resp.status, 200)
                body = resp.read().decode("utf-8")

        # Third movement's title appears somewhere on its page.
        self.assertIn(third_title, body)
        # Prev/next nav references neighboring movements.
        self.assertIn('href="/seed/2"', body)
        self.assertIn('href="/seed/4"', body)
        self.assertIn('href="/seed/"', body)  # nav index link

    def test_seed_movement_out_of_range_returns_404(self) -> None:
        with _ServerHarness() as srv:
            with self.assertRaises(urllib.error.HTTPError) as ctx:
                urllib.request.urlopen(srv.url("/seed/99"), timeout=3.0)
        self.assertEqual(ctx.exception.code, 404)

    def test_seed_movement_zero_returns_404(self) -> None:
        with _ServerHarness() as srv:
            with self.assertRaises(urllib.error.HTTPError) as ctx:
                urllib.request.urlopen(srv.url("/seed/0"), timeout=3.0)
        self.assertEqual(ctx.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
