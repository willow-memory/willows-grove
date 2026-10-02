# Next pile: the runtime, the one script

*Started 2026-10-02, late. A draft for the next bite. Nothing here is built
or sealed. Every assessment under a "(agent-reported)" heading is unattested.*

## What it is

**The gate is the script** (§8 of `workflow.md`). One run, from check-in to
check-out to reconcile. It isn't a checkpoint inside something else.

**Where it lives: Rat (ratatosk).** The one-box plan's D1 proposes Rat as the
one runtime behind every front end. D1 is **not sealed yet**. The run order
goes into Rat; the seven purposes are its parts.

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

- D1: is Rat the one runtime? (Unsealed.)
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
- It isn't in Rat (D1 is unsealed).
- The chain is one box's chain; packet stamps between boxes (ΔΣ=42) aren't
  built.

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
