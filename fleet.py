"""
fleet.py — Grove FleetManager
b17: FLEET1  ΔΣ=42

Spawns fleet services on Grove open, terminates them on close.
Restart policy: silent ×2, alert callback on 3rd failure (once per service).
"""
import logging
import os
import subprocess
import threading
import time
from pathlib import Path
from typing import Callable

_VENV_PYTHON = Path.home() / ".willow-venv" / "bin" / "python3"
_SYS_PYTHON  = "/usr/bin/python3"
_AGENTS_BIN  = Path.home() / "agents" / "hanuman" / "bin"
_GROVE_DIR   = Path(__file__).parent
_PY          = str(_VENV_PYTHON) if _VENV_PYTHON.exists() else _SYS_PYTHON
_LOG_FILE    = Path.home() / ".willow" / "fleet.log"
_PID_FILE    = Path.home() / ".willow" / "grove.pid"

logging.basicConfig(
    filename=_LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s fleet: %(message)s",
)
_log = logging.getLogger("fleet")

# corpus_watcher is intentionally excluded from the automatic fleet.
# Governance note in corpus-watcher.py: "Must be started by human action only."
# It watches ~/  via inotify and is resource-heavy. Enable via Grove Settings.
_SERVICES: dict[str, dict] = {
    "grove_serve": {
        "cmd": [_PY, str(_GROVE_DIR / "grove_serve.py"), "--host", "0.0.0.0", "--port", "7777"],
        "cwd": str(_GROVE_DIR),
        "env": {"WILLOW_PG_DB": "willow_19", "WILLOW_PG_USER": os.environ.get("USER", "")},
    },
    "journal_responder": {
        "cmd": [_SYS_PYTHON, str(_AGENTS_BIN / "journal_responder.py")],
        "cwd": str(_AGENTS_BIN),
        "env": {"JANE_MODEL": "yggdrasil:v9"},
    },
    "journal_watcher": {
        "cmd": [_SYS_PYTHON, str(_AGENTS_BIN / "journal_watcher.py")],
        "cwd": str(_AGENTS_BIN),
        "env": {},
    },
}

_MAX_SILENT_RESTARTS = 2


def already_running() -> bool:
    """Return True if another Grove instance owns the PID file."""
    try:
        pid = int(_PID_FILE.read_text().strip())
        # Check if that PID is actually alive
        os.kill(pid, 0)
        return True
    except (FileNotFoundError, ValueError, ProcessLookupError, PermissionError):
        return False


def _write_pid() -> None:
    _PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    _PID_FILE.write_text(str(os.getpid()))


def _clear_pid() -> None:
    try:
        _PID_FILE.unlink(missing_ok=True)
    except Exception:
        pass


class FleetManager:
    """Owns the lifecycle of all Grove fleet services."""

    def __init__(self, on_alert: Callable[[str, int], None] | None = None) -> None:
        self._on_alert    = on_alert
        self._procs:   dict[str, subprocess.Popen] = {}
        self._failures: dict[str, int]             = {}
        self._alerted:  set[str]                   = set()   # alert fires once per service
        self._running   = False
        self._monitor   = threading.Thread(target=self._watch_loop, daemon=True)

    def start(self) -> None:
        _write_pid()
        self._running = True
        for name, cfg in _SERVICES.items():
            self._failures[name] = 0
            self._spawn(name, cfg)
        self._monitor.start()
        _log.info("FleetManager started. Services: %s", list(_SERVICES))

    def stop(self) -> None:
        self._running = False
        for name, proc in list(self._procs.items()):
            try:
                proc.terminate()
                proc.wait(timeout=5)
                _log.info("Stopped %s (PID %d)", name, proc.pid)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
        self._procs.clear()
        _clear_pid()
        _log.info("FleetManager stopped.")

    def status(self) -> dict[str, str]:
        result = {}
        for name in _SERVICES:
            proc = self._procs.get(name)
            if proc is None:
                result[name] = "stopped"
            elif proc.poll() is None:
                result[name] = "running"
            else:
                result[name] = f"dead (rc={proc.returncode})"
        return result

    def _spawn(self, name: str, cfg: dict) -> None:
        env = {**os.environ, **cfg.get("env", {})}
        log_fh = open(_LOG_FILE, "a")
        try:
            proc = subprocess.Popen(
                cfg["cmd"],
                cwd=cfg.get("cwd"),
                env=env,
                stdout=log_fh,
                stderr=log_fh,
            )
            self._procs[name] = proc
            _log.info("Spawned %s PID %d", name, proc.pid)
        except Exception as exc:
            _log.error("Failed to spawn %s: %s", name, exc)
            self._failures[name] = self._failures.get(name, 0) + 1

    def _watch_loop(self) -> None:
        while self._running:
            time.sleep(5)
            for name, cfg in _SERVICES.items():
                if not self._running:
                    break
                proc = self._procs.get(name)
                if proc is None or proc.poll() is not None:
                    self._failures[name] = self._failures.get(name, 0) + 1
                    count = self._failures[name]
                    _log.warning("%s exited (failure #%d)", name, count)
                    if count <= _MAX_SILENT_RESTARTS:
                        self._spawn(name, cfg)
                    elif name not in self._alerted and self._on_alert:
                        self._alerted.add(name)   # alert fires exactly once
                        self._on_alert(name, count)
