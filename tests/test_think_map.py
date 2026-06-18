"""tests/test_think_map.py — Think Map P0 store/validate + outline."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture(autouse=True)
def soil_tmp(tmp_path, monkeypatch):
    monkeypatch.setenv("WILLOW_STORE_ROOT", str(tmp_path))


from grove.apps.think_map import store, validate
from grove.apps.think_map.outline import render_outline


def test_validate_three_approaches():
    m = store.new_map(problem="How do stewards relate to cards?")
    m = store.add_approach(m, text="A", tradeoff="Simple nav")
    m = store.add_approach(m, text="B", tradeoff="Dense home")
    errs = validate.validation_errors(m)
    assert any("exactly 3" in e for e in errs)


def test_validate_recommendation():
    m = store.new_map(problem="Long enough problem here?")
    m = store.add_approach(m, text="A", tradeoff="Trade one")
    m = store.add_approach(m, text="B", tradeoff="Trade two")
    m = store.add_approach(m, text="C", tradeoff="Trade thr")
    errs = validate.validation_errors(m)
    assert any("recommended" in e for e in errs)


def test_validate_confirm_ready():
    m = store.new_map(problem="How do stewards relate to cards?")
    m = store.add_approach(m, text="Separate panes", tradeoff="More nav clicks")
    m = store.add_approach(m, text="Dots on Home", tradeoff="Dense layout")
    m = store.add_approach(m, text="Map only", tradeoff="Loses loop")
    m = store.set_recommended(m, store.approach_nodes(m)[0]["id"])
    assert validate.can_confirm(m)


def test_create_from_upstream():
    pending = {
        "work_id": "b17:UPST1-abc",
        "title": "DontFeedTheAI #5 review",
        "repo": "zeroc00I/DontFeedTheAI",
        "their_comment": "Nice clean slice",
        "open_questions": ["SSE boundary?"],
    }
    m = store.create_from_upstream(pending)
    assert m["source"]["type"] == "upstream"
    assert m["source"]["ref"] == "b17:UPST1-abc"
    assert "DontFeedTheAI" in m["center"]["text"]


def test_save_and_load_last_draft():
    m = store.new_map(problem="Draft problem statement here")
    store.save_map(m)
    loaded = store.load_last_draft()
    assert loaded is not None
    assert loaded["center"]["text"].startswith("Draft problem")


def test_render_outline_shows_problem():
    m = store.new_map(problem="Test problem long enough")
    text = render_outline(m)
    assert "THINK MAP[/]" in text
    assert "Test problem" in text
