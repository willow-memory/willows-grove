# Python archaeology, in the grid (2026-10-06)

*A Claude Code session in `rudi193-cmd/quick-stupids`, 2026-10-03 → 06. The
operator asked for the earliest Python to be cloned and built, then each later
milestone, then hmac and hashlib, then everything pushed to the store. On
seeing this branch: "yes, add it to the one-box grid". The operator's words are
quoted verbatim. The build and test figures were measured in that session's
container. Everything else is the agent's reading. Every box is `unattested`.
The full record is `safe-app-store/research/python-archaeology/` (PR #224,
merged). This grid points at it and doesn't copy it.*

## The notes (the source)

### HO · The ask

- **Operator, the start.** "clone in the earliest version of python that is available", then "try to build it".
- **Operator, the steps.** "shallow clone 2.0 and build it", "shallow clone 3.0 and build it", "shallow clone 3.14 and build it", then "will you actually do the same for 3.9 as well".
- **Operator, the test.** "I would like you to prepare a PR for 3.14, only using the pre AI code."
- **Operator, the modules.** "Would you do the same, first build for hmac and hash", then "please clone in the first stable version of each as well, and run it like we did python".
- **Operator, where it goes.** "push the patches and table to safe app store, along with all the tables.", then "yes, add it to the one-box grid".

### HP · 1993 to 1994

- **0.9.8, rebuilt.** Tag `v0.9.8` (1993-01-10) has no Makefile, no `PROTO.h`, no `dictobject.c`. About 20 files were reconstructed or backported, including Guido's own dict from 1993-03-27. The 1993 suite passes and its output matches the shipped `testall.out` line for line.
- **The 64-bit bug in 0.9.8.** `int_mul` compared against `(long)0x80000000`, negative on 32-bit and positive on LP64, so `2*1` raised OverflowError.
- **0.9.9, compared only.** Old class syntax removed, an `access` statement, `hash()`, fast locals. Not built.
- **1.0.0, cut mid-move.** No tag. Commit `2a7cbe9` (1994-01-26) points `INCLDIR` at a directory that doesn't exist, ships a truncated `version.c`, and calls itself "0.9.0++".
- **The bug that waited until 1.5.** On 64-bit, `.pyc` files truncated big ints: `5000000000` came back as `705032704`. Upstream fixed it in 1.5. The suite couldn't see it.

### HQ · 2000 to 2008

- **2.0.** Two lines, `-fwrapv`, and one stray committed `config.h`. 82 of 82 test modules pass. A one-byte overflow in `int_repr` (fixed upstream in 2.2) was caught by modern glibc.
- **2.2, the first hmac.** Both git tags for 2.2 are mislabelled. Real 2.2 final is commit `22768184cb`. It builds with no changes: 155 OK, 1 failed (`test_mktime` assumes a 32-bit `time_t`).
- **2.5, the first hashlib.** Three small changes, including two Subversion keywords git never expanded, reconstructed as `r25:51908` from 2006 release banners. 273 OK, 3 failed (gdbm magic, zlib), none in hmac or hashlib.
- **3.0.** No changes to the core. Three small module fixes. 294 of 297.
- **The same answer for 24 years.** RFC 2202 HMAC-MD5 `9294727a…` and HMAC-SHA1 `b6173186…` come out identical on 2.2, 2.5, 3.0, 3.9.0, 3.14.0 and 3.15.0rc3.

### HR · 2020 to 2026

- **3.9.0, the last before Copilot.** Stock build, no changes. 393 of 399 test modules. Copilot's preview was announced 2021-06-29.
- **3.14.0.** Stock build. 460 of 462. Both failures are the container: an HTTPS proxy and no VSOCK device.
- **3.15.0rc3.** Stock build, the newest at the time. 471 of 473, the same two container failures. `_decimal` is no longer bundled.
- **The trend.** From rebuilding missing files by hand in 1993 to `./configure && make` with nothing to change from 2020 on.
- **What every failure turned out to be.** A 32-bit-era assumption, a newer system library, or the container. One, 3.9's `test_cmd_line`, wasn't confirmed.

### HS · The pre-AI fix

- **The constraint.** Every added line must already exist verbatim in CPython at `dcb1caef5bd8` (2021-06-28, the last commit before Copilot's preview). The agent places lines; it writes none.
- **The fix.** Eight lines in the VSOCK test's `setUp`: probe one connection to the local CID and skip on `ENODEV`. Four of the eight are the 2021 test's own client lines, moved.
- **The gate.** `preai_gate.py` passes on the diff and fails when one new line is added.
- **The dropped guard.** A second guard was tried and removed: taking it out changed nothing, so no test could fail on it.
- **Still needed.** 3.15.0rc3 and 3.14.8 both carry the upstream change gh-145548 and still fail the same way. Not opened upstream; untested on a host where VSOCK works.

### HT · Where it went

- **The store.** `safe-app-store/research/python-archaeology/`: README with every table, five build patches, six BUILD notes, and the pre-AI fix with its gate. PR #224, merged 2026-10-05.
- **The playground.** One row in the quick-stupids README map, commit `edd0a09` on branch `ccr-62ce0a8b-e5m30g`.
- **Container only.** The built interpreters and the local CPython branch `gh-vsock-enodev-skip`. Gone when the container is.
- **Reconstructed, not measured.** 2.0's `$Revision: 1.6$` (from a commit count) and 2.5's `r25:51908` (from 2006 banners). Both are labelled in the store.

## Grid

<!-- cross-table:grid -->
| | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| **HO** The ask | Operator, the start | Operator, the steps | Operator, the test | Operator, the modules | Operator, where it goes |
| **HP** 1993 to 1994 | 0.9.8, rebuilt | The 64-bit bug in 0.9.8 | 0.9.9, compared only | 1.0.0, cut mid-move | The bug that waited until 1.5 |
| **HQ** 2000 to 2008 | 2.0 | 2.2, the first hmac | 2.5, the first hashlib | 3.0 | The same answer for 24 years |
| **HR** 2020 to 2026 | 3.9.0, the last before Copilot | 3.14.0 | 3.15.0rc3 | The trend | What every failure turned out to be |
| **HS** The pre-AI fix | The constraint | The fix | The gate | The dropped guard | Still needed |
| **HT** Where it went | The store | The playground | Container only | Reconstructed, not measured |  |
<!-- /cross-table:grid -->

## Sources

<!-- cross-table:sources -->
| Row | What it holds | Source |
|---|---|---|
| HO | The ask | the notes, section HO (operator's words verbatim; build and test figures measured in the session; the rest the agent's reading) |
| HP | 1993 to 1994 | the notes, section HP (operator's words verbatim; build and test figures measured in the session; the rest the agent's reading) |
| HQ | 2000 to 2008 | the notes, section HQ (operator's words verbatim; build and test figures measured in the session; the rest the agent's reading) |
| HR | 2020 to 2026 | the notes, section HR (operator's words verbatim; build and test figures measured in the session; the rest the agent's reading) |
| HS | The pre-AI fix | the notes, section HS (operator's words verbatim; build and test figures measured in the session; the rest the agent's reading) |
| HT | Where it went | the notes, section HT (operator's words verbatim; build and test figures measured in the session; the rest the agent's reading) |
<!-- /cross-table:sources -->

## Index

<!-- cross-table:index -->
| Cell | Rule | Source | Share | Standing |
|---|---|---|---|---|
| HO1 | - **Operator, the start.** "clone in the earliest version of python that is available", then "try to build it". | `willows-grove/docs/design/one-box/python-archaeology-2026-10-06.md`:16 | 2.52% | unattested |
| HO2 | - **Operator, the steps.** "shallow clone 2.0 and build it", "shallow clone 3.0 and build it", "shallow clone 3.14 and build it", then "will you actually do the same for 3.9 as well". | `willows-grove/docs/design/one-box/python-archaeology-2026-10-06.md`:17 | 4.16% | unattested |
| HO3 | - **Operator, the test.** "I would like you to prepare a PR for 3.14, only using the pre AI code." | `willows-grove/docs/design/one-box/python-archaeology-2026-10-06.md`:18 | 2.23% | unattested |
| HO4 | - **Operator, the modules.** "Would you do the same, first build for hmac and hash", then "please clone in the first stable version of each as well, and run it like we did python". | `willows-grove/docs/design/one-box/python-archaeology-2026-10-06.md`:19 | 4.09% | unattested |
| HO5 | - **Operator, where it goes.** "push the patches and table to safe app store, along with all the tables.", then "yes, add it to the one-box grid". | `willows-grove/docs/design/one-box/python-archaeology-2026-10-06.md`:20 | 3.32% | unattested |
| HP1 | - **0.9.8, rebuilt.** Tag `v0.9.8` (1993-01-10) has no Makefile, no `PROTO.h`, no `dictobject.c`. About 20 files were reconstructed or backported, including Guido's own dict from 1993-03-27. The 1993 suite passes and its output matches the shipped `testall.out` line for line. | `willows-grove/docs/design/one-box/python-archaeology-2026-10-06.md`:24 | 6.27% | unattested |
| HP2 | - **The 64-bit bug in 0.9.8.** `int_mul` compared against `(long)0x80000000`, negative on 32-bit and positive on LP64, so `2*1` raised OverflowError. | `willows-grove/docs/design/one-box/python-archaeology-2026-10-06.md`:25 | 3.39% | unattested |
| HP3 | - **0.9.9, compared only.** Old class syntax removed, an `access` statement, `hash()`, fast locals. Not built. | `willows-grove/docs/design/one-box/python-archaeology-2026-10-06.md`:26 | 2.50% | unattested |
| HP4 | - **1.0.0, cut mid-move.** No tag. Commit `2a7cbe9` (1994-01-26) points `INCLDIR` at a directory that doesn't exist, ships a truncated `version.c`, and calls itself "0.9.0++". | `willows-grove/docs/design/one-box/python-archaeology-2026-10-06.md`:27 | 3.98% | unattested |
| HP5 | - **The bug that waited until 1.5.** On 64-bit, `.pyc` files truncated big ints: `5000000000` came back as `705032704`. Upstream fixed it in 1.5. The suite couldn't see it. | `willows-grove/docs/design/one-box/python-archaeology-2026-10-06.md`:28 | 3.91% | unattested |
| HQ1 | - **2.0.** Two lines, `-fwrapv`, and one stray committed `config.h`. 82 of 82 test modules pass. A one-byte overflow in `int_repr` (fixed upstream in 2.2) was caught by modern glibc. | `willows-grove/docs/design/one-box/python-archaeology-2026-10-06.md`:32 | 4.14% | unattested |
| HQ2 | - **2.2, the first hmac.** Both git tags for 2.2 are mislabelled. Real 2.2 final is commit `22768184cb`. It builds with no changes: 155 OK, 1 failed (`test_mktime` assumes a 32-bit `time_t`). | `willows-grove/docs/design/one-box/python-archaeology-2026-10-06.md`:33 | 4.34% | unattested |
| HQ3 | - **2.5, the first hashlib.** Three small changes, including two Subversion keywords git never expanded, reconstructed as `r25:51908` from 2006 release banners. 273 OK, 3 failed (gdbm magic, zlib), none in hmac or hashlib. | `willows-grove/docs/design/one-box/python-archaeology-2026-10-06.md`:34 | 5.05% | unattested |
| HQ4 | - **3.0.** No changes to the core. Three small module fixes. 294 of 297. | `willows-grove/docs/design/one-box/python-archaeology-2026-10-06.md`:35 | 1.64% | unattested |
| HQ5 | - **The same answer for 24 years.** RFC 2202 HMAC-MD5 `9294727a…` and HMAC-SHA1 `b6173186…` come out identical on 2.2, 2.5, 3.0, 3.9.0, 3.14.0 and 3.15.0rc3. | `willows-grove/docs/design/one-box/python-archaeology-2026-10-06.md`:36 | 3.57% | unattested |
| HR1 | - **3.9.0, the last before Copilot.** Stock build, no changes. 393 of 399 test modules. Copilot's preview was announced 2021-06-29. | `willows-grove/docs/design/one-box/python-archaeology-2026-10-06.md`:40 | 2.98% | unattested |
| HR2 | - **3.14.0.** Stock build. 460 of 462. Both failures are the container: an HTTPS proxy and no VSOCK device. | `willows-grove/docs/design/one-box/python-archaeology-2026-10-06.md`:41 | 2.43% | unattested |
| HR3 | - **3.15.0rc3.** Stock build, the newest at the time. 471 of 473, the same two container failures. `_decimal` is no longer bundled. | `willows-grove/docs/design/one-box/python-archaeology-2026-10-06.md`:42 | 2.98% | unattested |
| HR4 | - **The trend.** From rebuilding missing files by hand in 1993 to `./configure && make` with nothing to change from 2020 on. | `willows-grove/docs/design/one-box/python-archaeology-2026-10-06.md`:43 | 2.82% | unattested |
| HR5 | - **What every failure turned out to be.** A 32-bit-era assumption, a newer system library, or the container. One, 3.9's `test_cmd_line`, wasn't confirmed. | `willows-grove/docs/design/one-box/python-archaeology-2026-10-06.md`:44 | 3.52% | unattested |
| HS1 | - **The constraint.** Every added line must already exist verbatim in CPython at `dcb1caef5bd8` (2021-06-28, the last commit before Copilot's preview). The agent places lines; it writes none. | `willows-grove/docs/design/one-box/python-archaeology-2026-10-06.md`:48 | 4.34% | unattested |
| HS2 | - **The fix.** Eight lines in the VSOCK test's `setUp`: probe one connection to the local CID and skip on `ENODEV`. Four of the eight are the 2021 test's own client lines, moved. | `willows-grove/docs/design/one-box/python-archaeology-2026-10-06.md`:49 | 4.05% | unattested |
| HS3 | - **The gate.** `preai_gate.py` passes on the diff and fails when one new line is added. | `willows-grove/docs/design/one-box/python-archaeology-2026-10-06.md`:50 | 2.00% | unattested |
| HS4 | - **The dropped guard.** A second guard was tried and removed: taking it out changed nothing, so no test could fail on it. | `willows-grove/docs/design/one-box/python-archaeology-2026-10-06.md`:51 | 2.77% | unattested |
| HS5 | - **Still needed.** 3.15.0rc3 and 3.14.8 both carry the upstream change gh-145548 and still fail the same way. Not opened upstream; untested on a host where VSOCK works. | `willows-grove/docs/design/one-box/python-archaeology-2026-10-06.md`:52 | 3.84% | unattested |
| HT1 | - **The store.** `safe-app-store/research/python-archaeology/`: README with every table, five build patches, six BUILD notes, and the pre-AI fix with its gate. PR #224, merged 2026-10-05. | `willows-grove/docs/design/one-box/python-archaeology-2026-10-06.md`:56 | 4.25% | unattested |
| HT2 | - **The playground.** One row in the quick-stupids README map, commit `edd0a09` on branch `ccr-62ce0a8b-e5m30g`. | `willows-grove/docs/design/one-box/python-archaeology-2026-10-06.md`:57 | 2.55% | unattested |
| HT3 | - **Container only.** The built interpreters and the local CPython branch `gh-vsock-enodev-skip`. Gone when the container is. | `willows-grove/docs/design/one-box/python-archaeology-2026-10-06.md`:58 | 2.84% | unattested |
| HT4 | - **Reconstructed, not measured.** 2.0's `$Revision: 1.6$` (from a commit count) and 2.5's `r25:51908` (from 2006 banners). Both are labelled in the store. | `willows-grove/docs/design/one-box/python-archaeology-2026-10-06.md`:59 | 3.52% | unattested |
| HT5 | *source silent* | — | 0.00% | unattested |
<!-- /cross-table:index -->

## Measure

<!-- cross-table:measure -->
- **Cells:** 30, of which 29 found (96.7%).
- **Text:** 4399 characters. An even share would be 3.33% per cell.
- **Trim:** 0 cell(s) cut at 420 characters; the index keeps 100.0% of the source text.

| Row | What it holds | Found | Characters | Share | Largest cell |
|---|---|---|---|---|---|
| HO | The ask | 5/5 | 718 | 16.32% | HO2 4.16% |
| HP | 1993 to 1994 | 5/5 | 882 | 20.05% | HP1 6.27% |
| HQ | 2000 to 2008 | 5/5 | 824 | 18.73% | HQ3 5.05% |
| HR | 2020 to 2026 | 5/5 | 648 | 14.73% | HR5 3.52% |
| HS | The pre-AI fix | 5/5 | 748 | 17.00% | HS1 4.34% |
| HT | Where it went | 4/5 | 579 | 13.16% | HT1 4.25% |

- **Largest:** HP1 6.27%, HQ3 5.05%, HQ2 4.34%, HS1 4.34%, HT1 4.25%.
- **Smallest:** HQ4 1.64%, HS3 2.00%, HO3 2.23%, HR2 2.43%, HP3 2.50%.
- **Holding nothing:** HT5.

**Evenness.** Gini 0.18 (0 means every box holds the same, 1 means one box holds everything).
- **Fat** (at least 3× an even share; often several rules in one box, a candidate to split): none.
- **Thin** (at most 0.25× an even share; a label with a line behind it): none.

**Sources.** How much of each source file the grid draws on (distinct passages over the file's characters, whitespace collapsed, not counting any tables this script generated in it).

| File | Cells | Drawn | File | Coverage |
|---|---|---|---|---|
| `willows-grove/docs/design/one-box/python-archaeology-2026-10-06.md` | 29 | 4399 | 5222 | 84.2% |
<!-- /cross-table:measure -->
