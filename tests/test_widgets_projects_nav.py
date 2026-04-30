"""tests/test_widgets_projects_nav.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from widgets.projects_nav import _fetch_nav_counts, _NavRefreshed

_ALL_IDS = ("tasks", "agents", "routing", "skills", "logs")


def test_fetch_returns_all_ids():
    result = _fetch_nav_counts()
    for cid in _ALL_IDS:
        assert cid in result, f"missing key: {cid}"


def test_fetch_values_are_strings():
    result = _fetch_nav_counts()
    for cid in _ALL_IDS:
        assert isinstance(result[cid]["count"], str), f"{cid}.count not str"
        assert isinstance(result[cid]["state"], str), f"{cid}.state not str"


def test_fetch_agents_fallback_on_failure(monkeypatch):
    import grove_reader
    def _fail(*args, **kwargs): raise RuntimeError("db down")
    monkeypatch.setattr(grove_reader, "grove_agents", _fail)
    result = _fetch_nav_counts()
    assert result["agents"]["count"] == "—"
    assert result["logs"]["count"] == "live"


def test_fetch_logs_always_live():
    result = _fetch_nav_counts()
    assert result["logs"]["count"] == "live"


def test_fetch_skills_missing_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    result = _fetch_nav_counts()
    assert result["skills"]["count"] == "—"


def test_fetch_skills_counts_md_files(tmp_path, monkeypatch):
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    skills_dir = tmp_path / ".willow" / "skills"
    skills_dir.mkdir(parents=True)
    (skills_dir / "a.md").write_text("skill a")
    (skills_dir / "b.md").write_text("skill b")
    (skills_dir / "ignore.txt").write_text("not a skill")
    result = _fetch_nav_counts()
    assert result["skills"]["count"] == "2"


def test_nav_refreshed_carries_data():
    data = {"tasks": {"count": "3", "state": "yellow"}}
    msg = _NavRefreshed(data)
    assert msg.data == data
