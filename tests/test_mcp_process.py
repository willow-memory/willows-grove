"""tests/test_mcp_process.py — grove serve process control."""
import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from grove.apps import mcp_process


def test_serve_status_not_running_when_no_record(monkeypatch):
    monkeypatch.setattr(mcp_process, "_read_record", lambda: {})
    status = mcp_process.serve_status()
    assert status["running"] is False
    assert status["pid"] is None


def test_stop_serve_when_not_running(monkeypatch):
    monkeypatch.setattr(mcp_process, "serve_status", lambda: {"running": False, "pid": None})
    ok, msg = mcp_process.stop_serve()
    assert ok is False
    assert "not running" in msg


def test_start_serve_already_running(monkeypatch):
    monkeypatch.setattr(
        mcp_process,
        "serve_status",
        lambda: {"running": True, "pid": 99999},
    )
    ok, msg = mcp_process.start_serve()
    assert ok is False
    assert "already running" in msg


def test_restart_serve_calls_stop_then_start(monkeypatch):
    calls: list[str] = []

    def fake_stop():
        calls.append("stop")
        return True, "stopped"

    def fake_start(**kwargs):
        calls.append("start")
        return True, "started"

    monkeypatch.setattr(mcp_process, "stop_serve", fake_stop)
    monkeypatch.setattr(mcp_process, "start_serve", fake_start)
    ok, msg = mcp_process.restart_serve()
    assert ok is True
    assert calls == ["stop", "start"]
