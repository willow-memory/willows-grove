"""
fleet.py — Grove FleetManager
b17: FLEET1  ΔΣ=42

Spawns fleet services on Grove open, terminates them on close.
Restart policy: silent ×2, alert callback on 3rd failure.
"""
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
    "corpus_watcher": {
        "cmd": [_SYS_PYTHON, str(_AGENTS_BIN / "corpus-watcher.py")],
        "cwd": str(_AGENTS_BIN),
        "env": {},
    },
}

_MAX_SILENT_RESTARTS = 2


class FleetManager:
    """Owns the lifecycle of all Grove fleet services."""

    def __init__(self, on_alert: Callable[[str, int], None] | None = None) -> None:
        # on_alert(service_name, failure_count) — called on 3rd failure
        self._on_alert   = on_alert
        self._procs:  dict[str, subprocess.Popen] = {}
        self._failures: dict[str, int]            = {}
        self._running   = False
        self._monitor   = threading.Thread(target=self._watch_loop, daemon=True)

    def start(self) -> None:
        self._running = True
        for name, cfg in _SERVICES.items():
            self._failures[name] = 0
            self._spawn(name, cfg)
        self._monitor.start()

    def stop(self) -> None:
        self._running = False
        for name, proc in list(self._procs.items()):
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
        self._procs.clear()

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
        try:
            proc = subprocess.Popen(
                cfg["cmd"],
                cwd=cfg.get("cwd"),
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self._procs[name] = proc
        except Exception:
            self._failures[name] = self._failures.get(name, 0) + 1

    def _watch_loop(self) -> None:
        while self._running:
            time.sleep(5)
            for name, cfg in _SERVICES.items():
                proc = self._procs.get(name)
                if proc is None or proc.poll() is not None:
                    if not self._running:
                        break
                    self._failures[name] = self._failures.get(name, 0) + 1
                    count = self._failures[name]
                    if count <= _MAX_SILENT_RESTARTS:
                        self._spawn(name, cfg)
                    elif self._on_alert:
                        self._on_alert(name, count)
