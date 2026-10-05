# One-box ↔ the four pieces join

Companion joining [`README.md`](README.md) (one-box) to the four pieces named
on 2026-10-05 in [`../one-script/README.md`](../one-script/README.md) ("Where
the reading lands"): one script, serve, one hook, one key. Desk session
019xJcd52XquwTaeZYqKL8QH. The operator: "check out the one box stuff too", then
"write the join". Agent-reported; no seal invented.

---

## Each piece, and where one-box already has it

| Piece | Already in one-box | Where |
|-------|--------------------|-------|
| **One hook** (`hook.py`, PR 107: Read allowed, Write asks, everything else denied) | "Reading is open; saving is guarded": the public-repository metaphor, where anyone clones and a human merges. The hook's policy line is that rule | §0 rule 1b; session 10-01 |
| **One key** (the human seals) | "Presence is a label; authority is a passkey": a WebAuthn grant the server only verifies. Janus's rule is already written: "the passkey challenge hashes that outbound content, so a one-time Yes covers only those bytes" | §0 1c; §9 (egress means outbound); §15 1–2 |
| **One script** (code drives) | D1 (Rat is the one runtime) and D2 (everything lives inside willow-bot) are sealed (`02050acf`, `656a352f`). Q14: one-script's gate is a decision step, not a fourth Gate process | [`one-script-join.md`](one-script-join.md); next-pile |
| **Serve** (only the tables in scope) | In part: the IN-door pool bundle; untrusted text wrapped as a labelled data block; Nestor read as a neighborhood by explicit edge, so "the deterministic system will return all the info, instead of just the one chunk the model wants" | §15 4; session 10-01, tool surface |

---

## What the bare hook settles

| One-box item | Before | With the bare hook |
|--------------|--------|--------------------|
| §15 1, the model runs as the operator's uid | The model's shell can reach Rat's socket, and `SO_PEERCRED` can't tell it from the operator. Ops split into model-reachable and human-only | The model has no shell. It can't reach a socket at all; the split stays for every other caller |
| Phase 8, the model-facing surface | About 169 tools; observe a week, then narrow to all reads, propose-only writes and one "hand to Rat" verb | Two tools: Read, and Write with the human's yes. No hand-to-Rat verb: the script runs, the model reads what it served |
| Phase 6, egress via the client's web tools | Disabled or reported `unenforced` | Denied: WebFetch and WebSearch aren't Read |

## What it doesn't settle

| One-box item | Why it still holds |
|--------------|--------------------|
| §15 3, the doors can be removed | A hook works only while it's wired. The model can't Edit, but it can ask to Write `.claude/settings.json`, and a yes there unwires everything. One-box's answer stands: install the hook through managed settings (`allowManagedHooksOnly`), which the operator's uid can't write without sudo; detect a missing door |
| Three-dialect OUT ([`crosslink-appendix.md`](crosslink-appendix.md)) | Claude Code honors the JSON decision; Windsurf and Kiro need exit 2; Goose blocks only on PreToolUse. The policy line is the same everywhere; the output format is per front end |
| §15 4, pooled content is untrusted | The model reads served text, so injection can still arrive through a Read. It has no hands to act on it, which leaves the worst case a bad proposed write, which the human sees before saying yes |

---

## The contradiction

**One-box:** "Read verbs are not gated or hidden" (§0 1b), and Phase 8 makes
"all reads" model-facing.

**Serve:** the model reads only the tables in its scope, and a table out of
scope isn't named, counted or marked. "If the model never even knows the Box
exists" (the operator, 2026-10-05, the security core).

Both can't hold for the model. The 10-05 security core ("what are we willing
to show it?") reads as a turn away from 10-01. One reading that keeps both:
reading is open for people (the public repository; local material never
needs a grant), and the model reads only what's served. **Q19, the
operator's.**

---

## What one-box adds to serve

1. **A trust label on every served table:** `untrusted` or `human-sealed`,
   with its source receipt (§15 4), so pooled text arrives as data and never
   reads as instructions.
2. **A home.** Under D2 (sealed), serve lives inside willow-bot.
3. **Fail closed and loud** (box rule 1a): no sealed scope, nothing served,
   and the empty serve says why (three-state: empty is not unreachable).

---

## What this join does not do

- Does not seal Q19, or any D-decision still open.
- Does not build serve or wire the hook.
- Does not retire any one-box phase. Rat, the sockets, portless and the
  egress grant are where the four pieces run; this join names what changes
  for the model, not for the box.
