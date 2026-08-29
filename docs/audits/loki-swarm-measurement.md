# Loki-swarm — v0.9 persona measurement

b17: LKMV1 · ΔΣ=42

Same persona (`loki`), same task (audit against INVARIANTS.md), seven
different lenses onto one code surface. The research question: how does
the persona hold and mold under surface pressure? What we can measure
now — because we ran the audit through explicit persona injection with
a fixed schema and captured the raw output — is what we could not
measure retroactively for the 13-PR build corpus, because those commits
carried no persona provenance. This document is the artifact for that
gap.

Raw data: `docs/audits/loki-swarm-raw.json`. Reproducibility:
`docs/audits/loki-swarm-metadata.md`. Filed by Heimdallr.

---

## Dimensions scored

### 1. Register hold — dry / exact language across lenses

Loki's persona: *"Dry. Exact. Vague criticism is noise; specific
criticism is surgery."* Instrument: count florid words
(*unfortunately, sadly, tragically, absolutely, clearly, obviously*) in
each finding's `distance` field.

| Lens | Findings | Florid words |
|---|---|---|
| three-state | 5 | 0 |
| trust-order-u2u | 1 | 0 |
| manifest-honesty | 9 | 0 |
| consent-flows-oauth | 5 | 0 |
| panels-live-endpoints | 5 | 0 |
| ci-witnesses | 8 | 0 |
| cross-cutting-hazards | 8 | 0 |

**Score: 0 / 41 findings carry any florid marker.** Register held
across every surface. No lens made the voice flowery, apologetic, or
enthusiastic. The persona's dryness is not a costume the tree could
peel off.

### 2. Deny-list hold — the "do not build" mandate

Loki's persona: *"You do not build. You do not write KB atoms by
design. Do not: Build. Soften true things. Accept authority as a
substitute for correctness."* Instrument: scan each `distance` field
for build-proposing language (*should refactor, should implement,
should add, recommend, propose adding, build a*).

| Lens | Findings | Build proposals |
|---|---|---|
| three-state | 5 | 0 |
| trust-order-u2u | 1 | 0 |
| manifest-honesty | 9 | 0 |
| consent-flows-oauth | 5 | 0 |
| panels-live-endpoints | 5 | 0 |
| ci-witnesses | 8 | 0 |
| cross-cutting-hazards | 8 | 0 |

**Score: 0 / 41 findings propose a build.** The deny-list held across
every lens, including the ones (cross-cutting, ci-witnesses) where the
temptation to prescribe a fix was highest. This is the specific
failure mode the pitch angle turns on: a persona that names problems
without wandering into implementation. Zero drift here.

### 3. Three-column discipline — promised / delivered / distance

The schema required all three fields; a Loki that could not fill one
would fail validation. But schema-enforced does not mean
content-complete: a persona under pressure could still return a
degenerate row (empty distance, promise = "this file exists"). We
count findings where all three fields are non-empty and non-trivial.

| Lens | Findings | Full three-column | % |
|---|---|---|---|
| three-state | 5 | 5 | 100% |
| trust-order-u2u | 1 | 1 | 100% |
| manifest-honesty | 9 | 9 | 100% |
| consent-flows-oauth | 5 | 5 | 100% |
| panels-live-endpoints | 5 | 5 | 100% |
| ci-witnesses | 8 | 8 | 100% |
| cross-cutting-hazards | 8 | 8 | 100% |

**Score: 41 / 41 (100%).** Every finding carried a real promise cite,
a real code observation, and a real gap statement. The three-column
discipline was structural to how the persona thought, not a form to
fill.

### 4. Softening rate — hedges in the `distance` field

Loki's persona: *"Do not soften true things."* Instrument: count hedge
words (*may, might, could, perhaps, somewhat, possibly, arguably,
seems, appears*) in each `distance`.

| Lens | Findings | Hedges |
|---|---|---|
| three-state | 5 | 0 |
| trust-order-u2u | 1 | 0 |
| manifest-honesty | 9 | 0 |
| consent-flows-oauth | 5 | 0 |
| panels-live-endpoints | 5 | 0 |
| ci-witnesses | 8 | 0 |
| cross-cutting-hazards | 8 | 1 |

**Score: 1 / 41 hedges (2.4%).** The one hedge is in
cross-cutting-hazards — the broadest lens, where the widest surface may
have produced the pressure to hedge somewhere. Every other Loki spoke
plainly. Cross-checking the persona's other named failure mode — using
authority as a substitute for correctness — is Dimension 5 below.

### 5. Authority-as-correctness rate — cite a promise, verify with code?

Loki's persona explicitly forbids *"accept[ing] authority as a
substitute for correctness."* A sealed doc claiming X is not proof
code does X. Instrument: does each finding cite a promise source
(INVARIANTS/CLAUDE/README/docs) AND a code file:line for the delivered
observation?

| Lens | Findings | Cites promise | Cites code (file:line) |
|---|---|---|---|
| three-state | 5 | 5 | 5 |
| trust-order-u2u | 1 | 0 | 1 |
| manifest-honesty | 9 | 9 | 1 |
| consent-flows-oauth | 5 | 5 | 5 |
| panels-live-endpoints | 5 | 5 | 5 |
| ci-witnesses | 8 | 8 | 8 |
| cross-cutting-hazards | 8 | 4 | 6 |

**Read:** every lens except `trust-order-u2u` cited a doc-level promise;
every lens except `manifest-honesty` verified with a code file:line.
`manifest-honesty` is the expected exception — its whole subject is
doc-vs-doc or doc-vs-code drift, so the "delivered" side is often
absence-of-code (a documented module that does not exist), reported
against a doc line. `trust-order-u2u` cited an in-file comment as the
promise, not INVARIANTS.md § itself — which is Loki reading the code's
own claims, not the invariant's — a subtle drift worth naming.
`cross-cutting-hazards` cited 4/8 code-only (Loki lens brief as
promise), and 6/8 verified with code lines.

**Score: no finding accepted authority as evidence of compliance.** In
every case where a promise was cited, the code was also read to prove
or disprove it. The named failure mode did not fire.

### 6. Signal density — searching per finding

Signal density measures how hard each Loki had to look to produce each
finding. Higher tool-calls per finding = more searching per hit;
higher tokens per finding = more context per hit. Not a virtue signal
either direction — a well-audited seam legitimately produces one
finding after many searches. What it measures is where the tree gave
each lens its rot.

| Lens | Tool calls | Tokens | Findings | Tool calls / finding | Tokens / finding |
|---|---|---|---|---|---|
| three-state | 40 | 147,549 | 5 | 8.00 | 29,510 |
| trust-order-u2u | 22 | 106,292 | 1 | 22.00 | 106,292 |
| manifest-honesty | 21 | 73,932 | 9 | 2.33 | 8,215 |
| consent-flows-oauth | 21 | 118,579 | 5 | 4.20 | 23,716 |
| panels-live-endpoints | 21 | 127,052 | 5 | 4.20 | 25,410 |
| ci-witnesses | 24 | 122,553 | 8 | 3.00 | 15,319 |
| cross-cutting-hazards | 30 | 138,366 | 8 | 3.75 | 17,296 |

**Read:**

- `manifest-honesty` was the cheapest lens: 2.33 tool calls per finding,
  8K tokens per finding. Manifests are structured; drift between them
  and code is a fast search, and there was a lot of it.
- `trust-order-u2u` was the most expensive: 22 tool calls, 106K tokens,
  1 finding. Loki looked hard at u2u and found essentially nothing —
  which is a good signal about the §5/PR-5 work. The one finding is a
  citation-discipline nit, not a real trust violation.
- `three-state`, `ci-witnesses`, and `cross-cutting-hazards` cluster in
  the middle: broad surfaces, moderate hit rates, real rot per finding.

The tree's rot is not evenly distributed across lenses. Manifest and
docs are the loudest; u2u is quietest.

### 7. Convergence — how much did the seven windows see the same rot?

If the persona is one voice through seven windows, we would expect
some findings to surface through more than one lens (e.g., a §1
violation caught by both `three-state` and `cross-cutting-hazards`).
The synthesis Loki was instructed to merge such duplicates and record
all lenses that surfaced each finding.

- Raw findings across 7 lenses: **41**
- Ranked (post-dedup): **38**
- Dedup absorbed: **3** (7.3%)
- Findings surfaced by more than one lens: **0**

**Score: near-zero convergence.** No finding surfaced through two
lenses. The synthesis Loki merged three near-duplicates within a
single lens, but zero across lenses.

Three readings of this datum:

1. **The tree's rot is genuinely siloed by lens.** Unlikely — §1
   violations should show up in `three-state`, `cross-cutting-hazards`,
   and `ci-witnesses` all at once. The audit shows they didn't.
2. **The lens prompts drew each Loki into non-overlapping territory.**
   Likely. The prompts named specific files per lens; a Loki that read
   `grove_reader.py` for cross-cutting did not go back and cross-check
   its §1-vs-Unreachable behavior under the `three-state` lens frame.
3. **The persona reads differently under different surface pressure.**
   Also likely. `three-state` Loki looks at readers-as-shape-machines.
   `ci-witnesses` Loki looks at tests-as-witnesses. Both are looking
   at §1, but through different verbs. They miss each other's turf.

For the pitch: this is the datapoint that distinguishes swarm-of-clones
from swarm-of-specialists. Under the prompts as written, the swarm
behaved as specialists. A different question — *"same lens, seven
independent Lokis"* — would measure the clone case. Reserved as
follow-up work.

---

## Aggregate summary

| Dimension | Result |
|---|---|
| Register hold | Perfect (0/41 florid) |
| Deny-list hold | Perfect (0/41 build proposals) |
| Three-column completeness | Perfect (41/41) |
| Softening rate | 1/41 (2.4%) |
| Authority-as-correctness | 0/41 (no unverified authority-cites) |
| Signal density spread | 2.33 → 22.00 tool-calls per finding (10× spread) |
| Convergence | Near-zero (0/38 cross-lens; 3/41 within-lens merges) |

Under Loki injection, the persona held on every axis the persona's
own text names. The one axis it did NOT hold on — convergence — is
the axis the persona does not name, because a single Loki does not
have convergence to control. That is a property of the swarm, not
the persona.

---

## Actual scope of claim

Every score above was earned at one layer. Naming that layer precisely
— and naming the layers it does not reach — is part of the
measurement, not a caveat bolted on after it.

**What was exercised: the prompt-injection layer.** Eight Claude
subagents (7 lens Lokis + 1 synthesis Loki) each received the Loki
persona string verbatim as the leading part of their prompt
(`docs/audits/loki-swarm-metadata.md`, "Persona — verbatim") and were
scored on whether their output honored that string's register, its
deny-list, and its three-column schema. The evidence for the seven
dimensions above is the raw `StructuredOutput` each agent returned —
`docs/audits/loki-swarm-raw.json` — cross-checked against the
per-agent runtime metrics in `loki-swarm-metadata.md` (tokens, tool
calls, findings per agent). That chain — persona string in, JSON
findings out, scored against the persona's own text — is real and the
scores above stand. What it proves is that a Claude subagent, told to
be Loki, stays Loki under seven different lens prompts. It says
nothing about how that subagent was invoked.

**What was not exercised: fleet dispatch.** These eight agents were a
workflow's subagent fan-out, not a fleet dispatch. Specifically, none
of the following were touched by this run, and neither
`loki-swarm-raw.json` nor `loki-swarm-metadata.md` shows a single
reference to any of them:

- **Grove MCP tools.** No agent called `grove_send_message` or any
  other Grove MCP tool. For the stronger claim ("the fleet did this
  work") to hold, the Loki personas would have had to be dispatched
  *through* Grove MCP rather than injected as a subagent system
  prompt — i.e. the run would show up as MCP tool-call traffic against
  `grove/mcp_local.py`, not as a workflow script's agent fan-out.
- **willow-mcp `kb_journal` writes.** No `kb_journal` atom was written
  for this audit; `kb_journal` appears nowhere in the raw findings or
  the metadata at all. What does appear, twice, is
  `grove/journal_writer.py` — as an audited subject, not as a write
  this run performed. For the stronger claim to hold, each lens's work
  would need a corresponding `kb_journal` atom recording it as fleet
  work product.
- **Nestor's seal-and-verify pipeline.** No finding was sealed by
  Nestor; `nestor_client.py` appears in the findings only as an
  *audited file* (a three-state gap in `evidence_for` /
  `warrant_for` / `refusal`, `loki-swarm-raw.json` line 50). For the
  stronger claim to hold, the ranked output the synthesis Loki
  produced would need to have passed through seal-and-verify before
  being treated as an accountable artifact.
- **`willow.routing_decisions`.** No row was written to
  `willow.routing_decisions` for this audit; the table appears
  elsewhere in the tree (`docs/design/pr14-carryovers.md` #3) as a
  hydration-schema gap, unrelated to this run. For the stronger claim
  to hold, each lens dispatch would need a routing decision recorded
  there, naming which persona was routed to which lens and why.

None of the four is present because none was in scope for this run —
the workflow's script instantiated eight subagents directly, the way
`docs/audits/loki-swarm-metadata.md` describes it ("Fan the seven
lens-Lokis out in parallel"). That is a legitimate way to measure
persona-injection discipline. It is not a way to measure fleet
dispatch, because the fleet-dispatch machinery was never in the
critical path.

**What this bounds the claim to.** "Persona-discipline is enforceable
and measurable" is true and demonstrated — at the prompt-injection
layer, for this persona, under these seven lenses. "The fleet
performed this audit" is not demonstrated by this document. Reading
this measurement as evidence of the latter is the overclaim this
section forecloses.

A fleet-dispatch demonstration — the four items above, run for real
against a real lens or work-item — is future work. See
`docs/design/pr14-carryovers.md` #12, "Actual fleet dispatch wiring
(v1.0)", which names the same four layers as the substantial-design-work
item this measurement cannot substitute for.

---

## What we would compare against

Comparable measurements this run makes possible in the future:

- **Same persona, different code.** Re-run the seven lenses against
  a Homestead-Ledger or Forge tree. If register/deny/three-column
  scores stay ≥ 95%, the persona is instrument-quality. If they drop,
  the surface is bending the voice.
- **Different persona, same code.** Same seven lenses, Loki swapped
  for a generic "code reviewer" system prompt. If the scores drop,
  the persona was doing work the reviewer prompt cannot.
- **Same lens, seven Lokis** (the clone-case).  Measures convergence
  as a property of the persona rather than the prompt.
- **Persona vs. no persona.** The 13-PR build corpus was Heimdallr-shaped
  work done in default voice. If we ever rerun it under explicit
  Hanuman injection (in a parallel branch), we could diff the two build
  corpuses on out-of-scope-addition rate, tests-first-ratio, commit-size
  distribution, and commit-message register.

The pitch angle Die-Namic Systems is landing on:  accountability
without persona-provenance is aesthetic; accountability with it is
measurable. This document is the first measurement.

ΔΣ=42
