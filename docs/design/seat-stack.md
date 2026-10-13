<!-- b17: WGRV1  ΔΣ=42 -->
# Willow seat stack — phone, session, bus, desk

Written 2026-09-07. Un-stalls grove seat work now that **Ratatosk** lives in
`willow-memory/ratatosk` and on the fleet manifest (`role: session_runtime`).

Persona partition still holds: **Willow** owns what the desk is for;
**Heimdallr** owns whether the served surface tells the truth
([grove-persona-partition.md](grove-persona-partition.md)).

## The stack (top to bottom)

```
┌─────────────────────────────────────────────────────────────┐
│  Phone / desktop seat UI (Capacitor Willow, Termux, CLI)   │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│  Ratatosk — session runtime (willow-memory/ratatosk)         │
│  Crown + hooks + permission gate; optional --mcp to muscle   │
│  RATATOSK_GROVE_CHANNEL → grove_send_message on lifecycle    │
└───────────────┬─────────────────────────┬─────────────────┘
                │                         │
                │ stdio / HTTP MCP        │ grove bus (when channel set)
                ▼                         ▼
┌───────────────────────┐     ┌───────────────────────────────┐
│  willow-mcp --serve    │     │  Grove channels (Postgres)     │
│  OAuth / PKCE sign-in  │     │  Heimdallr watch reads these   │
│  operator box: :8768*  │     │  Desk page :8766 loopback only │
└───────────────────────┘     └───────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│  Tier-0 homecoming — USB/adb deposit to the box (not vault)  │
│  phone-tier0-sync.md                                         │
└─────────────────────────────────────────────────────────────┘
```

\* Package default port is **8765**; this operator box runs **`--serve` on
8768** so 8765 stays Nestor UI / verifier origin. See
[phone-seat-production.md](phone-seat-production.md).

## Port map (do not mix these up)

| Port | Service | Phone? | Auth |
|------|---------|--------|------|
| **8765** | Nestor UI / keep / default `willow-mcp` in source | No | Browser key / origin-bound |
| **8766** | Grove desk HTML (`grove_serve.py`) | **Never** — D4 loopback | None |
| **8767** | Grove MCP (`grove/mcp_local.py --serve`) | Tunnel OK | OAuth / PKCE |
| **8768** | `willow-mcp --serve` on this box | **Yes** — phone sign-in | OAuth / PKCE |

Executable assertions: `tests/test_port_map.py` (8765/8766/8767); phone
ratification for 8768 is operator config, not yet encoded in that test file.

## What each layer owns

| Layer | Owns | Does not own |
|-------|------|----------------|
| **Willow seat** (`seat/willow/`) | Probe scripts, intake JSON, desk composition doctrine, federation unblock wrappers | Grove HTML, watcher, `:8766` bind |
| **CLI seat** ([`grove/seat_cli.py`](../../grove/seat_cli.py)) | The terminal front end: stages over willow-bot's `onescript/api.py`, the box stream, the checked reply sentence, the pooled-proposal deposit | Any seal or seal key, a model provider choice (Rat's ladder picks), a listener |
| **Ratatosk** | Session lifecycle, tool permission gate, Grove bus posts when configured | Charter law, vault keys, desk rendering |
| **willow-mcp** | Muscle, envelopes, store, dispatch, `--serve` | Persona roster curation (reads charter) |
| **Heimdallr / Grove** | Served desk honesty, resident watcher, `:8767` MCP resource | Operator seat scripts under `seat/willow/` |

## CLI seat

The third front end beside the web components and the phone APK. All three
call willow-bot's `one-script/onescript/api.py`, so a terminal run leaves the
same record rows the app does. Run it with
[`scripts/grove-seat`](../../scripts/grove-seat): a terminal process, no
listener, no port. Code: [`grove/seat_cli.py`](../../grove/seat_cli.py).

Stages, in order:

| Stage | What happens |
|-------|--------------|
| checkin | `api.checkin`: the record, the probes, the four gates |
| resume | `api.resume`: the newest human-sealed scope, pinned at its `upto`; none or unreachable scopes fresh |
| scope | `api.scope` proposes a stack and names its subject |
| served | `api.serve`, the silent start-check: serves only a scope a past seal covers |
| chain | `api.escalate`: D0 code, then the hash record, then a local rung |
| flowering | one cloud turn on the human's yes: `ratatosk --onescript --class flowering` (Rat's ladder picks the provider) |
| proposals | each pass shown and left pooled, nothing sealed |
| checkout | `api.checkout`, then the pool deposited into Nestor as drafts |

**Reply sentence.** A reply is box cards plus one sentence
([`grove/seat_boxes.py`](../../grove/seat_boxes.py)). A local model says it,
`qwen3:4b` on the Ollama loopback (override with `GROVE_SAY_MODEL`), and code
checks it against the boxes: every cite served, every box cited, nothing the
boxes lack, the human's words quoted exactly
([`grove/seat_say.py`](../../grove/seat_say.py)). A failed check strikes the
sentence and code's own stands; an unreachable model is an `unreachable` card
and the same code sentence, never a crash.

**Never seals.** No prompt asks for a seal and the seat holds no key. At
checkout one `seal ↗` offer points at the Nestor UI (`:8765`), the only place
a seal is made.

**Venv.** `scripts/grove-seat` takes the first that exists: `GROVE_VENV`,
`$WILLOW_HOME/willow-bot/venvs/willow-bot`, the legacy
`$WILLOW_HOME/venvs/willow-bot` (with a stderr warning), `./.venv`, then
`python3`.

## Ratatosk ↔ Grove wiring

Environment:

- `RATATOSK_GROVE_CHANNEL` — channel name for `grove_send_message` (unset =
  grove posts skipped, not an error).
- `--mcp` — connect Ratatosk to willow-mcp stdio so bus sends are receipted.

Probe from the box:

```bash
cd ~/github/willow-memory/willows-grove
. ~/github/willow-memory/.willow/fleet.env   # or your fleet join
bash seat/willow/scripts/willow-seat.sh probe
```

The probe prints a **ratatosk** section: package version, channel, and a
dry `grove.send()` receipt (skipped / sender-missing / ok).

## Related docs

- [phone-seat-production.md](phone-seat-production.md) — Willow app ids + 8768
- [phone-tier0-sync.md](phone-tier0-sync.md) — homecoming deposit
- [phone-surface-context.md](phone-surface-context.md) — longer phone audit
- [willow-grove-premise.md](willow-grove-premise.md) — Ratatosk row in org table
