"""grove/apps/mcp_process.py — manage grove.mcp_local --serve from the dashboard.
b17: WDASH  ΔΣ=42
"""
from __future__ import annotations

import os
import signal
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import soil

from grove.apps.mcp_registry import _REPO_ROOT, _SERVE_PORT, probe_serve_port

_COLLECTION = "grove-dashboard/mcp-serve"
_RECORD_ID = "grove"


def _log_path() -> Path:
    p = Path.home() / ".willow" / "grove-mcp-serve.log"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _python() -> str:
    candidates = [
        os.environ.get("GROVE_VENV", ""),
        str(Path.home() / "willow-2.0" / ".venv-dev"),
        str(Path.home() / "github" / "willow-2.0" / ".venv-dev"),
    ]
    for base in candidates:
        if not base:
            continue
        py = Path(base).expanduser() / "bin" / "python3"
        if py.is_file():
            return str(py)
    return "python3"


def _pid_alive(pid: int | None) -> bool:
    if not pid or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _read_record() -> dict:
    return soil.get(_COLLECTION, _RECORD_ID) or {}


def _write_record(data: dict) -> None:
    soil.put(_COLLECTION, _RECORD_ID, data)


def _clear_record() -> None:
    soil.put(_COLLECTION, _RECORD_ID, {"pid": None, "port": _SERVE_PORT})


def serve_status() -> dict:
    rec = _read_record()
    pid = rec.get("pid")
    pid = int(pid) if pid else None
    running = _pid_alive(pid)
    if pid and not running:
        _clear_record()
        pid = None
        running = False
    port = int(rec.get("port") or _SERVE_PORT)
    return {
        "running": running,
        "pid": pid,
        "port": port,
        "up": probe_serve_port(port),
        "log_path": str(_log_path()),
        "started_at": rec.get("started_at", ""),
    }


def start_serve(*, watch: bool = False) -> tuple[bool, str]:
    status = serve_status()
    if status["running"]:
        return False, f"serve already running (pid {status['pid']})"
    py = _python()
    args = [py, "-m", "grove.mcp_local", "--serve"]
    if watch:
        args.append("--watch")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(_REPO_ROOT) + (
        f":{env['PYTHONPATH']}" if env.get("PYTHONPATH") else ""
    )
    env.setdefault("WILLOW_PG_DB", "willow_20")
    env.setdefault("WILLOW_PG_USER", os.environ.get("USER", ""))
    env.setdefault("GROVE_MCP_PORT", str(_SERVE_PORT))
    log = _log_path()
    log.parent.mkdir(parents=True, exist_ok=True)
    with open(log, "a", encoding="utf-8") as logfh:
        logfh.write(f"\n--- start {datetime.now(timezone.utc).isoformat()} ---\n")
        proc = subprocess.Popen(
            args,
            cwd=str(_REPO_ROOT),
            env=env,
            stdout=logfh,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    _write_record({
        "pid": proc.pid,
        "port": _SERVE_PORT,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "watch": watch,
    })
    deadline = time.time() + 8.0
    while time.time() < deadline:
        if probe_serve_port(_SERVE_PORT):
            return True, f"serve started pid {proc.pid} on :{_SERVE_PORT}"
        if proc.poll() is not None:
            return False, f"serve exited early (code {proc.returncode}); see {log}"
        time.sleep(0.25)
    return True, f"serve pid {proc.pid} started (port not responding yet — check {log})"


def stop_serve() -> tuple[bool, str]:
    status = serve_status()
    pid = status.get("pid")
    if not pid or not status["running"]:
        _clear_record()
        return False, "serve not running"
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError as exc:
        _clear_record()
        return False, f"stop failed: {exc}"
    deadline = time.time() + 6.0
    while time.time() < deadline:
        if not _pid_alive(pid):
            _clear_record()
            return True, f"serve stopped (was pid {pid})"
        time.sleep(0.2)
    try:
        os.kill(pid, signal.SIGKILL)
    except OSError:
        pass
    _clear_record()
    return True, f"serve killed (pid {pid})"


def restart_serve(*, watch: bool = False) -> tuple[bool, str]:
    stop_serve()
    return start_serve(watch=watch)
