"""tests/test_chat.py
b17: WGRV1  ΔΣ=42
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from panes.chat import (
    render_content, format_ts, sort_channels, _build_channel_label
)
from datetime import datetime


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
    channels = [{"name": "architecture"}, {"name": "general"}, {"name": "readme"}]
    result = sort_channels(channels)
    assert [c["name"] for c in result] == ["general", "architecture", "readme"]


def test_sort_channels_unknown_appended_alphabetically():
    channels = [{"name": "random"}, {"name": "general"}, {"name": "zzz"}]
    result = sort_channels(channels)
    assert result[0]["name"] == "general"
    assert result[-1]["name"] == "zzz"


def test_build_channel_label_plain():
    ch = {"name": "general", "unread": 0, "agent_name": None}
    assert _build_channel_label(ch) == "# general"


def test_build_channel_label_unread():
    ch = {"name": "general", "unread": 3, "agent_name": None}
    label = _build_channel_label(ch)
    assert "# general" in label
    assert "3" in label


def test_build_channel_label_agent():
    ch = {"name": "willow-grove", "unread": 0, "agent_name": "hanuman"}
    label = _build_channel_label(ch)
    assert "# willow-grove" in label
    assert "hanuman" in label


def test_build_channel_label_agent_and_unread():
    ch = {"name": "willow-grove", "unread": 2, "agent_name": "hanuman"}
    label = _build_channel_label(ch)
    assert "# willow-grove" in label
    assert "hanuman" in label
    assert "2" in label
