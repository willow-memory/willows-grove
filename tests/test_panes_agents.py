"""tests/test_panes_agents.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from panes.agents import agent_state, age_str

def test_agent_state_running():
    assert agent_state(60)   == ("running", "green")

def test_agent_state_idle():
    assert agent_state(300)  == ("idle",    "yellow")

def test_agent_state_stale():
    assert agent_state(1800) == ("stale",   "dim")

def test_agent_state_gone():
    assert agent_state(7200) == ("gone",    "dim")

def test_age_str_seconds():
    assert age_str(45)   == "45s"

def test_age_str_minutes():
    assert age_str(125)  == "2m"

def test_age_str_hours():
    assert age_str(7200) == "2h"
