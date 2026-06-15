"""widgets/card_builder_modal.py — scripted v1 card builder wizard.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Checkbox, Input, Label, Select, Static

from grove.apps.card_builder import wizard
from grove.apps.card_builder.wizard import WizardMode, WizardState
from grove.theme_textual import ACCENT, BG, BORDER, PRIMARY, SECONDARY
from widgets.card_store import seed_catalog


class CardBuilderModal(ModalScreen[bool]):
    """Step-through wizard: catalog enable, SOIL count, or nav link. No LLM."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=False),
    ]

    DEFAULT_CSS = f"""
    CardBuilderModal {{
        align: center middle;
    }}
    CardBuilderModal #cb-box {{
        width: 56;
        height: auto;
        max-height: 90%;
        border: solid {BORDER};
        background: {BG};
        padding: 1 2;
    }}
    CardBuilderModal Label {{
        color: {PRIMARY};
        margin-bottom: 1;
    }}
    CardBuilderModal #cb-title {{
        color: {ACCENT};
        text-style: bold;
        margin-bottom: 1;
    }}
    CardBuilderModal #cb-preview {{
        color: {SECONDARY};
        margin: 1 0;
        min-height: 2;
    }}
    CardBuilderModal #cb-error {{
        color: #c0392b;
        margin-bottom: 1;
    }}
    CardBuilderModal Select {{
        margin-bottom: 1;
    }}
    CardBuilderModal Input {{
        margin-bottom: 1;
    }}
    CardBuilderModal #cb-actions {{
        height: auto;
        margin-top: 1;
    }}
    CardBuilderModal Button {{
        margin-right: 1;
    }}
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._state = WizardState()
        self._saved = False

    @property
    def card_saved(self) -> bool:
        return self._saved

    def compose(self) -> ComposeResult:
        with Container(id="cb-box"):
            yield Static("Add dashboard card", id="cb-title")
            yield Static("", id="cb-step-label")
            with Vertical(id="cb-fields"):
                yield Select([], id="cb-mode", prompt="Card type")
                yield Select([], id="cb-catalog", prompt="Catalog card")
                yield Select([], id="cb-soil", prompt="SOIL collection")
                yield Select([], id="cb-nav", prompt="Open page")
                yield Input(placeholder="Card label", id="cb-label")
                yield Checkbox("Link to a page when clicked", id="cb-link-nav")
                yield Select([], id="cb-nav-link", prompt="Link target")
            yield Static("", id="cb-preview")
            yield Static("", id="cb-error")
            with Vertical(id="cb-actions"):
                yield Button("Save", variant="primary", id="cb-save")
                yield Button("Cancel", id="cb-cancel")

    def on_mount(self) -> None:
        seed_catalog()
        self._populate_mode_select()
        self._apply_step()
        self.query_one("#cb-mode", Select).focus()

    def _populate_mode_select(self) -> None:
        mode = self.query_one("#cb-mode", Select)
        mode.set_options(wizard.mode_choices())

    def _populate_catalog_select(self) -> None:
        sel = self.query_one("#cb-catalog", Select)
        choices = wizard.catalog_choices()
        if choices:
            sel.set_options(choices)
            sel.value = choices[0][0]
            self._state.catalog_id = choices[0][0]
        else:
            sel.set_options([("", "— none available —")])

    def _populate_soil_select(self) -> None:
        sel = self.query_one("#cb-soil", Select)
        choices = wizard.soil_choices()
        if choices:
            sel.set_options(choices)
            sel.value = choices[0][0]
            self._state.collection = choices[0][0]
        else:
            sel.set_options([("", "— no collections found —")])

    def _populate_nav_select(self) -> None:
        choices = wizard.nav_choices()
        nav = self.query_one("#cb-nav", Select)
        nav_link = self.query_one("#cb-nav-link", Select)
        if choices:
            nav.set_options(choices)
            nav_link.set_options(choices)
            nav.value = choices[0][0]
            nav_link.value = choices[0][0]
            self._state.nav_target = choices[0][0]
        else:
            nav.set_options([("", "— none —")])
            nav_link.set_options([("", "— none —")])

    def _apply_step(self) -> None:
        mode = self._state.mode
        self.query_one("#cb-step-label", Static).update(
            "Choose what kind of card to add."
            if mode is None
            else f"Configure your {mode.value.replace('_', ' ')} card."
        )
        self.query_one("#cb-catalog", Select).display = mode == WizardMode.CATALOG
        self.query_one("#cb-soil", Select).display = mode == WizardMode.SOIL_COUNT
        self.query_one("#cb-nav", Select).display = mode == WizardMode.NAV
        label_input = self.query_one("#cb-label", Input)
        label_input.display = mode in (WizardMode.SOIL_COUNT, WizardMode.NAV)
        link_cb = self.query_one("#cb-link-nav", Checkbox)
        link_cb.display = mode == WizardMode.SOIL_COUNT
        nav_link = self.query_one("#cb-nav-link", Select)
        nav_link.display = mode == WizardMode.SOIL_COUNT and link_cb.value
        if mode == WizardMode.SOIL_COUNT and not label_input.value:
            label_input.value = wizard.default_label_for_state(self._state)
        if mode == WizardMode.NAV and not label_input.value:
            label_input.value = wizard.default_label_for_state(self._state)
        self._update_preview()
        self._clear_error()

    def _update_preview(self) -> None:
        self.query_one("#cb-preview", Static).update(wizard.preview_line(self._state))

    def _clear_error(self) -> None:
        self.query_one("#cb-error", Static).update("")

    def _show_error(self, message: str) -> None:
        self.query_one("#cb-error", Static).update(message)

    @on(Select.Changed, "#cb-mode")
    def _on_mode_changed(self, event: Select.Changed) -> None:
        value = event.value
        if not value or value is Select.BLANK:
            self._state.mode = None
        else:
            self._state.mode = WizardMode(str(value))
        if self._state.mode == WizardMode.CATALOG:
            self._populate_catalog_select()
        elif self._state.mode == WizardMode.SOIL_COUNT:
            self._populate_soil_select()
            self._populate_nav_select()
        elif self._state.mode == WizardMode.NAV:
            self._populate_nav_select()
        self._apply_step()

    @on(Select.Changed, "#cb-catalog")
    def _on_catalog_changed(self, event: Select.Changed) -> None:
        if event.value and event.value is not Select.BLANK:
            self._state.catalog_id = str(event.value)
        self._update_preview()

    @on(Select.Changed, "#cb-soil")
    def _on_soil_changed(self, event: Select.Changed) -> None:
        if event.value and event.value is not Select.BLANK:
            self._state.collection = str(event.value)
            if not self.query_one("#cb-label", Input).value:
                self.query_one("#cb-label", Input).value = wizard.default_label_for_state(
                    self._state
                )
        self._update_preview()

    @on(Select.Changed, "#cb-nav")
    def _on_nav_changed(self, event: Select.Changed) -> None:
        if event.value and event.value is not Select.BLANK:
            self._state.nav_target = str(event.value)
            if not self.query_one("#cb-label", Input).value:
                self.query_one("#cb-label", Input).value = wizard.default_label_for_state(
                    self._state
                )
        self._update_preview()

    @on(Select.Changed, "#cb-nav-link")
    def _on_nav_link_changed(self, event: Select.Changed) -> None:
        if event.value and event.value is not Select.BLANK:
            self._state.nav_target = str(event.value)
        self._update_preview()

    @on(Input.Changed, "#cb-label")
    def _on_label_changed(self, event: Input.Changed) -> None:
        self._state.label = event.value.strip()
        self._update_preview()

    @on(Checkbox.Changed, "#cb-link-nav")
    def _on_link_nav_changed(self, event: Checkbox.Changed) -> None:
        self._state.link_nav = bool(event.value)
        self.query_one("#cb-nav-link", Select).display = (
            self._state.mode == WizardMode.SOIL_COUNT and event.value
        )
        self._update_preview()

    @on(Button.Pressed, "#cb-save")
    def _on_save(self) -> None:
        label_input = self.query_one("#cb-label", Input)
        self._state.label = label_input.value.strip()
        saved = wizard.commit_state(self._state)
        if saved is None:
            err = "; ".join(self._state.errors) or "Could not save card."
            self._show_error(err)
            return
        self._saved = True
        self.dismiss(True)

    @on(Button.Pressed, "#cb-cancel")
    def action_cancel(self) -> None:
        self.dismiss(False)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.action_cancel()
            event.prevent_default()
            event.stop()
