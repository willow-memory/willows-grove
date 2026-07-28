# Willow Grove

Unified human+agent dashboard for the Willow system. Textual TUI — no web server, no ports.

Channels, agent presence, routing decisions, task queue, knowledge base, and model switching — one surface, all local.

---

## Prerequisites

- Python 3.11+
- PostgreSQL (tested on 14+)
- `bwrap` (bubblewrap) for the kart sandbox — optional, kart degrades gracefully without it

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Create the database

```bash
createdb willow_20
psql -d willow_20 -f schema.sql
```

`schema.sql` creates all schemas idempotently. Safe to re-run.

### 3. Configure environment

```bash
cp .env.example .env
# edit .env — at minimum set WILLOW_DB_URL or leave defaults if using peer auth
```

The only required environment is a reachable Postgres database. Everything else degrades gracefully.

Docs index: `docs/INDEX.md`

### 4. Run

```bash
python3 app.py
```

---

## Enterprise documentation

Grove history drives continuously refreshed artifacts (digests, ADR/incident **candidates**). Start at **[`docs/INDEX.md`](docs/INDEX.md)**. Regenerate locally:

```bash
make grove-docs
# or: ./scripts/grove_docs_refresh.sh
```

---

## Entry points

| Command | What |
|---------|------|
| `python3 app.py` | Main Textual dashboard |
| `python3 -m grove` | Lightweight curses TUI (SSH / narrow terminal) |
| `python3 -m grove_standalone` | Standalone DM app |
| `python3 grove_serve.py` | LAN command server (HMAC-signed) |

---

## Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `WILLOW_DB_URL` | _(unset)_ | Full Postgres DSN — overrides PG_DB/PG_USER |
| `WILLOW_PG_DB` | `willow_20` | Database name |
| `WILLOW_PG_USER` | `$USER` | Database user |
| `WILLOW_ROOT` | `~/github/willow-2.0` | Path to willow-2.0 repo (health scripts, skills) |
| `WILLOW_STORE_ROOT` | `~/.willow/store` | SOIL local key-value store |
| `GROVE_KNOWN_AGENTS` | _(auto-discovered)_ | Comma-separated agent names for ThoughtStream |

---

## Architecture

| File | Role |
|------|------|
| `app.py` | Textual app — WillowGrove |
| `grove_db.py` | DB layer — pool, schema bootstrap, all grove operations |
| `grove_reader.py` | Read helpers for dashboard widgets |
| `schema.sql` | DB bootstrap — run once |
| `kart_worker.py` | Task queue consumer (daemon thread) |
| `grove/` | Curses TUI subpackage |
| `grove_standalone.py` | Standalone Textual DM app |
| `u2u/` | Authenticated LAN transport — signed, **not** encrypted (see Notes) |
| `bridge/` | Matrix bridge |
| `grove_serve.py` | LAN HTTP command server |

---

## Notes

- **No web ports.** The dashboard reads from Postgres directly. Nothing listens on a network port unless you explicitly run `grove_serve.py`.
- **u2u is authenticated, not confidential.** This was previously described as
  "encrypted" and "end-to-end encrypted". It is not. `u2u/packets.py` writes
  `json.dumps(packet)` onto a plain TCP socket; the `cryptography` dependency is
  used only for Ed25519 **signing**. Every packet's origin and integrity are
  verified before it is acted on, but the body is plaintext on the wire — anyone
  who can observe the LAN segment can read a DM. Treat u2u as trusted-LAN-only.
  Adding a confidentiality layer is an open decision, not a shipped feature.
- **u2u consent is opt-in.** A newly admitted contact starts with every
  `consent_*` flag False and can deliver nothing until you grant a permission
  (`ContactStore.set_consent`). Contacts already in `grove_contacts.json` keep
  whatever flags are stored there.
- **ThoughtStream** shows messages from agents discovered via HEARTBEAT messages. Set `GROVE_KNOWN_AGENTS` to pin the list.
- `public.knowledge` and `public.tasks` in `schema.sql` are stubs for standalone setups. If you run willow-2.0, its migrations manage those tables instead.
