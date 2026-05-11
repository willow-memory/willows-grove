"""panes/todos.py — Personal to-do list pane.
b17: WGRV1  ΔΣ=42
"""
import uuid

from textual import on
from textual.containers import Container
from textual.widgets import DataTable, Input, Label

import soil

_COLLECTION = "willow-dashboard/todos"


def todos_open_count() -> int:
    """Count of undone to-dos — used by card grid."""
    try:
        items = soil.all_records(_COLLECTION)
        return sum(1 for r in items if not r.get("done", False))
    except Exception:
        return 0


def _load() -> list[dict]:
    return soil.all_records(_COLLECTION)


def _add(text: str) -> None:
    soil.put(_COLLECTION, str(uuid.uuid4()), {"text": text.strip(), "done": False})


def _toggle(record_id: str, current_done: bool) -> None:
    rec = soil.get(_COLLECTION, record_id)
    if rec:
        rec["done"] = not current_done
        rec.pop("_id", None)
        soil.put(_COLLECTION, record_id, rec)


class TodosPane(Container):
    DEFAULT_CSS = """
    TodosPane {
        height: 1fr;
        padding: 1 2;
    }
    TodosPane #todos-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    TodosPane #todos-table {
        height: 1fr;
    }
    TodosPane #todos-input {
        height: 3;
        margin-top: 1;
    }
    """

    def compose(self):
        yield Label("  My To-Do List", id="todos-title")
        table = DataTable(id="todos-table", cursor_type="row")
        table.add_columns(" ", "Task")
        yield table
        yield Input(placeholder="Add a to-do… press Enter to save", id="todos-input")

    def on_mount(self) -> None:
        self._items: list[dict] = []
        self._refresh()

    def _refresh(self) -> None:
        self._items = _load()
        table = self.query_one("#todos-table", DataTable)
        table.clear()
        if not self._items:
            table.add_row("[dim]○[/dim]", "[dim]Nothing here yet — type below to add one[/dim]")
            return
        for item in self._items:
            done = item.get("done", False)
            mark = "[green]✓[/green]" if done else "○"
            text = f"[dim strike]{item['text']}[/dim strike]" if done else item["text"]
            table.add_row(mark, text)

    @on(Input.Submitted, "#todos-input")
    def _on_add(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if text:
            _add(text)
            event.input.clear()
        self._refresh()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.cursor_row < len(self._items):
            item = self._items[event.cursor_row]
            _toggle(item["_id"], item.get("done", False))
            self._refresh()
