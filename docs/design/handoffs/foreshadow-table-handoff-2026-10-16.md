# Handoff: foreshadow tests and the first-bite GM table (2026-10-16)

§1 What I now understand · §2 What was done · §3 How the GM should be served · §4 Seventeen questions · §5 Risks and open gates

*Cloud session, 2026-10-16, branch `claude/bold-goodall-9ablrs`. Persona: willow,
by desk default (`session_enter` did not run). Agent-reported; not ratified.
Files: [`seat/willow/experiments/foreshadow-2026-10-16/`](../../../seat/willow/experiments/foreshadow-2026-10-16/README.md).*

## §1 What I now understand

The operator wants an AI game master that builds the world live from the first
bite and anticipates what comes next, and the dice and records are the
evidence that it did. The fleet already holds the rule engines (Nestor's life
simulation, the-table, aetheris5e) and the serving discipline (the one
script). What's missing is the join: the GM's world facts and lore entering the
one-script record as rows, so `serve` can hand them over and the checks can
strike what wasn't served.

## §2 What was done

| Step | Result | Where |
|---|---|---|
| Peak and valley pass, three worlds | Exact odds and N=500 runs agree (≤3.7 points); peaks, valleys, pivots per world | experiment §4 |
| Predict-then-grade, Ironworks | Hasbeen heuristics 0/7; a one-seat bug found by the odds control and fixed | `runs/ironworks-grade*.json` |
| Tagging forecaster, Aetheris | 75% precision / 47% recall; vocabulary gaps named (negation, standing, ally lost, cost vs injury) | `runs/aetheris-*` |
| Setup tag, three worlds | Detector fails; 18–52% of runs reach the decision with no setup | `runs/setup-grade.txt` |
| Output rules surveyed | 15 rules from CLAUDE.md 7/15/16/17, the box stream, `seat_say` | session; summarized in §3 |
| Table session | Reset once; session 1 opened from the operator's bite (Middle-earth, Buckhorn); rule stack chosen by the operator: the box's built rule sets | `table/` |

## §3 How the GM should be served

Read from willow-bot `one-script/onescript/serve.py` and
`willow_bot/deterministic/resolvers.py`, not from memory.

| Step | Rule |
|---|---|
| Record | The human's line is a row (`who`, `bite`), kept verbatim |
| Piles | `serve.piles` groups the record by who/what/when/where; a row missing a W is in no pile |
| Scope | Code proposes the matching piles; the human seals one hash over the exact set |
| Serve | Only the sealed set, only the `PAYLOAD` fields (`family, standing, turn, verdict, reason, intent, bite`), with fresh per-check-in ids and a `human-sealed` or `untrusted` label |
| D0 | Classes G1–G5 only (route, title, id+question echo, flowering, verbatim); no class means `d0_escalate` |
| Speak | The model cites served ids; `seat_say` strikes anything the boxes lack |

Today "we're in the world of Middle-earth" serves the operator's four lines and
a gap. No lore row type or `PAYLOAD` field exists; the GM's sealed world facts
are not written into the record; rule-engine results would enter as `verdict`
rows.

## §4 Seventeen questions

1. Should the table's record move from the hand-kept `table/record.md` into a real one-script record (`checkin`, rows with W's)?
2. Which W's does a GM bite carry: who = human, what = bite, where = the scene's place, when = the turn?
3. Should a sealed world fact be its own row family, so it can be piled and served?
4. Does lore need a new `PAYLOAD` field, or a separate served table kind?
5. Who writes lore into the record: Jeles (sourced, person-verified), the operator, or both?
6. How does a Tolkien-world corpus hold citations without the text (copyright)?
7. Are ledger p3, p4 and f2 (unserved, from training) withdrawn?
8. Is "us" (the visitor's people) the operator's to seal next, before any sheet?
9. Which rule engine resolves first in play: the pool (`humans.py roll_pool`) or the d20 check (`compound.py ability_check`)?
10. Do rule-engine results enter the record as `verdict` rows written by code?
11. Do the GM's predictions become one-script wagers, graded in `reverse.reconcile_wagers` against the operator's seals?
12. Should the setup reference readings be sealed by the operator before any more grading?
13. Should the next tagger be a local model (qwen3:4b via the seat) with code checking its cites?
14. Should Nestor's life-simulation distributions be re-run on the desk, where the permission block doesn't apply?
15. Does the table's "players are never written down" law cover the bite rows, or only attendance and behaviour?
16. Should the experiment scripts become a the-table module (`apps/the-table/the_table/peaks.py`), or stay here as measurement?
17. What is the next single bite?

## §5 Risks and open gates

| Item | Detail |
|---|---|
| Reference readings | Not blind; every graded number moves with them |
| Fitted detector | The setup detector saw all three worlds first; the real test is an unread world |
| Training leak | The session's GM used its own knowledge of Middle-earth (palantír, hobbit, the Shire) before the serving question was asked; marked in the ledger |
| Scratchpad loss | The session's scratchpad is reclaimed with the container; everything needed is in this branch |
| Commit rule | Rule 5 needs the human's recorded authorization: the operator asked for this push in the session ("lets push everything needed and a handoff", "branch") |
