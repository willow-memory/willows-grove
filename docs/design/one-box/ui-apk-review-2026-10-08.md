# The UI and APK review, the phone proposes, and chat from boxes (2026-10-08)

*A Claude Code cloud session (started with every willow-memory repo attached,
branch `ccr-cb58d6e2-ehrzfe`, `session_enter` not run because the Grove MCP
servers needed authorization, `Persona: willow` by default). It reviewed the
Grove served page and the phone APK with deterministic checks first, recorded
that the phone only proposes, walked the one script's box flow, pulled in
willow-mcp PR 712, and thought through chat for small local models. The full
record is PR #126 (`docs/design/phone-seat-production.md`,
`docs/design/one-script/local-flow-and-ui.md`) and willow-mcp PR #714. The
operator's words are quoted verbatim. Everything else is the agent's reading.
Every box is `unattested`.*

## The notes (the source)

### JE · The review, checks first

- **The ask.** "I would like to talk over the UI, and more loosely, the apk. Quite a bit has changed since I last really played with them, so we're going to need a review." and "Run the deterministic scripts as much as you can before the reasoning comes in."
- **The stale branch.** The session branch was 126 commits behind `master`, which held CLAUDE.md rules 7–17 and the Watch reserved; fast-forwarded locally before anything was judged.
- **The Grove suites.** On `master` 8979d68: 751 unit tests passed, 12 skipped; Playwright e2e 36 of 36; docs-drift clean; ci-security-grep 7 hits, all allowlisted; hook wiring matched its sealed rows.
- **The page as served.** With no database and no willow-mcp: chat read-back unreachable, dispatch unreachable with its reason, envelopes empty, each distinct. Three of eight components render; card and cast-chip are loaded but unused, lens-switch is not loaded.
- **The APK tests blocked.** Running `safe-app-store`'s tests was denied by the permission classifier (an unattached repo), so the APK review was a read of the code only.

### JF · The APK as found

- **Last touched.** `apps/jarvis` web layer unchanged since 2026-09-06, package still named `jarvis`, `versionCode 1`.
- **Backup.** `android:allowBackup="true"`, while the Anthropic key and the willow-mcp tokens sit in app-private Preferences.
- **Key in the WebView.** The Anthropic SDK runs in the page with `dangerouslyAllowBrowser: true`.
- **The port policy.** `:8766` refused with a plain message, `:8768` the sign-in target; the PKCE sign-in was never completed end to end, and cleartext to loopback from an `https` page is unverified (55%).
- **The simplification.** "Well, I think a lot of this is going to change with the deterministic scripts. I think this is going to be a lot more simple in a way." The UI reduces to the one script's five screens: check-in, scope, served view, proposals, check-out.

### JG · The phone only proposes

- **The safest shape asked for.** "It doesn't have to be on term X but think of the safest way that this can be done, for example, like I know servers live on anthropic servers but for what we're asking the small local models to do I feel like a lot of that could be run just on a phone with rat in the package"
- **What the code needs.** Rat `--onescript` is standard library only and refuses cloud rungs; the one script is standard library plus `sqlite3`, with `cryptography` only for ed25519 seals.
- **The proposed shape.** One APK, embedded Python, the model as an in-process library so the app can drop `INTERNET` (a loopback server on a phone is open to every app on it), `allowBackup` off, sync over USB.
- **The decision.** "Phone only proposes, seal in Nestor on the box" A phone turn starts and ends on the box: served file in over USB, proposals out over USB.
- **Where it was written.** "Just in the grove for now" Recorded in `phone-seat-production.md`; no key, keyring or `cryptography` on the phone.

### JH · The one script, local first

- **Local first.** "Back to the local,  because that's where I need to be working first." and "All of that, and how it works with the UI."
- **The box walk.** Check-in hard-closed on ruff 0.16.10 against the 0.16.7 pin, then opened; scope gave subject `serve:167bfe94…`; serve without a seal answered empty; turn graded one `link_fail` and one `refused`; the walk stopped at the first seal.
- **PR 712 pulled in.** "Also need to pull in -mcp PR712, which is about to merge" `onescript_run_execute` runs the eight host steps with no shell; its own tests 126 passed; the full suite's 11 failures fail the same on `master` (running as root, the egress proxy).
- **The write-up.** "Write up the doc, and put those file types under git ignore" `local-flow-and-ui.md`: the ten-step flow through the verb, the local-model table, five read-only Grove panels; three tracked `.pyc` files untracked in willow-mcp.
- **The PRs.** "Pr please" willows-grove #126 and willow-mcp #714, each ending in `Ratified-by`.

### JI · Chat from boxes

- **Small models don't chat.** "Well I've been trying to figure out how the chat part of all of this will work. I mean I'm running 99% of it on local small models and they don't chat well. But I do have an idea for it but I want you to start thinking about that"
- **The hash line.** "Well I think you found it on the hash line. Like if those strings of boxes were reported to a small agent or small model then it could probably form a sentence out of them pretty quickly you know if it's served five boxes say"
- **Which five.** "I mean think about the plethora of of boxes that are now in this context session. What would you hand to a small model to create a sentence" Code picks them in the morning screen's order: needs you, changed, decided, blocked, routine passes as one box.
- **Keeping the sentence honest.** Every sentence cites its box ids, every served box is cited, no number or name the boxes don't hold; a failed check falls back to a sentence code fills in; hashes, paths and verbatim words never go to the model.
- **Why the sessions run in boxes.** "So why do you think I've been having sessions for the last few days run entirely inside of boxes?" The agent's reading (80%): the big models are making the substrate the small models will speak from. Then "yes add to the grid".

## Grid

<!-- cross-table:grid -->
| | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| **JE** The review, checks first | The ask | The stale branch | The Grove suites | The page as served | The APK tests blocked |
| **JF** The APK as found | Last touched | Backup | Key in the WebView | The port policy | The simplification |
| **JG** The phone only proposes | The safest shape asked for | What the code needs | The proposed shape | The decision | Where it was written |
| **JH** The one script, local first | Local first | The box walk | PR 712 pulled in | The write-up | The PRs |
| **JI** Chat from boxes | Small models don't chat | The hash line | Which five | Keeping the sentence honest | Why the sessions run in boxes |
<!-- /cross-table:grid -->

## Sources

<!-- cross-table:sources -->
| Row | What it holds | Source |
|---|---|---|
| JE | The review, checks first | the notes, section JE (operator words verbatim where quoted; the rest the agent's reading) |
| JF | The APK as found | the notes, section JF (operator words verbatim where quoted; the rest the agent's reading) |
| JG | The phone only proposes | the notes, section JG (operator words verbatim where quoted; the rest the agent's reading) |
| JH | The one script, local first | the notes, section JH (operator words verbatim where quoted; the rest the agent's reading) |
| JI | Chat from boxes | the notes, section JI (operator words verbatim where quoted; the rest the agent's reading) |
<!-- /cross-table:sources -->

## Index

<!-- cross-table:index -->
| Cell | Rule | Source | Share | Standing |
|---|---|---|---|---|
| JE1 | - **The ask.** "I would like to talk over the UI, and more loosely, the apk. Quite a bit has changed since I last really played with them, so we're going to need a review." and "Run the deterministic scripts as much as you can before the reasoning comes in." | `willows-grove/docs/design/one-box/ui-apk-review-2026-10-08.md`:18 | 4.98% | unattested |
| JE2 | - **The stale branch.** The session branch was 126 commits behind `master`, which held CLAUDE.md rules 7–17 and the Watch reserved; fast-forwarded locally before anything was judged. | `willows-grove/docs/design/one-box/ui-apk-review-2026-10-08.md`:19 | 3.51% | unattested |
| JE3 | - **The Grove suites.** On `master` 8979d68: 751 unit tests passed, 12 skipped; Playwright e2e 36 of 36; docs-drift clean; ci-security-grep 7 hits, all allowlisted; hook wiring matched its sealed rows. | `willows-grove/docs/design/one-box/ui-apk-review-2026-10-08.md`:20 | 3.88% | unattested |
| JE4 | - **The page as served.** With no database and no willow-mcp: chat read-back unreachable, dispatch unreachable with its reason, envelopes empty, each distinct. Three of eight components render; card and cast-chip are loaded but unused, lens-switch is not loaded. | `willows-grove/docs/design/one-box/ui-apk-review-2026-10-08.md`:21 | 5.06% | unattested |
| JE5 | - **The APK tests blocked.** Running `safe-app-store`'s tests was denied by the permission classifier (an unattached repo), so the APK review was a read of the code only. | `willows-grove/docs/design/one-box/ui-apk-review-2026-10-08.md`:22 | 3.28% | unattested |
| JF1 | - **Last touched.** `apps/jarvis` web layer unchanged since 2026-09-06, package still named `jarvis`, `versionCode 1`. | `willows-grove/docs/design/one-box/ui-apk-review-2026-10-08.md`:26 | 2.28% | unattested |
| JF2 | - **Backup.** `android:allowBackup="true"`, while the Anthropic key and the willow-mcp tokens sit in app-private Preferences. | `willows-grove/docs/design/one-box/ui-apk-review-2026-10-08.md`:27 | 2.41% | unattested |
| JF3 | - **Key in the WebView.** The Anthropic SDK runs in the page with `dangerouslyAllowBrowser: true`. | `willows-grove/docs/design/one-box/ui-apk-review-2026-10-08.md`:28 | 1.89% | unattested |
| JF4 | - **The port policy.** `:8766` refused with a plain message, `:8768` the sign-in target; the PKCE sign-in was never completed end to end, and cleartext to loopback from an `https` page is unverified (55%). | `willows-grove/docs/design/one-box/ui-apk-review-2026-10-08.md`:29 | 3.96% | unattested |
| JF5 | - **The simplification.** "Well, I think a lot of this is going to change with the deterministic scripts. I think this is going to be a lot more simple in a way." The UI reduces to the one script's five screens: check-in, scope, served view, proposals, check-out. | `willows-grove/docs/design/one-box/ui-apk-review-2026-10-08.md`:30 | 5.08% | unattested |
| JG1 | - **The safest shape asked for.** "It doesn't have to be on term X but think of the safest way that this can be done, for example, like I know servers live on anthropic servers but for what we're asking the small local models to do I feel like a lot of that could be run just on a phone with rat in the package" | `willows-grove/docs/design/one-box/ui-apk-review-2026-10-08.md`:34 | 6.01% | unattested |
| JG2 | - **What the code needs.** Rat `--onescript` is standard library only and refuses cloud rungs; the one script is standard library plus `sqlite3`, with `cryptography` only for ed25519 seals. | `willows-grove/docs/design/one-box/ui-apk-review-2026-10-08.md`:35 | 3.65% | unattested |
| JG3 | - **The proposed shape.** One APK, embedded Python, the model as an in-process library so the app can drop `INTERNET` (a loopback server on a phone is open to every app on it), `allowBackup` off, sync over USB. | `willows-grove/docs/design/one-box/ui-apk-review-2026-10-08.md`:36 | 4.05% | unattested |
| JG4 | - **The decision.** "Phone only proposes, seal in Nestor on the box" A phone turn starts and ends on the box: served file in over USB, proposals out over USB. | `willows-grove/docs/design/one-box/ui-apk-review-2026-10-08.md`:37 | 3.05% | unattested |
| JG5 | - **Where it was written.** "Just in the grove for now" Recorded in `phone-seat-production.md`; no key, keyring or `cryptography` on the phone. | `willows-grove/docs/design/one-box/ui-apk-review-2026-10-08.md`:38 | 2.76% | unattested |
| JH1 | - **Local first.** "Back to the local, because that's where I need to be working first." and "All of that, and how it works with the UI." | `willows-grove/docs/design/one-box/ui-apk-review-2026-10-08.md`:42 | 2.65% | unattested |
| JH2 | - **The box walk.** Check-in hard-closed on ruff 0.16.10 against the 0.16.7 pin, then opened; scope gave subject `serve:167bfe94…`; serve without a seal answered empty; turn graded one `link_fail` and one `refused`; the walk stopped at the first seal. | `willows-grove/docs/design/one-box/ui-apk-review-2026-10-08.md`:43 | 4.85% | unattested |
| JH3 | - **PR 712 pulled in.** "Also need to pull in -mcp PR712, which is about to merge" `onescript_run_execute` runs the eight host steps with no shell; its own tests 126 passed; the full suite's 11 failures fail the same on `master` (running as root, the egress proxy). | `willows-grove/docs/design/one-box/ui-apk-review-2026-10-08.md`:44 | 5.12% | unattested |
| JH4 | - **The write-up.** "Write up the doc, and put those file types under git ignore" `local-flow-and-ui.md`: the ten-step flow through the verb, the local-model table, five read-only Grove panels; three tracked `.pyc` files untracked in willow-mcp. | `willows-grove/docs/design/one-box/ui-apk-review-2026-10-08.md`:45 | 4.73% | unattested |
| JH5 | - **The PRs.** "Pr please" willows-grove #126 and willow-mcp #714, each ending in `Ratified-by`. | `willows-grove/docs/design/one-box/ui-apk-review-2026-10-08.md`:46 | 1.85% | unattested |
| JI1 | - **Small models don't chat.** "Well I've been trying to figure out how the chat part of all of this will work. I mean I'm running 99% of it on local small models and they don't chat well. But I do have an idea for it but I want you to start thinking about that" | `willows-grove/docs/design/one-box/ui-apk-review-2026-10-08.md`:50 | 5.06% | unattested |
| JI2 | - **The hash line.** "Well I think you found it on the hash line. Like if those strings of boxes were reported to a small agent or small model then it could probably form a sentence out of them pretty quickly you know if it's served five boxes say" | `willows-grove/docs/design/one-box/ui-apk-review-2026-10-08.md`:51 | 4.79% | unattested |
| JI3 | - **Which five.** "I mean think about the plethora of of boxes that are now in this context session. What would you hand to a small model to create a sentence" Code picks them in the morning screen's order: needs you, changed, decided, blocked, routine passes as one box. | `willows-grove/docs/design/one-box/ui-apk-review-2026-10-08.md`:52 | 5.23% | unattested |
| JI4 | - **Keeping the sentence honest.** Every sentence cites its box ids, every served box is cited, no number or name the boxes don't hold; a failed check falls back to a sentence code fills in; hashes, paths and verbatim words never go to the model. | `willows-grove/docs/design/one-box/ui-apk-review-2026-10-08.md`:53 | 4.75% | unattested |
| JI5 | - **Why the sessions run in boxes.** "So why do you think I've been having sessions for the last few days run entirely inside of boxes?" The agent's reading (80%): the big models are making the substrate the small models will speak from. Then "yes add to the grid". | `willows-grove/docs/design/one-box/ui-apk-review-2026-10-08.md`:54 | 5.12% | unattested |
<!-- /cross-table:index -->

## Measure

<!-- cross-table:measure -->
- **Cells:** 25, of which 25 found (100.0%).
- **Text:** 5179 characters. An even share would be 4.00% per cell.
- **Trim:** 0 cell(s) cut at 420 characters; the index keeps 100.0% of the source text.

| Row | What it holds | Found | Characters | Share | Largest cell |
|---|---|---|---|---|---|
| JE | The review, checks first | 5/5 | 1073 | 20.72% | JE4 5.06% |
| JF | The APK as found | 5/5 | 809 | 15.62% | JF5 5.08% |
| JG | The phone only proposes | 5/5 | 1011 | 19.52% | JG1 6.01% |
| JH | The one script, local first | 5/5 | 994 | 19.19% | JH3 5.12% |
| JI | Chat from boxes | 5/5 | 1292 | 24.95% | JI3 5.23% |

- **Largest:** JG1 6.01%, JI3 5.23%, JH3 5.12%, JI5 5.12%, JF5 5.08%.
- **Smallest:** JH5 1.85%, JF3 1.89%, JF1 2.28%, JF2 2.41%, JH1 2.65%.

**Evenness.** Gini 0.17 (0 means every box holds the same, 1 means one box holds everything).
- **Fat** (at least 3× an even share; often several rules in one box, a candidate to split): none.
- **Thin** (at most 0.25× an even share; a label with a line behind it): none.

**Sources.** How much of each source file the grid draws on (distinct passages over the file's characters, whitespace collapsed, not counting any tables this script generated in it).

| File | Cells | Drawn | File | Coverage |
|---|---|---|---|---|
| `willows-grove/docs/design/one-box/ui-apk-review-2026-10-08.md` | 25 | 5179 | 6162 | 84.0% |

**Across grids.** Each grid's part of all the text.

| Grid | Cells | Characters | Share of all |
|---|---|---|---|
| The UI and APK review, the phone proposes, and chat from boxes (2026-10-08) | 25 | 5179 | 10.4% |
| The desk session's grids, in the one-box grid (2026-10-06) | 30 | 5124 | 10.3% |
| One hook, two hashes, Draft 0.9, and the instruction files, in the grid (2026-10-06) | 30 | 5238 | 10.5% |
| The Grove, the field and the gates, in the grid (2026-10-06) | 30 | 5437 | 10.9% |
| Hashing, Deep Thought reviewed, and the one script as a snapshot (2026-10-05 to 06) | 25 | 5972 | 11.9% |
| Python archaeology, in the grid (2026-10-06) | 30 | 4399 | 8.8% |
| A random pull, and where it lands (2026-10-06) | 12 | 1905 | 3.8% |
| Session four: 113, G5 fix, relay initiation (2026-10-06) | 20 | 4059 | 8.1% |
| 113, tables only, and the quorum ruling (2026-10-06) | 25 | 4713 | 9.4% |
| Three answers, and what comes out of nowhere (2026-10-06) | 20 | 3780 | 7.6% |
| The VSOCK fix on main, the fork, and the wall at upstream (2026-10-06) | 20 | 4180 | 8.4% |
<!-- /cross-table:measure -->
