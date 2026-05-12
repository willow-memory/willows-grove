"""panes/search.py — Live KB search pane with debounced input.
b17: WGRV2  ΔΣ=42

Steal track: samballington/CodeWise (hybrid search), S1LV4/th0th (embedder compare)

Displays a Textual search pane that:
  - Shows a single-line input box at the top
  - Debounces keystrokes (300 ms) before issuing a query
  - Runs hybrid_search() via the fallback chain in willow/sigmap/fallback.py
  - Falls back to plain ILIKE on grove_db if the willow package is unavailable
  - Renders results as a scrollable list of score + title + domain rows
  - On Enter / click, shows full atom detail in a right-side panel

Card pattern mirrors panes/knowledge.py and panes/chat.py.

Layout:
    ┌─────────────────────────────────────┐
    │  [Search KB...                    ] │  ← Input (id="search-input")
    ├─────────────┬───────────────────────┤
    │ Results     │ Atom detail           │
    │ #id  score  │ # 12345  hanuman      │
    │ title text  │                       │
    │ …           │ Title                 │
    │             │ Summary text…         │
    └─────────────┴───────────────────────┘
"""
from __future__ import annotations

import logging
from typing import Optional

from rich.markup import escape
from textual import on, work
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, ScrollableContainer
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Input, Label, Static

import grove_db

logger = logging.getLogger(__name__)

# ── Search backend ────────────────────────────────────────────────────────────

_DEBOUNCE_S: float = 0.3    # 300 ms debounce before firing query
_MAX_RESULTS: int = 30       # cap displayed results
_SCORE_THRESHOLD: float = 0.0  # show all results (filter by level, not score)


def _search_kb(query: str, limit: int = _MAX_RESULTS) -> list[dict]:
    """
    Run the multi-level fallback search chain.

    Attempts willow/sigmap/fallback.py first (pgvector ANN → hybrid RRF →
    AST symbol → ILIKE).  Falls back to plain ILIKE via grove_db if the
    willow package is not importable (e.g., running the dashboard standalone).

    Returns a list of dicts with keys:
        id, title, summary, domain, weight, score, level_name
    """
    if not query.strip():
        return []

    # Try willow fallback chain
    try:
        from core.pg_bridge import PgBridge  # type: ignore
        from willow.sigmap.fallback import fallback_search  # type: ignore

        pg = PgBridge()
        results = fallback_search(query, pg, limit=limit)
        return [
            {
                "id": r.id,
                "title": r.title,
                "summary": r.summary,
                "domain": r.project,
                "weight": r.weight,
                "score": r.score,
                "level_name": r.level_name,
            }
            for r in results
        ]
    except Exception as exc:
        logger.debug("fallback_search unavailable (%s), using ILIKE", exc)

    # Plain ILIKE fallback (always available in dashboard context)
    conn = None
    try:
        conn = grove_db.get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, title, summary, project AS domain, weight
            FROM public.knowledge
            WHERE (title ILIKE %s OR summary ILIKE %s)
              AND invalid_at IS NULL
            ORDER BY weight DESC NULLS LAST, id DESC
            LIMIT %s
            """,
            (f"%{query}%", f"%{query}%", limit),
        )
        rows = cur.fetchall()
        return [
            {
                "id": r[0],
                "title": r[1] or "",
                "summary": r[2] or "",
                "domain": r[3] or "",
                "weight": r[4] or 0,
                "score": 0.0,
                "level_name": "ilike",
            }
            for r in rows
        ]
    except Exception as exc:
        logger.warning("search_kb ILIKE failed: %s", exc)
        return []
    finally:
        if conn is not None:
            grove_db.release_connection(conn)


def _fetch_atom(atom_id: str) -> dict | None:
    """Fetch a single knowledge atom by id for the detail panel."""
    conn = None
    try:
        conn = grove_db.get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, title, summary, project, weight, content "
            "FROM public.knowledge WHERE id = %s",
            (atom_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {
            "id": row[0], "title": row[1] or "",
            "summary": row[2] or "", "domain": row[3] or "",
            "weight": row[4] or 0, "content": row[5] or "",
        }
    except Exception:
        return None
    finally:
        if conn is not None:
            grove_db.release_connection(conn)


# ── Rendering helpers ─────────────────────────────────────────────────────────

def _truncate(text: str, n: int) -> str:
    if not text:
        return ""
    return text[:n] + ("…" if len(text) > n else "")


def _render_result_row(r: dict, selected: bool = False) -> str:
    _H  = "[bold #58a6ff]" if not selected else "[bold #ffffff on #1f6feb]"
    _D  = "[dim]"
    _E  = "[/]"
    _Y  = "[yellow]"

    score     = r.get("score") or 0.0
    level     = r.get("level_name", "")
    atom_id   = str(r.get("id", "?"))
    domain    = _truncate(str(r.get("domain") or ""), 10)
    title     = _truncate(str(r.get("title") or r.get("id") or "?"), 45)
    score_fmt = f"{score:.3f}" if score else f"{_D}{level}{_E}"

    return (
        f"{_H}#{atom_id:<8}{_E} "
        f"{score_fmt:>7}  "
        f"{_D}{domain:<10}{_E}  "
        f"{title}"
    )


def _render_atom_detail(atom: dict) -> str:
    _H = "[bold #58a6ff]"
    _D = "[dim]"
    _E = "[/]"
    lines: list[str] = []

    lines.append(
        f"{_H}#{atom.get('id', '?')}[/]  "
        f"{_D}{atom.get('domain', '')}  w={atom.get('weight', 0)}{_E}"
    )
    lines.append("")

    title = atom.get("title", "")
    if title:
        lines.append(f"[bold]{escape(title)}[/]")
        lines.append("")

    summary = atom.get("summary", "")
    if summary:
        lines.append(f"{_D}SUMMARY{_E}")
        lines.append(escape(summary))
        lines.append("")

    content = atom.get("content", "")
    if content:
        lines.append(f"{_D}CONTENT{_E}")
        if isinstance(content, dict):
            import json
            lines.append(escape(json.dumps(content, indent=2)[:2000]))
        else:
            lines.append(escape(str(content)[:2000]))

    return "\n".join(lines)


# ── Internal messages ─────────────────────────────────────────────────────────

class _ResultsReady(Message):
    def __init__(self, query: str, results: list[dict]) -> None:
        super().__init__()
        self.query = query
        self.results = results


class _AtomReady(Message):
    def __init__(self, atom: dict | None) -> None:
        super().__init__()
        self.atom = atom


# ── Result row widget ─────────────────────────────────────────────────────────

class _ResultRow(Label):
    """Single clickable result row."""

    DEFAULT_CSS = """
    _ResultRow {
        width: 1fr;
        padding: 0 1;
        color: #c9d1d9;
    }
    _ResultRow:hover {
        background: #21262d;
    }
    _ResultRow.-selected {
        background: #1f6feb;
        color: #ffffff;
    }
    """

    def __init__(self, result: dict, **kwargs) -> None:
        self._result = result
        super().__init__(_render_result_row(result), markup=True, **kwargs)

    def on_click(self) -> None:
        self.post_message(_RowSelected(self._result))


class _RowSelected(Message):
    def __init__(self, result: dict) -> None:
        super().__init__()
        self.result = result


# ── Main pane ─────────────────────────────────────────────────────────────────

class SearchPane(Container):
    """
    Live KB search pane.

    Debounces keystrokes at 300 ms, runs the fallback search chain, and renders
    results in a two-column layout: result list on the left, atom detail on the
    right.
    """

    DEFAULT_CSS = """
    SearchPane {
        height: 1fr;
    }
    SearchPane #search-input {
        width: 1fr;
        margin: 0 1;
        dock: top;
    }
    SearchPane #search-body {
        height: 1fr;
        layout: horizontal;
    }
    SearchPane #result-list {
        width: 1fr;
        height: 1fr;
        border-right: solid #30363d;
    }
    SearchPane #result-placeholder {
        color: #8b949e;
        padding: 1 2;
    }
    SearchPane #atom-detail {
        width: 2fr;
        height: 1fr;
        padding: 1 2;
        color: #c9d1d9;
    }
    """

    _debounce_timer = None

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search KB…", id="search-input")
        with Horizontal(id="search-body"):
            with ScrollableContainer(id="result-list"):
                yield Static(
                    "[dim]Type to search the knowledge base[/]",
                    id="result-placeholder",
                    markup=True,
                )
            yield Static(
                "[dim]Select a result to view detail[/]",
                id="atom-detail",
                markup=True,
            )

    # ── Input events ──────────────────────────────────────────────────────────

    @on(Input.Changed, "#search-input")
    def _on_input_changed(self, event: Input.Changed) -> None:
        """Debounce: cancel previous timer, start a new 300 ms one."""
        if self._debounce_timer is not None:
            self._debounce_timer.stop()
        query = event.value.strip()
        if not query:
            self._clear_results()
            return
        self._debounce_timer = self.set_timer(_DEBOUNCE_S, lambda: self._fire_search(query))

    @on(Input.Submitted, "#search-input")
    def _on_input_submitted(self, event: Input.Submitted) -> None:
        """Enter: cancel debounce timer and search immediately."""
        if self._debounce_timer is not None:
            self._debounce_timer.stop()
            self._debounce_timer = None
        query = event.value.strip()
        if query:
            self._fire_search(query)

    def _fire_search(self, query: str) -> None:
        self._debounce_timer = None
        self._run_search(query)

    # ── Background search ─────────────────────────────────────────────────────

    @work(thread=True)
    def _run_search(self, query: str) -> None:
        results = _search_kb(query)
        self.post_message(_ResultsReady(query, results))

    def on__results_ready(self, event: _ResultsReady) -> None:
        from textual.css.query import NoMatches

        list_container = self.query_one("#result-list", ScrollableContainer)

        # Remove old rows and placeholder
        for child in list(list_container.children):
            child.remove()

        if not event.results:
            list_container.mount(
                Static(
                    f"[dim]No results for {escape(event.query)!r}[/]",
                    id="result-placeholder",
                    markup=True,
                )
            )
            return

        for r in event.results:
            list_container.mount(_ResultRow(r))

    # ── Row selection → atom detail ───────────────────────────────────────────

    def on__row_selected(self, event: _RowSelected) -> None:
        self._fetch_atom(event.result["id"])

    @work(thread=True)
    def _fetch_atom(self, atom_id: str) -> None:
        atom = _fetch_atom(atom_id)
        self.post_message(_AtomReady(atom))

    def on__atom_ready(self, event: _AtomReady) -> None:
        from textual.css.query import NoMatches
        if event.atom:
            text = _render_atom_detail(event.atom)
        else:
            text = "[dim]Atom not found[/]"
        try:
            self.query_one("#atom-detail", Static).update(text)
        except NoMatches:
            pass

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _clear_results(self) -> None:
        from textual.css.query import NoMatches

        try:
            list_container = self.query_one("#result-list", ScrollableContainer)
        except NoMatches:
            return

        for child in list(list_container.children):
            child.remove()

        list_container.mount(
            Static(
                "[dim]Type to search the knowledge base[/]",
                id="result-placeholder",
                markup=True,
            )
        )

        try:
            self.query_one("#atom-detail", Static).update(
                "[dim]Select a result to view detail[/]"
            )
        except NoMatches:
            pass
