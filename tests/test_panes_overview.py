"""tests/test_panes_overview.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from unittest.mock import patch
from panes.overview import fetch_sysinfo, _pg_status, _ollama_status, _open_tasks

def test_fetch_sysinfo_keys():
    info = fetch_sysinfo()
    for key in ("cpu", "mem", "disk"):
        assert key in info
        assert isinstance(info[key], int)
        assert 0 <= info[key] <= 100

def test_pg_status_returns_tuple():
    with patch("panes.overview._pg_conn", side_effect=Exception("no db")):
        ok, count = _pg_status()
    assert ok is False
    assert count == 0

def test_ollama_status_unreachable():
    with patch("urllib.request.urlopen", side_effect=Exception("refused")):
        ok, models = _ollama_status()
    assert ok is False
    assert models == []

def test_open_tasks_returns_int():
    with patch("panes.overview._pg_conn", side_effect=Exception("no db")):
        count = _open_tasks()
    assert count == 0
