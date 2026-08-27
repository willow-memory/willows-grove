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

**This document extends; it does not synthesize.** Four prior docs already
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

- **[`willow-mcp/docs/PRIOR_ART.md`](../../../willow-mcp/docs/PRIOR_ART.md)** —
  837-line MCP-ecosystem survey with **hard license filter** (Apache-2.0
  compatible only; MPL/EPL flagged file-level copyleft; GPL/LGPL/AGPL
  listed anyway so the cost is visible not invisible). 13 sections
  covering MCP tool shapes, protocol features, observability, rate
  limiting, workflow engines, knowledge stores, agent authorization,
  voice ingress, safety machinery, privacy boundaries, knowledge
  governance, developer tooling, operational infrastructure.
  **Everything below Grove — voice pipeline, kb_journal, ledger, safety
  machinery, human-in-the-loop primitives — Grove inherits from here.**
  The Stack section below cites specific findings by section.

- **[`safe-app-store/docs/the-house-already-knew.md`](../../../rudi193-cmd/safe-app-store/docs/the-house-already-knew.md)** —
  Vishwakarma's field notes, 2026-08-05. Four things built one morning
  that already existed done better. The thesis: *"the fleet's largest
  development cost is redoing things"* — the fleet's organs (Jeles,
  Nestor, Article IV) are all pointed *outward*, none is aimed at the
  house's own codebase and decision history. **The Discipline section
  below operationalizes the two moves that doc names: point memory
  infra inward, find the second reader.**

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

   *Reference pattern:* `hornbook-knowledge/oakenscrolls-office/almanac_seam.py:37-49`
   — `_matcher()` tries to import Nestor's `StringMatcher` once, caches the
   result (`_MATCHER_TRIED` flag), and degrades exact-match search when
   absent. Grove's per-add-on activations should follow this shape:
   lazy import, probe once, cache, degrade gracefully — never crash on
   the absence of an add-on.

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
| **`hornbook-knowledge`** | Bureau's graduation destination. **`Jeles`** — verified-corpus organ: 1,028 human-verified Q/A nuggets across 74 seed files, 85+ institutional source cards (arXiv, PubMed, LOC, Europeana, WHO, IMF, CourtListener, …) with epistemic metadata (custody, review status, jurisdiction). Schema mirrors Nestor's pair shape by design — see D8. **`oakenscrolls-office`** — local-first calibration ledger (predictions with confidence, graded when world weighs in), with `almanac_seam.py` that reads local almanac-data clones directly (no git binary, no subprocess) and pins each clone's HEAD commit into citations. **`UTETY`** — pedagogy + trust layer, entirely different concern (learner + content); not a Grove connection, but its shape (no-egress zone + one named outbound seam holding only de-identified concept queries) is a reference for structural privacy the desk can borrow. | persona chips + skins (`§` mint for Jeles, `⌸` bark for Oakenscroll); Jeles's retrieval + source-card provenance surface when installed; Oakenscroll's cited-grade surface when installed |
| **`almanac-data`** | 13 domain corpora (civic, climate, transportation, science, health, agriculture, economy, education, environment, justice, energy) + `almanac-template`; two licenses (`LICENSE-CODE`, `LICENSE-DATA`); `SCHEMA-V2` shared | not consumed by Grove directly — Jeles/Oakenscrolls reach them; Grove may surface corpus provenance in Jeles-authored cards |
| **`homestead-affairs`** | Peer seat's family — `homestead` (base seat with keep/rungs/serve chokepoint), `homestead-ledger`, `homestead-health`, `homestead-law` | peer-seat awareness on the desk (may coexist as a sibling surface); Grove borrows discipline (rungs, `serve()`, DECISION card format) whether or not homestead itself is loaded |
| **`willow-memory` beyond charter** | `willow-data-vault`, `willow-gate`, `kartikeya`, `corpus-lens` | vault / gate / kart / corpus surfaces when installed |
| **`safe-app-store` (in `rudi193-cmd`)** | The current catalog + `libs/fleet-presence` + ~30 apps (Bureau, `jarvis`, `ratatosk`, `intake-desk`, `law-gazelle`, `private-ledger`, `nasa-archive`, `vision-board`, `the-binder`, `field-notes`, …); today it holds both the *apps* and the *build/graduation pattern*. The pattern half is graduating to Forge (below); the app-collection stays. | catalog / install surfaces (SITR1); each app renders its own surfaces when installed |
| **`rudi193-cmd/Forge`** | Vishwakarma's build tool — **the pattern he built while building safe-app-store, graduating into a tool that helps others build.** Started as checkpoint governance (checkpoint memory, engagement monitor, human-loop attestation); becoming the productized graduation pipeline itself (promotion, measurement, calibration, engagement scoring). Its own `promotion.json` — with `author: vishwakarma`, `host: safe-app-store` — is a self-illustration: Forge was graduated using the pattern Forge is now becoming. | build surfaces for anyone using Forge to build; not required to build Grove itself |
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

### Surface-rung ceiling — Homestead's pattern applied to Grove cards

Adopted from `homestead-affairs/homestead/docs/PHASE2-SURFACES.md` and
`DECISION-agent-retrieval.md`. Every card renders through one `serve()`
chokepoint; a reach past `serve()` on any surface is a build failure. The
ceiling per surface (`(plain, with_purpose)`):

| Grove surface | Homestead analog | Ceiling | Notes |
|---|---|---|---|
| Dispatch rail | S1_LIST | `(L1..L3, L1..L3)` | Ambient rows carry no payload; state-colored transitions only. |
| Envelope panel | S1_DETAIL | `(L1..L4, L1..L4)` | Opens with attestation (see P1). L5 dropped without trace. |
| kb_journal chat | S2_PROMPT | `(L2, L2)` | Purpose inert — value is auditability, no lift. Content never reaches local models beyond L2 derived. |
| MCP calls via Nestor | S3_AGENT | `(L2, L2)` | Closed at L2 both columns because *"S3 has no human in the loop; purpose's value is auditability, not lift."* |
| Export via envelope | S4_EGRESS | `(L2, L4)` | Purpose required, ledgered with `expected_head`. |

### Attestation gate on orchestrator writes (P1)

10 orchestrator write tools (`dispatch_send`, `dispatch_accept`,
`handoff_write_v4`, `verify_handoff`, `agent_clear`, `frank_append`,
`envelope_apply`, `envelope_propose`, `envelope_ratify`,
`envelope_reject`) require a **5-layer gate** per
`willow-mcp/docs/design/pgp-and-persona.md §1.3`:

1. `app_id = willow`
2. `WILLOW_HUMAN_ORCHESTRATOR=1` env
3. Live session file present
4. Valid sidecar signature (keyring v2 OR PGP v1 legacy)
5. Manifest `.sig`

Grove's Envelope panel **surfaces which attestation path is active** and
distinguishes denial reasons: `orchestrator_session_attestation_missing`
(re-attest) vs `orchestrator_session_attestation_invalid` (check keyring
/ PGP state). Sidecar files are never rendered directly.

### Voice state machine (P2)

6 states — `IDLE → ARMED → CAPTURE → TRANSCRIBE → DISPATCH → SPEAK`,
per `willow-memory/willow/design/willow-voice-ingress-membrane.md`. The
wake-word gate **IS** the consent boundary; pre-wake audio never reaches
the transcriber. FRANK receipts record facts, never audio. Voice adds
no new authority — a spoken command hits the same SAFE gate as a typed
one. The **utterance arbiter** (`willow-utterance-arbiter.md`) is the
sibling output layer; it decides whether a candidate (commitment,
reminder, refusal) crosses into an actual utterance, and never barges
CAPTURE. Grove **displays which state is live** in the voice affordance.

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
- evidence: `rudi193-cmd/Forge/promotion.json` — graduation pattern: apps carry `author` persona forward and `host: safe-app-store` preserves roots after moving to their own repo. Forge itself is the reference case (its own promotion.json points back), and the pattern is now graduating INTO Forge as a productized build tool — safe-app-store's build/graduation half moving out, its app-collection half staying.

### Patterns adopted from prior art (P1–P10)

These are prior-art decisions that Grove **adopts** rather than
re-invents. All sealed with evidence; each cites a specific fleet
document. Compact form; see the source docs for reasoning depth.

- **P1 · Orchestrator write attestation** — 5-layer gate on the 10
  orchestrator write tools. Grove surfaces missing vs invalid distinctly.
  (evidence: `willow-mcp/docs/design/pgp-and-persona.md §1.3` +
  `permissions-matrix.md`).
- **P2 · Voice state machine** — 6 states; wake-word IS consent boundary;
  utterance arbiter is the sibling output layer that never barges
  CAPTURE. (evidence: `willow-voice-ingress-membrane.md`,
  `willow-utterance-arbiter.md`, `PRIOR_ART.md §8`).
- **P3 · 5-surface rung ceiling with `serve()` chokepoint** — from
  Homestead. See the composition sketch above. (evidence:
  `homestead-affairs/homestead/docs/PHASE2-SURFACES.md`,
  `DECISION-agent-retrieval.md`).
- **P4 · Editor.js block model** — Apache-2.0, headless. Grove card
  bodies are ordered lists of typed JSON blocks. kb_journal atoms are
  natural blocks. (evidence: `PRIOR_ART.md §1 block-level content`).
- **P5 · Tree / stomata UI from `ui-concepts.md`** — trunk = health,
  sap = queue, canopy = fleet, stomata = 3-key egress gate. Grove ports
  the pattern to the browser without reimplementing. (evidence:
  `willow-mcp/docs/design/ui-concepts.md`, `PRIOR_ART.md §13`).
- **P6 · Grove permission split** — `grove_read` universal; `grove_write`
  only for hanuman/loki/jeles/ada. Grove UI dims send-affordance on
  read-only seats (skirnir, vishwakarma). (evidence:
  `permissions-matrix.md §1.6 + §3`).
- **P7 · Three consent toggles** — `internet` (enforced), `cloud_llm`
  (modeled), `lan` (modeled). Read from `settings.global.json`. Every
  scope is an explicit UI decision; unenforced toggles marked distinctly.
  (evidence: `consent-toggles.md`, `app_store_vision_and_gaps.md E5`
  warning).
- **P8 · Persona picker discipline** — only on orchestrator seat;
  specialists get persona injected via `packet.persona_path`; locked
  binding hides even the orchestrator picker. (evidence:
  `pgp-and-persona.md §2 + §3`, `specialist-registry.md §9`).
- **P9 · Configurable layouts** — discord / slack / mission-control /
  minimal / journal-first / mobile / custom. Personalization by layout,
  not just theme. Model switcher is a first-class app. (evidence:
  `safe-app-willow-grove/docs/superpowers/specs/2026-04-24-grove-os-design.md`).
- **P10 · Sender colors by hash + state glyphs** — per-persona sigil
  (identity, V-layer) alongside per-instance state glyph
  (`● / ◐ / ○ / ·` = running / degraded / idle / absent). Both sourced
  from `fleet_personas.json` + `grove_fleet_status.ui_state`. (evidence:
  `dashboard-design.md`, `grove-skins-beauty.md`).

### Warnings we're carrying (W1–W4)

These are fleet-wide dangers the design must not repeat.

- **W1 · Persona drift** — cast has been narrative for months with no
  central schema. Sigils and colors live in a **versioned
  `fleet_personas.json` in SOIL**, never hard-coded per-app. (evidence:
  `app_store_vision_and_gaps.md §3+§4, E6`).
- **W2 · Naming style** — use homestead's *"affairs you handle
  yourself"* framing. Avoid *"sovereignty"* language that slides into
  political autonomy. Legal control, not preference. (evidence:
  `homestead-affairs-face.md §1-2 + §8`).
- **W3 · KB redundancy** — fleet KB measured ~68% redundant, no dedup
  gate. Grove writes to `kb_journal` **hash content before insert**;
  skip if an atom with identical hash already exists. (evidence:
  `the-nestor-lineage.md §4.1`).
- **W4 · No b17-as-security theater** — `b17` is a file-lineage
  labeling convention; pub/sub sequence numbers are ordering, not
  authentication. Grove's real security stack: the 5-layer attestation
  gate (P1), PGP/keyring, FRANK hash-chained ledger, Nestor
  cryptographic seals, `kb_journal` schema gate, mutation-tested refusal
  guards. Nothing is layered on top of that as security theater.
  (evidence: `CLAUDE.md rule 4`, Nestor decision 0099, operator
  attestation).

### Reactions and anchors (R1–R2)

- **R1 · surface_card is Grove's inbound edge** — reaction engine
  (`willow-memory/willow/design/reaction-engine.md`) fires
  `surface_card` as one of its standard actions; Grove IS a consumer of
  those, not an initiator. Personas propose; the dispatch rail (the
  gateway) vets against allowlist per Jeles's `reaction-engine.md`
  pattern.
- **R2 · Off-machine head anchor** — if Grove ever exports records,
  `IntegrityLog` head anchor lives in `~/.willow/grove/anchors/`, NOT
  under `.../logs/`. Export returns head; operator records off-machine
  (catches truncation without on-machine closure). (evidence:
  `homestead/docs/PLAN-first-runnable.md bite 5`,
  `apps/homestead-health/docs/DECISION-living-lane-ledger.md`).

**D8 — Nestor and Jeles are the fleet's Independent Witnesses of Article 0 §0.2.** *(sealed)*
Every factual claim carries two provenance questions. **Nestor asks
*"did a named human check this?"*** — the sealing dimension. **Jeles asks
*"do enough independent sources back this?"*** — the corroboration
dimension. Both stores use the identical pair schema
(`source_text` / `source_lang` / `target_text` / `target_lang`); Jeles's
`corpus/compose.py` names this dual-write path explicitly. Grove renders
their refusals **distinctly**: Nestor's `¬` (pigeon-gray) means
*"unsealed — no human has checked."* Jeles's `§` (mint) means
*"insufficient independent sources."* **They must never collapse into a
single 'refused' chip** — two different meanings, two different remedies
(get a human vs. cite more sources). This satisfies Article 0 §0.2's
Independent Witness bar (materially distinct failure modes: one is a
signature check, one is a source-count check).
- evidence: `hornbook-knowledge/Jeles/corpus/compose.py` — "the two stores ask different questions — jeles asks 'do enough independent sources back this?', Nestor asks 'did a named human check it?'"
- evidence: `hornbook-knowledge/Jeles/README.md` — corpus sits in front of live search; confident nugget match answers instantly; misses log as gaps
- evidence: 1,028 human-verified nuggets across 74 seed files (adversarial rounds included: `adv_challenge`, `adv_steelman`, `adv_factcheck`); 85+ institutional source cards with epistemic metadata (custody / review status / jurisdiction)
- caveat: `rudi193-cmd/jeles-remote` has drifted from the canonical `Jeles` package (833 differing lines in its vendored `sources.py`, zero `_egress` references — the SSRF/key-leak fix is absent). Grove must not trust `jeles-remote` as a Jeles substitute; treat as a **known-drifted add-on**. Jeles-local is the source of truth.

**D9 — Grove's framework: vanilla JS + Web Components + no build step.** *(sealed)*
Grove ships as a single served page over the `gates_serve` pattern;
every desk-side library the Stack section names is framework-agnostic
except `dnd-kit`, `react-spring`, and `xyflow` — and Grove's mechanics
(edge-summoned cards on a fixed viewport, slide-in / slide-out
choreography, simple "which card is primary" state) don't need those.
Web Components give component architecture natively. **Trade-off
accepted:** no React ecosystem; if a later Grove wants shadcn or a
deep component library, that's a rewrite. Accepted because Grove's
interactions are simple (summon / dismiss / type / speak / hover), not
deep component trees.
- evidence: `willow-mcp/src/willow_mcp/gates_serve.py` — willow-mcp already serves HTML from Python without a JS build; the pattern Grove joins
- evidence: `safe-app-store/apps/jarvis/src/willow.js` — jarvis's browser client is small vanilla JS (OAuth 2.1 PKCE + IndexedDB); fleet consistency
- evidence: `willow-mcp/docs/PRIOR_ART.md §1` — Editor.js (Apache-2.0) is framework-agnostic; suits Grove's card content model without React coupling
- warrant (construction): a vanilla-JS Grove can be reviewed by `curl` on `127.0.0.1:8765`; no build artifacts to inspect; every dependency is a small named library the operator can audit — the magistrate-writes-no-code discipline made legible

**D10 — Where the unified persona registry lives.** *(sealed)*
`willow-memory/willow/fleet_personas.json` — charter-adjacent to
`fleet.json` (its parent). Schema extends fleet.json with `visual`
(color, sigil, color_token), `voice` (register, mandate, not_do parsed
from `personas/{name}.md`), `emission_fields`, and `canonical_file`
pointer. Writes are governance acts (per W1 — persona drift is the
danger this closes); charter placement makes each edit follow Article
VIII amendment discipline. All consumers (Grove, Nestor UI, jarvis,
homestead) read this one file. Grove reads at boot, caches, degrades
to bare `fleet.json` fields if the extended file is absent (per D7).
- evidence: `willow-memory/willow/fleet.json` — the parent (16 agents, 3 trust tiers, schema `fleet-roster/v1`); `fleet_personas.json` extends this shape
- evidence: `safe-app-store/docs/app_store_vision_and_gaps.md §3+§4 + E6` — W1: persona drift is documented; central schema is the fix
- evidence: `willow-memory/willow/CONSTITUTION.md` Article VIII — amendments to charter-carried data follow the ratify pipeline; matches the governance-act framing
- warrant (construction): consumers read the file directly (offline-safe); a `willow-mcp` read-through MCP endpoint may be added later, but the file remains canonical

**D11 — How Grove reaches Nestor.** *(sealed)*
Call `nestor serve` (MCP over stdio) from Grove's backend; render
Nestor's data in Grove's own card-native UI. **NOT iframe embed.**
Composes with the summonable-card model (Governance lens summons Nestor
cards); persona colors (V-layer) apply to Nestor-sourced content;
Nestor's refusal chip (V5) renders verbatim inside Grove's own chip.
Cytoscape.js is already a Grove dep (Nestor decision 0137 sealed it
inlined into the served page, no external CDN), so the Graph tab is
renderable in Grove's own style. Iframe-embed remains a fallback for
specific deep-dive views if ever needed — not the primary path.
- evidence: V5 (this store) — Nestor's refusal must render verbatim with negation preserved; requires Grove-native rendering, not iframe
- evidence: `Nestor/docs/dogfood/decisions/0137-read-only-decision-graph-in-desk.json` — Cytoscape.js MIT inlined into served page; Grove already carries this dep
- evidence: `willow-mcp/docs/PRIOR_ART.md §2` — MCP-over-stdio transport is stable; `nestor serve` is versioned
- evidence: composition sketch (above) — *"Governance answers via nestor decision check + evidence for + warrant for; refusal voice renders Nestor persona speech acts verbatim"* — already committed direction
- warrant (construction): one MCP client for `nestor serve` in Grove's backend; renders its output through Grove's card + chip vocabulary; iframe path preserved as escape hatch for specific views, not primary

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

## Stack (Apache-2.0 compatible)

**License filter is hard:** MIT, BSD, ISC, Zlib, Apache-2.0 are one-way
compatible (we depend on). MPL-2.0 / EPL-2.0 fine as deps but file-level
copyleft (want a look). GPL / LGPL / AGPL / SSPL / BUSL / Elastic / any
"custom" or "standard" license — **out**.

**Everything below Grove's own code is inherited from `willow-mcp` and
its own `PRIOR_ART.md`.** Grove's build layers on top; the desk-side
UI libraries are Grove-specific.

### Inherited from willow-mcp (base substrate)

| Layer | What | Cite |
|---|---|---|
| Voice pipeline | openWakeWord (Apache-2.0) + Silero VAD (MIT) + Faster Whisper (MIT) + Kokoro TTS (Apache-2.0). Wake-word-as-consent architecture (P2). | `PRIOR_ART.md §8` |
| Journal / KB writes | `kb_journal` tool writing atoms `domain=journal` into the confirmed knowledge schema; `knowledge_search(domain=journal)` on read | `willow-mcp/src/willow_mcp/server.py:2607` |
| Ledger | FRANK — hash-chained append-only Postgres ledger, tamper-evident, receipt-per-call | `PRIOR_ART.md §13` |
| Safety machinery | Friction floor (deterministic sycophancy detection, external to the model), StackOne Defender (Apache-2.0, indirect prompt-injection scanning on tool responses), secret-scan on egress | `PRIOR_ART.md §9` |
| Human-in-the-loop | `human_required` queue, priority + kind-based routing, unforgeable `attested_by`, human-only orchestrator seat | `PRIOR_ART.md §13` |
| Observability | `opentelemetry-instrumentation-mcp` auto-instruments Python MCP SDK; per-call latency + errors via OTel backends | `PRIOR_ART.md §3` |
| Commitment membrane | Calendar-backed, tamper-evident, receipt-not-recording, dew-rule surfacing (silent unless imminent/conflict/mismatch) | `willow-commitment-membrane.md`, `PRIOR_ART.md §13` |
| Egress membrane | Reach over content (not just endpoints); consented projection with field-level allow-list + human attestation over payload hash; unconditional redaction floor | `egress-membrane-constitutional-map.md` |

### Grove's own desk-side stack (net-new for the desk)

| Category | Library | License | Notes |
|---|---|---|---|
| Positioning / z-stacking | `floating-ui` | MIT | The primitive for cards floating on top of the meadow. Framework-agnostic. |
| Drag / dismiss / grid | `dnd-kit` (or `react-dnd`) | MIT | Modern lightweight; agnostic across React / Vue / Svelte. |
| Slide-in / slide-out | `motion` (framer-motion) *or* `react-spring`; vanilla via `motion-one` | MIT | Spring physics for summon / dismiss choreography. |
| Hotkeys / chording | `hotkeys-js` (3.8 KB) *or* `mousetrap` | MIT / **Apache-2.0** | `⌘G` / `⌘M` / `e` / `/` etc. |
| Terminal aesthetic | `xterm.js` | MIT | Any terminal-styled card. |
| Voice base | Web Speech API | native | No dependency. Chrome/Edge/Safari support. |
| Wake word ("hey willow") | `openWakeWord` (browser adapter) | **Apache-2.0** | Real Apache-2.0 option; ships in Grove only as **add-on** (P7 — voice-off is valid). |
| Infinite canvas / pan-zoom | `xyflow` (React Flow / Svelte Flow) | MIT | Only if a persona-cast or fleet graph gets a canvas view. |
| ASCII text art | `figlet.js` | MIT | Ambient art (headers, wordmarks). |
| Block content | **Editor.js** | **Apache-2.0** | P4. Card bodies as ordered JSON blocks. |
| Decision graph | **Cytoscape.js** | MIT | Inlined into served page, no CDN. Nestor decision 0137 already commits Grove to this. |

### Explicit avoids (surveyed and rejected)

- **`tldraw`** — custom license requires paid production license keys.
- **`GSAP`** — proprietary "standard license" with TOS restrictions on commercial use.
- **`jsPlumb Community`** — GPLv2. Out.
- **`porcupine-web` (Picovoice)** — proprietary engine + AccessKey (phones home since v2.0).

### Framework choice — sealed as D9

**Vanilla JS (ES2020+ modules) + Web Components + no build step.** See
D9 in the Decisions section for the sealed reasoning. Short version:
Grove ships as a single served page (`gates_serve` pattern); 10 of the
11 Grove-specific libs are framework-agnostic; React-only libs
(`dnd-kit`, `react-spring`, `xyflow`) aren't needed for Grove's actual
mechanics (edge-summoned cards, fixed viewport, simple state); Web
Components give component architecture natively; consistent with the
fleet's existing HTML surfaces (willow-mcp `gates_serve`, Nestor UI,
Jarvis's browser app all vanilla). Trade-off: no React ecosystem; if a
later Grove wants shadcn or a deep component library, that's a rewrite.
Accepted because Grove's interactions are simple (summon / dismiss /
type / speak / hover), not deep component trees.

## Discipline — how future Grove sessions ask before writing

Operationalizes the two moves from `the-house-already-knew.md`: **point
memory infra inward, find the second reader**.

### Point memory infra inward (Nestor + Jeles as Grove-local witnesses)

- **Grove's design decisions live in a Nestor store.** During this
  session, decisions were seeded into a scratch store
  (`nestor:willows-grove.db`, 31 sealed + 1 draft as of the last pass).
  For the persistent build, a Grove-owned Nestor store on
  `$WILLOW_HOME/nestor/willows-grove.db` holds every design decision as
  an evidence-backed sealed pair (per D8's two-witness pattern).
- **Before proposing any new design decision, run**
  `nestor decision check "<question>"` — the fuzzy matcher surfaces
  near-matches with the "read it before proposing" bounce. This is the
  Mistletoe / anti-rediscovery pattern made runtime.
- **Before adding an add-on, run** `jeles conflict_scan` (or the
  corresponding tool) — search for what refutes rather than what
  resembles.
- **Every persistent seat opens by asking, not by writing** — Grove's
  session-boot injects the latest sealed pairs into context so the seat
  boots knowing what the house already decided.

### Find the second reader (avoid one-witness-with-two-prompts)

Article 0 §0.2's Independent Witness bar — *"separate instances of the
same base model are presumed non-independent… three instances of one
model are one witness, not three."* Grove's ratification path must
route through:

- **A different base model** (e.g., a local model reviewing a claim
  sealed by a cloud model), OR
- **A person** (the operator) via the `human_required` queue.

Grove's Governance lens renders both paths distinctly and never counts
same-base agreement as corroboration.

### The runtime check surface

Grove exposes a small Governance-lens sub-panel that runs
`nestor decision check` on any proposed operator action (envelope
create, dispatch, canon promotion) and blocks with a *"read this first"*
card if a sealed decision is fuzzy-matched. Not a hard gate — the
operator can override — but the seal card is visible before the
override.

## Open decisions (still on the table)

*Reduced from the earlier list — several items settled by later
decisions or artboards. What remains:*

1. **Chat / summoned-card interaction** — when the chat card is
   summoned and the operator asks Willow to open envelopes, does
   Envelopes appear **beside** chat (narrowing it) or **replace** it
   with a return path? Both are viable; the modality-agnostic model
   supports either.
2. **Full-cast render vs trust-tier orbit** — all agents visible always,
   or trust-tier orbits (OPERATORs closer to Willow, WORKERs outer,
   Bureau's 5 non-graduated appearing only when their app is engaged)?
3. **Voice-panel materialization discipline** — when a spoken intent
   lands (WO-1), which surface materializes and by what rule? Depends
   on the utterance arbiter's decision and the reaction engine's
   `surface_card` action, but the specific mapping needs a table.
6. **Chat's home-edge (or lack of one)** — is chat a card on an edge
   (probably top-center as a persistent affordance), or purely
   voice/keyboard-summoned with no visible tab?
7. **Which desk layout ships as the default** (P9 says configurable —
   discord / slack / mission-control / minimal / journal-first / mobile
   / custom — but which is Grove's day-one).
8. **The parked bloom-row overlap** on the v1 artboard (documented; the
   v4 quiet-desk artboard resolves it; confirm on next full redraw).
9. **How `homestead-affairs` peer-seat coexistence renders on the
   desk** — if the operator has both Willow's Grove and Homestead
   running, do they cohabit or context-switch?

*Settled since the earlier draft:*
- ~~Framework choice~~ → **D9 sealed**: vanilla JS + Web Components + no build.
- ~~Nestor integration path~~ → **D11 sealed**: `nestor serve` MCP-over-stdio; card-native rendering, not iframe.
- ~~Persona-roster mint location~~ → **D10 sealed**: `willow-memory/willow/fleet_personas.json` (charter-adjacent to fleet.json).
- ~~Free-float vs grid-snap~~ → Modalities artboard + Envelopes-summoned
  artboard settled the summonable-card model (edges + slide-forward).
- ~~Bureau's 7 alongside fleet.json's 16~~ → V-layer picked 9 in-production
  personas; Bureau's 5 non-graduated remain in `apps/bureau`, surface
  only when their app is engaged.
- ~~Jarvis memory integration path~~ → D5 sealed: handler-call, not
  iframe or mirror.
- ~~Tri-modal desktop redraw~~ → Quiet Desk / Summoned / Modalities
  artboards published; base-vs-add-on covered; layout under P9.

## What this doc does not do

- Does not create envelopes, sign anything, or ratify a decision.
- Does not touch code — no imports changed, no wiring done.
- Does not speak for the operator. The seat proposes. USER ratifies.

## Related work

### In this repo
- `docs/design/forge-convergence.md` — Forge checkpoint / human_required convergence
- `docs/synthesis/the-one-desk.md` — ONEDSK (five-layer stack)
- `docs/synthesis/grove-starter-borrow-map.md` — GSBRW (steal-vs-wrap for third-party TUIs)

### In willow-mcp
- `docs/PRIOR_ART.md` — the 837-line ecosystem survey (parent for the Stack section above)
- `docs/design/pgp-and-persona.md` — attestation gate + persona picker discipline
- `docs/design/permissions-matrix.md` — the grove_read/write split
- `docs/design/consent-toggles.md` — the three toggles
- `docs/design/specialist-registry.md` — canonical roster shape
- `docs/design/session-lifecycle.md` — three entry modes, dispatch state machine
- `docs/design/ui-concepts.md` — tree / stomata / trunk / sap / canopy metaphor
- `src/willow_mcp/server.py:2607` — `kb_journal` (chat substrate)

### In willow-memory/willow
- `design/jarvis-build-orders.md` — WO-1 (voice) + WO-2 (commitment) build orders
- `design/willow-voice-ingress-membrane.md` — the 6-state voice pipeline
- `design/willow-utterance-arbiter.md` — the sibling output layer
- `design/willow-commitment-membrane.md` — dew-rule surfacing
- `design/egress-membrane-constitutional-map.md` — reach over content, not endpoints
- `design/reaction-engine.md` — surface_card is Grove's inbound edge
- `CONSTITUTION.md` — Article 0 + Articles I–XIII, Trace IDs
- `envelopes/pre-approved.json` — active grants (canonical envelope registry)
- `fleet.json` — canonical roster (16 agents, 3 trust tiers)

### In safe-app-store
- `docs/the-house-already-knew.md` — the discipline reminder
- `docs/the-fourth-store.md` — Nestor as fleet's sole decision keeper
- `docs/app_store_vision_and_gaps.md` — persona-drift warning, consent-unenforced warning
- `libs/fleet-presence/` — announce/roster/withdraw seam
- `apps/jarvis/` — memory substrate (IndexedDB + handlers)
- `apps/ratatosk/` — sovereign Claude-Code-alt, already Grove-wired

### In hornbook-knowledge
- `Jeles/docs/design/host-cards.md` — cards carry facts, consumers hold policy
- `Jeles/docs/design/reaction-engine.md` — `react(event, deps) → [proposal]`; gateway vets
- `oakenscrolls-office/almanac_seam.py` — reference for lazy-import + graceful degrade

### In homestead-affairs
- `homestead/docs/PHASE2-SURFACES.md` — the 5-surface rung ceiling
- `homestead/docs/DECISION-agent-retrieval.md` — S3_AGENT locked at L2/L2
- `homestead/docs/PLAN-first-runnable.md` — off-machine head anchor pattern
- `apps/homestead-health/docs/DECISION-living-lane-ledger.md` — IntegrityLog head anchor

### In Nestor
- `nestor/persona.py` — SPEECH_ACTS + NEGATIONS guard
- `docs/dogfood/decisions/0053-two-desks.json` — pair-surfaces defense
- `docs/dogfood/decisions/0055-jeles-bridge.json` — two-witness ledger discipline
- `docs/dogfood/decisions/0099-mutation-guard-proves-refusals.json` — real-security pattern (see W4)
- `docs/dogfood/decisions/0116-before-build-the-anti-rediscovery-hook.json` — advisory hook (see Discipline)
- `docs/dogfood/decisions/0137-read-only-decision-graph-in-desk.json` — Cytoscape inline commitment
- `docs/dogfood/decisions/0190-propose-refusal-gate.json` — seal-authority refused at surface

### Live artboards (design canvases)
- Voice Layer: <https://claude.ai/code/artifact/7454eb90-2674-4901-ae7c-7c57a9ac6f24>
- The Desk (Quiet / Summoned / Modalities): <https://claude.ai/code/artifact/65b9be2a-40cc-4b2f-b55d-16d4e699edb2>
- Grove Home (v1 — pre-reframe, kept for provenance): <https://claude.ai/code/artifact/25e72759-d647-4d17-aa1a-800e88741565>

ΔΣ=42
