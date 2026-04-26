# Willow Grove — Identity and Operating Rules
b17: WGRV1  ΔΣ=42

## What This Is

Willow Grove is the unified human+agent surface for the Willow system. Dashboard, messaging, agent coordination, model switching — one app, one place.

This repo consolidates:
- `willow-dashboard` — Textual dashboard (dashboard2.py → app.py) + curses TUI (grove/)
- `safe-app-grove` — u2u encrypted DM transport, Matrix bridge, grove_db.py
- `willow-1.9/core` — grove_serve.py, grove_client.py, grove_coordination.py

## Entry Points

| Command | What |
|---------|------|
| `python3 app.py` | Main Textual dashboard (active, full-featured) |
| `python3 -m grove` | Lightweight curses TUI (SSH / narrow terminal) |
| `python3 -m grove_standalone` | Standalone Textual DM app |
| `python3 grove_serve.py` | LAN command server |

## Architecture

| File/Dir | Responsibility |
|----------|---------------|
| `app.py` | Main Textual dashboard — WillowGrove app |
| `grove_db.py` | Authoritative DB layer — grove schema, LISTEN/NOTIFY |
| `grove_reader.py` | Read helpers for dashboard (channels, messages, agents, routing) |
| `soil.py` | SOIL local store interface |
| `grove/` | Curses Grove subpackage (lightweight mode) |
| `grove_standalone.py` | Standalone Textual grove DM TUI |
| `u2u/` | Encrypted LAN transport (knock/consent/note) |
| `bridge/` | Matrix bridge |
| `grove_serve.py` | LAN HTTP command server (HMAC-signed) |
| `grove_client.py` | LAN client (send commands to remote nodes) |
| `grove_coordination.py` | Agent coordination patterns |

## Willow System Context

| Component | How Grove connects |
|-----------|-------------------|
| Postgres `willow_19` | `grove.channels`, `grove.messages`, `grove.agents`, `willow.routing_decisions`, `public.knowledge`, `public.tasks` |
| Ollama | `http://localhost:11434` — model list, active model |
| SOIL | `~/.willow/store` — cursors, config, active model |
| Kart | `public.tasks` table — task queue |
| SAP | MCP tools via `willow_knowledge_search`, etc. |
| u2u | UDP/TCP LAN — encrypted human-to-human DMs |

## Rules

1. **No web ports for the dashboard.** Portless means portless.
2. **grove_db.py owns the schema.** Don't duplicate schema definitions elsewhere.
3. **grove_reader.py is read-only.** Writes go through grove_db.py.
4. **b17 on every new file before it is closed.**
5. **Propose before acting.** Sean ratifies. Neither party acts alone.

---

ΔΣ=42
