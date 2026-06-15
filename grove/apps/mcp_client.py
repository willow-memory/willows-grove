"""grove/apps/mcp_client.py — stdio MCP sessions for list/call from the dashboard.
b17: WDASH  ΔΣ=42
"""
from __future__ import annotations

import asyncio
import json
import os
from contextlib import asynccontextmanager
from typing import Any

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

_SESSION_TIMEOUT = 20.0


def _stdio_params(cfg: dict) -> StdioServerParameters:
    command = str(cfg.get("command", "")).strip()
    if not command:
        raise ValueError("server config missing command")
    args = [str(a) for a in cfg.get("args", [])]
    env = {str(k): str(v) for k, v in (cfg.get("env") or {}).items()}
    merged = dict(os.environ)
    merged.update(env)
    if "PYTHONPATH" not in merged and os.environ.get("PYTHONPATH"):
        merged["PYTHONPATH"] = os.environ["PYTHONPATH"]
    return StdioServerParameters(command=command, args=args, env=merged)


@asynccontextmanager
async def _stdio_session(cfg: dict):
    params = _stdio_params(cfg)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await asyncio.wait_for(session.initialize(), timeout=_SESSION_TIMEOUT)
            yield session


async def list_tools_async(cfg: dict) -> list[dict]:
    async with _stdio_session(cfg) as session:
        result = await asyncio.wait_for(session.list_tools(), timeout=_SESSION_TIMEOUT)
        out: list[dict] = []
        for tool in result.tools:
            out.append({
                "name": tool.name,
                "description": tool.description or "",
                "input_schema": tool.inputSchema or {},
            })
        return out


async def call_tool_async(cfg: dict, tool_name: str, arguments: dict[str, Any]) -> str:
    async with _stdio_session(cfg) as session:
        result = await asyncio.wait_for(
            session.call_tool(tool_name, arguments),
            timeout=_SESSION_TIMEOUT,
        )
        parts: list[str] = []
        for block in result.content:
            text = getattr(block, "text", None)
            if text is not None:
                parts.append(text)
            else:
                parts.append(str(block))
        body = "\n".join(parts) if parts else "(empty result)"
        if result.isError:
            return f"ERROR: {body}"
        return body


async def probe_stdio_async(cfg: dict) -> bool:
    try:
        tools = await list_tools_async(cfg)
        return len(tools) > 0
    except Exception:
        return False


def _run(coro):
    return asyncio.run(coro)


def list_tools(cfg: dict) -> tuple[list[dict], str | None]:
    try:
        return _run(list_tools_async(cfg)), None
    except Exception as exc:
        return [], str(exc)


def call_tool(cfg: dict, tool_name: str, arguments: dict[str, Any]) -> tuple[str, str | None]:
    try:
        return _run(call_tool_async(cfg, tool_name, arguments)), None
    except Exception as exc:
        return "", str(exc)


def probe_stdio(cfg: dict) -> bool:
    try:
        return _run(probe_stdio_async(cfg))
    except Exception:
        return False


def format_tool_result(text: str, *, max_len: int = 4000) -> str:
    """Pretty-print JSON tool output when possible."""
    stripped = text.strip()
    if stripped.startswith("{") or stripped.startswith("["):
        try:
            parsed = json.loads(stripped)
            text = json.dumps(parsed, indent=2, default=str)
        except Exception:
            pass
    if len(text) > max_len:
        return text[: max_len - 1] + "…"
    return text
