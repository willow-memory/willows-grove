"""Tests for the deterministic prediction reconcile (no model).

The reconcile never grades; it lines a prediction up against its recorded
outcome and escalates to the human when there is none. These tests pin that:
a null outcome escalates to the human, a matched outcome reports the band and
probability, and the script never writes ``graded_by``.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import reconcile  # noqa: E402


def _write(tmp_path, preds):
    p = tmp_path / "predictions.json"
    p.write_text(json.dumps(preds), encoding="utf-8")
    return p


def test_null_outcome_escalates_to_human(tmp_path):
    p = _write(
        tmp_path,
        [
            {
                "id": "P1",
                "distribution": [{"path": "the close", "p": 0.55, "band": "likely"}],
                "outcome": None,
            }
        ],
    )
    out = reconcile.reconcile_all(p)
    assert out["state"] == "found"
    assert out["escalate"] == ["P1"]
    assert out["escalate_to"] == "human"  # never a model for a grade
    row = out["rows"][0]
    assert row["state"] == "escalate"
    assert row["escalate_to"] == "human"
    assert row["graded_by"] is None


def test_matched_outcome_reconciles_band(tmp_path):
    p = _write(
        tmp_path,
        [
            {
                "id": "P1",
                "distribution": [
                    {"path": "the close", "p": 0.55, "band": "likely"},
                    {"path": "the pile after the session", "p": 0.25, "band": "middle"},
                ],
                "outcome": {"path_index": 1},
            }
        ],
    )
    row = reconcile.reconcile_all(p)["rows"][0]
    assert row["state"] == "reconciled"
    assert row["predicted_band"] == "middle"  # mutation target
    assert row["predicted_p"] == 0.25
    assert row["graded_by"] is None  # the script never grades


def test_match_by_substring(tmp_path):
    p = _write(
        tmp_path,
        [
            {
                "id": "P2",
                "distribution": [
                    {
                        "path": "the Kaggle work: day-two run",
                        "p": 0.45,
                        "band": "likely",
                    },
                ],
                "outcome": {"path": "kaggle"},
            }
        ],
    )
    row = reconcile.reconcile_all(p)["rows"][0]
    assert row["state"] == "reconciled"
    assert row["path_index"] == 0


def test_wager_without_scores_escalates(tmp_path):
    p = _write(tmp_path, [{"id": "P3", "kind": "wager", "outcome": None}])
    row = reconcile.reconcile_all(p)["rows"][0]
    assert row["state"] == "escalate"
    assert row["escalate_to"] == "human"


def test_outcome_naming_no_path_escalates(tmp_path):
    p = _write(
        tmp_path,
        [
            {
                "id": "P1",
                "distribution": [{"path": "the close", "p": 0.55, "band": "likely"}],
                "outcome": {"path": "something that does not exist"},
            }
        ],
    )
    row = reconcile.reconcile_all(p)["rows"][0]
    assert row["state"] == "escalate"


def test_missing_file_is_unreachable(tmp_path):
    out = reconcile.reconcile_all(tmp_path / "nope.json")
    assert out["state"] == "unreachable"
