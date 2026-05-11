"""widgets/card_store.py — SOIL-backed card definition store.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import soil

COLLECTION = "willow-dashboard/cards"

_CATALOG: list[dict] = [
    {"id": "todos",      "label": "To-Do List", "category": "personal", "nav_target": "#pane-todos", "order": 10},
    {"id": "projects",   "label": "Projects",   "category": "personal", "nav_target": "#pane-my-projects", "order": 11},
    {"id": "git-status", "label": "Git Status", "category": "dev",      "nav_target": "#pane-git",  "order": 100},
    {"id": "open-prs",   "label": "Open PRs",   "category": "dev",      "nav_target": "#pane-prs",  "order": 101},
]


def load_cards() -> list[dict]:
    """Return all enabled cards sorted by order."""
    records = soil.all_records(COLLECTION)
    enabled = [r for r in records if r.get("enabled", False)]
    return sorted(enabled, key=lambda r: r.get("order", 50))


def save_card(card: dict) -> None:
    """Upsert card by id."""
    soil.put(COLLECTION, card["id"], card)


def seed_catalog() -> None:
    """Insert disabled catalog cards if not already present."""
    existing_ids = {r["_id"] for r in soil.all_records(COLLECTION)}
    for template in _CATALOG:
        if template["id"] not in existing_ids:
            soil.put(COLLECTION, template["id"], {
                **template,
                "built_in": False,
                "enabled": False,
                "value_query": None,
                "state_query": None,
                "refresh_interval": 30,
            })


def validate_card_def(raw: dict) -> dict | None:
    """Validate and normalize a card-def dict. Returns normalized dict or None."""
    card_id = raw.get("id")
    label   = raw.get("label")
    if not card_id or not isinstance(card_id, str):
        return None
    if not label or not isinstance(label, str):
        return None
    return {
        "id":               card_id,
        "label":            label,
        "category":         raw.get("category", "custom"),
        "built_in":         False,
        "enabled":          bool(raw.get("enabled", True)),
        "order":            int(raw.get("order", 50)),
        "value_query":      raw.get("value_query"),
        "state_query":      raw.get("state_query"),
        "refresh_interval": int(raw.get("refresh_interval", 30)),
        "nav_target":       raw.get("nav_target"),
    }
