"""grove_serve.py — Willow's Grove served-page skeleton on 127.0.0.1:8766.
b17: WGRV1  ΔΣ=42

Joins the fleet's `gates_serve` pattern (`willow-mcp/src/willow_mcp/gates_serve.py`)
— a small Starlette + uvicorn app bound to loopback, no MCP, no auth of its
own beyond the loopback boundary. Same shape, different port (8766 vs 8767)
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
import sys
import threading
from pathlib import Path

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from grove import envelope_reader
from grove import journal_reader
from grove import kart_reader
from grove_html import render_page
from grove import journal_writer
from grove import persona_roster
from grove import seed_html
from grove import seed_reader
from grove.errors import Unreachable
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

# Optional Kart lens filter values (quiet tooling). C12's operator-facing
# Governance/PM/PA gearshift is demoted (Jarvis addendum); these tokens remain
# for ?lens= on /api/dispatch only. Any other value falls through unfiltered.
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

    Three-state (INVARIANTS.md §1):

    * 200 ``{"state": "populated", "tasks": [...]}`` — rows present.
    * 200 ``{"state": "empty",     "tasks": []}``    — table reached,
      no queued rows.
    * 503 ``{"state": "unreachable", "reason": "<why>"}`` — kart_reader
      raised ``Unreachable`` (missing DSN, missing table, connect
      failure, etc.).
    """
    lens = (request.query_params.get("lens") or "").strip().lower()
    try:
        if lens in _DISPATCH_LENSES:
            rows = kart_reader.read_by_lens(lens)
        else:
            rows = kart_reader.read_queue()
    except Unreachable as e:
        return JSONResponse(
            {"state": "unreachable", "reason": e.reason},
            status_code=503,
        )
    serialized = [_serialize_row(r) for r in rows]
    state = "populated" if serialized else "empty"
    return JSONResponse({"state": state, "tasks": serialized})


async def _envelopes(_request: Request) -> JSONResponse:
    """GET /api/envelopes — P1 live envelope registry.

    Three-state (INVARIANTS.md §1):

    * 200 ``{"state": "populated", "schema": ..., "envelopes": [...]}``
      — one or more envelopes on file.
    * 200 ``{"state": "empty",     "schema": ..., "envelopes": []}``
      — envelope dirs exist but hold no usable files.
    * 503 ``{"state": "unreachable", "reason": "..."}`` — no envelope
      directory found in the probe path.
    """
    try:
        doc = envelope_reader.read_all()
    except Unreachable as e:
        return JSONResponse(
            {"state": "unreachable", "reason": e.reason},
            status_code=503,
        )
    envelopes = doc.get("envelopes", []) if isinstance(doc, dict) else []
    state = "populated" if envelopes else "empty"
    return JSONResponse({"state": state, **doc})


async def _personas(_request: Request) -> JSONResponse:
    """GET /api/personas — the unified persona registry (D10).

    Three-state (INVARIANTS.md §1):

    * 200 ``{"state": "populated", "schema": ..., "personas": {...}}``
      — registry file present, one or more rows.
    * 200 ``{"state": "empty",     "schema": ..., "personas": {}}`` —
      registry file present but empty.
    * 503 ``{"state": "unreachable", "reason": "..."}`` — no
      fleet_personas.json in the probe path.

    Serves the ``fleet-personas/v1`` document verbatim (round-tripped
    from the file bytes, then wrapped with the ``state`` field on top).
    """
    try:
        roster = persona_roster.PersonaRoster.load()
    except Unreachable as e:
        return JSONResponse(
            {"state": "unreachable", "reason": e.reason},
            status_code=503,
        )
    # File was located — round-trip its bytes as before so the endpoint
    # hands back what the file holds, not the reader's PersonaRow dict.
    path = roster.path
    if path is None:
        # Defensive: PersonaRoster with no path is the "empty" shape.
        return JSONResponse(
            {
                "state": "empty",
                "schema": persona_roster.SCHEMA_ID,
                "personas": {},
            }
        )
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, ValueError):
        # File was there at locate time but became unreadable / drifted —
        # translate a mid-flight drop to Unreachable, not empty.
        return JSONResponse(
            {
                "state": "unreachable",
                "reason": f"registry at {path} became unreadable",
            },
            status_code=503,
        )
    # Populated when the roster has rows, empty otherwise.
    state = "populated" if roster.all() else "empty"
    if isinstance(data, dict):
        return JSONResponse({"state": state, **data})
    return JSONResponse(
        {"state": state, "schema": persona_roster.SCHEMA_ID, "personas": data}
    )


async def _journal(request: Request) -> JSONResponse:
    """POST /api/journal — chat card LEFT-side (C11) write endpoint.

    Three-state (INVARIANTS.md §1) — a successful write is always
    populated (there is no empty case for a write):

      200 ``{"state": "populated", "ok": true, "id": ..., "ts": ...}``
      400 ``{"ok": false, "reason": "text required"}`` on bad input.
      503 ``{"state": "unreachable", "ok": false, "reason": "..."}``
          when the writer raises ``Unreachable`` — willow-mcp is not
          reachable, or reached-but-rejected.

    The ``ok`` field is preserved alongside ``state`` for backward
    compatibility with pre-INVARIANTS clients; the client-side Web
    Components read ``state``.
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
    try:
        result = journal_writer.write_operator_turn(text, sender=sender)
    except Unreachable as e:
        return JSONResponse(
            {"state": "unreachable", "ok": False, "reason": e.reason},
            status_code=503,
        )
    return JSONResponse({"state": "populated", **result}, status_code=200)


async def _journal_recent(request: Request) -> JSONResponse:
    """GET /api/journal/recent?limit=<n>&since=<id> — chat card RIGHT-side (C11).

    Three-state (INVARIANTS.md §1):

    * 200 ``{"state": "populated", "atoms": [...]}`` — atoms present.
    * 200 ``{"state": "empty",     "atoms": []}``   — willow-mcp
      reached, nothing new since ``since``.
    * 503 ``{"state": "unreachable", "reason": "..."}`` — willow-mcp
      not reachable via any of the three paths.
    """
    try:
        limit = int(request.query_params.get("limit", "50"))
    except (TypeError, ValueError):
        limit = 50
    if limit <= 0:
        limit = 50
    if limit > 200:
        limit = 200
    since = request.query_params.get("since") or None
    try:
        atoms = journal_reader.read_recent(limit=limit, since_id=since)
    except Unreachable as e:
        return JSONResponse(
            {"state": "unreachable", "reason": e.reason},
            status_code=503,
        )
    state = "populated" if atoms else "empty"
    return JSONResponse({"state": state, "atoms": atoms})


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

    Three-state (INVARIANTS.md §1):

    * 200 ``{"state": "populated", "verdict": "sealed"|"refused"|"pending", ...}``
      — Nestor answered. Every verdict is a real state and is
      populated (there is no distinct empty case here — an unsealed
      claim's answer is ``pending``, which is still Nestor's answer).
    * 400 ``{"verdict": "invalid", "reason": "..."}`` on bad input.
    * 503 ``{"state": "unreachable", "verdict": "unavailable",
      "reason": "..."}`` when the nestor binary is not reachable.

    Preserves the pre-INVARIANTS ``verdict`` vocabulary alongside the
    new ``state`` field for backward compatibility with clients that
    only understand verdicts.
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
            {
                "state": "unreachable",
                "verdict": "unavailable",
                "reason": "nestor binary not reachable",
            },
            status_code=503,
        )

    try:
        result = client.decision_check(claim)
    except Unreachable as e:
        return JSONResponse(
            {
                "state": "unreachable",
                "verdict": "unavailable",
                "reason": e.reason,
            },
            status_code=503,
        )
    if result is None:
        # Nestor reached; no sealed pair for this claim → pending is
        # populated (Nestor's real answer), not empty (INVARIANTS.md §1).
        return JSONResponse(
            {
                "state": "populated",
                "verdict": "pending",
                "message": "no sealed pair for this claim",
            },
            status_code=200,
        )

    verdict = result.get("verdict") if isinstance(result, dict) else None
    if verdict == "sealed":
        return JSONResponse(
            {"state": "populated", "verdict": "sealed", "pair": result.get("pair")},
            status_code=200,
        )
    if verdict == "refused":
        # V5 discipline: pass the refusal payload through unchanged —
        # no field rename, no truncation, no whitespace cleanup. The
        # bytes on the wire are Nestor's own.
        return JSONResponse(
            {"state": "populated", "verdict": "refused", "refusal": result.get("refusal")},
            status_code=200,
        )

    # Unknown/other shape: treat as pending — Grove never invents a
    # verdict Nestor did not seal.
    return JSONResponse(
        {
            "state": "populated",
            "verdict": "pending",
            "message": "no sealed pair for this claim",
        },
        status_code=200,
    )


def build_app() -> Starlette:
    routes = [
        Route("/", _index),
        Route("/health", _health),
        Route("/api/journal", _journal, methods=["POST"]),
        Route("/api/journal/recent", _journal_recent),
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


def _host_looks_invalid(host: str) -> bool:
    """Cheap sanity check on GROVE_SERVE_HOST — not a full hostname/IP
    validator, just a filter for the obviously-wrong values an operator's
    shell can hand us (an empty value, embedded whitespace, a stray URL
    scheme, or a "host:port" pair pasted into the host slot by mistake).

    Bare IPv6 forms (``::1``, ``2001:db8::1``) carry more than one colon
    and are deliberately left alone — only a single, non-leading colon
    (the "host:port" shape) is treated as a mistake.
    """
    if not host or host != host.strip() or " " in host:
        return True
    if "://" in host:
        return True
    if host.count(":") == 1 and not host.startswith(":"):
        return True
    return False


def main() -> None:
    host = os.environ.get("GROVE_SERVE_HOST", DEFAULT_HOST)
    if _host_looks_invalid(host):
        print(
            f"GROVE_SERVE_HOST={host!r} is not a valid host; refusing to start.",
            file=sys.stderr,
        )
        sys.exit(2)

    port_raw = os.environ.get("GROVE_SERVE_PORT", str(DEFAULT_PORT))
    try:
        port = int(port_raw)
    except ValueError:
        print(
            f"GROVE_SERVE_PORT={port_raw!r} is not a valid port; refusing to start.",
            file=sys.stderr,
        )
        sys.exit(2)
    if not (0 < port < 65536):
        print(
            f"GROVE_SERVE_PORT={port_raw!r} is not a valid port; refusing to start.",
            file=sys.stderr,
        )
        sys.exit(2)

    run(host=host, port=port)


if __name__ == "__main__":
    main()
