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
createdb willow_19
psql -d willow_19 -f schema.sql
```

`schema.sql` creates all schemas idempotently. Safe to re-run.

### 3. Configure environment

```bash
cp .env.example .env
# edit .env — at minimum set WILLOW_DB_URL or leave defaults if using peer auth
```

The only required environment is a reachable Postgres database. Everything else degrades gracefully.

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
| `WILLOW_PG_DB` | `willow_19` | Database name |
| `WILLOW_PG_USER` | `$USER` | Database user |
| `WILLOW_ROOT` | `~/github/willow-1.9` | Path to willow-1.9 repo (health scripts, skills) |
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
| `u2u/` | Encrypted LAN transport |
| `bridge/` | Matrix bridge |
| `grove_serve.py` | LAN HTTP command server |

---

## Notes

- **No web ports.** The dashboard reads from Postgres directly. Nothing listens on a network port unless you explicitly run `grove_serve.py`.
- **ThoughtStream** shows messages from agents discovered via HEARTBEAT messages. Set `GROVE_KNOWN_AGENTS` to pin the list.
- `public.knowledge` and `public.tasks` in `schema.sql` are stubs for standalone setups. If you run willow-1.9, its migrations manage those tables instead.
