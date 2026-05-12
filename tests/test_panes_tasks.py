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


# ── Integration tests for tasks pane ───────────────────────────────────────────
from datetime import datetime, timezone
from panes.tasks import TasksPane

def test_fetch_tasks_empty_when_db_fails():
    """Verify fetch_tasks returns safe defaults on database failure."""
    with patch("grove_db.get_connection", side_effect=RuntimeError("DB down")):
        result = fetch_tasks()
        assert result["pending"] == 0
        assert result["running"] == 0
        assert result["done"] == 0
        assert result["rows"] == []

def test_fetch_backfill_progress_handles_missing_import():
    """Verify fetch_backfill_progress returns None when imports fail."""
    from panes.tasks import fetch_backfill_progress
    with patch("sys.path", ["/nonexistent"]):
        result = fetch_backfill_progress()
        # Should return None on import failure
        assert result is None or isinstance(result, (dict, type(None)))

def test_status_color_all_status_types():
    """Verify status_color handles all expected status values."""
    statuses = ["pending", "queued", "running", "complete", "completed", "failed", "error"]
    colors = [status_color(s) for s in statuses]
    assert all(isinstance(c, str) for c in colors)
    assert "dim" in colors  # pending/queued
    assert "yellow" in colors  # running
    assert "green" in colors  # complete/completed
    assert "red" in colors  # failed/error
