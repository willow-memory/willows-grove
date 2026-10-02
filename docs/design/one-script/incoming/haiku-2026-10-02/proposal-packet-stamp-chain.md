# Proposal: ΔΣ=42 — Packet Stamp Chain and Node-to-Node Custody

**Status:** Agent-reported, unattested. For the operator's review and decision.

**Cites:** CONST-VI (The Record), §0.5 (Record is append-only), workflow.md §8 (Chained gates on a packet), next-pile.md §Three rules

**Amends:** Clarifies and formalizes the ΔΣ=42 checksum concept from the constitution preamble into operational gates for inter-node communication.

---

## The Problem: Data Custody Across Nodes

When a data packet leaves one node and arrives at another (locally or across a network), three things must be true:

1. **What left was what arrived** — no bit flips, no redaction, no silent compression
2. **If something changed (legitimately), the change is declared and signed** — the layer that changed the packet owns the change
3. **The human can see the chain of custody** — every step, every signature, every declared change

Today's problem: a packet can be silently modified at a layer, and the next layer has no way to know. The only audit is retroactive, in logs.

ΔΣ=42 (Delta Sigma) proposes: **a chain of gates, one per layer, where each gate verifies the previous gate's stamp and adds its own.**

---

## The Gate Chain Architecture

A packet in transit has this shape:

```
┌─ Packet ─────────────────────────────────────┐
│                                               │
│ [Payload] | [Intent] | [Signature Chain]    │
│                                               │
│ Intent: {who, what, where, action}          │
│                                               │
│ Signature Chain:                             │
│   Gate 0 (sender): hash(payload), stamp S0  │
│   Gate 1 (network): hash(payload), stamp S1 │
│   Gate 2 (receiver): hash(payload), check    │
│                                               │
└──────────────────────────────────────────────┘
```

### The Stamp (Each Gate's Record)

A stamp is deterministic and immutable once issued. It contains:

| Field | Content | Who sets | Purpose |
|-------|---------|----------|---------|
| **hash** | SHA-256(payload + intent) | This gate | Detect any change to content or intent |
| **intent** | {who: agent ID, what: action type, where: destination, action: read/write/transform} | Sender (gate 0); inherited by others | Declare what the packet is supposed to do |
| **timestamp** | Seconds since epoch, recorded at this gate | NTP or system clock | Prevent replay attacks (gate *n* rejects old timestamps) |
| **nonce** | Unique random per packet | Gate 0; same nonce through the chain | Prevent replay and tie all stamps to one packet |
| **prior_hash** | Hash of the previous gate's stamp (gate 0 has prior_hash = 0) | This gate | Chain the gates together |
| **key_id** | ID of the signing key | This gate's identity | Prove which gate did the signing |

**Signing rule:** The stamp is signed with this gate's private key. A stamp is `valid` if:
- The signature verifies with the public key named in key_id
- The timestamp is recent (within configurable drift; default 1 hour)
- The nonce hasn't been seen before (recorded in a bloom filter at each gate)
- The prior_hash matches the previous gate's stamp hash

### What Each Gate Does

**Gate 0 (Sender):** Creates the packet, sets intent, computes hash, stamps it, and signs it.

**Gate 1…N (Intermediate Layers):** 
1. Verify Gate 0's stamp (or the previous gate's, if they exist).
2. Compute the hash of the payload **as received** (this is the "what arrived" measure).
3. If hash matches: append a new stamp (intent unchanged, new timestamp, same nonce, prior_hash = previous stamp hash).
4. If hash differs: the packet has been modified. This gate must choose:
   - **Declare the change** (Amend intent to {action: "compressed", bytes_out: X}, stamp and sign) and continue, or
   - **Reject** (refuse to pass, log the change, return error to sender with proof)

**Gate N+1 (Receiver):** Verifies the last gate's stamp, then checks the full chain backward (each stamp validates its prior). If any link is broken, the reception fails loudly with the break point named.

---

## Legitimate Transformations (Amend, Don't Hide)

Some layers must transform the payload: compression, encryption, filtering, redaction. Each one is a gate:

| Transformation | Intent field change | Stamp | Chain continues |
|---|---|---|---|
| Compression | `{action: "compressed", original_bytes: X, output_bytes: Y}` | New stamp, new timestamp, nonce preserved | Yes; next layer sees the intent |
| Encryption | `{action: "encrypted", cipher: "AES-256", key_id: K}` | New stamp, nonce preserved | Yes |
| Filter (redact) | `{action: "filtered", filter_id: "pii-strip-v2", fields_removed: [list]}` | New stamp, nonce preserved | Yes |

Each transformation is a gate, not a secret. The intent grows as the packet flows.

---

## Disagreements and Rejections

If a gate detects a mismatch **between the prior hash it received and what it recomputes**, the packet stops and both sides are notified:

1. **The rejecting gate logs** the mismatch with both hashes, the payload hash it computed, and the point in the chain where the break occurred.
2. **A rejection stamp is issued** (same structure, but intent is `{action: "rejected", reason: "stamp_mismatch", prior_hash_received: X, prior_hash_computed: Y}`).
3. **Sent to sender AND receiver** with the full chain so far. Both can see where the chain broke.
4. **Recorded in the Ledger** (CONST-VI: every break in custody is a recorded event).

**No silent drops, no unplanned transformations.** A packet that can't be verified doesn't silently succeed with reduced trust; it fails loudly.

---

## The Bloom Filter and Replay Prevention

Each gate maintains a time-windowed bloom filter of nonces seen in the last 24 hours:

- **At creation (Gate 0):** The nonce is unique and random, added to the filter.
- **At each gate:** Reject if the nonce is in the filter and the timestamp hasn't aged enough (within 1 hour by default, adjustable).
- **Age-out:** Nonces older than 24 hours are discarded from the filter.

This prevents:
- Replaying an old packet twice in one window
- Reordering packets (a late-arriving packet with an old timestamp is rejected)
- An attacker forging a packet with a guessed nonce (entropy is high, and the window is short)

---

## The Ledger Integration

Each packet's final stamp is recorded in the Ledger under CONST-VI:

```
Entry: {
  type: "packet_transit",
  nonce: <packet nonce>,
  sender: <gate 0 identity>,
  receiver: <final destination>,
  intent: <final intent after all transforms>,
  chain_length: <number of gates traversed>,
  final_verdict: "verified" | "rejected",
  chain_hash: hash(all stamps concatenated),
  timestamp: <gate N's timestamp>
}
```

If the verdict is "rejected", the mismatch details are included:
```
  rejection: {
    gate_id: <which gate rejected>,
    reason: "stamp_mismatch",
    prior_hash_expected: X,
    prior_hash_computed: Y,
    chain_so_far: [all stamps before rejection]
  }
```

The Ledger becomes the canonical record of custody. Queries:
- "Did this packet's hash change between nodes?" → Check Ledger entries in order
- "Which gate certified this transformation?" → Read the intent and key_id from the relevant stamp

---

## Wire Format (Agent-Proposed)

The packet on the wire (TCP/UDP/HTTP):

```
[Payload] | [Intent JSON] | [Stamp 0 JSON] | [Sig 0 Base64] | 
[Stamp 1 JSON] | [Sig 1 Base64] | … | [Nonce]

Length: variable
Encoding: UTF-8 for JSON, Base64 for signatures and nonce
Hash: SHA-256 throughout (deterministic, no collisions in practice)
```

A gate reading this packet:
1. Extracts the nonce at the end (fixed 32 bytes)
2. Reconstructs the payload and intent
3. Verifies each stamp signature in order
4. Computes its own hash of the reconstructed payload
5. Appends its own stamp and signature
6. Re-sends the full packet to the next gate

The signature overhead is ~150 bytes per gate. A packet through 5 gates adds ~750 bytes.

---

## Open Decisions (Operator's Call)

1. **Enforcement level:** Is ΔΣ=42 mandatory for all packets, or only for packets carrying law changes (amendments, precedents, sealed claims)?

2. **Internal vs. external:** Do inter-node packets need this (where nodes are in the same data center), or only cross-network?

3. **Timestamp drift tolerance:** How out-of-date can a packet be before it's auto-rejected? (Draft: 1 hour; could be 10 minutes for high-security, 24 hours for caches.)

4. **The bloom filter:** Should each gate have its own, or should there be a central (Ledger-backed) nonce registry? (Trade-off: distributed is faster, central is authoritative.)

5. **Payload format:** Is this required for all packets, or can a gate opt out for internal, non-law-affecting data? (E.g., a cache query doesn't need it; a permission check does.)

---

## Implementation Notes

**Existing reference:** in-toto (Apache-2.0, CNCF) does something similar for CI/CD steps. Each step signs what came in and what went out, and a final check confirms the chain matches the declared layout.

**Key difference here:** The gate config is per-user / per-operator, and the final authority is human attestation, not a company policy server. The chain is as strong as the weakest link, but the weakest link is audited.

**Build order:** Part of resolve.py (layer 5 if gates are runtime) or Part of boot.py (layer 1 if gates are startup). Either way, it's a door, so it belongs in gate.py (layer 4).

---

## References

- workflow.md §8 (Chained gates on a packet)
- next-pile.md §Three rules from tonight (The stamp)
- CONST-VI (The Record, append-only)
- ΔΣ=42 (constitution preamble)
- in-toto: https://in-toto.io (architecture inspiration)

