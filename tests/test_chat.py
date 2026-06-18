"""tests/test_chat.py
b17: WGRV1  ΔΣ=42
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime

from panes.chat import _build_channel_label, format_ts, render_content, sort_channels
from panes.chat_format import (
    dm_channel_name,
    dm_display_name,
    format_channel_title,
    is_direct_channel,
    partition_channels,
)


def test_render_content_plain():
    assert render_content("hello world") == "hello world"


def test_render_content_image_prefix_existing(tmp_path):
    p = tmp_path / "foo.png"
    p.write_bytes(b"")
    result = render_content(f"[image: {p}]")
    assert "IMAGE" in result
    assert "foo.png" in result
    assert "✓" in result


def test_render_content_image_prefix_missing():
    result = render_content("[image: /nonexistent/foo.png]")
    assert "IMAGE" in result
    assert "not found" in result


def test_format_ts_datetime():
    dt = datetime(2026, 4, 30, 14, 35, 0)
    assert format_ts(dt) == "14:35"


def test_format_ts_string():
    assert format_ts("2026-04-30 09:12:00") == "09:12"


def test_format_ts_none():
    assert format_ts(None) == ""


def test_sort_channels_known_order():
    channels = [
        {"name": "architecture", "channel_type": "group"},
        {"name": "general", "channel_type": "group"},
        {"name": "readme", "channel_type": "group"},
    ]
    result = sort_channels(channels)
    assert [c["name"] for c in result] == ["general", "architecture", "readme"]


def test_partition_text_and_dm():
    channels = [
        {"name": "general", "channel_type": "group", "unread": 0},
        {"name": "dm:hanuman", "channel_type": "direct", "unread": 2},
        {"name": "architecture", "channel_type": "group", "unread": 0},
    ]
    text, dms = partition_channels(channels)
    assert [c["name"] for c in text] == ["general", "architecture"]
    assert [c["name"] for c in dms] == ["dm:hanuman"]


def test_dm_names():
    assert dm_channel_name("Hanuman") == "dm:hanuman"
    assert dm_display_name("dm:hanuman") == "@hanuman"


def test_build_channel_label_plain():
    ch = {"name": "general", "unread": 0, "agent_name": None, "channel_type": "group"}
    label = _build_channel_label(ch)
    assert "# general" in label
    assert "●" not in label


def test_build_channel_label_dm():
    ch = {"name": "dm:hanuman", "unread": 1, "channel_type": "direct"}
    label = _build_channel_label(ch)
    assert "@hanuman" in label
    assert "# hanuman" not in label


def test_build_channel_label_unread():
    ch = {"name": "general", "unread": 3, "agent_name": None, "channel_type": "group"}
    label = _build_channel_label(ch)
    assert "# general" in label
    assert "3" in label


def test_build_channel_label_agent():
    ch = {
        "name": "willow-grove",
        "unread": 0,
        "agent_name": "hanuman",
        "channel_type": "persona",
    }
    label = _build_channel_label(ch)
    assert "# willow-grove" in label
    assert "hanuman" in label


def test_format_channel_title_dm():
    ch = {"name": "dm:hanuman", "channel_type": "direct"}
    assert "@hanuman" in format_channel_title(ch)
    assert is_direct_channel(ch)
