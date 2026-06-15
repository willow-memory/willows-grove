"""panes/user_todos.py — My Desk: user todos, projects, deadlines, atoms.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import uuid
from contextlib import suppress
from datetime import date

from rich.markup import escape as _e
from textual import on, work
from textual.binding import Binding
from textual.containers import Container, Horizontal, VerticalScroll
from textual.message import Message
from textual.widgets import DataTable, Input, Label, Static

import soil
from grove.apps.user_board import (
    PROJECTS_COLLECTION,
    TODOS_COLLECTION,
    board_summary,
    fetch_user_board,
)
from grove.theme_textual import ACCENT, DEGRADED, HEALTHY, IDLE, PRIMARY, SECONDARY
from panes.knowledge import atom_body_plain, atom_header_markup, fetch_atom

_KIND_LABEL = {
    "todo": "todo",
    "project": "proj",
    "task": "kart",
}


class _BoardFetched(Message):
    def __init__(self, board: dict) -> None:
        super().__init__()
        self.board = board


class _AtomDetail(Message):
    def __init__(self, atom: dict | None, prefix: str = "") -> None:
        super().__init__()
        self.atom = atom
        self.prefix = prefix


class UserTodosPane(Container):
    """User command center — todos linked to projects, deadlines, and atoms."""

    BINDINGS = [
        Binding("r", "refresh_data", "Refresh"),
        Binding("enter", "toggle_todo", "Toggle", show=False),
    ]

    DEFAULT_CSS = f"""
    UserTodosPane {{
        height: 1fr;
        padding: 0 1;
    }}
    UserTodosPane #desk-title {{
        color: {ACCENT};
        text-style: bold;
        height: 1;
    }}
    UserTodosPane #desk-stats {{
        height: 1;
        margin-bottom: 1;
    }}
    UserTodosPane #desk-add {{
        height: 3;
        margin-bottom: 1;
    }}
    UserTodosPane #desk-body {{
        height: 1fr;
    }}
    UserTodosPane #desk-queue {{
        width: 1fr;
        height: 1fr;
        border-right: solid {SECONDARY};
    }}
    UserTodosPane #desk-detail-scroll {{
        width: 1fr;
        height: 1fr;
    }}
    UserTodosPane #desk-detail-header {{
        height: auto;
        padding: 0 1;
    }}
    UserTodosPane #desk-detail-body {{
        height: auto;
        padding: 0 1;
    }}
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._items: list[dict] = []
        self._board: dict = {}

    def compose(self):
        yield Label("  My Desk — todos · projects · deadlines", id="desk-title")
        yield Static("", id="desk-stats", markup=True)
        yield Input(
            placeholder="Add todo: text | project | YYYY-MM-DD  (Enter to save)",
            id="desk-add",
        )
        with Horizontal(id="desk-body"):
            queue = DataTable(id="desk-queue", cursor_type="row")
            queue.add_columns(
                ("Due", "due"),
                ("Kind", "kind"),
                ("Project", "project"),
                ("Item", "item"),
            )
            yield queue
            with VerticalScroll(id="desk-detail-scroll"):
                yield Static(
                    f"[dim {SECONDARY}]Your command center — todos, projects, "
                    "deadlines, and running Kart tasks.[/]",
                    id="desk-detail-header",
                    markup=True,
                )
                yield Static("", id="desk-detail-body")

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        self._fetch()

    @work(thread=True, exit_on_error=False)
    def _fetch(self) -> None:
        self.post_message(_BoardFetched(fetch_user_board()))

    def on__board_fetched(self, event: _BoardFetched) -> None:
        try:
            self._apply_board(event.board)
        except Exception as exc:
            self._show_error(str(exc))

    def _apply_board(self, board: dict) -> None:
        self._board = board
        self._items = board.get("items") or []
        overdue = board.get("overdue", 0)
        open_todos = board.get("open_todos", 0)
        projects = board.get("active_projects", 0)
        stats = (
            f"[{PRIMARY}]{open_todos}[/] todos  "
            f"[{PRIMARY}]{projects}[/] projects"
        )
        if overdue:
            stats += f"  [{DEGRADED}]{overdue} overdue[/]"
        self.query_one("#desk-stats", Static).update(stats)

        table = self.query_one("#desk-queue", DataTable)
        table.clear()
        if not self._items:
            table.add_row("", "", "", "nothing on the desk — add a todo below")
            return
        for item in self._items:
            due = item.get("due_date") or "—"
            urgency = item.get("urgency", "none")
            if urgency == "overdue":
                due = f"[{DEGRADED}]{_e(due)}[/]"
            elif urgency == "soon":
                due = f"[{HEALTHY}]{_e(due)}[/]"
            else:
                due = _e(due)
            kind = _KIND_LABEL.get(item.get("kind", ""), item.get("kind", ""))
            project = _e(item.get("project") or "—")
            title = _e(item.get("title") or "")
            table.add_row(due, kind, project, title)

    @on(DataTable.RowHighlighted, "#desk-queue")
    def _on_row(self, event: DataTable.RowHighlighted) -> None:
        idx = event.cursor_row
        if idx < 0 or idx >= len(self._items):
            return
        self._show_item(self._items[idx])

    def _show_item(self, item: dict) -> None:
        kind = item.get("kind", "")
        title = item.get("title", "")
        project = item.get("project") or "—"
        due = item.get("due_date") or "—"
        notes = item.get("notes") or ""
        atom_id = item.get("atom_id") or ""
        urgency = item.get("urgency", "none")
        urg_s = ""
        if urgency == "overdue":
            urg_s = f"  [{DEGRADED}]OVERDUE[/]"
        elif urgency == "soon":
            urg_s = f"  [{HEALTHY}]due soon[/]"

        header = (
            f"[bold {ACCENT}]{_e(kind.upper())}[/]{urg_s}\n"
            f"[{PRIMARY}]{_e(title)}[/]\n"
            f"[dim {SECONDARY}]project[/] {_e(project)}  "
            f"[dim {SECONDARY}]due[/] {_e(due)}  "
            f"[dim {SECONDARY}]source[/] {_e(item.get('source', ''))}"
        )
        body_lines = []
        if notes:
            body_lines.append(notes)
        if kind == "todo":
            body_lines.append("Enter toggles done on todo rows.")
        if kind == "project":
            body_lines.append("Manage projects on nav 3 or link todos via project name.")
        if atom_id:
            prefix = "\n\n".join(body_lines) if body_lines else ""
            self._fetch_atom_detail(atom_id, prefix)
            return
        body = "\n\n".join(body_lines) if body_lines else "(no extra detail)"
        with suppress(Exception):
            self.query_one("#desk-detail-header", Static).update(header)
            self.query_one("#desk-detail-body", Static).update(body)

    @work(thread=True, exit_on_error=False)
    def _fetch_atom_detail(self, atom_id: str, prefix: str = "") -> None:
        self.post_message(_AtomDetail(fetch_atom(atom_id), prefix))

    def on__atom_detail(self, event: _AtomDetail) -> None:
        with suppress(Exception):
            if not event.atom:
                self.query_one("#desk-detail-header", Static).update("[dim]Atom not found[/]")
                self.query_one("#desk-detail-body", Static).update("")
                return
            hdr = atom_header_markup(event.atom)
            body = atom_body_plain(event.atom)
            if event.prefix:
                body = event.prefix + "\n\n" + body
            self.query_one("#desk-detail-header", Static).update(hdr)
            self.query_one("#desk-detail-body", Static).update(body)

    def _selected_item(self) -> dict | None:
        table = self.query_one("#desk-queue", DataTable)
        idx = table.cursor_row
        if 0 <= idx < len(self._items):
            return self._items[idx]
        return None

    def action_toggle_todo(self) -> None:
        item = self._selected_item()
        if not item or item.get("kind") != "todo":
            return
        rec_id = item.get("id")
        if not rec_id:
            return
        rec = soil.get(TODOS_COLLECTION, rec_id)
        if not rec:
            return
        rec["done"] = not rec.get("done", False)
        rec.pop("_id", None)
        soil.put(TODOS_COLLECTION, rec_id, rec)
        self.refresh_data()

    @on(Input.Submitted, "#desk-add")
    def _on_add(self, event: Input.Submitted) -> None:
        raw = event.value.strip()
        if not raw:
            return
        parts = [p.strip() for p in raw.split("|")]
        text = parts[0]
        project = parts[1] if len(parts) > 1 else ""
        due_raw = parts[2] if len(parts) > 2 else ""
        due_date = ""
        if due_raw:
            try:
                due_date = date.fromisoformat(due_raw[:10]).isoformat()
            except ValueError:
                self._show_error(f"bad date: {due_raw} (use YYYY-MM-DD)")
                return
        record = {
            "text": text,
            "done": False,
            "project": project,
            "due_date": due_date,
            "atom_id": "",
            "notes": "",
        }
        soil.put(TODOS_COLLECTION, str(uuid.uuid4()), record)
        event.input.clear()
        self.refresh_data()

    def _show_error(self, text: str) -> None:
        with suppress(Exception):
            self.query_one("#desk-detail-header", Static).update(
                f"[{DEGRADED}]My Desk[/]"
            )
            self.query_one("#desk-detail-body", Static).update(_e(text))
