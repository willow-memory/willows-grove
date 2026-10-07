# The one script: proposals from session 2026-10-02

## Start here: the one script, stripped down (2026-10-05)

[`hashing-session-handoff-2026-10-05.md`](hashing-session-handoff-2026-10-05.md)
is an outside pass that saw only the tracked repo. It cuts the one script to
two steps:

1. **Take a picture.** Hash every file and keep the list of paths and hashes.
   One hash over the list is the picture's fingerprint.
2. **Compare.** Same fingerprint means nothing changed; otherwise each file is
   added, removed or changed.

Everything below waits until a real change asks for it, added back one at a
time: explain (every change carries a reason), accept (the new picture becomes
the baseline, chained to the last), seal (the human signs the fingerprint).
The same pass reviews the skeleton: the record chain can be truncated or
rehashed undetected, `h16` keeps 64 bits, and one garbled line crashes boot.
The desk checked those three against `onescript/record.py`, and they hold.
(2026-10-06: the 64-bit hole is closed — `h16` is now `h256`, the full
digest. 2026-10-07: the other two are closed. The tip the human seals is kept
outside the box, in the anchor beside the keys, and check-in hard-closes when
the chain no longer reaches it: rows cut, or rewritten and rehashed. Rows after
the last sealed tip are still open to both, and the CLI has no seal command
yet, so on the box the anchor reads `never`. A garbled line is a break by line
number, never a crash.)
Agent-reported throughout; a proposal, not ratified as a build.

### The two steps already exist: file integrity checkers

*2026-10-05. The operator: "do you recall if there is already a script in the
world that already does what I want, just the simple?" Then: "if we took
tripwire from 1992, would all 4 needed to be added on to make a full package".
The desk's answer is from memory, with no web lookup; treat dates as claims to
verify.*

Picture and compare is a file integrity checker, and the idea predates AI by
decades: Tripwire (1992, Purdue), BSD `mtree` (about 1990), AIDE (1999). None
is on the box (Kart `JLCEV1NJ`: `aide`, `mtree`, `bsdtar`, `hashdeep` and
`tripwire` absent; no package installed). Adding one is an apt install, which
is egress and the operator's act.

**What the 1992 Tripwire already covers, against the handoff's add-backs:**

| Piece | 1992 Tripwire | Still to build |
|---|---|---|
| Picture + compare | has it: a baseline database, and a report of added, removed and changed files | nothing |
| Expected changes (the handoff's open question) | has it: a policy file sets what each path may change, and what to ignore | nothing |
| Attributes beyond content (`snap.py` review, problem 5) | has it: mode, owner, size, inode, timestamps | nothing |
| **1. Explain:** every change carries a reason | no: it reports a change, never why | **all of it** |
| **2. Accept:** the new picture becomes the baseline, chained to the last | half: update mode replaces the baseline and overwrites the old one | the chain: each baseline carries the previous fingerprint |
| **3. Seal:** the human signs the fingerprint | weak: in 1992 the protection was write-protected media; signed databases came with Tripwire 2.x (about 2000), keyed by a passphrase | a seal by the human's key, recorded as a human act |
| 4. Everything else | not its job | stays off until a real change asks for it |

**The catch with 1992 itself:** SHA-256 didn't exist until 2001. The original
Tripwire hashed with MD5, Snefru and CRC, and MD5 is broken. The pre-AI line
is March 2020, not 1992, so any pre-2020 release fits: AIDE (SHA-256), Open
Source Tripwire, or `snap.py` on Python 3.8.2, each checked by its published
hash.

**So the full package is an old checker plus two new pieces:** explain, and a
chained, sealed accept. Those are the two with the human in them.

**`snap.py`, if it's the checker** (desk review of the handoff's script):
- it fails to import on Python 3.8: `dict[str, str]` needs 3.9 or
  `from __future__ import annotations`
- it writes its baseline into the folder it photographs
- it reads each file whole into memory
- one unreadable file stops the run
- it sees content only, not mode or symlinks
- its baseline write isn't atomic

The fixes add about 20 lines, still stdlib only.

### What the box already has, and what that leaves (desk, agent-reported)

*The operator asked "anything else you would like to add?", then said
"please". Each point narrows the job.*

1. **The picture already exists.** `~/Forge/workshop/boxhash/box_hash.py`
   hashed 1,155,461 files (2026-10-03), with resumable batches and a hash per
   batch list. The missing half is the compare. One catch: its shards keep a
   120-character sample of every line's text, which is how secrets reached
   `out/` and `play/`. **A baseline holds hashes only, never content.**
2. **A picture only covers what it could see.** `box_hash.py` ran in Kart, so
   the vault and `~/.cache/huggingface` were never in it. From a sandboxed
   picture, "nothing changed" means "nothing visible changed". **Every
   picture records where it was taken from, and lists the paths it couldn't
   read as unreachable rather than leaving them out** (the three-state rule).
3. **Git already covers the repos.** For tracked files, a commit is the
   picture and `git status` is the compare. The checker is needed only where
   Git isn't: `$WILLOW_HOME`, the venvs, `~/.claude`, the Nest, untracked
   work.
4. **Most explanations already exist.** A change the session made itself
   carries its reason in the record (the PostToolUse pointer, "every write
   adds its own pointer"). Only the unexplained remainder goes to the human,
   as "1 new item needed for authorized user". The same compare gives
   `deep_thought` its "only what's new" cut: the previous screen against the
   new one.

### The stack: hash, one script and the operator's words on top of each other

*2026-10-05, desk session c3d31e6e. The operator: "stack it all up, whatever
from just the hash, one script, human chunks of it", then "put the stack in
the one script doc". The merged-tables method ("what merges, what stands out
when the pile is on top of itself?", next-pile.md) run on the ideas
themselves. Sources: the hashing handoff, this folder (README, workflow.md,
next-pile.md, `onescript/`), the operator's words verbatim, and the flowering
experiment. Agent-reported; a reading, not ratified.*

A ✓ means the source says it. Height is how many sources stack on the row.

| # | Point | Hash handoff | One script | Operator's words | Flowering | Height |
|---|---|---|---|---|---|---|
| 1 | Every thing gets a hash, and the hash is its identity | ✓ fingerprint | ✓ pile pointers carry a hash; a hash check comes before keywords | ✓ "gave each plot it's own hash" | ✓ `link_id`, excerpt ids | **4** |
| 2 | New things cite older hashes, up the list | ✓ hash chain, Merkle | ✓ record chain | ✓ "plot 1 (hash#), plot 2 (hash) up the list" | ✓ a cite is an excerpt id or an earlier `link_id` | **4** |
| 3 | Pointers, not prose | ✓ "a baseline holds hashes only, never content" | ✓ "the pile holds pointers, not the full files" | ✓ "Not the prose, but just the points" | ✓ only `{excerpts, joins[]}` goes into the next call | **4** |
| 4 | Code first, model last | ✓ "Git already does steps 1 and 2" | ✓ "the agent is the last call" | ✓ "It starts when it's need. Ends when the job is done. ESCILATE." | ✓ D0 13/13 (10 against fixture gold, 3 routed against the ruling); ≤ 0.0 cloud per act on 15 counted acts, rubric pending (§13) | **4** |
| 5 | Only a human makes it true | ✓ "the human signs the fingerprint" | ✓ the seal is `COMMIT`; the truth rule | ✓ "by a human that only a human could produce" | ✓ the operator's rubric; "Lets keep the tree", sealed bfe001f7 | **4** |
| 6 | Three states, never collapsed | ✓ a hash per panel payload | ✓ the reachability gate | ✓ INVARIANTS §1 | ✓ the materials check | **4** |
| 7 | Pile it up; what stacks is what matters | ✓ identical records dedupe by hash | ✓ `merge_flows`; mass decides attention | ✓ "what merges, what stands out when the pile is on top of itself?" | — | **3** |
| 8 | The model's job is connections | — | ✓ "flowering on material already gathered" (workflow §2c) | ✓ "Making connection between a group of ideas that a human hasn't seen yet." | ✓ joins, chain depth | **3** |
| 9 | Picture and compare | ✓ `snap.py` | ✓ B2 state check, reverse three-way | ✓ "the simple", Tripwire | — | **3** |
| 10 | A pre-AI foundation | ✓ Python 3.8.2 by checksum | ✓ the VSOCK pre-AI gate | ✓ the operator's idea | — | **3** |
| 11 | The database builds itself | — | ✓ write-ahead log → views → `COMMIT` | ✓ "deterministic postgres that builds itself" | — | **2** |
| 12 | The 3 / 7 / 13 / 23 rollup | — | ✓ auto flags, the ladder | ✓ "grouping the 23's by 3" | — | **2** |
| 13 | Once / session / permanent | — | ✓ `gate.allow` | ✓ "Run Once. Run For session. Run perm." | — | **2** |

**The tallest stacks, read down, are the system in five sentences:**

1. Everything is a hash.
2. Everything new cites the hashes it rests on.
3. Only hashes and pointers move; prose stays where it lives.
4. Code does the work, and the model is called last, only to propose connections.
5. Nothing is true until a human seals it.

**What the overlay connects that no single source does:**

| Overlap | Connection |
|---|---|
| Row 2 on row 5 | The review's worst hole (the record chain can be cut or rehashed, because its tip is stored nowhere) is closed by the tallest stack: the human seals the tip hash at check-out. |
| Row 7 on row 8 | The model never searches for connections. Code stacks the tables; the model looks only at what stands out. |
| Row 3 on the boot | A boot built from rows 1–3 is a list of hashes. This session's `session_enter` returned 173,921 characters. |
| Row 9 on row 2 | Each picture cites the previous fingerprint (the handoff's "accept"), so picture, compare and chain are one mechanism. |

**Thin stacks, still open:** rungs 7 and 17 (the operator's to define);
explain, every change carries a reason (named, not built); T1b chain depth
(the one flowering measure never run); the garbled-line crash in `record.py`
(desk-confirmed, not fixed). `h16` at 64 bits was fixed 2026-10-06 (`h256`).

**Stripped down, the one script is picture, cite, seal.** Everything else is
a view built on those three.

### The security core: the model never sees the box

*2026-10-05, desk session c3d31e6e. The operator: "what is security. It's just
a box that has to be filled out correctly. So if the model never even knows
the Box exists and is never given the opportunity to see any other box except
the one or the ones that it has scope too", then "That's the core of it", then
"add the security core to the one script doc". The readings and prior art
below are agent-reported; the prior art comes from abstracts only. Not
ratified.*

**The core, as one row:** the model is served only the points in its scope,
named by hashes it can't guess, and returns only proposed rows. Code fills
out every box, and the human seals. The model never sees a box, so it has
nothing to fill out wrong.

It needs no new row in the stack. It is what the five tallest rows add up to:

| Stack row | Security consequence |
|---|---|
| 1. Everything is a hash | Scope is a set of hashes |
| 3. Only hashes and pointers move | Serving is choosing which hashes |
| 4. Code first, model last | The model has no hands: no tools, no forms, no doors |
| 5. Only a human makes it true | The seal is the only write |

**Why the machinery shrinks.** MCP tools, the Kart sandbox, envelopes,
leases, hooks and session attestation exist because a model runs things. The
cross-session pile shows the cost: 1,699 waits, 163 + 163 grant churn and 247
refused shell calls (next-pile.md, "The pile on top of itself"). When code
drives, security is no longer "how do we stop the model doing harm with its
tools?" but "what are we willing to show it?"

**What is already in place:**

| Mechanism | Where |
|---|---|
| The model gets only `{excerpts, joins[]}` | flowering §1.3 |
| A cite outside the served pool is `link_fail`: caught by code and sent to flowering (addressed to willow), never accepted as an answer | flowering §13 |
| An act with any uncitable excerpt goes to flowering before any model call | flowering §13 (willow-bot #79) |
| A grant is answered only with the human's seal over exactly `allow:<capability>:<scope>` | next-pile.md, the capability door |

So scope is enforced by the same check that keeps joins honest: a hash the
model was never served is a name it can't know, and the validator catches it
and escalates the act rather than accepting it.

**Shared SOIL.** The operator, the same session: "I don't think were going to
need the shared soil anymore." The reading: each session's B1 store holds its
own record and pile; cross-session lookups are piles merged by hash
(`merge_flows`, a view rebuilt on demand); the one shared thing left is the
seal ledger, append-only and written only by the human.

**Where it can still leak: the content inside a served box.**

| Risk | Example | Answer in this design |
|---|---|---|
| Injection in served text | An excerpt says "ignore your instructions" | The model has no hands; the worst case is a bad proposed row, which stays unverified |
| Inference across boxes | Harmless points that, together, identify a person | Judge scope on the combination, not box by box (the mosaic rule) |
| Guessable hashes | A plain hash of low-entropy content (a PIN, a name) reverses by enumeration | Served ids are keyed (HMAC) or random, never plain content hashes; `h16` at 64 bits was too short (now `h256`, 2026-10-06) |
| The text going to the human | A proposed row worded to talk the human into sealing | The seal stays a human act; the human reads the points, not only the model's sentence |
| Seal substitution | Janus (below): an approval keyed to an attempt was counted for a different proposal, 100 → 1,000,000 | **A seal binds to one hash, never to an attempt or a session** |
| The serving code | A bug serves the wrong box | The real attack surface. Keep it tiny, readable and sealed: the pre-AI foundation (stack row 10) |

**Prior art** (search 2026-10-05, Jeles first, then the web; abstracts only;
open question logged as gap `f8680acc08e6`):

| Piece | Published? | Where |
|---|---|---|
| The model sees only references | Yes | Dual LLM pattern (Willison, 2023); CaMeL (arXiv 2503.18813) |
| Code drives; the model never picks the path | Yes | Blueprint First, Model Second (arXiv 2508.02721) |
| Proposals and approvals in a signed hash chain before anything runs | Yes | Janus (arXiv 2609.38266) |
| Fixed-shape output from the model that touches data | Yes | APPA (arXiv 2607.24625) |
| Trust the architecture, not the model | Yes | LATTICE (Frontiers in AI, 2026) |
| Truth, not just action, made only by a human seal | Not found | Janus gates effects; a human answer is one input among validators |
| Scope chosen by stacking hashed piles | Not found | — |
| The model's only job is proposing connections | Not found | Elsewhere the model still does bounded tasks |
| A pre-AI foundation under the serving code | Not found | — |

The operator, after reading Blueprint First: "The way they were describing
the workflow that they were using. Trying as hard as they could to make it
most of it deterministic, instead of reasoning." The difference the desk
reads (agent-reported): their blueprint is written by an expert before the
first run; here the procedure accumulates from what repeats, offered at the
third ask and sealed by the human.

The papers are in `~/Forge/workshop/papers-agent-security-2026-10-05/`
(outside the repo), with `READING-ORDER.md`.

### Where the reading lands: one script, serve, one hook, one key

*2026-10-05, desk session 019xJcd52XquwTaeZYqKL8QH. The operator, sharing the
reading order: "All good deterministic work, but none of it has come together
in one place", then "Add it". The desk hasn't read the papers; this mapping
is from the operator's descriptions of each and the desk's memory of them.
Agent-reported; not ratified.*

The one place is four pieces. Three are built; serve is the one most of the
reading points at, and isn't.

| Piece | Who | Does | Status |
|---|---|---|---|
| One script | code | builds the tables from the record | skeleton in `onescript/` |
| **Serve** | code | writes only the tables in scope to one file the model reads; a table out of scope isn't named, counted or marked | **first cut** in `onescript/serve.py` (2026-10-07); Q19 and the stack decided, see below |
| One hook | the model | Reads; Writes only if the human allows (`hook.py`, PR 107) | built, not wired |
| One key | the human | sets the scope and seals; nothing is true until then | the vault, handled separately |

| Piece | Reading that shapes it | What it takes |
|---|---|---|
| **One script** | Blueprint First; Anthropic, *Building Effective Agents* | Code picks the path, the model never does: a workflow, not an agent |
| | Kim and Spafford 1994, Tripwire | Picture and compare |
| | in-toto (USENIX 2019); RFC 9162, Certificate Transparency v2 | Each step signs what came in and what went out; an append-only hash log with proofs is the record |
| **Serve** | Willison 2023, the Dual LLM pattern | The model gets references, never the box |
| | Miller, Yee and Shapiro 2003; Miller 2006 | Holding a reference is the permission: the one served file is the model's only reference |
| | CaMeL, CaMeLoT, APPA | Capabilities on data: scope sits on the tables, not on tools |
| **One hook** | Saltzer and Schroeder 1975 | Economy of mechanism (about ten lines of code), fail-safe defaults (unknown tools denied), least privilege (Read only), complete mediation (matcher `*`) |
| | Meta, the Agents Rule of Two | The model holds untrusted input and sensitive data but no actions, so it passes by holding none |
| | LATTICE | No piece both decides and judges: the script decides, the model proposes, the key judges |
| | *Design Patterns* (2506.08837) | The six patterns: which is nearest, and what none of them do (open; the desk hasn't placed it) |
| **One key** | Janus | A seal binds to the bytes, never to the request: post-approval substitution moved an approval from 100 to 1,000,000 |
| | *Observability Gap* | Seal the visible points, not the results |
| **Under all four** | Thompson 1984, *Reflections on Trusting Trust* | The foundation: 3.9.0's source is signature-verified (`foundation/`), the compiler that built it is not |

**What the mapping shows:**

- Serve carries the most reading (Dual LLM, capabilities, CaMeL, the Rule of
  Two) and is the piece not built.
- Janus sets a rule for the key. The hook's `"Write": "ask"` approves a
  request; when the key comes in, the seal covers the exact bytes written, so
  an approval can't be moved to something else.
- What no paper does is still the prior-art table's "Not found" rows: truth
  made only by a human seal, scope chosen by stacking piles, and a pre-AI
  foundation.

### Serve, first cut

*2026-10-07, desk session. The operator: "Let's start working on the serve
chunk from the one script/one box". Agent-built; not sealed. CLAUDE.md
rule 4: the operator ratifies what's below before it's built on.*

`onescript/serve.py` writes one file, `served.json`, and a `serve` row in
the record. What it holds the run to (each line is a test in
`tests/test_serve.py`):

| Rule | From | How |
|---|---|---|
| Only the tables in scope; the rest isn't named, counted or marked | the security core | the file holds `state`, `why` and the scoped tables, nothing else |
| The scope is the human's seal over the exact set | Janus; "a seal binds to one hash" | the subject is `serve:` + one hash over the sorted table ids; a seal over a smaller set covers nothing wider |
| Ids the model can't guess | the security core, guessable hashes | each served id is an HMAC of the table hash under the run's serve key |
| A trust label on every table, with its receipt | four-pieces-join, what one-box adds 1 | `human-sealed` only when the record holds the human's seal over that table's hash, else `untrusted`; a table can't label itself; no receipt, nothing served |
| Fail closed and loud; empty isn't unreachable | four-pieces-join 3; INVARIANTS §1 | no scope or no seal: `empty`, with why; a sealed table that's missing: `unreachable` |
| Every serve is recorded with where | the where gap above | the `serve` row carries `where`, the scope subject, the served ids and the file's hash; the file gets its pile pointer |
| A cite outside the served file is `link_fail` | flowering §13 | `check_cites` |

**Decided 2026-10-07** (the operator: "Accept Q19, yes to the stack, narrow
the hook"):

| Decision | What it changes | Where |
|---|---|---|
| **Q19 accepted.** Reading is open for people; the model reads only what's served | The 10-01 rule ("There is nothing wrong with reading") is about people and the box; the 10-05 core is about what the model is shown. They don't collide | four-pieces-join, the contradiction |
| **The scope is a stack.** Code proposes a stack of piles; the human seals its one hash | `piles(rows, *ws)` groups the record by any of the four W's (exact, nothing judged; a row missing a W is in no pile). A pile's receipt is its group key plus each row's number and hash, checked against the chain before anything is served. `propose(stack, **match)` makes the card: readable names for the human, and the `subject` to seal | `onescript/serve.py` |
| **The hook is narrowed.** Read is allowed on the served file only | `hook.py` allows Read only when the path resolves to `ONESCRIPT_SERVED`; any other path, a link to another file, or no served file set is denied. Write still asks. Still built, not wired (N6) | `hook.py` |

**Still open:**

- **The mosaic rule:** scope judged on the combination. Not built; the
  recommendation on file is that code lists what a stack joins on the card
  and the human judges.
- **The home.** D2 puts serve in willow-bot; it sits beside the skeleton here
  until the operator moves it.
- **The serve key** makes ids and never signs authority, so HMAC can stay.
  The human's seal over the stack is the authority, and that's what becomes
  the passkey when the one key lands. A recommendation, not decided.
- **The where gap** limits the stack: only `write` rows carry a where, so a
  where-pile holds only writes.

### How the tables group: who, what, when, where

*2026-10-06, desk session 019xJcd52XquwTaeZYqKL8QH. The operator, on how the
tables cluster and group: "I think I just saw one of the easiest ways", "the
easiest ones are the easiest ones. The who what when where", then "yes" to
the reading below, and "add it to the one script doc". Agent-reported; not
ratified as a build.*

The four are the facts code can know without judging anything, so grouping
by them is exact matching, not fuzzy clustering. The record already stamps
three of them on every row, and the fourth on writes only
(`onescript/record.py`, `onescript/run.py`):

| W | Field | Groups into |
|---|---|---|
| **Who** | `who`, from the identity the gate verified | everything one seat or person did |
| **What** | `kind`: a write, a door, a seal, an act | everything of one kind: the auto flags' "same kind" axis (next-pile.md) |
| **When** | `ts` from the injected clock on every row; the turn on most | a turn, a session, a day |
| **Where** | `path` on a `write` row and `where` on its pile pointer; **no other row kind carries one** | everything that touched one place: the auto flags' "same subject" thread |

**The gap, found on a second pass (2026-10-06):** only `write` rows say
where. A `door` row records the verdict on a change but not the change's
path, an `act` row (a push) not where it went, and a `seal` row only its
`subject`. Until every `append` carries a `where` (the change's path, the
push's destination, the sealed subject), "who keeps touching this file"
only sees the writes. One field on `Record.append`; not built.

Grouping is a `GROUP BY` on fields that already exist. Each group's key is
hashed, the 3/7/13/23 ladder counts inside it, and pairs of W's are the
clusters:

- **who + where:** who keeps touching this file
- **what + when:** what kinds of thing happen at check-out
- **where + when:** the bike room at 06:27:22

That last one is the Discord ticket (Day 5, "You can't take the average"):
its answer was a when and a where, "Please review footage from 06:27:22".
Nobody judged anything; the timeline already held it.

**Why is the fifth W: code can't write it, but it can stamp where it came
from.** A why is a pointer, never prose, and there are two kinds:

| Kind of why | Already in the record | Code can check it |
|---|---|---|
| a cite: the earlier rows this one rests on | `cites` on `write` and `door` rows ("new things cite older hashes") | the hashes exist, or they don't |
| the human's words: what authorized it | the mandate on an `act` row (layer 7), and `Ratified-by: … "<verbatim>"` on every PR | the quote is on the record, or it isn't |

So a why groups like the other four: by mandate (everything done under one
"Lets PR") or by cite (everything built on one seal). A row with no why,
nothing cited and no mandate, is the "explain" step's hard close (every
change carries a reason; the hashing handoff's first add-back), and it goes
to the human. A why the model proposes ("these connect because …") is its
1%: it cites like everything else and stays unattested until the human
seals it. That's the four pieces again: the script groups by the four W's,
serve hands the model the groups in its scope, and the key answers why.

**Measured: the record has three and a half, the markdown has two.** The operator:
"That's what is written into the md/ tables, pretty regularly."
`scripts/scan/four_ws.py` counts it (stdlib, read only, the same output on
3.9.0 and 3.11). Across the 260 tables under `docs/`, each table is counted
from its cells, then again with what it inherits from the dated italic line
under its headings:

| W | Cells | With heading |
|---|---|---|
| who | 191 (73%) | 196 (75%) |
| what | 48 (18%) | 52 (20%) |
| when | 43 (16%) | 55 (21%) |
| where | 126 (48%) | 126 (48%) |
| all four | 9 (3%) | 12 (4%) |

Who and where are written regularly; when and what mostly aren't, and the
heading barely helps, because few sections carry a dated line. The record
stamps who, what and when on every row because code writes it, and where
on writes (the gap above). So grouping reads the record, not the prose: tables are written from the record, not parsed back
out of it. Two caveats: "who" counts any operator or persona name in a cell,
so it runs high; and "what" counts any seven-plus hex letters, so a word
like "defaced" passes as a commit.

**Matching when the wording isn't exact: the escalation ladder.** The
operator: "all those, with the hash groupings, could be matched, even if the
verbiage wasn't exact (think slm's)"; then "really, the majority of that can
be done with a nomic embedder" (`nomic-embed-text`; the voice-to-text garble
corrected at the operator's word); then "that's just another step on the escalate path";
then "yes, add it to the one script doc". It's the loop's ladder (next-pile.md,
the loop) and `resolve`'s, with rungs fitted to the four W's:

| Rung | Does | Passes up when |
|---|---|---|
| 1. Hash | the W as written is a lookup | no exact match |
| 2. Code | parses **when** (dates, turns) and **where** (paths: resolve, strip `./`) exactly | it doesn't parse |
| 3. Embedder | nearest known canonical **who** or **what** ("the operator", "Sean", "op" → one `who`; "wrote", "saved" → `write`) | below the similarity threshold, or a near-tie |
| 4. Small model | normalizes what's left into the four fields, citing its words | it can't cite, or answers `ESCALATE` |
| 5. Cloud | the same job with bigger context, still citing | the same |
| 6. The human | `ESCALATE` | — |

Every rung answers or passes the row up, and every answer is written back by
the hash of the phrasing, so the next time it stops at rung 1 and nothing
runs. Each rung is cheaper and dumber than the one above it.

- **The embedder can't make anything up.** It only measures closeness to
  canonical values that already exist, so its worst case is matching the
  wrong one, never producing a new value. Code takes when and where because
  embedders are poor at numbers and paths.
- **Deterministic rungs:** a pinned embedder or small model on CPU (fixed
  revision; greedy decoding for the small model) gives the same output for
  the same row (next-pile.md, "pinned small models as deterministic
  functions").
- **Cite or escalate.** Every field above rung 2 points at the words it came
  from; a value with nothing behind it fails, as `link_fail` does in
  flowering, and `ESCALATE` is always valid.
- **The risk is a wrong hit, not a miss** (next-pile.md, "A wrong hit doesn't
  escalate"): a confident match that merges two different things. So the
  threshold is conservative, and near-ties go up a rung instead of being
  guessed.
- **The threshold is the operator's number.** `deep_thought.py` already
  lists it ("the numbers are yours … the similarity threshold"); this is
  where it's used.

**The escalation benchmark already measures rung 4.** It's the classify
shape: fill a structured record from a short note, or `ESCALATE`.
On Day 3 every model's weakest shape was classify or ground. Classify was
the weakest for five of the twelve (Qwen3 235B, Claude Haiku 4.5, Gemma 4
26B, gpt-oss-20b and DeepSeek-R1), at 0.60 to 0.78 on task score
(`posts/day-3.md`). So the small model for this is chosen by its classify
floor, not its average.

### Who wrote it: the model writes markdown, the human doesn't

*2026-10-06, desk session 019xJcd52XquwTaeZYqKL8QH. The operator: "if
everything that goes into that file is markdown, then it's an instant easy
readable cross reference"; "yes, run it on this transcript"; "go through the
last couple of PR is worth of notes. And look at what I have been doing
specifically with markdown testing"; then "yes, add it to the one script
doc". Agent-reported; not ratified as a build.*

**The tell.** In an agent transcript, the human types plain sentences (or
voice-to-text) and the model writes markdown: headings, tables, bold, lists,
backticks. The transcript already says whose turn each text is (`user` or
`assistant`), so markdown against role is a cross-check, and its useful cell
is the one where they disagree.

`scripts/scan/md_split.py` (stdlib, read only, runs on 3.9.0) ran it on this
session's own transcript, 285 texts:

| Role | Source | Markdown | Plain |
|---|---|---|---|
| user | typed | 1 | 93 |
| user | attached file | 2 | 0 |
| user | harness (hook feedback, "Tool loaded.") | 0 | 3 |
| assistant | the model | 104 | 82 |

- **The human's side, markdown: three texts, all model-written.** The
  pasted reading order (from `READING-ORDER.md` in the papers folder), "The
  Median Machine" (smoothed in another session), and the item 7 review file
  (written by a chat session). Every piece of model text that came in
  through the human's hand was caught, and nothing the human typed was.
- **The model's side, plain: short status lines.** Of the first 80 counted,
  39 were "Holding." and 77 were under 200 characters: the one-liners
  before a tool call. Everything substantial the model wrote was markdown.
- It's a tell, not proof (box rule 1c: presence is a label; authority is a
  passkey). A model can be told to write plain, and a person can paste a
  table. The seal stays the proof.

**What the operator has been doing with markdown: shapes a script can
test.** The last few PRs (107, 109, 110) each had to pass four scripts in
Grove's CI before merging, and each tests one fixed markdown shape that
carries W's:

| Shape | Tested by | Carries |
|---|---|---|
| `Ratified-by: <id> — "<verbatim words>"`, the last line of a PR body | `scripts/check_ratification.py` | who and why, in the human's own words |
| `Persona: <key>` trailer on every commit | `scripts/check_persona_provenance.py` | who, on the model's side |
| a `PR N` on every `[Unreleased]` CHANGELOG bullet | `scripts/check_docs_drift.py`, `scripts/check_changelog_bullet.py` | what and where |
| an `INVARIANTS §N` citation resolves to a `## §N — …` heading | `scripts/check_docs_drift.py` | where, as a cite |
| every `## §N` names a test or workflow path that exists | `scripts/check_docs_drift.py` | why the rule holds: its witness |

It's the same idea as `md_split`, done on purpose: the markdown stays
readable to a person and checkable by code, because what matters sits in an
exact place. The human's words always sit in quotes in a known position
(`Ratified-by:`, or "The operator: …"), and everything around them is
labelled as the model's.

**A W is only as regular as what checks it.** That's the `four_ws`
measurement above. The tested shapes come out complete: every merged PR has
a `Ratified-by`, every commit a `Persona:`, every bullet a `PR N`. The
untested shape comes out sparse: the dated italic line that opens a section
("*2026-10-05, desk session …*") is a convention, nothing checks it, and
`four_ws` found when in only 16 to 21% of tables.

**Next, proposed:** a `check_*.py` in the same family. Every new section
under `docs/design/` opens with a dated line that names the session and
quotes the human. Then the markdown carries all four W's for the same reason
the PR bodies do: CI won't merge it without them. Not built.

### The words the documents share

*2026-10-06, desk session 019xJcd52XquwTaeZYqKL8QH. The operator: "Are there
any words in common or phrases in common across any of these documents?",
then "Add please". Counts computed; the reading is agent-reported.*

The pile on top of itself, run on words. `scripts/scan/shared_phrases.py`
(stdlib, read only, the same output on 3.9.0 and 3.11) counts each phrase
once per document across `one-script/` and `one-box/`: 33 documents, the
four constitution-proposal copies counted as one. Links, code, file names
and anything with a digit in it (ids, hashes, dates) are stripped first, so
what's counted is wording.

| Idea | Phrases (documents holding them) |
|---|---|
| Fail closed | "fails closed" (9), "fail closed" (6), "closed and loud" (6), "gate fails closed" (4), "fails closed and loud" (3) |
| The human makes it true | "human seals" (7), "operator's word" (7), "operator's call" (6), "standing grant" (6), "makes it true" (4), "reading is open" (4), "grant is the human's" (3) |
| Check against the record | "against the record" (6), "compared against the record" (3), "check on the assertion" (3) |
| The model's limits | "model never" (6), "gate is the script" (4) |
| How the work moves | "next bite" (8), "still open" (8), "morning screen" (7), "overnight pool" (6) |
| The series' own lines | "the benchmark caught me too" (4), "bugs looked like model behaviour" (4), "hook, one key" (4), "can't take the average" (3) |

**What it shows:**

1. **The most repeated rule is "fail closed and loud", and the stack's five
   sentences leave it out.** The five tallest rows of the stack (above)
   are hash, cite, pointers, code first and model last, and only a human
   seals. Measured by the documents' own words, "fails closed" is held by
   more documents than any phrasing of those five. Whether it's the sixth
   sentence is the operator's call.
2. **The shared phrases are the canonical values.** "Human seals",
   "against the record", "fails closed", "model never": these are the short
   fixed phrases rung 3 of the escalation ladder (the embedder) matches
   variant wordings onto. The documents already have their vocabulary;
   nobody has to invent one.
3. **Some repeats are the desk's habit, not ideas.** "Everything else" (9)
   and "desk session" (9) are the model's own signature phrases, the
   smoothing showing up in the record. They're stripped before grouping,
   not grouped on.

### If the model only writes tables

*2026-10-06, desk session 019xJcd52XquwTaeZYqKL8QH. The operator: "If a model
wrote all of their output as markdown tables. Add that into the docs wear
applicable. And I do mean all. Even prose. They get a box for that, if it can't
fit anywhere else in the current table from the session. Not a next bite, not a
wrap up. Literally anything that does not fit in a box." Agent-reported; not
ratified as a build.*

Take the "who wrote it" signal one step further. If the model enforces the rule
on itself — everything goes into a table, including prose — then "markdown on
the model's side" becomes "table on the model's side", and the 82 plain
one-liners collapse to a small set of structural exceptions (the harness
feedback, the one-word holds). The cross-check gets cleaner, and the
authorship gap widens.

**The rule:** every model output goes into the current session's table if it
fits any column. If it doesn't fit — prose that isn't a finding, a
context note, a planning remark — it gets a catch-all cell in that same row.
The cell is never "to be continued" and never left as free-flowing text
below the table. The session's table is the session.

| Fits | Where it goes |
|---|---|
| A finding (who, what, when, where, why) | The finding's row in the current table |
| A step done | A row with `kind = act` |
| A question to the operator | A row with `kind = ask` |
| Anything else — prose, context, caveat | A `notes` cell on the nearest relevant row; if no row exists yet, a new row `kind = note` |
| Nothing else fits | A `kind = note` row with a `text` cell; the session timestamp on it is its `when` |

**What this changes for the record.** The `md_split` results above show 82
model-side plain texts; with this rule enforced, those compress to three
categories: the one-liners before a tool call (structural, under 30 chars),
the harness-injected holds, and genuine single-word acknowledgements. Every
substantive output is now a table row with a `ts`, a `who`, and a `kind`. The
four W's are on it by construction, not by convention.

**The authorship signal sharpens.** The `md_split.py` cross-check already
catches model text pasted into the human's side (it did in this session). With
the table-only rule, the inverse also holds: plain prose on the model's side
without a structural reason is anomalous. The check now has two cells worth
testing, not one.

**Not a formatting preference.** The rule isn't about aesthetics. It's about
the record. A `notes` cell on a row is a field with a `ts`, a session ID, and
a `who`. Free prose below the table is none of those things. The table-only
rule is the same rule as "every act cites what authorizes it" — the output
isn't real until it's in the record, and the record is tables.

**The harness exception.** The rule covers model output. Harness-injected text
— stop hook feedback, "Tool loaded.", "Holding." — is tracked as `source =
"harness"` in `md_split.py`, separate from `source = "model"`. It's already a
different column in the transcript; the table-only rule doesn't touch it.

**The `where` gap survives.** Even with the rule fully enforced, `kind = note`
rows still don't carry `path` — they're notes, not writes. The gap named above
(only `write` rows have `path`; `door`, `act`, `seal`, and `note` rows don't)
is still there. The table-only rule closes "prose below the table"; it doesn't
close the `where` gap.

## The proposals from 2026-10-02

**Status:** draft proposals for the operator to read, edit and ratify. Nothing
here is built into a runtime or sealed. Assessments marked **agent-reported**
are unattested. This builds on the one-box plan (PR #102), and each proposal
is in its own commit so it can be kept, edited or dropped on its own.

| # | File | The proposal |
|---|---|---|
| 1 | [`workflow.md`](workflow.md), [`workflow-shape.mmd`](workflow-shape.mmd) | The workflow: data point 0, the truth rule, boot (B1–B3 and the hard close), every prompt as a bite, the repetition ladder (1 does it, 2 notices, 3 offers), the resolve ladder (the user's sources first, the model last), loops and the reverse pass, the 3B experiment, "the gate is the script", custom and chained gates |
| 2 | [`next-pile.md`](next-pile.md) | The runtime as one script: seven parts by purpose plus `run`, citing the constitution upward. Also: the stamp (who and standing, stamped at the door, never by the model); every change cites what it touches; reverse's triggers; the script-match check; the four close-time pieces; the overnight pool and the morning screen; what the script can't solve and the one who can; **the four gates the close needed** (tests, toolchain, freshness, reachability), with push as a grant card; and **three more layers**: claims (every checkable statement checked against the record before the human reads it), boundaries (everything crossing an edge classed by provenance and carded) and mandate (every act traced to the human words that authorise it, before it runs) |
| 3 | [`onescript/`](onescript/) | A runnable skeleton of #2: stdlib only, 53 tests. `record` (hash chain, stamp, open/close turns, pointers with provenance), `gate` (identity, citations, seals, grant cards, script match; **layer 5** claims, **layer 6** push cards by provenance, **layer 7** mandate), `resolve`, `predict`, `reverse` (three-way, four verdicts, witnesses by family), `boot` (probes and **the four gates**: tests, toolchain, freshness, reachability), `view` (the morning screen), `run` (`checkin`, `turn`, `act`, `say`, `checkout`). It uses [`scripts/scan/script_match.py`](scripts/scan/script_match.py) |
| — | [`day-3/`](day-3/) | Not a proposal: the source of the published **Day 2** DEV post (despite the folder name), the 55 PRs since Day 0, the post sources, and `predictions.json` (P1 and P2, both ungraded; the desk misread a late-night line as P2's grade, retracted 2026-10-02) |
| — | [`posts/`](posts/) | The **Day 3** DEV post source ("The benchmark caught me too"), its cover prompt, and the Kaggle dataset metadata patch that was applied to `rudi193/escalation-benchmark` |
| — | [`incoming/`](incoming/) | Three outside passes, kept by provenance: an Opus 5 session's six proposals against Draft 0.8 (reachability and staleness), a cold Haiku 4.5 session's three proposals, and a pointer to the operator's paper "Basins, Not Walls". Its README reconciles them with this PR, cross-checked against the record, and says what the one script took from each |
| — | [`deep_thought.py`](deep_thought.py) | Read-only probe that carries the sealed Answer (D1, D2, D9, Q13) and measures the box against it. Prints the morning screen (NEEDS YOU → … → GRADES → CHOICES → QUIET). Stdlib only; needs `WILLOW_HOME`. See next-pile.md § "deep_thought.py". Three improvements after the first run: ledger-join seals, write-kind triage, GRADES |
| 4 | [`constitution-proposal/`](constitution-proposal/) | Ten amendments and a neutral-language pass, built on Draft 0.7. **Brought into `governance/CONSTITUTION.md` as Draft 0.9 on 2026-10-06** with the Opus outside pass, renumbered where 0.8 had taken the number; unratified (see the folder's README) |

**In the skeleton now:** the four gates and the three layers from #2, each
tested against what happened on 2026-10-02. Run for real on the session's box,
the gates reported: `ruff` 0.15.20 on PATH against the pinned 0.16.7; the
constitution proposals built on Draft 0.7 against the law's 0.8; the Forge's
reliability tests unable to run (no `aggregate` here); the system interpreter,
not a venv.

**Taken from the incoming passes:** queue age reported as backpressure;
"enforcement status unknown" when no reconcile is on record; every agreed
claim recorded with `dissent: none recorded`; and a quote checker that reads
prose only. See [`incoming/README.md`](incoming/README.md).

**Not yet:** `run.act` decides and cards; it never performs the act. Keys are
HMAC rather than passkeys. There's no socket or peer check. Mandate rows are
data the human supplies, never read out of their words by the model. It isn't
in willow-bot yet, where D2 (sealed 2026-10-02) homes it.

**Kept local, not in this PR:** the session's map, marks and pile
(`workflow.md` cites `session-flow.md` and `marks.json`). They're built from
the session transcript and local memory, so publishing them is a separate
decision.

## Running the tests

```bash
cd onescript && python3 -m pytest -q tests   # 159 tests (24 capability door, 12 xref, 16 serve, 11 hook)
```

The Grove's CI doesn't collect these (its `testpaths` is `tests/`). ruff lints
and formats them like everything else.

## Running xref

Two hashes per file on arrival (git's blob id, recomputed here from the bytes on
disk, and the system's own SHA-256), then every id, link, `file:line` and commit
SHA checked across the repos. Read-only; same repos at the same commits give the
same bytes. Scope and first run: [`../one-box/research-2026-10-06.md`](../one-box/research-2026-10-06.md) §13.
Serve's home under D2 is willow-bot; serve reads this index, it does not rebuild it.

```bash
python3 -m onescript.xref index --repo ../../../../willows-grove \
    --repo ../../../../willow-bot --repo ../../../../willow-mcp \
    --out /tmp/xref --cache /tmp/xref-cache [--record BOX]
python3 -m onescript.xref slice --index /tmp/xref/index.json \
    --repo ../../../../willows-grove --id Q19 --out q19.txt   # for people (Q19)
```

## Running deep_thought

```bash
WILLOW_HOME=… python3 docs/design/one-script/deep_thought.py        # screen
WILLOW_HOME=… python3 docs/design/one-script/deep_thought.py --json  # rows
```

Read only. Without `WILLOW_HOME` the box probes report `unreachable` rather
than guessing a path. D2 homes the one script in willow-bot; this file sits
here until the operator moves it.
