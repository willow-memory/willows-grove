# Willow Grove Dashboard — Fresh Start

**Branch:** `dashboard/fresh-start`  
**Worktree:** `worktrees/dashboard-fresh`  
**Parent repo:** `willows-grove` (connected to the prior dashboard work)

## What survived

| Piece | Location |
|-------|----------|
| **Hero** | `widgets/hero.py`, `widgets/hero_scene.py`, `widgets/_hero_state.py`, `widgets/hero_db.py` |
| **Collapse** | `HeroScene.set_expanded()` — full hero on Home (`1`), one-line strip elsewhere (`2`) |
| **Harness** | `hero_test.py` — standalone hero + easter-egg keys |

## What was removed

April 30 shell pieces (nav rails, desk, card grid, chat strip, panes, fleet boot, kart daemon, curses Grove OS, etc.) are **gone from this worktree**. Grove connection stubs (`grove_db.py`, `grove_reader.py`, `schema.sql`) remain for when you wire data back in.

## Run

```bash
cd worktrees/dashboard-fresh
./dev.sh                # or ./run_dev.sh — fleet venv + willow_20
python3 -m pip install -r requirements.txt   # if no venv yet
python3 app.py          # minimal shell: hero + collapse + placeholder content
python3 hero_test.py    # hero-only harness (q/p/b/g/1/h)
python3 -m grove.mcp_local          # Grove MCP stdio
./run_mcp.sh --serve                # HTTP MCP on :8765
pytest tests/test_widgets_hero*.py tests/test_theme_textual.py tests/test_vitals.py tests/test_mcp_registry.py tests/test_mcp_registry.py
```

**`dev.sh` env:** `WILLOW_PG_DB` (default `willow_20`), `GROVE_VENV` to override Python.

## Build forward

**Read [`ANTI_SLOP.md`](ANTI_SLOP.md) first** — design gate for every UI change.

1. Pick the next region (content band, nav, vitals) from [`docs/superpowers/specs/2026-05-20-dashboard-feel-pass.md`](docs/superpowers/specs/2026-05-20-dashboard-feel-pass.md) or write a new spec.
2. Wire Grove/Postgres via `grove_reader` when a pane needs live data.
3. Merge to `master` only when Sean ratifies.

*ΔΣ=42*
