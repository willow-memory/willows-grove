# b17: WGRV1 ΔΣ=42
"""tests/test_grove_serve_envelopes.py — integration for the /api/envelopes route.

Same harness shape as tests/test_grove_serve_dispatch.py: starts the real
Starlette + uvicorn app on an ephemeral loopback port in a background
thread and hits the new envelope route with stdlib urllib. Asserts the
P1 shape (``schema`` + ``envelopes``) survives the round-trip in both
degraded (no dir) and populated cases.
"""
from __future__ import annotations

import contextlib
import json
import os
import socket
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest import mock


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


class EnvelopesRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        # Reset envelope_reader log-once state so this suite is order-independent.
        from grove import envelope_reader as er
        er._logged_missing_dirs = False
        er._logged_missing_files = False
        er._logged_malformed = set()

        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.fake_home = Path(self.tmp.name) / "no-home"
        self.fake_home.mkdir()
        # Point WILLOW_HOME at a directory that has no `envelopes/` child, so
        # the degraded-case tests do not accidentally pick up the operator's
        # real fleet directories.
        self.empty_willow_home = Path(self.tmp.name) / "empty_willow_home"
        self.empty_willow_home.mkdir()

    def _env(self, willow_home: Path):
        return mock.patch.dict(
            os.environ,
            {"HOME": str(self.fake_home), "WILLOW_HOME": str(willow_home)},
            clear=False,
        )

    def _get(self, url: str) -> tuple[int, dict]:
        req = urllib.request.Request(url, method="GET", headers={"accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8")
            return e.code, json.loads(raw)

    def test_returns_unreachable_when_no_dir(self) -> None:
        """Three-state (INVARIANTS.md §1): no envelope dir → 503 + state=unreachable.
        Supersedes the older read where absence collapsed to an empty list."""
        with self._env(self.empty_willow_home):
            with _ServerHarness() as srv:
                status, body = self._get(srv.url("/api/envelopes"))
        self.assertEqual(status, 503)
        self.assertEqual(body.get("state"), "unreachable")
        self.assertIn("envelope directory", body.get("reason", ""))

    def test_returns_empty_when_dir_present_but_no_files(self) -> None:
        """Directory exists but empty → 200 + state=empty."""
        willow_home = Path(self.tmp.name) / "empty_dir_home"
        env_dir = willow_home / "envelopes"
        env_dir.mkdir(parents=True)
        with self._env(willow_home):
            with _ServerHarness() as srv:
                status, body = self._get(srv.url("/api/envelopes"))
        self.assertEqual(status, 200)
        self.assertEqual(body.get("state"), "empty")
        self.assertEqual(body.get("schema"), "envelope-registry/v1.1")
        self.assertEqual(body.get("envelopes"), [])

    def test_returns_populated_envelopes_from_willow_home(self) -> None:
        willow_home = Path(self.tmp.name) / "populated_willow_home"
        env_dir = willow_home / "envelopes"
        env_dir.mkdir(parents=True)
        (env_dir / "a.json").write_text(
            json.dumps(
                {
                    "schema": "envelope-registry/v1.1",
                    "envelopes": [
                        {"id": "env-a", "grantee": "kart", "attestation": "attested"},
                        {"id": "env-b", "grantee": "loki", "attestation": "attestation_missing"},
                    ],
                }
            ),
            encoding="utf-8",
        )

        with self._env(willow_home):
            with _ServerHarness() as srv:
                status, body = self._get(srv.url("/api/envelopes"))

        self.assertEqual(status, 200)
        self.assertEqual(body.get("state"), "populated")
        self.assertEqual(body.get("schema"), "envelope-registry/v1.1")
        ids = sorted(e["id"] for e in body.get("envelopes", []))
        self.assertEqual(ids, ["env-a", "env-b"])


if __name__ == "__main__":
    unittest.main()
