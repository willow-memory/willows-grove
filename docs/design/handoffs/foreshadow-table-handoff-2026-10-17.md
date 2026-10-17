# Handoff: the table in one-script, the forged-seal fix, and a forecasting game (2026-10-17)

§1 Where to pick up · §2 What I now understand · §3 What was done · §4 Seventeen questions · §5 Risks and open gates

*Cloud sessions, 2026-10-16/17, two of them. Persona: willow, by desk default
(`session_enter` did not run in either). Agent-reported; not ratified. Follows
[`foreshadow-table-handoff-2026-10-16.md`](foreshadow-table-handoff-2026-10-16.md),
whose Q1 this answers. The second session reviewed PR 137, grew it until it
merged, then built and played a forecasting game on public randomness; §3's
last eight rows and all of §4 and §5 are its.*

## §1 Where to pick up

| Repo | Branch | State |
|---|---|---|
| willows-grove | `claude/intelligent-bohr-dm1up4` | Pushed, with a PR to `master`: the table's one-script record, its importer and break test (from `claude/cool-volta-hfkg92`), the forecasting game and its 7 rounds, and this handoff |
| willow-bot | `main` | [willow-memory/willow-bot#137](https://github.com/willow-memory/willow-bot/pull/137) **merged** 2026-10-17, head `c46416a`, 9 commits, CI green on 14 of 14 checks (Python 3.10–3.14) |

To run the table in a new container:

```sh
git clone https://github.com/willow-memory/willow-bot ../willow-bot   # beside willows-grove
cd ../willow-bot                                                     # main carries PR 137
python3 -m venv /tmp/v && /tmp/v/bin/pip install ruff==0.16.7 pytest cryptography
cd ../willows-grove/seat/willow/experiments/foreshadow-2026-10-16/table
ONESCRIPT_PYTHON=/tmp/v/bin/python ONESCRIPT_VENV=/tmp/v \
  python3 -I onescript_table.py propose "<the human's next line>"     # after the seal
```

A new container has no serve key: run `python3 -m onescript checkin` (with
`--box`, `--keys`, `--venv`) before `propose`, or it says so and stops. The
desk's keys file is `~/.willow/table-keys/keys.json`, made fresh. It is never
committed and holds no human key.

The first verb `main`'s code runs on `table/box/` writes one `pin` row after
its invocation row (§3). The table's box has no anchor and no seal rows, so
its pin names no tip and changes nothing that counts.

## §2 What I now understand

The table's record is a real one-script record, so the GM's facts reach the
model only through a scope the human sealed. Breaking it showed the seal was
the weak point: a row that *said* `who: human` was taken as the human's word.
Reviewing the fix showed the same mistake in a second place: the human's
signed tip proves the rows up to it never change, not that the human wrote
each of them. So nothing that grants authority may rest on a row's own
fields or on the tip alone; each seal carries its proof, an old proofless
seal counts only up to a tip the code pinned before it could be forged
around, and a wager's outcome is inside what the human signs.

## §3 What was done

| Step | Result | Where |
|---|---|---|
| Table → one-script | `table/box/record.jsonl`: check-in (all four gates satisfied), one desk `turn` per human line with the bite verbatim, then the scope card. 27 rows, chain unbroken. Nothing sealed | experiment README §5 |
| Pending | s1–s3 (sealed in chat), p1, p2 in `table/pending.jsonl`, awaiting the scope seal. p3, p4 held out (training, Q7). f1, f2 stay in `ledger.json` | `table/` |
| Break test, round 1 | 15 attacks on scratch copies. Two importer breaks fixed. One one-script break: A5, a hand-forged seal row unlocked serve | experiment README §7 |
| A5 fix | PR 137 re-verifies seal proofs; `bbc1a42` added old seals inside the sealed tip and the awaiting list reading verified seals | willow-bot PR 137 |
| Break test, round 2 | Suite 8× in random order: 488 passed, 1 skipped. Round-1 attacks and 8 new ones on the fix: all hold | first session |
| Review of PR 137 | `code-review` skill, 10 findings; #1–#3 read by hand. #6 closed by the human as no change. The rest fixed | second session |
| Fixes #1–#5, #8–#10 | `79432e8` old Nestor rows (#2); `863bfaf` an unreachable newer seal no longer hides a verified one in `resume` (#3); `6abad4d` `resume` takes the row that verifies, not any row over a held subject (#1); `9ba8e17` pair shape before keyring, `unreachable` kept on the morning screen, `held` by a handed key, one read of the record, `serve.sealed` → `claimed_seals` (#4, #5, #8, #9, #10) | willow-bot PR 137 |
| #6, option B | `6674497`: `--verifier`'s help says it filters one seal call and binds no later reader. A standing per-verifier allow-list (option C) waits until the keyring holds a second human | willow-bot PR 137 |
| #7 and the cutoff | A probe showed a forged outcome row graded as the human's once a later tip seal covered it, and the same gap in the old-seal rule. The human: the code settles the cutoff. `688dcf9`: the first verb pins the anchor; proofless seals count only up to the pinned tip. `c46416a`: the human seals `wager:` + one hash over wager and outcome. Probe: reconciled before, escalates after | willow-bot PR 137 |
| Checks | `onescript` suite 502 passed, 1 skipped, on the container's Python only. `ruff` 0.16.7 clean. Every fix's new tests fail on the commit before it, except the wager tests, which can't import the old code | second session |
| PR 137 merged | Description rewritten to match the head; CI green on 14 of 14 checks; merged by the human | willow-bot `main` |
| Forecasting game | `seat/willow/experiments/predictions-2026-10-17/play.py`: forecasts while a [drand](https://drand.love) beacon round is still ahead, then the beacon's randomness seeds the data and code grades by Brier score beside a coin flip and the exact odds. 12 questions; each simulated rate matched its exact odds. 7 rounds, 28 questions, every forecast committed before its beacon. Final: human 0.15971, oracle 0.15988, desk 0.15991, coin flip 0.250. A lead that small is noise | experiment README §5 |

## §4 Seventeen questions

1. Does the human seal the table's scope (`table/scope-card.json`) next?
2. Is that seal an HMAC proof or a Nestor pair (the APK path)?
3. Which line is the human's next bite, the one that carries the pending proposals?
4. Are s1–s3 sealed as one-script proposals one by one, or does the chat seal count as already given?
5. Are p3 and p4 withdrawn (old Q7)?
6. Do f1 and f2 become one-script wagers, now that a wager's outcome is signed (old Q11)?
7. Should a verb exist to seal a wager outcome, by key and by Nestor pair (none does today)?
8. On the human's own box, was the anchor file present and readable when `main`'s code first ran, so its old seals stayed pinned?
9. Roughly how many seal rows on the human's own box predate PR 137?
10. Should the human seal a tip on the table's box, so a cut can be seen (A7)?
11. Does `table/box/` stay in git, given that anyone with push can append to it?
12. Does lore get a `PAYLOAD` field, so a sealed `world/*.md` reaches the model (old Q4)?
13. When will the keyring hold a second human, which is when #6's option C (per-verifier subject prefixes) is due?
14. Should the forecasting game keep going, and should it ask questions whose odds the desk has not worked out (so the desk's own forecasts test something)?
15. Should the game's forecasts become one-script `wager` rows, sealed `wager:` subjects graded by the beacon instead of by hand?
16. Should `play.py` verify the drand BLS signature (it stores it, unchecked)?
17. What is the next single bite?

## §5 Risks and open gates

| Item | Detail |
|---|---|
| The pin's one gap | Rows a forger wrote before a box first ran PR 137's code still count, as on `main` |
| Missing anchor at first run | Its pin names no tip, and every old proofless seal on that box stops counting: those scopes and proposals must be sealed again |
| Old outcome seals | An outcome sealed over the bare wager hash counts for nothing. None are on record |
| A7 | With no sealed tip, cutting the record's last rows is not seen. One-script's documented limit |
| Nestor store unreachable with a real signature | Not exercised: it needs a signed pair. Tests cover the no-keyring and malformed-pair cases |
| The scratch venv | Gates satisfied only with a hand-made venv (ruff 0.16.7, pytest, cryptography); the container's own Python has no pytest |
| The game's beacon | drand's BLS signature is stored per round, not verified; the game trusts `api.drand.sh` for the randomness |
| The desk's forecasts | The desk wrote the deck and checked its exact odds, so its forecasts are oracle-informed; only the human's test anything |
| Commit rule | Rule 5: the human's words, first session: "push it, and then we're going to push it and try to break it", "fix A5 in willow-bot", "Add it onto PR 137", "update the handoff please, and push for the next session to pick up on the correct branch". Second session: "fix #2 on PR 137", "fix #3 on PR 137", "fix #1 on PR 137", "Line the rest up as todos, and fix. you have the context.", "close #6", "do option B on PR 137", "The code should mostly settle it on its own. The deterministic system is the point.", "do it on PR 137", "update the PR 137 description", "update the handoff and push it", "Let's play with data now. I want to keep predicting random things", "end after this round", "Wrap up what was done in a handoff and pr it." |
