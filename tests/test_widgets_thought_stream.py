"""tests/test_widgets_thought_stream.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from unittest.mock import patch
from widgets.thought_stream import _load_known_agents, parse_session_stats


def test_load_known_agents_from_env(monkeypatch):
    monkeypatch.setenv("GROVE_KNOWN_AGENTS", "alpha, Beta ,gamma")
    agents = _load_known_agents()
    assert "alpha" in agents
    assert "beta" in agents
    assert "gamma" in agents


def test_load_known_agents_env_lowercases(monkeypatch):
    monkeypatch.setenv("GROVE_KNOWN_AGENTS", "Hanuman,HEIMDALLR")
    agents = _load_known_agents()
    assert "hanuman" in agents
    assert "heimdallr" in agents


def test_load_known_agents_env_strips_whitespace(monkeypatch):
    monkeypatch.setenv("GROVE_KNOWN_AGENTS", " foo , bar ")
    agents = _load_known_agents()
    assert "foo" in agents
    assert "bar" in agents


def test_load_known_agents_from_db(monkeypatch):
    monkeypatch.delenv("GROVE_KNOWN_AGENTS", raising=False)
    fake_agents = [{"sender": "hanuman"}, {"sender": "heimdallr"}]
    with patch("grove_reader.grove_agents", return_value=fake_agents):
        agents = _load_known_agents()
    assert "hanuman" in agents
    assert "heimdallr" in agents


def test_load_known_agents_db_error_returns_empty(monkeypatch):
    monkeypatch.delenv("GROVE_KNOWN_AGENTS", raising=False)
    with patch("grove_reader.grove_agents", side_effect=Exception("db down")):
        agents = _load_known_agents()
    assert agents == frozenset()


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
