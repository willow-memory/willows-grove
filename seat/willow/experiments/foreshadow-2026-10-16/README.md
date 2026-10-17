# Foreshadow and the AI GM table (2026-10-16)

§1 What this is · §2 Files · §3 Run it · §4 Results · §5 The table session · §6 Limits · §7 Break test

## §1 What this is

A cloud session tested whether the fleet's game pieces (safe-app-store
`apps/the-table`, `apps/ai-game-master`, `aetheris5e`) and the one script
(willow-bot `one-script`) can anticipate what comes next in a story. Then it
turned the AI game master around, so it builds the world from the first bite.
Agent-reported; nothing here is ratified. Handoff:
[`docs/design/handoffs/foreshadow-table-handoff-2026-10-16.md`](../../../../docs/design/handoffs/foreshadow-table-handoff-2026-10-16.md).

## §2 Files

| File | What it does |
|---|---|
| `harness.py` | First pass: average foreshadow coverage, with one-script `predict.declare`/`grade` as the backward-counting forecaster |
| `peaks.py` | The peak and valley pass: exact 2d6 path odds beside N seeded runs of the real `StorySession`, rotating seats like `StorySession` does |
| `predict.py`, `grade.py` | Predict-then-grade (Ironworks): claims from the world file alone, hashed before the run; the grader refuses a prediction written after the run |
| `predict_tags.py`, `grade_tags.py` | The outcome-tagging forecaster (Aetheris): a five-tag keyword list (exposure, injury, insight, setback, trust) |
| `setup_pass.py`, `setup_probe.py` | The setup tag: does an outcome set up the decision beat? Phrase-match detector and probe |
| `runs/` | Every run, prediction, grade and reference reading, as produced (the one-seat Ironworks run is kept: `*-v1-oneseat.json`) |
| `table/` | The table session's record and ledger (fiction) |
| `table/onescript_table.py` | Moves `table/record.md` into a one-script box (`table/box/`): `migrate`, then `propose` after the human seals the scope |

## §3 Run it

Sibling checkouts are found beside this repo, or by `THE_TABLE_DIR` and
`ONESCRIPT_DIR`.

```sh
W=../../../../../safe-app-store/apps/the-table/worlds
python3 -I peaks.py $W/hasbeen.json 500
python3 -I predict.py $W/ironworks.json p.json   # before the run
python3 -I peaks.py $W/ironworks.json 500 > r.json
python3 -I grade.py p.json r.json $W/ironworks.json
```

Same seed, same result. Moved here from the session's scratchpad, the Hasbeen and Ironworks runs reproduced exactly.

## §4 Results

| Pass | Result |
|---|---|
| Hasbeen, coverage | one-script `predict` foresaw the decision beat 0% of the time (it had never seen one); the cast is foreshadowed only on b1 strong (54.4% suggested / 42.2% random) |
| Hasbeen, peaks | b2 is the biggest swing (1.48 of 1.58 bits); Gerald appears only via b1 strong or b2 miss; 35% of runs never meet him; no path names the Architect |
| Ironworks, predict-then-grade | Heuristics carried over from Hasbeen: 0/7. Odds control: 2/4. The control caught a one-seat bug, fixed in `peaks.py` (Hasbeen unchanged). There the dice change who knows what, not who appears |
| Aetheris, tagging | Odds 8/8; tagger 75% precision, 47% recall; exposure and injury forecast within 2 points; insight 58% forecast vs 100% actual; pivot b3 (Kesh) by the reference reading |
| All three, setup | The phrase detector fails (Hasbeen 0/3, Ironworks 0/1 with 4 false positives, Aetheris 2/3 with 1 by luck). By the reading, runs that reach the decision with no setup: Hasbeen 22%, Ironworks 52%, Aetheris 18%. Setup sits mostly on strong outcomes (4 of 7), not the miss path |

The reference readings (`runs/aetheris-reference.json`,
`runs/setup_reference.json`) are an agent's DRAFT, not blind; the operator
seals or corrects them, and every graded number moves with them.

## §5 The table session

`table/record.md` is session 1 of the AI GM built from the first bite (Middle-earth, a
visitor from Buckhorn come to see "this here machine" that predicts the
future); `table/record-session-0.md` is the reset first attempt. `table/ledger.json`
holds proposals and predictions, out of the chat by the operator's rule.

Since then the record is also a one-script record, `table/box/record.jsonl`
(27 rows, chain unbroken). It holds a check-in with all four gates satisfied,
then one desk `turn` per human line with the bite verbatim, then the scope card
(`table/scope-card.json`, stack `who=desk`). `record.md` stays as it was.

| Waiting | On |
|---|---|
| The scope's subject in `scope-card.json` | The human's seal (`python3 -m onescript seal serve:<hash>`, a proof or a Nestor pair) |
| `table/pending.jsonl`: s1–s3 (sealed in chat), p1, p2 | That seal; then `onescript_table.py propose "<next line>"` serves the scope, cites it, and sends them through the next turn as proposals, each awaiting its own `proposal:<hash>` seal |
| p3, p4 | Held out of pending: they rest on training (Q7) |
| f1, f2 | Stay in `ledger.json`; one-script wagers are Q11 |

The served view carries each line as a `turn_open` `intent` under `who=desk`.
One-script records the desk that typed the turn, not the human. A sealed
`world/*.md` lands in the box as a file, but its text is not in serve's
`PAYLOAD`, so lore is still not served (Q4).
Proposals p3, p4 and prediction f2 rest on the agent's training, not on anything
served. Under one-script `serve` they would be struck (handoff §4).

## §6 Limits

| Limit | Detail |
|---|---|
| No model | No Ollama in the cloud container; every tagger is code |
| Fitted | The setup detector was written after reading all three worlds |
| Not run | Nestor's life-simulation distributions (`humans.py --distribution 500`): blocked in the session by a permission check |

## §7 Break test

2026-10-17. Each attack ran on a scratch copy of `table/` with a throwaway human
key; the real box was not touched.

| # | Attack | Result |
|---|---|---|
| A1 | `propose` before any seal | Refused: serve is `empty` |
| A2 | A human line that starts with `-` (`-h`, `--proposal=…`) | **Broke the importer**: argparse took it as a flag. Fixed: `--` before every bite |
| A3, A4 | Keys readable by others; keys inside the box | Refused |
| A5 | A `seal` row appended by hand with a correct chain hash, no key | **Broke one-script**: serve populated, and all five proposals passed. A seal row carries no proof, and `serve.sealed()` trusts any `who: human` row. Nothing is anchored, so the chain can't see it |
| A5b | The same forgery over a proposal | Nothing written (`write_proposal` runs only after a real seal), but `pooled` hides the forged proposal as sealed |
| A6 | Edit a past bite | Caught: hard close, chain broken |
| A7 | Cut the last rows | Not caught: no tip is anchored (one-script's own documented limit) |
| A8 | Widen the sealed spec in `scope-card.json` | Refused: the seal covers that exact set |
| A9 | Hostile pending rows (`record.jsonl`, `../`, an extra key, an empty claim) | Each refused, by its rule |
| A11 | `propose` twice | Duplicate rows; `pooled` keeps one per subject |
| A12 | `record.md` with an unquoted line, a doubled space, a gap in numbering, CRLF | **Broke the importer**: each line was skipped silently (CRLF: all of them). Fixed: every line is read or the run stops |
| A14 | Seal, a new check-in, then `propose` | Works: the spec pins the stack. In a new container `propose` needs `onescript checkin` first, and now says so |
| A15 | Seal, then a new human turn, then `propose` | Works |

A5 is fixed in willow-bot, in [willow-memory/willow-bot#137](https://github.com/willow-memory/willow-bot/pull/137)
(open, CI green): a seal row carries its proof or Nestor pair, and every reader
checks it again. Re-tested 2026-10-17: the attacks above, plus 8 aimed at the
fix, all hold (handoff
[`foreshadow-table-handoff-2026-10-17.md`](../../../../docs/design/handoffs/foreshadow-table-handoff-2026-10-17.md)).

