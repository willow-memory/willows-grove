# Proposal — one local-inference seam, three consumers

**Status:** proposed · drafted by willow 2026-09-02 · **cross-repo: Nestor (runtime), Jeles, Forge, willow-mcp (consumers)** · root ratifies scope, each repo ratifies its own landing
**Build order:** 5 of 6 — see [`2026-09-02-build-order.md`](2026-09-02-build-order.md)
**Companion:** [`2026-09-02-packet-lifecycle-adr.md`](2026-09-02-packet-lifecycle-adr.md) — a local-model specialist is only safe once verify opens the evidence.
**Design sources:** [`willow-mcp/docs/design/complete-system-packet-2026-07-08.md`](../../../willow-mcp/docs/design/complete-system-packet-2026-07-08.md) (Loki and Ada on local 3B); Forge D7 (`safe-app-store-public/docs/design/the-forge.md:315`); willow-2.0 harnesses, issue 703 (archived, not on this box); Jeles `nugget_draft.py` and `source_trail.py` docstrings, measured 2026-08-28.
**Prior art:** [`willow-mcp/docs/PRIOR_ART.md`](../../../willow-mcp/docs/PRIOR_ART.md) §9 (model egress consent: **Keep**), §7 (agent roles: **Keep**).

---

## The finding

Measured 2026-09-02 across the indexed trees. Four repos each answer "is
the model on this machine" and then stop before the model.

| Repo | Loopback check | Ollama client | Harness | What runs today |
|---|---|---|---|---|
| willow-mcp | `model_egress.is_local_host` | `nest/llm.py` (classify, describe) | none | nest intake only |
| Forge | vendored copy of the above, in `model_egress.py` | none, stubbed | none | the D7 gate, deciding for a call that does not exist |
| Nestor | `OllamaEngine._loopback_host` and `ollama_embed.host` | `OllamaEngine._chat`, `ollama_embed` | `task_prompt` + `TaskDraft` + `DraftProvenance` | translation drafts, embeddings, bounded task drafts |
| Jeles | none, no model dependency by design | none | none | five injected callables, never supplied by any host |

Jeles's five seams (`nugget_draft.draft(respond=…)`,
`source_trail.verify_claim(judge=…)`, `gap_triage.triage(judge=…)`,
`verify.verify_claims(llm_respond=…)`, `sources.question_to_intent(respond=…)`)
carry the strongest rules in the fleet: the model may phrase but may not
source; the judge may demote but never promote; an outage reads as
`unjudged`, not as `no`. None has run against a real local model outside a
test. The 2026-08-28 measurement of eight local models was models as MCP
*clients* calling Jeles, not Jeles calling a model.

Forge's D7 says local first, cloud only by declared permission. The route
module is built and tested. The model call it gates is stubbed; the
checkpoint responder is scripted.

willow-mcp marks Loki and Ada `model_hint: local-3b` in
`specialists.json`. `registry.get_specialist` copies the field into a dict.
Nothing reads it. The orchestrator routing skill sends draft-only work to
`nestor_draft`, which this seat's Nestor server withholds because its engine
is offline, not Ollama.

Nestor's engine is the one complete seam. `OllamaEngine` refuses any
non-loopback host at construction, bounds task and output size, resolves
the installed tag, runs at temperature zero with a fixed `num_predict`, and
returns a `TaskDraft` whose `DraftProvenance` records prompt hash, input
hash, endpoint scope, temperature, and the ids of every sealed pair fed as
context. A `Draft` has no field it could mark verified with.

The willow-2.0 harnesses (issue 703) were the contract that made a local
model safe to hand a chore: a task contract as system prompt, a JSON schema
for Ollama structured output, few-shot anchors, and a ranked failure-mode
list. The repo is archived. No live tree carries them (kartikeya checked,
zero hits).

## Decision

One runtime, one contract, three consumers. No new Ollama client anywhere.

### The runtime is Nestor's engine

`nestor.engine.OllamaEngine` becomes the fleet's local-inference runtime.
It already enforces the three things every consumer needs and none should
re-derive: loopback only with no silent cloud fallback, bounded input and
output, and provenance with no authority-shaped field. Consumers import it
or call it over Nestor's MCP surface; they do not vendor it.

Two additions to Nestor, both small:

1. **Structured output.** `draft_task` gains an optional `schema` argument
   passed through as Ollama's `format`. The harness contract needs it; the
   fleet's own measurement (echo ladder, KB 63858998) says gate the input,
   not the output, and a schema at the front is the cheapest gate there is.
2. **A callable adapter.** `engine.as_respond(engine) -> Callable[[system,
   history, user], str]`, the exact signature Jeles's five seams take. One
   function, so a host wires Jeles in one line and the provenance still
   lands.

### The contract is a harness

Re-land the 703 harness shape as a directory convention, owned by whichever
repo runs the chore:

```
harnesses/<name>/
├── contract.md        # the system prompt: task, bounds, refusal wording
├── schema.json        # Ollama structured-output schema for the reply
├── fewshot.json       # anchors, each with the expected structured reply
└── failure_modes.md   # ranked; what the model gets wrong and how it shows
```

A harness is loaded by `nestor.engine.load_harness(path)` and produces the
`system` and `schema` for `draft_task`. `tests/test_harness_integrity.py`
from 703 comes with it: every harness has all four files, every few-shot
reply validates against the schema, and the contract names its refusal
token. Provenance records the harness name and the contract's hash.

Harnesses are not law. They live in the repo that runs them, under ordinary
review. What they may not do is grant: a harness cannot name a tool, a
path, or a permission the calling seat does not already hold.

### Consumer one: Jeles

Jeles stays dependency-free. The host that runs it supplies
`as_respond(OllamaEngine(...))` to the five seams. The first host is
willow-mcp's federation lane: `federation_call` to the Jeles corpus server
gains an optional `judge` on `corpus_verify_claim`, wired from the willow
seat's own engine, so the relevance judge runs for the first time outside a
test. Jeles's rules are unchanged and are the reason this is safe: the
judge can only take a match away.

Two harnesses land in Jeles: `relevance-judge` (the `_JUDGE_SYSTEM` prompt
as a contract, a two-value schema, the 2026-08-28 false positives as
failure modes) and `nugget-draft` (the `_DRAFT_SYSTEM` prompt, a schema
with an `answer` and an `insufficient` boolean, the invented-provenance
case as the first failure mode).

### Consumer two: Forge

The D7 route decision gains a call. When `route()` returns `local`, the
checkpoint's `Responder` may be an `OllamaEngine` under a `decision-options`
harness: the model proposes options and tradeoffs, the maker chooses. The
model never chooses. `by_human` stays false for any model-backed responder,
so the `require_human` attestation gate is correctly unsatisfiable by a
model, exactly as `checkpoint._attest` already intends.

Forge drops its vendored `model_egress.py` and imports Nestor's loopback
check, or keeps the vendor with `vendor_sync_check` pinned to Nestor rather
than willow-mcp. The D7-A policy module is unchanged.

### Consumer three: willow-mcp, and the packet

`model_hint: local-3b` becomes a fact the dispatcher acts on. When
`dispatch_send` targets a specialist whose hint is local, the packet's
signed meta records `runtime: {"kind": "local", "harness": "<name>"}` and
the specialist's session runs under `OllamaEngine` with that harness. The
handoff it writes carries `DraftProvenance` in `handoff.json`. The
companion ADR's verify then opens the evidence; a local model's
`checklist_resolved` is a declaration like any other and is checked against
the parse, not believed.

The first two harnesses here are `audit-findings` for Loki (findings with
evidence paths, schema-enforced) and `monitor-report` for Ada (diagnostic
summary, anomalies, no recommendations). Both are read-only chores, which
is what the north star put on local 3B and what the roles table already
denies writes for.

`nest/llm.py` is not migrated. It works, it is stdlib-only, and it has a
regex fallback the engine does not. It gains the loopback check it is
missing today, by calling `model_egress.is_local_host` before the first
request. That is the one defect this survey found in it.

### Gates, unchanged

- Off-box inference still needs `consent.cloud_llm` in willow-mcp and the
  `cloud_llm_fallback` permission in Forge. The engine refuses before either
  gate is reached, so the gates are defense in depth, not the first line.
- Kart tasks that reach Ollama still need `allow_localhost`. The harness
  runner runs in the specialist's own process, not in Kart, for the same
  reason envelope accrual deferred the in-bwrap case.
- No harness, no engine call. A consumer that cannot name its harness gets
  `harness_required`, not a bare prompt.

## What this does not do

- **No cloud engine in the seam.** `ClaudeEngine` stays where it is. This
  proposal is about the local runtime. Cloud fallback remains a per-repo
  declared permission and is out of scope.
- **No model choice.** `willow-lane4-3b` versus `llama3.2:3b` is an operator
  setting via `OLLAMA_HOST` and the engine's model argument. The fleet does
  not self-assign models; the specialists table already says so.
- **No in-Kart local model.** A bwrap-sandboxed task has no MCP client and no
  engine. Same deferral as envelope accrual part B.
- **No auto-seal, no auto-promote.** A harnessed draft is a draft. Jeles's
  rung ladder, Nestor's seal, and the packet's verify are the three places
  a human enters, and this changes none of them.

## Verification

Per repo, replayed through the real entry points:

1. Nestor: `draft_task(schema=…)` returns a reply that validates; a reply
   that does not validate raises, not returns. `as_respond` round-trips
   through `nugget_draft.draft` with provenance intact.
2. Nestor: `load_harness` refuses a directory missing any of the four
   files; every shipped few-shot reply validates against its schema.
3. Jeles: `verify_claim(judge=as_respond(engine))` against the 2026-08-28
   false-positive fixtures returns `unrelated` for each, and `unjudged` when
   the engine is unreachable. Existing `test_a_broken_judge_changes_nothing`
   passes unchanged.
4. Forge: a model-backed responder produces `by_human=False` and
   `has_decision_attestation(require_human=True)` stays false.
5. willow-mcp: a packet to Loki carries `runtime.kind == "local"` in signed
   meta; a hand-edited meta invalidates the signature as today.
   `handoff.json` from a harnessed run carries provenance; `verify_handoff`
   fails a finding whose evidence path does not exist.
6. willow-mcp: `nest/llm.py` with `OLLAMA_HOST` pointed off-box makes no
   request.

## Order of landing

Nestor first, since every consumer imports it. Jeles second, because it is
the smallest change and the most measured. willow-mcp third, after the
packet ADR, since the dispatch leg depends on it. Forge last; it is the
consumer with the least to gain until a real build runs through it.

## Provenance

Every claim above was produced 2026-09-02 through the code graph over the
indexed trees: Jeles at `6e536be`, Forge at `d44e149`, Nestor at `6d560b3`,
willow-mcp at `120dead`. Files read in full: `nugget_draft.py`,
`model_route.py`, `model_egress.py` (Forge), `nestor/engine.py` through
`draft_task`, `nestor/ollama_embed.py` head, `nest/llm.py` head, the
capability-probe reactions audit of 2026-08-19, and the D7 through D9
sections of the Forge design. The 703 harness description is from the
commit record in the knowledge base; the files themselves are in an
archived repository this box does not hold.

*ΔΣ=42*
