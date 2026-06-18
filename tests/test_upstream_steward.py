"""tests/test_upstream_steward.py — Grove read-only upstream steward consumer."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture(autouse=True)
def soil_tmp(tmp_path, monkeypatch):
    monkeypatch.setenv("WILLOW_STORE_ROOT", str(tmp_path))


import soil
from grove.apps import upstream_steward


def test_list_pending_empty():
    assert upstream_steward.list_pending() == []


def test_list_pending_skips_closed():
    soil.put(
        upstream_steward.PENDING_COLLECTION,
        "done-1",
        {"work_id": "done-1", "status": "posted", "title": "Old"},
    )
    soil.put(
        upstream_steward.PENDING_COLLECTION,
        "open-1",
        {"work_id": "open-1", "status": "awaiting_human", "title": "Reply needed"},
    )
    pending = upstream_steward.list_pending()
    assert len(pending) == 1
    assert pending[0]["work_id"] == "open-1"


def test_steward_summary_with_pending():
    soil.put(
        upstream_steward.PENDING_COLLECTION,
        "w1",
        {"work_id": "w1", "status": "awaiting_human", "lane": "urgent"},
    )
    soil.put(
        upstream_steward.PENDING_COLLECTION,
        "w2",
        {"work_id": "w2", "status": "awaiting_human"},
    )
    s = upstream_steward.steward_summary()
    assert "2 upstream" in s
    assert "urgent" in s


def test_fetch_digest():
    soil.put(
        upstream_steward.DIGEST_COLLECTION,
        upstream_steward.DIGEST_RECORD_ID,
        {"line": "3 open upstream PRs"},
    )
    status = upstream_steward.fetch_status()
    assert status["digest_line"] == "3 open upstream PRs"


def test_render_upstream():
    from panes.upstream import render_upstream

    text = render_upstream(
        {"pending_count": 1, "urgent_count": 0, "last_poll": "2026-05-24T20:00:00Z"},
        [{"work_id": "w1", "title": "PR review", "repo": "org/repo"}],
    )
    assert "UPSTREAM[/]" in text
    assert "PR review" in text
    assert "willow.sh upstream" in text
