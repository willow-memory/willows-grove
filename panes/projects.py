"""panes/projects.py — Personal projects from SOIL.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import uuid
from datetime import date

from textual import on
from textual.containers import Container
from textual.widgets import DataTable, Input, Label

import soil
from grove.theme_textual import ACCENT, HEALTHY, IDLE, PRIMARY, SECONDARY

_COLLECTION = "willow-dashboard/projects"


def projects_active_count() -> int:
    try:
        items = soil.all_records(_COLLECTION)
        return sum(1 for r in items if r.get("status", "active") == "active")
    except Exception:
        return 0


def _load() -> list[dict]:
    return soil.all_records(_COLLECTION)


def _add(name: str, due_date: str = "") -> None:
    soil.put(
        _COLLECTION,
        str(uuid.uuid4()),
        {"name": name.strip(), "status": "active", "due_date": due_date, "notes": ""},
    )


def _toggle(record_id: str, current_status: str) -> None:
    rec = soil.get(_COLLECTION, record_id)
    if rec:
        rec["status"] = "done" if current_status == "active" else "active"
        rec.pop("_id", None)
        soil.put(_COLLECTION, record_id, rec)


class ProjectsPane(Container):
    """Active/done projects stored in SOIL."""

    DEFAULT_CSS = f"""
    ProjectsPane {{
        height: 1fr;
        padding: 1 2;
    }}
    ProjectsPane #projects-title {{
        color: {ACCENT};
        text-style: bold;
        margin-bottom: 1;
    }}
    ProjectsPane #projects-table {{
        height: 1fr;
    }}
    ProjectsPane #projects-input {{
        height: 3;
        margin-top: 1;
    }}
    """

    def compose(self):
        yield Label("  My Projects  (Enter row to toggle done)", id="projects-title")
        table = DataTable(id="projects-table", cursor_type="row")
        table.add_columns(
            (" ", "mark"),
            ("Project", "name"),
            ("Due", "due"),
        )
        yield table
        yield Input(placeholder="Add project: name | YYYY-MM-DD (date optional)", id="projects-input")

    def on_mount(self) -> None:
        self._items: list[dict] = []
        self.refresh_data()

    def refresh_data(self) -> None:
        self._items = _load()
        table = self.query_one("#projects-table", DataTable)
        table.clear()
        if not self._items:
            table.add_row("", "[dim]No projects — type below to add one[/]", "")
            return
        for item in self._items:
            done = item.get("status", "active") == "done"
            mark = f"[{IDLE}]○[/]" if done else f"[{HEALTHY}]●[/]"
            name = item["name"]
            if done:
                name = f"[dim {SECONDARY} strike]{name}[/]"
            else:
                name = f"[{PRIMARY}]{name}[/]"
            due = item.get("due_date") or "—"
            table.add_row(mark, name, due)

    @on(Input.Submitted, "#projects-input")
    def _on_add(self, event: Input.Submitted) -> None:
        raw = event.value.strip()
        if not raw:
            return
        parts = [p.strip() for p in raw.split("|")]
        name = parts[0]
        due_date = ""
        if len(parts) > 1 and parts[1]:
            try:
                due_date = date.fromisoformat(parts[1][:10]).isoformat()
            except ValueError:
                return
        if name:
            _add(name, due_date)
            event.input.clear()
        self.refresh_data()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.cursor_row < len(self._items):
            item = self._items[event.cursor_row]
            _toggle(item["_id"], item.get("status", "active"))
            self.refresh_data()
