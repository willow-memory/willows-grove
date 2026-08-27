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

from grove_html import render_page


_WEB_ROOT = Path(__file__).resolve().parent / "web"


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8766


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


def build_app() -> Starlette:
    routes = [
        Route("/", _index),
        Route("/health", _health),
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
