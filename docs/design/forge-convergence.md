# The Forge convergence: one session machine

**b17: WGRV1 ΔΣ=42** · proposed 2026-09-23 by vishwakarma · root ratifies

**Status:** proposal. Nothing here is built. The organizing model for step **0**
and cloud use is **§1.5** (one tree, one soil; growth vs flowering).

`willow-grove-premise.md` has linked to this file since before it existed, as
"Forge checkpoint / human_required convergence". This is that paper. It is
wider than the link promised, because the convergence turned out to be the
whole session and not only the checkpoint.

**Operator, 2026-09-23**, across one conversation:

> I've been thinking about session start in willow-mcp, and how sessions run,
> and I think the forge could be a good shape to adopt.

> between the forge and willow, there should be willow-gate. It's still an
> immature tool, but we gotta start getting it up and in.

> The runtime and flowcharts from willows-grove. I think if you look at the
> way things have been setup, and how I've attempted to wire things together,
> you'll have a better understanding of where I'm trying to go (see the hook
> to the forge here, huh (hook pulls me offstage))

> lets land the paper in the grove.

**Operator, 2026-09-24** (desk — one tree, one soil):

> For willow (user and agent) it is planted in one soil. Trees don't operate
> as complex thinking models — I need this from the soil, or from wherever in
> the case of the system (Jeles, nestor, SOIL, et al). New branches can be
> spliced on (the other orgs or other repos) but the tree only draws what it
> needs when it's growing. When it's ready to flower it stores up that material,
> ready to produce the bud. … Local models can do so so much connect x to y,
> and that builds up and collects, and by the time all of those pieces are in
> one place, then the system (via the nest, or the multitude of other tools that
> are in the box …) … using these collection pools, we can eliminate almost all
> of the need to cloud models.

**Supersedes:** `forge-play/Forge` `docs/design/the-session-entry.md`
(branch `design/session-entry`, unmerged). That paper put the session's door
at the MCP verb. This one moves it to the hook. The Forge keeps a pointer.

**Builds on, does not replace:**
[`governance/proposals/2026-09-02-grove-hooks-and-skills.md`](../../governance/proposals/2026-09-02-grove-hooks-and-skills.md)
(the flowchart, its state table, and how rows land) and
[`the-forge-shape.md`](the-forge-shape.md). willow-mcp:
`docs/design/willow-gate-seam.md` and `docs/design/stateless-session-state.md`.

---

## 1. The claim

A session and a Forge bite are the same machine at two scales.

The hooks proposal says it in its own words: "A hook is a truth table. Event
and state in, one action out. The model sits at a leaf, never at a branch."
The Forge's entry says the same thing about a build: "The model is never
consulted: the scan is a regex over a table, the routing is memory." Both
rules come from `the-forge-shape.md` §2, §3 and §9.

Taken one step further, **a sealed row is a decision this human already
made**, and the Forge's goal is to proceed without asking only where that is
true. That is "the hook pulls me offstage". When a row is sealed, the hook acts
in the operator's place and the operator is not called. They are called back
only where nothing is sealed, and the close-out names that act in one
sentence (hooks proposal §3, "The close-out is an offer, not a checklist").

Mapped piece for piece:

| The session (grove) | The bite (Forge) |
|---|---|
| `session_start → orient`: every state from its reader, or `unreachable` | `open_bite`'s tiers: nestor, deposit, main, box, remote, each named, none silent |
| Rows are `(event, state) → action`, stored as sealed pairs | `run_checkpoint`: a decision this maker sealed is confirmed, not asked again |
| `session_end → deposit`: "propose unsealed pairs to the project Nestor" | `forge.deposit`: `ProposeOnly`, drafts only, never a seal |
| `stop → gate`: refuse a turn claiming done with no evidence | the Forge's refusals: an unasked entry, an ambiguous major with no choice |
| The close-out offer: "the store is open if you'd like to sign them" | `forge.human_loop`: the human-required queue and its attestations |

willow-gate stands at the two edges of that machine: it checks in at the
session's start and reconciles at its end.

## 1.5 One tree, one soil

The convergence arc is not "use Ollama more." It is **one organism** for the
operator and the Willow desk: **one soil**, incremental **growth** from what
the soil already holds, **collection pools** that accumulate joins, and
**flowering** only when enough material sits in one place to form a bud. Cloud
models are not daily metabolism; they are optional pollination when the pools
and local joins cannot close the bud.

**Soil (one ground for this tree).** The operator box nutrient layer: SOIL
collections (`stack`, commitments, orient aliases), Nestor ledger and seals,
Jeles corpus store (`$WILLOW_STORE_ROOT/ask_jeles_corpus/…`), Postgres readers
the grove uses, gap log, FRANK, handoffs, envelopes, federation to organs.
The tree does not invent doctrine; it **draws** from readers and sealed rows,
then adds thin **local joins** (connect *x* to *y*) via `nestor_draft`, nest
intake, hook deposits, and deterministic Python (host or Kart where policy
allows).

**Trunk and grafts.** **Willow (human + orchestrator seat)** is the trunk —
one `app_id`, one filing namespace, one gate registration target (§9 row 5).
**Grafts** are other repos and fleet apps (Hanuman checkout, Forge
`forge-engine`, workshops, federated MCPs): they splice on with their own
manifests and stores, but they do not get a second soil for the operator tree
unless federation or promotion explicitly says so.

**Session sapwood → heartwood.** `~/.forge` (and session-scoped drafts) are
fast, writable **sapwood** — rings of the current session. **Promotion on human
seal** moves material into SOIL (living ground: stack, next bites, orient) or
KB (fruit for others). Nothing crosses that boundary unsigned (§5). Open detail:
which atoms land in SOIL vs KB (§9 row 2).

**Growth vs flowering.**

| Phase | What happens | Typical tools |
|---|---|---|
| **Growth** | Many small, cheap passes; connect *x*→*y*→…; fill pools; measure **chain depth** per tier, then next tier builds on the **bundle** (experiment secondary) | `nestor_draft` + structured join rows, Nest intake, friction deposit, gap log, corpus-lens / reconciler joins, WCE, handoff drafts, host/Kart Python when policy allows |
| **Flowering** | Enough collected **in one place** to produce the bud | Operator seal, envelope ratify, bounded Hanuman dispatch, PR open, or — only if pools cannot close it — **one cloud pass** on material already in the pools |

**Collection pools (accumulators, not oracles).** These are the "multitude of
tools in the box" that **collect** before anything expensive runs: Nest
(review queue, matcher), Jeles corpus + federation read path, SOIL/KB store,
gap backlog, FRANK attribution, dispatch log + handoffs, `forge.human_loop`,
friction floor / SessionEnd deposit, idea→landing reconciler (when built),
corpus-lens analyzers, codebase-memory graph, activation-rail wake drafts,
watcher classify when live. Local models serve **growth** at the edges between
pool outputs; they do not replace the pools.

**Cloud-only-when (the bud rule).** Routine work should route **growth → pools
→ local join** until a **flowering threshold** is met: the operator (or a
sealed row) can name what "enough in one place" means for a given act — e.g.
dispatch brief complete from excerpts, gap + evidence cited, reconciliation
inputs present. Cloud Task / subagent / Opus audit is **flowering**, not the
default path. Whether this eliminates "almost all" cloud use is **unknown until
measured**; that measurement is §6 step **0**'s first obligation (below).

**How the tree reads §9 (direction, not ratified).**

| # | Tree read |
|---|---|
| 1 | Trunk id = Willow project + checkout; `.forge/project` beside handoff name (v08 diamond). |
| 2 | One soil per operator tree; KB = published fruit, SOIL = living ground; seal = sap → heartwood. |
| 5 | Trunk (`willow`) registers with the gate first; grafts consume trunk policy when touching operator soil. |
| 6 | One nutrient policy at the soil interface (willow-gate tier ∩ manifest); hosts render, they do not invent a second policy on the same event. |
| 7 | Forge `builder_id` = gate-bound identity on the graft branch. |
| 9 | Soil + ledger canonical; IDE harness vs Ratatosk = two draw paths; disagreement → wiring pin, not "pick a host." |

## 2. What exists, measured 2026-09-23

Read this session, from disk. The Ratatosk and drawio readings were done by a
survey agent with file:line against the tree (the code graph's Ratatosk index
is stale and was not trusted). The rest were read directly.

### The flowchart, sealed ahead of the code

Five rows are sealed in `governance/decisions/grove-hook-rows-sealed.json`:
`session_start → orient`, `prompt_submit → reinject`, `pre_compact → reinject`,
`stop → gate`, `session_end → deposit`. They are rendered to `hooks/wiring.json`
by `scripts/generate_grove_hook_wiring.py`.

What actually runs is a second source: `hooks/client-hooks.json`, compiled by
`scripts/sync_desk_client_hooks.py` into `.claude/settings.json` and
`.cursor/hooks.json`. The two disagree:

| Row | Sealed | Running |
|---|---|---|
| stop | `gate` (Grove's own `gate()`, `hooks/grove_hook.py`) | `before_stop`, which is willow-mcp's stop lint. **Grove's `gate()` is wired to no event.** |
| session_end | journal decisions and edges, propose unsealed pairs, write the stack snapshot | writes `{session_id, app_id, tool_calls, seat_drift}`; the docstring says the Nestor and journal writes are "a follow-up" |
| session_start | the hooks proposal's §2 state table (seam reach, packet, envelope, corpus age, attestation, unit manifest, model rung, port ownership) | blockers, seat drift, Nestor reach, the events line. Packet, envelope, corpus age, unit manifest and port ownership are not read |
| reinject | three byte-stable lines | four lines plus inbox lines |

This is declared against done, one level up: the flowchart itself drifted.
The hooks proposal's §6 pin was meant to catch exactly this. It compares
`wiring.json` to the store. Nothing compares `wiring.json` to what runs.

### Two hosts run sessions

**The IDE harness** runs every event through `hooks/grove-hook` into
`grove_hook.py main()`.

**Ratatosk** (`willow-memory/ratatosk`, `ratatosk.crown`) is the fleet's own
session runtime. It brackets a session exactly as the drawio
`willow-session-start` diagram draws it: `seat.enter()` calls `session_enter`
and refuses on error; `_shutdown` calls `session_handoff_write` or
`handoff_write_v4`; both are posted to the Grove bus. Its hooks
(`$WILLOW_HOME/ratatosk/hooks.json`) fire `SessionStart`, `SessionEnd`,
`PreTool`, `PostTool`, `PermissionDenied`, `PreCompact` and `PostCompact`.

For this paper, three things about Ratatosk matter:

- **It has no `Stop` event and no prompt-submit event.** The `stop → gate` and
  `reinject` rows have nowhere to run there.
- **It discards lifecycle hook results.** A `SessionStart` or `SessionEnd`
  hook cannot inject or gate anything, so the `orient` row cannot print into
  a Ratatosk session.
- **It carries its own permission gate** (`ratatosk.permission`: `PolicyStore`
  over tool names and `CapabilityGate` over intents, most restrictive wins).
  It does not import willow-gate, has no check-in and no trust ladder, and
  cites CONST-X-4 instead. `NeedsConfirmation` reaches a human only through
  the REPL's stdin. A woken seat never prompts, and `PendingConfirm` has no
  persistent queue. Its own comment (`tools.py`) names the fix: adopt the
  Forge's `human_loop`. That is the only Forge reference in the repo.

`SeatDaemon`'s seal watcher (`JsonlTailWatcher` over the Nestor ledger) calls
an `on_seal` that only logs. Its docstring says the real consumer, which would
upgrade the SOIL record keyed by `nestor_pair_id` to `status=sealed`, is a
willow-mcp task.

### willow-gate is mostly built, and its doors are not joined

willow-mcp shipped three phases of `willow-gate-seam.md` (per its CHANGELOG):
identity binding in observe mode (`agent_registry.py`, `session_binder.py`,
with the binder's ladder pinned to `willow_gate.TRUST_LEVELS` by
`tests/test_gate_take.py`); tier-ceiling enforcement (effective tools =
manifest ∩ tier ceiling), off by default behind `WILLOW_MCP_ENFORCE_BINDING`
and per-agent registration; and session reconciliation (`session_reconcile`),
a declared-against-done diff whose "done" side is `ReceiptLog`, which the
agent cannot write to. It records and never blocks.

The seam doc's §4 says `session_enter` performs the check-in. It does not:
`dispatch.session_enter` and its `server.py` wrapper bind a session file and
build `orientation`, and neither calls the binder. Reconciliation runs
"alongside `session_handoff_write`, not in front of it." The seam doc's
status line still reads "proposal / mapping only (no code yet)".

`stateless-session-state.md` measured the other half: binder sessions,
`entry_declared` and the server-stamped `started_ts` live in process memory,
so after a restart or on another process `session_reconcile` returns
`no_live_session`, and "the H3 declare-vs-did audit silently stops happening."

`install-graph-survey-2026-09-08.md` (this repo): `gate/registry.json` is
empty and `WILLOW_MCP_ENFORCE_BINDING` is unset. No seat is registered.

### The Forge is installed and mostly unused

willow-mcp pins `forge-play>=0.1.0,<1.0.0` as a hard dependency and uses
three re-exported modules (`human_loop`, `friction_floor`, `model_egress`) and
one call (`meter.py`, `is_local_host`). Nothing calls `forge.entry`, the
checkpoint router, `deposit`, `bundle` or `store_diff`. The Forge never
imports willow-mcp, and `tests/test_no_reach_back.py` enforces that.

The drawio `willow-v08-toolchain-path` diamond, "is the forge wired on this
box?", has no answer: its REVISIONS box says "there is no flag a repo can
consult".

## 3. The door is the hook, not the verb

`session_enter` and `session_handoff_write` are verbs a model has to remember
to call. `the-forge-shape.md:842` recorded what that costs: "An advisory alone
has already been tried and did not fire." A hook fires whether anyone
remembers or not.

So the two edges of the session machine are the rows, and the verbs become
what the rows call:

- **`session_start → orient`** performs the gate check-in and reports every
  state.
- **`session_end → deposit`** performs the reconciliation, deposits, and makes
  the offer.

That is the same join the gate seam doc drew (`check_in ↔ session_enter`,
`check_out ↔ session_handoff_write`), made at the layer that cannot be
skipped.

### One flowchart, every host a renderer

The hooks proposal already treats `hooks/wiring.json` as "an artifact of the
store, never the source". This paper extends that to every host:

- **The IDE harness:** the rows render into what `.claude/settings.json` runs.
  The running wiring is generated from the sealed rows, not compiled from a
  second hand-kept file, and a pin fails when what runs differs from what is
  sealed.
- **Ratatosk:** the same rows render into `hooks.json`. Ratatosk needs two
  changes before the rows can run there: a `Stop` event, and a lifecycle-hook
  contract whose result is read (for orient's output and the deposit's
  offer), not discarded.

A row sealed once runs the same way in both hosts, or its absence in a host
is reported, never silent.

## 4. The rows, converged

### session_start → orient

The hooks proposal's §2 state table is the specification. What converges
onto it:

- **One state vocabulary.** A small `forge.tiers` module in the Forge
  exports the states and a frozen `Tier(name, state, detail)`. Grove's
  readers, willow-mcp's orientation and the Forge's entry all report in it,
  so "unreachable" means the same thing in all three and the vocabulary has
  one home. INVARIANTS §1's three states (populated, empty, unreachable) are
  its base. The Forge's entry adds `not_attempted`, and willow-mcp's
  orientation adds `unconfigured` (no route, e.g. `alias_not_configured`) and
  `denied`.
- **Gate check-in**, when the seat is registered. The tier reports `bound
  (tier <n>)`, `unconfigured: seat not registered`, or `unreachable`. An
  unregistered seat enters exactly as today, which is the seam doc's opt-in
  rule unchanged.
- **The previous session's reconciliation verdict**: `reconciled`,
  `discrepancy` with the diff, or `unreachable`.
- **Next bites**: the open ones for this project, from any seat (Open, row 4
  settled "yes"), each with its state.
- **Project identity**: read from the checkout (Open, row 1). This is also
  the answer to the v08 diamond.

### stop → gate

Grove's `gate()` checks a single turn: a claim of "done" with no tool use
behind it. willow-gate's reconciliation checks a whole session: declared
against done, with receipts as ground truth. They are the same check at two
scales, and both belong in the machine. The first step is only to run the
row that is already sealed: wire `gate()` to `Stop` as `wiring.json` says, or
re-seal the row if willow-mcp's stop lint is what was meant. Either way, the
seal and the wiring must agree.

### session_end → deposit

The sealed row, built:

1. **Reconcile** through the gate (registered seats), and record the verdict
   for the next orient.
2. **Journal** the session's decisions and edges through `kb_journal`.
3. **Propose** unsealed pairs to the project Nestor through the Forge's
   `deposit.ProposeOnly`, the one facade the Forge allows to write a project
   store (propose, propose_edge, revise_draft; nothing else). The session
   never seals.
4. **Next bites.** Each gets a gap (`gap_log`), with an open → resolved
   lifecycle that already exists. A pair is proposed only when a bite turns
   into a decision. Operator, 2026-09-23: "both, with a gap per bite and a
   pair only when a bite is decided."
5. **The offer**, exactly as hooks proposal §3 states it: read the state,
   take the action, and let the voice speak once.

A SessionEnd hook cannot block (hooks proposal §7). The deposit warns and
flushes, and the gate's reconciliation records and never blocks. The two
rules agree.

### pre_tool_use

It stays willow-mcp's guard: one guard per event (hooks proposal §3). The
gate's tier ceiling already lives *inside* that guard (`_enforce_binding_gate`
within `_gate`), so willow-gate adds no second hook. Ratatosk's
`ratatosk.permission` is a second, separate gate on the same event in the
other host. This paper does not merge them (Open, row 6).

## 5. Checkpoint and human_required: the convergence the link promised

**One human-required queue.** The Forge's `human_loop` is the canonical
human-required queue and attestation store; willow-mcp re-exports it.
Ratatosk's `PendingConfirm` has no queue at all, and its own code says to
adopt `human_loop`. The deposit's offer ("one command is waiting on your
terminal") is a human-required act too. Three producers, one queue:
`forge.human_loop`. Whether willow-mcp's `human_required_*` verbs already
write through the re-exported module or keep a store of their own was not
read this session. That gets verified before anything is built on it.

**Sealed rows are checkpoints the operator already passed.** A hook row runs
without asking because a person sealed it: the Forge's auto band, at the scale
of the session. The difference matters. Hook rows are sealed in the Nestor UI
with the operator's key, so their seals can be verified. The Forge's
per-builder checkpoint store cannot yet verify its own (`the-positional-default.md`
in the Forge, gap 3; `by_human` is structurally false on the entry's path). So
the rows may act on sealed decisions now, and **the Forge's band router at
session start stays held** (§7).

**The seal is the promotion.** Operator, 2026-09-23, on where session state
lives: "~/.forge should be for the session, and then it gets promoted to the
willow soil (or kb) still uncertain about this shape." Ratatosk already has
the trigger half-built. `SeatDaemon` tails the Nestor ledger for seals, and
its docstring names the missing consumer: upgrade the SOIL record keyed by
`nestor_pair_id` to sealed. Proposed shape: a draft lives in `~/.forge`; **a
human seal is what promotes it** into Willow's SOIL or KB; and the watcher
that already sees the seal carries it across. Nothing is promoted that a
person did not sign. SOIL versus KB stays open (Open, row 2).

## 5.5 Execution: PR waves, doc strikethrough, specialist routing

Willow desk, 2026-09-24 — how this paper lands **with** the build PRs, not
after. Each merged step strikes its §6 line here the same way §9 keeps settled
rows (~~struck~~ + evidence). Hanuman lands code and doc edits in one PR per
wave; Loki audits each Hanuman handoff before push; Willow ratifies envelopes,
`grant-net`, and the PR `Ratified-by:` trailer. Discovery on dispatched work
uses **codebase-memory-mcp** on the indexed project slug (not grep-first).
Subagents and fleet dispatches use their own `app_id` and repo root (`hanuman`,
`loki`, … — never `willow` on the worker).

**Specialists**

| Agent | Assignment |
|---|---|
| **Willow** | Envelopes, egress lease, ratification, merge verify, gap resolve when a step closes. Exclude unrelated checkout dirt (`seat/willow/jeles-intake/willow-local.json`) from forge PRs. |
| **Hanuman** | All implementation: hooks, sync, tests, changelog, §6 strikethrough in the same PR as the step. Kart / `task_submit` with `app_id=hanuman`. |
| **Loki** | Adversarial audit after each Hanuman slice, before PR open. Read-only; file:line findings. |
| **Jeles** | One read: §9 row 10 — do `human_required_*` verbs write through `forge.human_loop`? (Before §6 step 6 deposit work.) |
| **Ada** | **Wave 0:** bibliography (§6 **0**) + support **flowering-threshold test** once operator defines protocol. **After each push:** `pr_checks_read` until every leg is conclusive. |
| **Vishwakarma** | Idle unless hook semantics change (re-seal vs `gate()`, composite `session_start` / `session_end` vs sealed action names). |
| **Heimdallr, Skirnir, Binder** | Out of scope for this wave unless serve/auth or homestead records are touched. |

**PR waves (build order aligned with §6)**

| Wave | Repo | Closes (strike in doc when merged) |
|---|---|---|
| **0** | *(gather + test — Ada bibliography; operator flowering protocol)* | §6 **0**: bibliography read; **flowering-threshold test** run per operator-defined shape; soil chemistry fixes if test fails; operator signs step 0 done. Does not strike until signed. |
| 1 | `willows-grove` (`docs/forge-convergence`) | Paper land + §6 **2** (sealed rows ↔ running wiring; `stop → gate`; pin). §6 **1** grove bullets (premise link, this file). PR body: operator ratification on landing the paper. |
| 2 | `forge-play/Forge` (`design/session-entry`) | §6 **1** — `the-session-entry.md` pointer only. |
| 3 | `willow-mcp` | §6 **1** — `willow-gate-seam.md` status matches shipped code. Optional: manifest grove tools (gap `1afd7033540d`). |
| 4+ | Forge / grove / willow-mcp / ratatosk / workshop | §6 **3–9** one dispatch at a time; operator answers §9 rows **5–7, 9** before steps **7–8** enforce choices. |

**Gaps on this program:** `41dd889bd7bd` (step 2), topic `forge-convergence` (operator table), `1afd7033540d` (manifest). Carried seal: Nestor pair `586af047` (operator UI, not a dispatch). FRANK `14740993` records the design commit.

**Dispatch rhythm:** Wave **0** (Ada bibliography + desk probes + **flowering-threshold test** — §6 **0**) completes before Wave 1
→ optional Loki drift resurvey → Hanuman wave → Loki audit → Willow ratify → Ada CI watch.

**Wave 0 (blocks §6 steps 1–9):** Inventory local-model corpus (Ada **0a–0c**), record live probes, then run the **flowering-threshold test** the operator defines (§6 **0**). Bibliography alone does not strike step 0. See §1.5 and §6 **0**.

## 6. Getting it up and in, in order

Each step reports before the next one acts on it. Struck lines are landings;
open lines are still build or operator.

0. **Growth, pools, and the flowering threshold (before §6 1–9).** Operator,
   2026-09-23–24: the fleet built deterministic bands and local paths, but they
   are not the hot path; cloud still carries routine work. §1.5 names the target:
   **one soil**, **collection pools**, **local *x*→*y* joins** during growth,
   **cloud only at flowering** when enough material is in one place. Whether
   that eliminates almost all cloud use is **not assumed** — it must be **tested
   properly** before hook convergence PRs (§6 **1–9**) land.

   **What step 0 proves.** Not a reading list. A bounded experiment: on real desk
   turns, **pools fill and local joins fire** during growth, and **cloud /
   Cursor Task / fleet dispatch** fires only when the **flowering threshold**
   for that act is met (operator-defined shape — recorded in stack/gap when
   ratified). Failure modes already measured: wrong soil chemistry (sealed rows
   ≠ running hooks; draft model ≠ SOIL `active_model`; Nestor retrieval hijacks
   excerpt-only drafts) — fix soil before blaming the metaphor.

   **First test (blocks everything else in this step).** The operator will define
   the **specific shape** of the flowering-threshold protocol next (scenarios,
   pass/fail, what counts as "enough in one place," what escalation markers
   force cloud). Until that protocol is written, run once, and signed off, §6
   **1–9** stay open. Pre-registered protocol:
   [`forge-convergence-flowering-experiment.md`](forge-convergence-flowering-experiment.md)
   (hypotheses, materials, tests T0–T6, expected findings E1–E6, post-run §9).
   Operator completes §8 sign-off there before T0.

   **Inputs already on disk (not completion):**

   - **Ada Wave 0a–0c** (`B2E3BBF4`, `EA120C8D`, `6435121E`) — stack ids
     `forge-convergence-wave0a-B2E3BBF4`, `forge-convergence-wave0b-EA120C8D`,
     `forge-convergence-wave0c-6435121E`; handoffs
     `handoffs/ada/willows-grove/wave0*-*.md`. Operator reads all three.
   - **Measured probes (2026-09-24, Willow desk).** Stack:
     `forge-convergence-step0-probes-2026-09-24`. Method: `nestor_draft` +
     Kart task `QLJG1E0L` (loopback blocked in sandbox).

   | Probe | Result |
   |---|---|
   | JSON classify (schema in prompt) | pass |
   | Summarize with `excerpts[]` | pass (three tight bullets) |
   | Summarize with source only in `task` | fail — model denies knowledge |
   | Out-of-domain (“file taxes”) | pass — `ESCALATE` |
   | `desk_attention` title from CI snippet | pass |
   | Tool-route one-liner | partial — `escalate` |
   | Compare merge vs force-push intent | fail — false `SAME` |
   | Policy Q&A (egress / allow_localhost) | fail — confident wrong |
   | Gap question from Wave 0a excerpts | fail — unrelated sealed pair injected |

   **Runtime facts:** drafts used **`llama3.2:3b`**, not SOIL `active_model`
   (`willow-lane4-3b:latest`). Kart **cannot** reach loopback Ollama
   (`allow_localhost` retired; sandbox `network_mode: isolated`) — the
   [`2026-09-02-mcp-jobs-ladder-test-plan.md`](../governance/proposals/2026-09-02-mcp-jobs-ladder-test-plan.md)
   batch still needs a host runner or `task_localhost`, not a cloud Kart task.

   **Growth-shaped coverage (for the test, not cloud replacement):** pre-dispatch
   `nestor_draft` with **`excerpts` only**; desk-attention copy from CI snippets;
   gap drafts without open retrieval; SessionEnd stance from deposit JSON;
   nest intake via `nest/llm.py` when Ollama is up; wake-draft triage;
   semantic KB / watcher classify when live. **Not flowering:** policy Q&A
   without sealed excerpt in prompt; full ladder batch without host runner;
   novel implementation (Hanuman) without bounded brief in pools.

   **Soil fixes (engineering enablers if the test fails — pick after protocol):**
   (A) `provider_ladder` on box + Nestor draft floor per KB **24097A70** + host
   fixture runner; (B) one hot path — excerpts-only `nestor_draft` before Task,
   log latency and operator thumbs; (C) retrieval tuning so unrelated seals do
   not hijack excerpt drafts.

   **Step 0 strikes when:** operator signs that the flowering-threshold test
   (defined shape, executed, verdict recorded) is done — not when bibliography
   alone is read.

1. **Papers agree with the code.** Correct `willow-gate-seam.md`'s status in
   willow-mcp. This file resolves the premise's link. The Forge's
   `the-session-entry.md` becomes a pointer here.
2. **The seal and the wiring agree.** Generate the running hook wiring from
   the sealed rows, and pin it. Resolve `stop → gate` (§4).
3. **One vocabulary.** `forge.tiers` in the Forge. orient reports every §2
   state from its reader, or `unreachable` with a reason: the hooks
   proposal's own verification item 2. Measure on one seat before it applies
   everywhere. Surfacing swallowed failures will be noisy at first, and that
   noise is information.
4. **The binder session is durable.** Keep `entry_declared` and `started_ts`
   beside the check-in nonces, which are already a shared file. Without this,
   steps 5 and 6 report on a control that is not running.
5. **The doors join at the rows.** orient checks in, and the deposit
   reconciles, for registered seats only.
6. **The deposit is built** as §4 lists it.
7. **Ratatosk renders the rows:** a `Stop` event, lifecycle results that are
   read, and `hooks.json` generated from the same rows.
8. **One seat is registered, in observe mode.** `WILLOW_MCP_ENFORCE_BINDING`
   stays off until the operator has read real verdicts.
9. **The workshop template carries the tracked hooks**, so every workshop
   made from `forge-play/forge-workshop` runs the flowchart from its first
   session. Hooks are per-checkout; the template is how the machine reaches
   a new project.

## 7. Held

**The Forge's band router at session start.** Two measured defects hold it,
both in the Forge. Band selection ignores the maker's calibration: two makers
100 points apart take identical band paths, and a maker wrong on every
decision still has 83.3% auto-applied (`the-forge-pedagogy.md` §5, pinned by
`tests/test_band_probe.py`). And the entry's seals are not verified. It waits
until both are closed. Sealed hook rows (§5) are not held, because their seals
can be checked.

## 8. Rules

- **Session entry never refuses on an orientation source.** A source that
  cannot be read is a state in the report. willow-mcp's orientation already
  keeps this ("Orientation is sugar. It must never be the reason entry
  fails."). The Forge's bite refusal without Nestor stays, for bites: two
  doors, two rules.
- **The Forge never imports willow-mcp or Grove.** Everything here is the
  fleet calling the Forge, or a Forge type the fleet imports.
- **The gate only narrows.** Effective access is willow-mcp's manifest
  intersected with the tier ceiling (willow-gate README, "embedders must not
  inherit that").
- **Observe before enforce.** Enforcement stays off until verdicts have been
  read on a registered seat.
- **A session deposits drafts.** No session verb seals, and no tier reports a
  draft as verified.
- **The flowchart is derived.** Rows live in the store; every host's wiring
  is generated from them, and a hand edit fails a pin (hooks proposal §0 and
  §6).
- **Growth before flowering.** Collection pools and local *x*→*y* joins carry
  routine work; cloud and fleet dispatch are for buds that pools cannot close,
  or acts the operator places above the flowering threshold (§1.5, §6 **0**).

## 9. Open

Settled rows are kept, struck: a question closed by an answer is evidence of
how it was answered. Rows carried over from the Forge paper keep their
answers.

| # | Question | State | Answer / waiting on |
|---|---|---|---|
| 1 | **Project identity.** A willow session's project is an explicit name or `<basename>-<path digest>` (`project_context`). The Forge engine's store is `forge-engine`, chosen by hand. A workshop derives its id from its repo name. `forge.bundle.cut` already writes `project_id` to `.forge/HEAD`. Proposed: the checkout declares its id in `.forge/project`, read at orient. The willow name keeps filing handoffs, and the id rides beside it. This also answers the v08 diamond. | in discussion | operator · **Tree:** trunk id + checkout; §1.5 |
| 2 | **Which SOIL.** | direction given | Operator, 2026-09-23: "~/.forge should be for the session, and then it gets promoted to the willow soil (or kb)". Proposed trigger: a human seal (§5). Open: SOIL vs KB. **Tree:** one soil; SOIL = living ground, KB = fruit; seal = promotion (§1.5). |
| 3 | ~~Where do next bites live?~~ | settled | Operator, 2026-09-23: "both, with a gap per bite and a pair only when a bite is decided." |
| 4 | ~~Does a next bite written by one seat surface to another seat on the same project?~~ | settled | Operator, 2026-09-23: yes. |
| 5 | **Which seat registers with the gate first?** It needs a regular session rhythm and a manifest narrow enough for a tier ceiling to mean something. | open | operator · **Tree:** trunk `willow` first (§1.5) |
| 6 | **Three gates.** willow-mcp's `_gate` (manifest, plus willow-gate's tier ceiling inside it), Ratatosk's `ratatosk.permission` (CONST-X-4), and Grove's turn gate. The turn gate is a different event, so it is not a duplicate. The first two are the same event in two hosts. Does Ratatosk take willow-gate's ceiling, or keep its own? | open | operator · **Tree:** one nutrient policy, two host renderers (§1.5) |
| 7 | **Does the Forge take a gate-bound `agent_id` as its `builder_id`?** It would give the Forge its first verified builder identity. It changes what the per-builder checkpoint store is keyed by, so existing stores need a mapping, not a rename. | open | operator · **Tree:** graft branch identity (§1.5) |
| 8 | **Where the durable binder session lives.** Beside the check-in nonces under `$WILLOW_HOME/gate/`, or in the session record `session_bind` already writes. | open | design, before step 4 |
| 9 | **Which host is canonical when they disagree?** The IDE harness has every event. Ratatosk is the fleet's own runtime. | open | operator · **Tree:** soil + ledger canonical; pin wiring (§1.5) |
| 10 | **Do willow-mcp's `human_required_*` verbs write through `forge.human_loop`?** | to verify | a read, before §5 is built on |

## Provenance

Measured 2026-09-23 by the vishwakarma seat; §1.5 and §6 **0** flowering gate
added 2026-09-24 from operator desk (tree metaphor, probes, Wave 0a–0c).
Read directly: willow-mcp
`pyproject.toml`, `dispatch.py` (`session_enter`, `session_handoff_write`,
`project_context`), the `server.py` `session_enter` wrapper,
`willow-gate-seam.md`, `stateless-session-state.md`, the willow-gate README
and header fields; the Forge's `forge/entry.py` and `forge.bundle.cut`; this
repo's `CLAUDE.md`, the hooks proposal, `fleet-wiring.md`, and
`willow-grove-premise.md`. Read by survey agents with file:line from disk:
`hooks/grove_hook.py`, `.claude/settings.json`, the sealed rows and
`wiring.json`; the drawio `willow-session-start`, `v04-full`,
`v08-toolchain-path` and `v11-verification-edge`; and Ratatosk (`crown.py`,
`seat.py`, `hooks.py`, `permission.py`, `capabilities.py`, `daemon.py`,
`tools.py`, `grove.py`). The operator's words are verbatim.

*ΔΣ=42*
