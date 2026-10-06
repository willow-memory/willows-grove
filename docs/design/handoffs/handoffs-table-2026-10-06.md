# Handoffs against Draft 0.9, as a table (2026-10-06)

*Desk session, 2026-10-06. The operator asked how the constitution's draft
compares "to the handoff", then "Anything that has handoff", then, when
offered the table: "Please". Agent-reported; not ratified.*

## How it's built

- **Every handoff in the three repos, and the Gerald session's three:** the
  hashing session's handoff (willows-grove); willow-mcp's two dated handoffs,
  its three repatriation handoffs, the handoff schema, the handoff-write
  skill, and its three handoff modules; the Gerald session's request and
  atoms, and this session's answers to it. The request and the answers are
  not in any repo, so their rows name the file and say so.
- **The source is a ledger,** [`handoff-ledger-2026-10-06.md`](handoff-ledger-2026-10-06.md),
  generated from the files. It gives each handoff's size, and for each of 14
  ideas from Draft 0.9 the number of case-insensitive text matches and the
  first line one is on. Every line names its handoff and its idea. A second
  run gave the same bytes.
- **A count says a word appears, not how it is used.** One known false
  positive is the delegation count in `handoff-py`: there "delegate" means one
  function calling another, not authority handed off. It is left in the
  ledger as data and named here.
- **Rows AS–BF,** one per handoff, after the branch grid's AR. Column 1 is the
  file. Columns 2–15 are the ideas, in the ledger's order. All 210 boxes were
  checked to be exactly their own line.

## What it shows

Read across the columns, not down the counts:

- **The old core travels.** Propose and ratify, the witness, and the human
  seal appear in most handoffs.
- **The constitution's additions don't.** No handoff mentions a quorum, and
  none mentions delegation of authority (the one hit is the false positive
  above).
- **One handoff cites the constitution's text.** The hashing handoff quotes
  ΔΣ=42's meaning from it. One other mentions it only as "HELD".
- **ΔΣ=42 appears in seven handoffs.** Several use it only as a closing
  seal. Where one says what it means, there are three meanings: "a checksum
  over change" (the constitution, quoted by the hashing handoff), "honest
  gaps" (the repatriation handoff), and "Dual Commit = Proposal +
  Ratification" (the Aionic material in the Gerald atoms). See the proposed "One name, one
  referent" in [`amendments-2026-10-06-grids.md`](../one-script/constitution-proposal/amendments-2026-10-06-grids.md).
- **The hard numbers live in one place.** Depth and size limits appear only
  in the Gerald material (the Aionic directives), in no repo handoff, and not
  in the constitution.

## The grid

<!-- cross-table:grid -->
| | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **AS** `grove-hashing-10-05` | the file | propose-ratify | witness | human-seal | append-only | escalate | capability | quorum | delegation | supremacy | limits | naming | delta-sigma | constitution | unknown |
| **AT** `mcp-07-23-wiring` | the file | propose-ratify | witness | human-seal | append-only | escalate | capability | quorum | delegation | supremacy | limits | naming | delta-sigma | constitution | unknown |
| **AU** `mcp-07-30-hooks` | the file | propose-ratify | witness | human-seal | append-only | escalate | capability | quorum | delegation | supremacy | limits | naming | delta-sigma | constitution | unknown |
| **AV** `session-handoff` | the file | propose-ratify | witness | human-seal | append-only | escalate | capability | quorum | delegation | supremacy | limits | naming | delta-sigma | constitution | unknown |
| **AW** `handoff-v3-assembling` | the file | propose-ratify | witness | human-seal | append-only | escalate | capability | quorum | delegation | supremacy | limits | naming | delta-sigma | constitution | unknown |
| **AX** `session-07-18-assembling` | the file | propose-ratify | witness | human-seal | append-only | escalate | capability | quorum | delegation | supremacy | limits | naming | delta-sigma | constitution | unknown |
| **AY** `handoff-schema` | the file | propose-ratify | witness | human-seal | append-only | escalate | capability | quorum | delegation | supremacy | limits | naming | delta-sigma | constitution | unknown |
| **AZ** `handoff-write-skill` | the file | propose-ratify | witness | human-seal | append-only | escalate | capability | quorum | delegation | supremacy | limits | naming | delta-sigma | constitution | unknown |
| **BA** `handoff-py` | the file | propose-ratify | witness | human-seal | append-only | escalate | capability | quorum | delegation | supremacy | limits | naming | delta-sigma | constitution | unknown |
| **BB** `handoff-validation-py` | the file | propose-ratify | witness | human-seal | append-only | escalate | capability | quorum | delegation | supremacy | limits | naming | delta-sigma | constitution | unknown |
| **BC** `session-pre-handoff-py` | the file | propose-ratify | witness | human-seal | append-only | escalate | capability | quorum | delegation | supremacy | limits | naming | delta-sigma | constitution | unknown |
| **BD** `gerald-request` | the file | propose-ratify | witness | human-seal | append-only | escalate | capability | quorum | delegation | supremacy | limits | naming | delta-sigma | constitution | unknown |
| **BE** `gerald-answers` | the file | propose-ratify | witness | human-seal | append-only | escalate | capability | quorum | delegation | supremacy | limits | naming | delta-sigma | constitution | unknown |
| **BF** `gerald-atoms` | the file | propose-ratify | witness | human-seal | append-only | escalate | capability | quorum | delegation | supremacy | limits | naming | delta-sigma | constitution | unknown |
<!-- /cross-table:grid -->

## Where each row comes from

<!-- cross-table:sources -->
| Row | What it holds | Source |
|---|---|---|
| AS | `grove-hashing-10-05` | `handoff-ledger-2026-10-06.md`, section grove-hashing-10-05 (generated from the file) |
| AT | `mcp-07-23-wiring` | `handoff-ledger-2026-10-06.md`, section mcp-07-23-wiring (generated from the file) |
| AU | `mcp-07-30-hooks` | `handoff-ledger-2026-10-06.md`, section mcp-07-30-hooks (generated from the file) |
| AV | `session-handoff` | `handoff-ledger-2026-10-06.md`, section session-handoff (generated from the file) |
| AW | `handoff-v3-assembling` | `handoff-ledger-2026-10-06.md`, section handoff-v3-assembling (generated from the file) |
| AX | `session-07-18-assembling` | `handoff-ledger-2026-10-06.md`, section session-07-18-assembling (generated from the file) |
| AY | `handoff-schema` | `handoff-ledger-2026-10-06.md`, section handoff-schema (generated from the file) |
| AZ | `handoff-write-skill` | `handoff-ledger-2026-10-06.md`, section handoff-write-skill (generated from the file) |
| BA | `handoff-py` | `handoff-ledger-2026-10-06.md`, section handoff-py (generated from the file) |
| BB | `handoff-validation-py` | `handoff-ledger-2026-10-06.md`, section handoff-validation-py (generated from the file) |
| BC | `session-pre-handoff-py` | `handoff-ledger-2026-10-06.md`, section session-pre-handoff-py (generated from the file) |
| BD | `gerald-request` | `handoff-ledger-2026-10-06.md`, section gerald-request (generated from the file) |
| BE | `gerald-answers` | `handoff-ledger-2026-10-06.md`, section gerald-answers (generated from the file) |
| BF | `gerald-atoms` | `handoff-ledger-2026-10-06.md`, section gerald-atoms (generated from the file) |
<!-- /cross-table:sources -->

## Index

<!-- cross-table:index -->
| Cell | Rule | Source | Share | Standing |
|---|---|---|---|---|
| AS1 | - handoff `grove-hashing-10-05` is `willows-grove/docs/design/one-script/hashing-session-handoff-2026-10-05.md`, 24881 bytes, 320 lines. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:26 | 0.98% | unattested |
| AS2 | - handoff `grove-hashing-10-05` idea `propose-ratify`: 11 matches, first on line 82. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:27 | 0.60% | unattested |
| AS3 | - handoff `grove-hashing-10-05` idea `witness`: 2 matches, first on line 147. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:28 | 0.55% | unattested |
| AS4 | - handoff `grove-hashing-10-05` idea `human-seal`: 13 matches, first on line 118. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:29 | 0.58% | unattested |
| AS5 | - handoff `grove-hashing-10-05` idea `append-only`: 2 matches, first on line 124. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:30 | 0.58% | unattested |
| AS6 | - handoff `grove-hashing-10-05` idea `escalate`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:31 | 0.42% | unattested |
| AS7 | - handoff `grove-hashing-10-05` idea `capability`: 1 match, first on line 319. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:32 | 0.56% | unattested |
| AS8 | - handoff `grove-hashing-10-05` idea `quorum`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:33 | 0.41% | unattested |
| AS9 | - handoff `grove-hashing-10-05` idea `delegation`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:34 | 0.44% | unattested |
| AS10 | - handoff `grove-hashing-10-05` idea `supremacy`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:35 | 0.43% | unattested |
| AS11 | - handoff `grove-hashing-10-05` idea `limits`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:36 | 0.41% | unattested |
| AS12 | - handoff `grove-hashing-10-05` idea `naming`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:37 | 0.41% | unattested |
| AS13 | - handoff `grove-hashing-10-05` idea `delta-sigma`: 5 matches, first on line 118. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:38 | 0.58% | unattested |
| AS14 | - handoff `grove-hashing-10-05` idea `constitution`: 2 matches, first on line 122. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:39 | 0.59% | unattested |
| AS15 | - handoff `grove-hashing-10-05` idea `unknown`: 2 matches, first on line 87. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:40 | 0.55% | unattested |
| AT1 | - handoff `mcp-07-23-wiring` is `willow-mcp/docs/handoffs/2026-07-23-mcp-wiring-and-corpus.md`, 6430 bytes, 52 lines. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:44 | 0.84% | unattested |
| AT2 | - handoff `mcp-07-23-wiring` idea `propose-ratify`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:45 | 0.45% | unattested |
| AT3 | - handoff `mcp-07-23-wiring` idea `witness`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:46 | 0.40% | unattested |
| AT4 | - handoff `mcp-07-23-wiring` idea `human-seal`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:47 | 0.42% | unattested |
| AT5 | - handoff `mcp-07-23-wiring` idea `append-only`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:48 | 0.42% | unattested |
| AT6 | - handoff `mcp-07-23-wiring` idea `escalate`: 1 match, first on line 17. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:49 | 0.52% | unattested |
| AT7 | - handoff `mcp-07-23-wiring` idea `capability`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:50 | 0.42% | unattested |
| AT8 | - handoff `mcp-07-23-wiring` idea `quorum`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:51 | 0.39% | unattested |
| AT9 | - handoff `mcp-07-23-wiring` idea `delegation`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:52 | 0.42% | unattested |
| AT10 | - handoff `mcp-07-23-wiring` idea `supremacy`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:53 | 0.41% | unattested |
| AT11 | - handoff `mcp-07-23-wiring` idea `limits`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:54 | 0.39% | unattested |
| AT12 | - handoff `mcp-07-23-wiring` idea `naming`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:55 | 0.39% | unattested |
| AT13 | - handoff `mcp-07-23-wiring` idea `delta-sigma`: 1 match, first on line 52. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:56 | 0.54% | unattested |
| AT14 | - handoff `mcp-07-23-wiring` idea `constitution`: 2 matches, first on line 47. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:57 | 0.56% | unattested |
| AT15 | - handoff `mcp-07-23-wiring` idea `unknown`: 1 match, first on line 45. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:58 | 0.51% | unattested |
| AU1 | - handoff `mcp-07-30-hooks` is `willow-mcp/docs/handoffs/2026-07-30-hooks-next-and-a-verification-lesson.md`, 13929 bytes, 249 lines. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:62 | 0.96% | unattested |
| AU2 | - handoff `mcp-07-30-hooks` idea `propose-ratify`: 1 match, first on line 63. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:63 | 0.55% | unattested |
| AU3 | - handoff `mcp-07-30-hooks` idea `witness`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:64 | 0.39% | unattested |
| AU4 | - handoff `mcp-07-30-hooks` idea `human-seal`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:65 | 0.41% | unattested |
| AU5 | - handoff `mcp-07-30-hooks` idea `append-only`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:66 | 0.42% | unattested |
| AU6 | - handoff `mcp-07-30-hooks` idea `escalate`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:67 | 0.40% | unattested |
| AU7 | - handoff `mcp-07-30-hooks` idea `capability`: 1 match, first on line 191. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:68 | 0.53% | unattested |
| AU8 | - handoff `mcp-07-30-hooks` idea `quorum`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:69 | 0.38% | unattested |
| AU9 | - handoff `mcp-07-30-hooks` idea `delegation`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:70 | 0.41% | unattested |
| AU10 | - handoff `mcp-07-30-hooks` idea `supremacy`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:71 | 0.40% | unattested |
| AU11 | - handoff `mcp-07-30-hooks` idea `limits`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:72 | 0.38% | unattested |
| AU12 | - handoff `mcp-07-30-hooks` idea `naming`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:73 | 0.38% | unattested |
| AU13 | - handoff `mcp-07-30-hooks` idea `delta-sigma`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:74 | 0.42% | unattested |
| AU14 | - handoff `mcp-07-30-hooks` idea `constitution`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:75 | 0.42% | unattested |
| AU15 | - handoff `mcp-07-30-hooks` idea `unknown`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:76 | 0.39% | unattested |
| AV1 | - handoff `session-handoff` is `willow-mcp/docs/repatriation/SESSION_HANDOFF.md`, 13678 bytes, 230 lines. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:80 | 0.75% | unattested |
| AV2 | - handoff `session-handoff` idea `propose-ratify`: 2 matches, first on line 44. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:81 | 0.57% | unattested |
| AV3 | - handoff `session-handoff` idea `witness`: 5 matches, first on line 43. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:82 | 0.52% | unattested |
| AV4 | - handoff `session-handoff` idea `human-seal`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:83 | 0.41% | unattested |
| AV5 | - handoff `session-handoff` idea `append-only`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:84 | 0.42% | unattested |
| AV6 | - handoff `session-handoff` idea `escalate`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:85 | 0.40% | unattested |
| AV7 | - handoff `session-handoff` idea `capability`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:86 | 0.41% | unattested |
| AV8 | - handoff `session-handoff` idea `quorum`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:87 | 0.38% | unattested |
| AV9 | - handoff `session-handoff` idea `delegation`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:88 | 0.41% | unattested |
| AV10 | - handoff `session-handoff` idea `supremacy`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:89 | 0.40% | unattested |
| AV11 | - handoff `session-handoff` idea `limits`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:90 | 0.38% | unattested |
| AV12 | - handoff `session-handoff` idea `naming`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:91 | 0.38% | unattested |
| AV13 | - handoff `session-handoff` idea `delta-sigma`: 3 matches, first on line 48. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:92 | 0.55% | unattested |
| AV14 | - handoff `session-handoff` idea `constitution`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:93 | 0.42% | unattested |
| AV15 | - handoff `session-handoff` idea `unknown`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:94 | 0.39% | unattested |
| AW1 | - handoff `handoff-v3-assembling` is `willow-mcp/docs/repatriation/handoff-v3-the-assembling.md`, 8991 bytes, 114 lines. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:98 | 0.86% | unattested |
| AW2 | - handoff `handoff-v3-assembling` idea `propose-ratify`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:99 | 0.48% | unattested |
| AW3 | - handoff `handoff-v3-assembling` idea `witness`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:100 | 0.43% | unattested |
| AW4 | - handoff `handoff-v3-assembling` idea `human-seal`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:101 | 0.45% | unattested |
| AW5 | - handoff `handoff-v3-assembling` idea `append-only`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:102 | 0.46% | unattested |
| AW6 | - handoff `handoff-v3-assembling` idea `escalate`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:103 | 0.44% | unattested |
| AW7 | - handoff `handoff-v3-assembling` idea `capability`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:104 | 0.45% | unattested |
| AW8 | - handoff `handoff-v3-assembling` idea `quorum`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:105 | 0.42% | unattested |
| AW9 | - handoff `handoff-v3-assembling` idea `delegation`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:106 | 0.45% | unattested |
| AW10 | - handoff `handoff-v3-assembling` idea `supremacy`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:107 | 0.45% | unattested |
| AW11 | - handoff `handoff-v3-assembling` idea `limits`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:108 | 0.42% | unattested |
| AW12 | - handoff `handoff-v3-assembling` idea `naming`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:109 | 0.42% | unattested |
| AW13 | - handoff `handoff-v3-assembling` idea `delta-sigma`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:110 | 0.46% | unattested |
| AW14 | - handoff `handoff-v3-assembling` idea `constitution`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:111 | 0.47% | unattested |
| AW15 | - handoff `handoff-v3-assembling` idea `unknown`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:112 | 0.43% | unattested |
| AX1 | - handoff `session-07-18-assembling` is `willow-mcp/docs/repatriation/session_handoff-2026-07-18_the-assembling.md`, 6134 bytes, 86 lines. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:116 | 0.99% | unattested |
| AX2 | - handoff `session-07-18-assembling` idea `propose-ratify`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:117 | 0.50% | unattested |
| AX3 | - handoff `session-07-18-assembling` idea `witness`: 1 match, first on line 52. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:118 | 0.57% | unattested |
| AX4 | - handoff `session-07-18-assembling` idea `human-seal`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:119 | 0.47% | unattested |
| AX5 | - handoff `session-07-18-assembling` idea `append-only`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:120 | 0.48% | unattested |
| AX6 | - handoff `session-07-18-assembling` idea `escalate`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:121 | 0.46% | unattested |
| AX7 | - handoff `session-07-18-assembling` idea `capability`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:122 | 0.47% | unattested |
| AX8 | - handoff `session-07-18-assembling` idea `quorum`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:123 | 0.45% | unattested |
| AX9 | - handoff `session-07-18-assembling` idea `delegation`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:124 | 0.47% | unattested |
| AX10 | - handoff `session-07-18-assembling` idea `supremacy`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:125 | 0.47% | unattested |
| AX11 | - handoff `session-07-18-assembling` idea `limits`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:126 | 0.45% | unattested |
| AX12 | - handoff `session-07-18-assembling` idea `naming`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:127 | 0.45% | unattested |
| AX13 | - handoff `session-07-18-assembling` idea `delta-sigma`: 2 matches, first on line 53. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:128 | 0.61% | unattested |
| AX14 | - handoff `session-07-18-assembling` idea `constitution`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:129 | 0.49% | unattested |
| AX15 | - handoff `session-07-18-assembling` idea `unknown`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:130 | 0.45% | unattested |
| AY1 | - handoff `handoff-schema` is `willow-mcp/docs/schema/handoff.schema.json`, 2267 bytes, 45 lines. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:134 | 0.70% | unattested |
| AY2 | - handoff `handoff-schema` idea `propose-ratify`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:135 | 0.43% | unattested |
| AY3 | - handoff `handoff-schema` idea `witness`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:136 | 0.38% | unattested |
| AY4 | - handoff `handoff-schema` idea `human-seal`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:137 | 0.40% | unattested |
| AY5 | - handoff `handoff-schema` idea `append-only`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:138 | 0.41% | unattested |
| AY6 | - handoff `handoff-schema` idea `escalate`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:139 | 0.39% | unattested |
| AY7 | - handoff `handoff-schema` idea `capability`: 1 match, first on line 21. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:140 | 0.52% | unattested |
| AY8 | - handoff `handoff-schema` idea `quorum`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:141 | 0.37% | unattested |
| AY9 | - handoff `handoff-schema` idea `delegation`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:142 | 0.40% | unattested |
| AY10 | - handoff `handoff-schema` idea `supremacy`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:143 | 0.40% | unattested |
| AY11 | - handoff `handoff-schema` idea `limits`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:144 | 0.37% | unattested |
| AY12 | - handoff `handoff-schema` idea `naming`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:145 | 0.37% | unattested |
| AY13 | - handoff `handoff-schema` idea `delta-sigma`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:146 | 0.41% | unattested |
| AY14 | - handoff `handoff-schema` idea `constitution`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:147 | 0.42% | unattested |
| AY15 | - handoff `handoff-schema` idea `unknown`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:148 | 0.38% | unattested |
| AZ1 | - handoff `handoff-write-skill` is `willow-mcp/skills/handoff-write.md`, 2779 bytes, 98 lines. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:152 | 0.68% | unattested |
| AZ2 | - handoff `handoff-write-skill` idea `propose-ratify`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:153 | 0.47% | unattested |
| AZ3 | - handoff `handoff-write-skill` idea `witness`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:154 | 0.42% | unattested |
| AZ4 | - handoff `handoff-write-skill` idea `human-seal`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:155 | 0.44% | unattested |
| AZ5 | - handoff `handoff-write-skill` idea `append-only`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:156 | 0.45% | unattested |
| AZ6 | - handoff `handoff-write-skill` idea `escalate`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:157 | 0.42% | unattested |
| AZ7 | - handoff `handoff-write-skill` idea `capability`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:158 | 0.44% | unattested |
| AZ8 | - handoff `handoff-write-skill` idea `quorum`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:159 | 0.41% | unattested |
| AZ9 | - handoff `handoff-write-skill` idea `delegation`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:160 | 0.44% | unattested |
| AZ10 | - handoff `handoff-write-skill` idea `supremacy`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:161 | 0.43% | unattested |
| AZ11 | - handoff `handoff-write-skill` idea `limits`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:162 | 0.41% | unattested |
| AZ12 | - handoff `handoff-write-skill` idea `naming`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:163 | 0.41% | unattested |
| AZ13 | - handoff `handoff-write-skill` idea `delta-sigma`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:164 | 0.45% | unattested |
| AZ14 | - handoff `handoff-write-skill` idea `constitution`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:165 | 0.45% | unattested |
| AZ15 | - handoff `handoff-write-skill` idea `unknown`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:166 | 0.42% | unattested |
| BA1 | - handoff `handoff-py` is `willow-mcp/src/willow_mcp/handoff.py`, 36685 bytes, 805 lines. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:170 | 0.64% | unattested |
| BA2 | - handoff `handoff-py` idea `propose-ratify`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:171 | 0.40% | unattested |
| BA3 | - handoff `handoff-py` idea `witness`: 1 match, first on line 43. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:172 | 0.47% | unattested |
| BA4 | - handoff `handoff-py` idea `human-seal`: 2 matches, first on line 263. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:173 | 0.51% | unattested |
| BA5 | - handoff `handoff-py` idea `append-only`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:174 | 0.38% | unattested |
| BA6 | - handoff `handoff-py` idea `escalate`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:175 | 0.36% | unattested |
| BA7 | - handoff `handoff-py` idea `capability`: 16 matches, first on line 224. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:176 | 0.52% | unattested |
| BA8 | - handoff `handoff-py` idea `quorum`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:177 | 0.34% | unattested |
| BA9 | - handoff `handoff-py` idea `delegation`: 1 match, first on line 553. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:178 | 0.50% | unattested |
| BA10 | - handoff `handoff-py` idea `supremacy`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:179 | 0.37% | unattested |
| BA11 | - handoff `handoff-py` idea `limits`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:180 | 0.34% | unattested |
| BA12 | - handoff `handoff-py` idea `naming`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:181 | 0.34% | unattested |
| BA13 | - handoff `handoff-py` idea `delta-sigma`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:182 | 0.38% | unattested |
| BA14 | - handoff `handoff-py` idea `constitution`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:183 | 0.39% | unattested |
| BA15 | - handoff `handoff-py` idea `unknown`: 7 matches, first on line 133. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:184 | 0.49% | unattested |
| BB1 | - handoff `handoff-validation-py` is `willow-mcp/src/willow_mcp/handoff_validation.py`, 8969 bytes, 176 lines. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:188 | 0.79% | unattested |
| BB2 | - handoff `handoff-validation-py` idea `propose-ratify`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:189 | 0.48% | unattested |
| BB3 | - handoff `handoff-validation-py` idea `witness`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:190 | 0.43% | unattested |
| BB4 | - handoff `handoff-validation-py` idea `human-seal`: 1 match, first on line 2. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:191 | 0.56% | unattested |
| BB5 | - handoff `handoff-validation-py` idea `append-only`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:192 | 0.46% | unattested |
| BB6 | - handoff `handoff-validation-py` idea `escalate`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:193 | 0.44% | unattested |
| BB7 | - handoff `handoff-validation-py` idea `capability`: 1 match, first on line 61. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:194 | 0.57% | unattested |
| BB8 | - handoff `handoff-validation-py` idea `quorum`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:195 | 0.42% | unattested |
| BB9 | - handoff `handoff-validation-py` idea `delegation`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:196 | 0.45% | unattested |
| BB10 | - handoff `handoff-validation-py` idea `supremacy`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:197 | 0.45% | unattested |
| BB11 | - handoff `handoff-validation-py` idea `limits`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:198 | 0.42% | unattested |
| BB12 | - handoff `handoff-validation-py` idea `naming`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:199 | 0.42% | unattested |
| BB13 | - handoff `handoff-validation-py` idea `delta-sigma`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:200 | 0.46% | unattested |
| BB14 | - handoff `handoff-validation-py` idea `constitution`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:201 | 0.47% | unattested |
| BB15 | - handoff `handoff-validation-py` idea `unknown`: 7 matches, first on line 6. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:202 | 0.55% | unattested |
| BC1 | - handoff `session-pre-handoff-py` is `willow-mcp/src/willow_mcp/session_pre_handoff.py`, 7692 bytes, 214 lines. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:206 | 0.80% | unattested |
| BC2 | - handoff `session-pre-handoff-py` idea `propose-ratify`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:207 | 0.49% | unattested |
| BC3 | - handoff `session-pre-handoff-py` idea `witness`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:208 | 0.44% | unattested |
| BC4 | - handoff `session-pre-handoff-py` idea `human-seal`: 4 matches, first on line 1. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:209 | 0.58% | unattested |
| BC5 | - handoff `session-pre-handoff-py` idea `append-only`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:210 | 0.47% | unattested |
| BC6 | - handoff `session-pre-handoff-py` idea `escalate`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:211 | 0.45% | unattested |
| BC7 | - handoff `session-pre-handoff-py` idea `capability`: 1 match, first on line 20. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:212 | 0.57% | unattested |
| BC8 | - handoff `session-pre-handoff-py` idea `quorum`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:213 | 0.43% | unattested |
| BC9 | - handoff `session-pre-handoff-py` idea `delegation`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:214 | 0.46% | unattested |
| BC10 | - handoff `session-pre-handoff-py` idea `supremacy`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:215 | 0.45% | unattested |
| BC11 | - handoff `session-pre-handoff-py` idea `limits`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:216 | 0.43% | unattested |
| BC12 | - handoff `session-pre-handoff-py` idea `naming`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:217 | 0.43% | unattested |
| BC13 | - handoff `session-pre-handoff-py` idea `delta-sigma`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:218 | 0.47% | unattested |
| BC14 | - handoff `session-pre-handoff-py` idea `constitution`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:219 | 0.47% | unattested |
| BC15 | - handoff `session-pre-handoff-py` idea `unknown`: 2 matches, first on line 41. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:220 | 0.57% | unattested |
| BD1 | - handoff `gerald-request` is `gerald-graph-handoff-request.md (uploaded to the session; not in a repo)`, 5067 bytes, 63 lines. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:224 | 0.91% | unattested |
| BD2 | - handoff `gerald-request` idea `propose-ratify`: 10 matches, first on line 9. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:225 | 0.56% | unattested |
| BD3 | - handoff `gerald-request` idea `witness`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:226 | 0.38% | unattested |
| BD4 | - handoff `gerald-request` idea `human-seal`: 1 match, first on line 7. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:227 | 0.51% | unattested |
| BD5 | - handoff `gerald-request` idea `append-only`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:228 | 0.41% | unattested |
| BD6 | - handoff `gerald-request` idea `escalate`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:229 | 0.39% | unattested |
| BD7 | - handoff `gerald-request` idea `capability`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:230 | 0.40% | unattested |
| BD8 | - handoff `gerald-request` idea `quorum`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:231 | 0.37% | unattested |
| BD9 | - handoff `gerald-request` idea `delegation`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:232 | 0.40% | unattested |
| BD10 | - handoff `gerald-request` idea `supremacy`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:233 | 0.40% | unattested |
| BD11 | - handoff `gerald-request` idea `limits`: 1 match, first on line 19. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:234 | 0.49% | unattested |
| BD12 | - handoff `gerald-request` idea `naming`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:235 | 0.37% | unattested |
| BD13 | - handoff `gerald-request` idea `delta-sigma`: 1 match, first on line 63. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:236 | 0.52% | unattested |
| BD14 | - handoff `gerald-request` idea `constitution`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:237 | 0.42% | unattested |
| BD15 | - handoff `gerald-request` idea `unknown`: 1 match, first on line 13. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:238 | 0.50% | unattested |
| BE1 | - handoff `gerald-answers` is `gerald-graph-handoff-answers.md (written in the session; not in a repo)`, 20370 bytes, 343 lines. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:242 | 0.92% | unattested |
| BE2 | - handoff `gerald-answers` idea `propose-ratify`: 14 matches, first on line 7. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:243 | 0.56% | unattested |
| BE3 | - handoff `gerald-answers` idea `witness`: 4 matches, first on line 59. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:244 | 0.51% | unattested |
| BE4 | - handoff `gerald-answers` idea `human-seal`: 2 matches, first on line 309. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:245 | 0.54% | unattested |
| BE5 | - handoff `gerald-answers` idea `append-only`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:246 | 0.41% | unattested |
| BE6 | - handoff `gerald-answers` idea `escalate`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:247 | 0.39% | unattested |
| BE7 | - handoff `gerald-answers` idea `capability`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:248 | 0.40% | unattested |
| BE8 | - handoff `gerald-answers` idea `quorum`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:249 | 0.37% | unattested |
| BE9 | - handoff `gerald-answers` idea `delegation`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:250 | 0.40% | unattested |
| BE10 | - handoff `gerald-answers` idea `supremacy`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:251 | 0.40% | unattested |
| BE11 | - handoff `gerald-answers` idea `limits`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:252 | 0.37% | unattested |
| BE12 | - handoff `gerald-answers` idea `naming`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:253 | 0.37% | unattested |
| BE13 | - handoff `gerald-answers` idea `delta-sigma`: 1 match, first on line 343. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:254 | 0.53% | unattested |
| BE14 | - handoff `gerald-answers` idea `constitution`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:255 | 0.42% | unattested |
| BE15 | - handoff `gerald-answers` idea `unknown`: 10 matches, first on line 14. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:256 | 0.52% | unattested |
| BF1 | - handoff `gerald-atoms` is `willows-grove/docs/design/gerald/gerald-session-atoms-2026-10-06.md`, 69712 bytes, 872 lines. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:260 | 0.88% | unattested |
| BF2 | - handoff `gerald-atoms` idea `propose-ratify`: 26 matches, first on line 7. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:261 | 0.55% | unattested |
| BF3 | - handoff `gerald-atoms` idea `witness`: 5 matches, first on line 45. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:262 | 0.50% | unattested |
| BF4 | - handoff `gerald-atoms` idea `human-seal`: 6 matches, first on line 75. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:263 | 0.52% | unattested |
| BF5 | - handoff `gerald-atoms` idea `append-only`: 2 matches, first on line 147. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:264 | 0.53% | unattested |
| BF6 | - handoff `gerald-atoms` idea `escalate`: 11 matches, first on line 273. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:265 | 0.52% | unattested |
| BF7 | - handoff `gerald-atoms` idea `capability`: 3 matches, first on line 377. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:266 | 0.52% | unattested |
| BF8 | - handoff `gerald-atoms` idea `quorum`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:267 | 0.36% | unattested |
| BF9 | - handoff `gerald-atoms` idea `delegation`: 0 matches. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:268 | 0.39% | unattested |
| BF10 | - handoff `gerald-atoms` idea `supremacy`: 2 matches, first on line 835. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:269 | 0.52% | unattested |
| BF11 | - handoff `gerald-atoms` idea `limits`: 7 matches, first on line 8. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:270 | 0.48% | unattested |
| BF12 | - handoff `gerald-atoms` idea `naming`: 2 matches, first on line 787. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:271 | 0.50% | unattested |
| BF13 | - handoff `gerald-atoms` idea `delta-sigma`: 3 matches, first on line 593. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:272 | 0.53% | unattested |
| BF14 | - handoff `gerald-atoms` idea `constitution`: 1 match, first on line 749. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:273 | 0.52% | unattested |
| BF15 | - handoff `gerald-atoms` idea `unknown`: 3 matches, first on line 291. | `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md`:274 | 0.50% | unattested |
<!-- /cross-table:index -->

## Measure

*Written by `cross_table.py fill --measure`, the same as the other grids.*

<!-- cross-table:measure -->
- **Cells:** 210, of which 210 found (100.0%).
- **Text:** 13919 characters. An even share would be 0.48% per cell.
- **Trim:** 0 cell(s) cut at 420 characters; the index keeps 100.0% of the source text.

| Row | What it holds | Found | Characters | Share | Largest cell |
|---|---|---|---|---|---|
| AS | `grove-hashing-10-05` | 15/15 | 1127 | 8.10% | AS1 0.98% |
| AT | `mcp-07-23-wiring` | 15/15 | 982 | 7.06% | AT1 0.84% |
| AU | `mcp-07-30-hooks` | 15/15 | 951 | 6.83% | AU1 0.96% |
| AV | `session-handoff` | 15/15 | 944 | 6.78% | AV1 0.75% |
| AW | `handoff-v3-assembling` | 15/15 | 989 | 7.11% | AW1 0.86% |
| AX | `session-07-18-assembling` | 15/15 | 1083 | 7.78% | AX1 0.99% |
| AY | `handoff-schema` | 15/15 | 884 | 6.35% | AY1 0.70% |
| AZ | `handoff-write-skill` | 15/15 | 935 | 6.72% | AZ1 0.68% |
| BA | `handoff-py` | 15/15 | 895 | 6.43% | BA1 0.64% |
| BB | `handoff-validation-py` | 15/15 | 1027 | 7.38% | BB1 0.79% |
| BC | `session-pre-handoff-py` | 15/15 | 1046 | 7.51% | BC1 0.80% |
| BD | `gerald-request` | 15/15 | 979 | 7.03% | BD1 0.91% |
| BE | `gerald-answers` | 15/15 | 990 | 7.11% | BE1 0.92% |
| BF | `gerald-atoms` | 15/15 | 1087 | 7.81% | BF1 0.88% |

- **Largest:** AX1 0.99%, AS1 0.98%, AU1 0.96%, BE1 0.92%, BD1 0.91%.
- **Smallest:** BA8 0.34%, BA12 0.34%, BA11 0.34%, BF8 0.36%, BA6 0.36%.

**Evenness.** Gini 0.11 (0 means every box holds the same, 1 means one box holds everything).
- **Fat** (at least 3× an even share; often several rules in one box, a candidate to split): none.
- **Thin** (at most 0.25× an even share; a label with a line behind it): none.

**Sources.** How much of each source file the grid draws on (distinct passages over the file's characters, whitespace collapsed, not counting any tables this script generated in it).

| File | Cells | Drawn | File | Coverage |
|---|---|---|---|---|
| `willows-grove/docs/design/handoffs/handoff-ledger-2026-10-06.md` | 210 | 13919 | 15998 | 87.0% |

**Across grids.** Each grid's part of all the text.

| Grid | Cells | Characters | Share of all |
|---|---|---|---|
| Handoffs against Draft 0.9 (2026-10-06) | 210 | 13919 | 12.8% |
| Rules cross table: boxes and branches (2026-10-06) | 169 | 27250 | 25.0% |
| Boxes, from outside the system (2026-10-06) | 20 | 3434 | 3.2% |
| The fat, dripped (2026-10-06) | 90 | 4063 | 3.7% |
| Gerald session atoms (2026-10-06) | 156 | 53779 | 49.4% |
| Open branches (2026-10-06) | 48 | 6475 | 5.9% |
<!-- /cross-table:measure -->

---

ΔΣ=42
