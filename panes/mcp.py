"""panes/mcp.py — interactive MCP control: serve lifecycle, tools, calls.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import json
from contextlib import suppress

from rich.markup import escape as _e
from textual import on, work
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.css.query import NoMatches
from textual.message import Message
from textual.widgets import DataTable, Input, Label, Static
from textual.widgets.data_table import RowKey

from grove.apps import mcp_catalog
from grove.apps.mcp_client import call_tool, format_tool_result, list_tools
from grove.apps.mcp_process import restart_serve, serve_status, start_serve, stop_serve
from grove.apps.mcp_registry import get_server, mcp_summary
from grove.theme_textual import ACCENT, DEGRADED, HEALTHY, IDLE, PRIMARY, SECONDARY

_HELP = (
    "s start  x stop  R restart  p probe  t tools  v all-tiers  Enter call  r refresh"
)

# Tools at or below this rank show by default; extended (rank 3) hides until 'v'.
_DEFAULT_MAX_RANK = mcp_catalog.TIER_RANK["standard"]


class _McpFetched(Message):
    def __init__(self, summary: dict) -> None:
        super().__init__()
        self.summary = summary


class _McpToolsLoaded(Message):
    def __init__(self, server: str, tools: list[dict], error: str | None) -> None:
        super().__init__()
        self.server = server
        self.tools = tools
        self.error = error


class _McpCallDone(Message):
    def __init__(self, tool: str, text: str, error: str | None) -> None:
        super().__init__()
        self.tool = tool
        self.text = text
        self.error = error


class _McpActionDone(Message):
    def __init__(self, text: str, ok: bool) -> None:
        super().__init__()
        self.text = text
        self.ok = ok


def _truncate(text: str, n: int) -> str:
    text = text.replace("\n", " ").strip()
    return text if len(text) <= n else text[: n - 1] + "…"


def format_tool_detail(tool: dict) -> str:
    schema = tool.get("input_schema") or {}
    schema_text = json.dumps(schema, indent=2, default=str)
    if len(schema_text) > 700:
        schema_text = schema_text[:699] + "…"
    desc = tool.get("description") or "(no description)"
    return (
        f"[bold {ACCENT}]{_e(tool.get('name', ''))}[/]\n"
        f"[{PRIMARY}]{_e(desc)}[/]\n\n"
        f"[dim {SECONDARY}]schema[/]\n{_e(schema_text)}"
    )


class MCPPane(Container):
    """MCP operator pane — serve control, tool browser, ad-hoc calls."""

    can_focus = True

    BINDINGS = [
        Binding("r", "refresh", "Refresh"),
        Binding("s", "start_serve", "Start"),
        Binding("x", "stop_serve", "Stop"),
        Binding("R", "restart_serve", "Restart"),
        Binding("p", "probe_server", "Probe"),
        Binding("t", "load_tools", "Tools"),
        Binding("v", "toggle_tiers", "All tiers"),
        Binding("enter", "call_tool", "Call", show=False),
        Binding("tab", "focus_next", "Next", show=False),
    ]

    DEFAULT_CSS = f"""
    MCPPane {{
        width: 1fr;
        height: 1fr;
        padding: 0 1;
    }}
    MCPPane #mcp-header {{
        height: auto;
        color: {SECONDARY};
        margin-bottom: 1;
    }}
    MCPPane #mcp-help {{
        height: 1;
        color: {SECONDARY};
        margin-bottom: 1;
    }}
    MCPPane #mcp-status {{
        height: auto;
        color: {PRIMARY};
        margin-bottom: 1;
    }}
    MCPPane #mcp-body {{
        height: 1fr;
    }}
    MCPPane #mcp-servers {{
        width: 38;
        height: 1fr;
        border-right: solid {SECONDARY};
    }}
    MCPPane #mcp-tools {{
        height: 1fr;
    }}
    MCPPane #mcp-tool-detail {{
        height: 8;
        padding: 0 1;
        border-top: solid {SECONDARY};
        color: {PRIMARY};
    }}
    MCPPane #mcp-args-label {{
        height: 1;
        color: {SECONDARY};
    }}
    MCPPane #mcp-args {{
        height: 3;
        margin-bottom: 1;
    }}
    MCPPane #mcp-result-scroll {{
        height: 1fr;
        border-top: solid {SECONDARY};
    }}
    MCPPane #mcp-result {{
        height: auto;
        padding: 0 1;
        color: {PRIMARY};
    }}
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._servers: list[dict] = []
        self._tools: list[dict] = []
        self._selected_server: str | None = None
        self._selected_tool: str | None = None
        self._server_keys: dict[str, RowKey] = {}
        self._tool_keys: dict[str, RowKey] = {}
        self._show_all_tiers: bool = False
        self._drift: dict = {}

    def compose(self):
        yield Label("MCP", id="mcp-title")
        yield Static("", id="mcp-header", markup=True)
        yield Static(_HELP, id="mcp-help")
        yield Static("", id="mcp-status", markup=True)
        with Horizontal(id="mcp-body"):
            servers = DataTable(id="mcp-servers", cursor_type="row")
            servers.add_columns(
                ("Server", "server"),
                ("Tr", "tr"),
                ("St", "status"),
                ("Tools", "tools"),
            )
            yield servers
            with Vertical():
                tools = DataTable(id="mcp-tools", cursor_type="row")
                tools.add_columns(
                    ("Tool", "tool"),
                    ("Group", "group"),
                    ("Tr", "tier"),
                    ("Description", "desc"),
                )
                yield tools
                yield Static("", id="mcp-tool-detail", markup=True)
        yield Label("arguments (JSON)", id="mcp-args-label")
        yield Input("{}", id="mcp-args")
        with VerticalScroll(id="mcp-result-scroll"):
            yield Static(
                "Select a server, press t to load tools, pick a tool, Enter to call.",
                id="mcp-result",
                markup=True,
            )

    def on_mount(self) -> None:
        self.refresh_data()
        with suppress(NoMatches):
            self.query_one("#mcp-servers", DataTable).focus()

    def refresh_data(self) -> None:
        self._fetch_summary()

    def _selected_server_row(self) -> dict | None:
        if not self._selected_server:
            return None
        for s in self._servers:
            if s["name"] == self._selected_server:
                return s
        return get_server(self._selected_server)

    def _selected_tool_row(self) -> dict | None:
        if not self._selected_tool:
            return None
        for t in self._tools:
            if t["name"] == self._selected_tool:
                return t
        return None

    @work(thread=True, exit_on_error=False)
    def _fetch_summary(self) -> None:
        summary = mcp_summary(probe_stdio=False)
        self.post_message(_McpFetched(summary))

    @work(thread=True, exit_on_error=False)
    def _fetch_tools(self, server_name: str, cfg: dict) -> None:
        tools, error = list_tools(cfg)
        self.post_message(_McpToolsLoaded(server_name, tools, error))

    @work(thread=True, exit_on_error=False)
    def _run_call(self, cfg: dict, tool_name: str, arguments: dict) -> None:
        text, error = call_tool(cfg, tool_name, arguments)
        self.post_message(_McpCallDone(tool_name, text, error))

    @work(thread=True, exit_on_error=False)
    def _run_probe(self, server_name: str, cfg: dict) -> None:
        from grove.apps.mcp_client import probe_stdio

        ok = probe_stdio(cfg)
        self.post_message(_McpActionDone(
            f"{server_name}: probe {'OK' if ok else 'failed'}",
            ok,
        ))

    @work(thread=True, exit_on_error=False)
    def _run_serve_action(self, action: str) -> None:
        if action == "start":
            ok, msg = start_serve()
        elif action == "stop":
            ok, msg = stop_serve()
        else:
            ok, msg = restart_serve()
        self.post_message(_McpActionDone(msg, ok))
        self.post_message(_McpFetched(mcp_summary(probe_stdio=False)))

    def on__mcp_fetched(self, event: _McpFetched) -> None:
        try:
            self._apply_summary(event.summary)
        except Exception as exc:
            self._set_result(f"[{DEGRADED}]MCP pane error[/]: {_e(str(exc))}")

    def _apply_summary(self, summary: dict) -> None:
        self._servers = summary.get("servers") or []
        serve = summary.get("serve") or serve_status()
        cfg = summary.get("config_path") or "(no config)"
        if serve.get("running"):
            serve_dot = f"[{HEALTHY}]●[/]" if serve.get("up") else f"[{DEGRADED}]◐[/]"
            pid_s = f"pid {serve.get('pid')}"
        elif serve.get("up"):
            serve_dot = f"[{DEGRADED}]◐[/]"
            pid_s = "port busy (not dashboard-managed)"
        else:
            serve_dot = f"[{IDLE}]○[/]"
            pid_s = "not started — press s"
        header = (
            f"[bold {ACCENT}]MCP control[/]  "
            f"[dim]config[/] {_e(cfg)}"
        )
        status = (
            f"grove serve :{serve.get('port', 8765)} {serve_dot}  "
            f"[dim]{pid_s}[/]  "
            f"[dim]log[/] {_e(serve.get('log_path', ''))}"
        )
        with suppress(NoMatches):
            self.query_one("#mcp-header", Static).update(header)
            self.query_one("#mcp-status", Static).update(status)

        try:
            table = self.query_one("#mcp-servers", DataTable)
        except NoMatches:
            return
        table.clear()
        self._server_keys.clear()
        if not self._servers:
            table.add_row("no servers", "", "", "")
            return
        for s in self._servers:
            dot = "●" if s.get("alive") else "○"
            tool_n = ""
            if s["name"] == self._selected_server and self._tools:
                tool_n = str(len(self._tools))
            key = table.add_row(
                s.get("name", ""),
                s.get("transport", "")[:4],
                dot,
                tool_n,
            )
            self._server_keys[s["name"]] = key
        if not self._selected_server and self._servers:
            self._selected_server = self._servers[0]["name"]
        if self._selected_server and self._selected_server in self._server_keys:
            with suppress(Exception):
                table.move_cursor(row=self._server_keys[self._selected_server])

    def on__mcp_tools_loaded(self, event: _McpToolsLoaded) -> None:
        try:
            self._apply_tools(event)
        except Exception as exc:
            self._set_result(f"[{DEGRADED}]tools UI error[/]: {_e(str(exc))}")

    def _apply_tools(self, event: _McpToolsLoaded) -> None:
        if event.server != self._selected_server:
            return
        if event.error:
            self._set_result(f"[{DEGRADED}]tools error[/]: {_e(event.error)}")
            return
        # Enrich live tools with registry group/tier; compute drift vs the registry.
        self._tools = mcp_catalog.annotate(event.tools)
        self._drift = mcp_catalog.drift([t.get("name", "") for t in self._tools])
        for s in self._servers:
            if s["name"] == event.server:
                s["alive"] = True
                break
        self._refresh_server_tool_counts()
        self._refresh_server_status_dot(event.server)
        self._render_tools(event.server)

    def _visible_tools(self) -> list[dict]:
        """Tier-filtered, sorted tools: by tier rank, then group, then name."""
        tools = self._tools
        if not self._show_all_tiers:
            tools = [
                t for t in tools
                if t.get("tier_rank", _DEFAULT_MAX_RANK) <= _DEFAULT_MAX_RANK
            ]
        return sorted(
            tools,
            key=lambda t: (t.get("tier_rank", 9), t.get("group", ""), t.get("name", "")),
        )

    def _render_tools(self, server: str) -> None:
        try:
            table = self.query_one("#mcp-tools", DataTable)
        except NoMatches:
            return
        table.clear()
        self._tool_keys.clear()
        visible = self._visible_tools()
        for tool in visible:
            mark = "" if tool.get("documented", True) else "·"  # undocumented (drift)
            key = table.add_row(
                tool.get("name", ""),
                _truncate(tool.get("group", ""), 14),
                f"{(tool.get('tier') or '')[:3]}{mark}",
                _truncate(tool.get("description", ""), 48),
            )
            self._tool_keys[tool["name"]] = key
        self._set_result(self._tools_summary(server, len(visible)))
        if visible:
            first = visible[0]["name"]
            self._selected_tool = first
            with suppress(Exception):
                table.move_cursor(row=self._tool_keys[first])
            self._show_tool_detail(visible[0])

    def _tools_summary(self, server: str, shown: int) -> str:
        d = self._drift or {}
        hidden = len(self._tools) - shown
        if self._show_all_tiers or hidden <= 0:
            tier_note = ""
        else:
            tier_note = f"  [dim](+{hidden} extended — v)[/]"
        drift_note = ""
        if d:
            ro, lo = len(d.get("registry_only", [])), len(d.get("live_only", []))
            if ro or lo:
                drift_note = (
                    f"  [dim]drift:[/] [{DEGRADED}]{lo} undocumented[/]"
                    f" · [{SECONDARY}]{ro} stale-doc[/]"
                )
            else:
                drift_note = f"  [{HEALTHY}]registry ✓[/]"
        return (
            f"[{PRIMARY}]{len(self._tools)} tools[/] on [bold]{_e(server)}[/]"
            f"{tier_note}{drift_note}"
        )

    def on__mcp_call_done(self, event: _McpCallDone) -> None:
        if event.error:
            self._set_result(f"[{DEGRADED}]call failed[/]: {_e(event.error)}")
            return
        body = format_tool_result(event.text)
        self._set_result(
            f"[bold {ACCENT}]{_e(event.tool)}[/]\n{_e(body)}",
        )

    def on__mcp_action_done(self, event: _McpActionDone) -> None:
        color = HEALTHY if event.ok else DEGRADED
        self._set_result(f"[{color}]{_e(event.text)}[/]")

    @on(DataTable.RowHighlighted, "#mcp-servers")
    def _on_server_highlight(self, event: DataTable.RowHighlighted) -> None:
        if event.row_key is None:
            return
        try:
            name = str(event.data_table.get_row(event.row_key)[0])
        except Exception:
            return
        if name == "no servers" or name == self._selected_server:
            return
        self._selected_server = name
        self._tools = []
        self._selected_tool = None
        with suppress(NoMatches):
            self.query_one("#mcp-tools", DataTable).clear()
            self.query_one("#mcp-tool-detail", Static).update("")
        self.action_load_tools()

    @on(DataTable.RowHighlighted, "#mcp-tools")
    def _on_tool_highlight(self, event: DataTable.RowHighlighted) -> None:
        if event.row_key is None:
            return
        try:
            name = str(event.data_table.get_row(event.row_key)[0])
        except Exception:
            return
        tool = next((t for t in self._tools if t["name"] == name), None)
        if not tool:
            return
        self._selected_tool = name
        self._show_tool_detail(tool)

    def _show_tool_detail(self, tool: dict) -> None:
        with suppress(NoMatches):
            self.query_one("#mcp-tool-detail", Static).update(format_tool_detail(tool))

    def _set_result(self, text: str) -> None:
        with suppress(NoMatches):
            self.query_one("#mcp-result", Static).update(text)

    def _refresh_server_tool_counts(self) -> None:
        if not self._selected_server or self._selected_server not in self._server_keys:
            return
        with suppress(Exception):
            table = self.query_one("#mcp-servers", DataTable)
            table.update_cell(
                self._server_keys[self._selected_server],
                "tools",
                str(len(self._tools)),
            )

    def _refresh_server_status_dot(self, server_name: str) -> None:
        if server_name not in self._server_keys:
            return
        alive = any(s.get("alive") for s in self._servers if s["name"] == server_name)
        with suppress(Exception):
            table = self.query_one("#mcp-servers", DataTable)
            table.update_cell(
                self._server_keys[server_name],
                "status",
                "●" if alive else "○",
            )

    def action_refresh(self) -> None:
        self.refresh_data()

    def action_toggle_tiers(self) -> None:
        """Show/hide extended-tier tools (the long tail)."""
        self._show_all_tiers = not self._show_all_tiers
        if self._selected_server and self._tools:
            self._render_tools(self._selected_server)

    def action_start_serve(self) -> None:
        self._set_result(f"[dim {SECONDARY}]starting grove serve…[/]")
        self._run_serve_action("start")

    def action_stop_serve(self) -> None:
        self._set_result(f"[dim {SECONDARY}]stopping grove serve…[/]")
        self._run_serve_action("stop")

    def action_restart_serve(self) -> None:
        self._set_result(f"[dim {SECONDARY}]restarting grove serve…[/]")
        self._run_serve_action("restart")

    def action_probe_server(self) -> None:
        server = self._selected_server_row()
        if not server:
            self._set_result(f"[{DEGRADED}]select a server first[/]")
            return
        cfg = server.get("cfg") or {}
        if server.get("transport") != "stdio":
            self._set_result(f"[{DEGRADED}]probe only works for stdio servers[/]")
            return
        self._set_result(f"[dim {SECONDARY}]probing {_e(server['name'])}…[/]")
        self._run_probe(server["name"], cfg)

    def action_load_tools(self) -> None:
        server = self._selected_server_row()
        if not server:
            if self._servers:
                self._selected_server = self._servers[0]["name"]
                server = self._servers[0]
            else:
                self._set_result(f"[{DEGRADED}]no servers in config[/]")
                return
        cfg = server.get("cfg") or {}
        if server.get("transport") != "stdio":
            self._set_result(
                f"[{DEGRADED}]tool browser uses stdio spawn — "
                f"{_e(server['name'])} is {server.get('transport')}[/]"
            )
            return
        self._set_result(f"[dim {SECONDARY}]loading tools for {_e(server['name'])}…[/]")
        self._fetch_tools(server["name"], cfg)

    def action_call_tool(self) -> None:
        focused = self.app.focused
        with suppress(NoMatches):
            if focused and focused.id == "mcp-args":
                self._execute_call()
                return
        with suppress(NoMatches):
            if focused and focused.id == "mcp-tools":
                self._execute_call()
                return
        server = self._selected_server_row()
        tool = self._selected_tool_row()
        if not server or not tool:
            self._set_result(f"[{DEGRADED}]select server + tool first (t to load)[/]")
            return
        with suppress(NoMatches):
            self.query_one("#mcp-args", Input).focus()

    def _execute_call(self) -> None:
        server = self._selected_server_row()
        tool = self._selected_tool_row()
        if not server or not tool:
            self._set_result(f"[{DEGRADED}]select server + tool first[/]")
            return
        cfg = server.get("cfg") or {}
        raw = self.query_one("#mcp-args", Input).value.strip() or "{}"
        try:
            arguments = json.loads(raw)
        except json.JSONDecodeError as exc:
            self._set_result(f"[{DEGRADED}]invalid JSON[/]: {_e(str(exc))}")
            return
        if not isinstance(arguments, dict):
            self._set_result(f"[{DEGRADED}]arguments must be a JSON object[/]")
            return
        self._set_result(
            f"[dim {SECONDARY}]calling {_e(tool['name'])} on {_e(server['name'])}…[/]"
        )
        self._run_call(cfg, tool["name"], arguments)
