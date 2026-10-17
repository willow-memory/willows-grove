# Handoff: the table in one-script, and the forged-seal fix (2026-10-17)

§1 Where to pick up · §2 What I now understand · §3 What was done · §4 Seventeen questions · §5 Risks and open gates

*Cloud session, 2026-10-16/17. Persona: willow, by desk default (`session_enter`
did not run). Agent-reported; not ratified. Follows
[`foreshadow-table-handoff-2026-10-16.md`](foreshadow-table-handoff-2026-10-16.md),
whose Q1 this answers.*

## §1 Where to pick up

| Repo | Branch | State |
|---|---|---|
| willows-grove | `claude/cool-volta-hfkg92` | Pushed. The table's one-script record, its importer, the break test, and this handoff. No PR |
| willow-bot | `claude/wizardly-dijkstra-va6dic` | Pushed: [willow-memory/willow-bot#137](https://github.com/willow-memory/willow-bot/pull/137), open, CI green, mergeable. Waiting on the human's review |
| willow-bot | `claude/cool-volta-hfkg92` | **Not this one.** It existed only in the container, held an earlier fix (`af5876c`) that PR 137 replaces, and was never pushed |

To run the table in a new container:

```sh
git clone https://github.com/willow-memory/willow-bot ../willow-bot   # beside willows-grove
cd ../willow-bot && git checkout claude/wizardly-dijkstra-va6dic      # main, once 137 merges
python3 -m venv /tmp/v && /tmp/v/bin/pip install ruff==0.16.7 pytest cryptography
cd ../willows-grove/seat/willow/experiments/foreshadow-2026-10-16/table
ONESCRIPT_PYTHON=/tmp/v/bin/python ONESCRIPT_VENV=/tmp/v \
  python3 -I onescript_table.py propose "<the human's next line>"     # after the seal
```

A new container has no serve key: run `python3 -m onescript checkin` (with
`--box`, `--keys`, `--venv`) before `propose`, or it says so and stops. The
desk's keys file is `~/.willow/table-keys/keys.json`, made fresh. It is never
committed and holds no human key.

## §2 What I now understand

The table's record is now a real one-script record, so the GM's facts can only
reach the model through a scope the human sealed. Breaking it showed that the
seal itself was the weak point: a row that *said* `who: human` was taken as the
human's word. The fix makes every seal carry its evidence and every reader
check it again. That fix belongs to one-script, not to the table.

## §3 What was done

| Step | Result | Where |
|---|---|---|
| Table → one-script | `table/box/record.jsonl`: check-in (all four gates satisfied), one desk `turn` per human line with the bite verbatim, then the scope card. 27 rows, chain unbroken. Nothing sealed | experiment README §5 |
| Pending | s1–s3 (sealed in chat), p1, p2 in `table/pending.jsonl`, awaiting the scope seal. p3, p4 held out (training, Q7). f1, f2 stay in `ledger.json` | `table/` |
| Break test, round 1 | 15 attacks on scratch copies. Two importer breaks (a `-` line taken as a flag; malformed lines skipped without an error) are fixed. One one-script break: A5, a hand-forged seal row unlocked serve | experiment README §7 |
| A5 fix | PR 137 (another session) re-verifies seal proofs. Added on top (`bbc1a42`): a proofless old seal holds only inside the human's sealed tip, and the morning screen's awaiting list reads verified seals. 3 new tests | willow-bot PR 137 |
| Break test, round 2 | Suite 8× in random order: 488 passed, 1 skipped. Round-1 attacks replayed: all hold. 8 new attacks on the fix (a pasted proof, a seal inside a rehashed tip, wrong-typed proofs, a deleted anchor, a swapped key, 3,000 forged seals): all hold. A full-gate check-in and the table path pass on the fixed code | this handoff §5 |

## §4 Seventeen questions

1. Is PR 137 reviewed and merged as it stands, or does the `unreachable` state need a different shape?
2. Once 137 merges, is the human's own box re-sealed scope by scope, or under one sealed tip?
3. Does the human seal the table's scope (`table/scope-card.json`) next?
4. Is that seal an HMAC proof or a Nestor pair (the APK path)?
5. Which line is the human's next bite, the one that carries the pending proposals?
6. Are s1–s3 sealed as one-script proposals one by one, or does the chat seal count as already given?
7. Are p3 and p4 withdrawn (old Q7)?
8. Does lore get a `PAYLOAD` field, so a sealed `world/*.md` reaches the model (old Q4)?
9. Should the served trust label read `human-sealed` when the scope is sealed, not only the table hash?
10. Should a turn record the human as `who`, or is "the desk that typed it" the right line?
11. Do f1 and f2 become one-script wagers (old Q11)?
12. Should the human seal a tip on the table's box, so a cut can be seen (A7)?
13. Does `table/box/` stay in git, given that anyone with push can append to it (the forgery is now harmless; a cut is not, without a tip)?
14. Should `onescript_table.py` move into one-script as a general "import a hand record" verb?
15. Is the 2026-10-16 handoff's Q2 (which W's a bite carries) settled by `who=desk`, or should a bite carry `where`?
16. Should willow-bot's tests gate run under a venv the box names, so a cloud check-in needs no hand-made venv?
17. What is the next single bite?

## §5 Risks and open gates

| Item | Detail |
|---|---|
| PR 137 not merged | Until it merges, `main` still trusts a seal row's `who` |
| Old seals after 137 | A seal row with no proof, outside a sealed tip, stops counting. Scopes sealed that way must be sealed again |
| A7 | With no sealed tip, cutting the record's last rows is not seen. One-script's documented limit |
| Nestor store unreachable with a real signature | Not exercised here: it needs a signed pair. PR 137's tests cover the no-keyring case |
| The scratch venv | Gates satisfied only with a hand-made venv (ruff 0.16.7, pytest, cryptography); the container's own Python has no pytest |
| Commit rule | Rule 5: the human's words this session: "push it, and then we're going to push it and try to break it", "fix A5 in willow-bot", "Add it onto PR 137", "update the handoff please, and push for the next session to pick up on the correct branch" |
