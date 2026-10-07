# Hashing, Deep Thought reviewed, and the one script as a snapshot (2026-10-05 to 06)

*A Claude Code cloud session (started from `willow-memory/willows-grove`)
that began as a lesson on hashing and turned toward the one script: what the
repos already do with hashes, a review of the `onescript/` skeleton, and the
operator's two ideas for stripping it down. The working record is a private
Claude Docs doc, "Hashing Session Handoff". The operator's words are quoted
verbatim. Everything else is the agent's reading. Every box is `unattested`.*

## The notes (the source)

### IU · Hashing, the explainer

- **The ask.** "Would you explain hash to me. How it works why it works Etc", then "Are things automatically hashed, or do you have to hatch them?" and "How have data Engineers used hash for security?"
- **What a hash is.** Any input becomes a fixed-size fingerprint: deterministic, fast, avalanche effect; one-way and collision resistant only for cryptographic hashes. SHA-256 of `hello` is `2cf24dba…9824`.
- **Why it can't be reversed.** Information is thrown away, the mixed operations (rotations, XOR, modular addition, 64 rounds) have no known shortcut, and 2^256 is too large to search. Believed, not proven; MD5 and SHA-1 fell.
- **Automatic or on purpose.** Nothing carries a hash until software computes one. Git, logins, HTTPS, Python dicts and OS updates hash on their own; `sha256sum`, `Get-FileHash` or `hashlib` hash on purpose.
- **Security uses in data engineering.** Keyed hashing (HMAC) for PII, pipeline checksums, hash-chained audit logs, password storage, k-anonymity breach checks. Failures given from memory: NYC taxi MD5 (2014), LinkedIn unsalted SHA-1 (2012).

### IV · Keys, the handoff doc, and the guess

- **The correction.** "So the key is to make sure something else rotates the hash before it ever gets posted anywhere you know that it's there's another layer of encryption". The key is rotated, not the hash, and HMAC is still hashing, not encryption; layers are defense in depth.
- **The handoff doc.** "Would you write me a hand off for the session please including any open questions." Written as a Claude Docs doc with a six-track research brief for web-research agents; every fact in it is from memory and marked for checking.
- **The first guess.** "Without looking at the container, I would like you to add a guess, in percentage, that how much I already knew about all of this." Guessed 30% (20–45%) from the conversation alone.
- **The repos read.** "Look at both repos that are in this container". Revised to 65% (55–80%): ΔΣ=42 is defined as a tamper-evidence seal, `willow-bot` deposits and `grove_db.py` `frank_ledger` are SHA-256 hash chains, and `bot.py` checks webhooks with HMAC and `hmac.compare_digest`.
- **Two `frank_ledger` gaps.** The tip query reads the latest row across every project, not this one, on a shared table; and two sends at once can read the same tip and fork the chain, since the anti-fork index guards only the genesis row. Not fixed.

### IW · Deep Thought, reviewed

- **The ask.** "Next thing I would like you to do is look at the one script/deepthought.py/ accompanying documentation for that". There is no `deepthought.py`; "Deep Thought: the attempt" in `next-pile.md` names the `onescript/` package.
- **What passes.** 53 tests pass and `ruff` is clean. `gate.py` uses HMAC-SHA256 with a `\x1f` separator and `hmac.compare_digest`, and fails closed; `record.py` hashes canonical JSON with atomic, fsynced writes.
- **Three attacks.** On a 5-row record, deleting the last 2 rows and rewriting row 1 with every later hash recomputed both pass `verify_chain()`; one garbled line crashes boot with `JSONDecodeError` instead of a hard close.
- **The fix offered.** Put the last row's hash into what the human seals at check-out and have `boot()` check the chain ends there; keep at least 128 bits instead of `h16`'s 64; report a garbled line as a break.
- **Docs drift.** `next-pile.md` says 29 tests and "local only, not in any repo"; the README says 53, and the package is in the repo. Signatures and seal proofs are also replayable, which matters once a socket exists.

### IX · The one script as a snapshot

- **The operator's idea.** "Basically it just needs to take a snapshot and anything that happens to the snapshot after that is what we need to think about." and "let's strip it down to its most basic form, and see what sticks"
- **Two steps.** Take a picture: hash every file with SHA-256 and keep the list, with one hash over the list as its fingerprint. Compare: a new picture later; same fingerprint means nothing changed, otherwise each file is added, removed or changed.
- **The test run.** A 50-line `snap.py`, stdlib only, in the session scratchpad: first run "picture taken: 3 files", second "nothing changed", then after three edits `added sub/new.txt`, `removed c.txt`, `changed a.txt`. Its full text is in the handoff doc, not in a repo.
- **What Git already does.** A commit is a picture and `git status` is the compare. What Git doesn't do is decide what a change means, which is the part worth building.
- **Add back in order.** Explain (an unexplained change is flagged), accept (the new picture becomes the baseline and stores the previous fingerprint), seal (the human signs the fingerprint, which also closes the truncation gap), and nothing else until a real change asks.

### IY · A pre-AI foundation

- **The narrow waist.** "It's more so about what the the user wants to do with it." and "a tiny little script that everything passes on and I'm not talking about tests I'm talking about like something very specific." Two readings offered, neither confirmed: every act passes through a before/after picture, or the script is small enough to read and seal.
- **The ask.** "What is last version of hash and pyton that came out before the pandemic." then "It's the code from before AI touched it."
- **The line.** Python 3.8.2 (late February 2020) with SHA-256 or SHA-3 from the standard library; BLAKE3 (January 2020) is not in it. Copilot's preview (June 2021) gives more than a year of margin. Dates from memory.
- **The proof and the cost.** Check `Python-3.8.2.tgz` against python.org's checksum and GPG signature, or CPython's tag `v3.8.2`. Costs: `snap.py` itself was written by AI, 3.8 lost security support in October 2024, and the stack under `hashlib` (OpenSSL, OS) has to be trusted as-is.
- **Bears on rows HS.** The archaeology session's pre-AI fix drew its line at `dcb1caef5bd8` (2021-06-28, the last commit before Copilot's preview) and required every added line to exist verbatim. This session's line is earlier and looser: the foundation is pre-AI, the small layer on top is sealed by the operator.

## Grid

<!-- cross-table:grid -->
| | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| **IU** Hashing, the explainer | The ask | What a hash is | Why it can't be reversed | Automatic or on purpose | Security uses in data engineering |
| **IV** Keys, the handoff doc, and the guess | The correction | The handoff doc | The first guess | The repos read | Two `frank_ledger` gaps |
| **IW** Deep Thought, reviewed | The ask | What passes | Three attacks | The fix offered | Docs drift |
| **IX** The one script as a snapshot | The operator's idea | Two steps | The test run | What Git already does | Add back in order |
| **IY** A pre-AI foundation | The narrow waist | The ask | The line | The proof and the cost | Bears on rows HS |
<!-- /cross-table:grid -->

## Sources

<!-- cross-table:sources -->
| Row | What it holds | Source |
|---|---|---|
| IU | Hashing, the explainer | the notes, section IU (operator words verbatim where quoted; the rest the agent's reading) |
| IV | Keys, the handoff doc, and the guess | the notes, section IV (operator words verbatim where quoted; the rest the agent's reading) |
| IW | Deep Thought, reviewed | the notes, section IW (operator words verbatim where quoted; the rest the agent's reading) |
| IX | The one script as a snapshot | the notes, section IX (operator words verbatim where quoted; the rest the agent's reading) |
| IY | A pre-AI foundation | the notes, section IY (operator words verbatim where quoted; the rest the agent's reading) |
<!-- /cross-table:sources -->

## Index

<!-- cross-table:index -->
| Cell | Rule | Source | Share | Standing |
|---|---|---|---|---|
| IU1 | - **The ask.** "Would you explain hash to me. How it works why it works Etc", then "Are things automatically hashed, or do you have to hatch them?" and "How have data Engineers used hash for security?" | `willows-grove/docs/design/one-box/hash-snapshot-2026-10-06.md`:14 | 3.37% | unattested |
| IU2 | - **What a hash is.** Any input becomes a fixed-size fingerprint: deterministic, fast, avalanche effect; one-way and collision resistant only for cryptographic hashes. SHA-256 of `hello` is `2cf24dba…9824`. | `willows-grove/docs/design/one-box/hash-snapshot-2026-10-06.md`:15 | 3.45% | unattested |
| IU3 | - **Why it can't be reversed.** Information is thrown away, the mixed operations (rotations, XOR, modular addition, 64 rounds) have no known shortcut, and 2^256 is too large to search. Believed, not proven; MD5 and SHA-1 fell. | `willows-grove/docs/design/one-box/hash-snapshot-2026-10-06.md`:16 | 3.78% | unattested |
| IU4 | - **Automatic or on purpose.** Nothing carries a hash until software computes one. Git, logins, HTTPS, Python dicts and OS updates hash on their own; `sha256sum`, `Get-FileHash` or `hashlib` hash on purpose. | `willows-grove/docs/design/one-box/hash-snapshot-2026-10-06.md`:17 | 3.47% | unattested |
| IU5 | - **Security uses in data engineering.** Keyed hashing (HMAC) for PII, pipeline checksums, hash-chained audit logs, password storage, k-anonymity breach checks. Failures given from memory: NYC taxi MD5 (2014), LinkedIn unsalted SHA-1 (2012). | `willows-grove/docs/design/one-box/hash-snapshot-2026-10-06.md`:18 | 4.04% | unattested |
| IV1 | - **The correction.** "So the key is to make sure something else rotates the hash before it ever gets posted anywhere you know that it's there's another layer of encryption". The key is rotated, not the hash, and HMAC is still hashing, not encryption; layers are defense in depth. | `willows-grove/docs/design/one-box/hash-snapshot-2026-10-06.md`:22 | 4.69% | unattested |
| IV2 | - **The handoff doc.** "Would you write me a hand off for the session please including any open questions." Written as a Claude Docs doc with a six-track research brief for web-research agents; every fact in it is from memory and marked for checking. | `willows-grove/docs/design/one-box/hash-snapshot-2026-10-06.md`:23 | 4.19% | unattested |
| IV3 | - **The first guess.** "Without looking at the container, I would like you to add a guess, in percentage, that how much I already knew about all of this." Guessed 30% (20–45%) from the conversation alone. | `willows-grove/docs/design/one-box/hash-snapshot-2026-10-06.md`:24 | 3.42% | unattested |
| IV4 | - **The repos read.** "Look at both repos that are in this container". Revised to 65% (55–80%): ΔΣ=42 is defined as a tamper-evidence seal, `willow-bot` deposits and `grove_db.py` `frank_ledger` are SHA-256 hash chains, and `bot.py` checks webhooks with HMAC and `hmac.compare_digest`. | `willows-grove/docs/design/one-box/hash-snapshot-2026-10-06.md`:25 | 4.77% | unattested |
| IV5 | - **Two `frank_ledger` gaps.** The tip query reads the latest row across every project, not this one, on a shared table; and two sends at once can read the same tip and fork the chain, since the anti-fork index guards only the genesis row. Not fixed. | `willows-grove/docs/design/one-box/hash-snapshot-2026-10-06.md`:26 | 4.19% | unattested |
| IW1 | - **The ask.** "Would you explain hash to me. How it works why it works Etc", then "Are things automatically hashed, or do you have to hatch them?" and "How have data Engineers used hash for security?" | `willows-grove/docs/design/one-box/hash-snapshot-2026-10-06.md`:14 | 3.37% | unattested |
| IW2 | - **What passes.** 53 tests pass and `ruff` is clean. `gate.py` uses HMAC-SHA256 with a `\x1f` separator and `hmac.compare_digest`, and fails closed; `record.py` hashes canonical JSON with atomic, fsynced writes. | `willows-grove/docs/design/one-box/hash-snapshot-2026-10-06.md`:31 | 3.55% | unattested |
| IW3 | - **Three attacks.** On a 5-row record, deleting the last 2 rows and rewriting row 1 with every later hash recomputed both pass `verify_chain()`; one garbled line crashes boot with `JSONDecodeError` instead of a hard close. | `willows-grove/docs/design/one-box/hash-snapshot-2026-10-06.md`:32 | 3.73% | unattested |
| IW4 | - **The fix offered.** Put the last row's hash into what the human seals at check-out and have `boot()` check the chain ends there; keep at least 128 bits instead of `h16`'s 64; report a garbled line as a break. | `willows-grove/docs/design/one-box/hash-snapshot-2026-10-06.md`:33 | 3.53% | unattested |
| IW5 | - **Docs drift.** `next-pile.md` says 29 tests and "local only, not in any repo"; the README says 53, and the package is in the repo. Signatures and seal proofs are also replayable, which matters once a socket exists. | `willows-grove/docs/design/one-box/hash-snapshot-2026-10-06.md`:34 | 3.63% | unattested |
| IX1 | - **The operator's idea.** "Basically it just needs to take a snapshot and anything that happens to the snapshot after that is what we need to think about." and "let's strip it down to its most basic form, and see what sticks" | `willows-grove/docs/design/one-box/hash-snapshot-2026-10-06.md`:38 | 3.78% | unattested |
| IX2 | - **Two steps.** Take a picture: hash every file with SHA-256 and keep the list, with one hash over the list as its fingerprint. Compare: a new picture later; same fingerprint means nothing changed, otherwise each file is added, removed or changed. | `willows-grove/docs/design/one-box/hash-snapshot-2026-10-06.md`:39 | 4.15% | unattested |
| IX3 | - **The test run.** A 50-line `snap.py`, stdlib only, in the session scratchpad: first run "picture taken: 3 files", second "nothing changed", then after three edits `added sub/new.txt`, `removed c.txt`, `changed a.txt`. Its full text is in the handoff doc, not in a repo. | `willows-grove/docs/design/one-box/hash-snapshot-2026-10-06.md`:40 | 4.55% | unattested |
| IX4 | - **What Git already does.** A commit is a picture and `git status` is the compare. What Git doesn't do is decide what a change means, which is the part worth building. | `willows-grove/docs/design/one-box/hash-snapshot-2026-10-06.md`:41 | 2.81% | unattested |
| IX5 | - **Add back in order.** Explain (an unexplained change is flagged), accept (the new picture becomes the baseline and stores the previous fingerprint), seal (the human signs the fingerprint, which also closes the truncation gap), and nothing else until a real change asks. | `willows-grove/docs/design/one-box/hash-snapshot-2026-10-06.md`:42 | 4.55% | unattested |
| IY1 | - **The narrow waist.** "It's more so about what the the user wants to do with it." and "a tiny little script that everything passes on and I'm not talking about tests I'm talking about like something very specific." Two readings offered, neither confirmed: every act passes through a before/after picture, or the script is small enough to read and seal. | `willows-grove/docs/design/one-box/hash-snapshot-2026-10-06.md`:46 | 5.93% | unattested |
| IY2 | - **The ask.** "Would you explain hash to me. How it works why it works Etc", then "Are things automatically hashed, or do you have to hatch them?" and "How have data Engineers used hash for security?" | `willows-grove/docs/design/one-box/hash-snapshot-2026-10-06.md`:14 | 3.37% | unattested |
| IY3 | - **The line.** Python 3.8.2 (late February 2020) with SHA-256 or SHA-3 from the standard library; BLAKE3 (January 2020) is not in it. Copilot's preview (June 2021) gives more than a year of margin. Dates from memory. | `willows-grove/docs/design/one-box/hash-snapshot-2026-10-06.md`:48 | 3.63% | unattested |
| IY4 | - **The proof and the cost.** Check `Python-3.8.2.tgz` against python.org's checksum and GPG signature, or CPython's tag `v3.8.2`. Costs: `snap.py` itself was written by AI, 3.8 lost security support in October 2024, and the stack under `hashlib` (OpenSSL, OS) has to be trusted as-is. | `willows-grove/docs/design/one-box/hash-snapshot-2026-10-06.md`:49 | 4.77% | unattested |
| IY5 | - **Bears on rows HS.** The archaeology session's pre-AI fix drew its line at `dcb1caef5bd8` (2021-06-28, the last commit before Copilot's preview) and required every added line to exist verbatim. This session's line is earlier and looser: the foundation is pre-AI, the small layer on top is sealed by the operator. | `willows-grove/docs/design/one-box/hash-snapshot-2026-10-06.md`:50 | 5.27% | unattested |
<!-- /cross-table:index -->

## Measure

<!-- cross-table:measure -->
- **Cells:** 25, of which 25 found (100.0%).
- **Text:** 5972 characters. An even share would be 4.00% per cell.
- **Trim:** 0 cell(s) cut at 420 characters; the index keeps 100.0% of the source text.

| Row | What it holds | Found | Characters | Share | Largest cell |
|---|---|---|---|---|---|
| IU | Hashing, the explainer | 5/5 | 1081 | 18.10% | IU5 4.04% |
| IV | Keys, the handoff doc, and the guess | 5/5 | 1269 | 21.25% | IV4 4.77% |
| IW | Deep Thought, reviewed | 5/5 | 1064 | 17.82% | IW3 3.73% |
| IX | The one script as a snapshot | 5/5 | 1186 | 19.86% | IX3 4.55% |
| IY | A pre-AI foundation | 5/5 | 1372 | 22.97% | IY1 5.93% |

- **Largest:** IY1 5.93%, IY5 5.27%, IV4 4.77%, IY4 4.77%, IV1 4.69%.
- **Smallest:** IX4 2.81%, IY2 3.37%, IW1 3.37%, IU1 3.37%, IV3 3.42%.

**Evenness.** Gini 0.09 (0 means every box holds the same, 1 means one box holds everything).
- **Fat** (at least 3× an even share; often several rules in one box, a candidate to split): none.
- **Thin** (at most 0.25× an even share; a label with a line behind it): none.

**Sources.** How much of each source file the grid draws on (distinct passages over the file's characters, whitespace collapsed, not counting any tables this script generated in it).

| File | Cells | Drawn | File | Coverage |
|---|---|---|---|---|
| `willows-grove/docs/design/one-box/hash-snapshot-2026-10-06.md` | 25 | 5570 | 6716 | 82.9% |

**Across grids.** Each grid's part of all the text.

| Grid | Cells | Characters | Share of all |
|---|---|---|---|
| Hashing, Deep Thought reviewed, and the one script as a snapshot (2026-10-05 to 06) | 25 | 5972 | 58.8% |
| The VSOCK fix on main, the fork, and the wall at upstream (2026-10-06) | 20 | 4180 | 41.2% |
<!-- /cross-table:measure -->
