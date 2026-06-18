"""grove/apps/think_map/store.py — SOIL CRUD for Think Map drafts.
b17: THNK1  ΔΣ=42
"""
from __future__ import annotations

import re
import uuid
from datetime import datetime

import soil

COLLECTION = "willow-dashboard/think_maps"
ACTIVE_COLLECTION = "willow-dashboard/think_map_active"
ACTIVE_RECORD = "current"


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _map_id() -> str:
    return f"b17:THNK1-{uuid.uuid4().hex[:8]}"


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:48] or "map"


def new_map(*, problem: str = "", source: dict | None = None, created_by: str = "user") -> dict:
    """Empty draft map with center node."""
    ts = _now()
    center_id = "n0"
    return {
        "id": _map_id(),
        "status": "draft",
        "created_at": ts,
        "updated_at": ts,
        "created_by": created_by,
        "source": source or {"type": "manual", "ref": ""},
        "center": {"id": center_id, "text": problem.strip(), "kind": "problem"},
        "nodes": [],
        "confirmed_at": None,
        "confirmed_choice": None,
        "exports": [],
    }


def save_map(m: dict) -> dict:
    m = dict(m)
    m["updated_at"] = _now()
    map_id = m.get("id") or _map_id()
    m["id"] = map_id
    soil.put(COLLECTION, map_id, m)
    return m


def load_map(map_id: str) -> dict | None:
    rec = soil.get(COLLECTION, map_id)
    if rec is None:
        return None
    if "id" not in rec:
        rec["id"] = map_id
    return rec


def set_active_map(map_id: str) -> None:
    soil.put(ACTIVE_COLLECTION, ACTIVE_RECORD, {"map_id": map_id})


def load_active_map() -> dict | None:
    rec = soil.get(ACTIVE_COLLECTION, ACTIVE_RECORD)
    if not rec or not rec.get("map_id"):
        return None
    return load_map(str(rec["map_id"]))


def load_last_draft() -> dict | None:
    drafts: list[dict] = []
    try:
        for rec in soil.all_records(COLLECTION):
            if rec.get("status", "draft") == "draft":
                drafts.append(rec)
    except Exception:
        return None
    if not drafts:
        return None
    drafts.sort(key=lambda r: r.get("updated_at") or r.get("created_at") or "", reverse=True)
    m = drafts[0]
    if "id" not in m and "_id" in m:
        m["id"] = m["_id"]
    return m


def _next_node_id(m: dict) -> str:
    ids = {m.get("center", {}).get("id", "n0")}
    for n in m.get("nodes") or []:
        ids.add(n.get("id", ""))
    n = 1
    while f"n{n}" in ids:
        n += 1
    return f"n{n}"


def approach_nodes(m: dict) -> list[dict]:
    return [n for n in m.get("nodes") or [] if n.get("kind") == "approach"]


def add_approach(m: dict, *, text: str = "", tradeoff: str = "") -> dict:
    m = dict(m)
    nodes = list(m.get("nodes") or [])
    nodes.append({
        "id": _next_node_id({**m, "nodes": nodes}),
        "parent": m["center"]["id"],
        "kind": "approach",
        "text": text,
        "tradeoff": tradeoff,
        "recommended": False,
    })
    m["nodes"] = nodes
    return m


def add_constraint(m: dict, *, text: str, hard: bool = True) -> dict:
    m = dict(m)
    nodes = list(m.get("nodes") or [])
    nodes.append({
        "id": _next_node_id({**m, "nodes": nodes}),
        "parent": m["center"]["id"],
        "kind": "constraint",
        "text": text,
        "hard": hard,
    })
    m["nodes"] = nodes
    return m


def add_satellite(m: dict, *, text: str, ref: dict | None = None) -> dict:
    m = dict(m)
    nodes = list(m.get("nodes") or [])
    nodes.append({
        "id": _next_node_id({**m, "nodes": nodes}),
        "parent": None,
        "kind": "satellite",
        "text": text,
        "ref": ref or {},
        "pinned": True,
    })
    m["nodes"] = nodes
    return m


def set_recommended(m: dict, node_id: str) -> dict:
    m = dict(m)
    nodes = []
    for n in m.get("nodes") or []:
        n = dict(n)
        if n.get("kind") == "approach":
            n["recommended"] = n.get("id") == node_id
        nodes.append(n)
    m["nodes"] = nodes
    return m


def update_node_text(m: dict, node_id: str, *, text: str = "", tradeoff: str | None = None) -> dict:
    m = dict(m)
    if m.get("center", {}).get("id") == node_id:
        center = dict(m["center"])
        if text:
            center["text"] = text
        m["center"] = center
        return m
    nodes = []
    for n in m.get("nodes") or []:
        n = dict(n)
        if n.get("id") == node_id:
            if text:
                n["text"] = text
            if tradeoff is not None:
                n["tradeoff"] = tradeoff
        nodes.append(n)
    m["nodes"] = nodes
    return m


def delete_node(m: dict, node_id: str) -> dict:
    if m.get("center", {}).get("id") == node_id:
        return m
    m = dict(m)
    m["nodes"] = [n for n in m.get("nodes") or [] if n.get("id") != node_id]
    return m


def create_from_upstream(pending: dict) -> dict:
    """Bridge: steward draft → think map draft."""
    title = (
        pending.get("title")
        or pending.get("subject")
        or pending.get("repo")
        or "Upstream thread"
    )
    work_id = pending.get("work_id") or pending.get("_id") or pending.get("id") or ""
    m = new_map(
        problem=f"Decide how to respond: {title}"[:200],
        source={"type": "upstream", "ref": str(work_id)},
    )
    if pending.get("url"):
        m = add_satellite(m, text=str(pending.get("url"))[:80], ref={"type": "url", "id": pending["url"]})
    for bit in (pending.get("fun_bits") or pending.get("open_questions") or [])[:3]:
        m = add_constraint(m, text=str(bit)[:120], hard=False)
    if pending.get("their_comment"):
        m = add_satellite(m, text=str(pending["their_comment"])[:120], ref={"type": "comment"})
    return save_map(m)
