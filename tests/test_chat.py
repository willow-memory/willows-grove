"""Tests for ChatApp data helpers.
b17: WDASH  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from grove.apps.chat import format_message_header, advance_cursor, ChatApp


def test_format_message_header_includes_sender():
    hdr = format_message_header("hanuman", "13:04")
    assert "hanuman" in hdr
    assert "13:04" in hdr


def test_advance_cursor_updates():
    cursors = {"general": 0, "architecture": 5}
    advance_cursor(cursors, "architecture", 10)
    assert cursors["architecture"] == 10


def test_advance_cursor_no_regression():
    cursors = {"architecture": 10}
    advance_cursor(cursors, "architecture", 7)
    assert cursors["architecture"] == 10


def test_chat_app_initial_state():
    app = ChatApp()
    assert app.id == "chat"
    assert app._active_channel == ""
    assert app._cursors == {}
    assert app._messages == []
    assert app._channels == []
