<!-- b17: WGRV1  ΔΣ=42 -->
# Phone keys: made anywhere, checked at home

**Status: proposed, 2026-11-11. Not ratified; nothing here is built.**
Beside [phone-tier0-sync.md](phone-tier0-sync.md), which it would change,
and [phone-seat-production.md](phone-seat-production.md), whose decision
it keeps.

## The operator's idea

In their words, on the evening the phone first ran willow's study:

> Each box makes its own key that needs to be signed. When it comes back
> home is where the issue is. So that I think is where the security layer
> needs to be is not necessarily where the key is produced but where it's
> verified.

So a box on the phone may make its own key. What matters is the door at
home: what comes back is accepted only if it proves it came from a box
home already knows.

## Why the kernel's own key can't carry this

A willow box's seal is an HMAC-SHA-256 under the box's key (`kernel.py`,
`proof`). To check an HMAC, the checker must hold the same secret that
made it. A seal made on the phone could be checked at home only if home
held the phone's secret, and then the secret has travelled: anyone who
copies it can make seals. So the kernel's key stays where it was made, and
proving where something came from needs a second key whose public half can
travel: a signature, not an HMAC.

## What already exists

Checked on the maintainer's machine and in the repositories, 2026-11-11.

| Piece | Where | What it does already |
|---|---|---|
| `share` add-on | willow, `adapters/stdlib/share/` | `share id` makes an Ed25519 pair; the secret half stays in its file, the public half (64 hex) can be shown to anyone. Packages of sealed answers are signed and checked by the public half alone. A key is replaced by a `rotated` row naming both keys, signed by the old one |
| `pgp` add-on | willow, `adapters/deps/pgp/` | signs exports with the person's PGP key; `verify` refuses a signature by a key the keyring doesn't have |
| A public-only verify ring | the box: `/etc/willow-mcp/verifiers.public.json` | root-owned, no secret half, can't sign. [nestor-seal-keyring.md](nestor-seal-keyring.md) §4 already says every reader that only checks points at it, and signing stays in one place: checking is already apart from signing |
| Identity binding | willow-mcp, `identity_binding.py` | a first sign-in makes an unconfirmed binding; only the operator, at the local terminal, confirms it (`confirm_binding`: "Not reachable from any MCP tool") |
| u2u contacts | this repo, `u2u/contacts.py` | known LAN peers, each with its Ed25519 public key; every consent off until granted kind by kind; `add` refuses a known address; a key rotation is refused unless a human confirmed it |
| Homecoming deposit | [phone-tier0-sync.md](phone-tier0-sync.md); the APK's `homecoming.js` | the phone's way home over USB. Unsigned: "Review it; do not treat it as sealed." |

## The gaps

1. **Nestor's import checks what, not who.** `portable.verify_bundle`
   checks that a bundle is well formed and is the one exported (its
   digest). Without `NESTOR_SEAL_KEY` set, `import_bundle` takes anything
   marked sealed as sealed; Nestor's own test says so
   (`tests/test_unconventional.py`, `TestBundleForgery.
   test_unsigned_import_trusts_bundle_word`: "A crafted bundle can inject
   false seals into an unsuspecting instance").
2. **The homecoming deposit carries no signature**, so the box can't tell
   the phone's deposit from anyone's.
3. **No ring of enrolled device keys** refuses an unknown signer at the
   door. u2u's contacts are that list for LAN peers; nothing is for a
   device's packages. The nearest thing in willow is an idea on its list,
   `signed-commits`.

## The shape proposed

The pieces above, put together; nothing new but the door.

1. **On the phone,** its box (its kernel key never leaves) and a `share`
   identity of its own.
2. **Enrolled at home, once, over the cable.** The phone shows its public
   half; the operator confirms it at the local terminal, as identity
   binding confirms a sign-in, and it goes into a public-only ring like
   the one Nestor's readers check against. The cable is the trusted
   channel for this one step, and nothing secret crosses it.
3. **Home, as a signed package.** The homecoming deposit travels as a
   `share` package signed by the phone's identity.
4. **Checked at the door, before anything lands:** the signature against
   the enrolled ring; the phone's record chain whole; and every row from a
   box that was enrolled. What fails is refused there and said, wherever
   it was made.
5. **Nestor stops taking a bundle's word.** An import with no signer it
   can check holds a claimed seal as a suggestion, not a seal.

A key replaced on the phone comes home as `share`'s `rotated` row, signed
by the old key; home takes the new key only on the operator's word at the
terminal, as u2u's `update_key` already demands.

## What it keeps, and what it leaves open

- **It keeps** "Phone only proposes, seal in Nestor on the box"
  ([phone-seat-production.md](phone-seat-production.md)) as one setting:
  a seal made on the phone arrives as *sealed by the phone*, and home can
  show it so, or hold it as a suggestion until the operator seals it at
  home. Which one is the operator's to choose.
- **Open:** whether the ring is willow-mcp's verifier ring, Nestor's, or a
  ring of its own; whether a lost phone's key is revoked by a row, and
  where that row lives; whether a deposit not yet checked waits at the
  door or is refused outright.

## What this is not

- Not a new cipher or format: `share`'s packages and Ed25519, as they are.
- Not the phone holding the operator's own signing key; the operator's
  key (`f8c34c93`) stays on the box.
- Not a change to the kernel: its key stays an HMAC key, and stays put.
