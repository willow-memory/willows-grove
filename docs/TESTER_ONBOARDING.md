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
git clone https://github.com/rudi193-cmd/safe-app-willow-grove.git
cd safe-app-willow-grove
```

---

## 2. Install Python dependencies

```bash
pip install -r requirements.txt
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
psql -d “$WILLOW_PG_DB” -c “SELECT COUNT(*) AS channels FROM grove.channels;”
psql -d “$WILLOW_PG_DB” -c “SELECT COUNT(*) AS messages FROM grove.messages WHERE is_deleted = 0;”
```

If the schema is loaded, both commands print a single row with counts (often `messages=0` on first run).

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
python3 app.py
```

The dashboard opens in your terminal. Use arrow keys to navigate, Enter to select.

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

## Chat directly with USER

USER runs a separate peer-to-peer node. To connect:

**You:**
```bash
python3 grove_standalone.py
```

Press `F1` to see your address (looks like `yourname@192.168.x.x:8550`). Share it with USER so he can knock you back.

**Connect to USER:**
In the sidebar, enter USER's address in the "knock" input and press Enter. USER will approve the connection. Once approved, select him from your contacts list and start typing.

> USER's address will be shared before the session. If it changes, press F1 on his end to get the updated one.

---

## Troubleshooting

**"could not connect to server"** — PostgreSQL isn't running. Start it: `pg_ctl start` or `brew services start postgresql`.

**blank screen / no channels** — Normal on first run. Press `c` to create a channel.

**port 8550 already in use** — Set `GROVE_PORT=8551` (or any open port) before running `grove_standalone.py`.

---

## Known limitations (beta)

- Card builder uses a local AI model (yggdrasil) — first response may be slow
- No mobile client
- No cloud sync — everything stays on your machine

---

Questions? Message USER in the Grove or open an issue on GitHub.
