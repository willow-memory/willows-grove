"""grove/apps/user_board.py — aggregate user desk items from SOIL + Grove + Kart.
b17: WDASH  ΔΣ=42
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any

import soil

TODOS_COLLECTION = "willow-dashboard/todos"
PROJECTS_COLLECTION = "willow-dashboard/projects"


def _parse_date(raw: str | None) -> date | None:
    if not raw:
        return None
    text = str(raw).strip()[:10]
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def _due_label(d: date | None, *, today: date | None = None) -> tuple[str, str]:
    """Return (display_date, urgency) where urgency is overdue|soon|ok|none."""
    if d is None:
        return "", "none"
    today = today or date.today()
    display = d.isoformat()
    if d < today:
        return display, "overdue"
    if (d - today).days <= 3:
        return display, "soon"
    return display, "ok"


def fetch_user_board(*, limit: int = 80) -> dict[str, Any]:
    """Unified desk snapshot — never raises."""
    today = date.today()
    items: list[dict[str, Any]] = []
    projects_by_name: dict[str, dict] = {}

    try:
        for rec in soil.all_records(PROJECTS_COLLECTION):
            name = str(rec.get("name") or "").strip()
            if name:
                projects_by_name[name.lower()] = rec
    except Exception:
        pass

    open_todos = 0
    overdue = 0
    try:
        for rec in soil.all_records(TODOS_COLLECTION):
            if rec.get("done"):
                continue
            open_todos += 1
            project = str(rec.get("project") or "").strip()
            due = _parse_date(rec.get("due_date"))
            due_s, urgency = _due_label(due, today=today)
            if urgency == "overdue":
                overdue += 1
            items.append({
                "kind": "todo",
                "id": rec.get("_id", ""),
                "title": str(rec.get("text") or "").strip() or "(untitled)",
                "project": project,
                "due_date": due_s,
                "urgency": urgency,
                "atom_id": str(rec.get("atom_id") or "").strip(),
                "notes": str(rec.get("notes") or "").strip(),
                "source": "todos",
                "sort_date": due or date.max,
            })
    except Exception:
        pass

    active_projects = 0
    try:
        for rec in soil.all_records(PROJECTS_COLLECTION):
            if rec.get("status", "active") != "active":
                continue
            active_projects += 1
            name = str(rec.get("name") or "").strip()
            due = _parse_date(rec.get("due_date"))
            due_s, urgency = _due_label(due, today=today)
            if urgency == "overdue":
                overdue += 1
            items.append({
                "kind": "project",
                "id": rec.get("_id", ""),
                "title": name or "(unnamed project)",
                "project": name,
                "due_date": due_s,
                "urgency": urgency,
                "atom_id": str(rec.get("atom_id") or "").strip(),
                "notes": str(rec.get("notes") or "").strip(),
                "source": "projects",
                "sort_date": due or date.max,
            })
    except Exception:
        pass

    try:
        from panes.tasks import fetch_tasks

        task_data = fetch_tasks()
        for row in task_data.get("rows", [])[:8]:
            if str(row.get("status", "")).lower() != "running":
                continue
            items.append({
                "kind": "task",
                "id": str(row.get("id", "")),
                "title": str(row.get("cmd") or "")[:72],
                "project": "kart",
                "due_date": str(row.get("ts") or "")[:16],
                "urgency": "ok",
                "atom_id": "",
                "notes": str(row.get("status") or ""),
                "source": "tasks",
                "sort_date": date.max,
            })
    except Exception:
        pass

    urgency_rank = {"overdue": 0, "soon": 1, "ok": 2, "none": 3}

    def _sort_key(item: dict) -> tuple:
        return (
            urgency_rank.get(item.get("urgency", "none"), 9),
            item.get("sort_date") or date.max,
            item.get("kind", ""),
            item.get("title", "").lower(),
        )

    items.sort(key=_sort_key)
    items = items[:limit]

    atom_ids = {i["atom_id"] for i in items if i.get("atom_id")}
    atoms: dict[str, dict] = {}
    if atom_ids:
        try:
            from panes.knowledge import fetch_atom

            for aid in atom_ids:
                atom = fetch_atom(aid)
                if atom:
                    atoms[aid] = atom
        except Exception:
            pass

    return {
        "items": items,
        "open_todos": open_todos,
        "active_projects": active_projects,
        "overdue": overdue,
        "atoms": atoms,
        "projects": list(projects_by_name.values()),
        "as_of": datetime.now().isoformat(timespec="seconds"),
    }


def board_summary(board: dict | None = None) -> str:
    data = board or fetch_user_board(limit=1)
    open_todos = data.get("open_todos", 0)
    overdue = data.get("overdue", 0)
    projects = data.get("active_projects", 0)
    if overdue:
        return f"{open_todos} open · {overdue} overdue"
    if open_todos or projects:
        return f"{open_todos} todos · {projects} projects"
    return "your command center"
