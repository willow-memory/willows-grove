"""widgets/knowledge_nav.py — KnowledgeNav for Knowledge ContextPanel slot.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from textual import on, work
from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Input, Static


class KnowledgeAtomSelected(Message):
    """Posted when the user confirms a result row in KnowledgeNav."""

    def __init__(self, atom_id: int) -> None:
        super().__init__()
        self.atom_id = atom_id


class _KnowledgeSearchDone(Message):
    def __init__(self, rows: list[dict]) -> None:
        super().__init__()
        self.rows: list[dict] = rows


class KnowledgeNav(Widget):
    """Left-panel widget: search input + results list for the Knowledge pane.

    Up/Down arrows move cursor through results.
    Enter with text = search; Enter with empty input = confirm highlighted result.
    """

    DEFAULT_CSS = """
    KnowledgeNav {
        width: 1fr;
        height: 1fr;
    }
    KnowledgeNav #kn-results {
        height: 1fr;
        padding: 0 1;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._rows: list[dict] = []
        self._cursor: int = -1

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search knowledge…", id="kn-search")
        yield Static("", id="kn-results", markup=True)

    @on(Input.Submitted, "#kn-search")
    def _on_search(self, event: Input.Submitted) -> None:
        query = event.value.strip()
        if not query:
            if self._cursor >= 0 and self._rows:
                self.action_confirm()
            return
        self._search(query)

    @work(thread=True)
    def _search(self, query: str) -> None:
        from panes.knowledge import search_kb
        rows = search_kb(query, limit=20)
        self.post_message(_KnowledgeSearchDone(rows))

    def on__knowledge_search_done(self, event: _KnowledgeSearchDone) -> None:
        self._rows = event.rows
        self._cursor = 0 if self._rows else -1
        self._render_results()

    def on_key(self, event) -> None:
        if event.key == "up":
            self.action_cursor_up()
            event.stop()
        elif event.key == "down":
            self.action_cursor_down()
            event.stop()

    def action_cursor_up(self) -> None:
        if self._rows and self._cursor > 0:
            self._cursor -= 1
            self._render_results()

    def action_cursor_down(self) -> None:
        if self._rows and self._cursor < len(self._rows) - 1:
            self._cursor += 1
            self._render_results()

    def action_confirm(self) -> None:
        if 0 <= self._cursor < len(self._rows):
            atom_id = self._rows[self._cursor]["id"]
            self.post_message(KnowledgeAtomSelected(atom_id))

    def _render_results(self) -> None:
        from textual.css.query import NoMatches
        if not self._rows:
            text = "[dim]no results[/]"
        else:
            lines = []
            for i, row in enumerate(self._rows):
                title = (row.get("title", "") or "—")[:16]
                atom_id = row.get("id", "?")
                if i == self._cursor:
                    lines.append(f"[reverse] {i + 1:2}. {atom_id} {title}[/]")
                else:
                    lines.append(f"[dim] {i + 1:2}.[/] [#58a6ff]{atom_id}[/] {title}")
            text = "\n".join(lines)
        try:
            self.query_one("#kn-results", Static).update(text)
        except NoMatches:
            pass
