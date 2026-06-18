"""grove/apps/card_builder/wizard.py — scripted card builder steps (v1, no LLM).
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from grove.apps.card_builder import discovery, templates


class WizardMode(str, Enum):
    CATALOG = "catalog"
    SOIL_COUNT = "soil_count"
    NAV = "nav"


@dataclass
class WizardState:
    mode: WizardMode | None = None
    catalog_id: str = ""
    collection: str = ""
    nav_target: str = ""
    label: str = ""
    link_nav: bool = False
    errors: list[str] = field(default_factory=list)


def mode_choices() -> list[tuple[str, str]]:
    return [
        (WizardMode.CATALOG.value, "Enable a catalog card"),
        (WizardMode.SOIL_COUNT.value, "Count items in SOIL"),
        (WizardMode.NAV.value, "Link to a page"),
    ]


def catalog_choices() -> list[tuple[str, str]]:
    rows = discovery.list_disabled_catalog()
    if not rows:
        return []
    return [(r["id"], r["label"]) for r in rows]


def soil_choices() -> list[tuple[str, str]]:
    rows = discovery.list_soil_collections()
    if not rows:
        return []
    return [(c, discovery.soil_collection_label(c)) for c in rows]


def nav_choices() -> list[tuple[str, str]]:
    return discovery.list_nav_targets()


def default_label_for_state(state: WizardState) -> str:
    if state.mode == WizardMode.CATALOG and state.catalog_id:
        for cid, label in catalog_choices():
            if cid == state.catalog_id:
                return label
    if state.mode == WizardMode.SOIL_COUNT and state.collection:
        return discovery.soil_collection_label(state.collection)
    if state.mode == WizardMode.NAV and state.nav_target:
        for tid, label in nav_choices():
            if tid == state.nav_target:
                return label
    return state.label


def preview_line(state: WizardState) -> str:
    if state.mode == WizardMode.CATALOG and state.catalog_id:
        card = next((r for r in discovery.list_disabled_catalog() if r["id"] == state.catalog_id), None)
        if card:
            target = card.get("nav_target") or "—"
            return f"Enable [{card['label']}] → {target}"
    if state.mode == WizardMode.SOIL_COUNT and state.collection:
        n = discovery.count_soil_collection(state.collection)
        label = state.label or default_label_for_state(state)
        nav = state.nav_target if state.link_nav and state.nav_target else "none"
        return f"[{label}] · {n} items · nav {nav}"
    if state.mode == WizardMode.NAV and state.nav_target:
        label = state.label or default_label_for_state(state)
        return f"[{label}] → {state.nav_target}"
    return "Pick options above to preview."


def validate_state(state: WizardState) -> list[str]:
    errors: list[str] = []
    if state.mode is None:
        errors.append("Choose a card type.")
        return errors
    if state.mode == WizardMode.CATALOG:
        if not state.catalog_id:
            errors.append("Choose a catalog card.")
        elif not any(c[0] == state.catalog_id for c in catalog_choices()):
            errors.append("Catalog card not available.")
    elif state.mode == WizardMode.SOIL_COUNT:
        if not state.collection:
            errors.append("Choose a SOIL collection.")
        label = (state.label or default_label_for_state(state)).strip()
        if not label:
            errors.append("Enter a label.")
        if state.link_nav and not state.nav_target:
            errors.append("Choose a nav target or turn off linking.")
    elif state.mode == WizardMode.NAV:
        if not state.nav_target:
            errors.append("Choose a page to open.")
        label = (state.label or default_label_for_state(state)).strip()
        if not label:
            errors.append("Enter a label.")
    return errors


def commit_state(state: WizardState) -> dict | None:
    """Validate and save card. Returns saved card dict or None."""
    state.errors = validate_state(state)
    if state.errors:
        return None
    assert state.mode is not None
    if state.mode == WizardMode.CATALOG:
        saved = templates.enable_catalog_card(state.catalog_id)
        if saved is None:
            state.errors = ["That card is already on Home or cannot be enabled."]
        return saved
    if state.mode == WizardMode.SOIL_COUNT:
        label = (state.label or default_label_for_state(state)).strip()
        nav = state.nav_target if state.link_nav and state.nav_target else None
        saved = templates.make_soil_count_card(
            collection=state.collection,
            label=label,
            nav_target=nav,
        )
        if saved is None:
            state.errors = ["Could not save card."]
        return saved
    label = (state.label or default_label_for_state(state)).strip()
    saved = templates.make_nav_card(label=label, nav_target=state.nav_target)
    if saved is None:
        state.errors = ["That page is already on Home."]
    return saved
