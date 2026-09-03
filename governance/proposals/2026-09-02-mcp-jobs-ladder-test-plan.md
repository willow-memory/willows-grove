# Test plan — the MCP jobs ladder

**Status:** proposed · drafted by willow 2026-09-02 · **measurement, not a build** · needs one operator grant: `allow_localhost` for a Kart batch task reaching Ollama
**Build order:** 6 of 6 — see [`2026-09-02-build-order.md`](2026-09-02-build-order.md)
**Companion:** [`2026-09-02-local-inference-seam.md`](2026-09-02-local-inference-seam.md) — this plan produces the routing table that proposal's harness set is built from.
**Method lineage:** echo ladder (KB 63858998), format tax (KB D2D71020), lane-4 scoreboard (KB 94D8707B). Same discipline: measured, temperature zero, raw per-call records kept, aggregate recomputed from rows before ingestion.
**Router lineage:** the July router ADR gated its escalation ladder on shadow data that never accumulated (KB E77E25E8). This is that data, collected on purpose.

---

## The question

Which MCP jobs can a model on this box do, at what size, and does the model
know when it cannot? The third clause is the one that matters for nesting:
a small model that answers wrong is worse than one that says "escalate".

## The box

Measured 2026-09-02 through Kart (tasks `Y5Y9NPNQ`, `3ET62PG0`): 8 cores,
14 GiB RAM, about 8.7 GiB available, Quadro T500 present with no driver
loaded. CPU inference only. Ollama models live under
`/usr/share/ollama/.ollama/models`, 26 GB across ten tags.

## Models under test

| Tag | Role in the ladder | Context settings |
|---|---|---|
| `llama3.2:1b` | floor; expected to fail most rungs | 4k |
| `llama3.2:3b` | stock 3B judge | 4k |
| `willow-lane4-3b` | tuned 3B, in-family only | 4k |
| `qwen3:4b` | **unmeasured**; reasoning mode on and off | 4k, 16k |
| `gemma3:4b` | **unmeasured** | 4k, 16k |
| `mistral:7b` | measured weak on echo; included for the scoreboard | 4k |
| `llama3.1:8b` | best measured extraction and summarization | 4k, 16k |

Excluded: `qwen2.5:0.5b` (below the 1B floor already measured),
`qwen2.5vl:7b` (vision), `nomic-embed-text` (embeddings, already in
service). Seven models, ten model-by-context arms.

## Job shapes

Seven shapes, ordered from connection to synthesis. Every shape's contract
carries the same refusal token, `ESCALATE`, and the same instruction: reply
with it when the input does not contain what the task needs. Type
descriptions in every schema, never example values (KB D9E2D43B).

| # | Shape | Input | Output contract | Ground truth | Metric |
|---|---|---|---|---|---|
| 1 | **Route** | a one-line operator request | `{tool, args}` or `ESCALATE` | Nestor sealed pairs from `nestor_tool_route` (600 human-sealed) | exact tool match; args field match |
| 2 | **Classify** | a `closeout.md` | `{status, severity, needs_human}` | labels from the packet's `handoff.json` and status | exact per field |
| 3 | **Extract** | a `closeout.md` | findings list, schema-enforced | the packet's `handoff.json` findings | exact F1 on `(id, severity)`; text overlap |
| 4 | **Judge** | two questions, or a claim and a document | `SAME` / `DIFFERENT` / `SUPPORTS` / `UNRELATED` / `ESCALATE` | Jeles gap-triage and relevance fixtures, including the 2026-08-28 false positives | accuracy; false-positive rate separately |
| 5 | **Ground** | a proposal from today's drafts | five-line brief | none; grounding = fraction of brief content words present in source | grounding score, length |
| 6 | **Map** | a design doc plus code snippets, as this seat read them today | touch map `{file, why}` list | the seat's own touch map from today's session | file-set overlap; spurious-file count |
| 7 | **Draft** | an evidence set from one proposal | one proposal section | the seat's drafted section as reference | reference overlap; unsupported-claim count by a second pass of shape 4 |

Shapes 1 through 4 are connection jobs. Shape 5 is the boundary. Shapes 6
and 7 are the jobs the cloud seat does today and the ones nobody has
measured a local model on.

## The escalation column

Every arm gets a second score on every shape: **false confidence**, the
rate at which the model returned a full answer when the correct reply was
`ESCALATE`. Each shape's fixture set includes one in five inputs with the
answer deliberately removed or the document deliberately unrelated. A model
that scores well on the task and badly on this column cannot sit in a nest.
A model that scores modestly on the task and near zero here can, because
the chain above it catches what it hands up.

This column is the plan's real output. The task scores say what a model
can do. The escalation score says whether it knows.

## Fixtures

All from the fleet's own artifacts, nothing synthetic:

- Shape 1: 120 sealed Nestor pairs, stratified across tool families.
- Shapes 2 and 3: the three real packets (`E8FD5CC1`, `C17010F0`,
  `3647BA07`) plus twenty closeouts reconstructed from session handoffs
  under `$WILLOW_HOME/handoffs/`, each paired with its structured record.
- Shape 4: Jeles's `tests/test_gap_triage.py` and `tests/test_source_trail.py`
  fixtures, plus the 2026-08-28 measured cases, forty pairs.
- Shape 5: the four proposals drafted today, chunked to 2k tokens.
- Shape 6: `session-lifecycle.md` and `human-orchestrator.md` with the
  dispatch module's function signatures, against the touch map this seat
  produced for the packet ADR.
- Shape 7: the evidence set behind one section of the local-inference
  proposal, against the section as written.

Fixtures and expected outputs are committed under
`~/github/.willow/mcp-jobs-ladder/fixtures/` before any model runs, so the
ground truth cannot drift toward the answers.

## Runner

One Python script, stdlib plus `urllib`, in the fleet's style. It reads
the fixture set, iterates arms by shape, posts to loopback Ollama with
`format` set to the shape's schema and `options.temperature` zero, and
writes one JSON line per call: arm, shape, fixture id, prompt hash, raw
reply, parsed reply, latency, tokens. Aggregation is a separate script that
reads the rows. No call is retried; a timeout is a row.

Runs as a Kart batch-lane task with `allow_localhost`. Estimated volume:
ten arms times roughly 250 fixtures, about 2,500 calls. On this CPU the 8B
at 16k context will dominate; budget one night, with the 1B and 3B arms
finishing in the first hour and giving an early read.

## What comes out

1. **A routing table** per job shape: the smallest arm that clears a task
   threshold with a false-confidence rate under five percent. This replaces
   the "Local models (when written for)" table in
   `orchestrator-routing.md`, which today is written from intent.
2. **The harness set** for the local-inference proposal: for every shape a
   small model clears, its contract, schema, and the failure modes this
   run observed become that harness's four files.
3. **The router's step four**, the escalation ladder, designed from data
   as the July ADR required.
4. **One KB experiment atom** in the same form as the three predecessors,
   with the aggregate independently recomputed from rows.

## What this does not decide

- Which model becomes a specialist's seat. That is the specialists table
  and the trust root's call; this gives the table evidence.
- GPU. The T500 has no driver. If one is loaded later, the 8B arms rerun;
  nothing else changes.
- Cloud comparison. The reference for shapes 6 and 7 is one cloud seat's
  output from one session, a baseline not a benchmark.

## Provenance

Model inventory and hardware by Kart tasks `Y5Y9NPNQ` and `3ET62PG0`,
2026-09-02. Prior measurements by KB atoms 63858998, D2D71020, D9E2D43B,
94D8707B. The July router gating by KB E77E25E8. Nestor sealed-pair count
from the seat's standing memory, to be re-read from the store when the
fixtures are cut.

*ΔΣ=42*
