"""tests/test_panes_projects.py — projects SOIL helpers."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from panes import projects


def test_projects_active_count_empty(monkeypatch):
    monkeypatch.setattr(projects.soil, "all_records", lambda _c: [])
    assert projects.projects_active_count() == 0


def test_projects_active_count_active_only(monkeypatch):
    monkeypatch.setattr(
        projects.soil,
        "all_records",
        lambda _c: [
            {"status": "active"},
            {"status": "done"},
            {"status": "active"},
        ],
    )
    assert projects.projects_active_count() == 2
