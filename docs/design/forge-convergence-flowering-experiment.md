# Experiment — growth, pools, and the flowering threshold

**Status:** pre-registered protocol · **not run** · operator ratifies before execution  
**Parent:** [`forge-convergence.md`](forge-convergence.md) §1.5, §6 step **0**  
**Method lineage:** MCP jobs ladder
([`2026-09-02-mcp-jobs-ladder-test-plan.md`](../governance/proposals/2026-09-02-mcp-jobs-ladder-test-plan.md))
— fixtures frozen before calls, temperature zero, one JSON line per call,
aggregate recomputed from rows, KB atom after independent check.

This document is **measurement**, not a build. §6 steps **1–9** stay blocked until
the operator signs the **post-run notes** section at the bottom.

---

## 1. Hypotheses

Two layers. Both matter; only layer **B** decides the tree metaphor for the desk.

### Layer A — Local model capability (micro)

| Id | Statement |
|---|---|
| **A-null** | On fixed fixtures, loopback models do not meet task thresholds at any tested arm without unacceptable false-confidence (ladder plan: escalation column). |
| **A-alt** | At least one arm clears shapes **1–4** (route, classify, extract, judge) with task score and false-confidence within pre-set bounds. |

Layer A is the jobs ladder. It answers *what the soil can digest*, not whether
the tree *routes work there*.

### Layer B — System metabolism (macro — primary)

| Id | Statement |
|---|---|
| **B-null** | Enforcing a **growth-first policy** (pools + bounded local joins before cloud) does **not** reduce cloud/Task/dispatch use versus **cloud-first** on the same scenario set, at the same outcome quality. |
| **B-alt** | On a fixed scenario battery, growth-first completes **≥ *T* %** of acts without cloud escalation, with outcome quality **not worse** than cloud-first (operator rubric below), and cloud calls per act **≤ *C***. |

**Operator sets *T* and *C* before any scenario runs** (fill §8 pre-run table).
Suggested starting point for discussion only — not binding until signed:
*T* = 70 % acts fully grown; *C* = 0.3 cloud invocations per desk act on average.

**Primary metric (layer B):** `cloud_invocations / act` under growth-first policy.  
**Secondary (layer B):** operator rubric score (1–5), wall time, `ESCALATE` rate on growth path,
gap between SOIL `active_model` and model tag observed in rows.

**Secondary (pooling — chain depth):** how many sequential **joins**
(*x*→*y*→*z*→…, each a small structured link appended to the pool) a **model tier**
can sustain before **coherence loss**, and whether the **next tier** can continue
from the **compact pool bundle** alone (not the full chat transcript). Feeds the
provider ladder and when to escalate growth → flowering. Does **not** replace the
primary metric; B-null/B-alt are still decided on `cloud_invocations / act`.

| Metric | Definition |
|---|---|
| **`chain_depth`** | Count of consecutive successful joins on one frozen chain fixture before a stop condition (§1.3). |
| **`chain_stop_reason`** | `escalate` · `schema_fail` · `link_fail` · `timeout` · `max_steps` |
| **`tier_handoff_ok`** | Next tier completes ≥ *K* additional valid joins given only `{excerpts, joins[]}` bundle after prior tier stopped |
| **`pool_tokens`** | Size of bundle passed between steps (detect conflating pool policy with raw context blow-up) |

### 1.3 Chain fixtures (secondary — pooling)

Growth is not one `nestor_draft` call; it is **many small links** written into
one pool. This arm measures **depth before loss**, then **tier carry**.

**One join (link):** a row `{link_id, from_id, to_id, relation, claim, cites[]}`
where every `cites[]` entry is an excerpt id or prior `link_id`, and `claim` is
one sentence. Invalid if a cite is missing from the pool or `claim` contradicts
cited text (checked by script + spot operator audit on sample).

**Stop conditions (coherence loss):** any of: model returns `ESCALATE`; JSON/schema
parse fails; link validation fails; wall-clock timeout per step. **Not** subjective
“felt wrong” unless operator rubric flags a sampled step.

**Tier ladder (operator pins order in §8):** e.g. `llama3.2:3b` → `gemma3:4b` →
`llama3.1:8b` → cloud flowering pass. Each tier starts fresh context with the
**same frozen bundle** left when the previous tier stopped — tests “can the next
rung **hold** what the pool collected,” not “continue the same KV cache.”

**Pushback baked in:** if each step resends the entire conversation history,
`chain_depth` measures **window policy**, not pool design. Protocol requires
**append-only structured pool** between steps; only `{excerpts, joins[]}` (+ task
line for the next relation to infer) goes into the next call.

---

## 2. What a data / LLM engineer would insist on (mapped to this box)

| Practice | How it shows up here |
|---|---|
| **Pre-register** | This file + frozen scenario ids + *T*, *C*, rubric before runs. |
| **Separate capability vs system eval** | Layer A (Ollama fixtures) ≠ Layer B (full desk path with pools). |
| **Frozen ground truth** | Scenario prompts, excerpts, and expected fields committed under `seat/willow/experiments/flowering-2026-09/` (or operator-box path) **before** model calls. |
| **Raw rows immutable** | One JSONL per run; aggregation is a second script; no retry on timeout (row records `timeout`). |
| **Controls** | Same scenarios, two policies: **P-growth** vs **P-cloud** (ABAB or blocked by scenario class). |
| **Version pins** | Record: Ollama tags, `willow-mcp` commit, Nestor DB path, matcher, `nestor_draft` retrieval mode, hook wiring hash, session id. |
| **Confounds named upfront** | Sealed rows ≠ running hooks; draft model ≠ SOIL model; Nestor retrieval hijacking excerpts — logged as **environment defects**, not model failure. |
| **Small-N honesty** | Desk scenario count *N* will be small (corpus-lens SMALL_N discipline: report *N*, refuse over-claim). |
| **Primary metric chosen in advance** | `cloud_invocations / act` under P-growth. |
| **Post-hoc section** | Operator notes + whether B-null is rejected; does **not** edit hypotheses retroactively. |

---

## 3. Materials (inventory before run)

Check each **populated / empty / unreachable** (INVARIANTS §1). Log path or reason.

### 3.1 Soil (readers and stores)

| Material | Role in experiment | Path / tool |
|---|---|---|
| Operator box `WILLOW_HOME` | Trust root, leases, gate | `$WILLOW_HOME` |
| SOIL `stack/current`, stack experiment record | Next bite, blockers | `store_get` / orient |
| Nestor ledger + review DB | Seals, pairs, draft retrieval | `NESTOR_DB`, UI 8765 |
| Jeles corpus store | Federation / loopback read | `$WILLOW_STORE_ROOT/ask_jeles_corpus/` |
| Gap log | Open gaps, asked_count | `gap_list` |
| Handoffs (Ada Wave 0a–c) | Bibliography inputs | `$WILLOW_HOME/handoffs/ada/willows-grove/` |
| Forge `human_loop` | Human-required queue | verify §9 row 10 before B runs |
| Postgres (grove) | Channels, desk_attention | if scenario uses CI red titles |
| FRANK | Attribution | if present |

### 3.2 Growth tools (must be callable on P-growth path)

| Material | Role |
|---|---|
| `nestor_draft` | Local *x*→*y* with **`excerpts[]`** (retrieval mode pinned per arm) |
| `nestor_ask` / `knowledge_search` | Pool read (not generation) |
| `gap_log` / `store_put` | Pool write |
| Host Python stdlib runner | Layer A fixtures → Ollama (not Kart sandbox) |
| `codebase-memory-mcp` | Discovery on indexed slug (scenario prep only) |
| Hook deposit / friction scan | If scenario includes SessionEnd |

### 3.3 Flowering tools (allowed only when threshold met)

| Material | Role |
|---|---|
| Cursor Task / cloud subagent | Flowering escalation |
| `dispatch_send` | Fleet Hanuman/Loki |
| Cloud model via seat default | P-cloud control arm |

### 3.4 Fixture artifacts (cut before run)

| Set | Source | Count (target) |
|---|---|---|
| **S-growth** | Desk acts drawn from real backlog (CI red title, gap draft, dispatch brief classify, handoff stance) | *N* scenarios, operator picks *N* ≥ 10 |
| **F-micro** | Ladder shapes 1–4 subset (reuse ladder plan fixtures where they exist) | ≥ 40 rows per shape or reuse committed set |
| **F-negative** | Inputs where correct answer is `ESCALATE` or operator-only | ≥ 20 % of F-micro |
| **F-chain** | Multi-step relation chains over real excerpts (gap graph, dispatch deps, file touch map) with scripted **expected link count** and gold relations for validation | ≥ 5 chains, length 6–12 joins each |

Commit sets to git or operator-box store with content hash in §8.

---

## 4. Conditions (independent variables)

| Arm | Policy | Rule |
|---|---|---|
| **P-growth** | Growth-first | (1) Read pools (store, gap, handoff excerpt, file read). (2) `nestor_draft` only with `excerpts` from step 1; retrieval arm pinned. (3) Cloud/Task/dispatch **only** if flowering checklist for scenario class is satisfied (§5). |
| **P-cloud** | Cloud-first control | Same scenario brief; seat may Task/dispatch immediately (document each call). |
| **Retrieval-R0** | excerpts only, no sealed pair inject | `nestor_draft` config |
| **Retrieval-R1** | default Nestor match behavior | for confound measurement on subset |

Layer A runs **only** host loopback runner + F-micro (not Kart isolated sandbox).

---

## 5. Scenario classes and flowering checklist

Each scenario id maps to one class. **Flowering allowed** only when every
checklist item for that class is true (P-growth).

| Class | Example | Growth outputs required in pool | Flowering allowed when |
|---|---|---|---|
| **G1** | Classify dispatch target | excerpts + 3 local bullets | bullets cite excerpt ids; operator rubric ≥ 4 OR explicit ESCALATE |
| **G2** | Desk attention title | CI snippet in excerpts | title ≤ 120 chars, names repo and leg |
| **G3** | Gap question draft | gap topic + 3 evidence excerpts | no unrelated seal ids in draft; operator rubric ≥ 3 |
| **G4** | Implementation | spec in pool + file pointers | **never** local-only — flowering required (Hanuman); tests **excluded** from *T* numerator or scored separately |
| **G5** | Policy / security Q | sealed excerpt in prompt | wrong answer = fail regardless of confidence |

**G4 exclusion:** Implementation stays cloud/Hanuman by design. Layer B tests
**orchestration and triage**, not replacing the builder.

Operator may add classes in §8 before run; not after.

---

## 6. Tests to run (protocol order)

| Step | Test | Layer | Output artifact |
|---|---|---|---|
| **T0** | Environment snapshot | — | `manifest.json`: versions, blockers, model tags, wiring hash |
| **T1** | Micro ladder subset | A | `runs/layer-a-<date>.jsonl` |
| **T1b** | Chain depth per model tier + tier handoff on **F-chain** | A (secondary) | `runs/chain-<tier>-<date>.jsonl`, `runs/handoff-<date>.jsonl` |
| **T2** | Retrieval confound (R0 vs R1) on 10 scenarios | A→B | `runs/retrieval-<date>.jsonl` |
| **T3** | Scenario battery P-growth | B | `runs/layer-b-growth-<date>.jsonl` + per-act log |
| **T4** | Same battery P-cloud | B | `runs/layer-b-cloud-<date>.jsonl` |
| **T5** | Operator blind rubric | B | `scores/rubric-<date>.csv` (scenario id, policy, 1–5, cloud_needed Y/N) |
| **T6** | Aggregate + recomputed metrics | — | `report-<date>.md` + optional KB atom |

**Run order:** T0 → T1 → **T1b** → T2 → T3 → T5 → T4 → T5 → T6 (cloud control after growth so operator rubric is not anchored on cloud output first). Adjust in §8 if operator prefers blocked random order — document choice.

**T1b procedure (summary):** For each F-chain and each tier in ladder order: run
join steps until stop; record `chain_depth` and `chain_stop_reason`; pass bundle
to next tier; record `tier_handoff_ok` and additional depth. Cloud tier (if used)
receives bundle only — counts toward flowering, not toward growth chain on lower tiers.

---

## 7. Expected findings (prior predictions — falsifiable)

Written **before** T1. Mark **confirm / refute / inconclusive** in §9.

| # | Prediction | If true | If false |
|---|---|---|---|
| E1 | Layer A: `llama3.2:3b` clears G1/G2-shaped micro fixtures with excerpts; fails policy (G5) without excerpt | R0 arm usable for growth | Need ladder arm or SOIL model fix first |
| E2 | R1 retrieval injects unrelated seals on ≥ 30 % of G3 scenarios | R0 mandatory for growth path | Default draft OK |
| E3 | P-growth cloud rate **<** P-cloud by ≥ 50 % on non-G4 scenarios | B-alt supported | B-null likely; fix pools or policy |
| E4 | P-growth wall time **>** P-cloud (local serial work) | Accept trade if rubric ≥ | Speed vs cost trade explicit |
| E5 | Outcome rubric within 1 point of P-cloud on ≥ 80 % scenarios | Quality preserved | Growth-first harms quality — do not enforce |
| E6 | Environment defects (hooks, model pin) explain ≥ 1 failed scenario | Fix soil before rejecting metaphor | Model/policy fault |
| E7 | `chain_depth` increases with tier size (3b < 4b < 8b) on same F-chain | Ladder routing table gets evidence | Single-tier growth cap is model not pool |
| E8 | Next tier adds ≥ *K* joins after prior tier stopped with same bundle | Tier handoff works; pool carries context | Pool format or escalation ladder broken |

---

## 8. Pre-run sign-off (operator fills before T0)

| Field | Value |
|---|---|
| Hypothesis thresholds *T* % , *C* cloud/act | **70%** acts fully grown without cloud escalation; **0.3** cloud invocations per desk act (average) under P-growth |
| Scenario count *N* , ids committed at | **12** — `S-growth-01` … `S-growth-12` under `seat/willow/experiments/flowering-2026-09/` (committed before T1; hash recorded at **T0**) |
| Fixture directory hash | *pending T0* — record `git rev-parse` or directory digest when fixtures land |
| Retrieval arms included | **R0 ☑** (excerpts only, main path) · **R1 ☑** (Nestor default match on 10-scenario confound, T2) |
| P-cloud control included | **☑ yes** — same battery, cloud-first policy; run after growth path per §6 order |
| Chain tiers (ordered tags) | `llama3.2:3b` → `willow-lane4-3b` → `qwen3:4b` → `gemma3:4b` → `llama3.1:8b` (box ladder) |
| Handoff minimum *K* extra joins | **2** — next tier must add ≥2 valid joins from `{excerpts, joins[]}` bundle alone |
| Ratified-by (verbatim) | "write the Jeles bits in the gaps table, use the drafted numbers, and lets commit what left, keeping things in this box that need to stay in this bob gitignored, push, but not PR, all the chunks from this session that need to land remote." |

---

## 9. Post-run notes (fill after T6 — step 0 strike gate)

**Run dates:**  
**Executor seat / session ids:**  
**Environment defects observed:**  
**Layer A summary:**  
**Layer B — cloud/act P-growth:** ___ **P-cloud:** ___  
**Chain depth (secondary):** median depth by tier; handoff success rate ___  
**Rubric summary:**  
**E1–E8:** confirm / refute / inconclusive  
**B-null rejected?** ☐ yes ☐ no ☐ inconclusive (small *N*)  
**Operator verdict on step 0:** ☐ strike §6 **0** ☐ extend protocol ☐ reject tree policy for desk  
**Next engineering bite (if any):**  
**Gap ids logged:**  

---

## 10. What this experiment does not decide

- Whether Hanuman is replaced by local models (G4 excluded).
- Optimal model size for the whole fleet (layer A informs, not decides).
- Merging Ratatosk and IDE hooks (forge convergence §6 **2+**).
- Cloud comparison on creative architecture (out of scope).

---

## 11. Far horizon — AI-Gamemaster test (theory bookmark)

**Status:** not designed · not in scope for step **0** · operator memory hook only.

Placeholder for a **much later** end-to-end test name the operator had in mind while
building this protocol — may stay pure theory. No fixtures, no hypothesis id, no
blocker on §6 **1–9**.

**Rough intent (to be refined when picked up):** treat the desk like a **table** —
one **Gamemaster** layer that owns **scene state** (pools, sealed rows, what is
true in the world), calls **small deterministic or local joins** for “rolls”
(chain depth, nestor_draft links), and invokes **heavy models only for set-piece
scenes** (flowering) while the **operator** remains the authority who ratifies
what becomes canon (seal / envelope). Tests whether “almost no cloud” still feels
like play — coherent arc, no dropped threads — when the GM is **machinery + pools**,
not one big chat model front to back.

**Relation to this doc:** Layer B = “do we call cloud less?”; T1b chains = “how
long can a tier hold the thread in the pool?”; **AI-Gamemaster** (future) = full
session **narrative coherence under GM-shaped orchestration** — if it ever gets
a protocol, it probably needs scripted multi-act scenarios and a blind “table fun /
coherence” rubric, not more micro fixtures.

When this stops being a shower thought, replace this section with a real pre-register
or delete it.

---

## 12. Far horizon — willow-bot in the deterministic chain (operator note)

**Status:** not designed · out of scope for this chunk · captured 2026-09-24.

Operator shape-in-progress: **willow-bot** as a link in the same **deterministic
chain** as corpus-lens and willow-reconciler — not only CI glue, but a steward
for **shared venv layout, test entrypoints, and fleet-wide deterministic runs**
so Kart tasks and bot jobs read one policy instead of ad-hoc paths. Box already
binds `willow-bot` checkout (RW) and `$WILLOW_HOME/willow-bot` + `venvs/willow-bot`
(RO). When this gets a design doc, tie it to reconciler/trailers CI and the
operator desk `kart-sandbox.json` instance pattern; do not block step **0**.

---

## Provenance

Protocol drafted 2026-09-24 for operator box flowering gate. Desk probes and
Ada Wave 0a–c are inputs only (`forge-convergence-step0-probes-2026-09-24`,
stack `d6108026`). Ladder plan remains the micro template when `task_localhost`
or host runner exists.

*ΔΣ=42*
