# Proposal — Grove's hooks and skills are a derived flowchart, not a hook layer

**Status:** proposed · drafted by willow 2026-09-02, from a working conversation with the operator · **willows-grove tracked hooks, one projects.json entry, one Nestor deposit** · root ratifies
**Build order:** 2 of 6 — see [`2026-09-02-build-order.md`](2026-09-02-build-order.md)
**First constraint (pending seal, see §0):** *an index the fleet depends on is derived from the trees, never maintained by hand.*
**Companions:** [`2026-09-02-packet-lifecycle-adr.md`](2026-09-02-packet-lifecycle-adr.md) (the exit the flowchart hands to), [`2026-09-02-local-inference-seam.md`](2026-09-02-local-inference-seam.md) (the leaves), [`2026-09-02-mcp-jobs-ladder-test-plan.md`](2026-09-02-mcp-jobs-ladder-test-plan.md) (which model runs a leaf), [`2026-09-02-unit-retirement.md`](2026-09-02-unit-retirement.md) (what the timers used to do).
**Design sources:** [`docs/design/the-forge-shape.md`](../../docs/design/the-forge-shape.md) §2, §3, §6, §9, §11, §12; Nestor `hooks/wiring.json` and `hooks/reinject.py`; willow-mcp `docs/design/hooks-and-skills.md` and `docs/PROJECT-WIRING.md`.

---

## 0. The constraint, and why it comes first

Operator, 2026-09-02, on Willow 1.4 or 1.5:

> I tried an index db across the repos, to hold what was in each repo, to
> try to keep track of what was in each, so the model could find it. Being
> very inexperienced in what a complex system that took to keep track of
> was, I might have quit then, and there would have never been a willow-mcp.

The index was right and the maintenance was impossible. The box has since
built the same index three ways and two of them work: the code graph
(derived from the tree, rebuilt on demand) and Nestor's corpus (pinned to a
commit, refreshed by a script that refuses a dirty tree). The third, the
knowledge base and SOIL, is maintained by hand and shows it.

So the rule this proposal is built on, put to Nestor as a decision pair:

```
source:  Where does an index the fleet depends on come from?
target:  Derived from the trees, never maintained by hand. A hand-kept index
         is wrong from the moment it is written and keeping it right is a job
         nobody has; that is why the 1.4 cross-repo index failed and why the
         code graph and the corpus work. Rows may be proposed by a session;
         the table is rebuilt from the repos at every PR.
```

Everything below is shaped so that no file in this proposal is a list
somebody keeps.

## 1. What Grove has, measured

- Generated hooks only. `settings.local.json` and `.cursor/hooks.json` carry
  willow-mcp's SessionStart bridge, PreToolUse guard, and SessionEnd stack
  snapshot. Rendered by `project sync`; gitignored; not Grove's.
- No tracked hooks, no prompt-submit or pre-compact reinject, no stop gate.
- No project skill. The session that drafted this loaded none.
- The only automatic atom writer in the fleet is Grove's own resident
  watcher, and it writes journal entries from Grove traffic, not from
  sessions. Sessions write atoms and edges only when someone remembers.
- Grove has **zero** claims in Nestor's corpus. Its archived predecessor
  holds 693. The Forge-shape doc, which states the design this proposal
  implements, is unfindable by the tool it is about.

Three hook philosophies are live in the fleet: willow-mcp's single guard,
Nestor's twelve modules behind one command in two dialects, and Grove's
nothing. The project-wiring incident measured what happens when two of them
overlap: sixteen hooks per session, four events gated twice.

## 2. The shape

A hook is a truth table. Event and state in, one action out. The model sits
at a leaf, never at a branch. That is the Forge-shape doc's §2 ("the
questions do not drift because they are not generated"), §3 ("a detectable
condition with a scripted response"), and §9 ("make the model's job small
enough that being wrong is cheap and visible"), applied to the session
itself.

Three questions with values, from §12, are the whole contract every event
answers:

1. **Has this been asked?** A step that skipped the corpus left no trace of
   skipping.
2. **Was the answer current?** The corpus age and behind-count travel with
   the answer.
3. **Did the result come back?** What was built, whether it passed, what
   connected.

An advisory answers none of these. A value can be checked.

### Events are fixed by the IDE

Session start, prompt submit, pre-compact, pre-tool-use (shell, write, MCP),
stop, session end. Nestor's manifest names exactly these. Grove adds none.

### States are fixed by readers that already exist

| State | Reader | Values |
|---|---|---|
| seam reach | Grove readers per INVARIANTS §1 | populated, empty, unreachable |
| packet | `dispatch_list` for the seat | none, pending, working, complete, verified, returned, failed |
| envelope | `envelope_list` against the enforced registry | active, expired, absent |
| corpus age | `corpus_snapshots.consolidated_at` and `refresh.py --dry-run` | fresh, behind by N, never |
| attestation | `session_enter` orientation | armed, missing, expired |
| unit manifest | live unit list against the five that belong | conformant, drift |
| model rung | `rungs.json` from the ladder | measured, corpus-only, none |
| port ownership | live socket table, each listener put to `nestor check` against a sealed `port` domain, **numeric matcher, zero tolerance** (under the string matcher 8766 scores 0.75 against 8765; a port off by one is a different server, never a near match) | matches, held by another, unsealed listener |

The port table, as decided 2026-09-02 (operator: *"serve is not as important
right now as the signing"*), proposed to the keep store as draft pairs in
domain `port` → `owner` and awaiting seal:

| port | owner | why |
|---|---|---|
| 8765 | Nestor UI, keep store, keyring | the operator's browser verifier key is origin-bound here; signing outranks serve |
| 8766 | Grove desk page | loopback only, sealed D4, never tunnelled |
| 8767 | Grove MCP `--serve` | tunnelled as its own resource |
| 8768 | willow-mcp `--serve` | moved off 8765 for the above; KB 2026B306 tier 2 says Pangolin terminates at 8765, so the remote seat is re-ratified against this row or serve returns when the key's origin is fixed (gap `d8b0bea7e205`) |
| 11434 | Ollama | loopback, the local runtime |
| 18789 | OpenClaw gateway | not fleet; recorded so the check does not report it as unsealed |

The port row is the operator's 2026-09-02 finding made a reader: a
"portless" system still runs five servers, the map lived in four prose
places, and nothing compared the live box to any of them. `nestor check`
already verifies a figure against its sealed baseline; a port is a figure.
The map is sealed once by a person, the socket table is read every boot,
and the two disagreeing is one line at session start. Gap `d8b0bea7e205`
carries the first re-ratification this row will report on.

Every value is a reader's output. None is a field someone sets.

### Actions are Python that already runs

Print orientation. Refuse a tool call. Inject three lines. Refuse a turn.
Write a journal entry. Propose a Nestor pair. Post to `#alerts`. Call a
harnessed local model. Nothing new is written for the flowchart itself.

### Rows are pairs with provenance

A row is `(event, state) → action`, with the reason and the session that
proposed it. That is a decision pair. It lives where decisions live, per
project, in Grove's own Nestor, in the connection layer the Forge-shape doc
§6 measured at zero rows. The flowchart is the first thing that goes in.

**The rows are not in this document.** Inventing them here would make the
table prose again. The operator holds the list; §6 says how it lands.

## 3. The four actions Grove carries, tracked

Nestor's shape: `hooks/wiring.json`, one command `hooks/grove-hook <client>
<action>`, two dialects, silence on allow. Declared `claude_hooks: "tracked"`
with `hook_manifest` in the projects registry so `project sync` renders
permissions and env and **no hooks**, and `project audit` reports drift.
That is the fix the wiring doc prescribes and Nestor already runs.

| Event | Action | Cost | What it answers |
|---|---|---|---|
| session start | **orient**: seat, Watch state per reader, packet state, corpus age, unit manifest check, attestation | expensive, once | 1 and 2 at boot |
| prompt submit, pre-compact | **reinject**: three lines. The seat rule. Where decisions go. The check command. | deterministic, every turn | keeps 1 alive under compaction |
| stop | **gate**: refuse a turn claiming done with no evidence token; block once, then advisory | cheap | 3, per turn |
| session end | **deposit**: journal the session's decisions and edges through `kb_journal`; propose unsealed pairs to the project Nestor; write the stack snapshot | bounded, once | 3, per session |

### Nestor first, when installed

Operator, 2026-09-02, restating the Forge-shape §11 rule for Grove: the
same hook the Forge carries lands here, *"always Nestor first, MCP first
when installed."* Not available, first. So the prompt-submit action gains a
row ahead of the reinject:

| State read | Action | What the voice gets |
|---|---|---|
| Nestor reachable (its MCP server answers `nestor_prefs`) | put the prompt to `nestor_ask`, and to the corpus when `--corpus-dir` is set; carry the corpus age | the state (sealed, draft, pending) and the age, as attributed context ahead of the turn |
| Nestor not installed | nothing, and the orient line says so once | a line at boot: "Nestor is not on this box" |
| Nestor installed, not answering | one line, fail open | "Nestor did not answer; unverified turn" |

"When installed" is the capability-composition chain of KB 2026B306 applied
to the seat's own hooks: if Nestor is installed, it is connected, and being
connected means being asked first. A turn that never asked is a step that
left no trace of being skipped. The answer's age travels with it, per
Forge-shape §12 rule 3, so a stale corpus never converts "nobody asked" into
"the box says no".

Pre-tool-use stays willow-mcp's guard, rendered or tracked but not both.
Grove adds no second gate on shell, write, or MCP. One guard per event.

The **deposit** is the piece the retired daemons were doing on timers. It
moves into the seam every session already crosses, so nothing has to run at
3am against a tree nobody chose.

### The close-out is an offer, not a checklist

Operator, 2026-09-02, on how the voice ends a session:

> Jarvis would not say "what remains on your side, in build order: seal the
> one pair in the Nestor UI, then the retirement command block." They would
> say something like, "the server's open now if you would like to sign
> them." The server would be checked if open, opened if not, prompt to the
> user, would you like to sign now, in a Willow voice. All the deterministic
> workflow we've been talking about.

So the deposit's last rows are the same shape as every other row: read a
state, take the action, and only then let the voice speak, once.

| State read | Action | What the voice says |
|---|---|---|
| unsealed pairs proposed this session, Nestor UI not serving | start `nestor.ui` against the keep store, loopback | "The store is open if you'd like to sign them." |
| unsealed pairs, UI already serving | nothing | the same line |
| no unsealed pairs | nothing | nothing |
| a retirement or grant block is waiting on the operator's terminal | write it to the desk as a pending act | "One command is waiting on your terminal when you're ready." |

The voice never lists steps. The system has already done every step it is
allowed to do; what is left is the human's act, and the voice names it in
one sentence and stops. A close-out that reads as a to-do list is the seat
doing the human's remembering out loud, which is the thing the deposit
exists to end.

This is also why the model count falls. Every row above is Python: a port
check, a subprocess, a store query, a template. The only place a model
could enter is the sentence, and the sentence is a template too. With
Nestor holding the decisions and the readers holding the state, the
session's close needs no model at all, and most of its middle needs one
small one at a leaf.

## 4. Skills are the seat, and the seat is one file

Nestor's hooks quote from `hooks/seat.md`. Grove's do the same from
`hooks/seat.md` in this repo: the three-state contract, Watch versus Desk,
Heimdallr's `not_do`, and the three questions. The reinject quotes the
governance line from it and flags drift if the file no longer carries the
line verbatim, exactly as Nestor's does.

willow-mcp's seventy-odd bundled skills describe workflows and none fires.
Grove carries one skill file and the hooks carry it into every turn. A
workflow that needs more than three lines is a leaf, not a skill.

## 5. Where the models sit

Grove tends the fleet, so Grove reaches a leaf more often than any seat:

| Leaf | Harness (seam proposal) | Rung (ladder) |
|---|---|---|
| classify a journal entry by domain | the resident watcher's existing prompt, as a harness | shape 2 |
| judge whether a Grove message is a decision worth a pair | `relevance-judge`, demote only | shape 4 |
| group the session's gaps for the deposit | `gap-triage` | shape 4 |
| draft the morning brief for the desk | `summarize-grounded` | shape 5 |

Each leaf is reached by a row. No leaf is reached by a model deciding to
call another model. The branch above every leaf is a table row a person can
read and argue with.

## 6. How rows land, and how they stay derived

1. A session proposes a row the way it proposes any decision: a pair in the
   project Nestor, draft, attributed, with the session id and the reason.
2. The operator seals or rejects with a reopen condition. Rejected rows stay
   as archived precedents, per the envelope-accrual discipline.
3. The tracked `hooks/wiring.json` is **generated** from the sealed rows by
   a script committed under `scripts/`, in the same PR that seals them. The
   test that pins it compares the manifest on disk to the rows in the store
   and fails on drift, the way `test_hook_wiring_sync.py` pins willow-mcp's
   two hook copies.
4. At every PR, the corpus refresh re-extracts Grove and the manifest is
   re-derived. A row that no reader can evaluate anymore, because the reader
   was removed, fails the pin and the PR.

The file in git is an artifact of the store, never the source. Editing it
by hand is the 1.4 mistake, and the test says so in its failure message.

## 7. What this does not do

- **It does not write the rows.** §2. The operator's list, landed through §6.
- **It does not add a guard.** willow-mcp's PreToolUse remains the one gate
  on tool calls. Grove's stop gate gates turns, a different event.
- **It does not block at session end.** A SessionEnd hook cannot block, per
  Nestor's own finding; the deposit warns and flushes.
- **It does not touch the packet.** The stop gate and the deposit hand to
  the packet lifecycle; they do not replace `handoff_write_v4`.
- **It does not run in Kart.** Hooks run in the IDE's harness, as today.

## 8. Verification

1. `project sync` on this repo with `claude_hooks: tracked` renders no hooks
   into `settings.local.json`; `project audit` reports zero drift against
   `hooks/wiring.json`.
2. Session start prints every state in §2's table with a value from its
   reader, or `unreachable` with a reason. Never blank.
3. Reinject output is three lines, byte-stable across a session, and flags
   drift when `hooks/seat.md` is edited under it.
4. The stop gate refuses a synthetic "all tests pass" with no evidence
   token once, then allows on `stop_hook_active`.
5. Session end writes one journal entry per decision surfaced, proposes the
   pairs, and the next `nestor_ask` for one of them returns `draft`, not
   `pending`.
6. The manifest-derivation script is idempotent against the store, and a
   hand edit to `hooks/wiring.json` fails the pin.
7. Grove appears in the corpus with more than zero claims after the first
   refresh that includes it.

## 9. Ratification

Tracked hooks in this repo, one entry change in `$WILLOW_HOME/mcp/projects.json`,
one new Nestor store for Grove's connections, and Grove added to the corpus
roster. The projects.json edit and the corpus roster are operator acts. The
rest is a willow-mcp-shaped build in willows-grove and needs the same narrow
`fs.write` envelope the companion proposals ask for, with this repo's paths
added.

## Provenance

Measured 2026-09-02: hook files by direct read of `.claude/settings.local.json`
and `.cursor/hooks.json`; the projects registry by direct read; Nestor's
manifest and runner by direct read; willow-mcp's hook set and the bundled
skill count by the code graph; Grove's corpus count from the Forge-shape doc
§12 as of 2026-08-30. The 1.4 account is the operator's, this session,
verbatim in §0.

*ΔΣ=42*
