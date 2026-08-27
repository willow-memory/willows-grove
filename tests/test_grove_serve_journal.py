# b17: WGRV1 ΔΣ=42
"""Integration tests for grove_serve.py's POST /api/journal (C11 LEFT).

Starts the real Starlette + uvicorn app on an ephemeral loopback port in a
background thread, then POSTs JSON with stdlib `urllib`. Stdlib only.

The writer is patched at the module level (``grove_serve.journal_writer``)
so we exercise the route wiring end-to-end without depending on willow-mcp
availability.
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


def _post_json(url: str, body: dict | None) -> tuple[int, dict]:
    """POST JSON; return (status, parsed body). No raise on 4xx/5xx."""
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data if data is not None else b"",
        method="POST",
        headers={"content-type": "application/json", "accept": "application/json"},
    )
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


class JournalRouteTests(unittest.TestCase):
    def test_missing_text_returns_400(self) -> None:
        with _ServerHarness() as srv:
            status, body = _post_json(srv.url("/api/journal"), {"sender": "operator"})
        self.assertEqual(status, 400)
        self.assertFalse(body.get("ok"))
        self.assertIn("reason", body)

    def test_empty_text_returns_400(self) -> None:
        with _ServerHarness() as srv:
            status, body = _post_json(srv.url("/api/journal"), {"text": "   "})
        self.assertEqual(status, 400)
        self.assertFalse(body.get("ok"))

    def test_success_returns_200_with_atom_id(self) -> None:
        import grove_serve

        def _fake_write(text, *, sender="operator"):
            self.assertEqual(text, "hello willow")
            self.assertEqual(sender, "operator")
            return {"ok": True, "id": "ABCD1234", "ts": "2026-08-27T00:00:00Z"}

        with _ServerHarness() as srv, patch.object(
            grove_serve.journal_writer, "write_operator_turn", _fake_write
        ):
            status, body = _post_json(
                srv.url("/api/journal"),
                {"text": "hello willow", "sender": "operator"},
            )
        self.assertEqual(status, 200)
        self.assertTrue(body.get("ok"))
        self.assertEqual(body.get("id"), "ABCD1234")
        self.assertEqual(body.get("ts"), "2026-08-27T00:00:00Z")

    def test_writer_degrades_returns_503(self) -> None:
        import grove_serve

        def _degraded(_text, *, sender="operator"):  # noqa: ARG001
            return {"ok": False, "reason": "willow-mcp not reachable"}

        with _ServerHarness() as srv, patch.object(
            grove_serve.journal_writer, "write_operator_turn", _degraded
        ):
            status, body = _post_json(
                srv.url("/api/journal"),
                {"text": "hi"},
            )
        self.assertEqual(status, 503)
        self.assertFalse(body.get("ok"))
        self.assertEqual(body.get("reason"), "willow-mcp not reachable")

    def test_operator_text_reaches_writer_verbatim(self) -> None:
        """V5 discipline through the route: bytes at the writer == bytes at the request."""
        import grove_serve

        captured: dict[str, str] = {}

        def _cap(text, *, sender="operator"):
            captured["text"] = text
            captured["sender"] = sender
            return {"ok": True, "id": "Z", "ts": "t"}

        weird = "  \tunedited — with newlines\n\nand spaces.  "
        with _ServerHarness() as srv, patch.object(
            grove_serve.journal_writer, "write_operator_turn", _cap
        ):
            _post_json(srv.url("/api/journal"), {"text": weird, "sender": "operator"})
        self.assertEqual(captured["text"], weird)
        self.assertEqual(captured["sender"], "operator")


if __name__ == "__main__":
    unittest.main()
