"""tests/test_chat_admin.py — channel name rules + archive guards."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from panes.chat_admin import can_archive_channel, normalize_channel_name


def test_normalize_strips_hash_and_lower():
    assert normalize_channel_name("# My-Project") == "my-project"


def test_normalize_rejects_empty():
    assert normalize_channel_name("   ") is None
    assert normalize_channel_name("#") is None


def test_normalize_rejects_dm_prefix():
    assert normalize_channel_name("dm:hanuman") is None


def test_normalize_rejects_protected():
    assert normalize_channel_name("general") is None
    assert normalize_channel_name("#dispatch") is None


def test_can_archive_custom():
    assert can_archive_channel("my-project") is True
    assert can_archive_channel("dm:hanuman") is True


def test_can_archive_protected():
    assert can_archive_channel("general") is False
    assert can_archive_channel("architecture") is False
