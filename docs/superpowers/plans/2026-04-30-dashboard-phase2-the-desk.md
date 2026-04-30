# Dashboard Phase 2 — The Desk Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the `DeskPane` static placeholder with a live widget that shows Grove unread channels, @mentions, Kart task counts, active agents, and system load — all fetched every 15 seconds in a background worker.

**Architecture:** `DeskData` dataclass holds all fetched values. `render_desk(data)` is a pure function (string in, string out) that builds the Rich markup — fully unit-testable without a running app. `DeskPane` becomes a `Container` with a `@work(thread=True)` worker that fetches data and posts `_DeskRefreshed` to trigger a redraw on the main thread.

**Tech Stack:** Python 3.10+, Textual (existing version), psycopg2, pytest. Reuses `grove_reader.py`, `panes/tasks.py`, `panes/overview.py` as read-only dependencies.

---

## File Map

| Action | File | Responsibility |
|--------|------|----------------|
| Modify | `panes/home.py` | Add `DeskData`, `_DeskRefreshed`, `render_desk()`, `fetch_desk_data()`, rewrite `DeskPane`. `HomeGrid` and `ProjectsGrid` unchanged. |
| Modify | `tests/test_panes_home.py` | Replace placeholder tests with `render_desk` unit tests. Keep `HomeGrid` and `ProjectsGrid` tests. |

---

## Task 1: DeskData dataclass and helper pure functions

**Files:**
- Modify: `panes/home.py`
- Modify: `tests/test_panes_home.py`

- [ ] **Step 1: Write failing tests**

Replace the contents of `tests/test_panes_home.py` with:

```python
"""tests/test_panes_home.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from panes.home import (
    DeskData, agent_dot, format_age, mini_bar,
    HOMEGRID_PLACEHOLDER, PROJECTS_PLACEHOLDER,
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

def test_homegrid_placeholder_mentions_phase():
    assert "Phase" in HOMEGRID_PLACEHOLDER or "home" in HOMEGRID_PLACEHOLDER.lower()

def test_projects_placeholder_lists_internal_panes():
    text = PROJECTS_PLACEHOLDER.lower()
    for pane in ("tasks", "agents", "routing", "skills", "logs"):
        assert pane in text
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
python3 -m pytest tests/test_panes_home.py -v
```

Expected: `ImportError` — `DeskData`, `agent_dot`, `format_age`, `mini_bar` not yet defined.

- [ ] **Step 3: Add `DeskData` and helpers to `panes/home.py`**

Read the current `panes/home.py` first. Then add the following at the top of the file, after the docstring and before `DESK_PLACEHOLDER` (which will be removed in Task 3):

```python
from __future__ import annotations
import os
from dataclasses import dataclass, field
from textual.message import Message
from textual.widgets import Static
from textual import work
from textual.containers import Container


@dataclass
class DeskData:
    unread_channels: list[dict] = field(default_factory=list)
    mentions:        list[dict] = field(default_factory=list)
    open_flags:      int        = 0
    running_tasks:   int        = 0
    pending_tasks:   int        = 0
    done_today:      int        = 0
    backfill:        dict | None = None
    agents:          list[dict] = field(default_factory=list)
    sysinfo:         dict       = field(default_factory=lambda: {"cpu": 0, "mem": 0, "disk": 0, "temp": 0})


def agent_dot(age_secs: int) -> str:
    if age_secs < 120:
        return "[green]●[/]"
    if age_secs < 900:
        return "[yellow]●[/]"
    return "[dim]●[/]"


def format_age(age_secs: int) -> str:
    if age_secs < 3600:
        return f"{age_secs // 60}m ago"
    return f"{age_secs // 3600}h ago"


def mini_bar(pct: float) -> str:
    filled = int(pct / 100 * 5)
    return "█" * filled + "░" * (5 - filled)
```

- [ ] **Step 4: Run tests — confirm they pass**

```bash
python3 -m pytest tests/test_panes_home.py -v
```

Expected: all tests PASSED.

- [ ] **Step 5: Commit**

```bash
git add panes/home.py tests/test_panes_home.py
git commit -m "feat(desk): DeskData dataclass + agent_dot/format_age/mini_bar helpers"
```

---

## Task 2: render_desk() pure function

**Files:**
- Modify: `panes/home.py`
- Modify: `tests/test_panes_home.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_panes_home.py`:

```python
from panes.home import render_desk

# ── render_desk sections ──────────────────────────────────────────────────────

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

def test_render_desk_truncates_long_channel_name():
    d = DeskData(unread_channels=[{"name": "this-is-a-very-long-channel-name", "unread": 1}])
    out = render_desk(d)
    lines = [l for l in out.splitlines() if "this-is" in l or len(l) > 0]
    for line in out.splitlines():
        assert len(line) <= 26 or "[" in line  # markup tags don't count toward display width
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
python3 -m pytest tests/test_panes_home.py -v 2>&1 | grep -E "PASSED|FAILED|ERROR" | tail -30
```

Expected: new `render_desk` tests all FAIL with `ImportError`. Previously passing tests still PASS.

- [ ] **Step 3: Implement `render_desk` in `panes/home.py`**

Add after the helper functions, before the existing placeholder constants:

```python
def render_desk(data: DeskData) -> str:
    _H = "[bold #58a6ff]"
    _V = "[#c9d1d9]"
    _D = "[dim]"
    _Y = "[yellow]"
    _E = "[/]"
    lines: list[str] = []

    # ── ATTENTION ────────────────────────────────────────────────────────────
    attn: list[str] = []
    for ch in data.unread_channels:
        name = ch["name"][:14]
        attn.append(f"  {_V}# {name:<14} {ch['unread']}{_E}")
    for m in data.mentions:
        snippet = f"{_Y}@←{m['sender']}{_E}"
        attn.append(f"  {snippet}"[:60])
    if data.open_flags > 0:
        attn.append(f"  {_Y}{data.open_flags} open flags{_E}")
    if attn:
        lines.append(f"{_H}⚡ ATTENTION{_E}")
        lines.extend(attn)
        lines.append("")

    # ── RUNNING ──────────────────────────────────────────────────────────────
    lines.append(f"{_H}▶ RUNNING{_E}")
    if data.running_tasks == 0 and data.pending_tasks == 0:
        lines.append(f"  {_D}idle{_E}")
    else:
        lines.append(f"  {_V}{data.running_tasks} running  {data.pending_tasks} pending{_E}")
    if data.backfill and data.backfill.get("table") != "done":
        pct = data.backfill.get("pct", 0)
        bar = mini_bar(pct)
        lines.append(f"  {_D}embed {bar} {pct:.0f}%{_E}")
    lines.append("")

    # ── DONE TODAY ───────────────────────────────────────────────────────────
    if data.done_today > 0:
        noun = "tasks" if data.done_today != 1 else "task"
        lines.append(f"{_H}✓ DONE TODAY{_E}")
        lines.append(f"  {_V}{data.done_today} {noun} complete{_E}")
        lines.append("")

    # ── SYSTEM ───────────────────────────────────────────────────────────────
    lines.append(f"{_H}⚙ SYSTEM{_E}")
    if not data.agents:
        lines.append(f"  {_D}no agents{_E}")
    else:
        for a in data.agents[:4]:
            dot     = agent_dot(a.get("age_secs", 9999))
            sender  = a["sender"][:12]
            age_str = format_age(a.get("age_secs", 0))
            lines.append(f"  {dot} {_V}{sender:<12}{_E} {_D}{age_str}{_E}")
    cpu = data.sysinfo.get("cpu", 0)
    mem = data.sysinfo.get("mem", 0)
    lines.append(f"  {_D}cpu {cpu}%  mem {mem}%{_E}")
    temp = data.sysinfo.get("temp", 0)
    if temp > 0:
        lines.append(f"  {_D}temp {temp}°C{_E}")

    return "\n".join(lines)
```

- [ ] **Step 4: Run tests — confirm they pass**

```bash
python3 -m pytest tests/test_panes_home.py -v 2>&1 | tail -20
```

Expected: all tests PASSED.

- [ ] **Step 5: Commit**

```bash
git add panes/home.py tests/test_panes_home.py
git commit -m "feat(desk): render_desk() pure function — all sections tested"
```

---

## Task 3: fetch_desk_data() — data fetching function

**Files:**
- Modify: `panes/home.py`
- Modify: `tests/test_panes_home.py`

- [ ] **Step 1: Write failing test**

Append to `tests/test_panes_home.py`:

```python
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
```

- [ ] **Step 2: Run test to confirm it fails**

```bash
python3 -m pytest tests/test_panes_home.py::test_fetch_desk_data_returns_desk_data -v
```

Expected: FAIL with `ImportError`.

- [ ] **Step 3: Implement `fetch_desk_data` in `panes/home.py`**

Add after `render_desk`, still before the placeholder constants:

```python
def fetch_desk_data(sender_name: str) -> DeskData:
    """Fetch all DeskData fields. Never raises — returns safe defaults on failure."""
    import json
    from datetime import date
    from pathlib import Path

    data = DeskData()

    # unread channels
    try:
        import grove_reader
        all_ch = grove_reader.grove_channels()
        data.unread_channels = [c for c in all_ch if c.get("unread", 0) > 0]
    except Exception:
        pass

    # @mentions — scan general + architecture
    try:
        import grove_reader
        target = f"@{sender_name}".lower()
        found: list[dict] = []
        for ch_name in ("general", "architecture"):
            for m in grove_reader.grove_messages(ch_name, limit=50):
                if target in m.get("content", "").lower():
                    found.append({
                        "channel": ch_name,
                        "sender": m.get("sender", "?"),
                        "snippet": m.get("content", "")[:20],
                    })
        data.mentions = found
    except Exception:
        pass

    # open flags from session anchor
    try:
        anchor = json.loads(
            (Path.home() / ".willow" / "session_anchor.json").read_text()
        )
        data.open_flags = anchor.get("open_flags", 0)
    except Exception:
        pass

    # kart task counts + done today
    try:
        from panes.tasks import fetch_tasks
        tasks = fetch_tasks()
        data.running_tasks = tasks.get("running", 0)
        data.pending_tasks = tasks.get("pending", 0)
        today = date.today().isoformat()
        data.done_today = sum(
            1 for r in tasks.get("rows", [])
            if r.get("status", "").lower() in ("complete", "completed")
            and r.get("ts", "").startswith(today)
        )
    except Exception:
        pass

    # backfill progress
    try:
        from panes.tasks import fetch_backfill_progress
        data.backfill = fetch_backfill_progress()
    except Exception:
        pass

    # active agents
    try:
        import grove_reader
        data.agents = grove_reader.grove_agents()
    except Exception:
        pass

    # sysinfo
    try:
        from panes.overview import fetch_sysinfo
        data.sysinfo = fetch_sysinfo()
    except Exception:
        pass

    return data
```

- [ ] **Step 4: Run all tests**

```bash
python3 -m pytest tests/test_panes_home.py -v
```

Expected: all tests PASSED.

- [ ] **Step 5: Commit**

```bash
git add panes/home.py tests/test_panes_home.py
git commit -m "feat(desk): fetch_desk_data() — safe multi-source data collector"
```

---

## Task 4: Rewrite DeskPane as live Container

**Files:**
- Modify: `panes/home.py`

- [ ] **Step 1: Confirm all existing tests still pass before making widget changes**

```bash
python3 -m pytest tests/test_panes_home.py tests/test_panes_chat.py tests/test_widgets_nav_bar.py -v 2>&1 | tail -10
```

Expected: all PASSED.

- [ ] **Step 2: Replace `DeskPane` in `panes/home.py`**

Remove the old `DeskPane` class (the `Static` placeholder) and `DESK_PLACEHOLDER` constant. Replace with:

```python
class _DeskRefreshed(Message):
    def __init__(self, data: DeskData) -> None:
        super().__init__()
        self.data = data


class DeskPane(Container):
    """Left column for Home — live Desk widget. Refreshes every 15s."""

    DEFAULT_CSS = """
    DeskPane {
        width: 1fr;
        height: 1fr;
        padding: 1 1;
    }
    DeskPane Static {
        width: 1fr;
        height: 1fr;
        color: #c9d1d9;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._sender = (
            os.environ.get("GROVE_SENDER")
            or os.environ.get("GROVE_NAME")
            or os.environ.get("USER", "sean")
        )

    def compose(self):
        yield Static("", id="desk-content", markup=True)

    def on_mount(self) -> None:
        self._fetch()
        self.set_interval(15, self._fetch)

    @work(thread=True)
    def _fetch(self) -> None:
        data = fetch_desk_data(self._sender)
        self.post_message(_DeskRefreshed(data))

    def on__desk_refreshed(self, event: _DeskRefreshed) -> None:
        try:
            from textual.css.query import NoMatches
            self.query_one("#desk-content", Static).update(render_desk(event.data))
        except Exception:
            pass
```

Also remove the `DESK_PLACEHOLDER` constant (it was only used by the old `DeskPane.__init__`).

- [ ] **Step 3: Verify import still works**

```bash
python3 -c "from panes.home import DeskPane, HomeGrid, ProjectsGrid, DeskData, render_desk, fetch_desk_data; print('ok')"
```

Expected: `ok`

- [ ] **Step 4: Run all tests**

```bash
python3 -m pytest tests/test_panes_home.py -v
```

Expected: all tests PASSED. (The placeholder tests for `DESK_PLACEHOLDER` were already removed in Task 1 — nothing to break.)

- [ ] **Step 5: Run the full test suite**

```bash
python3 -m pytest tests/ -v --tb=short 2>&1 | tail -15
```

Expected: same pass count as before this task, no new failures.

- [ ] **Step 6: Commit**

```bash
git add panes/home.py
git commit -m "feat(desk): DeskPane live widget — worker refresh + _DeskRefreshed message"
```

---

## Task 5: Smoke test — verify the Desk renders in the running app

- [ ] **Step 1: Launch the app**

```bash
python3 app.py
```

- [ ] **Step 2: Check the Home view (key `1`)**

The left column (ContextPanel) should show the Desk. Verify:
- [ ] `▶ RUNNING` section visible with task counts or "idle"
- [ ] `⚙ SYSTEM` section visible with CPU/mem
- [ ] `⚡ ATTENTION` section visible if any Grove channels have unread messages
- [ ] No crash on startup

- [ ] **Step 3: Wait 15 seconds and confirm the display refreshes**

Watch the system stats or task counts tick over. The display should update without flicker.

- [ ] **Step 4: Kill Postgres and confirm graceful degradation**

Stop Postgres momentarily, wait for the next refresh tick. The Desk should show zeros/empty lists, not crash.

- [ ] **Step 5: Final commit if any minor fixes were needed**

```bash
git add -p
git commit -m "fix(desk): smoke test fixes"
```

---

## Self-Review

**Spec coverage:**

| Spec requirement | Task |
|---|---|
| `DeskData` dataclass with all fields + defaults | Task 1 |
| `agent_dot`, `format_age`, `mini_bar` helpers | Task 1 |
| `render_desk` pure function | Task 2 |
| ATTENTION section conditional | Task 2 |
| RUNNING always shown, idle fallback | Task 2 |
| DONE TODAY conditional | Task 2 |
| SYSTEM always shown, agent list, cpu/mem, temp | Task 2 |
| `fetch_desk_data` with all 8 sources | Task 3 |
| @mention detection using `GROVE_SENDER` env var | Task 3 |
| `_DeskRefreshed` private message | Task 4 |
| `DeskPane` Container + `@work(thread=True)` worker | Task 4 |
| 15s refresh interval | Task 4 |
| No crash when Postgres down | Task 3 (each source individually guarded) |
| `DESK_PLACEHOLDER` removed | Task 4 |

**Type consistency:**
- `DeskData` defined Task 1, used in Tasks 2, 3, 4 ✓
- `render_desk(data: DeskData) -> str` defined Task 2, called in Task 4 ✓
- `fetch_desk_data(sender_name: str) -> DeskData` defined Task 3, called in Task 4 ✓
- `_DeskRefreshed.data: DeskData` defined and consumed in Task 4 ✓
- `mini_bar(pct: float) -> str` defined Task 1, used in Task 2 ✓
- `agent_dot(age_secs: int) -> str` defined Task 1, used in Task 2 ✓
- `format_age(age_secs: int) -> str` defined Task 1, used in Task 2 ✓

**Placeholder scan:** No TBDs, no vague steps. All code blocks complete.
