"""grove/apps/think_map/validate.py — confirm gate rules (brainstorming skill).
b17: THNK1  ΔΣ=42
"""
from __future__ import annotations

from grove.apps.think_map.store import approach_nodes


def validation_errors(m: dict) -> list[str]:
    """Return human-readable blockers; empty list means confirm-ready."""
    errors: list[str] = []
    center = (m.get("center") or {}).get("text") or ""
    if len(center.strip()) < 10:
        errors.append("Problem needs at least 10 characters")
    approaches = approach_nodes(m)
    if len(approaches) != 3:
        errors.append(f"Need exactly 3 approaches (have {len(approaches)})")
    for i, a in enumerate(approaches, 1):
        trade = (a.get("tradeoff") or "").strip()
        if len(trade) < 5:
            errors.append(f"Approach {i} needs a tradeoff (≥5 chars)")
        if not (a.get("text") or "").strip():
            errors.append(f"Approach {i} needs text")
    if approaches and not any(a.get("recommended") for a in approaches):
        errors.append("Mark one approach recommended (r)")
    if m.get("status") == "confirmed":
        errors.append("Map already confirmed")
    return errors


def can_confirm(m: dict) -> bool:
    return not validation_errors(m)
