"""tests/test_card_store.py
b17: WGRV1  ΔΣ=42
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(autouse=True)
def soil_tmp(tmp_path, monkeypatch):
    monkeypatch.setenv("WILLOW_STORE_ROOT", str(tmp_path))


from widgets.card_store import (
    BUILTIN_CARDS,
    COLLECTION,
    load_cards,
    load_home_cards,
    reconcile_duplicates,
    save_card,
    seed_catalog,
    unique_card_id,
    validate_card_def,
)


def test_save_and_load_card():
    save_card({"id": "test-card", "label": "Test", "enabled": True, "order": 10})
    cards = load_cards()
    assert any(c["id"] == "test-card" for c in cards)


def test_load_cards_only_enabled():
    save_card({"id": "enabled-card", "label": "On", "enabled": True, "order": 1})
    save_card({"id": "disabled-card", "label": "Off", "enabled": False, "order": 2})
    ids = [c["id"] for c in load_cards()]
    assert "enabled-card" in ids
    assert "disabled-card" not in ids


def test_load_cards_sorted_by_order():
    save_card({"id": "c3", "label": "C", "enabled": True, "order": 30})
    save_card({"id": "c1", "label": "A", "enabled": True, "order": 10})
    save_card({"id": "c2", "label": "B", "enabled": True, "order": 20})
    ids = [c["id"] for c in load_cards()]
    assert ids.index("c1") < ids.index("c2") < ids.index("c3")


def test_seed_catalog_inserts_four():
    seed_catalog()
    import soil

    all_recs = soil.all_records(COLLECTION)
    ids = [r["id"] for r in all_recs]
    assert "git-status" in ids
    assert "open-prs" in ids
    assert "desk-todos" in ids
    assert "kart-tasks" in ids


def test_seed_catalog_inserts_upstream_inbox():
    seed_catalog()
    import soil

    rec = soil.get(COLLECTION, "upstream-inbox")
    assert rec is not None
    assert rec["nav_target"] == "#pane-upstream"


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
        if r["id"] in ("git-status", "open-prs", "desk-todos", "kart-tasks"):
            assert r["enabled"] is False


def test_save_card_upserts():
    save_card({"id": "my-card", "label": "Original", "enabled": True, "order": 1})
    save_card({"id": "my-card", "label": "Updated", "enabled": True, "order": 1})
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


def test_load_home_cards_includes_builtins():
    cards = load_home_cards()
    assert len(cards) >= len(BUILTIN_CARDS)
    assert cards[0]["id"] == "user-todos"


def test_unique_card_id_avoids_builtin_collision():
    assert unique_card_id("Tasks") == "tasks-2"


def test_load_home_cards_skips_catalog_duplicates():
    save_card({
        "id": "git-status",
        "label": "Git Status",
        "enabled": True,
        "order": 100,
        "nav_target": "#pane-git",
    })
    ids = [c["id"] for c in load_home_cards()]
    assert "git" in ids
    assert "git-status" not in ids


def test_reconcile_duplicates_disables_catalog_aliases():
    save_card({
        "id": "open-prs",
        "label": "Open PRs",
        "enabled": True,
        "order": 101,
        "nav_target": "#pane-prs",
    })
    reconcile_duplicates()
    import soil

    rec = soil.get(COLLECTION, "open-prs")
    assert rec is not None
    assert rec["enabled"] is False


def test_retired_welcome_card_not_on_home():
    save_card({"id": "welcome", "label": "Welcome, Sean", "enabled": True, "order": 1})
    reconcile_duplicates()
    ids = [c["id"] for c in load_home_cards()]
    assert "welcome" not in ids


def test_retired_grove_card_not_on_home():
    save_card({"id": "grove", "label": "Grove", "enabled": True, "order": 2})
    save_card({"id": "jeles", "label": "Jeles", "enabled": True, "order": 3})
    reconcile_duplicates()
    ids = [c["id"] for c in load_home_cards()]
    assert "grove" not in ids
    assert "jeles" in ids
