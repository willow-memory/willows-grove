# b17: WGRV1 ΔΣ=42
"""Thin Grove-side MCP client for willow-mcp (C11 journal seam).

Grove reaches willow-mcp over the protocol it actually serves — MCP
``tools/call`` — not invented REST routes under ``/tools/*``. Two
transports, chosen in order:

  a. **Streamable HTTP** — when ``WILLOW_MCP_URL`` is set, POST JSON-RPC to
     ``{WILLOW_MCP_URL}/mcp`` (the SDK default ``streamable_http_path``).
  b. **stdio** — spawn a long-lived ``willow-mcp`` child (no ``--serve``)
     and speak newline-delimited JSON-RPC on its pipes, matching
     ``grove/nestor_client.py``.

If neither transport is available, ``call_tool`` returns ``None`` and
callers raise ``Unreachable`` — the honest three-state posture
(``docs/INVARIANTS.md`` §1).

Sync only, no asyncio in callers; HTTP uses ``asyncio.run`` per call.
"""
from __future__ import annotations

import asyncio
import importlib.util
import json
import logging
import os
import shlex
import shutil
import subprocess
import sys
import threading
from typing import Any, Optional

log = logging.getLogger(__name__)

_CALL_TIMEOUT = 30.0
_DEFAULT_INHERITED = ("HOME", "LOGNAME", "PATH", "SHELL", "TERM", "USER", "WILLOW_HOME")


def _resolve_stdio_argv() -> Optional[list[str]]:
    """Return argv to spawn willow-mcp in stdio mode, or ``None``."""
    override = os.environ.get("WILLOW_MCP_COMMAND", "").strip()
    if override:
        return shlex.split(override)
    exe = shutil.which("willow-mcp")
    if exe:
        return [exe]
    extra = os.environ.get("WILLOW_MCP_ARGS", "").strip()
    if importlib.util.find_spec("willow_mcp") is not None:
        argv = [sys.executable, "-m", "willow_mcp"]
        if extra:
            argv.extend(shlex.split(extra))
        return argv
    return None


def _mcp_http_url(base: str) -> str:
    url = base.strip().rstrip("/")
    return url if url.endswith("/mcp") else f"{url}/mcp"


def _unwrap_structured(result: dict[str, Any]) -> Any:
    sc = result.get("structuredContent") or result.get("structured_content")
    if isinstance(sc, dict):
        if "result" in sc:
            return sc["result"]
        return sc
    return _payload_from_content(result.get("content"))


def _parse_stdio_tool_response(resp: Optional[dict[str, Any]]) -> Optional[Any]:
    if not resp or resp.get("error"):
        return None
    result = resp.get("result") or {}
    if result.get("isError"):
        parsed = _unwrap_structured(result)
        if isinstance(parsed, dict) and "error" in parsed:
            return parsed
        return {"error": "tool_error"}
    parsed = _unwrap_structured(result)
    if parsed is not None:
        return parsed
    return _payload_from_content(result.get("content"))


def _payload_from_content(content: Any) -> Optional[Any]:
    if not content:
        return None
    blocks = content if isinstance(content, list) else [content]
    for block in blocks:
        if isinstance(block, dict):
            text = block.get("text")
        else:
            text = getattr(block, "text", None)
        if not isinstance(text, str) or not text.strip():
            continue
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text
    return None


def _parse_async_tool_result(result: Any) -> Optional[Any]:
    if result is None:
        return None
    if getattr(result, "isError", False):
        sc = getattr(result, "structured_content", None)
        if isinstance(sc, dict) and "error" in sc:
            return sc
        parsed = _payload_from_content(getattr(result, "content", None))
        if isinstance(parsed, dict) and "error" in parsed:
            return parsed
        return {"error": "tool_error"}
    sc = getattr(result, "structured_content", None)
    if isinstance(sc, dict):
        if "result" in sc:
            return sc["result"]
        if sc:
            return sc
    return _payload_from_content(getattr(result, "content", None))


class WillowMcpClient:
    """MCP client for willow-mcp — streamable HTTP or stdio child."""

    def __init__(self) -> None:
        self._url = os.environ.get("WILLOW_MCP_URL", "").strip()
        self._stdio_argv = _resolve_stdio_argv()
        self._proc: Optional[subprocess.Popen[str]] = None
        self._lock = threading.Lock()
        self._next_id = 0
        self._session_ready = False
        self._available: Optional[bool] = None

    def available(self) -> bool:
        if self._available is None:
            self._available = bool(self._url) or self._stdio_argv is not None
        return self._available

    def transport_label(self) -> str:
        return "http" if self._url else "stdio"

    def close(self) -> None:
        with self._lock:
            proc = self._proc
            self._proc = None
            self._session_ready = False
        if proc is None:
            return
        try:
            if proc.stdin and not proc.stdin.closed:
                proc.stdin.close()
        except Exception:  # noqa: BLE001
            pass
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except Exception:  # noqa: BLE001
            try:
                proc.kill()
            except Exception:  # noqa: BLE001
                pass

    def _start_stdio(self) -> None:
        if self._url or self._proc is not None and self._proc.poll() is None:
            return
        if not self._stdio_argv:
            return
        env = {k: os.environ[k] for k in _DEFAULT_INHERITED if k in os.environ}
        try:
            self._proc = subprocess.Popen(  # noqa: S603
                self._stdio_argv,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                env=env or None,
            )
        except (FileNotFoundError, OSError) as err:
            log.warning("willow_mcp_client: failed to spawn %r: %s", self._stdio_argv, err)
            self._proc = None
            self._available = False

    def _rpc_stdio(self, method: str, params: dict[str, Any], *, notify: bool = False) -> Optional[dict[str, Any]]:
        with self._lock:
            if self._proc is None or self._proc.poll() is not None:
                self._start_stdio()
            proc = self._proc
            if proc is None or proc.stdin is None or proc.stdout is None:
                return None
            req: dict[str, Any] = {"jsonrpc": "2.0", "method": method, "params": params}
            if not notify:
                self._next_id += 1
                req["id"] = self._next_id
            try:
                proc.stdin.write(json.dumps(req) + "\n")
                proc.stdin.flush()
                if notify:
                    return {}
                line = proc.stdout.readline()
            except (BrokenPipeError, OSError) as err:
                log.warning("willow_mcp_client: stdio transport error on %s: %s", method, err)
                self._session_ready = False
                return None
        if not line:
            return None
        try:
            return json.loads(line)
        except json.JSONDecodeError as err:
            log.warning("willow_mcp_client: bad stdio response for %s: %s", method, err)
            return None

    def _ensure_stdio_session(self) -> bool:
        if self._session_ready:
            return True
        init = self._rpc_stdio(
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "grove-willow-mcp-client", "version": "1.0"},
            },
        )
        if not init or init.get("error"):
            return False
        self._rpc_stdio("notifications/initialized", {}, notify=True)
        self._session_ready = True
        return True

    def _call_stdio(self, name: str, arguments: dict[str, Any]) -> Optional[Any]:
        if not self._ensure_stdio_session():
            return None
        resp = self._rpc_stdio("tools/call", {"name": name, "arguments": arguments})
        return _parse_stdio_tool_response(resp)

    async def _call_http_async(self, name: str, arguments: dict[str, Any]) -> Optional[Any]:
        from mcp import ClientSession
        from mcp.client.streamable_http import streamable_http_client

        url = _mcp_http_url(self._url)
        async with streamable_http_client(url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(name, arguments)
                return _parse_async_tool_result(result)

    def _call_http(self, name: str, arguments: dict[str, Any]) -> Optional[Any]:
        try:
            return asyncio.run(self._call_http_async(name, arguments))
        except Exception as err:  # noqa: BLE001
            log.warning("willow_mcp_client: HTTP tools/call %s failed: %s", name, err)
            return None

    def call_tool(self, name: str, arguments: dict[str, Any]) -> Optional[Any]:
        """Call one willow-mcp tool; return decoded payload or ``None`` on transport failure."""
        if not self.available():
            return None
        if self._url:
            return self._call_http(name, arguments)
        return self._call_stdio(name, arguments)


_client: Optional[WillowMcpClient] = None
_client_lock = threading.Lock()


def get_client() -> WillowMcpClient:
    global _client
    with _client_lock:
        if _client is None:
            _client = WillowMcpClient()
        return _client


def call_tool(name: str, arguments: dict[str, Any]) -> Optional[Any]:
    return get_client().call_tool(name, arguments)


def _reset_client_for_tests() -> None:
    """Drop the module singleton so env changes take effect in tests."""
    global _client
    with _client_lock:
        if _client is not None:
            _client.close()
        _client = None


__all__ = ["WillowMcpClient", "call_tool", "get_client"]
