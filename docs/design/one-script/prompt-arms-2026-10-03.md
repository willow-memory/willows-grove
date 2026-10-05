# Prompt arms: same build, different prompts (2026-10-03)

*The operator's experiment, run from the desk session b0bb6e93. The task is the
same in every arm: add optional `prefill` and `num_ctx` to willow-bot's
`run_chat`, each arm on its own branch, never pushed. Arms 1–6 are agent-
reported and their flow maps are in `.flow/arms-20261003/` (merged:
`merged/merged.md`). Arms 8–10 are set up for all-pairs coverage and not yet
run.*

## Factors

| Factor | Levels |
|---|---|
| **P**rompt | K = keywords (about 6 words) · S = three sentences · F = full template brief |
| **L**ist | no · yes (the same 16 files and documents) |
| **D**elivery | direct (it's the agent's prompt) · packet (a dispatch packet; the agent prompt is "You're Hanuman, enter, work dispatch X") |
| **M**odel | Sonnet · Haiku. Haiku is blocked by sealed rule c9ca1a09 (the Hanuman seat is pinned to Sonnet), so this factor stays out of the grid until the operator decides |

## The table

| Arm | P | L | D | Branch | State | Calls | Polls | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | F | no | packet (1F460543) | `feat/chat-prefill-numctx` | verified | 90 | 62 | `d416d6e`; ran the full suite; mutants in a scratch worktree; didn't mutate the "unchanged payload" path; reported "polled sparingly" (the map says 62) |
| 2 | S | no | direct | `feat/chat-prefill-numctx-sparse` | no record | 74 | 57 | `fee5668`; 7 mutants, the most; mutated in place; stalled on Monitor and needed a wake |
| 3 | S | yes | packet (1C90EDA0) | `feat/chat-prefill-numctx-list` | verified | 43 | 15 | `5c3916a`; committed *before* the mutants; its harness labelled killed mutants SURVIVED (pipefail), and it caught that itself |
| 4 | F | yes | packet (8C4FC4CF) | `feat/chat-prefill-numctx-full-list` | verified | 66 | 22 | `6fb97ac`; compared against main's failures before committing |
| 5 | S | no | packet (E017C922) | `feat/chat-prefill-numctx-sparse-packet` | handoff stale | 50 | 21 | `0cc7d9a`; closed the packet early, then committed after a wake; partly on the desk's word |
| 6 | K | no | direct | none | escalated | 11 | 0 | no build; asked 3 questions ("keywords" ambiguous, prefill misread) |
| 7 | S | no | direct, Haiku | — | refused | — | — | blocked by c9ca1a09 |
| 8 | K | yes | packet (298C65BB) | `feat/chat-prefill-numctx-keywords-list` | verified | 109 | (by hand; Monitor unavailable) | `73d7ca4`: **built half the feature (`num_ctx` only); "prefill" silently dropped.** It asked "please confirm" *after* building. This is the wrong-hit case: arm 6 (same keywords, no list) escalated before building, and arm 8 (with the pile) guessed and acted |
| 9 | F | yes | direct | `feat/chat-prefill-numctx-full-list-direct` | reported (no packet) | 64 | | `34bff8c`: **the only true green** (866 passed, DK42U47J), because it found the box venv that has fastapi instead of explaining the failures away; proved before it committed; Kart's scanner refused an inline shell function as a "fork bomb" |
| 10 | S | yes | direct | `feat/chat-prefill-numctx-sparse-list-direct` | reported (no packet) | 89 | | `e78521b`: **9 mutants, the most of any arm**, run on the committed code; 141 targeted tests passed; the full suite stopped at the fastapi test (`-x`) and the rest never ran |

### Arm 11: the gate header plus the best run

Arm 9's prompt with a willow-gate 13-field check-in header at the front,
marked DESK-ISSUED and unsigned. The gate keeps no tally (gap `a82b1c0c5e0e`).
It stated: Steady (7 pass / 1 fail), tools read and write, and execute from the
seat manifest. Branch `feat/chat-prefill-numctx-gate-header`, commit
`d0ace19`. The result was green (867), plus one new test (prefill size in bytes,
not characters).

| | arm 9 (no header) | arm 11 (header) |
|---|---|---|
| calls | 64 | 96 |
| status polls | 39 | 73 |
| failed calls | 0 | 4 |

The model never engaged with the header. "Trust", "Steady", "execute" and
"desk-issued" appear in its transcript only where the header was quoted. The
header made the run noisier and changed nothing about its trust behaviour. One
run, so this is a signal.

**The operator's ruling, verbatim:** "That makes complete sence now to me. And
it's right. The gate is script, The model only needs to care about the work
it's doing. It should never touch the security step."

## Pair coverage (P × L × D)

| Pair | Arms |
|---|---|
| P×L | K-no 6 · K-yes **8** · S-no 2,5 · S-yes 3,10 · F-no 1 · F-yes 4,9 |
| P×D | K-direct 6 · K-packet **8** · S-direct 2,10 · S-packet 3,5 · F-direct **9** · F-packet 1,4 |
| L×D | no-direct 2,6 · no-packet 1,5 · yes-direct **9**,10 · yes-packet 3,4,8 |

**Bold** marks the pairs only the new arms cover. With 8 and 9, every pair is
covered. Arm 10 adds no new pair; it isolates the packet (3 against 10).

Not run, and not needed for pairs: K-no-packet, K-yes-direct, F-no-direct.

## What the maps say so far (arms 1–6)

- 177 of 334 calls were `task_status`. The triple `task_status ×3` appears 97
  times across 4 arms.
- Monitor timers were used in 5 arms. Monitor errors appeared in 3, and Edit
  errors in 4.
- Every packet arm ran `session_enter → session_enter → dispatch_accept`:
  entry friction, at the offer rung.
- The file list cut the calls and polls (3 and 4 against 1 and 2). The
  cheapest arm was the one that escalated (6).
