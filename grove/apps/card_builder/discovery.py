"""grove/apps/card_builder/discovery.py — list data sources and nav targets.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import os
from pathlib import Path

import soil

from widgets.card_store import all_soil_cards
from widgets.nav_bar import NAV_LABELS, NAV_TARGETS


def _store_root() -> Path:
    return Path(os.environ.get("WILLOW_STORE_ROOT", str(Path.home() / ".willow" / "store")))


def list_soil_collections() -> list[str]:
    """Discover SOIL collections that have a store.db under the store root."""
    root = _store_root()
    if not root.exists():
        return []
    found: list[str] = []
    for db_path in root.rglob("store.db"):
        rel = db_path.parent.relative_to(root)
        found.append(str(rel))
    return sorted(set(found))


def list_nav_targets() -> list[tuple[str, str]]:
    """Return (target_id, label) pairs for top-level nav and internal panes."""
    targets: list[tuple[str, str]] = [
        ("#pane-user-todos", "My Desk"),
        ("#pane-tasks", "Tasks"),
        ("#pane-agents", "Agents"),
        ("#pane-routing", "Routing"),
        ("#pane-mcp", "MCP"),
        ("#pane-git", "Git"),
        ("#pane-prs", "PRs"),
    ]
    for name in NAV_TARGETS:
        if name == "home":
            continue
        targets.append((name, NAV_LABELS.get(name, name.title())))
    return targets


def list_disabled_catalog() -> list[dict]:
    """Catalog cards in SOIL that are not enabled yet and not built-in duplicates."""
    from widgets.card_store import _CATALOG_ALIASES, _builtin_nav_targets

    rows = all_soil_cards()
    return sorted(
        [
            r for r in rows
            if not r.get("enabled", False)
            and not r.get("built_in", False)
            and _card_id(r) not in _CATALOG_ALIASES
            and (not r.get("nav_target") or r.get("nav_target") not in _builtin_nav_targets())
        ],
        key=lambda r: (r.get("order", 50), r.get("label", "")),
    )


def _card_id(record: dict) -> str:
    return str(record.get("id") or record.get("_id") or "")


def soil_collection_label(collection: str) -> str:
    """Plain label from a SOIL collection path."""
    tail = collection.split("/")[-1].replace("-", " ").replace("_", " ")
    return tail.title()


def count_soil_collection(collection: str) -> int:
    """Row count for preview — never raises."""
    try:
        return len(soil.all_records(collection))
    except Exception:
        return 0
