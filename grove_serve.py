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

import json
import os
import subprocess
import threading
from pathlib import Path

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from grove import envelope_reader
from grove import kart_reader
from grove_html import render_page
from grove import journal_writer
from grove import persona_roster
from grove import seed_html
from grove import seed_reader
from grove.nestor_client import NestorClient


_WEB_ROOT = Path(__file__).resolve().parent / "web"


# Static home for the vanilla-JS Web Components (D9: no build step). The rail's
# module tag in grove_html.py resolves to /web/components/grove-dispatch-rail.js;
# StaticFiles hands it directly off the repo tree so a redeploy is a git pull.
_WEB_ROOT = Path(__file__).resolve().parent / "web"


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8766

# Lazy-singleton NestorClient — spinning up `nestor serve` as a subprocess is
# expensive (Python import + MCP handshake), so we reuse one child across
# every /api/nestor/decide call. Guarded by a module-level lock so concurrent
# first requests don't race the constructor. D11: Nestor is the decision
# keeper; Grove is a caller, not a co-author.
_NESTOR_CLIENT: NestorClient | None = None
_NESTOR_CLIENT_LOCK = threading.Lock()


def _get_nestor_client() -> NestorClient:
    """Return the shared, lazily constructed ``NestorClient``.

    The client's own ``available()`` check tells the caller whether the
    ``nestor`` binary is reachable; construction never raises, so we can
    hold a single instance forever and let per-call methods degrade.
    """
    global _NESTOR_CLIENT
    if _NESTOR_CLIENT is None:
        with _NESTOR_CLIENT_LOCK:
            if _NESTOR_CLIENT is None:
                _NESTOR_CLIENT = NestorClient()
    return _NESTOR_CLIENT

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


async def _envelopes(_request: Request) -> JSONResponse:
    """GET /api/envelopes — P1 live envelope registry.

    Additive read-only surface joining the served page to the fleet
    envelope directories (P1 — orchestrator write attestation; D7 —
    graceful degradation). Returns the ``envelope-registry/v1.1``
    payload from ``grove.envelope_reader.read_all()`` verbatim; on
    absent directories the reader emits an empty ``envelopes`` list
    so this route still answers 200 and the panel can render an
    "no envelopes on file" state without a fetch error.
    """
    return JSONResponse(envelope_reader.read_all())


async def _personas(_request: Request) -> JSONResponse:
    """GET /api/personas — the unified persona registry (D10).

    Serves the ``fleet-personas/v1`` document from
    ``willow-memory/willow/fleet_personas.json`` when present, so the
    front-end ``<grove-persona-registry>`` component (and every consumer
    of ``visual.{color,sigil}`` / ``voice``) reads from the same truth
    the Python roster does.

    Per D7 (*absence is a state, not a failure*), a missing registry
    file still answers 200 — the body is an empty-personas envelope so
    the served page keeps booting without the sidecar tree on disk.
    """
    path = persona_roster.locate_personas_file()
    if path is None:
        return JSONResponse(
            {"schema": persona_roster.SCHEMA_ID, "personas": {}}
        )
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, ValueError):
        # File was there at locate time but became unreadable / drifted —
        # degrade the same way D7 does elsewhere.
        return JSONResponse(
            {"schema": persona_roster.SCHEMA_ID, "personas": {}}
        )
    return JSONResponse(data)


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


async def _seed_index(_request: Request) -> HTMLResponse:
    """GET /seed/ — the six-movement onboarding landing page (D16).

    Renders the seed reader's six movements as chapter cards. On any
    absence the reader returns the D16 stub so this route still answers
    200 with a legible page (autonomous-continuity C3 — session
    continuity via seed's six movements must survive absence).
    """
    movements = seed_reader.load_movements()
    return HTMLResponse(seed_html.render_seed_index(movements))


async def _seed_movement(request: Request) -> HTMLResponse:
    """GET /seed/{n} — one movement page, n in 1..6 (D16).

    Any n outside 1..6 answers 404. Prev/next links use ``/seed/<n-1>``
    and ``/seed/<n+1>`` respectively; the ends of the arc get a spacer
    instead of a link.
    """
    raw = request.path_params.get("n", "")
    try:
        n = int(raw)
    except (TypeError, ValueError):
        return HTMLResponse("not found", status_code=404)
    if n < 1 or n > 6:
        return HTMLResponse("not found", status_code=404)

    movements = seed_reader.load_movements()
    by_n = {int(m["n"]): m for m in movements if "n" in m}
    movement = by_n.get(n)
    if movement is None:
        return HTMLResponse("not found", status_code=404)

    prev_url = f"/seed/{n - 1}" if n > 1 else None
    next_url = f"/seed/{n + 1}" if n < 6 else None
    return HTMLResponse(
        seed_html.render_seed_movement(movement, prev_url=prev_url, next_url=next_url)
    )


async def _nestor_decide(request: Request) -> JSONResponse:
    """POST /api/nestor/decide — check a proposed act against Nestor (D11/V5).

    Body: ``{"claim": "<the proposed action or assertion>"}``.

    The client-side ``NestorClient`` returns one of three shapes for
    ``decision_check(claim)``:

    * ``{"verdict": "sealed", "pair": {...}}`` — a matching sealed pair.
    * ``{"verdict": "refused", "refusal": {...}}`` — Nestor's own refusal
      speech act, passed through **verbatim** (V5 — no paraphrase, no
      summary, no truncation, no whitespace "cleanup"). Grove is not the
      author of the refusal; Grove only renders it.
    * ``None`` — no matching sealed decision, or the Nestor binary is
      not reachable. Whether that is the ``pending`` (D7 — absence is a
      state) or ``unavailable`` case is resolved by the client's
      ``available()`` probe.

    Responses:
      200 — ``{"verdict": "sealed"|"refused"|"pending", ...}``.
      400 — ``{"verdict": "invalid", "reason": "claim required"}``.
      503 — ``{"verdict": "unavailable", "reason": "nestor binary not reachable"}``.
    """
    try:
        payload = await request.json()
    except Exception:  # noqa: BLE001 — malformed body is a 400, not a 500
        return JSONResponse(
            {"verdict": "invalid", "reason": "invalid json body"},
            status_code=400,
        )

    claim = payload.get("claim") if isinstance(payload, dict) else None
    if not isinstance(claim, str) or not claim.strip():
        return JSONResponse(
            {"verdict": "invalid", "reason": "claim required"},
            status_code=400,
        )

    client = _get_nestor_client()
    if not client.available():
        return JSONResponse(
            {"verdict": "unavailable", "reason": "nestor binary not reachable"},
            status_code=503,
        )

    result = client.decision_check(claim)
    if result is None:
        # D7: absence of a decision is a valid state, not an error.
        return JSONResponse(
            {"verdict": "pending", "message": "no sealed pair for this claim"},
            status_code=200,
        )

    verdict = result.get("verdict") if isinstance(result, dict) else None
    if verdict == "sealed":
        return JSONResponse(
            {"verdict": "sealed", "pair": result.get("pair")},
            status_code=200,
        )
    if verdict == "refused":
        # V5 discipline: pass the refusal payload through unchanged —
        # no field rename, no truncation, no whitespace cleanup. The
        # bytes on the wire are Nestor's own.
        return JSONResponse(
            {"verdict": "refused", "refusal": result.get("refusal")},
            status_code=200,
        )

    # Unknown/other shape: treat as pending (D7) — Grove never invents a
    # verdict Nestor did not seal.
    return JSONResponse(
        {"verdict": "pending", "message": "no sealed pair for this claim"},
        status_code=200,
    )


def build_app() -> Starlette:
    routes = [
        Route("/", _index),
        Route("/health", _health),
        Route("/api/journal", _journal, methods=["POST"]),
        Route("/api/dispatch", _dispatch),
        Route("/api/envelopes", _envelopes),
        Route("/api/personas", _personas),
        Route("/api/nestor/decide", _nestor_decide, methods=["POST"]),
        Route("/seed/", _seed_index),
        Route("/seed/{n}", _seed_movement),
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
