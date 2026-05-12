"""panes/projects.py — Personal projects pane.
b17: WGRV1  ΔΣ=42
"""
import uuid

from textual import on
from textual.containers import Container
from textual.widgets import DataTable, Input, Label

import soil

_COLLECTION = "willow-dashboard/projects"


def projects_active_count() -> int:
    """Count of active projects — used by card grid."""
    try:
        items = soil.all_records(_COLLECTION)
        return sum(1 for r in items if r.get("status", "active") == "active")
    except Exception:
        return 0


def _load() -> list[dict]:
    return soil.all_records(_COLLECTION)


def _add(name: str) -> None:
    soil.put(_COLLECTION, str(uuid.uuid4()), {"name": name.strip(), "status": "active"})


def _toggle(record_id: str, current_status: str) -> None:
    rec = soil.get(_COLLECTION, record_id)
    if rec:
        rec["status"] = "done" if current_status == "active" else "active"
        rec.pop("_id", None)
        soil.put(_COLLECTION, record_id, rec)


class ProjectsPane(Container):
    DEFAULT_CSS = """
    ProjectsPane {
        height: 1fr;
        padding: 1 2;
    }
    ProjectsPane #projects-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    ProjectsPane #projects-table {
        height: 1fr;
    }
    ProjectsPane #projects-input {
        height: 3;
        margin-top: 1;
    }
    """

    def compose(self):
        yield Label("  My Projects", id="projects-title")
        table = DataTable(id="projects-table", cursor_type="row")
        table.add_columns(" ", "Project")
        yield table
        yield Input(placeholder="Add a project… press Enter to save", id="projects-input")

    def on_mount(self) -> None:
        self._items: list[dict] = []
        self._refresh()

    def _refresh(self) -> None:
        self._items = _load()
        table = self.query_one("#projects-table", DataTable)
        table.clear()
        if not self._items:
            table.add_row("[dim]○[/dim]", "[dim]No projects yet — type below to add one[/dim]")
            return
        for item in self._items:
            done = item.get("status", "active") == "done"
            mark = "[green]✓[/green]" if done else "[blue]●[/blue]"
            name = f"[dim strike]{item['name']}[/dim strike]" if done else item["name"]
            table.add_row(mark, name)

    @on(Input.Submitted, "#projects-input")
    def _on_add(self, event: Input.Submitted) -> None:
        name = event.value.strip()
        if name:
            _add(name)
            event.input.clear()
        self._refresh()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.cursor_row < len(self._items):
            item = self._items[event.cursor_row]
            _toggle(item["_id"], item.get("status", "active"))
            self._refresh()
