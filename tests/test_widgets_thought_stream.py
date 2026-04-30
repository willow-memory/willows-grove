"""tests/test_widgets_thought_stream.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from widgets.thought_stream import is_agent_sender, parse_session_stats, KNOWN_AGENTS

def test_known_agents_not_empty():
    assert len(KNOWN_AGENTS) > 0

def test_is_agent_sender_known():
    for name in ("hanuman", "heimdallr", "ganesha"):
        assert is_agent_sender(name), f"{name} should be agent"

def test_is_agent_sender_human():
    assert not is_agent_sender("sean")
    assert not is_agent_sender("unknown_person")

def test_is_agent_sender_case_insensitive():
    assert is_agent_sender("HANUMAN")
    assert is_agent_sender("Heimdallr")

def test_parse_session_stats_full():
    data = {
        "written_at": "2026-04-30T09:00:00",
        "open_flags": 2,
        "handoff_summary": "Worked on dashboard.",
    }
    result = parse_session_stats(data)
    assert "2" in result

def test_parse_session_stats_missing_keys():
    result = parse_session_stats({})
    assert isinstance(result, str)

def test_parse_session_stats_none():
    result = parse_session_stats(None)
    assert isinstance(result, str)
