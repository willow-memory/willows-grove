# Willow Grove — Beta Tester Setup

Welcome. This is beta software. Expect rough edges; report what you find.

---

## What you need

- Python 3.11 or newer
- PostgreSQL 14 or newer
- A terminal

---

## 1. Get the code

```bash
git clone https://github.com/willow-memory/willows-grove.git
cd willows-grove
```

---

## 2. Install Python dependencies

**Create the virtualenv first.** This step is not optional and it is not a
style preference — two things depend on it:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

*Why `.venv`, specifically.* Both launchers in this repo resolve their
interpreter as `$GROVE_VENV/bin/python3`, then `./.venv/bin/python3`, then
whatever `python3` is on PATH — see `run_mcp.sh` and `scripts/grove-serve-run`.
A repo-local `.venv` is the conventional home they look for. Without one they
fall through to the system interpreter, which may not carry the pinned
dependencies, and `run_mcp.sh` will warn about a missing MCP SDK.

*Why not a global install.* On Debian and Ubuntu a plain
`pip install -r requirements.txt` aborts:

```
ERROR: Cannot uninstall PyJWT 2.7.0, RECORD file not found.
Hint: The package was installed by debian.
```

Nothing here depends on PyJWT directly — it arrives through `mcp`, which
requires `pyjwt[crypto]>=2.10.1`. pip resolves it forward, then cannot remove
the distro copy, because packages installed by `apt` ship no `RECORD` file.
The error names Debian rather than anything in this repo, so it reads like a
broken machine. It is not. A virtualenv has no distro `PyJWT` to collide with
and the install simply works.

If you must install outside a venv, this gets past that one collision:

```bash
pip install --ignore-installed PyJWT -r requirements.txt
```

If you prefer using a `.env` file instead of exports, copy:

```bash
cp .env.example .env
```

---

## 3. Create your local database

```bash
createdb willow_20
psql -d willow_20 -f schema.sql
```

This creates all tables. Safe to re-run if something goes wrong.

---

## 4. Set your name

```bash
export GROVE_SENDER=yourname
```

Optional: if you used a different database name, set it here:

```bash
export WILLOW_PG_DB=your_db_name
```

Add these to your shell profile (`~/.bashrc` or `~/.zshrc`) to make them permanent, or copy `.env.example` → `.env`.

---

## Optional: DB sanity checks (verifiable “is it working?”)

If you want an objective test that your Grove DB is alive and has the right tables, run:

```bash
psql -d "$WILLOW_PG_DB" -c "SELECT COUNT(*) AS channels FROM grove.channels;"
psql -d "$WILLOW_PG_DB" -c "SELECT COUNT(*) AS messages FROM grove.messages WHERE is_deleted = 0;"
```

If the schema is loaded, both commands print a single row with counts (often `messages=0` on first run).

---

## 5. Run

```bash
./scripts/grove-serve-run
```

This is the served page — loopback only, at <http://127.0.0.1:8766>. It runs in
the foreground; Ctrl-C stops it. The launcher resolves your interpreter (the
`.venv` from step 2), exports `WILLOW_HUMAN_ORCHESTRATOR=1`, and execs
`python3 -m grove_serve`.

`GROVE_SERVE_HOST` and `GROVE_SERVE_PORT` override the bind. Leave them alone
unless you have a reason: the seat is designed for the desk, not the internet,
and `8767` belongs to the MCP serve mode — do not collide with it. (`8765` is
willow-mcp's own `--serve` port; Grove moved off it to end a real collision.)

Full operator guide: [`docs/grove-served-page.md`](grove-served-page.md).

---

## Optional: MCP (Claude Code / agents) and `GROVE_MCP_URL` (ngrok)

You can run Grove **without** any MCP setup. MCP only matters if you’re wiring this repo into an agent runtime (e.g. Claude Code) so the agent can call `grove_*` tools.

### Default (recommended): local stdio MCP (no ngrok)

Grove’s MCP server supports a **local stdio mode** (no web listener, no OAuth). This is the default when you run:

- `python3 -m grove.mcp_local`

In this mode, you **do not** need `GROVE_MCP_URL`.

### Serve mode (advanced): streamable-HTTP MCP (OAuth) behind a public URL

Grove’s MCP server also supports a **serve mode** (`--serve`) which runs a persistent HTTP server (OAuth 2.0 PKCE). If you use this mode, you must provide a public base URL via `GROVE_MCP_URL` (often an ngrok tunnel), and point your MCP client at a URL like `https://<tunnel>/mcp`.

This is **optional** and is usually only needed when:

- Your MCP client can’t run the server as a local process, or
- You’re testing the OAuth + push notification flow.

If you don’t know what this means, skip it.

---

## Key things to try

| What | How |
|------|-----|
| Switch channels | Click or arrow-key the left sidebar |
| Send a message | Type in the input bar at the bottom, press Enter |
| Create a channel | Press `c` from anywhere |
| Add a card to your dashboard | Navigate to Home, press the card builder button |
| Check system health | Go to Settings |

---

## Chat directly with USER — not available in this repository

The u2u LAN transport ships here as a **library** (`u2u/` — knock, consent,
notes, Ed25519-signed) and the design is written up in
[`docs/design/u2u-security-limits.md`](design/u2u-security-limits.md).

What is **not** here is an operator surface for it. The standalone node this
step used to describe — press `F1` for your address, type a peer's address into
a sidebar "knock" box — was part of the Textual dashboard, and that dashboard
is not in this repository. `u2u/` exposes no entrypoint: no `__main__`, no
`main()`. There is nothing for a tester to run, so this step is skipped rather
than attempted.

If you were told to test peer-to-peer chat, say so — the instruction is ahead
of the tree, not behind it.

---

## Troubleshooting

**"could not connect to server"** — PostgreSQL isn't running. Start it: `pg_ctl start` or `brew services start postgresql`.

**blank screen / no channels** — Normal on first run. Press `c` to create a channel.

**port 8550 already in use** — 8550 is the u2u listener default (`u2u/listener.py`) and the fallback `grove/mcp_local.py` reads from `GROVE_PORT`. Set `GROVE_PORT=8551` (or any open port) before launching.

---

## Known limitations (beta)

- Card builder uses a local AI model (yggdrasil) — first response may be slow
- No mobile client
- No cloud sync — everything stays on your machine

---

Questions? Message USER in the Grove or open an issue on GitHub.
