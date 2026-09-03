# Build order — the six proposals of 2026-09-02

**Status:** index · drafted by willow 2026-09-02 · **the order is the operator's, stated as a question and answered from the record**

The question: *was Jarvis smart because of the AI, or because of the
information it had access to?* The record answered on 2026-07-01 (KB
C8BE7D78): the moat is context, not IQ. So the order is information first,
connections second, the model last and smallest. Every proposal below is the
system under the voice. None of it is what a person talks to.

| # | Proposal | What it gives the voice | Layer |
|---|---|---|---|
| 0 | the design-intent record, and the sealed constraint from [`2026-09-02-grove-hooks-and-skills.md`](2026-09-02-grove-hooks-and-skills.md) §0 | the operator's intent, written where the tools can read it | information |
| 1 | [`2026-09-02-unit-retirement.md`](2026-09-02-unit-retirement.md) | no false sensors: two dead timers stop writing, one unit manifest says what belongs | information |
| 2 | [`2026-09-02-grove-hooks-and-skills.md`](2026-09-02-grove-hooks-and-skills.md) | the house writes itself down: session-end deposit, Grove in the corpus, orient from readers, the seat in every turn | information |
| 3 | [`2026-09-02-packet-lifecycle-adr.md`](2026-09-02-packet-lifecycle-adr.md) | every packet ends and is recorded; a packet names its envelope, the first edge in the connection layer | information, then connections |
| 4 | [`2026-09-02-governed-path-write-gate-v2.md`](2026-09-02-governed-path-write-gate-v2.md) | the law cannot be rewritten by a file edit, so what the readers read is what root ratified | integrity of the information |
| 5 | [`2026-09-02-local-inference-seam.md`](2026-09-02-local-inference-seam.md) | one local runtime, harnessed, at the leaves only | model |
| 6 | [`2026-09-02-mcp-jobs-ladder-test-plan.md`](2026-09-02-mcp-jobs-ladder-test-plan.md) | which model clears which leaf, measured on this box | model, last |

## Why this order and not the one they were drafted in

They were drafted in the order the day found them: the stuck packet first,
the model questions in the middle, the hooks last. That is the order of
discovery. The order of building runs the other way.

- **Retirement before anything.** A sensor that reports from a tree that
  no longer exists is worse than no sensor. Step 1 costs one terminal
  session and removes the last noise from the old generation.
- **The deposit before the packet.** The packet lifecycle records what a
  specialist did. The deposit records what every session did, specialists
  and seats alike, whether or not a packet was involved. Most of today's
  work happened in no packet. Step 2 is what would have written it down.
- **The packet before the gate.** The gate protects the registry. The packet
  ADR makes the registry load-bearing by refusing a packet whose envelope
  is not active. Build the thing that reads the law before hardening the
  law against writes, so the hardening has a consumer.
- **The seam before the ladder.** The ladder measures models through
  harnesses. The seam defines the harness. Measuring first would measure a
  shape that then changes.
- **The model last.** Step 6 is the only step that can be skipped without
  the voice being less true. A 3B with steps 1 through 5 in front of it is
  better placed than a 70B without them. The ladder decides which rung
  runs which leaf; it does not decide whether the leaf exists.

## What each step needs from the operator

| # | Act |
|---|---|
| 0 | seal one pair in `nestor.ui`; ratify the design-intent atom |
| 1 | run the command block in the retirement record |
| 2 | one entry change in `mcp/projects.json`; add Grove to the corpus roster; a narrow `fs.write` envelope for this repo |
| 3 | the same envelope, extended to the dispatch and handoff modules |
| 4 | root's decision: grant or own hand |
| 5 | the envelope, extended to Nestor and Jeles; `allow_localhost` for the first harnessed run |
| 6 | `allow_localhost` for one Kart batch task, one night |

One envelope, widened three times, covers steps 2 through 5. That is the
envelope-accrual loop doing what it was built for.

## What the phone gets from each step

The Grove APK is not built. Its governing decision is **KB 2026B306**,
operator directive of 2026-09-01, which supersedes the thumb-drive decision
of 2026-08-30 (`docs/design/phone-surface-context.md` §12, Nestor drafts 9
through 14). The thumb drive removed a forced choice; it did not forbid the
second mode. The phone is **both** a removable volume and a network peer,
and it runs its own model, so the modes differ in reach, not in whether the
phone can work:

| tier | path | gate |
|---|---|---|
| 0 | USB, `adb` | none new; in production one direction already |
| 1 | LAN, u2u | signed, plaintext: signals only until Gate 6 |
| 2 | remote, Pangolin terminating at **:8765 only**, never :8766 | the ratified remote seat; Starlink is CGNAT so a public rendezvous is structurally required |

And the app itself is a **capability-composition chain**: if Nestor is
installed, connect it to willow-mcp and Grove; if Jeles, wire the corpus; if
Hornbook, its organ. Each install discloses both halves, what becomes
possible and what becomes reachable, or it is marketing rather than consent.
The seat's observation, sealed with it: this is Kart's `bind_try` one level
up, and it needs no new authorization concept, because authorization is
already the intersection of a manifest grant and a ratified server's tools,
surfaced at install time instead of call time. Read against that:

| # | Helps | Hinders or leaves open |
|---|---|---|
| 0 | The rung model *is* the phone: a worktree, a manifest, a harness, reach fixed by the box. | — |
| 1 | Tier 0 and tier 1 touch no port. | **Tier 2 does.** 2026B306 says Pangolin terminates at :8765 only. Operator, 2026-09-02: signing outranks serve, so the Nestor UI holds 8765 and serve sits on 8768, recorded in the port table of the hooks proposal. The remote seat is re-ratified against that table, or serve returns to 8765 once the browser key's origin is fixed (gap `d8b0bea7e205`). The Pangolin adapter landed 2026-09-01 and fronts whichever port the table says. `apps/jarvis` signs in by the same URL. |
| 2 | The session-end deposit is the sync payload. What a phone session writes into its project Nestor is exactly what `nestor export` carries home and `nestor import --apply` lands. Decision 11 named that primitive; the deposit says what goes in it. | The "store is open, sign?" row assumes a UI on the box. On the phone, signing meets the origin-bound key problem from gap `d8b0bea7e205` a second time. |
| 3 | A packet is a directory of JSON and Markdown: it copies to a volume unchanged. `failed` and `expires_at` are what a device that leaves for days needs. `envelope_ids` in signed meta make an offline accept checkable. | Accept re-checks the **enforced** registry. Off the box that is a snapshot; the ADR must say accept-offline checks the carried snapshot and re-verifies on sync. Expiry must exceed the sync cadence. |
| 4 | The registry the snapshot is taken from cannot have been hand-edited. | — |
| 5 | Nestor's engine is loopback Ollama, which Termux runs. The harness is model-agnostic. Decision 14: ratatosk's shape is right, only its transport was wrong. The phone runs the twenty cheap steps. | Phone-side Nestor needs `--engine ollama` and `--corpus-dir`, neither set in the live config. And the payload finding stands: a corpus map plus one search is 55% of a 4k window served, 10% lean (#261). |
| 6 | The 4k arms in the ladder are the phone's yardstick; `willow-lane4-3b` runs at 4096 by its own Modelfile. | The ladder runs on the box. A phone rung table is the same runner on the device, once. |

What landed in the last four days that the phone stands on, none of it in
the six: the Pangolin adapter behind the egress gate (willow-mcp 415), the
Nestor established lane installed at fleet standup so commons facts serve at
tier 1.5 without a seal (willow-mcp 417, Nestor 408314e), Jeles auto-promoting
core seed nuggets to the machine rung, and the vault's content-addressed
index that answers "do I already hold this file" by digest through archives
(willow-data-vault 20cf8de). The Forge's first-bite demo of 2026-09-01 walked
one person through one day and reported **the phone seat** as missing
outright, beside the keyword table, the playground, and a calibration ledger
with zero callers.

Two gaps none of the six touch, both already open in the phone doc:
`kart-sandbox.json` names the Android SDK zero times, so the build stage
fails inside the sandbox on a toolchain the host has; and the sync stage has
no script, only a primitive. Those, plus the phone seat itself and the
install-time disclosure chain, are the next proposals, not amendments to
these.

## Connections

The connection layer that the Forge-shape doc measured at zero rows is not
a step of its own. It is filled by three of the steps above: the packet's
`envelope_ids` (step 3), the deposit's edges (step 2), and the hook rows as
decision pairs (step 2, §6). Adding a seventh proposal for "edges" would be
prose about a table. The table fills when the steps that write to it run.

*ΔΣ=42*

## Progress — 2026-09-03, recorded by the willow seat

Read against the rows above, from the record (handoff `2026-09-03-df72e542`, FRANK 80609939 / 93e041a1 / 4db66d5b, #handoffs 375).

| Step | Moved | Still open |
|---|---|---|
| 0 | Operator sealed 99 pairs in `nestor.ui` on 8765, 67 of them Forge-origin; the Forge project store now holds them verified against the fleet keyring. | The design-intent atom is unchanged. |
| 1 | **Done.** ada retired 22 fossil units under envelope `env-shell.exec-b31eee38a08f`, packet 276C7A34 verified and cleared; after-state matches the retirement record. | The two ngrok units (binary still present) left for the operator. |
| 2 | The house can now hear: `willow-mcp grove-listen --app-id <seat>` (willow-mcp #421, merged) is 2.0's LISTEN/NOTIFY monitor rebuilt on the gate; the session-start skill names it for every seat. Session-end deposit done by hand this once: handoff file plus a pointer in #handoffs. | Tracked hooks, reinject, stop gate, Grove in the corpus — untouched. jeles and loki still hold no `grove_read`. Presence reads six hours stale (naive local timestamps read as UTC, gap a2ea88cc006b). |
| 3 | First full lifecycles on record: six packets sent under a ratified `dispatch` envelope, accepted, handed off, verified against the artifact, cleared (D83F9739, A47DD0CB, 276C7A34, 5ED80CC1, A09139D2, C01EA727). E8FD5CC1 parked by hand (`status.json` closed, meta untouched). | No withdraw verb still (afa515539c0a). `verify_handoff` demands a `text` key per finding that `handoff_write_v4` never asks for (5805dba0ad47). Witness and architect seats needed operator grants to close at all (2f20111ea877). |
| 4 | The enforced register was used as law for the first time since the planting: eight envelopes proposed and ratified under a keyring-attributed session; `dispatch_send` refused a role outside the envelope's task class (EAMBIG) and was right. | The register writer leaves `pre-approved.json` group-writable after every write, so `trusted_read` refuses the next read until the operator chmods (6b4b7737c535). Attestation and attribution are two locks under two key systems (bcd8b6d918da). Forge pushes had no envelope of their own; recorded on FRANK instead. |
| 5 | Nothing. The five packets were reviewed for fit against the seam proposal's own rule and none was safe for a local model; Sonnet seats ran them. | As drafted. |
| 6 | Nothing. | As drafted. |

Landed elsewhere the same night, feeding row 3: Forge #5 (PR-time deposit, propose-only as a type after loki's review), #6 (bundle cut/check, witnessed by skirnir), #8 (store diff, both loki notes fixed on-branch); v0.2.0 tagged; willow-bot #10 (bridge keys check runs on the check id, carries head_sha); store #219 (record-gate pointer).
