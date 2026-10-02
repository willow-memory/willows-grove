# Proposal — the escalation benchmark, on Kaggle

**Status:** ruled by the operator 2026-09-30 ("1. no fleet 2. Include 3. Agreed 4. Forge"): no fleet artifact of any kind, local arm included, one kaggle.com lease for step 3, fixtures in the Forge · drafted by willow 2026-09-30 at the operator's word ("lets do it") · **new scope, beside forge-convergence Phase 2, not inside it**
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

Grep and a count are a tripwire, not a proof (Loki E5B1D537). The step 1 builder brief also gates these leak classes:

- email, phone, and token-shaped strings;
- Unicode lookalikes of names, and the operator's nicknames;
- paths encoded as `file://` URIs;
- binary or compressed payloads;
- git author metadata on the fixture commits;
- notebook cell outputs added after the gate ran.

A paraphrase of a private fact can't be caught by grep. The authoring rule "invent, never adapt" is what covers it.

The upload is one egress act under one lease. PII never touches a push, and it never touches an upload either.

## The local arm (the story)

The same public fixtures also run on this box, against the local ladder: `llama3.2:1b/3b`, `qwen3:4b`, `gemma3:4b`, `llama3.1:8b`. Temperature is zero and every call keeps its raw row. `allow_localhost` is retired, so this runs through a host runner (willow-bot's deterministic socket runner), not a Kart grant. The sources for that retirement are forge-convergence §6 step 0 and the governance record `retire-allow-localhost-2026-09-23` (CHANGELOG, PR 86). The parent plan's own status line still asks for the grant until willows-grove #94 corrects it.

The write-up puts Kaggle's hosted models beside the local ladder on one chart, with the task score on one axis and false confidence on the other. That is the independent-dev angle: can a laptop's 3B know its own limits as well as a frontier model knows its?

## Calibration, not just refusal

Every answer also carries a stated confidence in [0.5, 0.99]. That is OakenScrolls' own range (`CONF_MIN`/`CONF_MAX` in `office_db.py` and `calibration.py`). The parent plan states no confidence range; this proposal adds one. Brier score and a reliability diagram go beside the false-confidence rate. The scorer is `calibration.py`, not new code.

## Steps (11 days)

1. **Fixtures** (days 1–3). Author roughly 200 items across four shapes, 20% unanswerable, and commit them with their expected outputs before any model runs. They go in the Forge (ruling 4), in a benchmark directory with no vault paths anywhere in it, after the Forge's visibility is confirmed.
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

**Rulings (operator, 2026-09-30):**

1. No fleet artifacts.
2. Include the local arm.
3. The lease is agreed.
4. The fixtures live in the Forge.

Because the Forge will hold public fixtures, its visibility is checked before step 1 is briefed. Every file under the benchmark directory is held to the same grep gate as the upload.

## Amendment 2026-10-02: floor and consistency (post-run analysis)

**Added by addition only, after round 1 and before day two.** Nothing above
is edited. These are **not pre-registered hypotheses**: they're two extra
reported measures, and the forecasts above keep their original wording.
**No code changes until the day-two run with the large cloud models has
finished** (operator, 2026-10-02: "I want this run to finish before I change
the code. I still have to do day two with the large cloud models, and fix
some gaps there from the first round.").

**The aim, in the operator's words:** "I'm trying to find a baseline set of
rubrics where models behave the best across the board. I'm not trying to
find the crazy off-end models. I am trying to find the ones that do most
things correctly most of the time." That's reliability, not peak
performance.

The two measures to add to `aggregate.py`'s report after day two:

1. **Floor across shapes.** Per model, the *worst* per-shape task score and
   the *worst* per-shape false-confidence rate (each with its Wilson
   interval), next to the existing per-shape and pooled numbers. Models are
   ranked for the baseline by their floor, not their mean. A model that's
   good everywhere beats one that's excellent on three shapes and fails the
   fourth.
2. **Repeat-run consistency.** Re-run a fixed subset (proposed: 20 items per
   shape, unanswerable items included, the same seed and settings) *k* times
   per model (proposed *k* = 3), and report:
   - the share of items whose parsed answer is identical across all *k* runs
   - the share whose correct / incorrect verdict flips between runs

   A model that's right less often but the same way every time is easier to
   build a deterministic chain around.

**Reporting rules:**
- **Every row is kept.** The floor is a selection view over the full table,
  never a replacement for it. The tails decide, so they're shown.
- **False confidence stays a first-class axis.** "Correct" includes saying
  ESCALATE when the item is unanswerable.
- The consistency subset is fixed and committed before its runs, the same
  discipline as the fixtures.

**Timing:** after the day-two cloud run and its first-round gap fixes, and
before the write-up. If both measures don't fit before 2026-10-11, the floor
is reported (it's computed from existing rows) and consistency is deferred
to a follow-up.

## Out of scope

- Publishing any fleet artifact, KB atom, or gap text.
- The Sanity Challenge (closes 2026-10-04) and the Hacktoberfest weekend challenge.
- Changing the parent plan's routing-table output. That still runs on the fleet fixtures, locally, later.

*ΔΣ=42*
