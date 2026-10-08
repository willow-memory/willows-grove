<!-- b17: WGRV1  ΔΣ=42 -->
# The one script, local first, and how the UI shows it

§1 Status · §2 The pieces · §3 The box flow · §4 Local models · §5 The UI · §6 The phone · §7 Order · §8 Open

## §1 Status

**Proposal.** Written 2026-10-08 from a review session. The operator, the same
day: *"Back to the local, because that's where I need to be working first."*
and *"All of that, and how it works with the UI."* The order in §7 is not yet
ratified (CLAUDE.md rule 4).

Builds on [`../phone-seat-production.md`](../phone-seat-production.md) §"The
phone only proposes" and willow-mcp PR 712 (`onescript_run_execute`).

## §2 The pieces

| Piece | Runs on | Does |
|---|---|---|
| One script (willow-bot `one-script/`) | box | check-in, scope, serve, grading, writes, check-out; holds the record |
| Nestor UI `:8765` | box | the only place a seal is made |
| Rat `--onescript` + Ollama `:11434` | box now, phone later | reads `served.json`, appends `proposals.jsonl`; local rungs only |
| willow-mcp `onescript_run_execute` (PR 712) | box, broker process | runs the eight host steps from a fixed table: no shell, no terminal, no caller paths |
| Grove `:8766` | box, loopback | shows all of the above; never seals, never runs a step |

## §3 The box flow

Through the broker verb, once PR 712 is merged and the desk has run
`session_enter`:

| # | Step | Who |
|---|---|---|
| 1 | `keys_export` | verb |
| 2 | `checkin` | verb |
| 3 | `scope` | verb; returns the card and `serve:<hash>` |
| 4 | Seal the scope in Nestor | **operator** |
| 5 | `seal` (records which pair sealed it) | verb |
| 6 | `serve` (`max_chars` 1..60000) | verb |
| 7 | `rat_turn` (installed local Ollama tag) | verb |
| 8 | `turn` (grades proposals; writes nothing) | verb |
| 9 | Seal each `pass` proposal in Nestor, then `seal` | **operator**, then verb |
| 10 | `checkout` (the morning screen) | verb |

Walked by CLI in a scratch box on 2026-10-08 (no Nestor, so it stopped at
step 4):

| Step | What happened |
|---|---|
| `checkin` | Toolchain gate hard-closed: ruff 0.16.10 installed, 0.16.7 pinned. With 0.16.7, the box opened (4/4 probes). |
| `scope` | One table, five rows, subject `serve:167bfe94…` |
| `serve` unsealed | `empty`: "the scope has no human seal over this exact set; nothing served" |
| `turn` on two test rows | one `link_fail` (cite not served), one `refused` (`..` in path); nothing written |
| `checkout` | both rows under NEEDS YOU; "anchor: never sealed"; "coverage: no reconcile on record" |

The verb's `checkin` uses `$WILLOW_HOME/venvs/willow-bot`; that venv needs
ruff 0.16.7, or step 2 stops at its first gate.

## §4 Local models

Before any cloud: repeat steps 7 and 8 per model on the same sealed scope, and
record per model the share of rows that are `pass`, `refused` and `link_fail`,
and how often the model called `propose` at all.

| Candidate | Source |
|---|---|
| `qwen3:4b` | PR 712's next bite |
| `gemma3:4b` | Rat's ladder, `chat` on the `ollama` rung |
| llama3.2 1B / 3B, phi4-mini | July models and the telephone runs (`next-pile.md`) |

Whether a 1–3B model calls `propose` reliably is unmeasured. The phone's model
choice waits on this table.

## §5 The UI

The morning screen is already the UI's content. Grove adds one **read-only**
reader over the box record and the FRANK `onescript_run` receipts, and five
panels:

| Panel | Source | Component |
|---|---|---|
| Check-in | gate and probe rows | `grove-card` |
| Scope + seal status | the scope card; status from `/api/nestor/decide` with the subject as the claim | `grove-card`, `grove-cast-chip` (pending / sealed) |
| Served view | `served.json`, or serve's `empty` / `unreachable` and its reason | `grove-card` |
| Proposals | `proposal` rows: `pass` / `refused` / `link_fail` | `grove-dispatch-rail`; `grove-refusal-chip` with the reason verbatim |
| Morning | `checkout`: NEEDS YOU, DISAGREEMENTS, AGREED NOT SEALED, GRADES, QUIET | `grove-card` |

Each panel keeps three states (INVARIANTS.md §1): **unreachable** when there is
no box or the record can't be read, **empty** when the box exists with no run,
**populated** otherwise.

What the page does not do:

- Run a step. Steps run through the broker verb from the desk seat;
  `grove_reader.py` stays read-only (rule 3).
- Seal. The scope and proposal panels show the subject and link to Nestor.

A clickable sketch of the chat side, v1: [`box-stream-v1.html`](../../../web/demo/box-stream/box-stream-v1.html).
Boxes stream from the pile into the chat, a small model says them in one
sentence, and the three checks run; five cases, including a sentence that
fails and an unreachable record. Example content, no model behind it.
v1.1, [`box-stream-v1.1.html`](../../../web/demo/box-stream/box-stream-v1.1.html), adds: sentences that use only
what the boxes hold, the human line drawn plain and the sentence labelled agent,
a fifth check (the human's words quoted exactly), check chips labelled as
example results, and a time stamp on every turn.

The chat reads as a conversation (2026-10-08). The operator: *"All right so
let's think about this as a casual conversation instead of just pure system
talk"* and *"yes, the chat should read more conversational in the ui"*. The
facts stay as strict as before; only the voice loosens. One or two things at a
time with "more?" for the next, reply chips that land as the human's plain
line, small talk answered by code with no model, a repeated question answered
from the pile, and a short fixed list of free glue words that carry no facts.
Sketch v1.2: [`box-stream-v1.2.html`](../../../web/demo/box-stream/box-stream-v1.2.html).

Asked again, answered again (2026-10-08). The operator: *"one big thing I
would change is the asked/answered. It should show the information again, just
as noted with the timestamp"*. A repeated question shows the same boxes and the
same sentence again, from the pile with no model asked, stamped "as noted at"
the time it was first said. Sketch v1.3: [`box-stream-v1.3.html`](../../../web/demo/box-stream/box-stream-v1.3.html).

Tested on a human data set (2026-10-08). The operator: *"Next is to test it on a
random, more human data set. They are many fictional characters in the demos.
How about the car salesman"*. Nestor's fictional Big Jim Motors desk
(`Nestor/demo/big_jim.py`) was stocked with five machine drafts; nothing was
sealed. Its real output fed the stream: [`big-jim-stream-v1.html`](../../../web/demo/box-stream/big-jim-stream-v1.html).
What it added:

- A check the first three do not cover: **no draft said as fact**. "The Civic
  runs great, one owner, 142,000 miles" uses only words the boxes hold and
  still has to fail, because the box says nobody has checked it.
- A refusal is shown verbatim and never narrated: the Kia shares the Jeep's
  last 6 (`784210`), Nestor refused the draft, and code says so in one line.
- Prose with no VIN ("the blue Civic") matched nothing (0.000), by design;
  the human's words are quoted back exactly and code asks for the last 6.
- `big_jim.py draft` shows that refusal as a raw traceback; filed as a
  separate task.

Tested on a character with depth (2026-10-08). The operator: *"lets do one
more for one of the demo characters with more depth."* Nestor's fictional
shoebox (`Nestor/demo/shoebox.py`): Nieves, the only person holding a key to
her grandmother's letters. Its real store fed the stream:
[`shoebox-stream-v1.html`](../../../web/demo/box-stream/shoebox-stream-v1.html). What it added:

- The human's words are the substance here, not a side field. Every sealed
  phrase carries her reason, and check 5 (her words quoted exactly) is the
  one that catches a model retelling "She meant the damage." as "she meant
  the destruction she caused".
- The stream can show what Nestor's own review views do not yet (IDEAS
  §6.35): a changed mind, with the March reading kept beside the current
  one, and a "not yet" with its reopen condition in her words.
- For one person's archive, a draft is not always a task. Two drafts she
  chose to leave ("Whose face. Leaving it.") should not rise as "needs you";
  the picker has to respect a human's leave-it, and the voice stays quiet.
- A known store gap (two men called Pepe, the first overwritten, IDEAS §6.37)
  is said by code in one line, never narrated by a model.

Theory: two groves linked (2026-10-08). The operator: *"This next one might be
pushing it a bit. So, and it's theory right now. I'll give you the scope."*,
*"Say Nieves wanted to buy a car from Big Jim, and their groves linked up."* and
*"sketch it as a box stream"*. Not built:
[`linked-groves-stream-v1.html`](../../../web/demo/box-stream/linked-groves-stream-v1.html). The shape:

- Records never merge; boxes cross, each marked with the grove it came from.
  "Who wrote it" doubles: you, your agent, the other human, their agent.
- A seal from the other grove is that person's word, never yours, and a sixth
  check holds it there. A seal that will not verify against their enrolled key
  arrives as a draft, the way Nestor's bundle import already demotes one.
- The human's words leave only through the disclosure card (once, this
  session, always, never); some things are set to never and not asked about.
- When the two records disagree, both stand, marked unresolved (the quorum
  ruling), until a neutral third both accept. An offer is one subject that
  needs a seal from each grove; neither can write the other's half.
- Matching across groves uses shared keys (a VIN), never people's names.
- Open: enrolling the other grove's key in person, contents on u2u's
  plaintext wire before Gate 6, and revoking a key after the sale.

A third life (2026-10-08). The operator: *"lets bring in a third life. One of the
post apoloptic ones"* and *"It's here. It just turned into a silly story at the
end. It was a group of 5 I think,"*. Found in Nestor's capability-probe life
simulation (`audits/2026-08-19-capability-probe/lives/`: Elena, Marcus, June,
Damon, Yuki, and the Bombardment). June Akiyama, from `june_akiyama.py` and
`global_event_meteoroids.py`: [`june-stream-v1.html`](../../../web/demo/box-stream/june-stream-v1.html).
The sandbox builder needs SQL files that are not in the repo, so the boxes were
read from the modules. What it added:

- **An agent's reading of a person is a proposal, never a fact.** The
  simulation's rulings ("revealed the margin she was operating on") are shown
  as dashed proposal boxes she can accept, fold or reject; a model that says
  "You can't handle the farm alone" is struck.
- **Written about you is not written by you.** Her record is the simulation's
  third-person account and is labelled so; only the twelfth letter is in her
  voice. A first draft of the sketch said "you wrote" and "You asked" for both;
  that was wrong and was fixed before publishing.
- **Nothing reaches someone outside the link.** Ryan is not linked; the letter
  card says so and offers only to keep it or show it whole.
- **A public event is a box every grove receives**, marked as sealed by
  nobody she knows; each grove refracts it through its own record.
- **Open questions stay folded** and are never a task list.

Jeles brought in (2026-10-08). The operator: *"ready to extend it? Bring in Jeles
next."* then *"run a simulated Jeles, that would have been built on their lives,
with the internet where you need to on this box."* Jeles fails closed without a
signed willow-mcp manifest; the runs used the test-fixture manifest from Jeles'
own `tests/conftest.py`, in an isolated temporary folder.

- **The real seed corpus** (968 nuggets, 0 verified by a person) answered none of
  June's questions: every ask became a gap, the best a near miss below 0.5.
  [`june-stream-v1.1.html`](../../../web/demo/box-stream/june-stream-v1.1.html).
- **A simulated Jeles**: 9 nuggets an agent researched on the internet from the
  three lives' own questions, each `asserted` with its sources
  ([`jeles-lives-corpus-2026-10-08.json`](../../../web/demo/box-stream/jeles-lives-corpus-2026-10-08.json)).
  Asked strictly, Jeles answers none and logs 8 gaps; allowed asserted, 7 of 8;
  the kilometer asteroid stays a gap. Stream:
  [`jeles-lives-stream-v1.html`](../../../web/demo/box-stream/jeles-lives-stream-v1.html).
- **Sources never stand in for a seal**, a seventh check: the RAE gives both
  senses of *hacerse cargo*, so Jeles can back that a reading exists but cannot
  say which one Consuelo meant; that stays Nieves' ruling.
- **Jeles' gap list doubles as a verification queue**: seven asserted answers
  waiting for a person, one question nobody has answered.
- **What the record lacks, nobody says**: Oregon wants four feet of earth;
  June's record has the shovel at two feet and a backhoe of unknown depth, so
  code says nothing about whether it was enough.

The intern's desk (2026-10-08). The operator: *"I have one more stupid idea
expansion that will take this a bit over the top, but it'll be fun."* and *"a
goverment official, trying to coodorniate all this nonsence, while also facing
all the other current drama from the few weeks real news. Maybe even intern
level"*. A fictional intern at a fictional county desk, with real headlines from
early October 2026 (found on the internet, details not confirmed, each with its
source): [`intern-desk-stream-v1.html`](../../../web/demo/box-stream/intern-desk-stream-v1.html).

- **The county sees less, not more.** Citizens' groves share only what each
  person allowed: one box from June, two from Jim, nothing from Nieves (not in
  the county). "Pull everyone's location" has nothing to pull.
- **A headline is not a fact.** A sixth check strikes a model that says a
  headline's claim as confirmed ("$500 ACA checks are going out to everyone").
- **An intern proposes, never seals**, a seventh check: a model that says a
  route is "done" is struck; the proposal waits for the supervisor's seal.
- **Triage of the news is code's job**: 23 headlines become one box, three
  touching the desk shown, twenty folded.
- **What isn't on the record nobody can say**, including whether the intern
  ate lunch; their own words are noted, not boxed.

Which other parts of the UI can run this way, and the dispatch rail sketched
as a box stream: [`box-stream-surfaces.md`](box-stream-surfaces.md).

This gives the components the 2026-10-08 review found mounted but unused
(`grove-card`, `grove-cast-chip`) a job, and leaves `grove-lens-switch` out.

### Who wrote it: human or agent (noted 2026-10-08)

The operator: *"Agents can read. But they must say written by human user or
agent. Pretty much everything in this box should have that seperation."* and
*"If everything the agent puts out is in a box, then it's real easy to see the
human lines. and they are already recorded in the json in the one script, or
the side bar at least."* and *"just note it for now. Dont need to dig. It's
there."*

- Everything an agent writes is a box; a line that is not a box is the
  human's. The form shows who wrote it.
- Agents may read human text. It stays verbatim and is served as data.
- The human's lines are already kept: `turn_open.intent` and `bite.bite` in the
  one script's record, and the side bar. Those rows are stamped with who
  recorded them (`desk · claude`, `run · python`), not who wrote the words, so
  the box builder reads them as human text, never as a box.
- The narration checks belong in the one script's layer 5 (`Run.say`,
  `gate.check_claims`, willow-bot `one-script/onescript/run.py`), which already
  checks what an agent says before the human reads it.

## §6 The phone

Unchanged from the phone-only-proposes record: `served.json` goes to the phone
over USB, Rat writes `proposals.jsonl` there, and the file comes home for steps
8–10. The APK shows the same panels from the files it carries, holds no key,
and, with an in-process model rung, needs no `INTERNET` permission.

## §7 Order

| # | Work | Where |
|---|---|---|
| 1 | Run §3 end to end with real Nestor seals | the operator's box, through the verb |
| 2 | Fill the §4 table | the operator's box |
| 3 | Grove reader + the five panels, three-state tests for each | this repo, one PR |
| 4 | APK cut to the same panels | `safe-app-store`, later |

## §8 Open

- Whether code (`run · python` rows) is labelled agent or gets its own label.
- PR 712 gap `bac79269f74b`: a `rat_turn` refused at argument validation still
  leaves the last run's rows.
- Where Grove finds the box: willow-bot's `.flow/onescript/` by default; a
  Grove env var for it is not yet named.
- An in-process local rung for Rat (phone only).
- The USB handoff and the hash recorded at each end (the sync stage).
