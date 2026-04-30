# Dashboard Phase 4b: Knowledge ContextPanel Nav + Atom Viewer — Design Spec
b17: WGRV1  ΔΣ=42

## Goal

When the user navigates to **Knowledge**, the left `ContextPanel` shows a search input and results list. Pressing Enter on a result opens the full atom in the main `KnowledgePane` area.

## Architecture

### New file: `widgets/knowledge_nav.py`

**`KnowledgeAtomSelected(Message)`**
- `atom_id: int` — the knowledge atom to display

**`KnowledgeNav(Widget)`**
- Composes: `Input(placeholder="Search…", id="kn-search")` at top + `Static(id="kn-results", markup=True)` below
- On Input.Submitted: runs `search_kb(query)` in background thread via `@work(thread=True)`; posts `_KnowledgeSearchDone(rows)`
- `on__knowledge_search_done`: renders results into `#kn-results` as a numbered list; stores results in `self._rows`
- Up/Down arrow keys move `self._cursor` through results; renders highlight
- Enter on a highlighted result posts `KnowledgeAtomSelected(atom_id)`

Result row format (fits 26-char panel):
```
  1. [#58a6ff]42[/] truncated-title (16 chars max)
```
Highlighted row uses `[reverse]` markup.

Up to 20 results shown. Empty query clears results.

### Modify `panes/knowledge.py`

**Remove**: the `Input`, `Label`, and `DataTable` from `KnowledgePane.compose()` and the `_run_search` handler.

**Add**: `Static("", id="kb-atom", markup=True)` — renders the selected atom.

**Add**: `fetch_atom(atom_id: int) -> dict | None` — pure function, queries:
```sql
SELECT id, title, summary, domain, weight, content
FROM public.knowledge WHERE id = %s
```
Falls back to selecting without `content` column if it does not exist.

**Add**: `render_atom(atom: dict) -> str` — pure function, returns rich markup string with sections: ID/domain header, title, summary, content (if present).

**Add**: `KnowledgePane.display_atom(atom_id: int) -> None` — public method called by `app.py`; fetches atom in background thread via `@work(thread=True)`, posts `_AtomFetched`, updates `#kb-atom`.

Keep: `search_kb()`, `_pg_conn()`, `truncate_text()` unchanged.

### Modify `app.py` — `ContextPanel` and `WillowGrove`

`ContextPanel`:
- Import `KnowledgeNav`
- `compose()` adds `KnowledgeNav(id="ctx-knowledge")`
- `ctx_map` adds `"knowledge": "#ctx-knowledge"`

`WillowGrove`:
- Import `KnowledgeAtomSelected` from `widgets.knowledge_nav`
- Add `on_knowledge_atom_selected(event)` — calls `self.query_one(KnowledgePane).display_atom(event.atom_id)`

`KnowledgeAtomSelected` bubbles up the DOM from `KnowledgeNav` → `ContextPanel` → `WillowGrove`. `WillowGrove` is the common ancestor of all widgets (same pattern as `on_card_activated`).

## Data Flow

```
KnowledgeNav Input.Submitted
  → @work search_kb(query) [thread]
  → post _KnowledgeSearchDone(rows)
  → render results list + store in self._rows

KnowledgeNav Up/Down key
  → move self._cursor
  → re-render results with highlight

KnowledgeNav Enter key (on result row)
  → post KnowledgeAtomSelected(atom_id)

WillowGrove.on_knowledge_atom_selected
  → self.query_one(KnowledgePane).display_atom(atom_id)

KnowledgePane.display_atom(atom_id)
  → @work fetch_atom(atom_id) [thread]
  → post _AtomFetched(atom)
  → render_atom(atom) → update #kb-atom
```

## CSS

`KnowledgeNav`:
- `width: 1fr; height: 1fr; padding: 0`
- `#kn-search`: full width, 1-line input
- `#kn-results`: `height: 1fr; overflow-y: auto; padding: 0 1`

`KnowledgePane`:
- `#kb-atom`: `height: 1fr; padding: 1 2; overflow-y: auto`

## Testing

`tests/test_widgets_knowledge_nav.py`:
- `KnowledgeAtomSelected` stores `atom_id`
- `KnowledgeNav` constructs without error

`tests/test_panes_knowledge.py`:
- `fetch_atom` returns `None` on DB failure
- `fetch_atom` returns dict with `id`, `title`, `summary`, `domain`, `weight` when DB succeeds (mock)
- `render_atom` returns string containing title
- `render_atom` handles missing `content` key gracefully
- `render_atom` is a string
- `search_kb` (existing) — keep existing tests

## Out of Scope

- Fuzzy/semantic search (ILIKE is sufficient)
- Editing atoms from the viewer
- Pagination beyond 20 results
- Keyboard shortcut to jump to search input
