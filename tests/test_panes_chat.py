"""tests/test_panes_chat.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from datetime import datetime
from panes.chat import format_ts, sender_color, sort_channels

def test_format_ts_datetime():
    dt = datetime(2026, 4, 25, 13, 4, 0)
    assert format_ts(dt) == "13:04"

def test_format_ts_string_fallback():
    assert "13:04" in format_ts("2026-04-25 13:04:22")

def test_format_ts_none():
    assert format_ts(None) == ""

def test_sender_color_stable():
    assert sender_color("hanuman") == sender_color("hanuman")

def test_sender_color_different():
    colors = {sender_color(n) for n in ["hanuman", "ganesha", "jeles", "heimdallr"]}
    assert len(colors) > 1

def test_sort_channels_pinned_first():
    channels = [
        {"name": "readme",       "unread": 0},
        {"name": "general",      "unread": 0},
        {"name": "architecture", "unread": 0},
        {"name": "zebra",        "unread": 0},
    ]
    names = [c["name"] for c in sort_channels(channels)]
    assert names.index("general") < names.index("zebra")
    assert names.index("architecture") < names.index("zebra")


# ── Integration tests for chat pane ────────────────────────────────────────────
from unittest.mock import patch, MagicMock
from panes.chat import render_content

def test_render_content_detects_image_prefix():
    """Verify content rendering recognizes typed content prefixes."""
    result = render_content("[image: /tmp/test.png]")
    assert "IMAGE" in result
    assert "/tmp/test.png" in result

def test_render_content_detects_file_prefix():
    """Verify content rendering recognizes file prefixes."""
    result = render_content("[file: /home/user/doc.pdf]")
    assert "FILE" in result

def test_render_content_passes_through_normal():
    """Verify normal message content passes through unchanged."""
    msg = "Hello from @hanuman"
    result = render_content(msg)
    assert result == msg

def test_render_content_handles_missing_file():
    """Verify content rendering shows 'not found' for missing files."""
    result = render_content("[image: /nonexistent/file.png]")
    assert "not found" in result
