"""panes/think_map.py — Think Map outline pane (P1: draft edit + save).
b17: THNK1  ΔΣ=42
"""
from __future__ import annotations

from textual import on
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.message import Message
from textual.widgets import Input, Static

from grove.apps.think_map import store, validate
from grove.apps.think_map.outline import outline_rows, render_outline
from grove.theme_textual import ACCENT, SECONDARY


class ThinkMapOpen(Message):
    """Load a specific map (e.g. from Upstream bridge)."""

    def __init__(self, map_id: str) -> None:
        super().__init__()
        self.map_id = map_id


class ThinkMapNavigate(Message):
    """Open Think Map pane with a map loaded."""

    def __init__(self, map_id: str) -> None:
        super().__init__()
        self.map_id = map_id


class ThinkMapPane(Container):
    """Outline brainstorm map — SOIL-backed draft; confirm/export is P3."""

    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("n", "add_branch", "Branch", show=False),
        Binding("c", "add_constraint", "Constraint", show=False),
        Binding("r", "recommend", "Recommend", show=False),
        Binding("d", "delete_node", "Delete", show=False),
        Binding("ctrl+s", "save_draft", "Save", show=False),
    ]

    DEFAULT_CSS = f"""
    ThinkMapPane {{
        height: 1fr;
        padding: 0 1;
    }}
    ThinkMapPane #tm-outline {{
        height: 1fr;
        min-height: 8;
    }}
    ThinkMapPane #tm-edit {{
        height: 3;
        margin-top: 1;
        border: tall {ACCENT};
    }}
    ThinkMapPane #tm-hint {{
        height: 1;
        color: {SECONDARY};
    }}
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._map: dict = store.new_map()
        self._sel = 0

    def compose(self):
        yield Static("", id="tm-outline", markup=True)
        yield Static("Enter: edit selected · Esc: blur editor", id="tm-hint")
        with Vertical():
            yield Input(placeholder="Edit selected node…", id="tm-edit")

    def on_mount(self) -> None:
        active = store.load_active_map()
        if active:
            self._map = active
        else:
            last = store.load_last_draft()
            self._map = last if last else store.new_map()
        self._sel = 0
        self._refresh()

    def on_think_map_open(self, event: ThinkMapOpen) -> None:
        loaded = store.load_map(event.map_id)
        if loaded:
            self._map = loaded
            self._sel = 0
            self._refresh()

    def _rows(self) -> list[dict]:
        return outline_rows(self._map)

    def _selected(self) -> dict | None:
        rows = self._rows()
        if not rows:
            return None
        self._sel = max(0, min(self._sel, len(rows) - 1))
        return rows[self._sel]

    def _refresh(self) -> None:
        rows = self._rows()
        sel_id = rows[self._sel]["id"] if rows else ""
        errors = validate.validation_errors(self._map)
        self.query_one("#tm-outline", Static).update(
            render_outline(
                self._map,
                selected_id=sel_id,
                errors=errors if errors else None,
            )
        )

    def action_cursor_down(self) -> None:
        rows = self._rows()
        if rows:
            self._sel = min(self._sel + 1, len(rows) - 1)
            self._refresh()

    def action_cursor_up(self) -> None:
        if self._sel > 0:
            self._sel -= 1
            self._refresh()

    def action_add_branch(self) -> None:
        if len(store.approach_nodes(self._map)) >= 3:
            return
        self._map = store.add_approach(self._map, text="New approach", tradeoff="TBD tradeoff")
        self._sel = len(self._rows()) - 1
        self._refresh()

    def action_add_constraint(self) -> None:
        self._map = store.add_constraint(self._map, text="New constraint")
        self._sel = len(self._rows()) - 1
        self._refresh()

    def action_recommend(self) -> None:
        row = self._selected()
        if row and row.get("kind") == "approach":
            self._map = store.set_recommended(self._map, row["id"])
            self._refresh()

    def action_delete_node(self) -> None:
        row = self._selected()
        if row and row.get("kind") != "problem":
            self._map = store.delete_node(self._map, row["id"])
            self._sel = max(0, self._sel - 1)
            self._refresh()

    def action_save_draft(self) -> None:
        self._map = store.save_map(self._map)
        store.set_active_map(self._map["id"])
        self._refresh()

    @on(Input.Submitted, "#tm-edit")
    def _edit_submitted(self, event: Input.Submitted) -> None:
        row = self._selected()
        if not row:
            return
        text = event.value.strip()
        if not text:
            return
        self._map = store.update_node_text(self._map, row["id"], text=text)
        event.input.value = ""
        self._map = store.save_map(self._map)
        self._refresh()

    def on_click(self) -> None:
        self.query_one("#tm-edit", Input).focus()
