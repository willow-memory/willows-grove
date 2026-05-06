"""tests/test_card_store.py
b17: WGRV1  ΔΣ=42
"""
import os
import pytest


@pytest.fixture(autouse=True)
def soil_tmp(tmp_path, monkeypatch):
    monkeypatch.setenv("WILLOW_STORE_ROOT", str(tmp_path))


from widgets.card_store import (
    load_cards, save_card, seed_catalog, validate_card_def, COLLECTION
)


def test_save_and_load_card():
    save_card({"id": "test-card", "label": "Test", "enabled": True, "order": 10})
    cards = load_cards()
    assert any(c["id"] == "test-card" for c in cards)


def test_load_cards_only_enabled():
    save_card({"id": "enabled-card",  "label": "On",  "enabled": True,  "order": 1})
    save_card({"id": "disabled-card", "label": "Off", "enabled": False, "order": 2})
    ids = [c["id"] for c in load_cards()]
    assert "enabled-card"  in ids
    assert "disabled-card" not in ids


def test_load_cards_sorted_by_order():
    save_card({"id": "c3", "label": "C", "enabled": True, "order": 30})
    save_card({"id": "c1", "label": "A", "enabled": True, "order": 10})
    save_card({"id": "c2", "label": "B", "enabled": True, "order": 20})
    ids = [c["id"] for c in load_cards()]
    assert ids.index("c1") < ids.index("c2") < ids.index("c3")


def test_seed_catalog_inserts_two():
    seed_catalog()
    import soil
    all_recs = soil.all_records(COLLECTION)
    ids = [r["id"] for r in all_recs]
    assert "git-status" in ids
    assert "open-prs"   in ids


def test_seed_catalog_idempotent():
    seed_catalog()
    seed_catalog()
    import soil
    all_recs = soil.all_records(COLLECTION)
    git_recs = [r for r in all_recs if r["id"] == "git-status"]
    assert len(git_recs) == 1


def test_seed_catalog_inserts_disabled():
    seed_catalog()
    import soil
    all_recs = soil.all_records(COLLECTION)
    for r in all_recs:
        if r["id"] in ("git-status", "open-prs", "build", "todos"):
            assert r["enabled"] is False


def test_save_card_upserts():
    save_card({"id": "my-card", "label": "Original", "enabled": True, "order": 1})
    save_card({"id": "my-card", "label": "Updated",  "enabled": True, "order": 1})
    cards = [c for c in load_cards() if c["id"] == "my-card"]
    assert len(cards) == 1
    assert cards[0]["label"] == "Updated"


def test_validate_card_def_rejects_missing_id():
    assert validate_card_def({"label": "No ID"}) is None


def test_validate_card_def_rejects_missing_label():
    assert validate_card_def({"id": "no-label"}) is None


def test_validate_card_def_defaults_order():
    card = validate_card_def({"id": "x", "label": "X"})
    assert card is not None
    assert card["order"] == 50


def test_validate_card_def_defaults_enabled():
    card = validate_card_def({"id": "x", "label": "X"})
    assert card is not None
    assert card["enabled"] is True
