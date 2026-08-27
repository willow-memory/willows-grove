# b17: WGRV1 ΔΣ=42
"""Integration tests for grove_serve.py's POST /api/nestor/decide (D11/V5).

Starts the real Starlette + uvicorn app on an ephemeral loopback port in a
background thread, then POSTs JSON with stdlib ``urllib``. Stdlib only.

The shared ``NestorClient`` singleton is reset around each test so mocks
land on a fresh instance. ``NestorClient.decision_check`` and
``.available`` are patched at the class level so we exercise route wiring
end-to-end without depending on a real ``nestor`` binary.
"""
from __future__ import annotations

import contextlib
import copy
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


def _post(url: str, body: bytes | None, *, content_type: str = "application/json") -> tuple[int, dict, bytes]:
    """POST; return (status, parsed body, raw bytes). No raise on 4xx/5xx."""
    req = urllib.request.Request(
        url,
        data=body if body is not None else b"",
        method="POST",
        headers={"content-type": content_type, "accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            raw = resp.read()
            try:
                return resp.status, json.loads(raw.decode("utf-8")), raw
            except json.JSONDecodeError:
                return resp.status, {"raw": raw.decode("utf-8", "replace")}, raw
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw.decode("utf-8")), raw
        except json.JSONDecodeError:
            return e.code, {"raw": raw.decode("utf-8", "replace")}, raw


def _post_json(url: str, body: dict | None) -> tuple[int, dict]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    status, parsed, _raw = _post(url, data)
    return status, parsed


class NestorDecideRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        # Reset the lazy singleton so each test starts from a fresh client
        # object that our patch.object can rebind.
        import grove_serve
        grove_serve._NESTOR_CLIENT = None

    # ---- 400 shape ----
    def test_empty_body_returns_400(self) -> None:
        with _ServerHarness() as srv:
            # Truly empty body (not even {}); server must degrade to 400.
            status, body, _raw = _post(srv.url("/api/nestor/decide"), None)
        self.assertEqual(status, 400)
        self.assertEqual(body.get("verdict"), "invalid")

    def test_missing_claim_returns_400(self) -> None:
        with _ServerHarness() as srv:
            status, body = _post_json(srv.url("/api/nestor/decide"), {"other": "x"})
        self.assertEqual(status, 400)
        self.assertEqual(body.get("verdict"), "invalid")

    def test_empty_claim_returns_400(self) -> None:
        with _ServerHarness() as srv:
            status, body = _post_json(srv.url("/api/nestor/decide"), {"claim": "   "})
        self.assertEqual(status, 400)
        self.assertEqual(body.get("verdict"), "invalid")

    # ---- 503 shape ----
    def test_binary_absent_returns_503(self) -> None:
        """Default on this box: nestor binary is not on PATH → 503."""
        import grove_serve
        # Force the client's availability probe to say "no", so the
        # response is 503 regardless of local $PATH state.
        with _ServerHarness() as srv, patch.object(
            grove_serve.NestorClient, "available", return_value=False
        ):
            status, body = _post_json(
                srv.url("/api/nestor/decide"), {"claim": "may we ship?"}
            )
        self.assertEqual(status, 503)
        self.assertEqual(body.get("verdict"), "unavailable")
        self.assertIn("reason", body)
        self.assertIn("nestor", body["reason"])

    # ---- 200 shapes ----
    def test_sealed_pair_response(self) -> None:
        import grove_serve
        pair = {
            "id": "PAIR-42",
            "question": "may we merge?",
            "answer": "yes, with the review clause",
            "sealed_at": "2026-08-27T00:00:00Z",
        }

        def _sealed(_self, question):
            self.assertEqual(question, "may we merge?")
            return {"verdict": "sealed", "pair": pair}

        with _ServerHarness() as srv, patch.object(
            grove_serve.NestorClient, "available", return_value=True
        ), patch.object(
            grove_serve.NestorClient, "decision_check", _sealed
        ):
            status, body = _post_json(
                srv.url("/api/nestor/decide"), {"claim": "may we merge?"}
            )
        self.assertEqual(status, 200)
        self.assertEqual(body.get("verdict"), "sealed")
        self.assertEqual(body.get("pair"), pair)

    def test_refusal_response_verbatim(self) -> None:
        """V5 — Nestor's refusal payload passes through byte-for-byte."""
        import grove_serve
        refusal = {
            "persona": "nestor",
            "act": "durable_rejection",
            # Deliberately weird whitespace and punctuation to prove no
            # cleanup happens along the way.
            "body": "  no.\n\nthis pair is  not  sealed — I will not affirm it.  ",
            "warrant_ids": ["W-1", "W-2"],
            "evidence_ids": ["E-9"],
            "seal_sig": "ed25519:abc123",
        }
        # Deep-copy for the round trip so the test isn't fooled by
        # mutating aliasing.
        payload_out = {"verdict": "refused", "refusal": copy.deepcopy(refusal)}

        def _refused(_self, _question):
            return payload_out

        with _ServerHarness() as srv, patch.object(
            grove_serve.NestorClient, "available", return_value=True
        ), patch.object(
            grove_serve.NestorClient, "decision_check", _refused
        ):
            status, body = _post_json(
                srv.url("/api/nestor/decide"), {"claim": "should we deploy?"}
            )
        self.assertEqual(status, 200)
        self.assertEqual(body.get("verdict"), "refused")
        # Byte-for-byte equality of the refusal dict (V5 discipline).
        self.assertEqual(body.get("refusal"), refusal)
        # And specifically the body string — no strip, no ellipsis.
        self.assertEqual(body["refusal"]["body"], refusal["body"])

    def test_pending_when_decision_check_returns_none(self) -> None:
        """D7 — absence of a decision is a valid state (200 pending)."""
        import grove_serve

        def _no_match(_self, _question):
            return None

        with _ServerHarness() as srv, patch.object(
            grove_serve.NestorClient, "available", return_value=True
        ), patch.object(
            grove_serve.NestorClient, "decision_check", _no_match
        ):
            status, body = _post_json(
                srv.url("/api/nestor/decide"), {"claim": "novel claim"}
            )
        self.assertEqual(status, 200)
        self.assertEqual(body.get("verdict"), "pending")
        self.assertIn("message", body)

    def test_client_is_reused_across_requests(self) -> None:
        """The lazy singleton: two requests hit the same client instance."""
        import grove_serve

        seen: list[int] = []

        def _no_match(self, _question):
            seen.append(id(self))
            return None

        with _ServerHarness() as srv, patch.object(
            grove_serve.NestorClient, "available", return_value=True
        ), patch.object(
            grove_serve.NestorClient, "decision_check", _no_match
        ):
            _post_json(srv.url("/api/nestor/decide"), {"claim": "one"})
            _post_json(srv.url("/api/nestor/decide"), {"claim": "two"})
        self.assertEqual(len(seen), 2)
        self.assertEqual(seen[0], seen[1], "expected one shared NestorClient")


if __name__ == "__main__":
    unittest.main()
