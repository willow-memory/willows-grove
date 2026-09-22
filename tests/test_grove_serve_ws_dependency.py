"""tests/test_grove_serve_ws_dependency.py — dispatch 452ED95B.

Measured 2026-09-22T06:29Z: `grove-serve.service` reloaded onto #81's
master; a harness Monitor's WS upgrade against a live `/events/{seat}` got
`HTTP 404`, then close 1006. Nothing in this repo declared `websockets` or
`wsproto`: uvicorn ships no WebSocket implementation of its own, so it
refused every upgrade before Starlette's route ever ran. Starlette's
`TestClient` serves WebSockets in-process and needs neither library, which
is exactly why the route's own 70-test suite was green while the live
socket 404'd — this file is the leg that closes that gap.

``EventsWsLibraryImportableTests`` is deliberately a test that CANNOT pass
without the fix landing all the way to the interpreter under test: it
asserts a real WebSocket library is importable, via uvicorn's own
resolution. Before `websockets` (or `wsproto`) is actually installed in
whatever venv runs this file, it fails — that is the point, not a bug in
the test. It is expected to still fail inside Kart's sandbox (network
isolated, no egress lease held by this seat to `pip install` it); it is
expected to pass once CI's `pip install -r requirements.txt` step picks up
the newly-declared dependency, and once `scripts/grove-serve-run` (or an
operator) installs it into the served page's own venv.
"""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from starlette.testclient import TestClient  # noqa: E402

import grove_serve  # noqa: E402


class EventsWsLibraryImportableTests(unittest.TestCase):
    """The gate: this must fail until a WS library is actually installed."""

    def test_uvicorn_has_a_websocket_implementation_to_upgrade_with(self) -> None:
        from uvicorn.protocols.websockets.auto import AutoWebSocketsProtocol

        self.assertIsNotNone(
            AutoWebSocketsProtocol,
            "no WebSocket library (websockets or wsproto) is importable — "
            "uvicorn will answer every /events/{seat} upgrade with a bare "
            "HTTP 404. pip install websockets (requirements.txt/pyproject.toml "
            "now declare it; this interpreter's venv has not installed it yet).",
        )

    def test_ws_library_available_matches_uvicorns_own_resolution(self) -> None:
        from uvicorn.protocols.websockets.auto import AutoWebSocketsProtocol

        self.assertEqual(
            grove_serve._ws_library_available(), AutoWebSocketsProtocol is not None
        )


class HealthEventsFieldTests(unittest.TestCase):
    """/health's `events` field — three-state, never a silent 404."""

    def _get_health(self) -> dict:
        with TestClient(grove_serve.build_app()) as c:
            resp = c.get("/health")
        self.assertEqual(resp.status_code, 200)
        return resp.json()

    def test_events_populated_when_ws_library_available(self) -> None:
        with patch.object(grove_serve, "_ws_library_available", lambda: True):
            body = self._get_health()
        self.assertEqual(body.get("events"), {"state": "populated"})
        self.assertIs(body.get("ok"), True)

    def test_events_unreachable_when_ws_library_missing(self) -> None:
        with patch.object(grove_serve, "_ws_library_available", lambda: False):
            body = self._get_health()
        self.assertEqual(
            body.get("events"),
            {"state": "unreachable", "reason": "no websocket library"},
        )
        # /health itself still answers ok=True — a missing WS library dims
        # one route, not the whole served page.
        self.assertIs(body.get("ok"), True)


class RunStartupHonestyTests(unittest.TestCase):
    """`run()` names the gap out loud rather than serving silent 404s."""

    def test_run_prints_warning_when_ws_library_missing(self) -> None:
        with (
            patch.object(grove_serve, "_ws_library_available", lambda: False),
            patch("uvicorn.run") as mock_run,
            patch("builtins.print") as mock_print,
        ):
            grove_serve.run(host="127.0.0.1", port=0)
        mock_run.assert_called_once()
        printed = " ".join(str(c.args[0]) for c in mock_print.call_args_list)
        self.assertIn("websocket", printed.lower())
        self.assertIn("404", printed)

    def test_run_does_not_warn_when_ws_library_available(self) -> None:
        with (
            patch.object(grove_serve, "_ws_library_available", lambda: True),
            patch("uvicorn.run") as mock_run,
            patch("builtins.print") as mock_print,
        ):
            grove_serve.run(host="127.0.0.1", port=0)
        mock_run.assert_called_once()
        printed = " ".join(str(c.args[0]) for c in mock_print.call_args_list)
        self.assertNotIn("websocket", printed.lower())


class GroveServeRunScriptTests(unittest.TestCase):
    """Static-content check on scripts/grove-serve-run — the launcher this
    repo ships (as opposed to CI's own `pip install -r requirements.txt`)
    installs/verifies the WS library on start, per the assignment."""

    def test_script_checks_for_and_installs_a_ws_library(self) -> None:
        script = (Path(ROOT) / "scripts" / "grove-serve-run").read_text(
            encoding="utf-8"
        )
        self.assertIn("import websockets", script)
        self.assertIn("import wsproto", script)
        self.assertIn("pip install", script)
        self.assertIn("websockets", script)


if __name__ == "__main__":
    unittest.main()
