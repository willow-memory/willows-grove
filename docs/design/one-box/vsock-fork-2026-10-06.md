# The VSOCK fix on `main`, the fork, and the wall at upstream (2026-10-06)

*A Claude Code cloud session (started from `willow-memory/willow-bot`) that
picked up the VSOCK ENODEV fix from the quick-stupids session (rows HO–HT,
[`python-archaeology-2026-10-06.md`](python-archaeology-2026-10-06.md)).
The operator uploaded the PR description `d052cd6d-cpython-vsock-PR.md`; the
session ran the `main` version on a Firecracker guest, wrote a handoff,
committed the patch to the operator's fork, and stopped at `python/cpython`.
The operator's words are quoted verbatim. Everything else is the agent's
reading. Every box is `unattested`.*

## The notes (the source)

### IQ · The `main` version, run on a Firecracker guest

- **The box.** The session's own container was a Firecracker microVM (kernel `6.18.44-fc-v70`) with `/dev/vsock` present and local CID 3: the environment the PR description's "Not verified" section said was missing.
- **The failure, reproduced.** A bare probe gave `connect((3, port))` → `ENODEV` (`[Errno 19] No such device`) and `connect((1, port))` (`VMADDR_CID_LOCAL`) → `ETIMEDOUT` after 2.02 s: no loopback transport. Same mode as the original report.
- **Before the patch.** CPython `main` at `cfd6cf7` (2026-10-05), built `--with-pydebug`. `ThreadedVSOCKSocketStreamTest.testStream` errored: server `TimeoutError: timed out`, client `OSError: [Errno 19] No such device`, `Result: FAILURE`, about 11 s.
- **After the patch.** The description's 7 added lines, applied exactly: skipped `'[Errno 19] No such device'`, 3 of 3 runs, `Result: SUCCESS`.
- **Full `test_socket`.** With the patch: SUCCESS, 753 run, 291 skipped, 37.9 s. The patch applied cleanly at `cfd6cf7`, though the description named `83b40d06f63`.

### IR · The handoff and the reviewer points

- **Handoff asked.** "Would you give me a handoff for that chunk". Written as `HANDOFF-vsock-main-verification.md` in the session scratchpad, with the tested diff `vsock-enodev-main.diff` beside it. Neither is tracked in a repo.
- **`self.cli` reuse.** `setUp` (server thread) binds the probe socket to `self.cli`; `clientSetUp` (client thread) rebinds the name later. Safe: `addCleanup` bound the probe's own `close`, and `clientRun` waits on `server_ready`, set only after `listen()` or in `_setUp`'s `finally`. A local name would read better but adds a line with no pre-AI origin.
- **Probe cost.** Where the CID is remapped to `VMADDR_CID_LOCAL` and no loopback transport exists, the probe's `connect()` times out at the kernel's default, measured 2.02 s, then setup continues as before.
- **Still not verified.** A host where VSOCK works end to end; `preai_gate.py` not re-run on the `cfd6cf7` diff (added lines identical); no NEWS entry, so `skip news` is needed.
- **Bears on Baton 1.** Its open item "VSOCK fix untested on a host where VSOCK works" stays 100% open: this run was another non-working host, now on `main` as well as 3.14.

### IS · The fork and the commit

- **The ask.** "I still need to sign all the py stuff on git hub, but if I forked it, would you be able to PR it?" then "cpython-fork".
- **The fork.** `rudi193-cmd/cpython-fork`, attached to the session with push; its `main` was at `cfd6cf7`, the commit already built and tested, so no rebase.
- **The author.** "you are in this box, connected to my github." The GitHub identity read back as `rudi193-cmd`, Sean Campbell, rudi193@gmail.com; the commit was authored with that name and email for the CLA check, without a Claude co-author line.
- **The commit.** `8ba6b5c` on branch `gh-vsock-enodev-skip-main` of the fork, title `gh-NNNNN: Skip VSOCK stream test when the transport reports ENODEV`. `Lib/test/test_socket.py` byte-identical to the tested file. Pushed.
- **The paste files.** `PR-body.md` (the operator's description with the `main` results moved into Verification) and `ISSUE-body.md` (CPython's bug-report layout), both in the session scratchpad.

### IT · The wall at `python/cpython`

- **The operator's correction.** "You can search issues, you can post, you can do all of these things?!? Why are you forgetting the most basic git today?" The agent had said it couldn't reach upstream before trying to attach it.
- **First denial.** Attaching `python/cpython` with push was denied by the auto-mode classifier, twice, the second time after the operator's "go".
- **Second denial.** "I switched to accept edits mode". The attach then reached GitHub and was refused: push access to `python/cpython` is needed, and the operator's account has none. Read access is anonymous only and covers no issue or PR tools.
- **The miss.** The agent first blamed the permission mode before knowing the GitHub check would also refuse; the mode switch cost the operator a round trip. The upstream wall held in every mode.
- **Left for the operator.** Open the issue from `ISSUE-body.md`, open the PR from `python/cpython/compare/main...rudi193-cmd:cpython-fork:gh-vsock-enodev-skip-main` with `PR-body.md`, then hand back the issue number so the fork's commit title can match.

## Grid

<!-- cross-table:grid -->
| | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| **IQ** The main version, run on a Firecracker guest | The box | The failure, reproduced | Before the patch | After the patch | Full `test_socket` |
| **IR** The handoff and the reviewer points | Handoff asked | `self.cli` reuse | Probe cost | Still not verified | Bears on Baton 1 |
| **IS** The fork and the commit | The ask | The fork | The author | The commit | The paste files |
| **IT** The wall at python/cpython | The operator's correction | First denial | Second denial | The miss | Left for the operator |
<!-- /cross-table:grid -->

## Sources

<!-- cross-table:sources -->
| Row | What it holds | Source |
|---|---|---|
| IQ | The main version, run on a Firecracker guest | the notes, section IQ (agent's reading) |
| IR | The handoff and the reviewer points | the notes, section IR (operator words verbatim where quoted; the rest the agent's reading) |
| IS | The fork and the commit | the notes, section IS (operator words verbatim where quoted; the rest the agent's reading) |
| IT | The wall at python/cpython | the notes, section IT (operator words verbatim where quoted; the rest the agent's reading) |
<!-- /cross-table:sources -->

## Index

<!-- cross-table:index -->
| Cell | Rule | Source | Share | Standing |
|---|---|---|---|---|
| IQ1 | - **The box.** The session's own container was a Firecracker microVM (kernel `6.18.44-fc-v70`) with `/dev/vsock` present and local CID 3: the environment the PR description's "Not verified" section said was missing. | `willows-grove/docs/design/one-box/vsock-fork-2026-10-06.md`:16 | 5.14% | unattested |
| IQ2 | - **The failure, reproduced.** A bare probe gave `connect((3, port))` → `ENODEV` (`[Errno 19] No such device`) and `connect((1, port))` (`VMADDR_CID_LOCAL`) → `ETIMEDOUT` after 2.02 s: no loopback transport. Same mode as the original report. | `willows-grove/docs/design/one-box/vsock-fork-2026-10-06.md`:17 | 5.77% | unattested |
| IQ3 | - **Before the patch.** CPython `main` at `cfd6cf7` (2026-10-05), built `--with-pydebug`. `ThreadedVSOCKSocketStreamTest.testStream` errored: server `TimeoutError: timed out`, client `OSError: [Errno 19] No such device`, `Result: FAILURE`, about 11 s. | `willows-grove/docs/design/one-box/vsock-fork-2026-10-06.md`:18 | 6.00% | unattested |
| IQ4 | - **After the patch.** The description's 7 added lines, applied exactly: skipped `'[Errno 19] No such device'`, 3 of 3 runs, `Result: SUCCESS`. | `willows-grove/docs/design/one-box/vsock-fork-2026-10-06.md`:19 | 3.42% | unattested |
| IQ5 | - **Full `test_socket`.** With the patch: SUCCESS, 753 run, 291 skipped, 37.9 s. The patch applied cleanly at `cfd6cf7`, though the description named `83b40d06f63`. | `willows-grove/docs/design/one-box/vsock-fork-2026-10-06.md`:20 | 3.92% | unattested |
| IR1 | - **Handoff asked.** "Would you give me a handoff for that chunk". Written as `HANDOFF-vsock-main-verification.md` in the session scratchpad, with the tested diff `vsock-enodev-main.diff` beside it. Neither is tracked in a repo. | `willows-grove/docs/design/one-box/vsock-fork-2026-10-06.md`:24 | 5.45% | unattested |
| IR2 | - **`self.cli` reuse.** `setUp` (server thread) binds the probe socket to `self.cli`; `clientSetUp` (client thread) rebinds the name later. Safe: `addCleanup` bound the probe's own `close`, and `clientRun` waits on `server_ready`, set only after `listen()` or in `_setUp`'s `finally`. A local name would read better but adds a line with no pre-AI origin. | `willows-grove/docs/design/one-box/vsock-fork-2026-10-06.md`:25 | 8.47% | unattested |
| IR3 | - **Probe cost.** Where the CID is remapped to `VMADDR_CID_LOCAL` and no loopback transport exists, the probe's `connect()` times out at the kernel's default, measured 2.02 s, then setup continues as before. | `willows-grove/docs/design/one-box/vsock-fork-2026-10-06.md`:26 | 4.95% | unattested |
| IR4 | - **Still not verified.** A host where VSOCK works end to end; `preai_gate.py` not re-run on the `cfd6cf7` diff (added lines identical); no NEWS entry, so `skip news` is needed. | `willows-grove/docs/design/one-box/vsock-fork-2026-10-06.md`:27 | 4.23% | unattested |
| IR5 | - **Bears on Baton 1.** Its open item "VSOCK fix untested on a host where VSOCK works" stays 100% open: this run was another non-working host, now on `main` as well as 3.14. | `willows-grove/docs/design/one-box/vsock-fork-2026-10-06.md`:28 | 4.14% | unattested |
| IS1 | - **The ask.** "I still need to sign all the py stuff on git hub, but if I forked it, would you be able to PR it?" then "cpython-fork". | `willows-grove/docs/design/one-box/vsock-fork-2026-10-06.md`:32 | 3.23% | unattested |
| IS2 | - **The fork.** `rudi193-cmd/cpython-fork`, attached to the session with push; its `main` was at `cfd6cf7`, the commit already built and tested, so no rebase. | `willows-grove/docs/design/one-box/vsock-fork-2026-10-06.md`:33 | 3.78% | unattested |
| IS3 | - **The author.** "you are in this box, connected to my github." The GitHub identity read back as `rudi193-cmd`, Sean Campbell, rudi193@gmail.com; the commit was authored with that name and email for the CLA check, without a Claude co-author line. | `willows-grove/docs/design/one-box/vsock-fork-2026-10-06.md`:34 | 5.91% | unattested |
| IS4 | - **The commit.** `8ba6b5c` on branch `gh-vsock-enodev-skip-main` of the fork, title `gh-NNNNN: Skip VSOCK stream test when the transport reports ENODEV`. `Lib/test/test_socket.py` byte-identical to the tested file. Pushed. | `willows-grove/docs/design/one-box/vsock-fork-2026-10-06.md`:35 | 5.33% | unattested |
| IS5 | - **The paste files.** `PR-body.md` (the operator's description with the `main` results moved into Verification) and `ISSUE-body.md` (CPython's bug-report layout), both in the session scratchpad. | `willows-grove/docs/design/one-box/vsock-fork-2026-10-06.md`:36 | 4.67% | unattested |
| IT1 | - **The operator's correction.** "You can search issues, you can post, you can do all of these things?!? Why are you forgetting the most basic git today?" The agent had said it couldn't reach upstream before trying to attach it. | `willows-grove/docs/design/one-box/vsock-fork-2026-10-06.md`:40 | 5.45% | unattested |
| IT2 | - **First denial.** Attaching `python/cpython` with push was denied by the auto-mode classifier, twice, the second time after the operator's "go". | `willows-grove/docs/design/one-box/vsock-fork-2026-10-06.md`:41 | 3.49% | unattested |
| IT3 | - **Second denial.** "I switched to accept edits mode". The attach then reached GitHub and was refused: push access to `python/cpython` is needed, and the operator's account has none. Read access is anonymous only and covers no issue or PR tools. | `willows-grove/docs/design/one-box/vsock-fork-2026-10-06.md`:42 | 5.89% | unattested |
| IT4 | - **The miss.** The agent first blamed the permission mode before knowing the GitHub check would also refuse; the mode switch cost the operator a round trip. The upstream wall held in every mode. | `willows-grove/docs/design/one-box/vsock-fork-2026-10-06.md`:43 | 4.67% | unattested |
| IT5 | - **Left for the operator.** Open the issue from `ISSUE-body.md`, open the PR from `python/cpython/compare/main...rudi193-cmd:cpython-fork:gh-vsock-enodev-skip-main` with `PR-body.md`, then hand back the issue number so the fork's commit title can match. | `willows-grove/docs/design/one-box/vsock-fork-2026-10-06.md`:44 | 6.08% | unattested |
<!-- /cross-table:index -->

## Measure

<!-- cross-table:measure -->
- **Cells:** 20, of which 20 found (100.0%).
- **Text:** 4180 characters. An even share would be 5.00% per cell.
- **Trim:** 0 cell(s) cut at 420 characters; the index keeps 100.0% of the source text.

| Row | What it holds | Found | Characters | Share | Largest cell |
|---|---|---|---|---|---|
| IQ | The main version, run on a Firecracker guest | 5/5 | 1014 | 24.26% | IQ3 6.00% |
| IR | The handoff and the reviewer points | 5/5 | 1139 | 27.25% | IR2 8.47% |
| IS | The fork and the commit | 5/5 | 958 | 22.92% | IS3 5.91% |
| IT | The wall at python/cpython | 5/5 | 1069 | 25.57% | IT5 6.08% |

- **Largest:** IR2 8.47%, IT5 6.08%, IQ3 6.00%, IS3 5.91%, IT3 5.89%.
- **Smallest:** IS1 3.23%, IQ4 3.42%, IT2 3.49%, IS2 3.78%, IQ5 3.92%.

**Evenness.** Gini 0.13 (0 means every box holds the same, 1 means one box holds everything).
- **Fat** (at least 3× an even share; often several rules in one box, a candidate to split): none.
- **Thin** (at most 0.25× an even share; a label with a line behind it): none.

**Sources.** How much of each source file the grid draws on (distinct passages over the file's characters, whitespace collapsed, not counting any tables this script generated in it).

| File | Cells | Drawn | File | Coverage |
|---|---|---|---|---|
| `willows-grove/docs/design/one-box/vsock-fork-2026-10-06.md` | 20 | 4180 | 5032 | 83.1% |
<!-- /cross-table:measure -->
