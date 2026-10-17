# Predicting random things (2026-10-17)

§1 What this is · §2 Play · §3 Scoring · §4 Limits · §5 Results (2026-10-17)

## §1 What this is

A forecasting game on seeded random data. Each round names a
[drand](https://drand.love) beacon round that hasn't happened yet. Forecasts
are written while it is still in the future; the script refuses one after.
When the beacon publishes, its randomness seeds the data, code works out each
answer, and every forecaster is graded. Nobody, the agent included, can know
the data before forecasting.

## §2 Play

| Step | Command |
|---|---|
| Open a round (questions are picked by an already-public beacon) | `python3 -I play.py open [--ahead N]` |
| Forecast: the chance each question comes out "yes" | `python3 -I play.py forecast R WHO q=0.4 q2=70% …` |
| Reveal and grade, once the beacon is out | `python3 -I play.py reveal R` |
| Running scores | `python3 -I play.py board` |

The 12 questions are in `play.py` (`DECK`): dice, coins, cards, shuffles,
birthdays. Four per round.

## §3 Scoring

Brier score per question, `(p − outcome)²`, averaged; lower is better. Two
baselines ride every round: **coin flip** (50% on everything, scores 0.25)
and **oracle** (the exact probability, worked out by code, shown only at
reveal). Beating the oracle over many rounds is luck; matching it is skill.

## §4 Limits

| Limit | Detail |
|---|---|
| Beacon not verified | The drand BLS signature is stored in the round file, not checked (no BLS library in the standard library) |
| The agent knows the odds | It wrote the deck and its exact-odds checks, so its forecasts are oracle-informed. The human's forecasts are the real test |
| One forecast per player per round | A forecast stands once written; no edits |

## §5 Results (2026-10-17)

Seven rounds, 28 questions, beacon rounds 6558962 to 6559022. Every
forecast was written 6 to 10 beacon rounds before its data existed; none
was refused or edited. Round files: `rounds/001.json` to `rounds/007.json`.

| Rank | Who | Questions | Mean Brier |
|---|---|---|---|
| 1 | human | 28 | 0.15971 |
| 2 | oracle | 28 | 0.15988 |
| 3 | willow (the desk) | 28 | 0.15991 |
| 4 | coin flip | 28 | 0.250 |

The three are 0.0002 apart: noise. The human's one large miss was round 1's
`3d6` (12% against 26%); from round 4 on, every human forecast sat within a
few points of the exact odds.
