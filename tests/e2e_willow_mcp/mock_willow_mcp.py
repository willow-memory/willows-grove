# b17: WGRV1 ΔΣ=42
"""Minimal MCP mock of willow-mcp's ``kb_journal`` read+write tools.

Speaks **MCP Streamable HTTP** at ``/mcp`` — the same transport the real
willow-mcp serves in ``--serve`` mode — not invented REST routes under
``/tools/*``. In-memory only; state dies with the process. This mock
exists so Grove's C11 loop (``docs/design/autonomous-continuity.md`` C11)
can be pinned end-to-end in CI without the real willow-mcp being
reachable.

Protocol surface (mirrors willow-mcp MCP tools):

  * ``kb_journal`` — accepts ``app_id``, ``content``, ``source``, ``tags``.
    Stores an atom keyed by a generated id and returns ``{"id", "ts", "ok": true}``.

  * ``kb_journal_read`` — returns stored atoms newest-first, honoring
    ``limit`` and ``since_id``.

Harness-only HTTP routes (not part of willow-mcp):

  * ``GET /health`` — liveness for the conftest wait-loop.
  * ``POST /kill`` / ``POST /restore`` / ``POST /reset`` — test controls.
"""
from __future__ import annotations

import datetime as _dt
import secrets
import threading
from typing import Any

from mcp.server.mcpserver import MCPServer
from starlette.requests import Request
from starlette.responses import JSONResponse

_TOOL_NAMES = frozenset({"kb_journal", "kb_journal_read"})
_last_store: "_Store | None" = None


class _Store:
    """In-memory atom store guarded by a lock; process-lifetime only."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._atoms: list[dict[str, Any]] = []
        self._killed = False

    def kill(self) -> None:
        with self._lock:
            self._killed = True

    def restore(self) -> None:
        with self._lock:
            self._killed = False

    def is_killed(self) -> bool:
        with self._lock:
            return self._killed

    def reset(self) -> None:
        with self._lock:
            self._atoms = []
            self._killed = False

    def add(self, atom: dict[str, Any]) -> None:
        with self._lock:
            self._atoms.insert(0, atom)

    def snapshot(self) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._atoms)


def _now_iso() -> str:
    return _dt.datetime.now(_dt.UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _new_id() -> str:
    return "atom-" + secrets.token_hex(6)


def get_store() -> _Store:
    """Return the store from the most recent ``build_app()`` call."""
    if _last_store is None:
        build_app()
    assert _last_store is not None
    return _last_store


def tool_names() -> frozenset[str]:
    """MCP tool names this mock registers — for drift pins."""
    return _TOOL_NAMES


def build_app():
    """Build a fresh Starlette app with its own in-memory store."""
    global _last_store
    store = _Store()
    _last_store = store
    mcp = MCPServer("mock-willow-mcp")

    @mcp.tool()
    def kb_journal(
        app_id: str,
        content: str,
        source: str = "",
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        if store.is_killed():
            return {"error": "killed"}
        if not isinstance(content, str) or not content:
            return {"error": "content required"}
        atom_id = _new_id()
        ts = _now_iso()
        atom = {
            "id": atom_id,
            "ts": ts,
            "content": content,
            "source": source if isinstance(source, str) else str(source),
            "tags": list(tags) if isinstance(tags, (list, tuple)) else [],
            "domain": "journal",
        }
        store.add(atom)
        return {"id": atom_id, "ts": ts, "ok": True}

    @mcp.tool()
    def kb_journal_read(
        app_id: str,
        limit: int = 50,
        since_id: str | None = None,
    ) -> list[dict[str, Any]] | dict[str, str]:
        if store.is_killed():
            return {"error": "killed"}
        if not isinstance(limit, int) or limit <= 0:
            limit = 50
        limit = min(limit, 200)
        atoms = store.snapshot()
        if since_id:
            for i, atom in enumerate(atoms):
                if atom.get("id") == since_id:
                    atoms = atoms[:i]
                    break
        return atoms[:limit]

    @mcp.custom_route("/health", methods=["GET"])
    async def health(_request: Request) -> JSONResponse:
        return JSONResponse({"ok": True})

    @mcp.custom_route("/kill", methods=["POST"])
    async def kill(_request: Request) -> JSONResponse:
        store.kill()
        return JSONResponse({"killed": True})

    @mcp.custom_route("/restore", methods=["POST"])
    async def restore(_request: Request) -> JSONResponse:
        store.restore()
        return JSONResponse({"killed": False})

    @mcp.custom_route("/reset", methods=["POST"])
    async def reset(_request: Request) -> JSONResponse:
        store.reset()
        return JSONResponse({"reset": True})

    return mcp.streamable_http_app()


__all__ = ["build_app", "get_store", "tool_names"]
