#!/usr/bin/env python3
"""Deterministic reconcile for one-script predictions (no model).

Reads a predictions.json and lines each prediction up against its recorded
outcome. It never grades: the grade is a human-only act (truth rule; P3 adds
that the desk is a party to its wager, CONST §0.2). The script's only job is
the factual reconcile, and an honest ``escalate`` -- to the human, never to a
model -- when the record holds no outcome yet.

Contract for a graded prediction's ``outcome`` (written by a human or by a
deterministic experiment, never by this script):

  - distribution prediction: ``{"path_index": int}`` OR ``{"path": "<substr>"}``
    naming which ``distribution`` entry actually happened.
  - wager (``kind == "wager"``): ``{"winner": "operator"|"desk"|"split"|"void",
    "scores": {...}}`` -- produced by the deterministic experiment scores, not
    a model.

Top-level state (three-state, never collapsed):
  found       -- predictions read; each row reconciled or escalated
  unreachable -- predictions file missing or unreadable

Per-row state:
  reconciled  -- outcome present; lined up against the prediction
  escalate    -- no outcome: escalate to the human (never to a model for a grade)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

DEFAULT_PATH = Path(__file__).with_name("day-3") / "predictions.json"


def load_predictions(path):
    """Return the predictions list, or None if the file is unreachable."""
    p = Path(path)
    if not p.exists():
        return None
    with p.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError("predictions.json must be a JSON array")
    return data


def _match_distribution(pred, outcome):
    """Return (index, entry) of the distribution path the outcome names.

    (None, None) when the outcome names no entry.
    """
    dist = pred.get("distribution") or []
    if "path_index" in outcome:
        i = outcome["path_index"]
        if isinstance(i, int) and 0 <= i < len(dist):
            return i, dist[i]
        return None, None
    needle = (outcome.get("path") or "").strip().lower()
    if needle:
        for i, entry in enumerate(dist):
            if needle in (entry.get("path") or "").lower():
                return i, entry
    return None, None


def reconcile_one(pred):
    """Reconcile one prediction. Never sets a grade."""
    row = {
        "id": pred.get("id", "?"),
        "kind": pred.get("kind", "distribution"),
        "graded_by": None,  # a grade is a human act; this script never sets it
    }
    outcome = pred.get("outcome")
    if outcome is None:
        row["state"] = "escalate"
        row["escalate_to"] = "human"
        row["reason"] = (
            "no recorded outcome; the grade is the operator's"
            " (CONST §0.2 for the wager)"
        )
        return row
    if pred.get("kind") == "wager":
        row["state"] = "reconciled"
        row["winner"] = outcome.get("winner")
        row["scores"] = outcome.get("scores")
        row["note"] = (
            "winner read from the deterministic scores;"
            " the grade is still the operator's"
        )
        return row
    idx, entry = _match_distribution(pred, outcome)
    if entry is None:
        row["state"] = "escalate"
        row["escalate_to"] = "human"
        row["reason"] = "outcome does not name any distribution path"
        return row
    row["state"] = "reconciled"
    row["path_index"] = idx
    row["predicted_p"] = entry.get("p")
    row["predicted_band"] = entry.get("band")
    row["actual_path"] = entry.get("path")
    return row


def reconcile_all(path=DEFAULT_PATH):
    """Reconcile every prediction in the file against its recorded outcome."""
    preds = load_predictions(path)
    if preds is None:
        return {
            "state": "unreachable",
            "path": str(path),
            "reason": "predictions file not found",
        }
    rows = [reconcile_one(p) for p in preds]
    escalated = [r["id"] for r in rows if r["state"] == "escalate"]
    return {
        "state": "found",
        "path": str(path),
        "count": len(rows),
        "reconciled": [r["id"] for r in rows if r["state"] == "reconciled"],
        "escalate": escalated,
        "escalate_to": "human" if escalated else None,
        "rows": rows,
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    path = Path(argv[0]) if argv else DEFAULT_PATH
    print(json.dumps(reconcile_all(path), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
