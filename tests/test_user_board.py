"""tests/test_user_board.py — My Desk aggregation."""
import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from grove.apps import user_board


def test_board_summary_empty(monkeypatch):
    monkeypatch.setattr(user_board, "fetch_user_board", lambda **kw: {
        "open_todos": 0, "active_projects": 0, "overdue": 0,
    })
    assert user_board.board_summary() == "your command center"


def test_board_summary_overdue(monkeypatch):
    monkeypatch.setattr(user_board, "fetch_user_board", lambda **kw: {
        "open_todos": 3, "active_projects": 2, "overdue": 1,
    })
    assert "overdue" in user_board.board_summary()


def test_fetch_user_board_sorts_overdue_first(monkeypatch):
    today = date.today()
    yesterday = (today - timedelta(days=1)).isoformat()
    tomorrow = (today + timedelta(days=1)).isoformat()

    monkeypatch.setattr(
        user_board.soil,
        "all_records",
        lambda col: {
            user_board.TODOS_COLLECTION: [
                {"_id": "a", "text": "later", "done": False, "due_date": tomorrow},
                {"_id": "b", "text": "late", "done": False, "due_date": yesterday},
            ],
            user_board.PROJECTS_COLLECTION: [],
        }.get(col, []),
    )
    monkeypatch.setattr(
        "panes.tasks.fetch_tasks",
        lambda: {"rows": []},
    )

    board = user_board.fetch_user_board(limit=10)
    assert board["overdue"] == 1
    assert board["items"][0]["title"] == "late"
    assert board["items"][0]["urgency"] == "overdue"
