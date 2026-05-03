"""panes/mcp.py — MCP server viewer.
b17: WGRV1  ΔΣ=42
"""
import json
from pathlib import Path

from textual import work
from textual.containers import Container
from textual.message import Message
from textual.widgets import DataTable, Label

_MCP_PATHS = [
    Path.home() / ".mcp.json",
    Path(__file__).parent.parent / ".mcp.json",
]


def _read_mcp_servers() -> list[dict]:
    """Read ~/.mcp.json or repo-local .mcp.json. Returns list of server dicts."""
    for path in _MCP_PATHS:
        if path.exists():
            try:
                data = json.loads(path.read_text())
                servers = data.get("mcpServers", {})
                out = []
                for name, cfg in servers.items():
                    cmd = cfg.get("command", "")
                    args = " ".join(str(a) for a in cfg.get("args", []))
                    out.append({"name": name, "command": f"{cmd} {args}".strip()})
                return out
            except Exception as e:
                return [{"name": f"(parse error: {e})", "command": ""}]
    return []


class _MCPFetched(Message):
    def __init__(self, servers: list[dict]) -> None:
        super().__init__()
        self.servers = servers


class MCPPane(Container):
    def compose(self):
        yield Label("  MCP Servers", id="mcp-title")
        table = DataTable(id="mcp-table", cursor_type="row")
        table.add_columns("Server", "Command")
        yield table

    def on_mount(self) -> None:
        self._fetch()

    def refresh_data(self) -> None:
        self._fetch()

    @work(thread=True)
    def _fetch(self) -> None:
        self.post_message(_MCPFetched(_read_mcp_servers()))

    def on__mcp_fetched(self, event: _MCPFetched) -> None:
        from textual.css.query import NoMatches
        try:
            table = self.query_one("#mcp-table", DataTable)
        except NoMatches:
            return
        table.clear()
        if not event.servers:
            table.add_row("[dim]no servers found — check ~/.mcp.json[/]", "")
            return
        for s in event.servers:
            cmd = s["command"][:60] + "…" if len(s["command"]) > 60 else s["command"]
            table.add_row(s["name"], f"[dim]{cmd}[/]")
