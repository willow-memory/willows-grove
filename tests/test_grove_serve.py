"""Tests for grove_serve.py HTTP surface.
b17: WDASH  ΔΣ=42

Spins up a real HTTPServer on a random port so routing, auth, and response
format are all exercised end-to-end. grove_db calls are patched out so no
real Postgres is required.
"""
import hashlib
import hmac
import http.server
import json
import sys
import os
import threading
import urllib.error
import urllib.request
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grove_serve

_TEST_TOKEN = "deadbeefdeadbeefdeadbeefdeadbeef"


def _sign_body(token: str, body: bytes) -> str:
    return hmac.new(token.encode(), body, hashlib.sha256).hexdigest()


def _sign_path(token: str, path: str) -> str:
    return hmac.new(token.encode(), path.encode(), hashlib.sha256).hexdigest()


@pytest.fixture(scope="module")
def server():
    """Start a GroveHandler HTTPServer on a random port for the whole module."""
    grove_serve._TOKEN = _TEST_TOKEN
    httpd = http.server.HTTPServer(("127.0.0.1", 0), grove_serve.GroveHandler)
    port = httpd.server_address[1]
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    base = f"http://127.0.0.1:{port}"
    yield base
    httpd.shutdown()


def _get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req) as r:
        return r.status, json.loads(r.read())


def _post(url, payload, headers=None):
    body = json.dumps(payload).encode()
    headers = {"Content-Type": "application/json", **(headers or {})}
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


# ── /health ──────────────────────────────────────────────────────────────────

def test_health_200(server):
    status, data = _get(f"{server}/health")
    assert status == 200
    assert data["status"] == "ok"
    assert data["service"] == "grove-serve"


def test_unknown_get_404(server):
    with pytest.raises(urllib.error.HTTPError) as exc:
        urllib.request.urlopen(f"{server}/not-a-path")
    assert exc.value.code == 404


# ── /grove/channels ───────────────────────────────────────────────────────────

def test_channels_missing_sig_401(server):
    with pytest.raises(urllib.error.HTTPError) as exc:
        urllib.request.urlopen(f"{server}/grove/channels")
    assert exc.value.code == 401


def test_channels_bad_sig_401(server):
    req = urllib.request.Request(
        f"{server}/grove/channels",
        headers={"X-Grove-Sig": "badsig"},
    )
    with pytest.raises(urllib.error.HTTPError) as exc:
        urllib.request.urlopen(req)
    assert exc.value.code == 401


def test_channels_valid_sig_200(server):
    path = "/grove/channels"
    sig = _sign_path(_TEST_TOKEN, path)
    mock_conn = MagicMock()
    fake_channels = [{"id": 1, "name": "general", "channel_type": "group"}]
    with patch("grove_db.get_connection", return_value=mock_conn), \
         patch("grove_db.list_channels", return_value=fake_channels), \
         patch("grove_db.release_connection"):
        status, data = _get(f"{server}{path}", headers={"X-Grove-Sig": sig})
    assert status == 200
    assert data["channels"][0]["name"] == "general"


# ── /grove/send ───────────────────────────────────────────────────────────────

def test_send_missing_sig_401(server):
    status, data = _post(f"{server}/grove/send", {"channel": "general", "content": "hi"})
    assert status == 401


def test_send_missing_fields_400(server):
    payload = {"channel": "general"}
    body = json.dumps(payload).encode()
    sig = _sign_body(_TEST_TOKEN, body)
    status, data = _post(
        f"{server}/grove/send", payload,
        headers={"X-Grove-Sig": sig},
    )
    assert status == 400


def test_send_valid_200(server):
    payload = {"channel": "general", "content": "hello fleet", "sender": "hanuman"}
    body = json.dumps(payload).encode()
    sig = _sign_body(_TEST_TOKEN, body)
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_cur.fetchone.return_value = (42,)
    with patch("grove_db.get_connection", return_value=mock_conn), \
         patch("grove_db.send_message", return_value={"id": 99}), \
         patch("grove_db.release_connection"):
        status, data = _post(
            f"{server}/grove/send", payload,
            headers={"X-Grove-Sig": sig},
        )
    assert status == 200
    assert data["ok"] is True
    assert data["channel"] == "general"


def test_send_body_too_large_413(server):
    body = b"x" * (grove_serve.GroveHandler._MAX_BODY + 1)
    sig = _sign_body(_TEST_TOKEN, body)
    req = urllib.request.Request(
        f"{server}/grove/send",
        data=body,
        headers={"Content-Type": "application/json", "X-Grove-Sig": sig},
    )
    with pytest.raises(urllib.error.HTTPError) as exc:
        urllib.request.urlopen(req)
    assert exc.value.code == 413


# ── /command ─────────────────────────────────────────────────────────────────

def test_command_missing_sig_401(server):
    status, data = _post(f"{server}/command", {"cmd": "status"})
    assert status == 401


def test_command_disallowed_403(server):
    payload = {"cmd": "rm -rf /"}
    body = json.dumps(payload).encode()
    sig = _sign_body(_TEST_TOKEN, body)
    with patch("grove_serve._run_command", return_value=("Command not allowed: rm -rf /", 403)) as mock_run:
        status, data = _post(
            f"{server}/command", payload,
            headers={"X-Grove-Sig": sig},
        )
    # _run_command enforces allowlist internally and returns 403 exit code;
    # the handler always wraps it as 200 with exit_code in payload
    assert status == 200
    assert data["exit_code"] == 403


def test_command_allowed_runs(server):
    payload = {"cmd": "status"}
    body = json.dumps(payload).encode()
    sig = _sign_body(_TEST_TOKEN, body)
    with patch("grove_serve._run_command", return_value=("willow ok", 0)):
        status, data = _post(
            f"{server}/command", payload,
            headers={"X-Grove-Sig": sig},
        )
    assert status == 200
    assert data["output"] == "willow ok"
    assert data["exit_code"] == 0
