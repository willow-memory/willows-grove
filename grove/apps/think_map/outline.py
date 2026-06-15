"""grove/apps/think_map/outline.py — outline rows for Think Map pane.
b17: THNK1  ΔΣ=42
"""
from __future__ import annotations

from rich.markup import escape as _e

from grove.theme_textual import ACCENT, PRIMARY, SECONDARY


def outline_rows(m: dict) -> list[dict]:
    """Flat selectable rows: center, approaches, constraints, satellites."""
    rows: list[dict] = []
    center = m.get("center") or {}
    cid = center.get("id", "n0")
    rows.append({
        "id": cid,
        "kind": "problem",
        "depth": 0,
        "label": center.get("text") or "(problem)",
        "tradeoff": "",
        "recommended": False,
    })
    nodes = m.get("nodes") or []
    for n in nodes:
        kind = n.get("kind", "note")
        if kind == "approach":
            prefix = "★ " if n.get("recommended") else ""
            rows.append({
                "id": n.get("id", ""),
                "kind": kind,
                "depth": 1,
                "label": prefix + (n.get("text") or "(approach)"),
                "tradeoff": n.get("tradeoff") or "",
                "recommended": bool(n.get("recommended")),
            })
        elif kind == "constraint":
            rows.append({
                "id": n.get("id", ""),
                "kind": kind,
                "depth": 1,
                "label": "⛔ " + (n.get("text") or "(constraint)"),
                "tradeoff": "",
                "recommended": False,
            })
        elif kind == "satellite":
            pin = "● " if n.get("pinned") else "○ "
            rows.append({
                "id": n.get("id", ""),
                "kind": kind,
                "depth": 1,
                "label": pin + (n.get("text") or "(satellite)"),
                "tradeoff": "",
                "recommended": False,
            })
    return rows


def render_outline(m: dict, *, selected_id: str = "", errors: list[str] | None = None) -> str:
    lines: list[str] = []
    status = m.get("status", "draft")
    lines.append(f"[bold {ACCENT}]THINK MAP[/]  [dim {SECONDARY}]{status}[/]")
    problem = (m.get("center") or {}).get("text") or ""
    if problem:
        lines.append(f"[dim {SECONDARY}]Problem:[/] {_e(problem[:100])}")
    src = m.get("source") or {}
    if src.get("type") == "upstream" and src.get("ref"):
        lines.append(f"[dim {SECONDARY}]from upstream {_e(str(src['ref']))}[/]")
    lines.append("")
    for row in outline_rows(m):
        indent = "  " * row["depth"]
        rid = row["id"]
        sel = f"[reverse {ACCENT}]" if rid == selected_id else f"[{PRIMARY}]"
        end = "[/]" if rid == selected_id else "[/]"
        lines.append(f"{indent}{sel}{_e(row['label'])}{end}")
        if row.get("tradeoff"):
            lines.append(f"{indent}  [dim {SECONDARY}]Tradeoff: {_e(row['tradeoff'][:80])}[/]")
    lines.append("")
    if errors:
        lines.append(f"[bold]Confirm blocked:[/]")
        for e in errors:
            lines.append(f"  • {_e(e)}")
    else:
        lines.append(f"[dim {SECONDARY}]j/k move · Enter edit · n branch · c constraint · r recommend · d del · Ctrl-S save[/]")
    return "\n".join(lines)
