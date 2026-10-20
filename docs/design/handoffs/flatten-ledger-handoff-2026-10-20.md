# Handoff: the flatten done, the honest forecast ledger, and the post (2026-10-20)

§1 Where to pick up · §2 What I now understand · §3 What was done · §4 Seventeen questions · §5 Risks and open gates

*Cloud session `01WpF9VeQij17q9eaens5cNb`, 2026-10-19/20. Persona: willow, by desk default
(`session_enter` did not run). Agent-reported; not ratified. For the operator's next **local**
session. The flatten's own record is [`flatten-2026-10-19.md`](../one-script/flatten-2026-10-19.md);
this handoff doesn't restate it.*

## §1 Where to pick up

Everything below is merged. Nothing from this session is waiting on a branch.

| Repo | Default branch | What landed today |
|---|---|---|
| willow-bot | `main`, release **v1.16.0** | Flatten F1–F6 and the deck reader (PR 147, v1.15.0); the market ledger (PR 149, v1.16.0) |
| willows-grove | `master`, release **v0.26.0** | The seat on the one pile and the flatten record (PR 160); the post source, figures and cover prompt (PR 162) |
| safe-app-store | `master` | The table and catgrid on the one pile (PR 226) |
| Nestor | `master` | Decisions 0249–0253, **drafts** (PR 324) |
| DispatchesFromReality | `main` | Case Study 4 and the packet brought current (PR 14) |
| rudi193-cmd (profile) | `main` | The profile README brought current (PR 1) |

Published: ["My Robot Keeps Its Receipts"](https://dev.to/sean_campbell_840bd62bf7e/my-robot-keeps-its-receipts-3h9g)
on DEV. The source is [`posts/ledger.md`](../one-script/posts/ledger.md).

**First, on the box:**

```sh
cd ~/github/willow-bot && git pull                       # main at v1.16.0
cd ~/github/willows-grove && git pull                    # master at v0.26.0+
cd ~/github/safe-app-store && git pull
```

The cloud sandbox could reach neither drand nor stooq.com (both 403), so the beacon and the price
reader have **never run live**. The box is the first place they can.

**The first live market call** (paper only):

```sh
cd ~/github/willow-bot/one-script
echo '{"symbol":"SPY","kind":"up","close_date":"YYYY-MM-DD"}' > /tmp/call.json   # a trading day ahead
echo '[{"path":"yes","p":0.55},{"path":"no","p":0.45}]'      > /tmp/dist.json
python3 -m onescript --drand forecast spy-1 --dist /tmp/dist.json --market /tmp/call.json
python3 -m onescript --drand seal-tip tip:N:HASH --proof P   # the tip it printed; before 13:00 UTC on the close date
# after the close:
python3 -m onescript --drand --prices market-reveal YYYY-MM-DD
python3 -m onescript --drand --prices market-outcome WAGER --human-key FILE
```

Have the `coin` role make the same call at 50% beside it, as the baseline.

## §2 What I now understand

The flatten's point was never tidiness. Every copy of the stream, the record, the seal or a rule
was a place where two versions could quietly disagree, and the fleet's whole promise is that a
person can trust what it says. One of each makes that disagreement impossible rather than
unlikely.

Today's three outputs are one idea. The benchmark asked whether a model knows when it doesn't
know. The ledger asks the same of whoever makes a market call, and a 50% call (Brier 0.25 either
way) is the forecaster's `ESCALATE`. The case study and the post tell that story with the
receipts attached. The ledger has no edge and claims none. Its value is a record that can't lie
about whether anyone has one.

## §3 What was done

| Step | Result | Where |
|---|---|---|
| The deck reader (F6, R1) | `onescript/deck.py`: `play.py`'s 12 questions as a reader. Parity with the frozen `play.py` over 40 seeds; mutation 9/9 | willow-bot PR 147 |
| F6 audit | R4, R5 and R6 were already in the tree, with their suites green. R1's rounds were retired by a `SUCCESSOR.md` note beside them (the operator: "a"). F6 marked done | flatten record §3 |
| Cross-repo CI | The circular checkouts were fixed: each sibling checkout takes the same-named branch, else the default. A `master`→`main` ref error of mine was fixed. Two layout bugs were found by reproducing CI's layout locally, and fixed | PRs 147, 160, 226 |
| Merged and released | 147, 160, 226, 324 merged (the operator: "merge them"); willow-bot v1.15.0, Grove v0.26.0 | — |
| The market ledger | `onescript/market.py`. A call is a wager; commitment is timed by drand's rounds against 13:00 UTC; the price reader (`--prices`, stooq) is asked again at every proposal. 42 tests; mutation 14/14 | willow-bot PR 149, v1.16.0 |
| Portfolio | Case Study 4 in DispatchesFromReality. Inventory "current home" section. Background adds grocery operations. Profile README rewritten (the operator: "1 b, 2 a, 3 a") | DFR PR 14, profile PR 1 |
| The post | Desk draft, four figures (`make_figures.py`; the fourth a seeded simulation, labelled so), cover prompt (a drawn cover was turned down and removed). Published as "My Robot Keeps Its Receipts" | Grove PR 162 |

## §4 Seventeen questions

1. Does `--drand` read the live chain from the box (`beacon.drand_reader`), and does `latest` advance?
2. Does `--prices` read a real close from stooq for `SPY` (`market.stooq_symbol` maps it to `spy.us`)?
3. Does stooq answer for an index (`^SPX`) the way `stooq_symbol` assumes?
4. Is 13:00 UTC the right deadline for you, or should a call close earlier (the night before)?
5. Which symbols and kinds should the first week of calls use?
6. Who makes calls besides you: the desk, a local model, the coin?
7. Should a seat card show market calls waiting on a seal, as it shows `wager` lines?
8. Seal or reject Nestor drafts 0249–0253 in `nestor ui`?
9. Is a first live deck round worth running alongside the market calls?
10. Should drand's BLS signature be checked (`BLS_UNVERIFIED` today) before the ledger's record counts for anything public?
11. Should the willow-bot CHANGELOG's merge-commit double entries (the Jeles note) be fixed by hand?
12. T10: the spec says `unreachable` where the tree says `escalate`. Keep the tree's answer, or rule?
13. Are the three seal paths now truly one? Read `StorySession.seal` and `table.beat_seal` on the box once.
14. Should the PR-outcome reader ("forecast your own work") come next, on the same pattern?
15. Should DispatchesFromReality's older Willow case study (Case 3) be trimmed now that Case 4 exists?
16. What does the next DEV post cover: the first week of live calls, graded?
17. What is the next single bite?

## §5 Risks and open gates

| Item | Detail |
|---|---|
| Live readers untested | drand and stooq have only run as offline stand-ins. Expect the first live run to surface something |
| The price reader is trusted | stooq's close is taken as given and re-checked at each proposal, never against a second source |
| BLS unverified | drand's signatures aren't checked; the record says so (`BLS_UNVERIFIED`) |
| Cloud-only state, gone with the container | The unpushed `f4-move-undone` backup branches (the undone F4 move, in willow-bot, safe-app-store and willows-grove), and this container's `~/.claude/settings.json` hook prefix (`WILLOW_HOME=/root`). Neither is on GitHub; the move it backed up was withdrawn by F-13 anyway |
| Nestor drafts | 0249–0253 are drafts until you seal or reject them |
| Not merged before release | Nothing. All six PRs are merged; the releases cut cleanly |
