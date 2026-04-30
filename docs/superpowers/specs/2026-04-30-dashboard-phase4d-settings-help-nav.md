# Dashboard Phase 4d: Settings + Help ContextPanel Nav — Design Spec
b17: WGRV1  ΔΣ=42

## Goal

When the user navigates to **Settings**, the left `ContextPanel` shows live consent status dots (internet, cloud LLM, LAN); the main pane shows interactive toggle rows that write to `~/.willow/consent.json`. When the user navigates to **Help**, the left panel shows a focusable section list; selecting a section scrolls the main pane to that section.

## Architecture

### Consent store: `~/.willow/consent.json`

System-wide. Three boolean keys — defaults to `true` if key is absent or file is missing:

```json
{
  "internet": true,
  "cloud_llm": false,
  "lan": true
}
```

Written atomically (write to `.tmp`, then rename). Read by both `SettingsNav` (polling) and `SettingsPane` (on mount + after each toggle).

### New file: `widgets/settings_nav.py`

**`SettingsNav(Widget)`**
- No selection — pure status display, same pattern as `HealthNav`
- Composes: `Static(id="sn-header")` + `Static(id="sn-status", markup=True)`
- `on_mount`: calls `_fetch()` + sets 15s interval
- `@work(thread=True) _fetch()` — reads `consent.json`, posts `_ConsentStatusFetched`
- `on__consent_status_fetched()` — updates `#sn-status` with three dot lines

Rendered status lines (one per toggle):
```
[green]●[/] [dim]internet[/]  on
[red]●[/] [dim]cloud llm[/]  off
[green]●[/] [dim]lan[/]  on
```

CSS:
- `width: 1fr; height: 1fr; padding: 1 1`
- `#sn-header`: `color: #58a6ff; text-style: bold`
- `#sn-status`: `height: 1fr`

### New file: `panes/settings.py`

**`_read_consent() -> dict`** — pure function, never raises. Reads `~/.willow/consent.json`. Returns `{"internet": True, "cloud_llm": True, "lan": True}` as defaults if file is absent or malformed.

**`_write_consent(data: dict) -> None`** — atomic write: dumps to `consent.json.tmp`, renames to `consent.json`. Never raises.

**`ConsentToggleRow(Widget)`**
- `can_focus = True`
- `BINDINGS = [("enter", "toggle", "Toggle")]`
- Constructor: `key: str, label: str, description: str, enabled: bool`
- Renders: dot + label + ON/OFF + `[dim]description[/]`
- `action_toggle()` → flips `_enabled`, re-renders, posts `_ConsentChanged(key, enabled)`
- CSS: `height: 3; width: 1fr; padding: 0 1; border-bottom: solid #30363d`
- `:focus { background: #21262d }`

**`_ConsentChanged(Message)`** — `key: str`, `enabled: bool`

**`SettingsPane(Container)`**
- `on_mount`: reads consent, mounts three `ConsentToggleRow` widgets:
  - `key="internet"`, label="Internet", description="Allow outbound internet connections"
  - `key="cloud_llm"`, label="Cloud LLM", description="Send prompts to cloud AI providers (e.g. Anthropic)"
  - `key="lan"`, label="LAN", description="Allow local network communication between devices"
- `on__consent_changed(event)`: reads current consent, flips `event.key`, writes back

CSS:
- `SettingsPane`: `height: 1fr; padding: 1 2`
- Header label `"CONSENT"` in `#58a6ff` bold above the rows

### New file: `widgets/help_nav.py`

**`HelpSectionSelected(Message)`**
- `section: str` — one of `"overview"`, `"navigation"`, `"shortcuts"`, `"privacy"`

**`HelpNavRow(Widget)`**
- `can_focus = True`
- `BINDINGS = [("enter", "activate", "Go")]`
- Constructor: `section: str, label: str`
- Renders label, posts `HelpSectionSelected(section)` on activate/click
- CSS: `height: 1; width: 1fr; padding: 0 1`
- `:focus { background: #21262d }`

**`HelpNav(Widget)`**
- Composes: header `Static("HELP")` + four `HelpNavRow` instances:
  - `("overview", "Overview")`
  - `("navigation", "Navigation")`
  - `("shortcuts", "Shortcuts")`
  - `("privacy", "Privacy & Consent")`
- CSS: `width: 1fr; height: 1fr; padding: 1 0`
- Header: `color: #58a6ff; text-style: bold; padding: 0 1`

### New file: `panes/help.py`

**`HelpPane(VerticalScroll)`**
- Composes four `Static` widgets with `id="help-{section}"` and `markup=True`:
  - `#help-overview` — system overview
  - `#help-navigation` — what each nav tab does
  - `#help-shortcuts` — all keyboard shortcuts
  - `#help-privacy` — consent model and data streams
- `jump_to_section(section: str)` — calls `self.query_one(f"#help-{section}").scroll_visible()`

**Content:**

`#help-overview`:
```
[bold #58a6ff]Willow Grove[/]

Local-first AI workspace. One surface for messaging, task coordination,
knowledge, and agent management. Everything runs on your machine.
Postgres holds the memory. Ollama runs the models. You hold the keys.
```

`#help-navigation`:
```
[bold #58a6ff]Navigation[/]

[bold]Home[/]       Dashboard — tasks, agents, active thoughts
[bold]Chat[/]       Grove channels — agent and human messaging
[bold]Projects[/]   Active projects and task queues
[bold]Knowledge[/]  Search and browse the knowledge base
[bold]Providers[/]  AI model providers — enable/disable
[bold]Health[/]     Subsystem status — pg, ollama, kart, SOIL
[bold]Settings[/]   Consent and security controls
[bold]Help[/]       This panel
```

`#help-shortcuts`:
```
[bold #58a6ff]Keyboard Shortcuts[/]

[bold]q[/]       Quit
[bold]r[/]       Refresh
[bold]1–8[/]     Navigate to Home / Chat / Projects / Knowledge /
            Providers / Health / Settings / Help
[bold]e[/]       Enable selected provider (Providers pane)
[bold]d[/]       Disable selected provider (Providers pane)
[bold]Enter[/]   Confirm selection / toggle (nav rows, settings)
[bold]↑ ↓[/]     Move cursor (Knowledge search results)
```

`#help-privacy`:
```
[bold #58a6ff]Privacy & Consent[/]

Willow runs locally. No data leaves your machine unless you explicitly
enable cloud features.

[bold]Internet[/]    Outbound internet connections. Off = fully air-gapped.
[bold]Cloud LLM[/]   Prompts sent to cloud AI providers (e.g. Anthropic).
                Off = local models only.
[bold]LAN[/]         Local network communication between your devices.
                Off = no outbound LAN traffic.

Consent state is stored at [dim]~/.willow/consent.json[/] and applies
system-wide to all apps installed through Willow Grove.

Authorization is enforced by the SAP gate — apps must present a
PGP-signed manifest to access any Willow tool.
```

### Modify `app.py` — `ContextPanel` and `WillowGrove`

`ContextPanel`:
- Import `SettingsNav` from `widgets.settings_nav`, `HelpNav` from `widgets.help_nav`
- `compose()` adds `SettingsNav(id="ctx-settings")` and `HelpNav(id="ctx-help")`
- `ctx_map` adds `"settings": "#ctx-settings"` and `"help": "#ctx-help"`

`WillowGrove`:
- Import `HelpSectionSelected` from `widgets.help_nav`
- Import `SettingsPane` from `panes.settings`, `HelpPane` from `panes.help`
- Replace `Static("[ Settings — coming soon ]", id="pane-settings")` with `SettingsPane(id="pane-settings")`
- Replace `Static("[ Help — coming soon ]", id="pane-help")` with `HelpPane(id="pane-help")`
- Add `on_help_section_selected(event)` → `self.query_one(HelpPane).jump_to_section(event.section)`

## Data Flow

```
SettingsNav._fetch() [thread]
  → _read_consent()
  → post _ConsentStatusFetched
  → update #sn-status dots

ConsentToggleRow.action_toggle()
  → flip _enabled, re-render
  → post _ConsentChanged(key, enabled)

SettingsPane.on__consent_changed()
  → _read_consent() → flip key → _write_consent()

HelpNavRow.action_activate()
  → post HelpSectionSelected(section)

WillowGrove.on_help_section_selected()
  → HelpPane.jump_to_section(section)
  → query_one(f"#help-{section}").scroll_visible()
```

## Testing

`tests/test_panes_settings.py`:
- `_read_consent()` returns defaults when file missing
- `_read_consent()` returns correct values when file present
- `_write_consent()` writes and re-reads correctly
- `_write_consent()` never raises on bad path
- `ConsentToggleRow` stores `_key`, `_label`, `_enabled`
- Toggle flips `_enabled`

Note: `SettingsNav._fetch()` imports `_read_consent` from `panes.settings` as a local import inside the `@work` method — same pattern as `ProvidersNav` importing `_read_providers` from `panes.providers`.

`tests/test_widgets_help_nav.py`:
- `HelpSectionSelected` stores `section`
- `HelpNavRow` stores `_section`

## Out of Scope

- Per-app consent overrides (system-wide only)
- Consent enforcement at runtime (that's the SAP gate's job)
- Editing the PGP-signed manifest from the UI
- Internet access enforcement via firewall rules
