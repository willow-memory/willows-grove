"""tests/test_widgets_command_provider.py
b17: WGRV1  ΔΣ=42
"""
from widgets.command_provider import _nav_hits, _action_hits, _channel_hits


def test_nav_hits_returns_eight():
    assert len(_nav_hits()) == 8


def test_nav_hits_have_required_keys():
    for hit in _nav_hits():
        assert "display" in hit
        assert "text" in hit
        assert "target" in hit


def test_nav_hits_include_home_and_help():
    targets = [h["target"] for h in _nav_hits()]
    assert "home" in targets
    assert "help" in targets


def test_action_hits_have_required_keys():
    for hit in _action_hits():
        assert "display" in hit
        assert "text" in hit
        assert "action" in hit


def test_action_hits_include_refresh_and_quit():
    actions = [h["action"] for h in _action_hits()]
    assert "refresh" in actions
    assert "quit" in actions


def test_channel_hits_returns_channels():
    channels = [{"name": "general"}, {"name": "architecture"}]
    hits = _channel_hits(lambda: channels)
    assert len(hits) == 2


def test_channel_hit_display_format():
    hits = _channel_hits(lambda: [{"name": "general"}])
    assert hits[0]["display"] == "Open #general"


def test_channel_hit_text_contains_name():
    hits = _channel_hits(lambda: [{"name": "general"}])
    assert "general" in hits[0]["text"]


def test_channel_hit_has_channel_key():
    hits = _channel_hits(lambda: [{"name": "general"}])
    assert hits[0]["channel"] == "general"


def test_channel_hits_empty_on_exception():
    def bad():
        raise RuntimeError("db down")
    assert _channel_hits(bad) == []
