"""tests/test_panes_knowledge_mount.py — Knowledge pane search regression."""
import asyncio
import os
import sys
from unittest.mock import patch

from textual.app import App, ComposeResult

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from panes.knowledge import KnowledgePane, _KbSearchDone


class _KbApp(App):
    def compose(self) -> ComposeResult:
        yield KnowledgePane(id="pane-knowledge")


def test_knowledge_search_hex_ids_no_int_crash():
    """Regression: Willow 2.0 knowledge.id is TEXT (hex), not int."""

    async def _run() -> None:
        sample = [
            {
                "id": "1794CECD",
                "title": "Grove dashboard",
                "summary": "notes",
                "domain": "dev",
                "weight": 1.0,
            }
        ]
        with patch("panes.knowledge.search_kb", return_value=sample):
            with patch("panes.knowledge.fetch_atom", return_value={
                "id": "1794CECD",
                "title": "Grove dashboard",
                "summary": "notes",
                "domain": "dev",
                "weight": 1.0,
                "content": {"ok": True},
            }):
                app = _KbApp()
                async with app.run_test(size=(100, 30)) as pilot:
                    pane = app.query_one(KnowledgePane)
                    pane.on__kb_search_done(_KbSearchDone(sample))
                    await pilot.pause()
                    pane._select_row(0)
                    await pilot.pause()
                    body = app.query_one("#kb-body-text").render()
                    assert "ok" in str(body).lower() or "notes" in str(body)

    asyncio.run(_run())
