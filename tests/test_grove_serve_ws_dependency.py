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


class GroveServeRunOfflineBehaviorTests(unittest.TestCase):
    """Loki 1BA3415E F1: scripts/grove-serve-run must never exit before exec
    just because its own self-install failed. Under the unit's
    Restart=on-failure/RestartSec=2, an `exit 1` here means an offline box
    with a stale venv serves NOTHING (HTTP included) and retries pip every
    2 s — worse than the 404 stream it replaces. These tests run the REAL
    script (via `bash`, so the git executable bit is irrelevant) against a
    fake `python3` under $GROVE_VENV that lets each of grove-serve-run's
    checks succeed or fail independently and marks whether the final
    `exec "$PY" -m grove_serve` was actually reached.
    """

    _FAKE_PY = """\
#!/usr/bin/env python3
import sys

argv = sys.argv[1:]

if "-c" in argv:
    code = argv[argv.index("-c") + 1]
    if "import grove_serve" in code:
        sys.exit(0)
    if "import websockets" in code:
        sys.exit(0 if {ws_ok} else 1)
    if "import wsproto" in code:
        sys.exit(1)
    sys.exit(0)

if argv[:1] == ["-m"] and len(argv) > 1 and argv[1] == "pip":
    if {pip_ok}:
        sys.exit(0)
    sys.stderr.write("simulated: could not resolve pypi.org (offline)\\n")
    sys.exit(1)

if argv[:2] == ["-m", "grove_serve"]:
    print("EXEC_REACHED")
    sys.exit(0)

sys.exit(0)
"""

    def _run_script(self, *, ws_ok: bool, pip_ok: bool):
        import shutil
        import stat
        import subprocess
        import tempfile

        tmp_path = Path(tempfile.mkdtemp(prefix="grove-serve-run-test-"))
        try:
            venv_bin = tmp_path / "venv" / "bin"
            venv_bin.mkdir(parents=True)
            fake_py = venv_bin / "python3"
            fake_py.write_text(
                self._FAKE_PY.format(ws_ok=ws_ok, pip_ok=pip_ok), encoding="utf-8"
            )
            fake_py.chmod(fake_py.stat().st_mode | stat.S_IEXEC)

            script = Path(ROOT) / "scripts" / "grove-serve-run"
            env = dict(os.environ)
            env["GROVE_VENV"] = str(tmp_path / "venv")
            return subprocess.run(
                ["bash", str(script)],
                env=env,
                capture_output=True,
                text=True,
                timeout=10,
            )
        finally:
            shutil.rmtree(tmp_path, ignore_errors=True)

    def test_offline_install_failure_still_execs_the_server(self) -> None:
        result = self._run_script(ws_ok=False, pip_ok=False)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        # Reached exactly once — the script does not retry pip in-process;
        # a single EXEC_REACHED is the proof there is no in-script loop.
        self.assertEqual(result.stdout.count("EXEC_REACHED"), 1)
        self.assertIn("could not install websockets", result.stderr)

    def test_successful_install_execs_without_a_failure_warning(self) -> None:
        result = self._run_script(ws_ok=False, pip_ok=True)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("EXEC_REACHED", result.stdout)
        self.assertIn("websockets installed", result.stderr)
        self.assertNotIn("could not install", result.stderr)

    def test_library_already_present_skips_install_entirely(self) -> None:
        result = self._run_script(ws_ok=True, pip_ok=False)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("EXEC_REACHED", result.stdout)
        self.assertNotIn("installing websockets", result.stderr)
        self.assertNotIn("could not install", result.stderr)


if __name__ == "__main__":
    unittest.main()
