"""grove/apps/card_builder/values.py — resolve live card subtitles from value_source.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import soil


def resolve_subtitle(card: dict) -> str:
    """Return subtitle text for a home card — static or live count."""
    source = card.get("value_source")
    if isinstance(source, dict):
        kind = source.get("type")
        if kind == "soil_count":
            collection = source.get("collection", "")
            try:
                n = len(soil.all_records(collection))
            except Exception:
                n = 0
            noun = "item" if n == 1 else "items"
            return f"{n} {noun}"
    static = card.get("subtitle")
    if static:
        return str(static)
    return ""
