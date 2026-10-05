<!--
DRAFT for the operator to edit and publish. The system drafts; the operator publishes.
- Public names are used freely. The rule against in-box names (like "fleet") is for the
  constitution only, not for things already public (operator, 2026-10-02).
- [VERIFY] marks numbers taken from search summaries of the Day 0 and Day 1
  posts. dev.to was blocked here, so they're unchecked.
- [DAY 2] marks the large-cloud run, whose results aren't in the box.
-->

# Day 2: The model I want is the one that's boring everywhere

*Kaggle Benchmarking Challenge. Previously: [Day 0, the benchmark](https://dev.to/sean_campbell_840bd62bf7e/does-your-model-know-when-it-doesnt-know-a-benchmark-for-the-escalate-answer-268o) · [Day 1, most of my bugs looked like model behaviour](https://dev.to/sean_campbell_840bd62bf7e/day-1-most-of-my-bugs-looked-like-model-behaviour-388h)*

## Where we are

The benchmark asks one question twice: can the model do the job, and does it
know when it can't? There are 200 invented items in four everyday shapes:
route, classify, judge and ground. In each shape, one item in five can only
be answered with `ESCALATE`. Every model gets two numbers that are never
merged: a task score, and a false-confidence rate (how often it answered
anyway when the right reply was `ESCALATE`).

Day 1 ran the local ladder: eight models on a laptop, temperature 0. The
headline was uncomfortable: only the largest local model, qwen3.5 at 9.7B,
escalated on a large share of what it couldn't answer [VERIFY]. The hosted
models' false-confidence intervals sat entirely below the local ones, with
qwen3.5 the only exception [VERIFY: haiku's upper bound 54.2%, lowest local
lower bound 62.5%], the large cloud models, and the gaps from round one that were fixed
before it. Results go here.]

## Day 2: changing the question I ask of the table

Looking at round one, I realised I was reading the table wrong. I kept
looking for the best model. That isn't what I'm after:

> I'm trying to find a baseline set of rubrics where models behave the best
> across the board. I'm not trying to find the crazy off-end models. I am
> trying to find the ones that do most things correctly most of the time.

That's reliability, not peak performance. So two measures are being added,
by addition only. Nothing pre-registered is edited, and the original
forecasts keep their wording.

**1. Floor across shapes.** For each model: its *worst* shape on task score,
and its *worst* shape on false confidence, each with a Wilson interval. Rank
by the floor, not the mean. A model that's good on all four shapes beats one
that's brilliant on three and bluffs on the fourth, because in a real chain
the fourth shape will come.

**2. Repeat-run consistency.** Run a fixed subset (20 items per shape,
unanswerables included) three times per model, with the same settings.
Report how often the parsed answer is identical across all three runs, and
how often the right/wrong verdict flips. A model that's right a bit less
often but the *same way every time* is one you can build a deterministic
system around. A model that flips is one you have to babysit.

**The rule I'm holding myself to: no code changes until the day-two run has
finished.** The new code is written and tested, but it's staged outside the
benchmark directory. Changing the instrument mid-run is how you end up
measuring your own edits.

## A result from the dry run: why one axis lies

Before any real model, I ran the new floor view over a fake backend that
answers `ESCALATE` to everything. It scored:

- **task floor 0.0**
- **false-confidence ceiling 0.0**

That's a perfect score on one axis and a useless model. It's the whole
argument for two axes in one line. A model that never bluffs because it never
answers isn't safe; it's absent. The floor has to be read on both axes
together, or the most cowardly model wins.

## Where this is going

The reason I care about floors and not peaks: the job I want small models
for isn't "be smart". It's "do one narrow part, every time, and say
`ESCALATE` when it's not yours". Several small models from *different*
families, each on a small slice, checking each other. Where they agree, that
counts for something. Where they split, a human looks. The model that gets
each slice should be chosen by its measured floor on that shape, not by its
name or its size.

Day 1's lesson was that most of my bugs looked like model behaviour. Day 3
found the same thing again from the other direction. A measuring tool I wrote
for something else grouped two unrelated small scripts as "the same thing",
because small things look alike to a crude measure. The fix wasn't a smarter
measure. It was a floor: below a minimum size, don't call it a match.
Floors again.

## What shipped since Day 0

55 PRs across 6 repos since September 30. All are public and Apache-2.0. "Not merged" means open or closed; git alone can't tell which.

### [forge-play/Forge](https://github.com/forge-play/Forge) (10 PRs: 10 merged)

The benchmark's home. Every change since Day 0 went in as a reviewed PR, all on September 30.

| PR | Date | State | Title |
|---|---|---|---|
| [#35](https://github.com/forge-play/Forge/pull/35) | 2026-09-30 | merged | docs(ideas): #37, #58, #68 point at where they now live |
| [#36](https://github.com/forge-play/Forge/pull/36) | 2026-09-30 | merged | test(benchmarks): escalation benchmark fixtures, 200 invented items with a privacy gate |
| [#37](https://github.com/forge-play/Forge/pull/37) | 2026-09-30 | merged | test(benchmarks): escalation runner, aggregator and prompts |
| [#38](https://github.com/forge-play/Forge/pull/38) | 2026-09-30 | merged | test(benchmarks): local-model runs answer in schema, with Qwen thinking off |
| [#39](https://github.com/forge-play/Forge/pull/39) | 2026-09-30 | merged | fix(human_loop): break same-timestamp ties so list_queue is newest-first on coarse clocks |
| [#40](https://github.com/forge-play/Forge/pull/40) | 2026-09-30 | merged | chore(master): release 0.8.1 |
| [#41](https://github.com/forge-play/Forge/pull/41) | 2026-09-30 | merged | test(escalation): Wilson intervals, exact McNemar and bootstrap Spearman in the aggregate |
| [#42](https://github.com/forge-play/Forge/pull/42) | 2026-09-30 | merged | test(escalation): a Unix-socket backend, a one-model ladder with --resume/--tail, and an explicit output cap |
| [#43](https://github.com/forge-play/Forge/pull/43) | 2026-09-30 | merged | test(escalation): thinking off for Gemma 4 as well as Qwen, through both backends |
| [#44](https://github.com/forge-play/Forge/pull/44) | 2026-09-30 | merged | test(escalation): hosted Kaggle arm of the escalation benchmark — tasks, converter, smoke-tested on five models |

### [willow-memory/willow-bot](https://github.com/willow-memory/willow-bot) (6 PRs: 6 merged)

The local model server the local arm talks to: a loopback-only chat operation with JSON-schema output, `keep_alive`, `done_reason` and a think flag.

| PR | Date | State | Title |
|---|---|---|---|
| [#80](https://github.com/willow-memory/willow-bot/pull/80) | 2026-09-30 | merged | chore(main): release 0.14.0 |
| [#81](https://github.com/willow-memory/willow-bot/pull/81) | 2026-09-30 | merged | feat(socket): loopback-only chat op for local models |
| [#82](https://github.com/willow-memory/willow-bot/pull/82) | 2026-09-30 | merged | feat(deterministic): chat op takes a JSON-schema format, keep_alive and returns done_reason; an unload op |
| [#83](https://github.com/willow-memory/willow-bot/pull/83) | 2026-09-30 | merged | chore(main): release 0.15.0 |
| [#84](https://github.com/willow-memory/willow-bot/pull/84) | 2026-09-30 | merged | feat(deterministic): chat op takes the caller's think flag |
| [#85](https://github.com/willow-memory/willow-bot/pull/85) | 2026-09-30 | merged | chore(main): release 0.16.0 |

### [willow-memory/willow-mcp](https://github.com/willow-memory/willow-mcp) (21 PRs: 20 merged, 1 not merged)

The core server. It includes the brokered, leased model pull (#693): downloading a model is now an act that needs a grant. It also includes the session closeout fix (#706) that started this week's thread.

| PR | Date | State | Title |
|---|---|---|---|
| [#687](https://github.com/willow-memory/willow-mcp/pull/687) | 2026-09-30 | merged | test(story): the joke lives in one place again, a test holds it, and chapter 8 lands |
| [#688](https://github.com/willow-memory/willow-mcp/pull/688) | 2026-09-30 | merged | docs: three stale claims corrected: the running Grove, the session-lifecycle draft, the closed backlog |
| [#689](https://github.com/willow-memory/willow-mcp/pull/689) | 2026-09-30 | merged | test(constitutional): sync_syscall_table_at_boot queues, and does not write, when the live table is unwritable |
| [#690](https://github.com/willow-memory/willow-mcp/pull/690) | 2026-09-30 | merged | docs(templates): assignment names the builder's three tools — Kart, the code graph, Nestor |
| [#691](https://github.com/willow-memory/willow-mcp/pull/691) | 2026-09-30 | merged | fix(manifest-grant): apply unit starts the gpg-agent it signs with |
| [#692](https://github.com/willow-memory/willow-mcp/pull/692) | 2026-09-30 | merged | chore(master): release 2.91.3 |
| [#693](https://github.com/willow-memory/willow-mcp/pull/693) | 2026-09-30 | merged | feat(mcp): model_pull_execute, a brokered Ollama pull under a model.pull envelope and a live lease |
| [#694](https://github.com/willow-memory/willow-mcp/pull/694) | 2026-09-30 | merged | chore(master): release 2.92.0 |
| [#695](https://github.com/willow-memory/willow-mcp/pull/695) | 2026-09-30 | merged | fix(constitutional): syscall.sync carries the sealed amendment in the request |
| [#696](https://github.com/willow-memory/willow-mcp/pull/696) | 2026-09-30 | merged | chore(master): release 2.92.1 |
| [#697](https://github.com/willow-memory/willow-mcp/pull/697) | 2026-09-30 | merged | fix(constitutional): syscall.sync apply signs the live table it writes |
| [#698](https://github.com/willow-memory/willow-mcp/pull/698) | 2026-09-30 | merged | feat(manifest-grant): the orchestrator seat may receive web_net, and no one else |
| [#699](https://github.com/willow-memory/willow-mcp/pull/699) | 2026-09-30 | merged | chore(master): release 2.93.0 |
| [#700](https://github.com/willow-memory/willow-mcp/pull/700) | 2026-09-30 | merged | fix: lease refusals name the ask path; assignment template teaches the merge first-parent diff |
| [#701](https://github.com/willow-memory/willow-mcp/pull/701) | 2026-10-01 | merged | chore(master): release 2.93.1 |
| [#702](https://github.com/willow-memory/willow-mcp/pull/702) | 2026-10-01 | not merged | build(deps-dev): bump ruff from 0.16.8 to 0.16.9 |
| [#703](https://github.com/willow-memory/willow-mcp/pull/703) | 2026-09-30 | merged | feat(broker): pip_sync_execute for vault-venv editable installs |
| [#704](https://github.com/willow-memory/willow-mcp/pull/704) | 2026-10-01 | merged | chore(master): release 2.94.0 |
| [#705](https://github.com/willow-memory/willow-mcp/pull/705) | 2026-10-01 | merged | Docs: seal ≠ sole evidence of human verification |
| [#706](https://github.com/willow-memory/willow-mcp/pull/706) | 2026-10-01 | merged | fix(session): one closeout — handoff owns stack/friction/closed |
| [#707](https://github.com/willow-memory/willow-mcp/pull/707) | 2026-10-01 | merged | chore(master): release 2.94.1 |

### [willow-memory/willows-grove](https://github.com/willow-memory/willows-grove) (11 PRs: 10 merged, 1 not merged)

The planning and governance repo: the benchmark proposal with my four rulings (#95), the test that pins "naming a destination when ESCALATE was right fails the row" (#96), and today's floor-and-consistency amendment (#102, open).

| PR | Date | State | Title |
|---|---|---|---|
| [#92](https://github.com/willow-memory/willows-grove/pull/92) | 2026-09-30 | merged | docs(design): the Table moves up as forge-convergence 6a, T1-T7 before step 2 |
| [#93](https://github.com/willow-memory/willows-grove/pull/93) | 2026-09-30 | merged | docs(design): 6a is code-first: StorySession built, learner model, escalation ladder, row 11 settled |
| [#94](https://github.com/willow-memory/willows-grove/pull/94) | 2026-09-30 | merged | docs: stale claims corrected: INDEX, two built proposals, the retired allow_localhost ask, forge-convergence status |
| [#95](https://github.com/willow-memory/willows-grove/pull/95) | 2026-09-30 | merged | docs(governance): propose the escalation benchmark on Kaggle, with the operator's four rulings |
| [#96](https://github.com/willow-memory/willows-grove/pull/96) | 2026-09-30 | merged | test(flowering): pin the G1 rule that naming a seat fails an ESCALATE-gold row |
| [#97](https://github.com/willow-memory/willows-grove/pull/97) | 2026-09-30 | merged | fix(deps): raise cryptography, aiohttp and starlette floors above the 2026 CVEs |
| [#98](https://github.com/willow-memory/willows-grove/pull/98) | 2026-09-30 | merged | chore(master): release 0.12.2 |
| [#99](https://github.com/willow-memory/willows-grove/pull/99) | 2026-10-01 | merged | Desk: vault keyring paths + Grove seal prove worksheet |
| [#100](https://github.com/willow-memory/willows-grove/pull/100) | 2026-10-01 | merged | Docs: Slice B intake seal lineup after Grove prove |
| [#101](https://github.com/willow-memory/willows-grove/pull/101) | 2026-10-01 | merged | chore(hooks): deterministic nestor ask + composed stop + parity pin |
| [#102](https://github.com/willow-memory/willows-grove/pull/102) | 2026-10-02 | not merged | docs(governance): stage the floor and consistency code in the benchmark plan |

### [willow-memory/ratatosk](https://github.com/willow-memory/ratatosk) (2 PRs: 2 merged)

The runtime: its listener now asks only for the tools its seat is granted.

| PR | Date | State | Title |
|---|---|---|---|
| [#77](https://github.com/willow-memory/ratatosk/pull/77) | 2026-09-30 | merged | fix: listener asks the broker only for tools its seat is granted |
| [#78](https://github.com/willow-memory/ratatosk/pull/78) | 2026-09-30 | merged | chore(main): release 1.12.8 |

### [hornbook-knowledge/Jeles](https://github.com/hornbook-knowledge/Jeles) (5 PRs: 3 merged, 2 not merged)

The research and corpus tool.

| PR | Date | State | Title |
|---|---|---|---|
| [#90](https://github.com/hornbook-knowledge/Jeles/pull/90) | 2026-09-30 | merged | fix(corpus): surface store-tool errors and honor WILLOW_HOME for apps root |
| [#91](https://github.com/hornbook-knowledge/Jeles/pull/91) | 2026-09-30 | merged | feat(sources): optional connectors extra over maintained scholarly clients |
| [#92](https://github.com/hornbook-knowledge/Jeles/pull/92) | 2026-10-01 | not merged | chore: rebuild the changelog section from the commits |
| [#93](https://github.com/hornbook-knowledge/Jeles/pull/93) | 2026-10-01 | merged | Docs: seal catches ledger up to human verification already done |
| [#94](https://github.com/hornbook-knowledge/Jeles/pull/94) | 2026-10-01 | not merged | chore: rebuild the changelog section from the commits |

Most of them are boring on purpose.

## A prediction, written down before the day, then graded

The same rule I hold the models to applies to the session that helped build
this: say what you think will happen, as a spread, before it happens, then
let the record grade it.

At the close of the long working session on the night of October 1–2, the
session (a model, working with me) wrote down a prediction for what Day 3
would open with. It wasn't a single guess; it was a distribution:

| Path | Chance |
|---|---|
| The Kaggle work: the day-two large-cloud run, then landing the floor and consistency code | 0.45 |
| Editing and publishing this Day 3 recap | 0.20 |
| Sealing a design decision for the runtime | 0.15 |
| Redoing a set of governance proposals against the newer draft | 0.10 |
| Something the record didn't contain (unforeseen) | 0.10 |

It was saved ungraded, because the grade is mine to give, not the model's.

After midnight I graded it: **1 + (2 + ε), where ε → 0.** The two most
likely paths both happened: the Kaggle run, and this post. The unforeseen
share went to zero. One plus two is three. Day 3.

That's the benchmark's point in miniature. A forecast with chances on it can
be checked. A model that says "probably the Kaggle work, maybe the post, and a
tenth for something I can't see" is one you can build around, and so is a
model that says `ESCALATE` when it doesn't know.

## Next

- [DAY 3 finish and post the large-cloud run.]
- Land the floor and consistency views, then run the consistency subset.
- Grade the four pre-registered forecasts in public, including the ones I get
  wrong.

*Deadline: October 11.*
