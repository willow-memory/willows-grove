# What in the system is only prose — 2026-10-03

*Desk (Willow seat), at the operator's ask: "What else in this system is
strictly prose?" then "I don't feel like that was a full check of the whole
system." **Prose** here means a rule that is written down but that no code,
test or CI step reads or enforces. Agent-reported; the receipts are the Kart
task ids.*

## Method

1. List every place a rule lives across the eight repos on the box
   (Kart QKJSY539).
2. For each numbered invariant and constitution article, count references in
   code, tests and CI (Kart LVS39MU3, 2,392 code files scanned).
3. Run the repo's own `governance/scripts/const_coverage.py`, then rerun it
   with `.worktrees/` excluded (Kart 7UPLD2MY, HKXEXP4M).
4. Read each configured hook's source.

A reference isn't enforcement: a comment, a JSON data row or a list in a test
all count as references. So step 2 is an upper bound, and step 3 (human
verdicts) is the real measure.

## Where the rules live

| Source | Count | Enforced by |
|---|---|---|
| `governance/CONSTITUTION.md` (Draft 0.8) | 65 clauses | **64 with no verdict, 1 marked "differently", 0 marked "satisfied".** 28 cited nowhere, 18 only in docs or tests, 19 in non-test code. Gap `ab808b678ab1`. |
| `docs/INVARIANTS.md` | 12 sections | All 12 referenced in code or CI (9 to 86 references each). §10–§12 have their own CI scripts (`check_ratification`, `check_persona_provenance`, `check_changelog_bullet`). The other sections are referenced but not individually proven enforced. |
| `CLAUDE.md` rules 1–6 | 6 | Rule 6: CI scripts. Rule 2 (schema): `tests/test_schema_completeness.py`. Rules 1, 3, 4, 5: no checker found. Rule 1 ("no web ports") contradicts the served page on `:8766` in the same file. |
| Hooks (4 settings files, 56 commands) | — | See below. |
| Memory files | 78 | All prose. Exception verified tonight: "no shell on this seat" is enforced by `willow_mcp.pre_tool_hook`, which refused a Bash call. |
| Nestor `.claude/skills/*/SKILL.md` | 5 | Prose. |
| willow-mcp `docs/AGENTS.md`, `skills/persona-overlays.md` | 2 | Prose. |
| `hooks/seat.md` | 1 | Only its anchor line is checked (`_seat_drift`); the rest is prose. |

## Hooks: which ones read the record, and which read prose

| Hook | Reads | Verdict |
|---|---|---|
| willow-mcp `pre_tool_hook` (PreToolUse) | the seat's manifest and the tool name | **enforces.** It refused Bash tonight. |
| willow-mcp `stop_lint_gate` (Stop) | ruff on the project | **enforces**, mechanically |
| willow-mcp `stop-issue-closure-check.sh` (Stop) | git log against GitHub issue state | **enforces.** It says itself that it's narrow and mechanical, not a check on what the assistant claims. |
| grove `gate` (Stop) | the model's last text block, against `done\|complete\|all tests pass` | **reads prose**, and its "no tool call" half can't ever be true, because it reads only the last transcript entry (`grove_hook.py:819-833`). Gaps `36fb554af073`, `18882291cc24`. |
| grove `reinject` (UserPromptSubmit) | four fixed sentences | **prose injection**; nothing checks they're followed |
| grove `reinject`, Nestor line | TCP 8765, then the `nestor ask` CLI | **reports wrong.** The UI port answers, the CLI call fails, and the failure prints as "Nestor: unreachable" while the Nestor MCP answers (ledger intact, 2,487 memories). Gap `25bbb8c75474`. |
| grove `orient` and inbox | blockers, the Grove inbox, `/health` | reads the record |

## The pattern

What holds is what a script reads off the record: the manifest gate, ruff,
the issue-closure check, ratification and persona CI, the hash checks, the
seals. What drifts is what's only written for a model to follow, or what a
hook judges from the model's wording. The constitution, which binds
everything, is the largest prose surface: its coverage tool exists, but 64 of
65 clauses have no recorded verdict.

## Not covered

- willow-bot, willow-gate, kartikeya, ratatosk and Jeles rule text beyond the
  file inventory. No CLAUDE.md, INVARIANTS or constitution file was found
  there, and their hooks and CI weren't read.
- The 78 memory files weren't checked one by one for a matching enforcer.
- The willow-mcp constitutional manifest (`constitutional.py`,
  `sync_constitutional.py`) wasn't mapped clause by clause.
