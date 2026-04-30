"""tests/test_panes_home.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from panes.home import (
    DeskData, agent_dot, format_age, mini_bar,
    HomeGrid, ProjectsGrid,
)

# ── DeskData ──────────────────────────────────────────────────────────────────

def test_desk_data_defaults():
    d = DeskData()
    assert d.unread_channels == []
    assert d.mentions == []
    assert d.open_flags == 0
    assert d.running_tasks == 0
    assert d.pending_tasks == 0
    assert d.done_today == 0
    assert d.backfill is None
    assert d.agents == []
    assert d.sysinfo == {"cpu": 0, "mem": 0, "disk": 0, "temp": 0}

def test_desk_data_custom():
    d = DeskData(running_tasks=3, pending_tasks=7)
    assert d.running_tasks == 3
    assert d.pending_tasks == 7

# ── agent_dot ─────────────────────────────────────────────────────────────────

def test_agent_dot_green():
    assert "[green]" in agent_dot(60)

def test_agent_dot_yellow():
    assert "[yellow]" in agent_dot(300)

def test_agent_dot_dim():
    assert "[dim]" in agent_dot(1000)

# ── format_age ────────────────────────────────────────────────────────────────

def test_format_age_minutes():
    assert format_age(90) == "1m ago"

def test_format_age_hours():
    assert format_age(7200) == "2h ago"

def test_format_age_zero():
    assert format_age(0) == "0m ago"

# ── mini_bar ──────────────────────────────────────────────────────────────────

def test_mini_bar_full():
    assert mini_bar(100) == "█████"

def test_mini_bar_empty():
    assert mini_bar(0) == "░░░░░"

def test_mini_bar_half():
    result = mini_bar(50)
    assert "██" in result
    assert "░░" in result
    assert len(result) == 5

# ── placeholder strings still present ────────────────────────────────────────

def test_homegrid_is_container():
    from textual.containers import Container
    assert issubclass(HomeGrid, Container)

def test_projectsgrid_is_container():
    from textual.containers import Container
    assert issubclass(ProjectsGrid, Container)


# ── render_desk sections ──────────────────────────────────────────────────────
from panes.home import render_desk

def test_render_desk_running_always_present():
    d = DeskData()
    out = render_desk(d)
    assert "RUNNING" in out

def test_render_desk_system_always_present():
    d = DeskData()
    out = render_desk(d)
    assert "SYSTEM" in out

def test_render_desk_attention_absent_when_empty():
    d = DeskData()
    out = render_desk(d)
    assert "ATTENTION" not in out

def test_render_desk_attention_present_with_unread():
    d = DeskData(unread_channels=[{"name": "general", "unread": 3}])
    out = render_desk(d)
    assert "ATTENTION" in out
    assert "general" in out
    assert "3" in out

def test_render_desk_attention_present_with_flags():
    d = DeskData(open_flags=2)
    out = render_desk(d)
    assert "ATTENTION" in out
    assert "2" in out
    assert "flags" in out

def test_render_desk_attention_present_with_mention():
    d = DeskData(mentions=[{"channel": "general", "sender": "hanuman", "snippet": "hey @sean"}])
    out = render_desk(d)
    assert "ATTENTION" in out
    assert "hanuman" in out

def test_render_desk_idle_when_no_tasks():
    d = DeskData(running_tasks=0, pending_tasks=0)
    out = render_desk(d)
    assert "idle" in out.lower()

def test_render_desk_task_counts():
    d = DeskData(running_tasks=2, pending_tasks=5)
    out = render_desk(d)
    assert "2" in out
    assert "5" in out

def test_render_desk_backfill_bar():
    d = DeskData(backfill={"pct": 80, "table": "embeddings"})
    out = render_desk(d)
    assert "embed" in out
    assert "80" in out

def test_render_desk_done_today_absent_when_zero():
    d = DeskData(done_today=0)
    out = render_desk(d)
    assert "DONE" not in out

def test_render_desk_done_today_present():
    d = DeskData(done_today=3)
    out = render_desk(d)
    assert "DONE" in out
    assert "3" in out

def test_render_desk_agent_line():
    d = DeskData(agents=[{"sender": "hanuman", "age_secs": 60}])
    out = render_desk(d)
    assert "hanuman" in out

def test_render_desk_no_agents():
    d = DeskData(agents=[])
    out = render_desk(d)
    assert "no agents" in out

def test_render_desk_cpu_mem():
    d = DeskData(sysinfo={"cpu": 12, "mem": 44, "disk": 30, "temp": 0})
    out = render_desk(d)
    assert "12" in out
    assert "44" in out

def test_render_desk_temp_absent_when_zero():
    d = DeskData(sysinfo={"cpu": 10, "mem": 20, "disk": 30, "temp": 0})
    out = render_desk(d)
    assert "temp" not in out.lower()

def test_render_desk_temp_present_when_set():
    d = DeskData(sysinfo={"cpu": 10, "mem": 20, "disk": 30, "temp": 55})
    out = render_desk(d)
    assert "55" in out

def test_render_desk_is_string():
    assert isinstance(render_desk(DeskData()), str)


# ── fetch_desk_data ────────────────────────────────────────────────────────────
from panes.home import fetch_desk_data

def test_fetch_desk_data_returns_desk_data():
    """fetch_desk_data must return DeskData even when all sources fail."""
    result = fetch_desk_data("sean")
    assert isinstance(result, DeskData)
    assert isinstance(result.unread_channels, list)
    assert isinstance(result.agents, list)
    assert isinstance(result.sysinfo, dict)
    assert isinstance(result.running_tasks, int)
    assert isinstance(result.done_today, int)
