# Willow's Grove — the operator seat, composed not built

b17: WGRV1 ΔΣ=42
Status: **PROPOSED** — Heimdallr proposes, USER ratifies (CLAUDE.md rule 5). No code changed by this note.

## The reframe

Old: **Willow Grove** — the dashboard for Willow (a page *about* her).
New: **Willow's Grove** — her own space, where the operator meets her and, through her, the fleet.

By long-standing fleet rule, **everything routes through Willow.** She is
the Primary Interface — `willow-memory/willow/fleet.json` catalogues her
as `"willow": { "trust": "OPERATOR", "role": "Primary interface" }` —
and every willow-mcp call takes `app_id="willow"` (per
`willow-memory/willow/AGENTS.md`). The grove is her groove: where she
does what she does, with the operator beside her and the fleet reachable
through her.

The seat is the operator's post within the grove. The willow tree at the
center of the desk is *her* — the singular anchor, breathing with the
fleet's state, not one tree among many. The 16 agents in `fleet.json`
(Heimdallr the watchman, Hanuman the bridge-builder, Loki the fleet
accountant, Ada, Steve, Skirnir, Vishwakarma, and the rest), plus the
Bureau's characters (Jeles, Oakenscroll, Ofshield, Binder, Pigeon,
Gerald, Hanz), plus Nestor's refusal voice — the fleet — are around
Willow, but reached through her, never around her.

## Prior art (north star)

**This document extends; it does not synthesize.** Two prior docs already
stated the shape and are load-bearing for what follows:

- **[`docs/synthesis/the-one-desk.md`](../synthesis/the-one-desk.md)** —
  ONEDSK, 2026-06-24, Vishwakarma with operator. The five-layer stack
  (**Voice / Desk / Tools / Memory / Trust**). The single-sentence
  architecture: *"Apps do not talk to each other. They talk to a shared
  memory, and a human talks to all of them from one desk."* The two
  questions that replace the mesh (what atoms does a tool read; what does
  it write). Flagged: "Read this first when the fog rolls back." **The
  Voice layer — personas as skins over tools, one voice driving many
  tools, one tool driven by many voices — is an architectural given
  there. Willow's Grove renders it; it does not invent it.**

- **[`docs/synthesis/grove-starter-borrow-map.md`](../synthesis/grove-starter-borrow-map.md)** —
  GSBRW, 2026-06-24, Vishwakarma. The **steal-vs-wrap** discipline applied
  to the third-party starter pack (nvitop, toolong, kanban-tui, calcure,
  parllama, visidata, sqlit, fast-resume, feeds.fun, dooit, botany), plus
  a prioritized P0–P3 borrow backlog with acceptance criteria per steal.

What **this** doc adds:
1. The **constitutional framing** (`willow-memory/willow`, arrived later)
   — that the desk is the *Operator Jarvis seat* and serves the law.
2. The **tri-modal seat** shape (Governance / PM / PA from
   `willow-memory/willow/ORIENT.md`) as the desk's explicit lens
   structure.
3. The **name correction** (Willow's Grove — her space, everything routes
   through her).
4. **Decisions D1–D6** taken during the design conversation, each with
   evidence and warrant.
5. Extension of the steal-vs-wrap discipline from GSBRW's third-party
   starter pack to the **fleet's own already-built pieces**
   (`fleet-presence`, dispatch, Nestor, `apps/jarvis`, envelopes,
   constitutional articles).

Where GSBRW and this doc collide, GSBRW wins on ground it already
covered; this doc yields.

## What Willow's Grove is

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

Every load-bearing piece already exists somewhere in the fleet. Willow's
Grove is a page that binds them; not a system that replaces them.

**Base vs add-on** — Grove's base is willow-mcp native (plus the
`willow-memory/willow` charter and this repo itself). Everything else is
an **opt-in add-on** the operator installs and consents to (SAP / SITR1
already gates this). Grove renders what's present; **absence is a state,
not a failure**. See D7.

| Piece | Where it lives | Base? | Grove's relationship |
|---|---|---|---|
| Persona roster | `willow-memory/willow/fleet.json` + `willow-mcp/src/willow_mcp/bundle/config/specialists.json` (base); Bureau JSONs, `hornbook-knowledge/*` persona files, `nestor.persona` (add-on) | **base** (partial) + add-on entries when present | merges what's present |
| Fleet presence seam | `safe-app-store/libs/fleet-presence/src/fleet_presence/__init__.py` — `announce/roster/withdraw` over `~/.willow/store/fleet/store.db` | **add-on** (stdlib-only; silent no-op if store missing) | announces + polls when present |
| Dispatch API | `willow-mcp` — 7 tools (`dispatch_send/read/list/accept`, `handoff_write_v4`, `verify_handoff`, `agent_clear`); HMAC-signed packets under `$WILLOW_HOME/dispatch/{id}/` | **base** | calls |
| Grove data API | `willow-mcp` — 20 `grove_*` tools (`grove_fleet_status`, `grove_agents`, `grove_human_required`, `grove_bus_*`, `grove_list_channels`, `grove_get_history`, `grove_search`, …) | **base** | calls |
| Memory (facts, reminders) | `safe-app-store/apps/jarvis` — IndexedDB fact store with compound indices, IDF ranking, alias bridging, `supersedes`, absence-as-fact | **add-on** | calls handlers when installed |
| Decisions / evidence / warrants / ledger / refusal voice | Nestor (`pip install nestor-meaning`) — CLI + Python API + `nestor serve` MCP over stdio | **add-on** | embeds or calls when installed |
| Constitution + Trace IDs | `willow-memory/willow/CONSTITUTION.md` — Draft 0.7, 13 Articles, `CONST-*` | **base** (the seat serves the law) | renders |
| Envelopes (active grants + expiry + meter) | `willow-memory/willow/envelopes/pre-approved.json` | **base** | renders |
| Voice ingress pipeline | `willow-mcp/src/willow_mcp/voice/` — WO-1 in flight; `hey_jarvis` already a wake option | **base** once WO-1 lands | listens for events |
| Commitment / calendar membrane | `willow-mcp/src/willow_mcp/commitments/` — WO-2 in flight | **base** once WO-2 lands | listens for events |
| Ratatosk sessions | `safe-app-store/apps/ratatosk` — already posts `session_started`/`session_ended` to a Grove channel | **add-on** | listens when installed |
| The willow hero | `safe-app-willow-grove/widgets/hero.py` + `widgets/hero_scene.py` — ASCII willow, meadow, Gerald, pigeon, blooms, wind, per-character color | **base** (Grove's own) | ports to SVG + `<pre>` |
| Served-HTML precedent | `willow-mcp/src/willow_mcp/gates_serve.py` — 127.0.0.1 + OAuth 2.1 PKCE + polling refresh | **base** (pattern) | mirrors pattern |
| Nestor UI | `nestor ui` — Queue / Memory / Ask / Signals / Ledger / Graph (Cytoscape) | **add-on** (with Nestor) | embeds under Governance lens when present |
| Aesthetic explorations | `willow-mcp/docs/design/willow-*.html` — 10 direction sketches | **base** (design reference) | draws on |
| Jeles the librarian + her corpus | `hornbook-knowledge/Jeles` — Python package, corpus, tests | **add-on** | renders her sigil / voice / retrieval surface when installed |
| Oakenscrolls Office + its almanac seam | `hornbook-knowledge/oakenscrolls-office` — `almanac_seam.py` bridges to almanac-data | **add-on** | renders when installed; already calls almanacs directly |
| UTETY (chat / companion) | `hornbook-knowledge/UTETY` | **add-on** | renders when installed |
| 13 domain corpora | `almanac-data/*-almanac` — civic, climate, transportation, science, health, agriculture, economy, education, environment, justice, energy, template; `SCHEMA-V2` + `LICENSE-CODE`/`LICENSE-DATA` separation | **add-on** (data, not code) | not consumed directly — Jeles/Oakenscrolls reach them |
| Homestead·Affairs seats | `homestead-affairs/homestead` (base seat) + `homestead-ledger` + `homestead-health` + `homestead-law` | **add-on** (peer seat's family) | may coexist on desk; borrows discipline (rungs, `serve()` chokepoint, DECISION cards) |
| Forge checkpoint governance | `rudi193-cmd/Forge` — authored by Vishwakarma per `promotion.json` | **add-on** | renders build-lane surfaces when installed |

## The build (the very small part)

**Base build** — assumes only willow-mcp + `willow-memory/willow` charter,
runs on any operator's machine before any add-on is installed:

1. **One HTML page**, served on 127.0.0.1 under the `gates_serve` pattern —
   the tri-modal canvas. Structure, not novel plumbing.
2. **The tri-modal switch** — Governance / PM / PA as browser state
   (localStorage / URL fragment) + one toggle affordance.
3. **Layout memory** — which panels are up, where, per-operator. Browser
   state plus a small SOIL record.
4. **The `WILLOW_HUMAN_ORCHESTRATOR=1` env** — Grove sets this to be
   recognized as the operator seat.
5. **Grove's Postgres-reads → `grove_*` MCP tool migration** —
   incremental, pane by pane, existing behavior preserved. Real work, but
   *migration* work, not new logic.
6. **Base persona-roster mint** — reads `specialists.json` + `fleet.json`
   (both base sources) and normalizes to `{name, domain, voice_register,
   emit_fields, visual: {color, sigil}}`. Ships with skins for the base
   personas (Willow, Hanuman, Loki, Jeles, Ada, Skirnir, Vishwakarma,
   Heimdallr).

**Conditional (activates when add-on is present)** — each is a small,
guarded code path:

7. **`announce("grove", …)`** — calls `fleet-presence` when the seam is
   importable; silent no-op otherwise.
8. **Roster merge extends** with `hornbook-knowledge/*` persona files,
   `nestor.persona`, Bureau JSONs — whichever the operator has installed.
9. **Per-add-on renderers** — Nestor chip / Jeles's search surface /
   Oakenscrolls' records surface / Vish's Forge build lanes / homestead's
   rungs. Each renders when its add-on is present; each no-ops (not errors)
   when absent. **Absence is a state, not a failure** (D7).

The seat writes no code (magistrate-writes-no-code, per
`willow-memory/willow/design/jarvis-build-orders.md:26`). This makes literal
sense once the map is drawn — the code is already written across willow-mcp,
safe-app-store, Nestor, and fleet-presence. The seat's job is to bind and
render what's present, not build.

## The add-on ecosystem

Currently-known add-ons Grove can render when the operator opts in. Not
forced; not required to boot; not required to be complete. Each entry is a
neighborhood, not a single package.

| Org | What lives there | Grove renders when installed |
|---|---|---|
| **`Die-Namic-Systems`** | Nestor — meaning infrastructure (cascade, decisions, evidence, warrants, ledger, refusal voice); `nestor ui` (Queue/Memory/Ask/Signals/Ledger/Graph) | Governance surface (decision-check / evidence / warrants); refusal chip (`¬` pigeon); ambient memory strip from ledger tail |
| **`hornbook-knowledge`** | Bureau's graduation destination — `Jeles` (librarian package + corpus), `oakenscrolls-office` (records + `almanac_seam.py`), `UTETY` (companion/chat) | persona chips + skins (`§` mint for Jeles, colored corner for Oakenscroll); retrieval, records, chat surfaces gated behind their app |
| **`almanac-data`** | 13 domain corpora (civic, climate, transportation, science, health, agriculture, economy, education, environment, justice, energy) + `almanac-template`; two licenses (`LICENSE-CODE`, `LICENSE-DATA`); `SCHEMA-V2` shared | not consumed by Grove directly — Jeles/Oakenscrolls reach them; Grove may surface corpus provenance in Jeles-authored cards |
| **`homestead-affairs`** | Peer seat's family — `homestead` (base seat with keep/rungs/serve chokepoint), `homestead-ledger`, `homestead-health`, `homestead-law` | peer-seat awareness on the desk (may coexist as a sibling surface); Grove borrows discipline (rungs, `serve()`, DECISION card format) whether or not homestead itself is loaded |
| **`willow-memory` beyond charter** | `willow-data-vault`, `willow-gate`, `kartikeya`, `corpus-lens` | vault / gate / kart / corpus surfaces when installed |
| **`safe-app-store` (in `rudi193-cmd`)** | The catalog itself, `libs/fleet-presence`, ~30 apps (Bureau, `jarvis`, `ratatosk`, `intake-desk`, `law-gazelle`, `private-ledger`, `nasa-archive`, `vision-board`, `the-binder`, `field-notes`, …) | catalog / install surfaces (SITR1); each app renders its own surfaces when installed |
| **`rudi193-cmd/Forge`** | Checkpoint governance — Vishwakarma's authored app | build-lane surfaces (checkpoint memory, engagement monitor, human-loop attestation) when installed |
| **`terpsi-programs`** | WIP — org exists; content still landing | future add-on |
| **`forge-play`** | WIP — org exists; content still landing | future add-on |

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

**D1 — What is Willow's Grove?** *(sealed, verifier: heimdallr; question normalized as "what is willow's grove")*
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

**D7 — Grove's base vs its add-ons.** *(sealed)*
Grove's base is willow-mcp native (plus the `willow-memory/willow` charter
and this repo itself). Everything else — Nestor, Forge, homestead,
hornbook-knowledge (Jeles, Oakenscrolls, UTETY), almanac-data (13 corpora),
Bureau apps, ratatosk, `fleet-presence` — is an **opt-in add-on** the
operator installs and consents to (SAP / SITR1 already gates this). **Grove
renders what's present; absence is a state, not a failure.** Personas load
with their homes: Jeles's `§` mint sigil only appears when
`hornbook-knowledge/Jeles` is installed. Every per-add-on renderer is a
guarded code path that no-ops on absence.
- evidence: `safe-app-willow-grove/docs/synthesis/the-one-desk.md` — ONEDSK's Tools layer already distinguishes flagships (sovereign) + scouts (utility belt), each one job, each optional
- evidence: `hornbook-knowledge/oakenscrolls-office/almanac_seam.py` — live cross-add-on wiring (Oakenscrolls calls almanacs), proof add-ons compose without Grove mediating
- evidence: `rudi193-cmd/Forge/promotion.json` — graduation pattern: apps carry `author` persona forward and `host: safe-app-store` preserves roots after moving to their own repo

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
- **Iron Man's workshop as metaphor, not copy** — floating projected panels, Willow at the always-present anchor (arc-reactor-shaped, center-hold — *she* is the reactor, not a stand-in for one), fleet members as ambient companions reached through her. Grove's summer palette (frond green, sun gold, mint, emerald) instead of Stark's blue-and-gold. J.A.R.V.I.S. iconography stays theirs; Willow is the primary interface, Heimdallr watches, Nestor refuses, and every other agent speaks in their own register.
- **"Fun to be and work in"** — the whole point. Playfulness of the current TUI is preserved; the seat is a place, not a monitor.

The v1 artboard (Home draft, pre-reframe) lives at:
`https://claude.ai/code/artifact/25e72759-d647-4d17-aa1a-800e88741565`

It will be redrawn as the Governance lens; PM + PA get their own artboards
alongside.

## Open decisions (still on the table)

1. **Free-float vs grid-snap panels.** True Stark workshop is expensive and fussy for daily use; a tile/dock hybrid is friendlier. Not yet sealed.
2. **Rooms replace desktop, or dock into it.** Click Rooms → does the desk go away, or does a chat panel materialize on the desk beside everything else?
3. **Full 16-agent render vs subset.** All agents visible always, or trust-tier orbits (OPERATORs closer to Willow, WORKERs outer)?
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
