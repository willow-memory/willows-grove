# Predictions 2026-10-17 — successor

§1 Status · §2 Where new rounds go · §3 What maps where · §4 Why this file

## §1 Status

| Item | State |
|---|---|
| This experiment (`play.py`, `export.py`, `README.md`, `rounds/001–007.json`) | Frozen (willows-grove CLAUDE.md rule 12). Kept as written, not authoritative for new rounds |
| Successor | willow-bot `one-script/onescript/deck.py` (flatten F6, R1; willow-bot `f061518`) |
| Decided | 2026-10-20, the operator: "a" (leave the rounds frozen, note the successor beside them) |

## §2 Where new rounds go

| Step | Here (frozen) | Now |
|---|---|---|
| Open a round | `play.py open` | Pick a drand round still ahead; a forecast names it |
| Forecast | `play.py forecast R WHO q=p` | `python3 -m onescript forecast ID --dist FILE --deck FILE` (`{question, beacon_round}`; yes/no; one per round, question and role) |
| Commit | the round file's own refusal after the round | The human seals the tip the forecast printed (`seal-tip`) |
| Reveal | `play.py reveal R` | `python3 -m onescript --drand deck-reveal ROUND` (`deck` verdict rows) |
| Grade | `play.py board` (Brier) | `deck-outcome WAGER` proposes; the human's `seal-outcome`; `reconcile` (Brier) |

## §3 What maps where

| Here | There | Held equal by |
|---|---|---|
| `DECK` (12 questions), its draws and exact odds | `deck.DECK`, `deck.answer`, `deck.odds` | `onescript/tests/test_deck.py`: every draw and odds over 40 seeds × 12 questions |
| `Stream` | `onescript/stream.py` (`sha256-stream/v1`) | the same test, and `test_stream.py` |
| `rounds/*.json` | not imported: their forecasts sit under no tip the human sealed, so the chain can't show they came first | — |

## §4 Why this file

The rounds are a frozen record; a later note goes beside them, never into them (rule 12). This file exists so a reader who finds `play.py` knows it is no longer where rounds are played, and where they are.
