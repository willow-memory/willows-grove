"""tests/test_panes_home.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from panes.home import DESK_PLACEHOLDER, HOMEGRID_PLACEHOLDER, PROJECTS_PLACEHOLDER

def test_desk_placeholder_is_string():
    assert isinstance(DESK_PLACEHOLDER, str)
    assert len(DESK_PLACEHOLDER) > 0

def test_homegrid_placeholder_mentions_phase():
    assert "Phase" in HOMEGRID_PLACEHOLDER or "home" in HOMEGRID_PLACEHOLDER.lower()

def test_projects_placeholder_lists_internal_panes():
    text = PROJECTS_PLACEHOLDER.lower()
    for pane in ("tasks", "agents", "routing", "skills", "logs"):
        assert pane in text, f"Expected '{pane}' in ProjectsGrid placeholder"
