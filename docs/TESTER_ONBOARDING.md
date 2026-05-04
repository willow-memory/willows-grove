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

---

## 3. Create your local database

```bash
createdb grove_local
psql -d grove_local -f schema.sql
```

This creates all tables. Safe to re-run if something goes wrong.

---

## 4. Set your name

```bash
export WILLOW_PG_DB=grove_local
export GROVE_SENDER=yourname
```

Add these to your shell profile (`~/.bashrc` or `~/.zshrc`) to make them permanent.

---

## 5. Run

```bash
python3 app.py
```

The dashboard opens in your terminal. Use arrow keys to navigate, Enter to select.

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

## Chat directly with Sean

Sean runs a separate peer-to-peer node. To connect:

**You:**
```bash
python3 grove_standalone.py
```

Press `F1` to see your address (looks like `yourname@192.168.x.x:8550`). Share it with Sean so he can knock you back.

**Connect to Sean:**
In the sidebar, enter Sean's address in the "knock" input and press Enter. Sean will approve the connection. Once approved, select him from your contacts list and start typing.

> Sean's address will be shared before the session. If it changes, press F1 on his end to get the updated one.

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

Questions? Message Sean in the Grove or open an issue on GitHub.
