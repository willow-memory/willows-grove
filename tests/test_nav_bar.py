"""tests/test_nav_bar.py — wave 2 nav targets."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from widgets.nav_bar import NAV_LABELS, NAV_TARGETS, NavChanged


def test_nav_targets_seven_in_order():
    assert NAV_TARGETS == [
        "home", "chat", "projects", "knowledge",
        "providers", "settings", "help",
    ]


def test_nav_labels_plain_text():
    assert NAV_LABELS["home"] == "Home"
    assert NAV_LABELS["chat"] == "Chat"
    assert all(" " not in v or v == "Knowledge" for v in NAV_LABELS.values())


def test_nav_changed_carries_target():
    msg = NavChanged("projects")
    assert msg.target == "projects"
