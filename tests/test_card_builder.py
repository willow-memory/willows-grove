"""tests/test_card_builder.py — scripted wizard + templates."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(autouse=True)
def soil_tmp(tmp_path, monkeypatch):
    monkeypatch.setenv("WILLOW_STORE_ROOT", str(tmp_path))


import soil
from grove.apps.card_builder.templates import enable_catalog_card, make_nav_card, make_soil_count_card
from grove.apps.card_builder.values import resolve_subtitle
from grove.apps.card_builder.wizard import WizardMode, WizardState, commit_state, validate_state
from widgets.card_store import COLLECTION, seed_catalog


def test_enable_catalog_card():
    seed_catalog()
    saved = enable_catalog_card("git-status")
    assert saved is None


def test_enable_catalog_card_allows_custom():
    seed_catalog()
    soil.put("willow-dashboard/cards", "custom-link", {
        "id": "custom-link",
        "label": "Custom",
        "enabled": False,
        "nav_target": "help",
        "order": 200,
    })
    saved = enable_catalog_card("custom-link")
    assert saved is not None
    assert saved["enabled"] is True


def test_make_soil_count_card():
    soil.put("willow-dashboard/todos", "t1", {"text": "one"})
    saved = make_soil_count_card(
        collection="willow-dashboard/todos",
        label="My Todos",
    )
    assert saved is not None
    assert saved["value_source"]["type"] == "soil_count"
    assert resolve_subtitle(saved) == "1 item"


def test_make_nav_card():
    saved = make_nav_card(label="Chat", nav_target="chat", subtitle="messages")
    assert saved is not None
    assert saved["nav_target"] == "chat"
    assert saved.get("value_source") is None


def test_wizard_commit_catalog_rejects_builtin_duplicate():
    seed_catalog()
    state = WizardState(mode=WizardMode.CATALOG, catalog_id="open-prs")
    card = commit_state(state)
    assert card is None
    assert state.errors


def test_wizard_validate_missing_mode():
    state = WizardState()
    errors = validate_state(state)
    assert errors


def test_wizard_commit_soil_count():
    soil.put("demo/items", "a", {"n": 1})
    state = WizardState(
        mode=WizardMode.SOIL_COUNT,
        collection="demo/items",
        label="Items",
        link_nav=True,
        nav_target="help",
    )
    card = commit_state(state)
    assert card is not None
    rows = soil.all_records(COLLECTION)
    assert any(r["id"] == card["id"] for r in rows)
