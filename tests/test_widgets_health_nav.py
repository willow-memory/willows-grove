"""tests/test_widgets_health_nav.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock
from widgets.health_nav import _fetch_health_status


def test_health_status_returns_required_keys():
    status = _fetch_health_status()
    for key in ("pg", "ollama", "kart", "soil"):
        assert key in status
        assert "ok" in status[key]
        assert "label" in status[key]


def test_health_status_ok_is_bool():
    status = _fetch_health_status()
    for key in ("pg", "ollama", "kart", "soil"):
        assert isinstance(status[key]["ok"], bool)


def test_health_status_label_is_str():
    status = _fetch_health_status()
    for key in ("pg", "ollama", "kart", "soil"):
        assert isinstance(status[key]["label"], str)


def test_health_status_never_raises():
    with patch("psycopg2.connect", side_effect=Exception("no db")):
        with patch("grove_db.get_connection", side_effect=Exception("no db")):
            with patch("urllib.request.urlopen", side_effect=Exception("no net")):
                status = _fetch_health_status()
    assert isinstance(status, dict)
    assert status["pg"]["ok"] is False
    assert status["ollama"]["ok"] is False


def test_soil_false_when_missing(tmp_path):
    with patch("widgets.health_nav._SOIL_STORE", tmp_path / "nonexistent"):
        status = _fetch_health_status()
    assert status["soil"]["ok"] is False


def test_soil_true_when_present(tmp_path):
    store = tmp_path / "store"
    store.mkdir()
    with patch("widgets.health_nav._SOIL_STORE", store):
        status = _fetch_health_status()
    assert status["soil"]["ok"] is True


def test_kart_ok_with_mock_db():
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = (3,)
    mock_conn.cursor.return_value = mock_cur
    with patch("grove_db.get_connection", return_value=mock_conn):
        with patch("grove_db.release_connection"):
            status = _fetch_health_status()
    assert status["kart"]["ok"] is True
    assert "3" in status["kart"]["label"]
