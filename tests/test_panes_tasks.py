"""tests/test_panes_tasks.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from unittest.mock import patch
from panes.tasks import fetch_tasks, status_color

def test_fetch_tasks_no_db():
    with patch("grove_db.get_connection", side_effect=Exception("no db")):
        result = fetch_tasks()
    assert result["pending"] == 0
    assert result["running"] == 0
    assert result["done"]    == 0
    assert result["rows"]    == []

def test_status_color_complete():
    assert status_color("complete")  == "green"
    assert status_color("completed") == "green"

def test_status_color_running():
    assert status_color("running")   == "yellow"

def test_status_color_pending():
    assert status_color("pending")   == "dim"
    assert status_color("queued")    == "dim"

def test_status_color_failed():
    assert status_color("failed")    == "red"
    assert status_color("error")     == "red"
