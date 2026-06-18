"""tests/test_chat_persona.py — Wave C persona routing + dispatch."""
import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from panes.chat_persona import (
    build_dispatch_payload,
    effective_reply_channel,
    get_reply_override,
    normalize_agent,
    normalize_reply_channel,
    set_reply_override,
)
from panes.chat_commands import execute_mod_command
from panes.chat_format import format_channel_title, format_member_row


def test_normalize_agent():
    assert normalize_agent("@Hanuman") == "hanuman"
    assert normalize_agent("  kart ") == "kart"


def test_normalize_reply_channel():
    assert normalize_reply_channel("#general") == "general"
    assert normalize_reply_channel("dm:hanuman") is None


@patch("panes.chat_persona.soil.get")
def test_get_reply_override(mock_get):
    mock_get.return_value = {"reply_channel": "handoffs"}
    assert get_reply_override("ops") == "handoffs"
    mock_get.return_value = {"reply_channel": ""}
    assert get_reply_override("ops") is None


@patch("panes.chat_persona.soil.put")
def test_set_reply_override(mock_put):
    set_reply_override("ops", "handoffs")
    mock_put.assert_called_once()
    assert mock_put.call_args[0][2]["reply_channel"] == "handoffs"


def test_effective_reply_channel():
    with patch("panes.chat_persona.get_reply_override", return_value="handoffs"):
        assert effective_reply_channel("ops") == "handoffs"
    assert effective_reply_channel("ops", override="alerts") == "alerts"


def test_build_dispatch_payload():
    payload = build_dispatch_payload(agent="@Kart", prompt="hello", reply_channel="general")
    assert payload == {"to": "kart", "prompt": "hello", "reply_channel": "general"}


def test_format_channel_title_reply_route():
    ch = {"name": "ops", "channel_type": "group", "agent_name": "hanuman"}
    title = format_channel_title(ch, reply_override="handoffs")
    assert "ops" in title
    assert "handoffs" in title


def test_format_member_row_bound_marker():
    row = format_member_row("hanuman", 30, bound=True)
    assert "▶" in row


@patch("panes.chat_commands.set_reply_override")
@patch("panes.chat_commands.grove_reader.grove_set_channel_agent")
def test_takeover_command(mock_bind, mock_reply):
    mock_bind.return_value = {"ok": True}
    result = execute_mod_command("takeover", active_channel="ops")
    assert result["ok"] is True
    assert result.get("refresh_persona") is True
    assert result.get("clear_waiting") is True
    mock_bind.assert_called_once_with("ops", None)
    mock_reply.assert_called_once_with("ops", None)


@patch("panes.chat_commands.set_reply_override")
def test_reply_command(mock_reply):
    result = execute_mod_command("reply handoffs", active_channel="ops")
    assert result["ok"] is True
    assert result.get("refresh_persona") is True
    mock_reply.assert_called_once_with("ops", "handoffs")


@patch("panes.chat_commands.grove_reader.grove_set_channel_agent")
def test_agent_bind_refresh_persona(mock_bind):
    mock_bind.return_value = {"ok": True, "agent": "hanuman"}
    result = execute_mod_command(":agent hanuman", active_channel="ops")
    assert result.get("refresh_persona") is True
