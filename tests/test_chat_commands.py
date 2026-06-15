"""tests/test_chat_commands.py — Wave B `:` mod command parser."""
import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from panes.chat_commands import COMMAND_HINT, execute_mod_command, parse_mod_command


def test_parse_strips_colon_prefix():
    assert parse_mod_command(":agent hanuman") == ("agent", ["hanuman"])
    assert parse_mod_command("archive") == ("archive", [])


def test_parse_quoted_desc():
    verb, args = parse_mod_command(':desc "fleet ops room"')
    assert verb == "desc"
    assert args == ["fleet ops room"]


def test_parse_empty():
    assert parse_mod_command("") == ("", [])
    assert parse_mod_command(":") == ("", [])


def test_help_returns_panel():
    result = execute_mod_command("help", active_channel="general")
    assert result["ok"] is True
    assert result.get("show_panel") is True
    assert "create NAME" in result["message"]


@patch("panes.chat_commands.grove_reader.grove_set_channel_agent")
def test_agent_bind(mock_bind):
    mock_bind.return_value = {"ok": True, "agent": "hanuman"}
    result = execute_mod_command(":agent hanuman", active_channel="my-room")
    assert result["ok"] is True
    mock_bind.assert_called_once_with("my-room", "hanuman")
    assert result.get("refresh_persona") is True


@patch("panes.chat_commands.grove_reader.grove_archive_channel")
def test_archive_active(mock_archive):
    mock_archive.return_value = {"ok": True, "name": "my-room"}
    result = execute_mod_command("archive", active_channel="my-room")
    assert result["ok"] is True
    mock_archive.assert_called_once_with("my-room")
    assert result["open_channel"] == "general"


@patch("panes.chat_commands.grove_reader.grove_list_archived_channels")
def test_channels_archived_empty(mock_list):
    mock_list.return_value = []
    result = execute_mod_command("channels archived", active_channel="general")
    assert result["ok"] is True
    assert result.get("show_panel") is True
    assert "no archived" in result["message"]


def test_unknown_command():
    result = execute_mod_command("nope", active_channel="general")
    assert result["ok"] is False
    assert "unknown command" in result["message"]
