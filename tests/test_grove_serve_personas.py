# b17: WGRV1 ΔΣ=42
"""tests/test_grove_serve_personas.py — integration test for /api/personas.

Same harness shape as tests/test_grove_serve_dispatch.py: starts the real
Starlette + uvicorn app on an ephemeral loopback port in a background thread
and hits the new personas route with stdlib urllib.

Covers both D10 cases:

* No ``fleet_personas.json`` on disk anywhere in the candidate probe path
  (D7 — absence is a state): 200 + empty-personas envelope.
* A ``fleet-personas/v1`` file sitting at
  ``$WILLOW_HOME/willow-memory/willow/fleet_personas.json`` — 200 + parsed
  body matches what the reader would see.
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


_FIXTURE = {
    "schema": "fleet-personas/v1",
    "agents": [
        {
            "agent": "willow",
            "role": "primary",
            "trust": "flagship",
            "voice": {"register": "warm", "mandate": "the seat"},
            "visual": {
                "color": "#8FBC8F",
                "sigil": "\U0001F333",
                "color_token": "willow.green",
            },
            "canonical_file": "willow-memory/willow/personas/willow.md",
            "emission_fields": ["utterance", "state"],
        },
        {
            "agent": "loki",
            "role": "scout",
            "trust": "utility",
            "voice": {"register": "sharp"},
            "visual": {"color": "#7C1F3F", "sigil": "\U0001F98A"},
            "canonical_file": "personas/loki.md",
            "emission_fields": ["utterance"],
        },
    ],
}


class PersonasRouteTests(unittest.TestCase):
    """The two D10 shapes: missing sidecar file, and a real one."""

    def setUp(self) -> None:
        # Every test isolates HOME + WILLOW_HOME so the reader cannot see the
        # host's real registry file. persona_roster caches nothing between
        # calls, so the environ override is enough — no module reload needed.
        self._prior_env = {
            k: os.environ.get(k) for k in ("HOME", "WILLOW_HOME")
        }
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.addCleanup(self._restore_env)

    def _restore_env(self) -> None:
        for k, v in self._prior_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def _isolate_home(self) -> Path:
        fake_home = Path(self._tmp.name) / "no-home"
        fake_home.mkdir(exist_ok=True)
        os.environ["HOME"] = str(fake_home)
        os.environ.pop("WILLOW_HOME", None)
        # Reset the log-once flag so the D7 info log fires cleanly in a fresh
        # process, matching test_persona_roster.
        from grove import persona_roster as pr
        pr._logged_missing = False
        return fake_home

    def test_missing_registry_returns_empty_envelope(self) -> None:
        self._isolate_home()
        with _ServerHarness() as srv:
            with urllib.request.urlopen(srv.url("/api/personas"), timeout=2.0) as resp:
                self.assertEqual(resp.status, 200)
                body = json.loads(resp.read().decode("utf-8"))
        self.assertEqual(body.get("schema"), "fleet-personas/v1")
        self.assertEqual(body.get("personas"), {})

    def test_present_registry_is_returned_verbatim(self) -> None:
        fake_home = self._isolate_home()
        willow_home = fake_home  # WILLOW_HOME wins over ~ per the reader.
        target = willow_home / "willow-memory" / "willow" / "fleet_personas.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(_FIXTURE), encoding="utf-8")
        os.environ["WILLOW_HOME"] = str(willow_home)

        with _ServerHarness() as srv:
            with urllib.request.urlopen(srv.url("/api/personas"), timeout=2.0) as resp:
                self.assertEqual(resp.status, 200)
                body = json.loads(resp.read().decode("utf-8"))
        self.assertEqual(body.get("schema"), "fleet-personas/v1")
        agents = body.get("agents")
        self.assertIsInstance(agents, list)
        self.assertEqual([a["agent"] for a in agents], ["willow", "loki"])
        # The row round-trips exactly — the endpoint hands back what the file
        # holds; it does not reshape into the reader's PersonaRow dict.
        willow = agents[0]
        self.assertEqual(willow["visual"]["color"], "#8FBC8F")
        self.assertEqual(willow["voice"]["register"], "warm")


if __name__ == "__main__":
    unittest.main()
