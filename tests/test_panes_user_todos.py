"""tests/test_panes_user_todos.py — My Desk markup regression."""
import asyncio
import os
import sys
from unittest.mock import patch

from textual.app import App, ComposeResult

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from panes.user_todos import UserTodosPane, _BoardFetched


class _DeskApp(App):
    def compose(self) -> ComposeResult:
        yield UserTodosPane(id="pane-user-todos")


def test_my_desk_detail_header_markup_valid():
    """Regression: stray [/] in detail header crashed layout."""

    async def _run() -> None:
        board = {
            "items": [{
                "kind": "todo",
                "id": "abc",
                "title": "Ship [beta] feature",
                "project": "grove",
                "due_date": "2026-05-20",
                "urgency": "overdue",
                "atom_id": "",
                "notes": "from sean",
                "source": "todos",
            }],
            "open_todos": 1,
            "active_projects": 0,
            "overdue": 1,
        }
        app = _DeskApp()
        async with app.run_test(size=(100, 30)) as pilot:
            pane = app.query_one(UserTodosPane)
            pane.on__board_fetched(_BoardFetched(board))
            pane._show_item(board["items"][0])
            await pilot.pause()
            header = app.query_one("#desk-detail-header", Static)
            str(header.render())

    from textual.widgets import Static
    asyncio.run(_run())
