"""tests/test_content_stack.py — nav pane wiring."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from widgets.content_stack import _REFRESH_TARGETS
from widgets.nav_bar import NAV_TARGETS


def test_refresh_targets_cover_data_panes():
    for target in ("projects", "knowledge", "providers", "settings"):
        assert target in _REFRESH_TARGETS
        assert target in NAV_TARGETS


def test_internal_pane_ids():
    from widgets.content_stack import _INTERNAL_PANES
    assert len(_INTERNAL_PANES) == 9
    assert "#pane-think-map" in _INTERNAL_PANES
