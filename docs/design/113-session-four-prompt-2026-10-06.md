# 113: session four — the opening prompt, improved

Agent-reported (Persona: willow, by Desk default; `session_enter` was not
reachable in this session). Nothing here ratifies anything. Builds on
[`113-session-three-prompt-2026-10-06.md`](113-session-three-prompt-2026-10-06.md);
no earlier file is changed. Percentages are the agent's judgment, each with
its own basis.

The human's ask, verbatim: "Improve the prompt, and then push everything"

## §1 What happened when the prompt ran

| Step | What the prompt said | What happened |
|------|----------------------|---------------|
| Seat | Run `session_enter`; if missing, say so in one line | Missing; seat marked unverified in one line |
| Branch | Fetch and check out `ccr-542b5884-0deee5` | Done; tip `261f78b` confirmed |
| Read | Five files in order, open with a read table | Done; table led the reply |
| Task | Blank | Human asked about "the table that was supposed to be growing" |
| Table hunt | Not in the prompt | Seat asked which table; human said "all of it, master table a handful of commits back"; seat hunted `git log --all` and found `ccr-392b8b73-v809qu` |
| Check | Run `cross_table.py check` | First run used `--root /home/user/willows-grove`; G5 appeared unreachable; second run with `--root /home/user` fixed it |
| Fix | Update G5 pattern + re-run fill | Done on `ccr-392b8b73-v809qu`; 168 found, 0 not_found |

## §2 Changes

| # | Change | Why | % it helps (basis) |
|---|--------|-----|--------------------|
| 1 | Name `ccr-392b8b73-v809qu` and its key file in the prompt | Seat had to hunt it from `git log --all` across all branches | 90% (the hunt took a full exchange) |
| 2 | State the `--root /home/user` flag for `cross_table.py` | First run used the wrong root; one extra round | 85% (hit this session) |
| 3 | Add the cross table's current state to the opening context | Seat didn't know the table existed until the human mentioned it | 80% (it was unknown at prompt time) |
| 4 | Add session four's prompt record to the reading list | It's the newest file in the record | 80% (same reason session three's was added) |
| 5 | Note that `ccr-542b5884-0deee5` and `ccr-392b8b73-v809qu` are sibling branches (both off `a111829`) | Switching branches mid-session was disorienting; naming them in advance would let the seat plan | 70% (context, not a blocker) |
| 6 | Keep `Task:` blank | Operator decides; Rule 10 still applies | 90% (correct this session) |

## §3 The prompt, improved

```text
You are opening willows-grove at the repo root.

Before acting:
1. Run session_enter(app_id="willow"). If the tool is missing or the Grove
   connectors are unauthorized, say so in one line and carry on with the seat
   marked unverified.
2. git fetch origin, then check out ccr-542b5884-0deee5 (tip 261f78b or later).
3. Read, in this order:
   CLAUDE.md
   docs/design/113-session-record-2026-10-06.md
   docs/design/113-guesses-2026-10-06.md          (frozen; do not edit)
   docs/design/113-session-two-2026-10-06.md
   docs/design/113-session-three-prompt-2026-10-06.md
   docs/design/113-session-four-prompt-2026-10-06.md
   Open your reply with a table of what you read and what you could not reach,
   then go straight on to the task. Don't wait for me.

Context for this session:
- A second branch, ccr-392b8b73-v809qu, holds the rules cross table:
  docs/design/one-box/rules-cross-table-2026-10-06.md — 13 × 13, 168 found,
  1 silent (G6, by design). G5 was fixed this session (pattern updated for
  the rewritten CLAUDE.md). Both branches diverge from a111829 (PR 112).
- When running cross_table.py, use --root /home/user (not the repo root),
  so that willows-grove/ paths in the map resolve.
- The 113 trigger is in docs/design/113-guesses-2026-10-06.md (§ Trigger).
  Hold it exactly as worded. Check this session against it.

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
- Your "fixed" rows are for me to confirm (§0.1). The §4 lesson in session two
  is mine; do not resolve it.

Task: <your ask here>. Fetch the remotes before judging any state. Answer in
chat unless I ask you to write.
```

## §4 What this file does not do

| Item | State |
|------|-------|
| Earlier 113 files | Unchanged |
| `113-session-record-2026-10-06.md` | Not updated this session — session four's log belongs there; held for a separate commit or next session |
| The 113 trigger | Waiting; no natural 113 this session (90%: checked against git output and conversation) |
