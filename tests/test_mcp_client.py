"""tests/test_mcp_client.py — MCP stdio client helpers."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from grove.apps.mcp_client import format_tool_result, _stdio_params


def test_stdio_params_merges_env():
    params = _stdio_params({
        "command": "python3",
        "args": ["-m", "grove.mcp_local"],
        "env": {"WILLOW_PG_DB": "willow_20"},
    })
    assert params.command == "python3"
    assert params.args == ["-m", "grove.mcp_local"]
    assert params.env["WILLOW_PG_DB"] == "willow_20"


def test_format_tool_result_pretty_json():
    raw = json.dumps({"ok": True, "n": 2})
    out = format_tool_result(raw)
    assert '"ok": true' in out.lower() or '"ok": True' in out


def test_format_tool_result_truncates():
    out = format_tool_result("x" * 5000, max_len=100)
    assert len(out) <= 100
    assert out.endswith("…")
