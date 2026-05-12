"""Tests for grove_reader.py
b17: WDASH  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta
import grove_reader


def _mock_conn(rows_by_query):
    conn = MagicMock()
    cur = MagicMock()
    conn.cursor.return_value = cur
    call_count = [0]
    def fetchall_side():
        i = call_count[0]
        call_count[0] += 1
        return rows_by_query[i] if i < len(rows_by_query) else []
    def fetchone_side():
        i = call_count[0]
        call_count[0] += 1
        rows = rows_by_query[i] if i < len(rows_by_query) else []
        return rows[0] if rows else None
    cur.fetchall.side_effect = fetchall_side
    cur.fetchone.side_effect = fetchone_side
    return conn


def test_grove_agents_returns_list():
    now = datetime.now(timezone.utc)
    rows = [("hanuman", now - timedelta(seconds=30)),
            ("heimdallr", now - timedelta(seconds=90))]
    conn = _mock_conn([rows])
    result = grove_reader.grove_agents(conn=conn)
    assert len(result) == 2
    assert result[0]["sender"] == "hanuman"
    assert result[0]["age_secs"] < 60
    assert result[1]["age_secs"] < 120


def test_grove_agents_empty():
    conn = _mock_conn([[]])
    result = grove_reader.grove_agents(conn=conn)
    assert result == []


def test_grove_channels_with_unread():
    channel_rows = [(1, "general", None), (2, "architecture", None)]
    unread_general = [(0, 100)]
    unread_arch = [(3, 52)]
    conn = _mock_conn([channel_rows, unread_general, unread_arch])
    result = grove_reader.grove_channels(conn=conn, last_seen_ids={"architecture": 49})
    assert len(result) == 2
    by_name = {r["name"]: r for r in result}
    assert "general" in by_name
    assert "architecture" in by_name
    assert by_name["general"]["unread"] == 0
    assert by_name["architecture"]["unread"] == 3


def test_grove_channels_empty():
    conn = _mock_conn([[]])
    result = grove_reader.grove_channels(conn=conn)
    assert result == []


def test_routing_decisions_returns_empty_on_missing_table():
    conn = MagicMock()
    cur = MagicMock()
    conn.cursor.return_value = cur
    cur.execute.side_effect = Exception("relation does not exist")
    result = grove_reader.routing_decisions(conn=conn)
    assert result == []


def test_routing_decisions_returns_rows():
    now = datetime.now(timezone.utc)
    rows = [(now, "debug gleipnir", "ganesha", "rule-debug", 0.95, 3)]
    conn = _mock_conn([rows])
    result = grove_reader.routing_decisions(conn=conn)
    assert len(result) == 1
    assert result[0]["routed_to"] == "ganesha"
    assert result[0]["confidence"] == 0.95


def test_ui_state_running():
    assert grove_reader._ui_state(30, None) == "running"


def test_ui_state_idle():
    assert grove_reader._ui_state(300, None) == "idle"


def test_ui_state_stale():
    assert grove_reader._ui_state(1000, None) == "stale"


def test_ui_state_unknown():
    assert grove_reader._ui_state(None, None) == "unknown"


def test_ui_state_blocked_via_heartbeat():
    assert grove_reader._ui_state(30, "[AGENT_VIEW] status=blocked reason=waiting") == "blocked"


def test_grove_latest_message_for_sender_found():
    conn = _mock_conn([[(42, "hello world", "corr-1", None)]])
    result = grove_reader.grove_latest_message_for_sender("hanuman", conn=conn)
    assert result is not None
    assert result["id"] == 42
    assert result["content"] == "hello world"
    assert result["correlation_id"] == "corr-1"


def test_grove_latest_message_for_sender_none():
    conn = _mock_conn([[]])
    result = grove_reader.grove_latest_message_for_sender("nobody", conn=conn)
    assert result is None


def test_grove_agent_fleet_rows_running():
    now = datetime.now(timezone.utc)
    hb = [("hanuman", now - timedelta(seconds=30), None)]
    peek = [("hanuman", 99, "working on FAV", "corr-x", False)]
    conn = _mock_conn([hb, peek])
    rows = grove_reader.grove_agent_fleet_rows(conn=conn)
    assert len(rows) == 1
    r = rows[0]
    assert r["sender"] == "hanuman"
    assert r["ui_state"] == "running"
    assert r["blocked"] is False
    assert r["peek"] == "working on FAV"
    assert r["correlation_id"] == "corr-x"


def test_grove_agent_fleet_rows_blocked_by_flag():
    now = datetime.now(timezone.utc)
    hb = [("hanuman", now - timedelta(seconds=30), None)]
    peek = [("hanuman", 99, "need approval", "corr-x", True)]
    conn = _mock_conn([hb, peek])
    rows = grove_reader.grove_agent_fleet_rows(conn=conn)
    r = rows[0]
    assert r["ui_state"] == "blocked"
    assert r["blocked"] is True
    assert r["reply_to_message_id"] == 99


def test_grove_agent_fleet_rows_blocked_by_heartbeat():
    now = datetime.now(timezone.utc)
    hb = [("hanuman", now - timedelta(seconds=30), "[AGENT_VIEW] status=blocked reason=waiting")]
    peek = [("hanuman", 99, "last msg", None, False)]
    conn = _mock_conn([hb, peek])
    rows = grove_reader.grove_agent_fleet_rows(conn=conn)
    r = rows[0]
    assert r["ui_state"] == "blocked"
    assert r["blocked"] is True
    assert r["reply_to_message_id"] is None


def test_grove_agent_fleet_rows_empty():
    conn = _mock_conn([[]])
    rows = grove_reader.grove_agent_fleet_rows(conn=conn)
    assert rows == []


def test_color_for_sender_stable():
    c1 = grove_reader.color_for_sender("hanuman")
    c2 = grove_reader.color_for_sender("hanuman")
    assert c1 == c2


def test_color_for_sender_different():
    colors = {grove_reader.color_for_sender(n) for n in
              ["hanuman", "heimdallr", "oakenscroll", "design-claude", "jeles"]}
    assert len(colors) > 1
