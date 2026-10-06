# Rules cross table: boxes and branches (2026-10-06)

*Desk session, 2026-10-06. Collected by the agent from the docs and code named
in each row and reported here as found. Nothing here is ratified, and nothing
here changes a rule. Each source still holds its own rule.*

> "This isn't about making everything fit in a box — it's about making a box
> that the user and the system can grow together." (operator, 2026-10-01)

## How to use it

- The grid is 13 × 13: 13 rows (A–M) by 13 columns (1–13), all 169 cells
  filled. The label column and the number row are only there to give every
  cell its address, such as **B3** or **G2**.
- To use a rule, name its address. Each cell is a short label, and the index
  under the grid gives that cell's rule copied from its source, with the file
  and line it came from.
- Once an address is given out it is never renumbered. When the grid needs
  to grow, the new rules go in a second grid.
- Picking cells is up to whoever is in the seat. This table doesn't choose
  any.

## For agents: how to fill this out

### Is there enough context here?

Enough to find any rule and check it against its source line. What's here:

- Every cell has an address, a short label, and an index entry.
- 168 cells carry a rule copied from one file and line in willows-grove,
  willow-mcp or willow-bot, filled by `fill_cells.py` (one regex per cell, so
  the same tree gives the same bytes).
- Every row names its source.

What's still missing:

- Every entry is `unattested`. A script copied it, and nobody has witnessed
  or sealed it.
- Long passages are trimmed at about 420 characters (…). For those, the
  source line is where the rest is.
- G6 is `source silent`: the session branch name comes from the cloud
  harness, not from any file.
- The 57 documents under "Also applicable" were found by title and have not
  been read.
- Row F refers to numbered boxes ("box 2", "box 6") whose list was not found.

"Filling this out" now means closing those gaps: witnessing entries, reading
past the trims, sorting the extra documents into cells, and finding F's list.
It never means changing a rule.

### The entry every filled cell gets

One row in the index, in this shape:

| Cell | Rule | Source | Standing |
|---|---|---|---|
| J5 | The rule in one or two sentences, in the source's own words where it has them. | `repo: path` §section, line N | unattested |

- **Source** is one file and one line or section. If a rule has two sources,
  name both, and say which one is canonical.
- **Standing** is `unattested` when an agent wrote it, `witnessed` when a
  second, independent check agreed, and `sealed` only when the operator seals
  it. No agent writes `witnessed` or `sealed` on its own entry.
- If the source can't be found, can't be read, or doesn't say it, write that
  in the Rule column (`not found`, `unreachable`, `source silent`). Never
  leave the cell blank and never fill it with a guess. This is INVARIANTS §1:
  three states, never collapsed.

### Fixed for every agent

1. **Addresses never move.** Don't renumber, reorder, merge or delete a cell.
   A cell that turns out wrong gets a correction in its entry, and the label
   stays until the operator changes it.
2. **Copy, don't compose.** The rule comes from the source. If the source and
   the label disagree, the source wins, and you flag the label. Don't fix the
   label yourself.
3. **One cell, one source line.** If you can't point to the line, the cell
   isn't filled.
4. **Propose, don't seal.** Every change is a commit on a branch with a
   `Persona:` trailer, and the operator decides whether it merges (G2–G5).
5. **No new rules in this grid.** It's full. A new rule goes in a second grid
   (`rules-cross-table-2`), with addresses that start from N1.
6. **Look in the box first** (C1–C3). The source paths are all local. Don't
   go to the web for anything in this table.
7. **The vault is the operator's key.** Row D describes the box rule. Don't
   read, open or write anything under the vault to fill it.

### Small agents (local models, short context, single-step tools)

Work one cell at a time:

1. Take the next cell that needs work, reading left to right, top to bottom:
   an entry trimmed with …, one marked `source silent` or `not found`, or one
   flagged as the wrong passage.
2. Open only that row's source from "Where each row comes from".
3. Search it for the label's key words. Take the first passage that states
   the rule.
4. Write the entry: copy the passage (trim it to one or two sentences), with
   the path and line number, `unattested`.
5. If nothing matches, write `source silent` and the path you searched. Move
   on, and don't widen the search.
6. Stop after each cell. Your output is one index row and nothing else.

Don't read the "Also applicable" documents, don't touch other cells, and
don't decide whether a rule is right.

### Large agents (frontier models, long context, many tools)

Work one row at a time:

1. Read the row's source in full, plus the row's "Also applicable" documents.
2. Fill every unfilled cell in the row with an entry in the shape above.
3. Check every entry in the row against its source line. Flag any that no
   longer match, or where the regex caught the wrong passage.
4. For each "Also applicable" document, say which cells it bears on, or that
   it bears on none. Move a document that doesn't fit the row to the row it
   does fit, and say why.
5. Where two sources disagree, record both and name the conflict. Don't pick
   a winner, because that's the operator's call.
6. Record anything that belongs in a second grid as a proposal at the end of
   the row. Don't put it in this grid.
7. Row F: look for the numbered box list. If you find it, cite it. If not,
   record where you looked.

A large agent's output is one commit per row, with a summary: cells filled,
cells `source silent`, conflicts found, and documents moved.

## The grid

| | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **A** Box rules | Honest state | Gates fail closed, loud | Presence is a label; authority is a passkey | Reading open, saving guarded | Human seals, system proposes | Willow seat is where the human is | Egress: three keys + click | Portless | Hooks are doors | Auto-merge is a standing grant | Template ships the box | Exceptions declared, never silent | No front end is primary |
| **B** Security core | Model sees only its scope | Code fills, human seals | One hook: Read allow, Write ask | Cite outside the pool is `link_fail` | Mosaic rule | Unguessable ids | Seal binds to one hash | Serving code is the attack surface | Injected text: the model has no hands | Human reads the points, not just the sentence | Only the seal ledger is shared | Model gets only `{excerpts, joins[]}` | Uncitable excerpt → flowering first |
| **C** Look in the box first | Ask Nestor first | Then look in the box | Only then go remote | Silent corpus ≠ absence | Name which tier answered | Record that the box was checked | A skipped step fails loud | Greenfield archive is in the box | `superseded/` is in the box | Retired repos are a shelf | Refused ≠ retired | Rule 1: coverage is all of `~/github` | Rule 2: the PR is the extraction event |
| **D** willow-bot box rule | `WILLOW_HOME`, else `WILLOW_VAULT_BOX` | Blank is unset; `~` expands | Absolute path only | Must already exist | Made only by `provision.sh` | Resolve, never create | Steward state lives in the box | Script key path is in the box | Counters live in the box, not `~/.willow` | Carried-over counter keeps its mode | Carry-over lock held for the whole copy | Unconfigured reads as "not configured" | Every resolver uses the one rule |
| **E** willow-bot box workspace | Persistence | Isolation | Egress by request only | Auditability | Reach unchanged | No runs from GitHub triggers | No long-lived shells | No ambient current venv | No new MCP package or tools | No webhook surface changes | No bot-held tokens (broker only) | Doesn't replace Kart for seats | Model weights stay out (for now) |
| **F** One-script rules | The stamp | Every proposal cites | Reverse re-checks | `view` draws the heading from the stamp | The law = constitution + the user's half | Code checks the cite's form; a witness checks it's true | Unknown law is refused | Amends waits for the seal | Egress without a grant writes a card | Any internal error fails closed | Agent proposals can't ratify themselves | Same box → same bytes | No clock but the enter key |
| **G** Git branches | willow-mcp ruleset | Feature branch + PR | No persona merges alone | Standing grant in first commit | Trailers: `Persona:`, `Ratified-by:` | Session branch name | All commits on the feature branch | Reviewed shell work goes through Kart | Read-only git is fine | `hotfix/`: same rule, faster name | Merge commits are exempt | Release-please exempt on two conditions | Code PRs add a CHANGELOG bullet |
| **H** The tree | One tree, one soil | Grafts splice on | Sapwood → heartwood on seal | Growth before flowering | Model at a leaf | Gate only narrows | Session and bite: one machine, two scales | Entry never refuses on orientation | The Forge imports no fleet code | The flowchart is derived | Cloud is pollination, not metabolism | Pools collect; they aren't oracles | One nutrient policy at the soil |
| **I** The stack | Everything is a hash | New cites older hashes | Pointers, not prose | Code first, model last | Only a human makes it true | Three states, never collapsed | Pile it up; what stacks matters | The model's job is connections | Picture and compare | A pre-AI foundation | The database builds itself | The 3 / 7 / 13 / 23 rollup | Once / session / permanent |
| **J** Invariants | §1 Three-state contract | §2 Supersedes D7 | §3 Doc discipline | §4 Reader/endpoint coverage | §5 Trust order | §6 Manifests describe code | §7 Consent is real, not automatic | §8 Panels read live endpoints | §9 Seed reads real canon | §10 CI proves the invariants | §11 Persona provenance | §12 Ratification | §12 Grandfather (PRs 1–11) |
| **K** Operator decisions | D1 Canonical runtime | D2 Where the chain lives | D3 Home of the socket standard | D4 The browser door | D5 The #101 sealed record | D6 Friction ownership | D7 Forge refusal without Nestor | D8 u2u and the bridge | D9 Second front end | D10 Ingress: no tunnel by default | D11 Grants away from the box | D12 Helper commit persona | Kaggle benchmark comes first |
| **L** One-box phases | 0 Close the holes | 1 The socket standard | 2 Rat gets a door | 3 Front ends: one contract | 4 The lifecycle behind Rat | 5 Nestor behind Rat | 6 Egress: click to grant | 7 Portless | 8 The surface grows per user | 9 The template ships the box | Sequencing: what not to break | Gap pass | The first three bites |
| **M** The ladder and the seven | Rung 1: hash | Rung 2: code | Rung 3: embedder | Rung 4: small model | Rung 5: cloud | Rung 6: the human | boot | predict | record | gate | resolve | view | reverse |

## Where each row comes from

| Row | What it holds | Source |
|---|---|---|
| A | Box rules | `README.md` §0, §9, §10, §15; `session-2026-10-01.md`; CHANGELOG (PR 102) |
| B | Security core | `../one-script/README.md`, the security core |
| C | Look in the box first | `../the-forge-shape.md` §3, §12 |
| D | willow-bot box rule | willow-bot `willow_bot/paths.py`, `tests/test_box_rule.py` |
| E | willow-bot box workspace | `../willow-bot-box-spec.md` §3, §9, §11 |
| F | One-script rules | `../one-script/next-pile.md`, rules and `gate.py` |
| G | Git branches | willow-mcp `CONTRIBUTING.md`, `skills/worktree.md`; `INVARIANTS.md` §3, §11, §12; `CLAUDE.md` 5–6 |
| H | The tree | `../forge-convergence.md` §1, §1.5, §8 |
| I | The stack | `../one-script/README.md`, the stack (rows 1–13) |
| J | Invariants | `../../INVARIANTS.md` §1–§12 |
| K | Operator decisions | `README.md` §2 and §15 (D1–D12); `../one-script/next-pile.md`, constraints |
| L | One-box phases | `README.md` §3–§15 |
| M | The ladder and the seven | `../one-script/README.md` (resolve ladder); `../one-script/next-pile.md` (the seven) |

## Also applicable (shallow pass)

*Found by title and opening lines across willows-grove, willow-mcp and willow-bot (the Willow repo has no commits yet). Not read in full and not folded into the cells: each is a place to look next for that row.*

| Row | Documents |
|---|---|
| A | willows-grove: `docs/design/approval-broker.md` · willows-grove: `docs/design/u2u-security-limits.md` · willow-mcp: `docs/design/egress-request-seam.md` · willow-mcp: `docs/design/consent-toggles.md` · willow-mcp: `skills/consent.md` · willows-grove: `docs/design/one-box/research-2026-10-06.md` · willows-grove: `docs/design/one-box/instruction-files-2026-10-06.md` |
| B | willow-mcp: `docs/design/trust-architecture.md` · willow-mcp: `docs/design/willow-gate-seam.md` · willow-mcp: `docs/design/security-hardening-review-2026-07-08.md` · willow-mcp: `docs/design/deny-tools-completeness-review.md` · willow-bot: `SECURITY_AUDIT.md` |
| C | willow-mcp: `skills/external-guard.md` · willow-mcp: `docs/design/nestor-tool-route.md` · willow-bot: `docs/PRIOR-ART.md` · willows-grove: `governance/LOCAL_GITHUB_LAYOUT.md` |
| D | willow-bot: `INSTALL.md` · willow-bot: `docs/MOVE-STAY-BORROW.md` · willows-grove: `docs/design/vault-home-store.md` |
| E | willow-mcp: `skills/kart-tasks.md` · willow-mcp: `docs/design/kart-lift-spec.md` · willow-mcp: `docs/design/kart-productionization.md` · willows-grove: `deploy/kart-sandbox.md` |
| F | willows-grove: `docs/design/one-script/workflow.md` · willows-grove: `docs/design/one-script/constitution-proposal/README.md` · willow-mcp: `docs/design/bound-receipt-schema.md` · willow-mcp: `docs/design/build-loop-receipts.md` |
| G | willows-grove: `CONTRIBUTING.md` · willow-mcp: `ARCHITECT.md` · willow-mcp: `skills/review.md` · willow-mcp: `skills/tdd.md` · willow-mcp: `docs/design/brokered-push.md` · willow-mcp: `docs/design/fleet-versioning.md` |
| H | willows-grove: `docs/design/the-forge-shape.md` · willows-grove: `governance/proposals/2026-09-02-grove-hooks-and-skills.md` · willow-mcp: `docs/design/hooks-and-skills.md` · willow-mcp: `docs/design/session-lifecycle.md` · willow-mcp: `docs/design/stateless-session-state.md` |
| I | willows-grove: `docs/design/one-script/hashing-session-handoff-2026-10-05.md` · willows-grove: `docs/design/one-script/prompt-arms-2026-10-03.md` |
| J | willows-grove: `governance/CONSTITUTION.md` · willows-grove: `governance/CASEBOOK.md` · willow-mcp: `docs/design/permissions-matrix.md` · willow-mcp: `docs/design/pgp-and-persona.md` |
| K | willows-grove: `docs/design/one-box/review-2026-10-01.md` · willows-grove: `docs/design/forge-convergence.md` · willow-mcp: `docs/design/operator-tier-not-do-review.md` · willow-mcp: `docs/design/human-orchestrator.md` |
| L | willows-grove: `docs/design/one-box/parts-partition.md` · willows-grove: `docs/design/one-box/four-pieces-join.md` · willows-grove: `docs/design/one-box/one-script-join.md` · willows-grove: `docs/design/one-box/sketches.md` · willows-grove: `docs/design/one-box/verify-2026-10-02.md` |
| M | willow-mcp: `skills/orchestrator-routing.md` · willow-mcp: `docs/design/specialist-registry.md` · willows-grove: `governance/proposals/2026-09-02-local-inference-seam.md` · willow-bot: `loki/SPEC.md` |

## Index

*Filled 2026-10-06 by `fill_cells.py` (deterministic: one regex per cell, run against the local clones of willows-grove, willow-mcp and willow-bot). Each Rule is copied from the line named in Source, collapsed to one line and trimmed at about 420 characters (…). Nothing is composed. Standing is `unattested` for every cell: an agent ran the script, and nobody has witnessed or sealed it.*

| Cell | Rule | Source | Standing |
|---|---|---|---|
| A1 | 1. **Honest state.** Populated, empty or unreachable (plus `not_asked` and `unenforced`), never collapsed, always with a reason. | willows-grove: `docs/design/one-box/README.md`:75 | unattested |
| A2 | 1a. **Every gate fails closed, and loud.** | willows-grove: `docs/design/one-box/README.md`:77 | unattested |
| A3 | 1c. **Presence is a label; authority is a passkey.** The model runs as the operator's uid, so a uid alone never unlocks a human-only act (§15). | willows-grove: `docs/design/one-box/README.md`:78 | unattested |
| A4 | 1b. **Reading is open; saving is guarded** (operator, 2026-10-01: "There is nothing wrong with reading. Anyone can read anything all day long, it's just how, and who saves it into their system is what matters."). | willows-grove: `docs/design/one-box/README.md`:80 | unattested |
| A5 | 2. **The human seals; the system only proposes.** | willows-grove: `docs/design/one-box/README.md`:113 | unattested |
| A6 | 3. **The willow seat is wherever the human is.** Helpers, Rat and dispatched seats never hold willow. | willows-grove: `docs/design/one-box/README.md`:114 | unattested |
| A7 | 4. **Egress takes three keys plus the human's click.** | willows-grove: `docs/design/one-box/README.md`:116 | unattested |
| A8 | 5. **Portless.** Helpers talk over Unix sockets, and the kernel knows the peer's uid. | willows-grove: `docs/design/one-box/README.md`:117 | unattested |
| A9 | 6. **Hooks are doors, not verbs.** The front end is a shim; one local runtime decides. | willows-grove: `docs/design/one-box/README.md`:119 | unattested |
| A10 | - **Auto-merge** (operator, 2026-10-01): "I often press the merge button myself. But when I'm comfortable … I will hit Auto merge and walk away." A standing grant is the human's auto-merge: | willows-grove: `docs/design/one-box/README.md`:89 | unattested |
| A11 | The workshop template ships the box, never a tree. | willows-grove: `docs/design/one-box/README.md`:129 | unattested |
| A12 | The box rule then reads: *one browser door, signed actions, everything else UDS; exceptions are declared, never silent.* | willows-grove: `docs/design/one-box/README.md`:562 | unattested |
| A13 | **No front end is primary** (operator, 2026-10-01: "Don't code for claude exclusively … this is supposed to be able to be run on anything."). | willows-grove: `docs/design/one-box/README.md`:386 | unattested |
| B1 | **The core, as one row:** the model is served only the points in its scope, named by hashes it can't guess, and returns only proposed rows. | willows-grove: `docs/design/one-script/README.md`:159 | unattested |
| B2 | Code fills out every box, and the human seals. | willows-grove: `docs/design/one-script/README.md`:160 | unattested |
| B3 | POLICY = {"Read": "allow", "Write": "ask"} | willows-grove: `docs/design/one-script/next-pile.md`:1305 | unattested |
| B4 | A cite outside the served pool is `link_fail`: caught by code and sent to flowering (addressed to willow), never accepted as an answer — flowering §13 | willows-grove: `docs/design/one-script/README.md`:185 | unattested |
| B5 | Inference across boxes — Harmless points that, together, identify a person — Judge scope on the combination, not box by box (the mosaic rule) | willows-grove: `docs/design/one-script/README.md`:204 | unattested |
| B6 | Guessable hashes — A plain hash of low-entropy content (a PIN, a name) reverses by enumeration — Served ids are keyed (HMAC) or random, never plain content hashes; `h16` at 64 bits was too short (now `h256`, 2026-10-06) | willows-grove: `docs/design/one-script/README.md`:205 | unattested |
| B7 | Seal substitution — Janus (below): an approval keyed to an attempt was counted for a different proposal, 100 → 1,000,000 — **A seal binds to one hash, never to an attempt or a session** | willows-grove: `docs/design/one-script/README.md`:207 | unattested |
| B8 | The serving code — A bug serves the wrong box — The real attack surface. Keep it tiny, readable and sealed: the pre-AI foundation (stack row 10) | willows-grove: `docs/design/one-script/README.md`:208 | unattested |
| B9 | Injection in served text — An excerpt says "ignore your instructions" — The model has no hands; the worst case is a bad proposed row, which stays unverified | willows-grove: `docs/design/one-script/README.md`:203 | unattested |
| B10 | The text going to the human — A proposed row worded to talk the human into sealing — The seal stays a human act; the human reads the points, not only the model's sentence | willows-grove: `docs/design/one-script/README.md`:206 | unattested |
| B11 | The operator, the same session: "I don't think were going to need the shared soil anymore." The reading: each session's B1 store holds its own record and pile; cross-session lookups are piles merged by hash (`merge_flows`, a view rebuilt on demand); the one shared thing left is the seal ledger, append-only and written only by the human. | willows-grove: `docs/design/one-script/README.md`:196 | unattested |
| B12 | The model gets only `{excerpts, joins[]}` — flowering §1.3 | willows-grove: `docs/design/one-script/README.md`:184 | unattested |
| B13 | An act with any uncitable excerpt goes to flowering before any model call — flowering §13 (willow-bot #79) | willows-grove: `docs/design/one-script/README.md`:186 | unattested |
| C1 | 1. **Ask Nestor.** If the corpus answers, stop. | willows-grove: `docs/design/the-forge-shape.md`:129 | unattested |
| C2 | 2. **Look in the box** — including archives, greenfield, `superseded/`, anything retired. Retired is not gone; it is a different shelf. | willows-grove: `docs/design/the-forge-shape.md`:130 | unattested |
| C3 | 3. **Only then go remote**, and say why the first two did not answer. | willows-grove: `docs/design/the-forge-shape.md`:132 | unattested |
| C4 | **A silent corpus is not proof of absence, it is proof nobody extracted.** | willows-grove: `docs/design/the-forge-shape.md`:139 | unattested |
| C5 | The entry scan (§3) already asks the corpus; the tier-2 step is a second, cheap, local lookup before any network call, and it fails the same way — loudly, naming which tier answered. | willows-grove: `docs/design/the-forge-shape.md`:147 | unattested |
| C6 | A build that reaches the network without recording that the box was checked has skipped a step and left no trace of the skip, which is §11's rule again in a different place. | willows-grove: `docs/design/the-forge-shape.md`:148 | unattested |
| C7 | For the Forge this is a hook, not a habit. | willows-grove: `docs/design/the-forge-shape.md`:145 | unattested |
| C8 | The second tier is the one that was missing, and it is where the volume is: the greenfield archive holds two dozen retired repositories — `willow-1.9`, `willow-canonical`, `willow-compose`, `willow-nest`, `willow-tech-manual`, `safe-design`, `jeles-remote` — none of them in the corpus. | willows-grove: `docs/design/the-forge-shape.md`:135 | unattested |
| C9 | Archived, not deleted (CLAUDE.md §4). A map that was accurate on its date stays useful as evidence of what the box looked like then; what it must not do is sit beside the current one with nothing saying which is which. | willows-grove: `governance/architecture/superseded/README.md`:3 | unattested |
| C10 | Retired is not gone; it is a different shelf. | willows-grove: `docs/design/the-forge-shape.md`:131 | unattested |
| C11 | That is the same distinction the refresh driver already draws between *refused* and *retired*, applied one level up: at the moment Nestor returned zero for "ratatosk", the correct reading was *the corpus was never given the legacy monolith* — not *ratatosk does not exist*. | willows-grove: `docs/design/the-forge-shape.md`:140 | unattested |
| C12 | Rule 1 — coverage: everything under `~/github` | willows-grove: `docs/design/the-forge-shape.md`:568 | unattested |
| C13 | Not a nightly cron. The PR, and the reasons are structural rather than preferential: | willows-grove: `docs/design/the-forge-shape.md`:615 | unattested |
| D1 | def willow_home() -> Path: """Root data directory for willow-bot state: the box (`$WILLOW_HOME`, else `$WILLOW_VAULT_BOX`). Raises `BoxNotConfigured` when neither is set — never a guessed path. | willow-bot: `willow_bot/paths.py`:68 | unattested |
| D2 | A blank env is treated as unset (whitespace-only counts as blank); `~` in the value is expanded. | willow-bot: `willow_bot/paths.py`:72 | unattested |
| D3 | A relative box moves with the working directory: under a unit that is the checkout. Not a box (Loki 757108E8). | willow-bot: `willow_bot/paths.py`:55 | unattested |
| D4 | A named box that does not exist is refused too (Loki A726C6F8): the first write would otherwise create a whole bogus tree, and every read would report "empty" when the truth is "no box".""" for name in names or BOX_ENV: raw = os.environ.get(name, "").strip() if raw: box = Path(raw).expanduser() if not box.is_absolute(): | willow-bot: `willow_bot/paths.py`:47 | unattested |
| D5 | f"{name}={box} is not an existing directory; the box is created by " "willow-data-vault's bootstrap/provision.sh, never by willow-bot." | willow-bot: `willow_bot/paths.py`:60 | unattested |
| D6 | Callers must not pass this Path to a write without first ensuring its parent tree exists — this function computes a path, it does not create one. | willow-bot: `willow_bot/paths.py`:74 | unattested |
| D7 | def test_state_path_is_in_the_box(tmp_path): assert _real_state_path() == tmp_path / "loki_pr_watch_state.json" | willow-bot: `tests/test_box_rule.py`:34 | unattested |
| D8 | def test_script_key_path_is_the_box_never_dot_willow(monkeypatch, tmp_path, name): | willow-bot: `tests/test_box_rule.py`:85 | unattested |
| D9 | The counter lives in the box (willow_bot.persona_store), not ~/.willow. Every function takes an explicit path for tests; None means the box. | willow-bot: `sigh.py`:7 | unattested |
| D10 | def test_a_carried_over_counter_has_the_mode_a_fresh_one_gets(monkeypatch, tmp_path): | willow-bot: `tests/test_box_rule.py`:144 | unattested |
| D11 | def test_the_lock_is_held_for_the_whole_copy(monkeypatch, tmp_path): | willow-bot: `tests/test_box_rule.py`:155 | unattested |
| D12 | class BoxNotConfigured(RuntimeError): """Neither ``WILLOW_HOME`` nor ``WILLOW_VAULT_BOX`` names the box. A ``RuntimeError`` so callers that already treat an unconfigured App as "not configured" (``github_app._configured``) keep doing so.""" | willow-bot: `willow_bot/paths.py`:28 | unattested |
| D13 | The one rule every box resolver in this repo uses. | willow-bot: `willow_bot/paths.py`:46 | unattested |
| E1 | 1. **Persistence** — Box contents survive bot process restarts; they live under `bot_dir()` (§5), not the git checkout. | willows-grove: `docs/design/willow-bot-box-spec.md`:83 | unattested |
| E2 | 2. **Isolation** — Every execution uses existing Kart / forge-play / kartikeya bubblewrap paths (§6). No parallel “trust the bot uid” runner for untrusted code. | willows-grove: `docs/design/willow-bot-box-spec.md`:84 | unattested |
| E3 | 3. **Egress** — Any network use (including `pip install`) is **request-only**. The bot never self-grants: same three-key / consent / lease / envelope stack as `task_submit` (`willow-mcp` tests: `test_task_submit_allow_net_*`). Lane A (§6.1) has **no net**; lane B must pass the gate. | willows-grove: `docs/design/willow-bot-box-spec.md`:85 | unattested |
| E4 | 4. **Auditability** — Each `run_in_venv` produces a stable `Result` (§4) suitable for logs, JSONL pools, and replay; side effects are listed in `artifacts` or gated installs. | willows-grove: `docs/design/willow-bot-box-spec.md`:86 | unattested |
| E5 | 5. **Reach unchanged** — No new top-level MCP server, no new Willow discovery path. New capability appears only when existing tools (steward heartbeat, deterministic socket ops, future internal hooks) invoke the box API. | willows-grove: `docs/design/willow-bot-box-spec.md`:87 | unattested |
| E6 | 4. **#69** — Confirm no box execution from GitHub-triggered paths until contributor policy is sealed. | willows-grove: `docs/design/willow-bot-box-spec.md`:321 | unattested |
| E7 | - Long-lived interactive shells / PTYs | willows-grove: `docs/design/willow-bot-box-spec.md`:259 | unattested |
| E8 | - Ambient “current venv” session state across calls | willows-grove: `docs/design/willow-bot-box-spec.md`:260 | unattested |
| E9 | - New MCP package or new `willow-mcp` tools (optional: enrich steward `status` JSON only) | willows-grove: `docs/design/willow-bot-box-spec.md`:261 | unattested |
| E10 | - Changes to GitHub App webhook surface or #69 “troll” behavior | willows-grove: `docs/design/willow-bot-box-spec.md`:262 | unattested |
| E11 | - Bot-held GitHub tokens or SSH credentials (broker only) | willows-grove: `docs/design/willow-bot-box-spec.md`:263 | unattested |
| E12 | - Replacing Kart for **seat** `task_submit` workloads | willows-grove: `docs/design/willow-bot-box-spec.md`:264 | unattested |
| E13 | - Moving Ollama weights into `box/` (horizon noted in `INSTALL.md`; separate slice) | willows-grove: `docs/design/willow-bot-box-spec.md`:265 | unattested |
| F1 | **1. The stamp (operator).** Every output is stamped at the OUT door by `record`. The model doesn't write the stamp. | willows-grove: `docs/design/one-script/next-pile.md`:44 | unattested |
| F2 | **2. Every proposal cites what it touches (operator).** A proposal is PR-*shaped*, not a GitHub PR: any change to the box. | willows-grove: `docs/design/one-script/next-pile.md`:56 | unattested |
| F3 | **3. Reverse runs on three triggers** (a fourth, the script's own version changing, is added below). | willows-grove: `docs/design/one-script/next-pile.md`:66 | unattested |
| F4 | `view` draws the heading from the stamp ("What this shows (hanuman, unattested):"). | willows-grove: `docs/design/one-script/next-pile.md`:53 | unattested |
| F5 | - "The law" is the fixed half (the Constitution) **plus** the user's own half: standing grants, precedents, sealed rows. | willows-grove: `docs/design/one-script/next-pile.md`:59 | unattested |
| F6 | - Python checks that the citation exists, is well formed, and matches what the change touches. Only a witness checks that it's *true*. | willows-grove: `docs/design/one-script/next-pile.md`:63 | unattested |
| F7 | Unknown law is refused. | willows-grove: `docs/design/one-script/next-pile.md`:282 | unattested |
| F8 | Amends waits for the seal. | willows-grove: `docs/design/one-script/next-pile.md`:282 | unattested |
| F9 | Egress without a grant writes a grant card. | willows-grove: `docs/design/one-script/next-pile.md`:282 | unattested |
| F10 | Any internal error fails closed. \| | willows-grove: `docs/design/one-script/next-pile.md`:282 | unattested |
| F11 | - §0.2: the agent proposed all of this, so it can't count toward ratifying it. | willows-grove: `docs/design/one-script/next-pile.md`:247 | unattested |
| F12 | Same box → same bytes. | willows-grove: `docs/design/one-script/next-pile.md`:306 | unattested |
| F13 | **Desk, in one line:** keywords group into flags at the bottom, clusters predict the next ask at the top, and the enter key is the only clock between them. | willows-grove: `docs/design/one-script/next-pile.md`:895 | unattested |
| G1 | `master` is protected by a **no-bypass ruleset**: all changes land through a pull request with a green `test` check. Direct pushes to `master` are rejected. | willow-mcp: `CONTRIBUTING.md`:51 | unattested |
| G2 | @constraint severity=critical Every change goes through a feature branch and a pull request. Direct commits to `master` / `main` are banned — no exceptions, including "quick fixes." | willow-mcp: `skills/worktree.md`:129 | unattested |
| G3 | No fleet persona has unilateral authority to open a pull request, merge a pull request, or push to master — not Heimdallr, not Hanuman, not Loki, not even Willow. | willows-grove: `docs/INVARIANTS.md`:466 | unattested |
| G4 | - **Standing authorizations** may cover a defined scope of work (e.g. "run it, keep the reorder" covering the 13-PR v0.9 plan's in-branch commits). A standing authorization must be recorded once in the branch's first substantive commit under its scope, with a `Ratified-by:` trailer citing the verbatim standing quote; every subsequent in-branch commit under that scope inherits it. | willows-grove: `docs/INVARIANTS.md`:500 | unattested |
| G5 | 6. **Persona provenance and ratification are enforced, not aspirational.** Every commit that changes tracked code — including `.md`, which is tracked code under §3 — carries a `Persona:` trailer whose value is a key from `governance/fleet_personas.json`, verbatim and lowercase. Merge commits are exempt; release-please's own release commit is exempt on a bounded pair (author `willow-ci[bot]` AND subject … | willows-grove: `CLAUDE.md`:95 | unattested |
| G6 | *source silent: no file in the repos holds this; it comes from the cloud session's harness.* | — | unattested |
| G7 | - All commits on the feature branch only. | willow-mcp: `skills/worktree.md`:53 | unattested |
| G8 | - Shell mutations that need review → `task_submit` (Kart), not ad-hoc agent Bash, when the repo policy requires it. | willow-mcp: `skills/worktree.md`:54 | unattested |
| G9 | - Read-only git/gh on the operator desk is fine: `git status`, `git log`, `git diff`, `gh pr view`, `gh pr list`. | willow-mcp: `skills/worktree.md`:56 | unattested |
| G10 | - Urgent work gets a `hotfix/<slug>` branch — same rule, faster name. | willow-mcp: `skills/worktree.md`:124 | unattested |
| G11 | Merge commits are exempt (they carry no work, only structure); commits that only touch untracked files (worktree scaffolding, etc.) are exempt by nature. | willows-grove: `docs/INVARIANTS.md`:407 | unattested |
| G12 | Both axes must match; a PR meeting only one still owes §12 its signature. | willows-grove: `docs/INVARIANTS.md`:521 | unattested |
| G13 | - Every code-changing PR appends a bullet to `CHANGELOG.md`'s `[Unreleased]` section under `### Changed`, `### Added`, `### Fixed`, or `### Removed`, per Keep a Changelog v1.1.0. | willows-grove: `docs/INVARIANTS.md`:125 | unattested |
| H1 | **Willow (human + orchestrator seat)** is the trunk — one `app_id`, one filing namespace, one gate registration target (§9 row 5). | willows-grove: `docs/design/forge-convergence.md`:102 | unattested |
| H2 | **Grafts** are other repos and fleet apps (Hanuman checkout, Forge `forge-engine`, workshops, federated MCPs): they splice on with their own manifests and stores, but they do not get a second soil for the operator tree unless federation or promotion explicitly says so. | willows-grove: `docs/design/forge-convergence.md`:104 | unattested |
| H3 | Nothing crosses that boundary unsigned (§5). | willows-grove: `docs/design/forge-convergence.md`:112 | unattested |
| H4 | - **Growth before flowering.** Collection pools and local *x*→*y* joins carry routine work; cloud and fleet dispatch are for buds that pools cannot close, or acts the operator places above the flowering threshold (§1.5, §6 **0**). | willows-grove: `docs/design/forge-convergence.md`:712 | unattested |
| H5 | The model sits at a leaf, never at a branch." The Forge's entry says the same thing about a build: "The model is never consulted: the scan is a regex over a table, the routing is memory." Both rules come from `the-forge-shape.md` §2, §3 and §9. | willows-grove: `docs/design/forge-convergence.md`:59 | unattested |
| H6 | - **The gate only narrows.** Effective access is willow-mcp's manifest intersected with the tier ceiling (willow-gate README, "embedders must not inherit that"). | willows-grove: `docs/design/forge-convergence.md`:702 | unattested |
| H7 | A session and a Forge bite are the same machine at two scales. | willows-grove: `docs/design/forge-convergence.md`:56 | unattested |
| H8 | - **Session entry never refuses on an orientation source.** A source that cannot be read is a state in the report. willow-mcp's orientation already keeps this ("Orientation is sugar. It must never be the reason entry fails."). The Forge's bite refusal without Nestor stays, for bites: two doors, two rules. | willows-grove: `docs/design/forge-convergence.md`:695 | unattested |
| H9 | - **The Forge never imports willow-mcp or Grove.** Everything here is the fleet calling the Forge, or a Forge type the fleet imports. | willows-grove: `docs/design/forge-convergence.md`:700 | unattested |
| H10 | - **The flowchart is derived.** Rows live in the store; every host's wiring is generated from them, and a hand edit fails a pin (hooks proposal §0 and §6). | willows-grove: `docs/design/forge-convergence.md`:709 | unattested |
| H11 | Cloud models are not daily metabolism; they are optional pollination when the pools and local joins cannot close the bud. | willows-grove: `docs/design/forge-convergence.md`:90 | unattested |
| H12 | **Collection pools (accumulators, not oracles).** | willows-grove: `docs/design/forge-convergence.md`:122 | unattested |
| H13 | 6 — One nutrient policy at the soil interface (willow-gate tier ∩ manifest); hosts render, they do not invent a second policy on the same event. | willows-grove: `docs/design/forge-convergence.md`:146 | unattested |
| I1 | 1 — Every thing gets a hash, and the hash is its identity — ✓ fingerprint — ✓ pile pointers carry a hash; a hash check comes before keywords — ✓ "gave each plot it's own hash" — ✓ `link_id`, excerpt ids — **4** | willows-grove: `docs/design/one-script/README.md`:110 | unattested |
| I2 | 2 — New things cite older hashes, up the list — ✓ hash chain, Merkle — ✓ record chain — ✓ "plot 1 (hash#), plot 2 (hash) up the list" — ✓ a cite is an excerpt id or an earlier `link_id` — **4** | willows-grove: `docs/design/one-script/README.md`:111 | unattested |
| I3 | 3 — Pointers, not prose — ✓ "a baseline holds hashes only, never content" — ✓ "the pile holds pointers, not the full files" — ✓ "Not the prose, but just the points" — ✓ only `{excerpts, joins[]}` goes into the next call — **4** | willows-grove: `docs/design/one-script/README.md`:112 | unattested |
| I4 | 4 — Code first, model last — ✓ "Git already does steps 1 and 2" — ✓ "the agent is the last call" — ✓ "It starts when it's need. Ends when the job is done. ESCILATE." — ✓ D0 13/13 (10 against fixture gold, 3 routed against the ruling); ≤ 0.0 cloud per act on 15 counted acts, rubric pending (§13) — **4** | willows-grove: `docs/design/one-script/README.md`:113 | unattested |
| I5 | 5 — Only a human makes it true — ✓ "the human signs the fingerprint" — ✓ the seal is `COMMIT`; the truth rule — ✓ "by a human that only a human could produce" — ✓ the operator's rubric; "Lets keep the tree", sealed bfe001f7 — **4** | willows-grove: `docs/design/one-script/README.md`:114 | unattested |
| I6 | 6 — Three states, never collapsed — ✓ a hash per panel payload — ✓ the reachability gate — ✓ INVARIANTS §1 — ✓ the materials check — **4** | willows-grove: `docs/design/one-script/README.md`:115 | unattested |
| I7 | 7 — Pile it up; what stacks is what matters — ✓ identical records dedupe by hash — ✓ `merge_flows`; mass decides attention — ✓ "what merges, what stands out when the pile is on top of itself?" — — — **3** | willows-grove: `docs/design/one-script/README.md`:116 | unattested |
| I8 | 8 — The model's job is connections — — — ✓ "flowering on material already gathered" (workflow §2c) — ✓ "Making connection between a group of ideas that a human hasn't seen yet." — ✓ joins, chain depth — **3** | willows-grove: `docs/design/one-script/README.md`:117 | unattested |
| I9 | 9 — Picture and compare — ✓ `snap.py` — ✓ B2 state check, reverse three-way — ✓ "the simple", Tripwire — — — **3** | willows-grove: `docs/design/one-script/README.md`:118 | unattested |
| I10 | 10 — A pre-AI foundation — ✓ Python 3.8.2 by checksum — ✓ the VSOCK pre-AI gate — ✓ the operator's idea — — — **3** | willows-grove: `docs/design/one-script/README.md`:119 | unattested |
| I11 | 11 — The database builds itself — — — ✓ write-ahead log → views → `COMMIT` — ✓ "deterministic postgres that builds itself" — — — **2** | willows-grove: `docs/design/one-script/README.md`:120 | unattested |
| I12 | 12 — The 3 / 7 / 13 / 23 rollup — — — ✓ auto flags, the ladder — ✓ "grouping the 23's by 3" — — — **2** | willows-grove: `docs/design/one-script/README.md`:121 | unattested |
| I13 | 13 — Once / session / permanent — — — ✓ `gate.allow` — ✓ "Run Once. Run For session. Run perm." — — — **2** | willows-grove: `docs/design/one-script/README.md`:122 | unattested |
| J1 | §1 — The three-state contract: Every reader returns EITHER a value with a bounded shape (populated OR empty) OR raises a `grove.errors.Unreachable` sentinel. **A bare `[]` or `{}` MUST NOT mean "unreachable" anywhere in the tree.** | willows-grove: `docs/INVARIANTS.md`:13 | unattested |
| J2 | §2 — Supersedes D7 (premise doc): `docs/design/willow-grove-premise.md` D7 sealed the phrase *"absence is a state, not a failure"*. That phrase was widely misread as "empty-on-failure is fine" — the readers collapsed "could-not-reach-the-source" into `[]` / `{}` / `None`, and the Web Components rendered nothing (which reads to the operator as "there is nothing there"), which IS the fleet's disease named in … | willows-grove: `docs/INVARIANTS.md`:102 | unattested |
| J3 | §3 — Doc discipline: - Every design-doc reference in code comments cites `INVARIANTS.md §<anchor>`, not line numbers in `DESIGN_CONSTRAINTS.md` (line numbers rot; anchors don't). | willows-grove: `docs/INVARIANTS.md`:120 | unattested |
| J4 | §4 — Reader/endpoint coverage (v0.9 PR 1 baseline): Every reader listed below returns bounded-shape-or-`Unreachable`; every endpoint answers 200/populated, 200/empty, or 503/unreachable. | willows-grove: `docs/INVARIANTS.md`:139 | unattested |
| J5 | §5 — Trust order: Every u2u packet has its signature verified before consent is consulted; consent decisions never render on unverified data. The order is **signature → consent → dispatch**, in exactly that sequence. | willows-grove: `docs/INVARIANTS.md`:161 | unattested |
| J6 | §6 — Manifests describe code, not aspirations: Every capability described in `safe-app-manifest.json` reflects a property the code demonstrably has. Aspirational descriptions belong in design docs, not in a manifest that claims trust from consumers. Tests enforce this. | willows-grove: `docs/INVARIANTS.md`:198 | unattested |
| J7 | §7 — Consent flows are real, not automatic: OAuth authorization never auto-issues a code. The operator approves via a loopback-only page. Access tokens have a bounded TTL suitable for the operator seat, not 30 days. DNS-rebinding protection is on regardless of scheme; a public tunnel deployment requires an explicit operator acknowledgement flag. | willows-grove: `docs/INVARIANTS.md`:220 | unattested |
| J8 | §8 — Panels consume live endpoints by default: Every Web Component consumes its live `/api/*` endpoint by default. Fixture-based rendering is opt-in (harness use only). The served page renders live state, not curated data. | willows-grove: `docs/INVARIANTS.md`:266 | unattested |
| J9 | §9 — Seed reads real canon: The `/seed/` route renders content from `governance/seed/canon/` (in this repo, relocated from the archived `willow-memory/willow` charter repository — see `governance/README.md`) when the probe path resolves. On absence the stub is served (C3 discipline). No content is invented at render time; the reader either quotes canon verbatim (HTML-escaped) or serves the stub. | willows-grove: `docs/INVARIANTS.md`:298 | unattested |
| J10 | §10 — CI proves the invariants: Every INVARIANTS section is enforced by at least one CI step. Ollama, Playwright, docs-drift, and security-grep are CI-first (never operator-only). Tests that require services declare them in `.github/workflows/tests.yml`. | willows-grove: `docs/INVARIANTS.md`:335 | unattested |
| J11 | §11 — Persona provenance: Every commit that changes tracked code carries a `Persona:` trailer naming the fleet persona active for the work. Accountability without persona-provenance is aesthetic; accountability with it is measurable. | willows-grove: `docs/INVARIANTS.md`:389 | unattested |
| J12 | §12 — Ratification: Persona provenance (§11) tracks who did the work. §12 tracks who authorized it to leave the branch. No fleet persona has unilateral authority to open a pull request, merge a pull request, or push to master — not Heimdallr, not Hanuman, not Loki, not even Willow. | willows-grove: `docs/INVARIANTS.md`:463 | unattested |
| J13 | Grandfather: PRs 1 through 11 in the Grove v0.9 stand-up were opened and merged without recorded `Ratified-by:` metadata. Same gap-class as pre-v0.9 persona provenance: real, logged, not backfillable. See `docs/design/pr14-carryovers.md`. §12 is hard from the commit that seals it forward. | willows-grove: `docs/INVARIANTS.md`:507 | unattested |
| K1 | D1 — **Canonical runtime.** Is Rat (ratatosk) the one runtime every shim calls? This flips forge-convergence §3 ("two hosts render rows") to "one runtime, many shims" and answers §9 row 9 — Yes. Seal it as its own decision — Phase 2 | willows-grove: `docs/design/one-box/README.md`:182 | unattested |
| K2 | D2 — **Where the chain lives.** Ratatosk imports willow-bot (heavy deps: fastapi, JWT), **or** the stdlib-only `deterministic/` is extracted into its own package, **or** Rat calls willow-bot's socket — Extract `deterministic/` as its own stdlib package, imported by both. Socket-calling is the interim — Phase 2 | willows-grove: `docs/design/one-box/README.md`:183 | unattested |
| K3 | D3 — **Home of the socket standard** (the shared UDS helper) — Forge, as the fleet's vendoring source (decision 2026-09-12), as a small stdlib module. The Forge never imports willow, so this is allowed — Phase 1 | willows-grove: `docs/design/one-box/README.md`:184 | unattested |
| K4 | D4 — **The browser door.** Browsers can't speak UDS, so "portless" needs one browser-facing door — One loopback front door that proxies by path to UDS backends (Grove page, Nestor UI, gates), with every mutation signed in the browser (§7) — Phase 7 | willows-grove: `docs/design/one-box/README.md`:185 | unattested |
| K5 | D5 — **The #101 sealed record.** Revert the hand edit and re-propose through Nestor, or ratify after the fact — Revert and re-propose. The rows will change again in Phase 4 anyway — Phase 4 | willows-grove: `docs/design/one-box/README.md`:186 | unattested |
| K6 | D6 — **Friction ownership** (the #706 regression) — The OUT door at SessionEnd runs friction and corpus-lens with the real transcript, via receipts. The handoff keeps the stack and the closed marker — Phase 4 | willows-grove: `docs/design/one-box/README.md`:187 | unattested |
| K7 | D7 — **The Forge entry's hard refusal without Nestor, and workshop Rule 1** ("ask Nestor before you search") — Make Nestor-unreachable a reported state, not a refusal. Change the paper first — Phase 5 | willows-grove: `docs/design/one-box/README.md`:188 | unattested |
| K8 | D8 — **u2u and the Matrix bridge.** They are LAN and Synapse by design. Accept them as declared exceptions to portless? — Yes, but bind the bridge to an explicit interface, not 0.0.0.0, and list both as exceptions in the box — Phase 7 | willows-grove: `docs/design/one-box/README.md`:189 | unattested |
| K9 | D9 — **Which commercial front end is the second proof** beside Ratatosk's REPL — Whichever the operator uses daily; the contract is neutral either way — Phase 3 | willows-grove: `docs/design/one-box/README.md`:190 | unattested |
| K10 | D10 — **Ingress.** What may reach the box from the public internet, and through whom — **No tunnel by default.** willow-bot **polls** GitHub instead of receiving webhooks. claude.ai remote MCP is **opt-in**, opened by the operator only when wanted, through **frp** (Apache-2.0, forwards to a Unix socket) on a server the operator rents and controls. Excluded on the operator's criterion, unwillingness to depend on … | willows-grove: `docs/design/one-box/README.md`:191 | unattested |
| K11 | D11 — How a grant is made away from the box (phone seat) — The card waits until the operator is at the box. A phone passkey on a real hostname comes later, if wanted | willows-grove: `docs/design/one-box/README.md`:738 | unattested |
| K12 | D12 — The persona for helper and bookkeeping commits — Add `willow-bot` to `fleet_personas.json` through its own ratified PR | willows-grove: `docs/design/one-box/README.md`:739 | unattested |
| K13 | - **The Kaggle benchmark comes first** (deadline 2026-10-11). No Forge code changes until the day-two cloud run finishes. | willows-grove: `docs/design/one-script/next-pile.md`:245 | unattested |
| L1 | 3. Phase 0 — Close the holes (independent; can start now): These are box repairs. They are small and they don't wait on the design. | willows-grove: `docs/design/one-box/README.md`:248 | unattested |
| L2 | 4. Phase 1 — The socket standard (box): One small stdlib module, `forge.sock` (D3), used by every helper: | willows-grove: `docs/design/one-box/README.md`:278 | unattested |
| L3 | 5. Phase 2 — Rat gets a door (the runtime): In ratatosk, add `ratatosk serve`: a UDS server on the Phase 1 standard, run by a user unit, with these ops: | willows-grove: `docs/design/one-box/README.md`:308 | unattested |
| L4 | 6. Phase 3 — Front ends: one neutral contract, many adapters: **No front end is primary** (operator, 2026-10-01: "Don't code for claude exclusively … this is supposed to be able to be run on anything."). | willows-grove: `docs/design/one-box/README.md`:384 | unattested |
| L5 | 7. Phase 4 — The lifecycle behind Rat: 1. **`end` owns closeout through receipts.** Each instrument (stack, friction, corpus-lens, pre-handoff) writes a receipt keyed on `(app, session, transcript extent)`. Any stale or missing receipt reruns. This replaces the `closed` flag and fixes all of the #706 gaps: | willows-grove: `docs/design/one-box/README.md`:432 | unattested |
| L6 | 8. Phase 5 — Nestor behind Rat: noticing and relating: 1. **Relational read.** Add `neighborhood(id, hops=2)` to Nestor's Python API, with a `nestor` CLI and an op. It returns the pair, its lineage, its edges, and each linked pair **with its own state and edges**. Today `constraints_on` goes one hop and leaves out the neighbours' states. Rat puts the neighborhood into the IN-door bundle. Neighbours come by edge … | willows-grove: `docs/design/one-box/README.md`:462 | unattested |
| L7 | 9. Phase 6 — Egress: click to grant, through Jeles: 1. **A typed reason in the chain.** `needs_egress{scope, host_class, why, asked}` as a flowering *reason* next to `local_unreachable` (`chain.py:235`), with its own bucket in `summarize_chain`. | willows-grove: `docs/design/one-box/README.md`:490 | unattested |
| L8 | **Done when:** `ss -ltnp` on the box shows only the front door plus the declared exceptions, and a pin test enumerates the binds from the unit templates. | willows-grove: `docs/design/one-box/README.md`:568 | unattested |
| L9 | 11. Phase 8 — The model-facing surface grows per user: 1. **Observe.** Rat logs which willow-mcp verbs each front-end model calls, per user, continuously. | willows-grove: `docs/design/one-box/README.md`:574 | unattested |
| L10 | 12. Phase 9 — The template ships the box: - **Package the shims and the socket client** as an installable with entry points, not files copied into the repo. This respects workshop Rule 5 ("nothing here grows logic"). | willows-grove: `docs/design/one-box/README.md`:594 | unattested |
| L11 | 13. Sequencing, and what not to break: - **The DEV × Kaggle benchmark (deadline 2026-10-11) runs beside this and takes priority until it's submitted.** No step here touches `Forge/benchmarks/escalation/`. | willows-grove: `docs/design/one-box/README.md`:607 | unattested |
| L12 | 15. Gap pass (deterministic, 2026-10-01): The operator asked for everything that had been missed, found deterministically and backed by the web where needed. **Method:** | willows-grove: `docs/design/one-box/README.md`:639 | unattested |
| L13 | 14. The first three bites I'd propose: 1. **Phase 0.1:** lock `gates --serve` (token + Origin + JSON-only), with a test that a forged POST is refused. Small, and it closes a real hole today. | willows-grove: `docs/design/one-box/README.md`:744 | unattested |
| M1 | 1. Hash — the W as written is a lookup — no exact match | willows-grove: `docs/design/one-script/README.md`:369 | unattested |
| M2 | 2. Code — parses **when** (dates, turns) and **where** (paths: resolve, strip `./`) exactly — it doesn't parse | willows-grove: `docs/design/one-script/README.md`:370 | unattested |
| M3 | 3. Embedder — nearest known canonical **who** or **what** ("the operator", "Sean", "op" → one `who`; "wrote", "saved" → `write`) — below the similarity threshold, or a near-tie | willows-grove: `docs/design/one-script/README.md`:371 | unattested |
| M4 | 4. Small model — normalizes what's left into the four fields, citing its words — it can't cite, or answers `ESCALATE` | willows-grove: `docs/design/one-script/README.md`:372 | unattested |
| M5 | 5. Cloud — the same job with bigger context, still citing — the same | willows-grove: `docs/design/one-script/README.md`:373 | unattested |
| M6 | 6. The human — `ESCALATE` — — | willows-grove: `docs/design/one-script/README.md`:374 | unattested |
| M7 | 1 — boot — B1 session record, B2 state + attestation, B3 egress index, then the hard close — CONST-I, V, III — `seat.py`, `session.py` (partly) — workflow §2 (prose) | willows-grove: `docs/design/one-script/next-pile.md`:31 | unattested |
| M8 | 2 — predict — declare the next-bite distribution before the work — CONST-IV, §0.2 — none — `predictions.json` (shape) | willows-grove: `docs/design/one-script/next-pile.md`:32 | unattested |
| M9 | 3 — record — append-only turn record, **the stamp**, pile pointers — CONST-VI, §0.5 — `session.py` (JSONL), `traces.py` — `side_runner.py` (record half) | willows-grove: `docs/design/one-script/next-pile.md`:33 | unattested |
| M10 | 4 — gate — the doors: fail closed and loud, peer uid, grant cards, egress — CONST-III, II, §0.3, V.2 — `permission.py`, `policy.py`, `hooks.py` — `onebox.py` + 10 tests | willows-grove: `docs/design/one-script/next-pile.md`:34 | unattested |
| M11 | 5 — resolve — the user's sources first, then web through the gate, then local model, then cloud — CONST-IV (Ground), XII, III — `ladder.py` + `provider_ladder.json` (the **model** rungs only) — workflow §3 (sketch) | willows-grove: `docs/design/one-script/next-pile.md`:35 | unattested |
| M12 | 6 — view — drawio / Mermaid / md from the record; marks drawn, never written — CONST-VI, IV.5 — none — `make_flow.py`, `side_runner.py` (view half) | willows-grove: `docs/design/one-script/next-pile.md`:36 | unattested |
| M13 | 7 — reverse — re-check old assertions: pile hashes, citations, quotes, prediction grades, repetition counts, floor and consistency — CONST-XI, App. B, IV.2 — none — the inline checker (crude), `reliability.py` | willows-grove: `docs/design/one-script/next-pile.md`:37 | unattested |

---

ΔΣ=42
