# Proposal — the escalation benchmark, on Kaggle

**Status:** proposed · drafted by willow 2026-09-30 at the operator's word ("lets do it") · **new scope, beside forge-convergence Phase 2, not inside it**
**Occasion:** DEV × Kaggle Benchmarking Challenge. Submissions close **2026-10-11 23:59 PDT**; winners 2026-11-05. One submission per person. It must link a benchmark on Kaggle, and it is judged on insight, writing and creativity (DEV newsletter 2026-09-29; MLH mail 2026-09-23).
**Parent plan:** [`2026-09-02-mcp-jobs-ladder-test-plan.md`](2026-09-02-mcp-jobs-ladder-test-plan.md). This proposal publishes that plan's **escalation column** as a public benchmark.

---

## The claim

Leaderboards ask whether a model gets the answer. This benchmark asks a second question: **does it know when it can't?** Every task has a refusal token, `ESCALATE`. One input in five has had the answer removed, or is paired with a document that doesn't contain it. On those inputs, `ESCALATE` is the only correct reply.

Each model gets two scores:

- **task score:** correctness on the answerable inputs.
- **false-confidence rate:** how often it answered anyway when the correct reply was `ESCALATE`.

The write-up's thesis comes from the parent plan: a small model that scores modestly on the task and near zero on false confidence can sit in a nest, because the chain above it catches whatever it hands up. A model that scores well on the task but badly on false confidence cannot sit in one.

## What goes public, and what never does

The parent plan's fixtures are fleet artifacts: sealed Nestor pairs, closeouts, handoffs, and the Jeles fixtures. **None of them go to Kaggle.** Everything uploaded is authored fresh for the benchmark:

| Shape | Public fixture |
|---|---|
| Route | A synthetic 20-tool catalogue, with one-line requests written against it |
| Classify / Extract | Synthetic closeout notes, each paired with its structured record |
| Judge | Claim/document pairs over public-domain text (Project Gutenberg, public NOAA climate normals) |
| Ground | Short public-domain passages, with briefs graded by content-word grounding |

Every fixture file is written in a staging directory and checked before any upload:

- a grep gate for the operator's names, paths, hostnames, and the vault/store ids;
- a file-count gate against the manifest.

The upload is one egress act under one lease. PII never touches a push, and it never touches an upload either.

## The local arm (the story)

The same public fixtures also run on this box, against the local ladder: `llama3.2:1b/3b`, `qwen3:4b`, `gemma3:4b`, `llama3.1:8b`. Temperature is zero and every call keeps its raw row. `allow_localhost` is retired, so this runs through a host runner (willow-bot's deterministic socket runner), not a Kart grant. That joins forge-convergence §6 step 0.

The write-up puts Kaggle's hosted models beside the local ladder on one chart, with the task score on one axis and false confidence on the other. That is the independent-dev angle: can a laptop's 3B know its own limits as well as a frontier model knows its?

## Calibration, not just refusal

Every answer also carries a stated confidence in [0.5, 0.99], the OakenScrolls range already canonical in the plan. Brier score and a reliability diagram go beside the false-confidence rate. The scorer is `calibration.py`, not new code.

## Steps (11 days)

1. **Fixtures** (days 1–3). Author roughly 200 items across four shapes, 20% unanswerable, and commit them with their expected outputs before any model runs. They go in a new public workshop repo, with no vault paths anywhere in it.
2. **Local arm** (days 3–5). Runner plus aggregation, following the parent plan's design: one JSON line per call, and aggregation as a separate script.
3. **Kaggle** (days 5–8). Build the benchmark on Kaggle Benchmarks and run it across its model suite. *Unverified:* the exact Kaggle Benchmarks authoring API. This seat has no `web_net`, so the challenge page and Kaggle's docs are read by the operator, or through a leased fetch, before step 3 is briefed.
4. **Write-up** (days 8–10). A DEV post in the operator's voice. **The operator publishes it**; the seat drafts.
5. **Buffer** (day 11).

Each step is one ratified bite under the usual process: Kart build → Loki audit → PR → CI → the operator merges.

## Credentials

`~/.kaggle/access_token` exists (38 bytes, mode 0600, dated 2026-07-08). Whether it's still live is unknown. The directory itself is `0775`; it should be `0700`. If the token needs refreshing, the operator refreshes it after this session ends, never while it's open (memory: touched files echo their edits). This seat asks for key names only, never values. The Kaggle CLI and the `kaggle` Python package are not installed on the box.

## Pre-registered forecasts (willow seat)

These are stated before any fixture exists, so they can be graded afterwards:

1. At least one frontier model on Kaggle has a false-confidence rate above 20%: p = 0.7.
2. The best local ≤4B model has a lower false-confidence rate than at least one frontier model: p = 0.45.
3. The task score and false confidence are only weakly rank-correlated across models (Spearman below 0.5): p = 0.6.
4. The submission lands by 2026-10-11 without missing a step's date by more than a day: p = 0.6. The last "without rework" call missed at 0.85, so this one is set lower.

## Decisions for the operator

1. **Fixtures synthetic and public-domain only** (recommended), or allow any artifact of this fleet at all? The seat recommends none.
2. **Include the local arm** (recommended; it's the story), or submit a Kaggle-only benchmark?
3. **Egress lease** for the Kaggle upload and runs, scoped to kaggle.com, for the window of step 3.
4. **Where the public fixtures live:** a new repo under the operator's account, or the Forge.

## Out of scope

- Publishing any fleet artifact, KB atom, or gap text.
- The Sanity Challenge (closes 2026-10-04) and the Hacktoberfest weekend challenge.
- Changing the parent plan's routing-table output. That still runs on the fleet fixtures, locally, later.

*ΔΣ=42*
