"""tests/test_panes_mcp.py — MCP pane messages + mount regression."""
import asyncio
import os
import sys
from unittest.mock import patch

from textual.app import App, ComposeResult
from textual.widgets import DataTable, Static

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from panes.mcp import MCPPane, _McpActionDone, _McpFetched, _McpToolsLoaded
from grove.theme_textual import SECONDARY

_SAMPLE = {
    "count": 2,
    "serve_up": False,
    "config_path": "/tmp/.mcp.json",
    "serve": {"running": False, "pid": None, "port": 8765, "up": False, "log_path": "/tmp/log"},
    "servers": [
        {
            "name": "willow",
            "transport": "stdio",
            "endpoint": "bash /tmp/willow.sh",
            "alive": False,
            "cfg": {"command": "bash", "args": ["willow.sh"]},
        },
        {
            "name": "grove",
            "transport": "stdio",
            "endpoint": "python3 -m grove.mcp_local",
            "alive": True,
            "cfg": {"command": "python3", "args": ["-m", "grove.mcp_local"]},
        },
    ],
}


class _McpTestApp(App):
    def compose(self) -> ComposeResult:
        yield MCPPane(id="pane-mcp")


def test_mcp_fetched_message_carries_summary():
    summary = {"count": 2, "servers": [], "serve_up": False, "config_path": "/x"}
    msg = _McpFetched(summary)
    assert msg.summary["count"] == 2


def test_mcp_fetched_handler_name():
    assert _McpFetched.handler_name == "on__mcp_fetched"


def test_mcp_tools_loaded_handler_name():
    assert _McpToolsLoaded.handler_name == "on__mcp_tools_loaded"


def test_mcp_action_done_handler_name():
    assert _McpActionDone.handler_name == "on__mcp_action_done"


def test_mcp_pane_exposes_refresh():
    assert callable(MCPPane.refresh_data)


def test_mcp_pane_set_result_accepts_markup():
    pane = MCPPane()

    async def _run() -> None:
        app = App()
        app.compose = lambda: [pane]
        async with app.run_test() as pilot:
            await pilot.pause()
            pane._set_result(f"[dim {SECONDARY}]loading…[/]")
            text = str(app.query_one("#mcp-result", Static).render())
            assert "loading" in text

    asyncio.run(_run())


def test_mcp_refresh_tool_count_updates_cell():
    """Regression: Textual auto column keys are None — must use explicit 'tools' key."""

    async def _run() -> None:
        app = _McpTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            pane = app.query_one(MCPPane)
            pane._servers = list(_SAMPLE["servers"])
            pane._selected_server = "grove"
            pane._tools = [{"name": "grove_list_channels", "description": "", "input_schema": {}}]
            pane._apply_summary(_SAMPLE)
            pane._apply_tools(_McpToolsLoaded("grove", pane._tools, None))
            await pilot.pause()
            table = app.query_one("#mcp-servers", DataTable)
            grove_key = pane._server_keys["grove"]
            assert table.get_row(grove_key)[3] == "1"

    asyncio.run(_run())


def test_mcp_pane_mount_populates_servers():
    """Regression: worker fetch must reach on__mcp_fetched and fill rows."""

    async def _run() -> None:
        with patch("panes.mcp.mcp_summary", return_value=dict(_SAMPLE)):
            app = _McpTestApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                header = app.query_one("#mcp-header", Static)
                assert "/tmp/.mcp.json" in str(header.render())
                table = app.query_one("#mcp-servers", DataTable)
                assert table.row_count == 2

    asyncio.run(_run())
