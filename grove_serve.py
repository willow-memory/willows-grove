"""grove_serve.py — Willow's Grove served-page skeleton on 127.0.0.1:8766.
b17: WGRV1  ΔΣ=42

Joins the fleet's `gates_serve` pattern (`willow-mcp/src/willow_mcp/gates_serve.py`)
— a small Starlette + uvicorn app bound to loopback, no MCP, no auth of its
own beyond the loopback boundary. Same shape, different port (8766 vs 8765)
so it does not collide with `grove-mcp-serve` when both are up.

Two routes for this first pass:

* ``GET /``       — the proof-of-life placeholder page (`grove_html.render_page`).
* ``GET /health`` — ``{"ok": true, "commit": "<git head short sha or 'unknown'>"}``.

The premise doc (D4) sealed served HTML on 127.0.0.1 as the desk-surface
pattern; D9 sealed vanilla JS + Web Components + no build step for the front
end. This module is deliberately empty of behavior — no cards, no chips, no
sockets — so the very first stand-up is a real page over a real port, and
subsequent Gate work fills the inside without re-negotiating the shell.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from grove import kart_reader
from grove_html import render_page
from grove import journal_writer


_WEB_ROOT = Path(__file__).resolve().parent / "web"


# Static home for the vanilla-JS Web Components (D9: no build step). The rail's
# module tag in grove_html.py resolves to /web/components/grove-dispatch-rail.js;
# StaticFiles hands it directly off the repo tree so a redeploy is a git pull.
_WEB_ROOT = Path(__file__).resolve().parent / "web"


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8766

# Lenses the dispatch rail's tri-modal switch understands (C12). Any other
# value falls through to the unfiltered queue.
_DISPATCH_LENSES = {"governance", "pm", "pa"}


def _resolve_commit() -> str:
    """Best-effort short SHA of the current git HEAD.

    Runs `git rev-parse` against the repo root (this file's directory). Falls
    back to ``"unknown"`` if git is not on PATH or the working tree is not a
    repo — /health still answers 200 in that case; it just carries an honest
    ``unknown`` instead of inventing a sha.
    """
    repo_root = Path(__file__).resolve().parent
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_root,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return out or "unknown"
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


async def _index(_request: Request) -> HTMLResponse:
    return HTMLResponse(render_page())


async def _health(_request: Request) -> JSONResponse:
    return JSONResponse({"ok": True, "commit": _resolve_commit()})


def _serialize_row(row: dict) -> dict:
    """JSON-safe copy of a kart row (dates → isoformat strings)."""
    out: dict = {}
    for key, value in row.items():
        if hasattr(value, "isoformat"):
            out[key] = value.isoformat()
        else:
            out[key] = value
    return out


async def _dispatch(request: Request) -> JSONResponse:
    """GET /api/dispatch?lens=<governance|pm|pa> — Kart escalation queue.

    Additive read-only surface joining the served page to the Kart seam
    (C6-C8, C12). The operator picks the drain-tier from the rail; there
    is no auto-drain in v1, so this route emits nothing beyond what the
    Kart producers already put in ``public.tasks``.

    An unknown / missing ``lens`` renders the unfiltered queue. Any
    upstream failure (missing DSN, missing table, missing column) is
    already log-once inside ``kart_reader`` and lands here as ``[]``.
    """
    lens = (request.query_params.get("lens") or "").strip().lower()
    if lens in _DISPATCH_LENSES:
        rows = kart_reader.read_by_lens(lens)
    else:
        rows = kart_reader.read_queue()
    return JSONResponse([_serialize_row(r) for r in rows])


async def _journal(request: Request) -> JSONResponse:
    """POST /api/journal — chat card LEFT-side (C11) write endpoint.

    Accepts JSON ``{"text": "...", "sender": "operator"}``. Delegates to
    ``grove.journal_writer.write_operator_turn`` — which writes the operator's
    words verbatim into willow-mcp's ``kb_journal`` (V5-style discipline: the
    operator's own utterance is load-bearing and must not be reshaped here).

    Responses:
      200 — ``{"ok": true, "id": "<atom>", "ts": "<iso>"}``.
      400 — ``{"ok": false, "reason": "text required"}`` on empty/missing text.
      503 — ``{"ok": false, "reason": "<why>"}`` when the writer degrades
            (willow-mcp not reachable, or reachable-but-rejected). The client
            leaves the text in the composer and the operator retries.
    """
    try:
        payload = await request.json()
    except Exception:  # noqa: BLE001 — malformed body is a 400, not a 500
        return JSONResponse({"ok": False, "reason": "invalid json body"}, status_code=400)

    text = payload.get("text") if isinstance(payload, dict) else None
    sender = payload.get("sender", "operator") if isinstance(payload, dict) else "operator"
    if not isinstance(text, str) or not text.strip():
        return JSONResponse({"ok": False, "reason": "text required"}, status_code=400)
    if not isinstance(sender, str) or not sender:
        sender = "operator"

    # Verbatim discipline: pass `text` unchanged — no strip, no normalize.
    result = journal_writer.write_operator_turn(text, sender=sender)
    if not result.get("ok"):
        return JSONResponse(result, status_code=503)
    return JSONResponse(result, status_code=200)


def build_app() -> Starlette:
    routes = [
        Route("/", _index),
        Route("/health", _health),
        Route("/api/journal", _journal, methods=["POST"]),
        Route("/api/dispatch", _dispatch),
    ]
    # `/web` serves the vanilla-JS Web Components + libs (D9 — no build step).
    # Mounted only when the directory exists so unit tests that import this
    # module from an unusual cwd don't fall over on a missing tree.
    if _WEB_ROOT.is_dir():
        routes.append(Mount("/web", app=StaticFiles(directory=str(_WEB_ROOT)), name="web"))
    return Starlette(routes=routes)


def run(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    """Serve until interrupted (Ctrl-C). Loopback-only by default."""
    import uvicorn

    if host not in ("127.0.0.1", "localhost", "::1"):
        # Grove's served page is a desk-surface, not an internet-facing app.
        # Match gates_serve.py's stance: allow the override, but say so loudly.
        print(
            f"WARNING: binding grove_serve to {host!r}, not localhost — "
            "the desk surface is designed for loopback; a public bind widens "
            "who can see the desk."
        )
    print(f"willow's grove — served page on http://{host}:{port} — Ctrl-C to stop")
    uvicorn.run(build_app(), host=host, port=port, log_level="warning")


def main() -> None:
    host = os.environ.get("GROVE_SERVE_HOST", DEFAULT_HOST)
    port = int(os.environ.get("GROVE_SERVE_PORT", str(DEFAULT_PORT)))
    run(host=host, port=port)


if __name__ == "__main__":
    main()
