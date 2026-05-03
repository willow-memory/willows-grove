"""Tests for VitalsApp data helpers.
b17: WDASH  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from unittest.mock import patch, MagicMock
import json
from grove.apps.vitals import fetch_vitals, format_vitals_line, _pg_ok, _kart_ok


def test_fetch_vitals_structure():
    mock_tags = json.dumps({"models": [
        {"name": "yggdrasil:v9"}, {"name": "nomic-embed-text"}
    ]}).encode()
    mock_resp = MagicMock()
    mock_resp.read.return_value = mock_tags
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_resp):
        with patch("grove.apps.vitals._pg_ok", return_value=(True, "69k atoms")):
            with patch("grove.apps.vitals._soil_ok", return_value=True):
                with patch("grove.apps.vitals._kart_ok",
                           return_value={"ok": True, "running": 2, "queued": 3}):
                    v = fetch_vitals()

    assert "ollama" in v
    assert v["ollama"]["ok"] is True
    assert "yggdrasil:v9" in v["ollama"]["active"]
    assert "pg" in v
    assert "soil" in v


def test_format_vitals_line_healthy():
    v = {
        "pg":     {"ok": True,  "detail": "69k atoms"},
        "ollama": {"ok": True,  "active": "yggdrasil:v9", "count": 2},
        "soil":   {"ok": True},
        "kart":   {"ok": True,  "running": 3, "queued": 5},
    }
    line = format_vitals_line(v)
    assert "pg" in line
    assert "●" in line
    assert "ygg" in line


def test_pg_ok_returns_count():
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.fetchone.return_value = (42,)
    with patch("grove_db.get_connection", return_value=mock_conn):
        with patch("grove_db.release_connection") as rel:
            ok, detail = _pg_ok()
    assert ok is True
    assert "42" in detail
    rel.assert_called_once_with(mock_conn)


def test_pg_ok_db_error_returns_false():
    with patch("grove_db.get_connection", side_effect=Exception("refused")):
        ok, detail = _pg_ok()
    assert ok is False
    assert "refused" in detail


def test_kart_ok_returns_counts():
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.fetchone.return_value = (2, 5)
    with patch("grove_db.get_connection", return_value=mock_conn):
        with patch("grove_db.release_connection") as rel:
            result = _kart_ok()
    assert result["ok"] is True
    assert result["running"] == 2
    assert result["queued"] == 5
    rel.assert_called_once_with(mock_conn)


def test_kart_ok_db_error_returns_false():
    with patch("grove_db.get_connection", side_effect=Exception("down")):
        result = _kart_ok()
    assert result["ok"] is False
    assert result["running"] == 0
    assert result["queued"] == 0


def test_format_vitals_line_pg_down():
    v = {
        "pg":     {"ok": False, "detail": "ECONNREFUSED"},
        "ollama": {"ok": False, "active": "", "count": 0},
        "soil":   {"ok": False},
        "kart":   {"ok": False, "running": 0, "queued": 0},
    }
    line = format_vitals_line(v)
    assert "○" in line
