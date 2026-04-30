# Dashboard Phase 4c: Providers + Health ContextPanel Nav — Design Spec
b17: WGRV1  ΔΣ=42

## Goal

When the user navigates to **Providers**, the left `ContextPanel` shows a live focusable provider list; selecting a row moves the DataTable cursor in the main `ProvidersPane`. When the user navigates to **Health**, the left panel shows live subsystem status indicators (pg, ollama, kart, SOIL) that auto-refresh every 15s.

## Architecture

### New file: `widgets/providers_nav.py`

**`ProviderRowSelected(Message)`**
- `name: str` — provider name selected

**`ProvidersNavRow(Widget)`**
- `can_focus = True`
- `BINDINGS = [("enter", "activate", "Select")]`
- Constructor: `name: str, enabled: bool, ptype: str`
- Renders: `[green]●[/]` or `[red]●[/]` dot + name + ON/OFF + local/cloud
- `update_row(enabled: bool, ptype: str)` — refreshes display
- `action_activate()` → posts `ProviderRowSelected(self._name)`
- `on_click()` → `action_activate()`

**`ProvidersNav(Widget)`**
- Composes rows dynamically from `_read_providers()` on each refresh
- `on_mount`: calls `_fetch()` + sets 15s interval
- `@work(thread=True) _fetch()` — calls `_read_providers()`, posts `_ProvidersRefreshed`
- `on__providers_refreshed()` — rebuilds rows if provider list changed, else calls `update_row` on each

### New file: `widgets/health_nav.py`

**`HealthNav(Widget)`**
- No selection — pure status display
- Composes: `Static(id="hn-status", markup=True)`
- `on_mount`: calls `_fetch()` + sets 15s interval
- `@work(thread=True) _fetch()` — calls `_fetch_health_status()`, posts `_HealthStatusFetched`
- `on__health_status_fetched()` — updates `#hn-status`

**`_fetch_health_status() -> dict`** — pure function, never raises. Returns:
```python
{
    "pg":     {"ok": bool, "label": str},   # e.g. "up" / "down"
    "ollama": {"ok": bool, "label": str},   # "up" / "down"
    "kart":   {"ok": bool, "label": str},   # "3 pending" / "idle"
    "soil":   {"ok": bool, "label": str},   # "ok" / "missing"
}
```

Sources:
- **pg**: `psycopg2.connect(dbname="willow_19", connect_timeout=2)` — ok if no exception
- **ollama**: `urllib.request.urlopen("http://localhost:11434", timeout=2)` — ok if no exception
- **kart**: `SELECT COUNT(*) FROM public.tasks WHERE status IN ('pending','running')` via psycopg2 — ok if count >= 0
- **SOIL**: `Path.home() / ".willow" / "store"` — ok if dir exists

### Modify `panes/providers.py`

**Add**: `ProvidersPane.select_provider(name: str) -> None` — finds the DataTable row whose first cell matches `name`, moves `cursor_row` there using `DataTable.move_cursor(row=idx)`.

### Modify `app.py` — `ContextPanel` and `WillowGrove`

`ContextPanel`:
- Import `ProvidersNav`, `HealthNav`
- `compose()` adds `ProvidersNav(id="ctx-providers")` and `HealthNav(id="ctx-health")`
- `ctx_map` adds `"providers": "#ctx-providers"` and `"health": "#ctx-health"`

`WillowGrove`:
- Import `ProviderRowSelected` from `widgets.providers_nav`
- Add `on_provider_row_selected(event)` → calls `self.query_one(ProvidersPane).select_provider(event.name)`

## Data Flow

```
ProvidersNav._fetch() [thread]
  → _read_providers() [already exists in panes/providers.py — local import]
  → post _ProvidersRefreshed(providers)
  → rebuild/update rows

ProvidersNavRow.action_activate()
  → post ProviderRowSelected(name)

WillowGrove.on_provider_row_selected
  → ProvidersPane.select_provider(name)
  → DataTable.move_cursor(row=idx)

HealthNav._fetch() [thread]
  → _fetch_health_status()
  → post _HealthStatusFetched(status)
  → render status lines into #hn-status
```

## CSS

`ProvidersNavRow`:
- `height: 1; width: 1fr; padding: 0 1`
- `:focus { background: #21262d }`

`ProvidersNav`:
- `width: 1fr; height: 1fr; padding: 1 0`
- Header label `"PROVIDERS"` in `#58a6ff` bold

`HealthNav`:
- `width: 1fr; height: 1fr; padding: 1 1`
- `#hn-status`: `height: 1fr`

## Testing

`tests/test_widgets_providers_nav.py`:
- `ProviderRowSelected` stores `name`
- `ProvidersNavRow` stores `_name`, `_enabled`, `_ptype`
- `update_row()` mutates `_enabled` and `_ptype`

`tests/test_widgets_health_nav.py`:
- `_fetch_health_status()` returns dict with keys `pg`, `ollama`, `kart`, `soil`
- Each value has `ok` (bool) and `label` (str)
- Never raises even when all sources fail
- SOIL returns `ok=False` when directory missing
- kart returns `ok=True` and numeric label when DB succeeds (mock)

## Out of Scope

- Enable/disable from the nav panel (those bindings stay in main ProvidersPane)
- Health subsystem drill-down
- Ollama model list in nav
