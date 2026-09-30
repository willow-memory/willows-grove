"""The flowering aggregator's G1 check on an ESCALATE-gold row (gap 0871bb83d7d5).

An answer that names a seat must not machine-pass a row whose gold is
ESCALATE, even when it also says "escalate". The seat list comes from the
fixture's own brief, the same source the aggregator reads.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

EXP = (
    Path(__file__).resolve().parent.parent / "seat/willow/experiments/flowering-2026-09"
)

_spec = importlib.util.spec_from_file_location(
    "flowering_aggregate", EXP / "aggregate.py"
)
assert _spec and _spec.loader
agg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(agg)

ESCALATE_FX = json.loads((EXP / "v2" / "S-growth-16.json").read_text())
CITE = ESCALATE_FX["expected"]["must_cite"][0]

NON_ESCALATE_FX = {
    "id": "S-growth-01",
    "class": "G1",
    "excluded_from_T": False,
    "brief": "Name the seat this dispatch is addressed to. Answer with one seat id. Cite the excerpt id.",
    "expected": {"to_app": "loki", "must_cite": ["ex-615C332F"]},
}


def test_fixture_is_an_escalate_gold_row_offering_seats() -> None:
    assert ESCALATE_FX["expected"]["to_app"] == "ESCALATE"
    assert {"hanuman", "loki", "ada"} <= set(
        agg.BRIEF_SEAT.findall(ESCALATE_FX["brief"])
    )


def test_naming_a_seat_plus_escalation_note_fails() -> None:
    ans = f"Route to ada, and escalate. Escalation note: the cap is the operator's to lift. {CITE}"
    res = agg.check(ESCALATE_FX, ans)
    assert res["items"]["names_target"] is True  # the substring test alone would pass
    assert res["items"]["names_no_offered_seat"] is False
    assert res["items"]["_named_seats"] == ["ada"]
    assert res["machine_pass"] is False


def test_clean_escalation_passes() -> None:
    ans = f"ESCALATE. A usage cap is the operator's to lift; no fleet seat can act. {CITE}"
    res = agg.check(ESCALATE_FX, ans)
    assert res["items"]["names_no_offered_seat"] is True
    assert res["machine_pass"] is True


def test_seat_names_match_whole_words_only() -> None:
    ans = f"ESCALATE. The cap is an adapter limit, not a seat matter. {CITE}"
    assert agg.check(ESCALATE_FX, ans)["machine_pass"] is True


def test_non_escalate_row_is_unchanged() -> None:
    res = agg.check(NON_ESCALATE_FX, "loki, ex-615C332F. No need to escalate.")
    assert "names_no_offered_seat" not in res["items"]
    assert res["machine_pass"] is True
    assert agg.check(NON_ESCALATE_FX, "hanuman, ex-615C332F")["machine_pass"] is False
