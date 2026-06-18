"""Tests for vitals strip helpers.
b17: WDASH  ΔΣ=42
"""
import json
import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from grove.apps.vitals import (
    _kart_ok,
    _pg_ok,
    fetch_vitals,
    format_vitals_line,
    format_vitals_markup,
    grove_live,
    grove_live_model,
)


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
                with patch(
                    "grove.apps.vitals._kart_ok",
                    return_value={"ok": True, "running": 2, "queued": 3},
                ):
                    with patch("grove.apps.vitals.grove_live", return_value=False):
                        with patch("grove.apps.vitals.server_count", return_value=2):
                            with patch("grove.apps.vitals.probe_serve_port", return_value=False):
                                v = fetch_vitals()

    assert "ollama" in v
    assert v["ollama"]["ok"] is True
    assert v["ollama"]["count"] == 2
    assert v["grove"]["live"] is False
    assert v["grove"]["model"] == ""
    assert v["mcp"]["count"] == 2


def test_format_vitals_line_healthy_no_grove_model():
    v = {
        "pg":     {"ok": True,  "detail": "69k atoms"},
        "ollama": {"ok": True,  "count": 2},
        "soil":   {"ok": True},
        "kart":   {"ok": True,  "running": 3, "queued": 5},
        "grove":  {"live": False, "model": ""},
    }
    line = format_vitals_line(v)
    assert "pg" in line
    assert "●" in line
    assert "ygg" not in line
    assert "mistral" not in line


def test_format_vitals_line_shows_model_only_when_grove_live():
    v = {
        "pg":     {"ok": True,  "detail": "69k atoms"},
        "ollama": {"ok": True,  "count": 2},
        "soil":   {"ok": True},
        "kart":   {"ok": True,  "running": 0, "queued": 0},
        "grove":  {"live": True, "model": "qwen2.5:3b"},
    }
    line = format_vitals_line(v)
    assert "qwen2.5:3b" in line


def test_format_vitals_markup_omits_model_when_grove_idle():
    v = {
        "pg":     {"ok": True,  "detail": ""},
        "ollama": {"ok": True,  "count": 4},
        "soil":   {"ok": True},
        "kart":   {"ok": True,  "running": 0, "queued": 0},
        "grove":  {"live": False, "model": ""},
    }
    markup = format_vitals_markup(v)
    assert "ollama" not in markup.lower()
    assert "mistral" not in markup
    assert "ygg" not in markup


def test_grove_live_model_empty_when_not_live():
    with patch("grove.apps.vitals.grove_live", return_value=False):
        assert grove_live_model() == ""


def test_grove_live_model_reads_soil_when_live():
    with patch("grove.apps.vitals.grove_live", return_value=True):
        with patch("soil.get", return_value={"value": "mistral:7b"}):
            assert grove_live_model() == "mistral:7b"


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
        "ollama": {"ok": False, "count": 0},
        "soil":   {"ok": False},
        "kart":   {"ok": False, "running": 0, "queued": 0},
        "grove":  {"live": False, "model": ""},
    }
    line = format_vitals_line(v)
    assert "○" in line
