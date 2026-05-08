"""tests/test_widgets_card_grid.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from widgets.card_grid import (
    _STATE_COLORS, _CARD_NAV, BUILTIN_CARDS, LAUNCHER_CARDS,
    fetch_runtime_card_values,
)

# ── constants ─────────────────────────────────────────────────────────────────

def test_state_colors_has_required_keys():
    for key in ("green", "amber", "red", "blue", "yellow", "dim", ""):
        assert key in _STATE_COLORS

def test_card_nav_covers_all_builtin_ids():
    builtin_ids = {cid for cid, _ in BUILTIN_CARDS}
    for cid in builtin_ids:
        assert cid in _CARD_NAV

def test_builtin_cards_has_seven():
    assert len(BUILTIN_CARDS) == 7

def test_launcher_cards_has_seven():
    assert len(LAUNCHER_CARDS) == 7

def test_launcher_cards_all_have_nav():
    for _, _, nav in LAUNCHER_CARDS:
        assert nav.startswith("#pane-")

# ── fetch_runtime_card_values ─────────────────────────────────────────────────

def test_fetch_returns_dict_for_all_builtin_ids():
    result = fetch_runtime_card_values()
    builtin_ids = {cid for cid, _ in BUILTIN_CARDS}
    for cid in builtin_ids:
        assert cid in result

def test_fetch_values_are_strings():
    result = fetch_runtime_card_values()
    for cid, data in result.items():
        assert isinstance(data["value"], str), f"{cid}.value is not str"
        assert isinstance(data["sub"], str), f"{cid}.sub is not str"
        assert isinstance(data["state"], str), f"{cid}.state is not str"

def test_fetch_does_not_raise():
    """Must return safe defaults even when all sources fail."""
    result = fetch_runtime_card_values()
    assert isinstance(result, dict)

def test_fetch_yggdrasil_reads_env(monkeypatch):
    monkeypatch.setenv("WILLOW_MODEL", "claude-test-model")
    result = fetch_runtime_card_values()
    assert result["yggdrasil"]["value"] == "claude-test-model"
    assert result["yggdrasil"]["sub"] == "active model"

def test_fetch_fleet_counts_key_vars(monkeypatch):
    monkeypatch.setenv("WILLOW_ANTHROPIC_KEY", "sk-test-1")
    monkeypatch.setenv("WILLOW_OPENAI_KEY", "sk-test-2")
    result = fetch_runtime_card_values()
    assert int(result["fleet"]["value"]) >= 2
    assert result["fleet"]["sub"] == "api keys"

def test_fetch_secrets_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    result = fetch_runtime_card_values()
    assert result["secrets"]["value"] == "—"
    assert result["secrets"]["sub"] == "vault"

def test_fetch_secrets_reads_file(tmp_path, monkeypatch):
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    willow_dir = tmp_path / ".willow"
    willow_dir.mkdir()
    (willow_dir / "secrets.json").write_text('{"KEY_A": "val1", "KEY_B": "val2"}')
    result = fetch_runtime_card_values()
    assert result["secrets"]["value"] == "2"

def test_fetch_mcp_reads_file(tmp_path, monkeypatch):
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    mcp = {"mcpServers": {"willow": {}, "grove": {}}}
    import json
    (tmp_path / ".mcp.json").write_text(json.dumps(mcp))
    result = fetch_runtime_card_values()
    assert result["mcp"]["value"] == "2"


# ── CardActivated ─────────────────────────────────────────────────────────────
from widgets.card_grid import CardActivated

def test_card_activated_fields():
    msg = CardActivated("kart", "#pane-tasks")
    assert msg.card_id == "kart"
    assert msg.nav_target == "#pane-tasks"

def test_card_activated_empty_nav():
    msg = CardActivated("secrets", "")
    assert msg.nav_target == ""

def test_card_activated_content_nav():
    msg = CardActivated("knowledge", "knowledge")
    assert msg.nav_target == "knowledge"
