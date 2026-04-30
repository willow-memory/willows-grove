"""tests/test_panes_home.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from panes.home import (
    DeskData, agent_dot, format_age, mini_bar,
    HOMEGRID_PLACEHOLDER, PROJECTS_PLACEHOLDER,
)

# ── DeskData ──────────────────────────────────────────────────────────────────

def test_desk_data_defaults():
    d = DeskData()
    assert d.unread_channels == []
    assert d.mentions == []
    assert d.open_flags == 0
    assert d.running_tasks == 0
    assert d.pending_tasks == 0
    assert d.done_today == 0
    assert d.backfill is None
    assert d.agents == []
    assert d.sysinfo == {"cpu": 0, "mem": 0, "disk": 0, "temp": 0}

def test_desk_data_custom():
    d = DeskData(running_tasks=3, pending_tasks=7)
    assert d.running_tasks == 3
    assert d.pending_tasks == 7

# ── agent_dot ─────────────────────────────────────────────────────────────────

def test_agent_dot_green():
    assert "[green]" in agent_dot(60)

def test_agent_dot_yellow():
    assert "[yellow]" in agent_dot(300)

def test_agent_dot_dim():
    assert "[dim]" in agent_dot(1000)

# ── format_age ────────────────────────────────────────────────────────────────

def test_format_age_minutes():
    assert format_age(90) == "1m ago"

def test_format_age_hours():
    assert format_age(7200) == "2h ago"

def test_format_age_zero():
    assert format_age(0) == "0m ago"

# ── mini_bar ──────────────────────────────────────────────────────────────────

def test_mini_bar_full():
    assert mini_bar(100) == "█████"

def test_mini_bar_empty():
    assert mini_bar(0) == "░░░░░"

def test_mini_bar_half():
    result = mini_bar(50)
    assert "██" in result
    assert "░░" in result
    assert len(result) == 5

# ── placeholder strings still present ────────────────────────────────────────

def test_homegrid_placeholder_mentions_phase():
    assert "Phase" in HOMEGRID_PLACEHOLDER or "home" in HOMEGRID_PLACEHOLDER.lower()

def test_projects_placeholder_lists_internal_panes():
    text = PROJECTS_PLACEHOLDER.lower()
    for pane in ("tasks", "agents", "routing", "skills", "logs"):
        assert pane in text
