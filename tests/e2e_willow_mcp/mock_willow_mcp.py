# b17: WGRV1 ΔΣ=42
"""Minimal Starlette mock of willow-mcp's ``kb_journal`` read+write.

Just enough to satisfy the contracts Grove's ``journal_writer`` and
``journal_reader`` speak — no auth, no persistence, no schema
validation. In-memory only; state dies with the process. This mock
exists so Grove's C11 loop (``docs/design/autonomous-continuity.md``
C11) can be pinned end-to-end in CI without the real willow-mcp being
reachable — see ``docs/INVARIANTS.md`` §1 (three-state) and §10 (CI
proves the invariants).

Protocol surface (mirrors willow-mcp's tool routes):

  * ``POST /tools/kb_journal`` — accepts a JSON body
    ``{"app_id", "content", "source", "tags"}`` matching the payload
    ``grove/journal_writer.py`` builds. Stores an atom keyed by a
    generated id and returns ``{"id", "ts", "ok": true}``.

  * ``GET|POST /tools/kb_journal_read`` — returns stored atoms
    newest-first, honoring ``limit`` and ``since_id`` (query params
    on GET, JSON body on POST — the reader in ``grove/journal_reader.py``
    speaks GET; POST is accepted for tests that want to inspect it).
    The response is a bare list of atom dicts — the shape
    ``_atoms_from_payload`` accepts.

  * ``POST /kill`` — flips a kill flag so both journal endpoints
    return 503 until ``POST /restore`` is called. Lets tests exercise
    the "unreachable" state distinctly from the empty state.

  * ``POST /restore`` — clears the kill flag. Idempotent.

Runs on an ephemeral port picked by the harness in ``conftest.py``.

Sync only — stdlib + Starlette match the rest of ``grove_serve.py``.
"""
from __future__ import annotations

import datetime as _dt
import secrets
import threading
from typing import Any

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route


class _Store:
    """In-memory atom store guarded by a lock; process-lifetime only.

    Atoms are stored newest-first — new writes are prepended so a bare
    read (no filter) yields the natural order the reader expects.
    """

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
    """Timezone-aware UTC ISO 8601 with a trailing ``Z`` — matches the writer."""
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _new_id() -> str:
    """Short random atom id. Good enough for tests; no collision guard needed."""
    return "atom-" + secrets.token_hex(6)


def build_app() -> Starlette:
    """Build a fresh Starlette app with its own store.

    Each harness call gets an isolated store — tests do not step on
    each other's atoms even when the module is imported once per
    interpreter.
    """
    store = _Store()

    async def kb_journal_write(request: Request) -> JSONResponse:
        """POST /tools/kb_journal — accept an atom, return its id."""
        if store.is_killed():
            return JSONResponse({"error": "killed"}, status_code=503)
        try:
            body = await request.json()
        except Exception:  # noqa: BLE001 — any decode failure is a bad request
            return JSONResponse({"error": "bad json"}, status_code=400)
        if not isinstance(body, dict):
            return JSONResponse({"error": "expected object"}, status_code=400)
        content = body.get("content")
        source = body.get("source") or ""
        tags = body.get("tags") or []
        if not isinstance(content, str) or not content:
            return JSONResponse({"error": "content required"}, status_code=400)
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
        return JSONResponse({"id": atom_id, "ts": ts, "ok": True})

    async def kb_journal_read(request: Request) -> JSONResponse:
        """GET|POST /tools/kb_journal_read — return atoms newest-first.

        Grove's ``journal_reader`` sends this as GET with query params;
        the mock also accepts POST for tests that prefer JSON bodies.
        """
        if store.is_killed():
            return JSONResponse({"error": "killed"}, status_code=503)

        limit = 50
        since_id: str | None = None

        if request.method == "POST":
            try:
                body = await request.json()
            except Exception:  # noqa: BLE001
                body = {}
            if isinstance(body, dict):
                if isinstance(body.get("limit"), int):
                    limit = body["limit"]
                if isinstance(body.get("since_id"), str):
                    since_id = body["since_id"] or None
        else:
            qp = request.query_params
            try:
                limit = int(qp.get("limit", "50"))
            except (TypeError, ValueError):
                limit = 50
            since_id = qp.get("since_id") or None

        if limit <= 0:
            limit = 50
        if limit > 200:
            limit = 200

        atoms = store.snapshot()  # already newest-first
        if since_id:
            # Trim to strictly newer than since_id. If the id is not in
            # the store (rotation / stale cursor) return everything —
            # same posture as the reader's own _apply_since.
            for i, atom in enumerate(atoms):
                if atom.get("id") == since_id:
                    atoms = atoms[:i]
                    break
        return JSONResponse(atoms[:limit])

    async def kill(_request: Request) -> JSONResponse:
        """POST /kill — flip the kill flag on both endpoints."""
        store.kill()
        return JSONResponse({"killed": True})

    async def restore(_request: Request) -> JSONResponse:
        """POST /restore — clear the kill flag."""
        store.restore()
        return JSONResponse({"killed": False})

    async def reset(_request: Request) -> JSONResponse:
        """POST /reset — wipe stored atoms and clear the kill flag.

        Not part of the willow-mcp protocol; a test-only convenience so
        the conftest fixture can hand each test a clean store without
        rebuilding the whole uvicorn server.
        """
        store.reset()
        return JSONResponse({"reset": True})

    async def health(_request: Request) -> JSONResponse:
        """GET /health — plain liveness check for the harness's wait-loop."""
        return JSONResponse({"ok": True})

    routes = [
        Route("/health", health, methods=["GET"]),
        Route("/tools/kb_journal", kb_journal_write, methods=["POST"]),
        Route("/tools/kb_journal_read", kb_journal_read, methods=["GET", "POST"]),
        Route("/kill", kill, methods=["POST"]),
        Route("/restore", restore, methods=["POST"]),
        Route("/reset", reset, methods=["POST"]),
    ]
    app = Starlette(routes=routes)
    # Expose the store for direct inspection in same-process tests.
    app.state.store = store
    return app


__all__ = ["build_app"]
