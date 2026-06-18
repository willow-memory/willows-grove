"""grove/apps/upstream_steward.py — read-only consumer for Upstream Steward (2.0 writes).
b17: WGRV1  ΔΣ=42

SOIL layout (written by willow-2.0 agents/hanuman upstream steward):
  upstream_steward/pending/{work_id}  — draft awaiting human
  upstream_steward/digest/latest        — daily brief

See: willow-2.0/docs/superpowers/specs/2026-05-24-upstream-steward-design.md
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import soil

PENDING_COLLECTION = "upstream_steward/pending"
DIGEST_COLLECTION = "upstream_steward/digest"
DIGEST_RECORD_ID = "latest"
CURSOR_FILE = Path.home() / ".willow" / "upstream_steward" / "cursor.json"


def _record_id(rec: dict) -> str:
    return str(rec.get("work_id") or rec.get("id") or rec.get("_id") or "")


def _load_cursor() -> dict:
    try:
        if CURSOR_FILE.exists():
            return json.loads(CURSOR_FILE.read_text())
    except Exception:
        pass
    return {}


def list_pending() -> list[dict]:
    """Pending drafts needing human approval — sorted urgent first."""
    rows: list[dict] = []
    try:
        for rec in soil.all_records(PENDING_COLLECTION):
            status = str(rec.get("status") or "awaiting_human")
            if status in ("posted", "closed", "skipped"):
                continue
            rows.append(rec)
    except Exception:
        return []
    rows.sort(
        key=lambda r: (
            0 if r.get("lane") == "urgent" else 1,
            str(r.get("updated_at") or r.get("created_at") or ""),
        )
    )
    return rows


def fetch_digest() -> dict | None:
    try:
        return soil.get(DIGEST_COLLECTION, DIGEST_RECORD_ID)
    except Exception:
        return None


def fetch_status() -> dict[str, Any]:
    """Dashboard-safe status snapshot — never raises."""
    pending = list_pending()
    urgent = sum(1 for p in pending if p.get("lane") == "urgent")
    cursor = _load_cursor()
    digest = fetch_digest() or {}
    return {
        "pending_count": len(pending),
        "urgent_count": urgent,
        "last_poll": cursor.get("last_poll"),
        "last_tracker_run": cursor.get("last_tracker_run"),
        "digest_line": str(digest.get("line") or digest.get("summary") or "").strip(),
        "as_of": datetime.now().isoformat(timespec="seconds"),
    }


def steward_summary() -> str:
    """One-line stat for My Desk / home subline."""
    status = fetch_status()
    n = status.get("pending_count", 0)
    if not n:
        return ""
    urgent = status.get("urgent_count", 0)
    if urgent:
        return f"{n} upstream · {urgent} urgent"
    return f"{n} upstream draft{'s' if n != 1 else ''}"


def pending_preview(limit: int = 8) -> list[dict]:
    """Trimmed rows for UI tables."""
    out: list[dict] = []
    for rec in list_pending()[:limit]:
        out.append({
            "work_id": _record_id(rec),
            "repo": rec.get("repo") or "",
            "kind": rec.get("kind") or rec.get("post_target") or "thread",
            "title": (rec.get("title") or rec.get("subject") or _record_id(rec))[:60],
            "lane": rec.get("lane") or "draft",
            "status": rec.get("status") or "awaiting_human",
            "url": rec.get("url") or "",
        })
    return out
