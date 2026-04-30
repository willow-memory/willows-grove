"""tests/test_widgets_nav_bar.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from widgets.nav_bar import NAV_TARGETS, NavChanged

def test_nav_targets_exact():
    assert NAV_TARGETS == ["home", "chat", "projects", "knowledge",
                           "providers", "health", "settings", "help"]

def test_nav_targets_no_internal_panes():
    for forbidden in ("tasks", "agents", "routing", "skills", "logs", "overview"):
        assert forbidden not in NAV_TARGETS

def test_nav_changed_target():
    msg = NavChanged("chat")
    assert msg.target == "chat"

def test_nav_changed_all_targets():
    for t in NAV_TARGETS:
        msg = NavChanged(t)
        assert msg.target == t
