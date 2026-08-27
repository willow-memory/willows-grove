<!-- b17: WGRV1  ΔΣ=42 -->
# u2u security limits — what it does, and what it does not

This doc names the security properties `u2u/` provides *today*, and — more
importantly — the ones it does not. It exists because `safe-app-manifest.json`
and `README.md` previously advertised u2u as "End-to-end encrypted" / "Encrypted
LAN transport" while the wire format was plaintext JSON on a bare TCP socket
(see `CODE_REVIEW.md` P0 — "the manifest claims u2u is encrypted; it is not").
INVARIANTS.md §6 says the manifest describes code, not aspirations. This is
where the aspiration lives instead.

## Guarantees u2u provides today

- **Authenticity.** Every accepted packet carries an Ed25519 signature over its
  payload; the listener runs `Packet.validate(packet, contact.public_key_hex)`
  before dispatching to a registered handler. An impostor with a different
  private key cannot present a packet under the signer's `from` address that
  passes the check.
- **Integrity.** The signature covers the packet body, so a wire-level tamper
  (bit flip, replay of a modified payload) fails validation and is dropped.
- **Non-repudiation within the signing-key boundary.** If you hold a peer's
  public key and their signed packet, the signer cannot deny having produced
  that exact payload — bounded by the assumption that their signing key was not
  compromised or copied. u2u knows nothing beyond that boundary.

## What u2u does NOT provide

- **Confidentiality.** `Packet.serialize` at
  [`u2u/packets.py:74-75`](../../u2u/packets.py) writes
  `json.dumps(packet, separators=(",", ":")) + "\n"` onto a bare
  `asyncio.open_connection` socket. There is no key agreement, no AEAD, no TLS,
  no application-layer sealing. The `cryptography` dependency is imported only
  for `Ed25519PrivateKey` / `Ed25519PublicKey` — **signing**, not encryption.
- **Traffic confidentiality.** Anyone on the LAN path — same Wi-Fi, same
  switch, same tap point — can read every DM body, sender, recipient, and
  timestamp in cleartext.
- **Forward secrecy.** Nothing to be secret in the first place. Non-goal today.

## What using u2u today means for the operator

DMs are as private as the LAN they travel across, and no more. On a trusted
home LAN with no attackers on-path this is fine. On a coffee-shop Wi-Fi, a
compromised switch, or any network you don't own, treat u2u DM bodies as public
to that segment. Signing still buys you authenticity — an impostor can't
convincingly *forge* a DM from a peer whose key you know — but it buys no
secrecy.

## Planned — Gate 6

Real confidentiality is a Gate 6 conversation, not a v0.9 patch. The current
plan (subject to Gate 6 review):

- Add an AEAD confidentiality layer per-contact — likely Noise (IK) or `age`
  recipients — over the existing signed-JSON envelope.
- Keep Ed25519 signing exactly as it is; the confidentiality layer sits on top,
  it does not replace authenticity.
- Wire format bump (`U2U-WIRE-2`) with a negotiated fallback so Gate-6-and-newer
  peers can still speak to Gate-5 peers during the migration, at the cost of no
  confidentiality on that hop.

Until that lands, do not treat u2u as encrypted, do not describe it as
encrypted in operator-facing docs, and do not carry the word "encrypted"
through a manifest that claims consumer trust.
