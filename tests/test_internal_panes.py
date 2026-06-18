"""tests/test_internal_panes.py — Home card internal pane helpers."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from panes.routing import fetch_routing
from panes.tasks import fetch_tasks, status_color
from widgets.content_stack import _INTERNAL_PANES


def test_internal_panes_registered():
    assert "#pane-user-todos" in _INTERNAL_PANES
    assert "#pane-tasks" in _INTERNAL_PANES
    assert "#pane-agents" in _INTERNAL_PANES
    assert "#pane-routing" in _INTERNAL_PANES
    assert "#pane-git" in _INTERNAL_PANES
    assert "#pane-prs" in _INTERNAL_PANES
    assert "#pane-mcp" in _INTERNAL_PANES


def test_fetch_tasks_returns_shape():
    data = fetch_tasks()
    assert "pending" in data
    assert "running" in data
    assert "done" in data
    assert isinstance(data["rows"], list)


def test_status_color_running():
    assert status_color("running")  # non-empty string


def test_fetch_routing_returns_list():
    assert isinstance(fetch_routing(limit=1), list)
