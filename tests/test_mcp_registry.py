"""tests/test_mcp_registry.py — MCP config reader."""
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from grove.apps.mcp_registry import list_servers, read_mcp_config, server_count


def test_read_mcp_config_from_repo(tmp_path, monkeypatch):
    cfg = {"mcpServers": {"willow": {"command": "echo"}, "grove": {"url": "http://x/mcp"}}}
    p = tmp_path / ".mcp.json"
    p.write_text(json.dumps(cfg))
    monkeypatch.setenv("MCP_CONFIG", str(p))
    path, data = read_mcp_config()
    assert path == p
    assert "willow" in data["mcpServers"]


def test_list_servers_stdio_and_http(tmp_path, monkeypatch):
    cfg = {
        "mcpServers": {
            "willow": {"command": "bash", "args": ["willow.sh"]},
            "grove": {"url": "http://127.0.0.1:8765/mcp"},
        }
    }
    p = tmp_path / ".mcp.json"
    p.write_text(json.dumps(cfg))
    monkeypatch.setenv("MCP_CONFIG", str(p))
    with patch("grove.apps.mcp_registry.probe_serve_port", return_value=True):
        servers = list_servers()
    assert server_count() == 2
    by_name = {s["name"]: s for s in servers}
    assert by_name["willow"]["transport"] == "stdio"
    assert by_name["grove"]["transport"] == "http"
    assert by_name["grove"]["alive"] is True


def test_server_count_zero_when_missing(monkeypatch, tmp_path):
    monkeypatch.setenv("MCP_CONFIG", str(tmp_path / "missing.json"))
    with patch("grove.apps.mcp_registry.mcp_config_paths", return_value=[tmp_path / "missing.json"]):
        assert server_count() == 0
