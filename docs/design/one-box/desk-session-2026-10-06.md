# One hook, two hashes, Draft 0.9, and the instruction files, in the grid (2026-10-06)

*Desk session `session_01AEYnPWKuWa4xmU3ZnsAZTS`, 2026-10-06, persona `willow`
by Desk default (`session_enter` was never reachable). It ran from the Day 5
handoff through PR #112, the instruction-file research and session three of
113. The operator's words are quoted verbatim. Test counts and hashes were
measured in the session's container; the per-CLI findings carry their own
source tags in the docs they point at; everything else is the agent's reading.
Every box is `unattested`. This grid points at the records and doesn't copy
them.*

## The notes (the source)

### IG · The ask

- **Operator, the start.** "If you were to set up a repo just on the files referenced, how would you set that up?", then "Don't think about how it affects Willow mcp. Think about how it affects every CLI across the universe."
- **Operator, the sources.** "Look it up", "check polyhook too", "Have them go to the official documentation wherever possible", then "check the open source ones against their GitHub repos".
- **Operator, the hashes.** "It can also use the hash that's already in it from GitHub", then "We get githubs hash, when it comes local, and then we get the systems hash".
- **Operator, the law.** "go ahead and bring them in all together", then "Are there any amendments you want to add for yourself.", then "write them up as their own proposal file".
- **Operator, the files.** "I want to know how those all respond to agent. MD or call.md, obviously I know that one, type files."

### IH · One hook, every CLI

- **The matrix.** `research-2026-10-06.md`: the pre-tool gate in 22 agent CLIs, every claim tagged by source. Only Claude Code's docs could be read directly; the rest came from the vendors' own repos or, where those were missing, search extracts marked as such.
- **Fail open.** A hook that crashes or times out lets the tool run almost everywhere. Copilot CLI is the only one that blocks on a crash by default; Cursor does with `failClosed`, Goose with `on_failure: "block"`. A timeout lets it through even on Copilot.
- **Ask is not universal.** A hook's "ask" turns into running the tool on Codex, and Codex's hook never sees reads. "Ask" belongs in each CLI's own permission settings.
- **polyhook.** Reference only. An "ask" comes out as allow, unknown callers and garbled input fail open, and Cursor (#44) and Windsurf (#78) payloads aren't recognised. Seen by running its published 0.2.0 wheel.
- **What hook.py covers today.** Claude Code as-is. Factory, Qwen and Junie probably, pending one captured payload each. Codex is a trap: a bare deny with no reason may be rejected and the tool run.

### II · Two hashes and xref

- **h256.** `record.py`'s `h16` cut SHA-256 to 64 bits; it is now `h256`, the full digest. A hash cut back to 64 bits reads as a chain break.
- **Arrival.** `onescript/xref.py` gives each tracked file git's blob id, the same id recomputed from the bytes on disk, and the system's own SHA-256. A file whose ids don't match is recorded and left out.
- **Checks.** Ids (Q, D, OW, F, CONST, INVARIANTS §, PR #), links, `file:line` citations and commit SHAs, across the repos. A bare filename away from its own folder is unanchored, not broken.
- **First run.** 1,512 files across willows-grove, willow-bot and willow-mcp, every blob id matching; the same bytes on three runs; 5 broken links and 5 out-of-range line citations, checked by hand.
- **Tested.** 97 tests pass on Python 3.9.23 and 3.11.15. A slice of one id is for people; serving it to the model waits on Q19.

### IJ · Draft 0.9

- **Brought in.** The ten 2026-10-02 amendments (renumbered IV.7, IV.8 and VI.6 where 0.8 had the number), the neutral-language proposal merged three ways onto 0.8, and the Opus outside pass.
- **Kept.** Article 0 and the Preamble byte-identical to 0.8; the Amendment History verbatim; Keeper of the Record kept over the proposal's "the Ledger".
- **Held for the operator.** Five Preamble edits, the two full proposal copies, a Casebook entry, and the new parameter numbers (180 days, 72 hours, 30 days, and an escalation rate with no default).
- **The seat's own proposals.** VIII.4 (an interested proposal says so), an IV.1 addition (a summary is not a source), V.10 (unknown is a lawful answer), and no clause for timeouts. Marked interested; the author can't ratify them.
- **Merged.** PR #112 as `a111829`, ratified "Refresh the box,  rebase, then pr, please."

### IK · The instruction files

- **AGENTS.md.** `instruction-files-2026-10-06.md`: 19 of the 22 CLIs read it natively. Claude Code reads it only when no CLAUDE.md exists up the tree, Gemini only when configured, Aider only through `--read`.
- **CLAUDE.md.** Read by Claude Code, Copilot, Amp, Cursor, Augment, Zed, OpenCode and Crush.
- **Closest wins.** The AGENTS.md convention's rule. Almost nothing implements it; most CLIs concatenate every file they find and rely on order.
- **Never untrusted.** None of the 22 treats an instruction file as untrusted data, so serve's output must never sit where a CLI auto-loads it.
- **Bugs on the way.** Continue never checks CLAUDE.md in the IDE; Crush skips lowercase names and orders files by Go map iteration; Cline lets a global rule override a workspace rule, against its docs.

### IL · Session three of 113

- **Read first.** `session_enter` unreachable; the four files read in the operator's order before anything else.
- **The review.** Session two's §2 misses and §9 open items, given in chat. Every §9 item unchanged: `Willow` has no branches, and the latest PR is #112.
- **The trigger.** No natural 113. The prompt named the session record for the trigger; its wording is in `113-guesses-2026-10-06.md`.
- **The prompt record.** Nine changes so the prompt runs in one turn, in `113-session-three-prompt-2026-10-06.md`, commit `261f78b` on `ccr-542b5884-0deee5`, not on this branch.
- **Operator, the ask.** "How would you improve that prompt. I just want it to run. Keep a record of it, and push that as well,  and give me the last 2 hashes"

## Grid

<!-- cross-table:grid -->
| | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| **IG** The ask | Operator, the start | Operator, the sources | Operator, the hashes | Operator, the law | Operator, the files |
| **IH** One hook, every CLI | The matrix | Fail open | Ask is not universal | polyhook | What hook.py covers today |
| **II** Two hashes and xref | h256 | Arrival | Checks | First run | Tested |
| **IJ** Draft 0.9 | Brought in | Kept | Held for the operator | The seat's own proposals | Merged |
| **IK** The instruction files | AGENTS.md | CLAUDE.md | Closest wins | Never untrusted | Bugs on the way |
| **IL** Session three of 113 | Read first | The review | The trigger | The prompt record | Operator, the ask |
<!-- /cross-table:grid -->

## Sources

<!-- cross-table:sources -->
| Row | What it holds | Source |
|---|---|---|
| IG | The ask | the notes, section IG (the operator's words verbatim) |
| IH | One hook, every CLI | the notes, section IH (the agent's reading of research-2026-10-06.md; per-CLI source tags there) |
| II | Two hashes and xref | the notes, section II (counts and hashes measured in the session; the rest the agent's reading) |
| IJ | Draft 0.9 | the notes, section IJ (the agent's reading of governance/CONSTITUTION.md Draft 0.9 and PR #112) |
| IK | The instruction files | the notes, section IK (the agent's reading of instruction-files-2026-10-06.md; per-CLI source tags there) |
| IL | Session three of 113 | the notes, section IL (the operator's words verbatim; the rest the agent's reading) |
<!-- /cross-table:sources -->

## Index

<!-- cross-table:index -->
| Cell | Rule | Source | Share | Standing |
|---|---|---|---|---|
| IG1 | - **Operator, the start.** "If you were to set up a repo just on the files referenced, how would you set that up?", then "Don't think about how it affects Willow mcp. Think about how it affects every CLI across the universe." | `willows-grove/docs/design/one-box/desk-session-2026-10-06.md`:16 | 4.30% | unattested |
| IG2 | - **Operator, the sources.** "Look it up", "check polyhook too", "Have them go to the official documentation wherever possible", then "check the open source ones against their GitHub repos". | `willows-grove/docs/design/one-box/desk-session-2026-10-06.md`:17 | 3.63% | unattested |
| IG3 | - **Operator, the hashes.** "It can also use the hash that's already in it from GitHub", then "We get githubs hash, when it comes local, and then we get the systems hash". | `willows-grove/docs/design/one-box/desk-session-2026-10-06.md`:18 | 3.26% | unattested |
| IG4 | - **Operator, the law.** "go ahead and bring them in all together", then "Are there any amendments you want to add for yourself.", then "write them up as their own proposal file". | `willows-grove/docs/design/one-box/desk-session-2026-10-06.md`:19 | 3.42% | unattested |
| IG5 | - **Operator, the files.** "I want to know how those all respond to agent. MD or call.md, obviously I know that one, type files." | `willows-grove/docs/design/one-box/desk-session-2026-10-06.md`:20 | 2.46% | unattested |
| IH1 | - **The matrix.** `research-2026-10-06.md`: the pre-tool gate in 22 agent CLIs, every claim tagged by source. Only Claude Code's docs could be read directly; the rest came from the vendors' own repos or, where those were missing, search extracts marked as such. | `willows-grove/docs/design/one-box/desk-session-2026-10-06.md`:24 | 4.98% | unattested |
| IH2 | - **Fail open.** A hook that crashes or times out lets the tool run almost everywhere. Copilot CLI is the only one that blocks on a crash by default; Cursor does with `failClosed`, Goose with `on_failure: "block"`. A timeout lets it through even on Copilot. | `willows-grove/docs/design/one-box/desk-session-2026-10-06.md`:25 | 4.91% | unattested |
| IH3 | - **Ask is not universal.** A hook's "ask" turns into running the tool on Codex, and Codex's hook never sees reads. "Ask" belongs in each CLI's own permission settings. | `willows-grove/docs/design/one-box/desk-session-2026-10-06.md`:26 | 3.21% | unattested |
| IH4 | - **polyhook.** Reference only. An "ask" comes out as allow, unknown callers and garbled input fail open, and Cursor (#44) and Windsurf (#78) payloads aren't recognised. Seen by running its published 0.2.0 wheel. | `willows-grove/docs/design/one-box/desk-session-2026-10-06.md`:27 | 4.05% | unattested |
| IH5 | - **What hook.py covers today.** Claude Code as-is. Factory, Qwen and Junie probably, pending one captured payload each. Codex is a trap: a bare deny with no reason may be rejected and the tool run. | `willows-grove/docs/design/one-box/desk-session-2026-10-06.md`:28 | 3.78% | unattested |
| II1 | - **h256.** `record.py`'s `h16` cut SHA-256 to 64 bits; it is now `h256`, the full digest. A hash cut back to 64 bits reads as a chain break. | `willows-grove/docs/design/one-box/desk-session-2026-10-06.md`:32 | 2.69% | unattested |
| II2 | - **Arrival.** `onescript/xref.py` gives each tracked file git's blob id, the same id recomputed from the bytes on disk, and the system's own SHA-256. A file whose ids don't match is recorded and left out. | `willows-grove/docs/design/one-box/desk-session-2026-10-06.md`:33 | 3.91% | unattested |
| II3 | - **Checks.** Ids (Q, D, OW, F, CONST, INVARIANTS §, PR #), links, `file:line` citations and commit SHAs, across the repos. A bare filename away from its own folder is unanchored, not broken. | `willows-grove/docs/design/one-box/desk-session-2026-10-06.md`:34 | 3.65% | unattested |
| II4 | - **First run.** 1,512 files across willows-grove, willow-bot and willow-mcp, every blob id matching; the same bytes on three runs; 5 broken links and 5 out-of-range line citations, checked by hand. | `willows-grove/docs/design/one-box/desk-session-2026-10-06.md`:35 | 3.78% | unattested |
| II5 | - **Tested.** 97 tests pass on Python 3.9.23 and 3.11.15. A slice of one id is for people; serving it to the model waits on Q19. | `willows-grove/docs/design/one-box/desk-session-2026-10-06.md`:36 | 2.44% | unattested |
| IJ1 | - **Brought in.** The ten 2026-10-02 amendments (renumbered IV.7, IV.8 and VI.6 where 0.8 had the number), the neutral-language proposal merged three ways onto 0.8, and the Opus outside pass. | `willows-grove/docs/design/one-box/desk-session-2026-10-06.md`:40 | 3.65% | unattested |
| IJ2 | - **Kept.** Article 0 and the Preamble byte-identical to 0.8; the Amendment History verbatim; Keeper of the Record kept over the proposal's "the Ledger". | `willows-grove/docs/design/one-box/desk-session-2026-10-06.md`:41 | 2.92% | unattested |
| IJ3 | - **Held for the operator.** Five Preamble edits, the two full proposal copies, a Casebook entry, and the new parameter numbers (180 days, 72 hours, 30 days, and an escalation rate with no default). | `willows-grove/docs/design/one-box/desk-session-2026-10-06.md`:42 | 3.78% | unattested |
| IJ4 | - **The seat's own proposals.** VIII.4 (an interested proposal says so), an IV.1 addition (a summary is not a source), V.10 (unknown is a lawful answer), and no clause for timeouts. Marked interested; the author can't ratify them. | `willows-grove/docs/design/one-box/desk-session-2026-10-06.md`:43 | 4.39% | unattested |
| IJ5 | - **Merged.** PR #112 as `a111829`, ratified "Refresh the box, rebase, then pr, please." | `willows-grove/docs/design/one-box/desk-session-2026-10-06.md`:44 | 1.68% | unattested |
| IK1 | - **AGENTS.md.** `instruction-files-2026-10-06.md`: 19 of the 22 CLIs read it natively. Claude Code reads it only when no CLAUDE.md exists up the tree, Gemini only when configured, Aider only through `--read`. | `willows-grove/docs/design/one-box/desk-session-2026-10-06.md`:48 | 3.99% | unattested |
| IK2 | - **CLAUDE.md.** Read by Claude Code, Copilot, Amp, Cursor, Augment, Zed, OpenCode and Crush. | `willows-grove/docs/design/one-box/desk-session-2026-10-06.md`:49 | 1.78% | unattested |
| IK3 | - **Closest wins.** The AGENTS.md convention's rule. Almost nothing implements it; most CLIs concatenate every file they find and rely on order. | `willows-grove/docs/design/one-box/desk-session-2026-10-06.md`:50 | 2.75% | unattested |
| IK4 | - **Never untrusted.** None of the 22 treats an instruction file as untrusted data, so serve's output must never sit where a CLI auto-loads it. | `willows-grove/docs/design/one-box/desk-session-2026-10-06.md`:51 | 2.73% | unattested |
| IK5 | - **Bugs on the way.** Continue never checks CLAUDE.md in the IDE; Crush skips lowercase names and orders files by Go map iteration; Cline lets a global rule override a workspace rule, against its docs. | `willows-grove/docs/design/one-box/desk-session-2026-10-06.md`:52 | 3.86% | unattested |
| IL1 | - **Read first.** `session_enter` unreachable; the four files read in the operator's order before anything else. | `willows-grove/docs/design/one-box/desk-session-2026-10-06.md`:56 | 2.14% | unattested |
| IL2 | - **The review.** Session two's §2 misses and §9 open items, given in chat. Every §9 item unchanged: `Willow` has no branches, and the latest PR is #112. | `willows-grove/docs/design/one-box/desk-session-2026-10-06.md`:57 | 2.92% | unattested |
| IL3 | - **The trigger.** No natural 113. The prompt named the session record for the trigger; its wording is in `113-guesses-2026-10-06.md`. | `willows-grove/docs/design/one-box/desk-session-2026-10-06.md`:58 | 2.56% | unattested |
| IL4 | - **The prompt record.** Nine changes so the prompt runs in one turn, in `113-session-three-prompt-2026-10-06.md`, commit `261f78b` on `ccr-542b5884-0deee5`, not on this branch. | `willows-grove/docs/design/one-box/desk-session-2026-10-06.md`:59 | 3.38% | unattested |
| IL5 | - **Operator, the ask.** "How would you improve that prompt. I just want it to run. Keep a record of it, and push that as well, and give me the last 2 hashes" | `willows-grove/docs/design/one-box/desk-session-2026-10-06.md`:60 | 3.02% | unattested |
<!-- /cross-table:index -->

## Measure

<!-- cross-table:measure -->
- **Cells:** 30, of which 30 found (100.0%).
- **Text:** 5238 characters. An even share would be 3.33% per cell.
- **Trim:** 0 cell(s) cut at 420 characters; the index keeps 100.0% of the source text.

| Row | What it holds | Found | Characters | Share | Largest cell |
|---|---|---|---|---|---|
| IG | The ask | 5/5 | 894 | 17.07% | IG1 4.30% |
| IH | One hook, every CLI | 5/5 | 1096 | 20.92% | IH1 4.98% |
| II | Two hashes and xref | 5/5 | 863 | 16.48% | II2 3.91% |
| IJ | Draft 0.9 | 5/5 | 860 | 16.42% | IJ4 4.39% |
| IK | The instruction files | 5/5 | 791 | 15.10% | IK1 3.99% |
| IL | Session three of 113 | 5/5 | 734 | 14.01% | IL4 3.38% |

- **Largest:** IH1 4.98%, IH2 4.91%, IJ4 4.39%, IG1 4.30%, IH4 4.05%.
- **Smallest:** IJ5 1.68%, IK2 1.78%, IL1 2.14%, II5 2.44%, IG5 2.46%.

**Evenness.** Gini 0.14 (0 means every box holds the same, 1 means one box holds everything).
- **Fat** (at least 3× an even share; often several rules in one box, a candidate to split): none.
- **Thin** (at most 0.25× an even share; a label with a line behind it): none.

**Sources.** How much of each source file the grid draws on (distinct passages over the file's characters, whitespace collapsed, not counting any tables this script generated in it).

| File | Cells | Drawn | File | Coverage |
|---|---|---|---|---|
| `willows-grove/docs/design/one-box/desk-session-2026-10-06.md` | 30 | 5238 | 6078 | 86.2% |
<!-- /cross-table:measure -->
