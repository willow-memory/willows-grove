"""grove/apps/card_builder/templates.py — scripted card-def builders (v1).
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from widgets.card_store import (
    _CATALOG_ALIASES,
    _builtin_nav_targets,
    get_card,
    save_card,
    unique_card_id,
    validate_card_def,
)


def enable_catalog_card(card_id: str) -> dict | None:
    """Enable a disabled catalog card. Returns saved card or None."""
    card = get_card(card_id)
    if card is None or card.get("built_in"):
        return None
    if card_id in _CATALOG_ALIASES:
        return None
    nav = card.get("nav_target")
    if nav and nav in _builtin_nav_targets():
        return None
    card["enabled"] = True
    normalized = validate_card_def(card)
    if normalized is None:
        return None
    save_card(normalized)
    return normalized


def make_soil_count_card(
    *,
    collection: str,
    label: str,
    nav_target: str | None = None,
    order: int = 50,
) -> dict | None:
    """Create a card that shows a SOIL collection count on the subtitle."""
    if nav_target and nav_target in _builtin_nav_targets():
        return None
    card_id = unique_card_id(label)
    raw = {
        "id": card_id,
        "label": label.strip(),
        "category": "custom",
        "built_in": False,
        "enabled": True,
        "order": order,
        "nav_target": nav_target,
        "subtitle": None,
        "value_source": {"type": "soil_count", "collection": collection},
        "refresh_interval": 30,
    }
    normalized = validate_card_def(raw)
    if normalized is None:
        return None
    save_card(normalized)
    return normalized


def make_nav_card(
    *,
    label: str,
    nav_target: str,
    subtitle: str | None = None,
    order: int = 50,
) -> dict | None:
    """Create a nav-only launcher card."""
    if nav_target in _builtin_nav_targets():
        return None
    card_id = unique_card_id(label)
    raw = {
        "id": card_id,
        "label": label.strip(),
        "category": "custom",
        "built_in": False,
        "enabled": True,
        "order": order,
        "nav_target": nav_target,
        "subtitle": subtitle or "open",
        "value_source": None,
        "refresh_interval": 30,
    }
    normalized = validate_card_def(raw)
    if normalized is None:
        return None
    save_card(normalized)
    return normalized
