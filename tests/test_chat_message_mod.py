"""tests/test_chat_message_mod.py — message mod helpers."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime

from panes.chat_format import format_message_block
from panes.chat_message_mod import flag_prefix, flag_status_label


def test_flag_prefix_empty():
    assert flag_prefix(set()) == ("", "")
    assert flag_prefix(None) == ("", "")


def test_flag_prefix_marks():
    plain, markup = flag_prefix({"urgent", "needs-reply", "starred"})
    assert plain.startswith("!?*")
    assert "!" in markup
    assert "*" in markup


def test_flag_status_label():
    assert flag_status_label({"urgent", "resolved"}) == "urgent, resolved"
    assert flag_status_label(set()) == ""


def test_format_message_block_shows_flags():
    plain, _ = format_message_block(
        "alice",
        "hello",
        datetime(2026, 5, 22, 10, 0),
        flags={"urgent"},
    )
    assert "!" in plain
    assert "hello" in plain
