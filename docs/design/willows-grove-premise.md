# Willows' Grove — the operator seat, composed not built

b17: WGRV1 ΔΣ=42
Status: **PROPOSED** — Heimdallr proposes, USER ratifies (CLAUDE.md rule 5). No code changed by this note.

## The reframe

Old: **Willow Grove** — the dashboard for Willow (singular tree, singular app).
New: **Willows' Grove** — the seat where the many willows (the fleet's agents) gather under the constitution.

The willows are the fleet: the 16 agents catalogued in
`willow-memory/willow/fleet.json`, plus the Bureau's characters (Jeles,
Oakenscroll, Ofshield, Binder, Pigeon, Gerald, Hanz), Nestor's refusal
voice, and the willow-mcp specialists (Hanuman, Loki, Ada, Skirnir,
Vishwakarma). The grove is where they meet. The seat is the operator's
post within it.

## What Willows' Grove is

The **Operator Jarvis seat**, rendered as a tri-modal desk that consumes
the fleet's already-existing surfaces without re-implementing them.

The tri-modal shape is not new. It is already stated in
`willow-memory/willow/ORIENT.md`:

| Office | Question | Where it looks |
|---|---|---|
| **Governance** | may we? who witnessed it? | `envelopes/pre-approved.json`, `human_required` queue, Constitutional Review queue |
| **PM** | what's in flight, by when, done how? | `fleet.json`, `dispatch_list`, WO-1/WO-2, envelope meters |
| **PA** | what does the operator need, when? | `pa/*` SOIL commitments, one prioritized card, protect operator attention |

The Grove desktop is a single canvas where the operator switches lenses.
Everything the desk shows is fetched, not synthesized.

## Why "composed, not built"

Every load-bearing piece already exists somewhere in the fleet. Willows'
Grove is a page that binds them; not a system that replaces them.

| Piece | Where it lives | Grove's relationship |
|---|---|---|
| Persona roster | `willow-memory/willow/fleet.json` (+ `safe-app-store/apps/bureau/data/professors/*.json`, `willow-mcp/src/willow_mcp/bundle/config/specialists.json`, `nestor.persona.Persona`) | reads |
| Fleet presence seam | `safe-app-store/libs/fleet-presence/src/fleet_presence/__init__.py` — `announce/roster/withdraw` over `~/.willow/store/fleet/store.db` | announces + polls |
| Dispatch API | `willow-mcp` — 7 tools (`dispatch_send/read/list/accept`, `handoff_write_v4`, `verify_handoff`, `agent_clear`); HMAC-signed packets under `$WILLOW_HOME/dispatch/{id}/` | calls |
| Grove data API | `willow-mcp` — 20 `grove_*` tools (`grove_fleet_status`, `grove_agents`, `grove_human_required`, `grove_bus_*`, `grove_list_channels`, `grove_get_history`, `grove_search`, …) | calls |
| Memory (facts, reminders) | `safe-app-store/apps/jarvis` — IndexedDB fact store with compound indices, IDF ranking, alias bridging, `supersedes`, absence-as-fact | calls handlers (`remember/recall/forget/set_reminder`) |
| Decisions / evidence / warrants / ledger / refusal voice | Nestor (`pip install nestor-meaning`) — CLI + Python API + `nestor serve` MCP over stdio | embeds or calls |
| Constitution + Trace IDs | `willow-memory/willow/CONSTITUTION.md` — Draft 0.7, 13 Articles, `CONST-*` | renders |
| Envelopes (active grants + expiry + meter) | `willow-memory/willow/envelopes/pre-approved.json` | renders |
| Voice ingress pipeline | `willow-mcp/src/willow_mcp/voice/` — WO-1 in flight; `hey_jarvis` already a wake option | listens for events |
| Commitment / calendar membrane | `willow-mcp/src/willow_mcp/commitments/` — WO-2 in flight | listens for events |
| Ratatosk sessions | `safe-app-store/apps/ratatosk` — already posts `session_started`/`session_ended` to a Grove channel | listens |
| The willow hero | `safe-app-willow-grove/widgets/hero.py` + `widgets/hero_scene.py` — ASCII willow, meadow, Gerald, pigeon, blooms, wind, per-character color | ports to SVG + `<pre>` |
| Served-HTML precedent | `willow-mcp/src/willow_mcp/gates_serve.py` — 127.0.0.1 + OAuth 2.1 PKCE + polling refresh | mirrors pattern |
| Nestor UI | `nestor ui` — Queue / Memory / Ask / Signals / Ledger / Graph (Cytoscape) | embeds under Governance lens |
| Aesthetic explorations | `willow-mcp/docs/design/willow-*.html` — 10 direction sketches | draws on |

## The build (the very small part)

1. **One HTML page**, served on 127.0.0.1 under the `gates_serve` pattern —
   the tri-modal canvas. Structure, not novel plumbing.
2. **The tri-modal switch** — Governance / PM / PA as browser state
   (localStorage / URL fragment) + one toggle affordance.
3. **Layout memory** — which panels are up, where, per-operator. Browser
   state plus a small SOIL record.
4. **The unified persona-roster mint** — a merge script that reads Bureau
   JSONs + `specialists.json` + `fleet.json` + Nestor persona + Heimdallr
   and normalizes to `{name, domain, voice_register, emit_fields}`. Once
   written, everyone reads it; nobody has to build it again.
5. **The seat's `announce("grove", …)` call** — Grove contributes its own
   presence to `fleet-presence`. A few lines.
6. **The `WILLOW_HUMAN_ORCHESTRATOR=1` env** — Grove sets this to be
   recognized as the operator seat.
7. **Grove's Postgres-reads → `grove_*` MCP tool migration** —
   incremental, pane by pane, existing behavior preserved. Real work, but
   *migration* work, not new logic.

The seat writes no code (magistrate-writes-no-code, per
`willow-memory/willow/design/jarvis-build-orders.md:26`). This makes literal
sense once the map is drawn — the code is already written across willow-mcp,
safe-app-store, Nestor, and fleet-presence. The seat's job is to bind and
render, not build.

## Composition sketch — what each surface renders

| Grove surface | What it fetches | How it renders |
|---|---|---|
| **The willow (arc reactor)** | none — local animation | port `widgets/hero.py` frames to `<pre>` + CSS sway; preserve per-character coloring and every easter egg (Gerald at midnight, pigeon walker, 1:42, hotdog at 0.318, blooms cycling) |
| **Persona horizon (the cast)** | `grove_fleet_status` + `fleet-presence.roster()` + unified `fleet_personas.json` | small glyphs per persona, state color from `ui_state`, dimming from heartbeat age; hover surfaces voice, click summons the persona's panel |
| **Envelope panel** (Governance) | `envelopes/pre-approved.json` | expiry countdown, meter (`current/max`), grantee, constitutional-article link, `enforced_by` reference |
| **Human_required queue** (Governance) | `grove_human_required()` | Heimdallr's Gjallarhorn — muted when quiet, alarm when populated; each row cites its blocking decision |
| **Dispatch rail** (PM) | `dispatch_list()` | state-colored transitions (`pending → working → complete → verified → cleared`); `unverified[]` red |
| **Fleet status** (PM) | `grove_fleet_status` + `grove_agents` | one row per agent from `fleet.json`; presence + what each is doing (`ui_state`, `blocked`, `correlation_id`, `reply_to_message_id`) |
| **Ambient memory strip** | `nestor ledger entries` tail + `nestor decision check` on visible actions | passage receipts with `tier`, `state`, `matcher`, `warrant_kinds`; fuzzy-match pointer when an operator action's phrasing overlaps a sealed pair |
| **Governance answers** ("may we?") | `nestor decision check` + `nestor evidence for` + `nestor warrant for` | seal card + evidence receipts + warrants; the "read it before proposing" bounce |
| **PA card** | `soil_list(collection=pa/commitments)` due-soon-first + `stack/current` | one prioritized card; write back to `stack/current` when it changes |
| **Refusal voice** | Nestor persona speech acts | render verbatim (`below_threshold`, `nothing_sealed`, `forged_seal`, …); negation-guarded, never apologetic |
| **Voice-triggered panels** | willow-mcp voice pipeline events | materialize the panel matched by `tool_oracle` intent → tool dispatch |

## Decisions on record

Sealed during the design exploration, each with evidence and warrant.
(These were sealed into a scratch Nestor store during the session; when the
Grove design gets its own live Nestor store, they get re-sealed there with
receipts intact.)

**D1 — What is Willows' Grove?** *(sealed, verifier: heimdallr)*
The operator's Jarvis seat rendered as a tri-modal desk (Governance / PM /
PA) that consumes fleet-presence, envelopes, and dispatch without
re-implementing them.
- evidence: `willow-memory/willow/AGENTS.md:47` — "Operator Jarvis seat" verbatim
- evidence: `willow-memory/willow/ORIENT.md:15` — tri-modal seat definition
- warrant (citation): `willow-memory/willow/CONSTITUTION.md` — Article 0

**D2 — Which repo owns the desktop code?** *(sealed)*
`safe-app-willow-grove` owns the desktop; `willow-memory/willow` is the
charter; `willow-mcp` is the muscle.
- evidence: `safe-app-willow-grove/CLAUDE.md`
- evidence: `willow-memory/willow/CLAUDE.md:3-4`

**D3 — Where is the canonical fleet roster?** *(sealed)*
`willow-memory/willow/fleet.json` — 16 agents, 3 trust tiers
(OPERATOR/ENGINEER/WORKER). Currently misaligned with the runtime; gap is
declared in-file (`roster-design-intent-unrecorded`).
- evidence: `willow-memory/willow/fleet.json` (schema `fleet-roster/v1`)

**D4 — May the Grove desktop run as served HTML?** *(sealed)*
Yes, on 127.0.0.1 with OAuth 2.1 / PKCE — precedent set by
`willow-mcp/src/willow_mcp/gates_serve.py` on `:8765`. The "no web ports"
rule in `safe-app-willow-grove/CLAUDE.md` is renegotiated by this
pattern; the operator has confirmed there are examples of served surfaces
within the rules.
- evidence: `willow-mcp/src/willow_mcp/gates_serve.py` (127.0.0.1 admin surface with OAuth + polling refresh)

**D5 — Does Grove re-implement Jarvis's memory?** *(sealed)*
No. Grove calls `apps/jarvis` handlers (`remember`/`recall`/`forget`/
`set_reminder`); Jarvis's IndexedDB fact store IS the desk's memory.
Iframe embed and memory mirror rejected as alternatives.
- evidence: `safe-app-store/apps/jarvis` — indexed fact store (compound indices, IDF, aliasing, `supersedes`, absence-as-fact)
- edge: **refines** D1 (specific case of "consumes without re-implementing")

**D6 — Direct Postgres reads, or `grove_*` MCP tools?** *(sealed)*
Migrate to willow-mcp's `grove_*` tools (20 exist). Current direct-Postgres
reads (in `grove_reader.py`, `panes/*`, `hero_stats.py`) are pre-redesign
plumbing.
- evidence: `willow-mcp/src/willow_mcp/grove_tools.py` — 20 tools already exposed

## Constitutional anchors

- **CONST-0-3** — No self-extension of capability. Grove renders envelopes; it does not create them. Envelope creation is Operator Key.
- **CONST-0-5** — Append-only ledger. Every Grove action leaves a receipt (via willow-mcp / Nestor / FRANK forwarding).
- **CONST-I** — Identity is the manifest, not the runtime. Grove's `app_id="willow"` (per AGENTS.md); its manifest is signed once, not per-tab.
- **CONST-V** — The Human. Grove is the surface where reserved decisions reach the operator. The `human_required` queue is not a widget; it is a constitutional obligation.
- **CONST-VI** — The Record. Grove appends only through willow-mcp / Nestor; content of past entries is never altered.
- **CONST-VII (default)** — Silence escalates. Anything the desk does not know how to route goes to the operator, not to whichever agent reaches it first.
- **CONST-X.4** — Concurrence rule. Where authorities disagree, the act is not performed; the conflict is recorded and escalated. Grove renders such conflicts on the Governance lens.

## Aesthetic direction (from the design conversation)

- **Lane B primary** — living meadow: SVG hero (or `<pre>` + CSS if the ASCII willow ports cleanly), breathable summer palette, cards floating on the meadow floor.
- **Lane A preserved** — the ASCII willow stays literally ASCII in the browser; every easter egg (Gerald at midnight, Mo Willems pigeon, 1:42, hotdog at 0.318, blooms cycling per position, wind sway) is kept.
- **Hints of Lane C** — bridge horizon shimmer (Bifröst-ish) where sky meets meadow; not costume, just an ambient nod.
- **Iron Man's workshop as metaphor, not copy** — floating projected panels, willow as the always-present anchor (arc-reactor-shaped, center-hold), fleet members as ambient companions. Grove's summer palette (frond green, sun gold, mint, emerald) instead of Stark's blue-and-gold. J.A.R.V.I.S. iconography stays theirs; Heimdallr is Grove's own voice.
- **"Fun to be and work in"** — the whole point. Playfulness of the current TUI is preserved; the seat is a place, not a monitor.

The v1 artboard (Home draft, pre-reframe) lives at:
`https://claude.ai/code/artifact/25e72759-d647-4d17-aa1a-800e88741565`

It will be redrawn as the Governance lens; PM + PA get their own artboards
alongside.

## Open decisions (still on the table)

1. **Free-float vs grid-snap panels.** True Stark workshop is expensive and fussy for daily use; a tile/dock hybrid is friendlier. Not yet sealed.
2. **Rooms replace desktop, or dock into it.** Click Rooms → does the desk go away, or does a chat panel materialize on the desk beside everything else?
3. **Full 16-agent render vs subset.** All willows visible always, or trust-tier orbits (OPERATORs closer, WORKERs outer)?
4. **Bureau's 7 personas alongside `fleet.json`'s 16.** Bureau's cast is not in `fleet.json` — do they appear on the desk as ambient presences too, or only when their app is engaged?
5. **Jarvis memory integration path.** Draft-leaning: handler-call (Grove wires the JS handlers directly). Alternates: iframe embed, memory mirror. Not yet sealed.
6. **Nestor integration path.** Embed `nestor ui` as an iframe under the Governance lens, or call `nestor serve` (MCP over stdio) from Grove's backend? Both viable.
7. **The tri-modal desktop redraw.** The v1 artboard predates the seat reframing; needs a Governance-first pass with PM + PA as sibling artboards.
8. **Persona-roster mint location.** Where does `fleet_personas.json` live — in this repo, in `willow-memory/willow`, or as a `willow-mcp` MCP endpoint served to any consumer?
9. **The parked bloom-row overlap.** From the v1 artboard — expected to self-resolve under the reframe; confirm on the redraw.
10. **Voice-panel materialization.** willow-mcp's voice pipeline (WO-1) is in flight. When a spoken intent lands, which lens does the resulting panel materialize under, and by what rule?

## What this doc does not do

- Does not create envelopes, sign anything, or ratify a decision.
- Does not touch code — no imports changed, no wiring done.
- Does not commit Grove to any specific integration path (Jarvis / Nestor); those decisions remain open.
- Does not speak for the operator. The seat proposes. USER ratifies.

## Related work

- `docs/design/forge-convergence.md` — the Forge checkpoint / human_required convergence (proposed earlier)
- `willow-memory/willow/design/jarvis-build-orders.md` — WO-1 (voice) and WO-2 (commitment) build orders
- `willow-memory/willow/design/willow-voice-ingress-membrane.md` — voice membrane design
- `willow-memory/willow/design/willow-commitment-membrane.md` — commitment membrane design

ΔΣ=42
