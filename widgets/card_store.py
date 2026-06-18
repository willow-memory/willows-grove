"""widgets/card_store.py — SOIL-backed card definitions + built-in Home cards.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import re

import soil

COLLECTION = "willow-dashboard/cards"

PLUS_CARD_ID = "add-card"

BUILTIN_CARDS: list[dict] = [
    {
        "id": "human",
        "label": "Human",
        "subtitle": "consent · attestation · review",
        "category": "work",
        "nav_target": "#pane-human",
        "built_in": True,
        "enabled": True,
        "order": 0,
    },
    {
        "id": "user-todos",
        "label": "My Desk",
        "subtitle": "todos · projects · deadlines",
        "category": "work",
        "nav_target": "#pane-user-todos",
        "built_in": True,
        "enabled": True,
        "order": 1,
    },
    {
        "id": "tasks",
        "label": "Tasks",
        "subtitle": "kart queue",
        "category": "work",
        "nav_target": "#pane-tasks",
        "built_in": True,
        "enabled": True,
        "order": 2,
    },
    {
        "id": "agents",
        "label": "Agents",
        "subtitle": "fleet bus",
        "category": "dev",
        "nav_target": "#pane-agents",
        "built_in": True,
        "enabled": True,
        "order": 3,
    },
    {
        "id": "routing",
        "label": "Routing",
        "subtitle": "decisions",
        "category": "dev",
        "nav_target": "#pane-routing",
        "built_in": True,
        "enabled": True,
        "order": 4,
    },
    {
        "id": "knowledge",
        "label": "Knowledge",
        "subtitle": "KB search",
        "category": "knowledge",
        "nav_target": "knowledge",
        "built_in": True,
        "enabled": True,
        "order": 5,
    },
    {
        "id": "think-map",
        "label": "Think",
        "subtitle": "brainstorm · map",
        "category": "knowledge",
        "nav_target": "#pane-think-map",
        "built_in": True,
        "enabled": True,
        "order": 6,
    },
    {
        "id": "mcp",
        "label": "MCP",
        "subtitle": "server registry",
        "category": "dev",
        "nav_target": "#pane-mcp",
        "built_in": True,
        "enabled": True,
        "order": 7,
    },
    {
        "id": "git",
        "label": "Git",
        "subtitle": "status",
        "category": "dev",
        "nav_target": "#pane-git",
        "built_in": True,
        "enabled": True,
        "order": 8,
    },
    {
        "id": "prs",
        "label": "PRs",
        "subtitle": "open",
        "category": "dev",
        "nav_target": "#pane-prs",
        "built_in": True,
        "enabled": True,
        "order": 9,
    },
]

_CATALOG: list[dict] = [
    {
        "id": "git-status",
        "label": "Git Status",
        "subtitle": "repo branch",
        "category": "dev",
        "nav_target": "#pane-git",
        "order": 100,
    },
    {
        "id": "open-prs",
        "label": "Open PRs",
        "subtitle": "awaiting review",
        "category": "dev",
        "nav_target": "#pane-prs",
        "order": 101,
    },
    {
        "id": "desk-todos",
        "label": "Desk TODOs",
        "subtitle": "your list",
        "category": "tasks",
        "nav_target": "#pane-user-todos",
        "order": 102,
    },
    {
        "id": "kart-tasks",
        "label": "Kart Tasks",
        "subtitle": "queue",
        "category": "tasks",
        "nav_target": "#pane-tasks",
        "order": 103,
    },
    {
        "id": "upstream-inbox",
        "label": "Upstream",
        "subtitle": "GitHub drafts",
        "category": "dev",
        "nav_target": "#pane-upstream",
        "order": 104,
    },
]

PLUS_CARD: dict = {
    "id": PLUS_CARD_ID,
    "label": "+",
    "subtitle": "Add card",
    "category": "system",
    "nav_target": PLUS_CARD_ID,
    "built_in": True,
    "enabled": True,
    "order": 9999,
}


_CATALOG_ALIASES: dict[str, str] = {
    "git-status": "git",
    "open-prs": "prs",
    "desk-todos": "user-todos",
    "kart-tasks": "tasks",
}

# Legacy cards from pre-fresh-start dashboard — never show on Home.
_RETIRED_HOME_IDS = frozenset({"welcome", "grove"})


def _builtin_ids() -> set[str]:
    return {c["id"] for c in BUILTIN_CARDS}


def _builtin_nav_targets() -> set[str]:
    return {c["nav_target"] for c in BUILTIN_CARDS if c.get("nav_target")}


def _card_id(record: dict) -> str:
    return str(record.get("id") or record.get("_id") or "")


def _is_duplicate_home_card(record: dict, seen_nav: set[str]) -> bool:
    """True if this SOIL card should not appear alongside built-ins."""
    cid = _card_id(record)
    if not cid or cid in _builtin_ids():
        return True
    if cid in _RETIRED_HOME_IDS or cid in _CATALOG_ALIASES:
        return True
    nav = record.get("nav_target")
    if nav:
        if nav in _builtin_nav_targets() or nav in seen_nav:
            return True
        seen_nav.add(nav)
    return False


def reconcile_duplicates() -> None:
    """Disable SOIL cards that duplicate built-in grid entries or are retired."""
    for rec in all_soil_cards():
        cid = _card_id(rec)
        nav = rec.get("nav_target")
        retired = cid in _RETIRED_HOME_IDS or cid in _builtin_ids()
        duplicate = cid in _CATALOG_ALIASES or (
            bool(nav) and nav in _builtin_nav_targets() and cid not in _builtin_ids()
        )
        if retired or duplicate:
            if rec.get("enabled"):
                rec["enabled"] = False
                save_card(rec)


def load_cards() -> list[dict]:
    """Return enabled SOIL cards sorted by order (excludes built-ins and duplicates)."""
    records = soil.all_records(COLLECTION)
    seen_nav: set[str] = set(_builtin_nav_targets())
    enabled: list[dict] = []
    for rec in records:
        if not rec.get("enabled", False):
            continue
        if "id" not in rec and "_id" in rec:
            rec["id"] = rec["_id"]
        if _is_duplicate_home_card(rec, seen_nav):
            continue
        enabled.append(rec)
    return sorted(enabled, key=lambda r: (r.get("order", 50), r.get("label", "")))


def load_home_cards() -> list[dict]:
    """Built-in cards + enabled SOIL cards, sorted by order."""
    builtins = [dict(c) for c in BUILTIN_CARDS if c.get("enabled", True)]
    soil_cards = load_cards()
    return sorted(
        builtins + soil_cards,
        key=lambda r: (r.get("order", 50), r.get("label", "")),
    )


def all_soil_cards() -> list[dict]:
    """All SOIL card records including disabled catalog entries."""
    records = soil.all_records(COLLECTION)
    for rec in records:
        if "id" not in rec and "_id" in rec:
            rec["id"] = rec["_id"]
    return records


def get_card(card_id: str) -> dict | None:
    for card in BUILTIN_CARDS:
        if card["id"] == card_id:
            return dict(card)
    rec = soil.get(COLLECTION, card_id)
    if rec is None:
        return None
    if "id" not in rec:
        rec["id"] = rec.get("_id", card_id)
    return rec


def save_card(card: dict) -> None:
    """Upsert card by id."""
    normalized = validate_card_def(card)
    if normalized is None:
        raise ValueError("invalid card definition")
    soil.put(COLLECTION, normalized["id"], normalized)


def seed_catalog() -> None:
    """Insert disabled catalog cards if not already present."""
    existing_ids = {_card_id(r) for r in soil.all_records(COLLECTION)}
    for template in _CATALOG:
        if template["id"] in existing_ids:
            continue
        soil.put(
            COLLECTION,
            template["id"],
            validate_card_def(
                {
                    **template,
                    "built_in": False,
                    "enabled": False,
                    "value_source": None,
                    "refresh_interval": 30,
                }
            ),
        )
    reconcile_duplicates()


def enable_dev_cards() -> None:
    """Turn on git-status and open-prs cards for local dashboard dev (idempotent)."""
    seed_catalog()
    for cid in ("git-status", "open-prs"):
        records = [r for r in soil.all_records(COLLECTION) if _card_id(r) == cid]
        if not records:
            continue
        card = dict(records[0])
        if card.get("enabled"):
            continue
        card["enabled"] = True
        save_card(card)


def validate_card_def(raw: dict) -> dict | None:
    """Validate and normalize a card dict. Returns normalized dict or None."""
    card_id = raw.get("id") or raw.get("_id")
    label = raw.get("label")
    if not card_id or not isinstance(card_id, str):
        return None
    if not label or not isinstance(label, str):
        return None
    value_source = raw.get("value_source")
    if value_source is not None and not isinstance(value_source, dict):
        return None
    return {
        "id": card_id,
        "label": label,
        "category": raw.get("category", "custom"),
        "built_in": bool(raw.get("built_in", False)),
        "enabled": bool(raw.get("enabled", True)),
        "order": int(raw.get("order", 50)),
        "subtitle": raw.get("subtitle"),
        "nav_target": raw.get("nav_target"),
        "value_source": value_source,
        "refresh_interval": int(raw.get("refresh_interval", 30)),
    }


def slugify(label: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return slug or "card"


def unique_card_id(label: str) -> str:
    """Return a unique SOIL card id for a new user card."""
    base = slugify(label)
    taken = _builtin_ids() | {r.get("id", r.get("_id")) for r in soil.all_records(COLLECTION)}
    if base not in taken:
        return base
    n = 2
    while f"{base}-{n}" in taken:
        n += 1
    return f"{base}-{n}"
