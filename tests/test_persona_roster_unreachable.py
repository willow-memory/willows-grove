# b17: WGRV1 ΔΣ=42
"""Regression: schema-drifted fleet_personas.json must surface as Unreachable,
not as a raw ValueError bubbling up into a Starlette 500.

Loki findings #9 + #10 (PR 12/13) — INVARIANTS.md §1 says every reader
returns populated / empty / Unreachable, and every endpoint answers
200/populated, 200/empty, or 503/unreachable. There is no fourth
'crashed' state. A malformed or truncated fleet_personas.json on disk
must therefore map to the same 503 + state=unreachable envelope that
an absent file produces, not to a bare HTTP 500 with no state field.

Two tests pin this at the two layers the invariant covers:

* The reader layer: ``PersonaRoster.load()`` against a truncated JSON
  file raises ``grove.errors.Unreachable`` (not ``ValueError``).
* The endpoint layer: ``GET /api/personas`` served from a temp
  ``$WILLOW_HOME`` whose registry file is truncated JSON returns
  ``503`` with ``{\"state\": \"unreachable\", \"reason\": \"...\"}``.

stdlib only (unittest + uvicorn in a background thread) to match
tests/test_grove_serve_personas.py.
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

from grove import persona_roster as pr  # noqa: E402
from grove.errors import Unreachable  # noqa: E402


# Truncated but recognizably v1 JSON — the schema field is there, but the
# document does not parse. Same drift shape a half-written file would show.
_DRIFT_BYTES = '{"schema": "fleet-personas/v1", "agents": ['


class PersonaRosterInvalidJsonUnreachableTests(unittest.TestCase):
    """Reader layer — ``PersonaRoster.load()`` translates parse failure.

    The constructor keeps its schema-strict ValueError contract
    (tests/test_persona_roster.py::test_wrong_schema_id_raises_value_error
    pins that); it is ``load()`` — the classmethod every caller in
    grove_serve.py actually uses — that must map the drift case to the
    same Unreachable sentinel the absent-file path already raises.
    """

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.willow_home = Path(self.tmp.name) / "willow_home"
        target = self.willow_home / "willow-memory" / "willow" / "fleet_personas.json"
        target.parent.mkdir(parents=True)
        target.write_text(_DRIFT_BYTES, encoding="utf-8")
        self.registry_path = target

        # Isolate HOME so the ~/willow-memory and ~/.willow candidates cannot
        # accidentally match anything on the host running the test.
        self.fake_home = Path(self.tmp.name) / "no-home"
        self.fake_home.mkdir()

        # Reset both log-once flags before every test.
        pr._logged_missing = False
        if hasattr(pr, "_logged_drift"):
            pr._logged_drift = False

    def test_invalid_json_raises_unreachable_not_value_error(self) -> None:
        env = {"HOME": str(self.fake_home), "WILLOW_HOME": str(self.willow_home)}
        with mock.patch.dict(os.environ, env, clear=False):
            with self.assertRaises(Unreachable) as ctx:
                pr.PersonaRoster.load()
        # Reason names the file so an operator sees which registry drifted.
        self.assertIn("fleet_personas.json", ctx.exception.reason)


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
    """Same in-thread uvicorn harness shape as tests/test_grove_serve_personas.py."""

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


class PersonasEndpointDriftUnreachableTests(unittest.TestCase):
    """Endpoint layer — /api/personas against a drifted registry file.

    Before the fix, ``_personas`` only wraps its ``PersonaRoster.load()``
    call in ``try/except Unreachable``; a ValueError from the reader
    escapes and Starlette returns a plain 500 with no ``state`` field.
    After the fix, the reader raises Unreachable for the drift case and
    the same except-branch turns it into the 503 envelope the invariant
    requires.
    """

    def setUp(self) -> None:
        self._prior_env = {k: os.environ.get(k) for k in ("HOME", "WILLOW_HOME")}
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.addCleanup(self._restore_env)

    def _restore_env(self) -> None:
        for k, v in self._prior_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def _get(self, url: str) -> tuple[int, dict]:
        req = urllib.request.Request(
            url, method="GET", headers={"accept": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8")
            try:
                return e.code, json.loads(raw)
            except ValueError:
                # Starlette's default 500 page is HTML — record it so the
                # assertion failure message shows what actually came back.
                return e.code, {"_raw": raw[:200]}

    def test_drifted_registry_returns_503_state_unreachable(self) -> None:
        fake_home = Path(self._tmp.name) / "no-home"
        fake_home.mkdir()
        os.environ["HOME"] = str(fake_home)

        willow_home = Path(self._tmp.name) / "willow_home"
        target = willow_home / "willow-memory" / "willow" / "fleet_personas.json"
        target.parent.mkdir(parents=True)
        target.write_text(_DRIFT_BYTES, encoding="utf-8")
        os.environ["WILLOW_HOME"] = str(willow_home)

        # Reset log-once flags so the drift log fires cleanly.
        pr._logged_missing = False
        if hasattr(pr, "_logged_drift"):
            pr._logged_drift = False

        with _ServerHarness() as srv:
            status, body = self._get(srv.url("/api/personas"))

        self.assertEqual(
            status,
            503,
            f"expected 503 on drifted registry; got {status} body={body!r}",
        )
        self.assertEqual(body.get("state"), "unreachable")
        self.assertIn("fleet_personas.json", str(body.get("reason", "")))


if __name__ == "__main__":
    unittest.main()
