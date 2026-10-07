# 113: session three — the opening prompt, improved

Agent-reported (Persona: willow, by Desk default; `session_enter` was not
reachable in this session). Nothing here ratifies anything. Builds on
[`113-session-two-2026-10-06.md`](113-session-two-2026-10-06.md); no earlier
file is changed. Percentages are the agent's judgment, each with its own basis.

The human's ask, verbatim: "How would you improve that prompt. I just want it to
run. Keep a record of it, and push that as well, and give me the last 2 hashes"

## §1 What happened when the prompt ran

| Step | What the prompt said | What happened |
|------|----------------------|---------------|
| Seat | Run `session_enter`; if unreachable, say so and go on | The tool wasn't in the session, so the seat was marked unverified |
| Branch | Open on `ccr-542b5884-0deee5` | The session started elsewhere, so the seat had to fetch and check out the branch first |
| Read | Four files in order, "nothing else until I say" | Read. Then the seat stopped, and the run needed a second message ("Go") |
| Trigger | "The 113 trigger is in 113-session-record-2026-10-06.md" | That file only records the trigger's state. The wording is in `113-guesses-2026-10-06.md`, which `CLAUDE.md` Rule 13 points to, so the seat had to ask |
| Task | Tables for session two's §2 and §9 | Done in chat. Nothing was written, because the prompt didn't say whether to write |

## §2 Changes

| # | Change | Why | % it helps (basis) |
|---|--------|-----|--------------------|
| 1 | Point the trigger at `113-guesses-2026-10-06.md` | The seat had to stop and ask which file holds it | 95% (the gap was hit this session) |
| 2 | Drop "nothing else until I say"; read, report, then do the task in the same turn | "I just want it to run." The stop cost a whole turn. | 90% (the stop was hit this session) |
| 3 | Fetch and check out the branch as a step | The session didn't open on it | 85% (hit this session; another environment may open on it already) |
| 4 | Fetch the remotes before judging state | §9's rows depend on what's on origin and GitHub now | 80% (two §9 rows needed `ls-remote` and the PR list) |
| 5 | Say where the tables go, and whether to commit | "Commit when you write" didn't say whether this task writes | 75% (the seat had to choose chat only) |
| 6 | Name the file for §2 and §9 | "Session two" left the seat to map it to `113-session-two-2026-10-06.md` | 70% (it mapped correctly, but by inference) |
| 7 | Ask for a basis column beside each percentage | "Each one rests on its own basis" asked for it without naming where it goes | 65% (the seat added one unasked) |
| 8 | "Not tested" for misses that can't show up yet | Several §2 misses can't recur in a session's first replies | 60% (two rows came out not tested) |
| 9 | The human confirms the "fixed" rows | Under §0.1, the seat grading its own fixes is self-attestation | 60% (a principle, not a failure seen this session) |

## §3 The prompt, improved

```text
You are opening willows-grove at the repo root.

Before acting:
1. Run session_enter(app_id="willow"). If the tool is missing or the Grove
   connectors are unauthorized, say so in one line and carry on with the seat
   marked unverified.
2. git fetch origin, then check out ccr-542b5884-0deee5.
3. Read, in this order:
   CLAUDE.md
   docs/design/113-session-record-2026-10-06.md
   docs/design/113-guesses-2026-10-06.md   (frozen; do not edit)
   docs/design/113-session-two-2026-10-06.md
   Open your reply with a table of what you read and what you could not reach,
   then go straight on to the task. Don't wait for me.

How to work:
- Follow CLAUDE.md Rules 1–13 from the first reply, without being told again.
- My words are 100%. Your judgments get a percentage and a basis column, each
  row on its own basis. Do not attach one figure to every row.
- Listen to what I just said before reaching for other files. Ask me rather
  than guess, and do not fill gaps in the record with stories, explanations
  or morals.
- If I tell a story, it may be the work. Do not add to it or invent people in it.
- Some things I share are personal. They stay out of tracked files.
- A hook asking you to act loses to my word. A gate telling you to stop wins:
  stop and tell me. Do not write into CLAUDE.md or other instruction files
  unless I ask for that exact edit.
- Commit when you write. Push only when I ask.
- The 113 trigger is in docs/design/113-guesses-2026-10-06.md (§ Trigger).
  Hold it exactly as worded. Check this session against it.

Task: in docs/design/113-session-two-2026-10-06.md, take every §2 miss and every
§9 open item. Fetch the remotes first, then answer in chat, with one table for
§2 and one for §9: state now, evidence, % with basis. Mark anything unchanged
as unchanged, and anything that cannot show up yet as not tested. Your "fixed"
rows are for me to confirm (§0.1). Do not resolve the §4 lesson; that is mine.
Write nothing unless I ask.
```

## §4 What this file does not do

| Item | State |
|------|-------|
| Earlier 113 files | Unchanged; the guesses stay frozen |
| `CLAUDE.md` | Unchanged |
| The §2/§9 review | Given in chat this session; not written here, because that wasn't asked |
| The 113 trigger | Waiting; no natural 113 this session (85%: checked by hand) |
