# Flatten-2 — guesses, 2026-10-20/21

Agent-reported (Persona: willow, by Desk default — `session_enter` did not run).
These are guesses, not findings. Nothing here ratifies anything. Percentages
are the agent's judgment, not measurements. Recorded because the operator said
"record your guesses, if not already done" (CLAUDE.md rule 10: any recorded
guess carries a percentage).

Cloud session `012onBhQDT2rhEYjuoFDQtha`. The plan these belong to:
flatten-2 (F6.5 to F19, `merge_check`, `diverge`), branches `claude/flatten-2*`.

## Guesses the operator has answered

Each was put to the operator as a recommendation with a percentage. "Matched"
means the operator's answer was the recommended one.

| # | Guess | Said | Operator's answer | Outcome |
|---|-------|------|-------------------|---------|
| G1 | oakenscrolls keeps its vendored calibration (device app, "small enough to audit"), held by a parity test | 80% | "1 revert" | Matched |
| G2 | Grove's served page starts and says `unreachable` without the one script | 85% | "2 start and say unreachable" | Matched |
| G3 | Trust-owner code stays off the reach; copies held byte for byte | 90% | "1 yes" | Matched |
| G4 | Playground apps (njord, semantic-translator, the ratatosk seam) revert to self-contained copies | 75% | "safe-app-store is a playground. a parts bin" | Matched in direction (wider: all of safe-app-store) |
| G5 | Installed willow-mcp carries parity-tested copies instead of refusing | 85% | "2 carry copies" | Matched |
| G6 | `sk-` / `hf_` stay unanchored in the funnel and ratatosk | 70% | "3 yes" | Matched |
| G7 | The org repos are targets; Nestor held by parity, not repointed | 80% | "1 yes" | Matched |
| G8 | Push the integration and merge-check branches | 85% | "2 push them" | Matched |
| G9 | The side bar is a panel beside the chat in the operator's local Claude Code | 55% | "a ledger or the human prompts and the system/model outputs", Rat-only | **Missed** (it is Rat's `session.py` ledger) |
| G10 | The side bar runs with every Rat turn, not every Claude Code prompt | 60% | "I think it landed as a rat only feature" | Matched |
| G21 | `escalated` is a step after a state, not a fourth state (INVARIANTS §1 names three) | 65% | "escalated is a step, not a state, and it's just the return to 0 for the next tier." | Matched |
| G22 | The one script's ladder would not `notice` the operator's repeated {∅} (`(\{ \emptyset \})` then `({∅})`), because the two asks get different keys | **No percentage: stated as fact, not as a guess** (rule 10 broken; recorded at the operator's word "record that as a guess") | Checked against the code after recording was asked | **Half right.** No `noticed`: held. Mechanism: wrong. The first ask keys as `['emptyset']`; the second has **no words and no key at all** (`bite_key` → `None`; `∅` is category Sm), so it never reaches the ladder. Nestor's `normalize`: `'emptyset'` then `''`, an empty norm decision 0204 refuses to seal. Not scored (no percentage) |
| G11 | "If a merge check could check merge" meant checking the git merge (A) over merge_check checking itself (B) | 60% | "How much wood could a wood chuck chuck..." | Unresolved |
| G23 | Cutting the prompt hook off `Run` leaves the rows a prompt writes byte-identical | 85% | Checked by a before/after capture (hit, blank, miss, over the cap, closed box) | **Matched**: identical apart from the code's own version hash |
| G24 | The hook drops below 80 ms per prompt | 70% | Timed beside the old hook, 8 runs each | **Missed**: median 157 ms to 116 ms (bare Python 21 ms) |
| G25 | `serve._chunk_entry` splits out without moving a served byte | 80% | The same capture | **Matched** |

## Guesses still open

| # | Guess | Said | Held as |
|---|-------|------|---------|
| G12 | Recorded bites holding decomposed (NFD) text are close to none (prompts are typed) | 90% | O-2 |
| G13 | NFC on the bite and the pile together (option B) over keeping `words_v1` or NFKC | 80% | O-2 |
| G14 | The one script adopts Nestor decision 0200's bar ("the operator sees a letter on their screen, and the store treats it the same way") | 90% | O-2 |
| G15 | Combining marks are kept inside the word (no split, no delete) | 85% | O-2 |
| G16 | Nestor's mark-stripping is a proposal for Nestor (Hindi/Thai collisions), never a change made from here | 80% | O-2 |
| G17 | F18 carried copies apply to ratatosk and the willow-bot wheel too, not only willow-mcp | 80% | Included unless told otherwise |
| G18 | Side bar Q2: split by author — the human's words in the vault, model outputs in the box store, keyed hashes in the chain, forgetting as a tombstone row | 80% | O-5 |
| G19 | Close two loops first: record the rulings (flatten doc F-19 on, Nestor drafts) and check out this box | — (recommended, no number) | O-4 |
| G20 | Add merge gates 9, 10, 13, 15, 16 first | — (recommended, no number) | O-3 |

## Scoring the answered ones

Brier score: the squared distance between the percentage and what happened
(1 for matched, 0 for missed). 0 is perfect; 0.25 is a coin at 50%.

| Set | n | Brier |
|-----|---|-------|
| G1–G8, G10, G21, G23, G25 (matched) | 12 | 0.0546 |
| G9, G24 (missed) | 2 | 0.3962 |
| All fourteen resolved | 14 | 0.1034 |

| Note | Detail |
|------|--------|
| What this measures | Agreement with the operator, not truth: eight of the ten were recommendations the operator could accept or turn down. A seat that guesses what the operator will say scores well here without being right about the code. |
| The one miss | G9 was a guess about a thing outside every repo in reach; the search ran (rule 14) and found nothing by that name, and the guess filled the gap. It was wrong. |
| Precision | Whole numbers; no more accurate than that. |

## Standing permission: push this file

Set by the operator, 2026-10-21. Held here so it survives the session.

| Item | Detail |
|------|--------|
| Words | "you have permission to auto push your guesses for this session" |
| Scope | Commits that change only this file, on `claude/flatten-gaps` in willows-grove |
| Lasts | This session (`012onBhQDT2rhEYjuoFDQtha`) only |
| Not covered | Any other file, branch or repo; those still wait for the operator's word (CLAUDE.md rule 9) |
