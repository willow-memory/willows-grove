# Hashing Session Handoff

*Moved here 2026-10-05 from `~/Desktop/Nest/Hashing Session Handoff.md` at the
operator's word ("lets put move and put it at the top of the one script md").
Written by a claude.ai session that saw only the tracked repo, with no Willow
tools. The text is verbatim; only the tables, flattened in the export, are
re-flowed as markdown. Everything in it is agent-reported and unattested. The
desk's check of the review against the code is at the end.*

Oct 5, 2026 · @Sean

A one-session explainer on hash functions, from basics to security use in data engineering, written up so research agents can pick up where it left off. Every fact here was given from memory, with no web lookups, so treat specific dates and incidents as claims to verify.

## What we covered

The session moved from "what is a hash" to how data engineers use one for security, then to related ideas. The conversation itself was the only output: no code was written and no repos were changed.

1. **What a hash is.** A function that turns input of any size into a fixed-size fingerprint. SHA-256 example: "hello" gives `2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824`. Properties: deterministic, fast, avalanche effect, one-way, collision resistant. The last two apply only to cryptographic hashes.
2. **How SHA-256 works inside.** Pad, split into 512-bit blocks, then 64 rounds of rotations, XOR/AND/NOT and modular addition on 8 state words. Why it can't be reversed: information is thrown away, the mixed operations have no known shortcut, and 2^256 is far too large to brute-force. Its security is believed, not proven; MD5 and SHA-1 have been broken.
3. **Automatic or manual?** Nothing carries a hash until software computes one. Git, logins, HTTPS, Python dicts, OS updates and cloud sync hash for you behind the scenes. You hash on purpose with `sha256sum`, `Get-FileHash` or `hashlib`.
4. **Security use in data engineering.** Pseudonymizing PII with keyed hashes (HMAC), pipeline integrity checks, tamper-evident audit logs, password and token storage, cross-organization matching, and k-anonymity breach checks. Failures covered: NYC taxi data (2014), LinkedIn (2012), and hashed-email ad matching.
5. **Keys, rotation and layers.** Corrected the idea that the protection is a second layer of encryption (see Corrections). Covered defense in depth.
6. **Extras.** Birthday paradox, Merkle trees, similarity hashes (perceptual, LSH, SimHash), consistent hashing, commitment schemes, proof of work, quantum impact, and history (Luhn 1953, MD5, SHA-1, SHAttered 2017, SHA-3 2015).

## Quick reference

Pick the hash by the job: the wrong family is the most common mistake.

| Job | Use | Avoid | Why |
|---|---|---|---|
| Password storage | Argon2id, bcrypt, scrypt (salted) | SHA-256, MD5, any fast hash | Slow on purpose, so guessing is expensive |
| Pseudonymizing PII (emails, phones, IDs) | HMAC-SHA-256 with a vaulted key | Plain SHA-256 / MD5 | Low-entropy inputs can be enumerated without a key |
| File and pipeline integrity | SHA-256, BLAKE3 | MD5, SHA-1 against attackers | MD5/SHA-1 collisions are practical |
| Tamper-evident logs | Hash chain or Merkle tree on SHA-256 | Unchained per-row hashes | Chaining makes any edit break every later link |
| Hash tables, sharding | xxHash, MurmurHash, SipHash | Cryptographic hashes (too slow) | Speed matters; SipHash resists hash-flooding |
| Near-duplicate detection | Perceptual hash, LSH, SimHash | Cryptographic hashes | You want similar inputs to land close together |
| Getting the original back | Encryption or a token vault | Any hash | Hashes cannot be reversed |

## Corrections to carry forward

One idea drifted during the session; this is the fixed version to start from.

| Drifted idea | Corrected idea |
|---|---|
| "Something rotates the hash before it is posted." | The key is rotated, not the hash. Rotation swaps the secret every so often so a stolen old key stops being useful. Old hashes then need re-hashing or a mapping. |
| "There's another layer of encryption." | A keyed hash (HMAC) is still hashing, not encryption: it cannot be reversed. What protects it is a secret mixed in so outsiders can't recompute it. Encryption is a separate layer around the whole system. |
| (implied) "Hashed data is anonymous." | Hashed personal data is pseudonymized, not anonymized. Under GDPR it is still personal data. |

The working sentence: mix a secret into the hash so nobody else can recreate it, keep that secret in a vault and change it periodically, and wrap the system in other layers (encryption, access control).

## Open questions

None of these block anything; they are where a next session or a research pass could go.

- [ ] What is the end goal? Is this general learning, or for a project such as Willow's Grove (audit logs, provenance checks, u2u signing)? The answer decides which research tasks matter most.
- [ ] Which follow-up did you want? Offered and not yet picked: birthday-problem math, why salts matter, how Git builds its hash tree, a toy hash in Python, Merkle trees or consistent hashing by hand.
- [ ] Verify the memory-based facts listed under Sources and caveats.
- [ ] Key rotation for HMAC pseudonyms in practice: how do teams re-key without breaking joins across history (dual-keying, versioned key IDs, re-hash jobs)?
- [ ] Current regulator stance: is there updated EDPB or ICO guidance on whether keyed hashing ever counts as anonymization?
- [ ] Post-quantum status: what NIST has finalized (SPHINCS+ is published as SLH-DSA, FIPS 205) and whether any guidance moves hash output sizes.
- [ ] Session environment: the Willow's Grove MCP server timed out and the Grove server needs authorization, so neither was used this session.

## Research brief for agents

Give each agent one track, ask it to open and cite primary pages (not search snippets), and to flag anything that contradicts this doc.

| Track | Question to answer | Search terms | Best sources |
|---|---|---|---|
| 1. Fact check | Are the dates and incidents under Sources and caveats correct? | "NYC taxi medallion MD5 deanonymization", "LinkedIn 2012 SHA-1 breach", "SHAttered SHA-1 collision" | Original researcher posts, shattered.io, court or company disclosures |
| 2. Current standards | What do NIST and OWASP recommend today for hashing and password storage? | "NIST FIPS 180-4", "FIPS 202 SHA-3", "OWASP Password Storage Cheat Sheet", "NIST SP 800-63B" | csrc.nist.gov, cheatsheetseries.owasp.org |
| 3. Pseudonymization in practice | How do real pipelines do keyed hashing, key storage and key rotation? | "HMAC pseudonymization data pipeline", "tokenization vs hashing PII", "key rotation pseudonymous identifiers" | Cloud vendor docs (AWS KMS, GCP Cloud DLP), engineering blogs from large data teams |
| 4. Legal status | Is hashed PII personal data under GDPR, CCPA and the FTC's view? | "EDPB pseudonymisation guidelines", "ENISA pseudonymisation techniques", "FTC hashing does not make data anonymous" | edpb.europa.eu, enisa.europa.eu, ftc.gov |
| 5. Tamper-evident logs | How do Certificate Transparency, Trillian and Sigstore/Rekor use Merkle trees? | "RFC 9162 certificate transparency", "Trillian verifiable log", "Sigstore Rekor transparency log" | IETF RFCs, project docs on GitHub |
| 6. Post-quantum | What is the status of hash-based signatures and of hash security against quantum attacks? | "FIPS 205 SLH-DSA", "Grover algorithm hash security", "NIST post-quantum standards 2024" | csrc.nist.gov |

**Judging sources.** Prefer standards bodies, RFCs, original papers and the affected company's own disclosure. Treat vendor marketing, SEO explainers and AI-written summaries as leads, not evidence. Note the publication date: hashing advice from before 2017 may still recommend SHA-1 or plain salted SHA-256 for passwords.

**What to bring back.** For each track: a two- or three-sentence answer, the links actually opened, an as-of date, and any corrections to this doc.

## Design notes

These are speculative ideas from a reading of the Willow's Grove project notes, not a review of its code. Each would be new work and needs your ratification first.

- **Hash-chained journal: already exists.** Written before I read the repos: willow-bot deposits and willows-grove frank_ledger already chain rows with SHA-256. See the revised guess section for two gaps in frank_ledger.
- **Provenance alongside the trailers.** The `Persona:` and `Ratified-by:` checks already lean on Git's hash chain. A signed tag or signed commit would bind the ratification to an exact tree hash.
- **u2u messages.** Ed25519 already hashes internally (SHA-512). If confidentiality arrives in Gate 6, hashing doesn't replace encryption; it covers integrity, not secrecy.
- **Three-state readers.** A content hash per panel payload could tell "populated and unchanged" apart from "populated and new" without diffing, which fits the populated / empty / unreachable contract without merging its states.
- **The vault.** Any HMAC key belongs in a secrets store, never in the repo or `.mcp.json`, and rotation needs a key ID stored next to each hash.

## For fun

Small things to try, each a few minutes long.

- [ ] **See the avalanche.** Run `printf hello | sha256sum` and `printf hellp | sha256sum`. One letter changes and about half the output bits flip.
- [ ] **Be a miner.** Write a loop that finds a number n where `sha256("willow" + n)` starts with `0000`. Each extra zero takes about 16 times longer, which is proof of work in miniature.
- [ ] **Break a weak pseudonym.** Hash every number from 0000 to 9999 and reverse a hashed 4-digit PIN instantly. It's the NYC taxi lesson at small scale.
- [ ] **Birthday surprise.** Truncate SHA-256 to 8 hex characters (32 bits) and hash random strings until two collide. Expect about 77,000 tries (roughly 2^16), not 4 billion.
- [ ] **Read Git's guts.** Run `git cat-file -p HEAD`, then follow the tree and parent hashes by hand. That's a Merkle structure you already use.
- [ ] **Puzzle.** Why does `hash(-1) == hash(-2)` in CPython? (Hint: -1 is reserved as an error code in the C API.)

## Guess: how much you already knew

My guess is about 30% overall (plausible range 20–45%), based only on how you asked and answered in this conversation. I didn't inspect the container; the one outside input is the project CLAUDE.md that loads automatically at session start.

| Topic | Guess | Signal |
|---|---|---|
| What a hash is, the fingerprint idea | 45% | Asked to start from scratch, but followed easily and moved on fast |
| SHA-256 internals (rounds, rotations, modular addition) | 10% | No follow-up questions on mechanics; reads as new |
| Automatic vs. manual hashing | 40% | "Do you have to hatch them?" points to a practical gap, yet you work daily with Git, which hashes for you |
| Security use in data engineering | 25% | The question was open-ended, a sign of exploring rather than checking |
| Keys, rotation, layered defense | 40% | You had the defense-in-depth instinct right; the terms (rotate the key, HMAC vs. encryption) were fuzzy |
| Extras (Merkle trees, consistent hashing, birthday paradox) | 15% | You asked "anything else", which suggests these were new |

**Why not lower:** you run a project with Ed25519-signed messages, OAuth/PKCE, and commit-provenance checks, so you have likely used hashes hands-on, even without the vocabulary. **Why not higher:** the questions followed a learner's path (what → how → where used → what else) and the one restatement drifted on terms. Asking for this guess "without looking" also hints you may know more than you showed, which is why the range runs up to 45%.

### Revised guess after reading both repos

Revised to about 65% (range 55–80%). The 30% guess above was too low: both repos already build on the ideas this session explained, and ΔΣ=42 is itself a tamper-evidence seal.

| Found | Where | What it shows |
|---|---|---|
| ΔΣ=42 defined as "the fleet's tamper-evidence seal … a checksum over change, enforced at the boundary" | `willows-grove/governance/CONSTITUTION.md` (Open Operator Decisions #3) | Tamper evidence is a founding principle, stamped on file headers across the repos |
| SHA-256 hash chain: `prev_hash`, `row_hash`, genesis constant, canonical JSON, `\x00` separator, `verify_chain` | `willow-bot/willow_bot/deposits.py` | A careful, correct hash-chain design |
| "Annul rows": corrections appended, never edited in place | `willow-bot/willow_bot/deposits.py` | Understanding of why append-only logs matter |
| frank_ledger hash chain in Postgres with an anti-fork genesis index | `willows-grove/grove_db.py` | The same pattern on a second storage layer |
| GitHub webhook HMAC-SHA256 checked with `hmac.compare_digest` | `willow-bot/bot.py` | Keyed hashing plus a constant-time compare, a detail many teams miss |
| Ed25519 signing, with a malformed packet kept distinct from a bad signature | `willows-grove/u2u/` | Signatures, and honest reporting of failures |
| ΔΣ=42 packet stamp-chain proposal (nonce, prior_hash, key_id, Bloom filter for replay) | `willows-grove/docs/design/one-script/incoming/haiku-2026-10-02/` | Chain-of-custody design across nodes |

**Why not higher:** many of these commits carry agent `Persona:` trailers or a Claude author, so you may direct and ratify this work rather than write the hash code yourself. That fits what the conversation showed: the concepts are strong (tamper evidence, chains, append-only records, custody), while some vocabulary was looser (rotate the key vs. the hash, HMAC vs. encryption). My estimate: about 85% on concepts and 35% on the mechanics and terms.

Two things spotted in frank_ledger (not fixed; fixing them would be new work):

- [ ] The tip query `SELECT hash FROM frank_ledger ORDER BY created_at DESC LIMIT 1` doesn't filter by project. The table is a shared fleet surface, so a grove row can chain onto another writer's row, while the genesis index expects one chain per project.
- [ ] Two sends at the same moment can read the same tip and write two rows with the same `prev_hash`, forking the chain. The anti-fork index only guards the genesis row; a per-project lock (`pg_advisory_xact_lock`) or a unique index on `(project, prev_hash)` would close it.
- [ ] Open per the constitution itself: ΔΣ=42's "enforcing artifact remains to be located or built." The two chains above, plus the stamp-chain proposal, are the natural candidates.

## Review: the one script ("Deep Thought")

The skeleton in `willows-grove/docs/design/one-script/onescript/` is careful work, but its record chain only catches clumsy edits. There is no `deepthought.py`; "Deep Thought: the attempt" is what next-pile.md calls this package. All 53 tests pass and ruff is clean. Nothing was changed; fixes would be new work needing ratification.

### Done well

- `gate.py`: HMAC-SHA256 with a `\x1f` separator between fields, `hmac.compare_digest`, and every internal error fails closed.
- `record.py`: hashes over canonical JSON, atomic and fsynced writes, and `version_of` hashes the script's own source so each row records which code wrote it.
- The human seat can only be entered with a seal proof from the human's key, and the morning probes check the gate still holds.
- The "what the script can't solve" section is honest and clear: the script can witness a claim, but only the human's seal makes it true.

### Tried against a 5-row record

| Attack | Result |
|---|---|
| Delete the last 2 rows | `verify_chain()` reports nothing wrong |
| Change row 1 to "FORGED" and recompute every later hash | Reports nothing wrong |
| Append one garbled line | Boot crashes with `JSONDecodeError` instead of a hard close |

### Findings and suggested fixes

- [ ] **The chain can be cut or rewritten.** The hash has no key and the last hash isn't stored anywhere else, so anyone who can write `record.jsonl` can truncate it or rehash it. Fix: put the last row's hash into what the human seals at check-out, and have `boot()` check the chain ends at the last sealed hash. A forger can't redo the seal without the human's key.
- [ ] **`h16` truncates SHA-256 to 64 bits.** By the birthday paradox, a matching pair takes about 2^32 tries, which is cheap. This affects row hashes and `pile.json` file pointers. Fix: keep at least 128 bits (32 hex characters).
- [ ] **A garbled line crashes boot.** Fix: report it as a chain break so the hard-close rule (report, options, wait) still applies.
- [ ] **Signatures can be replayed.** `sign(key, who, family)` is the same every time, and a seal proof for a subject is reusable. Fine in one process; it matters once the planned socket exists. Fix: a fresh challenge per check, or the planned move to Ed25519.
- [ ] **Docs drift.** next-pile.md says "29 tests" and "local only, not in any repo"; the README says 53 tests, and the package is in the repo.

## Stripped down: the one script as a snapshot

The one script can start as two steps: take a picture, then compare. Everything else waits until a real change asks for it. This is a proposal: the script below was tested only in a scratch folder and is not in any repo.

1. **Take a picture.** Hash every file with SHA-256 and save the list of paths and hashes. One hash over the whole list is the picture's fingerprint.
2. **Compare.** Take a new picture later. Same fingerprint means nothing changed; otherwise list each file as added, removed, or changed.

Test run:

```
$ python3 snap.py demo
picture taken: 3 files, 286b497a56fd
$ python3 snap.py demo
nothing changed
$ # edit a.txt, delete c.txt, add sub/new.txt
$ python3 snap.py demo
added    sub/new.txt
removed  c.txt
changed  a.txt
```

The script (`snap.py`, 50 lines, stdlib only):

```python
"""snap: take a picture of a folder, then say what changed since."""

import hashlib
import json
import sys
from pathlib import Path

SKIP = {".snap", ".git"}


def picture(root: Path) -> dict[str, str]:
    """Every file's path and its SHA-256."""
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*"))
        if p.is_file() and not SKIP & set(p.relative_to(root).parts)
    }


def fingerprint(pic: dict[str, str]) -> str:
    """One hash for the whole picture."""
    return hashlib.sha256(json.dumps(pic, sort_keys=True).encode()).hexdigest()


def compare(old: dict[str, str], new: dict[str, str]) -> dict[str, list[str]]:
    return {
        "added": sorted(new.keys() - old.keys()),
        "removed": sorted(old.keys() - new.keys()),
        "changed": sorted(k for k in old.keys() & new.keys() if old[k] != new[k]),
    }


def main(root: str = ".") -> None:
    root_path = Path(root)
    store = root_path / ".snap" / "picture.json"
    now = picture(root_path)
    if not store.exists():
        store.parent.mkdir(exist_ok=True)
        store.write_text(json.dumps(now, indent=1, sort_keys=True))
        print(f"picture taken: {len(now)} files, {fingerprint(now)[:12]}")
        return
    then = json.loads(store.read_text())
    if fingerprint(then) == fingerprint(now):
        print("nothing changed")
        return
    for kind, paths in compare(then, now).items():
        for p in paths:
            print(f"{kind:8} {p}")


if __name__ == "__main__":
    main(*sys.argv[1:])
```

Git already does steps 1 and 2 (a commit is a picture, `git status` is the compare). What Git doesn't do is decide what a change means, which is the part worth building.

What to add back, one at a time, only when a real change asks for it:

1. **Explain:** every change carries a one-line reason, and an unexplained change is flagged. The old "a change without a recorded cause is a hard close," as one rule.
2. **Accept:** approving the changes makes the new picture the baseline. Each picture stores the previous fingerprint, so the history becomes a chain.
3. **Seal:** the human signs the fingerprint. This also fixes the review's truncation and rehash gap.
4. Everything else in the current skeleton (gates, citations, resolve, predict, reverse, the morning screen) stays off until it earns its place.

Questions that decide the shape:

- [ ] What gets photographed? One repo folder, the whole box, or the record and the database?
- [ ] When is the picture taken? At check-in, at check-out, or on a schedule?
- [ ] Which changes are expected? Logs and caches that should be skipped like `.git`.
- [ ] Where does it live? For example `docs/design/one-script/snap.py`, next to `onescript/`. Needs ratification before it goes in a repo.

## Idea: a pre-AI foundation

Build the one script on code written before AI could have touched it, and check that by fingerprint rather than trust. Proposed by the operator; this section is the session's working-through, from memory, so dates are approximate.

Related idea, still open: the script as a narrow waist, one tiny correct layer everything passes through, like IP on the internet. Two readings were offered and neither is confirmed yet: every action passes through a before/after picture, or the script itself is small enough to read, check and seal.

**The line: before March 2020.** Python 3.8.2 shipped in late February 2020. Python 3.8 with SHA-256 or SHA-3 from the standard library is a fully pre-pandemic setup. BLAKE3 (January 2020) is pre-pandemic too but not in the standard library.

| Date | Event |
|---|---|
| Nov 2022 | ChatGPT |
| Jun 2021 | GitHub Copilot preview: AI-written code at scale begins |
| Jun 2020 | GPT-3 announced |
| Mar 2020 | Pandemic declared (the cutoff) |
| Feb 2020 | Python 3.8.2 released |

AI autocomplete existed before 2020 (TabNine added a GPT-2 model in 2019) but was niche, so the cutoff leaves more than a year of margin.

**How to prove it's the 2020 code:** check `Python-3.8.2.tgz` against the checksum and release manager's GPG signature on python.org, or use CPython's Git tag `v3.8.2`, whose commit hash fixes the whole source tree. That's ΔΣ=42 applied to the foundation.

The shape:

```
Python 3.8.2 + stdlib SHA-256  — pre-AI, verified by its published checksum
        ↓
snap.py                         — tiny; read, sealed, or retyped by the operator
        ↓
everything else                 — every change, AI-made or not, measured against the picture
```

Trade-offs:

- [ ] `snap.py` was written by AI in this session. Keep it tiny so it can be read and sealed, or retype it by hand (50 lines) so even the core is human-written.
- [ ] Old code is unpatched. Python 3.8 lost security support in October 2024, and 3.8.2 misses every fix from 3.8.3 to 3.8.20. Low risk for a script that only reads and hashes files; run it with no network.
- [ ] The line has to stop somewhere. `hashlib` usually calls OpenSSL, which sits on the OS, compiler and C library (Ken Thompson, "Reflections on Trusting Trust", 1984). Practical line: interpreter and directly-run code are pre-AI and fingerprinted; the OS is trusted as-is. Python's built-in SHA-256 can run without OpenSSL for one level deeper.
- [ ] Pre-AI is not bug-free. It proves who wrote the code, not that it's right, which is why the human seal still matters on top.

## Sources and caveats

No web pages were opened this session, so everything here is from memory and should be treated as approximate until Track 1 confirms it.

- Hans Peter Luhn's IBM memo proposing hashing: 1953
- MD5 published 1992 (RFC 1321); SHA-1 published 1995; SHA-3 standardized 2015 (FIPS 202)
- SHAttered, the first practical SHA-1 collision by Google and CWI: 2017
- LinkedIn breach of about 6.5 million unsalted SHA-1 password hashes: 2012
- NYC taxi trip data with MD5-hashed medallion numbers, reversed by enumeration: 2014
- SPHINCS+ standardized by NIST as SLH-DSA (FIPS 205): 2024
- Grover's algorithm roughly halves hash preimage security (SHA-256 to about 128-bit)
- Have I Been Pwned's range API sends the first 5 hex characters of a SHA-1 hash (k-anonymity)

## Desk check of the review (2026-10-05)

*Agent-reported. The desk read `onescript/record.py` on this box; it did not
re-run the attacks.*

| Finding | On this box |
|---|---|
| The chain can be cut or rewritten | **Holds in the code.** `verify_chain` checks only each row against its predecessor. The hash is unkeyed and the tip is stored nowhere else. |
| `h16` keeps 64 bits | **Holds.** `hexdigest()[:16]` in `record.py`, also used for `pile.json` pointers. |
| A garbled line crashes boot | **Holds.** `Record.rows()` runs `json.loads` on every line with no guard. |
| "No `deepthought.py`", "53 tests" | **Vantage, not drift.** `deep_thought.py` and `onescript/tests/test_capability.py` (24 tests) are untracked on this box; 53 + 24 is the 77 in next-pile.md. The stale "29 tests, local only" line in next-pile.md is real drift. |
| frank_ledger tip and fork | Not checked. Tracked code outside the one script. |
