# Willow's Grove — the served page (operator guide)

b17: WGRV1 ΔΣ=42

Audience: the operator sitting at Grove.

## What Grove is

Willow's Grove is the operator's seat: a small served HTML page bound to
`http://127.0.0.1:8766` that Willow renders from her side of the desk and
summons cards (chat, dispatch, envelopes, refusals) *from the edges* only
when they are needed. It is not a dashboard the operator visits; it is the
seat the operator sits at. The premise doc's workshop metaphor — Iron
Man's workshop as motif, Willow at the always-present anchor, fleet
members reached through her — is the design rationale: see
[`design/willow-grove-premise.md`](design/willow-grove-premise.md) **D14**
(OS-like pop-out with a visible home edge) and the *Aesthetic direction*
section for the composed-not-built stance the whole page inherits.

## Run it

```
./scripts/grove-serve-run
```

Foreground process. Loopback-only by default. Ctrl-C stops it. For a
persistent unit see `deploy/grove-serve.service.template` and the
`scripts/grove-serve` toggle.

The wrapper resolves the interpreter (`GROVE_VENV`, then `.venv`, then
`python3` on PATH), exports `WILLOW_HUMAN_ORCHESTRATOR=1`, and execs
`python3 -m grove_serve`. Overrides:

| Env var | Default | Read by | What it changes |
|---|---|---|---|
| `GROVE_SERVE_HOST` | `127.0.0.1` | [`grove_serve.py`](../grove_serve.py) | Bind host. Non-loopback prints a warning — the seat is designed for the desk, not the internet. |
| `GROVE_SERVE_PORT` | `8766` | [`grove_serve.py`](../grove_serve.py) | Bind port. `8765` is `grove-mcp-serve`; do not collide. |
| `WILLOW_HOME` | *(none)* | [`grove/envelope_reader.py`](../grove/envelope_reader.py), [`grove/persona_roster.py`](../grove/persona_roster.py), [`grove/nestor_client.py`](../grove/nestor_client.py) | Per-node override root. Highest-priority location for `envelopes/`, `fleet_personas.json`, and `nestor/` state. |
| `WILLOW_MCP_URL` | *(none)* | [`grove/journal_writer.py`](../grove/journal_writer.py) | If set, chat writes POST to `{WILLOW_MCP_URL}/tools/kb_journal`. Absent → in-process `willow_mcp.server` import; failing that → 503. |
| `WILLOW_DB_URL` | *(none)* | [`grove/kart_reader.py`](../grove/kart_reader.py) | Postgres DSN for the Kart escalation queue (`public.tasks`). Absent → dispatch rail returns `[]` (log-once). |
| `GROVE_VENV` | *(none)* | [`scripts/grove-serve-run`](../scripts/grove-serve-run) | Alternate venv root for the launcher. |

## What you see on the page

Every surface below is on the same served origin. Backend calls go through
the routes registered in [`grove_serve.py`](../grove_serve.py); the front end
is vanilla JS + Web Components loaded from `/web/components/` (no build step,
D9).

| Surface | Route / component | Backend it needs | What it does |
|---|---|---|---|
| Ambient top strip | rendered by [`grove_html.py`](../grove_html.py); status dot polls `GET /health` | `grove_serve.py` itself | Willow-name, live dot, commit sha. One glance to see the seat is up. |
| Lens switch | [`web/components/grove-lens-switch.js`](../web/components/grove-lens-switch.js) | none (client-side state); drives `/api/dispatch?lens=` | Tri-modal switch (Governance / PM / PA) — the lens the operator is looking through. |
| Chat card | [`web/components/grove-chat.js`](../web/components/grove-chat.js) | `POST /api/journal` → [`grove/journal_writer.py`](../grove/journal_writer.py) → willow-mcp `kb_journal` | LEFT side (operator → Willow) writes the operator's words verbatim into the journal. |
| Dispatch rail | [`web/components/grove-dispatch-rail.js`](../web/components/grove-dispatch-rail.js) | `GET /api/dispatch?lens=` → [`grove/kart_reader.py`](../grove/kart_reader.py) → Postgres `public.tasks` | Kart escalation queue, filtered by the current lens. |
| Envelope panel | [`web/components/grove-envelope-panel.js`](../web/components/grove-envelope-panel.js) | `GET /api/envelopes` → [`grove/envelope_reader.py`](../grove/envelope_reader.py) | P1 live envelope-registry view; renders "no envelopes on file" when absent. |
| Nestor refusal chip | [`web/components/grove-refusal-chip.js`](../web/components/grove-refusal-chip.js) | [`grove/nestor_client.py`](../grove/nestor_client.py) (via the panel host) | Shows the *reason* a Nestor pair refused, in Nestor's voice — never paraphrased. |
| Cast chips | [`web/components/grove-cast-chip.js`](../web/components/grove-cast-chip.js) + [`grove-persona-registry.js`](../web/components/grove-persona-registry.js) | `GET /api/personas` → [`grove/persona_roster.py`](../grove/persona_roster.py) | Ambient fleet-member chips carrying persona color, sigil, and voice from the unified registry (D10). |

## Tri-modal lens

The lens switch is a filter on the Kart queue, not a workspace divider —
see [`design/autonomous-continuity.md`](design/autonomous-continuity.md)
**C12**. **Governance** shows L4-authority-needed items, envelope
re-attestation reminders, and Nestor refusal chips. **PM** shows
L2/L3-authority-needed items, unclaimed roster items, and outstanding
proposals. **PA** shows L1-authority-needed items, upcoming `send_later`
reminders, and the operator's own drafts. One queue, three lenses on it.

## What happens on a cold box

Grove degrades absence-by-absence (premise D7: *absence is a state, not a
failure*).

- **Postgres not reachable / `WILLOW_DB_URL` unset** — `kart_reader` logs
  once and returns `[]`. Dispatch rail renders empty. Grove still boots.
- **willow-mcp not reachable** — chat card `POST /api/journal` returns
  `503 {"ok": false, "reason": "..."}`. The client leaves the text in
  the composer and the operator retries. The rest of the page keeps
  working.
- **`fleet_personas.json` missing** — `/api/personas` answers 200 with
  an empty-personas envelope. Cast chips fall back to bare `fleet.json`.
- **`envelopes/` missing** — `/api/envelopes` answers 200 with an empty
  list. Envelope panel renders "no envelopes on file".
- **`git` not on PATH / not a repo** — `/health` still answers 200; the
  `commit` field carries `"unknown"` rather than a fabricated sha.

The page never hard-fails on a missing sidecar. It says what is missing
and keeps the seat usable.

## Ports and portless

The house rule (`CLAUDE.md` rule 1) is *no web ports for the dashboard —
portless means portless*. The Textual dashboard (`app.py`, `grove/`) is
still portless and always will be. The served page is a **separate,
narrower surface** whose port was renegotiated by premise **D4** for the
desk-surface use case: loopback-only (`127.0.0.1:8766`) HTML that Willow
serves from her side of the seat. Binding to a non-loopback host still
runs, but prints a warning — the seat is designed for the desk, not the
internet.

## What's still ahead

The resident watcher process and its Gate 5 seal — a local Ollama model
that acts as the seat's at-rest actor, with Kart as the escalation seam
to bigger models — is the next big piece. See
[`design/autonomous-continuity.md`](design/autonomous-continuity.md)
**C4-C5**.
