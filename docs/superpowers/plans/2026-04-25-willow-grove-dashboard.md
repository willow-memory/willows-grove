# Willow Grove Dashboard — Full Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform `app.py` (5-tab stub) into the complete Willow Grove dashboard — animated Hero, live Chat with LISTEN/NOTIFY, Tasks, Agents, Routing, Knowledge, and a visual pass matching the Discord-skin spec.

**Architecture:** Split the current monolith (`app.py`) into `panes/` (one file per tab) and `widgets/` (shared components). `app.py` becomes a thin wire — imports panes, composes the app, owns the refresh loop. Each pane owns its own data fetch. `grove_reader.py` is the read-only data layer; `grove_db.py` is used for writes (chat send).

**Tech Stack:** Python 3.11+, Textual ≥0.61, psycopg2-binary (Postgres + LISTEN/NOTIFY), stdlib (urllib, threading, select, pathlib)

**Spec refs:** `docs/superpowers/specs/2026-04-24-grove-os-design.md`, `docs/superpowers/specs/2026-04-24-grove-skins-beauty.md`, `docs/superpowers/specs/2026-04-22-dashboard-design.md`

---

## File Map

**Create:**
- `panes/__init__.py`
- `panes/overview.py` — OverviewPane: pg/ollama/litellm/tasks/handoff + sysinfo (CPU/mem/disk/temp)
- `panes/chat.py` — ChatPane: channel list + RichLog + Input + LISTEN/NOTIFY
- `panes/tasks.py` — TasksPane: pending/running/done stats + DataTable
- `panes/agents.py` — AgentsPane: active agents with age + hash colors
- `panes/routing.py` — RoutingPane: live routing decision feed
- `panes/knowledge.py` — KnowledgePane: search input + DataTable results
- `panes/providers.py` — ProvidersPane (moved from app.py)
- `panes/skills.py` — SkillsPane (moved from app.py)
- `panes/health.py` — HealthPane (moved from app.py)
- `panes/logs.py` — LogsPane (moved from app.py)
- `widgets/__init__.py`
- `widgets/hero.py` — WillowHero: animated 10-frame sway, 3-pose cycle
- `widgets/status_row.py` — StatusRow (moved from app.py)
- `tests/test_panes_overview.py`
- `tests/test_panes_chat.py`
- `tests/test_panes_tasks.py`
- `tests/test_widgets_hero.py`

**Modify:**
- `app.py` — strip down to thin wire; import panes + widgets; update CSS

---

## Task 1: Module skeleton

**Files:**
- Create: `panes/__init__.py`
- Create: `widgets/__init__.py`

- [ ] **Step 1: Create package markers**

```bash
touch /home/sean-campbell/github/safe-app-willow-grove/panes/__init__.py
touch /home/sean-campbell/github/safe-app-willow-grove/widgets/__init__.py
```

- [ ] **Step 2: Verify imports work**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
python3 -c "import panes; import widgets; print('ok')"
```

Expected: `ok`

- [ ] **Step 3: Commit**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
git add panes/__init__.py widgets/__init__.py
git commit -m "feat(grove): add panes/ and widgets/ package skeletons"
```

---

## Task 2: Extract StatusRow to widgets/status_row.py

**Files:**
- Create: `widgets/status_row.py`
- Modify: `app.py` — replace inline StatusRow class with import

- [ ] **Step 1: Write the test**

Create `tests/test_widgets_status_row.py`:

```python
"""tests/test_widgets_status_row.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from widgets.status_row import dot, color_for_ok

def test_dot_true():
    assert dot(True) == "●"

def test_dot_false():
    assert dot(False) == "○"

def test_dot_none():
    assert dot(None) == "◌"

def test_color_ok():
    assert color_for_ok(True) == "green"

def test_color_fail():
    assert color_for_ok(False) == "red"

def test_color_unknown():
    assert color_for_ok(None) == "yellow"
```

- [ ] **Step 2: Run to verify failure**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
python3 -m pytest tests/test_widgets_status_row.py -v 2>&1 | head -15
```

Expected: `ModuleNotFoundError` on `widgets.status_row`

- [ ] **Step 3: Create widgets/status_row.py**

```python
"""widgets/status_row.py — StatusRow widget + helpers.
b17: WGRV1  ΔΣ=42
"""
from textual.widgets import Static


def dot(ok: bool | None) -> str:
    if ok is True:  return "●"
    if ok is False: return "○"
    return "◌"


def color_for_ok(ok: bool | None) -> str:
    if ok is True:  return "green"
    if ok is False: return "red"
    return "yellow"


class StatusRow(Static):
    """One-line status indicator: [●] label  value"""

    def __init__(self, label: str, **kwargs):
        super().__init__(**kwargs)
        self._label = label

    def set_status(self, ok: bool | None, value: str) -> None:
        color = color_for_ok(ok)
        d     = dot(ok)
        self.update(f"[{color}]{d}[/] [bold]{self._label}[/]  {value}")
```

- [ ] **Step 4: Run tests**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
python3 -m pytest tests/test_widgets_status_row.py -v
```

Expected: 6 PASS

- [ ] **Step 5: Update app.py to import StatusRow**

In `app.py`, replace the `StatusRow` class definition (lines ~155–169) with:

```python
from widgets.status_row import StatusRow
```

Remove the inline `StatusRow` class entirely.

- [ ] **Step 6: Verify app still imports cleanly**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
python3 -c "from app import WillowGrove; print('ok')"
```

Expected: `ok`

- [ ] **Step 7: Commit**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
git add widgets/status_row.py tests/test_widgets_status_row.py app.py
git commit -m "refactor(widgets): extract StatusRow + helpers to widgets/status_row.py"
```

---

## Task 3: WillowHero animated widget

**Files:**
- Create: `widgets/hero.py`
- Create: `tests/test_widgets_hero.py`

- [ ] **Step 1: Write the tests**

Create `tests/test_widgets_hero.py`:

```python
"""tests/test_widgets_hero.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from widgets.hero import POSES, advance_frame, render_frame

def test_poses_exist():
    assert "L" in POSES and "C" in POSES and "R" in POSES

def test_each_pose_has_10_frames():
    for key, frames in POSES.items():
        assert len(frames) == 10, f"pose {key} has {len(frames)} frames"

def test_advance_frame_cycles():
    pose, frame = "L", 0
    for _ in range(10):
        pose, frame = advance_frame(pose, frame)
    assert pose == "C"
    assert frame == 0

def test_advance_frame_full_cycle_returns_to_L():
    pose, frame = "L", 0
    for _ in range(30):
        pose, frame = advance_frame(pose, frame)
    assert pose == "L"
    assert frame == 0

def test_render_frame_returns_string():
    text = render_frame("C", 4)
    assert isinstance(text, str)
    assert len(text) > 0
```

- [ ] **Step 2: Run to verify failure**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
python3 -m pytest tests/test_widgets_hero.py -v 2>&1 | head -10
```

Expected: `ModuleNotFoundError` on `widgets.hero`

- [ ] **Step 3: Create widgets/hero.py**

```python
"""widgets/hero.py — Animated willow tree hero widget.
b17: WGRV1  ΔΣ=42
"""
from textual.widgets import Static

# 10-frame animation poses — L=lean left, C=center, R=lean right
POSES: dict[str, list[str]] = {
    "L": [
        r"ƒƒ\ ƒ ƒ ƒ  /ƒ ƒ ",
        r"ƒ ƒ\ ƒ ƒ  / ƒ ƒ ",
        r"ƒ  ƒ\ ƒ  /  ƒ ƒ ",
        r"ƒ  ƒ \  / ƒ  ƒ  ",
        r"ƒ  ƒ  \/  ƒ  ƒ  ",
        r"ƒ  ƒ  ║   ƒ  ƒ  ",
        r"ƒ  ƒ ƒ║    ƒ  ƒ ",
        r"ƒ    ƒ║     ƒ  ƒ",
        r"ƒ     ║ƒ     ƒ  ",
        r"ƒ     ║ƒ      ƒ ",
    ],
    "C": [
        r"ƒƒ\ ƒ ƒ ƒ /ƒ ƒ  ",
        r"ƒ ƒ\ ƒ ƒ / ƒ ƒ  ",
        r"ƒ  ƒ\   /  ƒ ƒ  ",
        r"ƒ  ƒ \ / ƒ  ƒ   ",
        r"ƒ  ƒ  ║  ƒ  ƒ   ",
        r"ƒ   ƒ ║  ƒ  ƒ   ",
        r"ƒ   ƒ ║ƒ  ƒ  ƒ  ",
        r"ƒ    ƒ║    ƒ  ƒ ",
        r"ƒ     ║ƒ    ƒ  ƒ",
        r"ƒ     ║ƒ     ƒ  ",
    ],
    "R": [
        r"ƒ\ ƒ ƒ ƒ ƒ/ƒƒ   ",
        r"ƒ \ ƒ ƒ ƒ /ƒ ƒ  ",
        r"ƒ  \ ƒ ƒ /  ƒ ƒ ",
        r"ƒ ƒ \   /ƒ  ƒ ƒ ",
        r"ƒ ƒ  \ / ƒ  ƒ ƒ ",
        r"ƒ ƒ   ║  ƒ  ƒ ƒ ",
        r"ƒ  ƒ ƒ║   ƒ  ƒ  ",
        r"ƒ    ƒ║    ƒ  ƒ ",
        r"ƒ     ║ƒ    ƒ   ",
        r"ƒ     ║ ƒ    ƒ  ",
    ],
}

_POSE_ORDER = ["L", "C", "R", "C"]  # L→C→R→C→L cycle


def advance_frame(pose: str, frame: int) -> tuple[str, int]:
    """Return (next_pose, next_frame) after advancing one step."""
    frame += 1
    if frame >= len(POSES[pose]):
        idx = (_POSE_ORDER.index(pose) + 1) % len(_POSE_ORDER)
        pose  = _POSE_ORDER[idx]
        frame = 0
    return pose, frame


def render_frame(pose: str, frame: int) -> str:
    return POSES[pose][frame]


_SCENE_TOP = [
    "        ,",
    "       /|\\",
    "      / | \\",
]

_SCENE_BOTTOM = [
    "      |   |",
    "   ~~~|~~~|~~~",
]


class WillowHero(Static):
    """Animated 10-frame willow tree sway. Cycles L→C→R→C→L."""

    DEFAULT_CSS = """
    WillowHero {
        height: 8;
        content-align: center middle;
        color: $success;
        text-style: bold;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._pose  = "C"
        self._frame = 4

    def on_mount(self) -> None:
        self.set_interval(0.18, self._tick)
        self._render()

    def _tick(self) -> None:
        self._pose, self._frame = advance_frame(self._pose, self._frame)
        self._render()

    def _render(self) -> None:
        branch = render_frame(self._pose, self._frame)
        lines  = _SCENE_TOP + [f"    {branch}"] + _SCENE_BOTTOM
        self.update("\n".join(lines))
```

- [ ] **Step 4: Run tests**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
python3 -m pytest tests/test_widgets_hero.py -v
```

Expected: 5 PASS

- [ ] **Step 5: Commit**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
git add widgets/hero.py tests/test_widgets_hero.py
git commit -m "feat(widgets): add WillowHero — animated 30-frame willow sway"
```

---

## Task 4: Extract existing panes to panes/

Move the four existing panes out of app.py into their own files. No new functionality — just a structural move.

**Files:**
- Create: `panes/providers.py`
- Create: `panes/skills.py`
- Create: `panes/health.py`
- Create: `panes/logs.py`
- Modify: `app.py`

- [ ] **Step 1: Create panes/providers.py**

```python
"""panes/providers.py — Provider enable/disable pane.
b17: WGRV1  ΔΣ=42
"""
import json
import os
import sqlite3
from pathlib import Path

from textual.binding import Binding
from textual.containers import Container
from textual.widgets import DataTable, Label

WILLOW_STORE = Path(os.environ.get("WILLOW_STORE_ROOT", Path.home() / ".willow" / "store"))


def _read_providers() -> list[dict]:
    col_dir = WILLOW_STORE / "willow" / "providers"
    if not col_dir.exists():
        return []
    providers = []
    try:
        db = col_dir / "store.db"
        if db.exists():
            conn = sqlite3.connect(str(db), check_same_thread=False)
            rows = conn.execute("SELECT data FROM records WHERE deleted = 0").fetchall()
            conn.close()
            for row in rows:
                try:
                    providers.append(json.loads(row[0]))
                except Exception:
                    pass
    except Exception:
        pass
    return providers


class ProvidersPane(Container):
    BINDINGS = [
        Binding("e", "enable_selected",  "Enable"),
        Binding("d", "disable_selected", "Disable"),
    ]

    def compose(self):
        yield Label("  Providers  (e=enable  d=disable)", id="prov-title")
        table = DataTable(id="prov-table", cursor_type="row")
        table.add_columns("Provider", "Status", "Type", "Models")
        yield table

    def refresh_data(self) -> None:
        table = self.query_one("#prov-table", DataTable)
        table.clear()
        providers = _read_providers()
        if not providers:
            table.add_row("No provider data", "run willow providers list", "", "")
            return
        for p in providers:
            status = "[green]ON[/]" if p.get("enabled") else "[red]OFF[/]"
            ptype  = "local" if p.get("local") else "cloud"
            models = ", ".join(p.get("models", [])[:2])
            table.add_row(p["name"], status, ptype, models)

    def action_enable_selected(self) -> None:
        table = self.query_one("#prov-table", DataTable)
        row   = table.cursor_row
        if row < 0:
            return
        name = str(table.get_cell_at((row, 0)))
        os.system(f"willow providers enable {name} &")
        self.refresh_data()

    def action_disable_selected(self) -> None:
        table = self.query_one("#prov-table", DataTable)
        row   = table.cursor_row
        if row < 0:
            return
        name = str(table.get_cell_at((row, 0)))
        if name == "ollama":
            self.app.notify("Ollama cannot be disabled.", severity="warning")
            return
        os.system(f"willow providers disable {name} &")
        self.refresh_data()
```

- [ ] **Step 2: Create panes/skills.py**

```python
"""panes/skills.py — Skills list pane.
b17: WGRV1  ΔΣ=42
"""
import os
from pathlib import Path

from textual.containers import Container
from textual.widgets import DataTable, Label, Static

WILLOW_ROOT  = Path(os.environ.get("WILLOW_ROOT", Path.home() / "github" / "willow-1.9"))
SKILLS_DIR   = WILLOW_ROOT / "willow" / "fylgja" / "skills"


def _read_skills() -> list[dict]:
    skills = []
    if not SKILLS_DIR.exists():
        return skills
    for path in sorted(SKILLS_DIR.glob("*.md")):
        name = path.stem
        description = ""
        try:
            text = path.read_text()
            in_front = False
            for line in text.splitlines():
                if line.strip() == "---":
                    in_front = not in_front
                    continue
                if in_front and line.startswith("description:"):
                    description = line[len("description:"):].strip().strip('"')
                    break
        except Exception:
            pass
        skills.append({"name": name, "description": description, "path": str(path)})
    return skills


class SkillsPane(Container):
    def compose(self):
        yield Label(f"  Skills — {SKILLS_DIR}", id="skills-title")
        table = DataTable(id="skills-table", cursor_type="row")
        table.add_columns("Name", "Description")
        yield table
        yield Static("", id="skill-detail")

    def refresh_data(self) -> None:
        table = self.query_one("#skills-table", DataTable)
        table.clear()
        for s in _read_skills():
            desc = s["description"][:80] + "…" if len(s["description"]) > 80 else s["description"]
            table.add_row(s["name"], desc)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        skills = _read_skills()
        if event.cursor_row < len(skills):
            skill = skills[event.cursor_row]
            try:
                content = Path(skill["path"]).read_text()[:500]
            except Exception:
                content = "(unreadable)"
            self.query_one("#skill-detail", Static).update(
                f"\n[bold]{skill['name']}[/]\n{skill['description']}\n\n{content}"
            )
```

- [ ] **Step 3: Create panes/health.py**

```python
"""panes/health.py — Health check pane.
b17: WGRV1  ΔΣ=42
"""
import os
import subprocess
from pathlib import Path

from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Label, Log

WILLOW_ROOT = Path(os.environ.get("WILLOW_ROOT", Path.home() / "github" / "willow-1.9"))


class HealthPane(Container):
    BINDINGS = [Binding("r", "run_health", "Run boot check")]

    def compose(self):
        yield Label("  Health  (r=run boot check)", id="health-title")
        yield Log(id="health-log", auto_scroll=True)

    def action_run_health(self) -> None:
        log    = self.query_one("#health-log", Log)
        script = WILLOW_ROOT / "willow" / "fylgja" / "skills" / "scripts" / "system_health.py"
        log.clear()
        log.write_line("Running willow health boot…")
        try:
            result = subprocess.run(
                ["python3", str(script), "--check", "boot",
                 "--willow-dir", str(Path.home() / ".willow"),
                 "--repo",        str(WILLOW_ROOT)],
                capture_output=True, text=True, timeout=30,
            )
            for line in (result.stdout + result.stderr).splitlines():
                color = ("green"  if "HEALTHY"  in line else
                         "red"    if "CRITICAL" in line else
                         "yellow" if "WARN"     in line else "")
                log.write_line(f"[{color}]{line}[/]" if color else line)
        except Exception as e:
            log.write_line(f"[red]Error: {e}[/]")
```

- [ ] **Step 4: Create panes/logs.py**

```python
"""panes/logs.py — Log tail pane.
b17: WGRV1  ΔΣ=42
"""
from pathlib import Path

from textual.containers import Container
from textual.widgets import Label, Log

WILLOW_LOGS = Path.home() / ".willow" / "logs"


def _tail_log(lines: int = 80) -> list[str]:
    try:
        logs = sorted(WILLOW_LOGS.glob("*.log"),
                      key=lambda p: p.stat().st_mtime, reverse=True)
        if not logs:
            return ["No log files found in ~/.willow/logs/"]
        return logs[0].read_text().splitlines()[-lines:]
    except Exception as e:
        return [f"Log read error: {e}"]


class LogsPane(Container):
    def compose(self):
        yield Label("  Logs — ~/.willow/logs/ (most recent)", id="logs-title")
        yield Log(id="log-view", auto_scroll=True)

    def refresh_data(self) -> None:
        log = self.query_one("#log-view", Log)
        log.clear()
        for line in _tail_log(80):
            log.write_line(line)
```

- [ ] **Step 5: Update app.py imports**

At the top of `app.py`, replace the four inline pane classes with imports. Remove the `ProvidersPane`, `SkillsPane`, `HealthPane`, and `LogsPane` class definitions from app.py entirely, and add:

```python
from panes.providers import ProvidersPane
from panes.skills    import SkillsPane
from panes.health    import HealthPane
from panes.logs      import LogsPane
```

Also remove the `_read_providers()` and `_read_skills()` and `_tail_log()` helper functions from app.py (they now live in the pane files). Keep `_pg_conn`, `_ollama_status`, `_litellm_status`, `_pg_status`, `_open_tasks`, `_last_handoff`, and `_http_get` — those are still needed by OverviewPane which hasn't moved yet.

- [ ] **Step 6: Verify app still runs**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
python3 -c "from app import WillowGrove; print('ok')"
```

Expected: `ok`

- [ ] **Step 7: Commit**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
git add panes/providers.py panes/skills.py panes/health.py panes/logs.py app.py
git commit -m "refactor(panes): extract Providers, Skills, Health, Logs to panes/"
```

---

## Task 5: OverviewPane with Hero + sysinfo

**Files:**
- Create: `panes/overview.py`
- Create: `tests/test_panes_overview.py`
- Modify: `app.py` — import OverviewPane, add WillowHero

- [ ] **Step 1: Write the tests**

Create `tests/test_panes_overview.py`:

```python
"""tests/test_panes_overview.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from unittest.mock import patch, MagicMock
from panes.overview import fetch_sysinfo, _pg_status, _ollama_status, _open_tasks

def test_fetch_sysinfo_keys():
    info = fetch_sysinfo()
    for key in ("cpu", "mem", "disk"):
        assert key in info
        assert isinstance(info[key], int)
        assert 0 <= info[key] <= 100

def test_pg_status_returns_tuple():
    with patch("panes.overview._pg_conn", side_effect=Exception("no db")):
        ok, count = _pg_status()
    assert ok is False
    assert count == 0

def test_ollama_status_unreachable():
    with patch("urllib.request.urlopen", side_effect=Exception("refused")):
        ok, models = _ollama_status()
    assert ok is False
    assert models == []

def test_open_tasks_returns_int():
    with patch("panes.overview._pg_conn", side_effect=Exception("no db")):
        count = _open_tasks()
    assert count == 0
```

- [ ] **Step 2: Run to verify failure**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
python3 -m pytest tests/test_panes_overview.py -v 2>&1 | head -10
```

Expected: `ModuleNotFoundError` on `panes.overview`

- [ ] **Step 3: Create panes/overview.py**

```python
"""panes/overview.py — Overview pane: status rows + sysinfo + Hero.
b17: WGRV1  ΔΣ=42
"""
import json
import os
import shutil
import urllib.request
from datetime import datetime
from pathlib import Path

from textual.containers import Container, Vertical
from textual.widgets import Label, Rule

from widgets.hero       import WillowHero
from widgets.status_row import StatusRow

SESSION_ANCHOR = Path.home() / ".willow" / "session_anchor.json"


def _http_get(url: str, timeout: int = 2) -> dict | None:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read())
    except Exception:
        return None


def _pg_conn():
    import psycopg2
    return psycopg2.connect(
        dbname=os.environ.get("WILLOW_PG_DB",   "willow_19"),
        user=os.environ.get("WILLOW_PG_USER", os.environ.get("USER", "")),
    )


def _pg_status() -> tuple[bool, int]:
    try:
        conn = _pg_conn()
        cur  = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM knowledge")
        count = cur.fetchone()[0]
        conn.close()
        return True, count
    except Exception:
        return False, 0


def _ollama_status() -> tuple[bool, list[str]]:
    data = _http_get("http://localhost:11434/api/tags")
    if not data:
        return False, []
    return True, [m["name"] for m in data.get("models", [])]


def _litellm_status() -> bool:
    return _http_get("http://localhost:4000/health") is not None


def _open_tasks() -> int:
    try:
        conn = _pg_conn()
        cur  = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM public.tasks WHERE status IN ('pending','queued')")
        count = cur.fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0


def _last_handoff() -> str:
    try:
        data = json.loads(SESSION_ANCHOR.read_text())
        return data.get("handoff_title", "—")
    except Exception:
        return "—"


def fetch_sysinfo() -> dict:
    """Return cpu/mem/disk/temp as 0-100 int percentages. Never raises."""
    result = {"cpu": 0, "mem": 0, "disk": 0, "temp": 0}
    try:
        with open("/proc/stat") as f:
            parts = f.readline().split()
        vals       = [int(x) for x in parts[1:]]
        idle       = vals[3] + (vals[4] if len(vals) > 4 else 0)
        result["cpu"] = max(0, min(100, int((1 - idle / max(sum(vals), 1)) * 100)))
    except Exception:
        pass
    try:
        info: dict[str, int] = {}
        with open("/proc/meminfo") as f:
            for line in f:
                k, v = line.split(":", 1)
                info[k.strip()] = int(v.strip().split()[0])
        total = info.get("MemTotal", 1)
        avail = info.get("MemAvailable", total)
        result["mem"] = max(0, min(100, int((total - avail) / total * 100)))
    except Exception:
        pass
    try:
        usage = shutil.disk_usage("/")
        result["disk"] = max(0, min(100, int(usage.used / usage.total * 100)))
    except Exception:
        pass
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            result["temp"] = int(f.read().strip()) // 1000
    except Exception:
        pass
    return result


def _bar(pct: int, width: int = 10) -> str:
    filled = int(pct / 100 * width)
    return "█" * filled + "░" * (width - filled)


class OverviewPane(Container):
    def compose(self):
        yield WillowHero(id="hero")
        yield Rule()
        yield Label("  Willow System", id="overview-title")
        yield StatusRow("Postgres     ", id="stat-pg")
        yield StatusRow("Ollama       ", id="stat-ollama")
        yield StatusRow("LiteLLM      ", id="stat-litellm")
        yield StatusRow("Open tasks   ", id="stat-tasks")
        yield StatusRow("Last handoff ", id="stat-handoff")
        yield Rule()
        yield Label("  System", id="sysinfo-title")
        yield StatusRow("CPU          ", id="stat-cpu")
        yield StatusRow("Memory       ", id="stat-mem")
        yield StatusRow("Disk         ", id="stat-disk")
        yield StatusRow("Temp         ", id="stat-temp")

    def refresh_data(self) -> None:
        pg_up, atoms = _pg_status()
        self.query_one("#stat-pg", StatusRow).set_status(
            pg_up, f"{atoms:,} KB atoms" if pg_up else "NOT CONNECTED"
        )
        ollama_up, models = _ollama_status()
        self.query_one("#stat-ollama", StatusRow).set_status(
            ollama_up, f"{len(models)} models" if ollama_up else "unreachable"
        )
        lt_up = _litellm_status()
        self.query_one("#stat-litellm", StatusRow).set_status(
            lt_up, "localhost:4000" if lt_up else "not running"
        )
        tasks = _open_tasks()
        self.query_one("#stat-tasks", StatusRow).set_status(tasks == 0, str(tasks))
        self.query_one("#stat-handoff", StatusRow).set_status(None, _last_handoff())

        info = fetch_sysinfo()
        self.query_one("#stat-cpu",  StatusRow).set_status(
            info["cpu"] < 90, f"{_bar(info['cpu'])}  {info['cpu']}%"
        )
        self.query_one("#stat-mem",  StatusRow).set_status(
            info["mem"] < 90, f"{_bar(info['mem'])}  {info['mem']}%"
        )
        self.query_one("#stat-disk", StatusRow).set_status(
            info["disk"] < 90, f"{_bar(info['disk'])}  {info['disk']}%"
        )
        temp_ok = None if info["temp"] == 0 else info["temp"] < 80
        self.query_one("#stat-temp", StatusRow).set_status(
            temp_ok, f"{info['temp']}°C" if info["temp"] else "n/a"
        )
```

- [ ] **Step 4: Run tests**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
python3 -m pytest tests/test_panes_overview.py -v
```

Expected: 4 PASS

- [ ] **Step 5: Update app.py**

In `app.py`:

1. Add import at top:
```python
from panes.overview  import OverviewPane
from widgets.hero    import WillowHero
```

2. Remove the inline `OverviewPane` class and all helper functions (`_http_get`, `_pg_conn`, `_ollama_status`, `_litellm_status`, `_pg_status`, `_open_tasks`, `_last_handoff`) — they now live in `panes/overview.py`.

3. The `compose()` method in `WillowGrove` should already reference `OverviewPane` by ID — no change needed there.

- [ ] **Step 6: Verify**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
python3 -c "from app import WillowGrove; print('ok')"
```

Expected: `ok`

- [ ] **Step 7: Commit**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
git add panes/overview.py tests/test_panes_overview.py app.py
git commit -m "feat(overview): Hero + sysinfo (CPU/mem/disk/temp) in OverviewPane"
```

---

## Task 6: ChatPane

**Files:**
- Create: `panes/chat.py`
- Create: `tests/test_panes_chat.py`
- Modify: `app.py` — add Chat tab

The Chat pane has two data paths:
- **Poll** (every 5s): `grove_reader.grove_channels()` + `grove_reader.grove_messages()`
- **Real-time**: Postgres `LISTEN grove_channel` → `pg_notify` fires on every new message (trigger already exists in `grove_db.py`)

- [ ] **Step 1: Write the tests**

Create `tests/test_panes_chat.py`:

```python
"""tests/test_panes_chat.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from unittest.mock import patch, MagicMock
from panes.chat import (
    format_ts, sender_color, _CHANNEL_ORDER, sort_channels,
)

def test_format_ts_datetime():
    from datetime import datetime
    dt  = datetime(2026, 4, 25, 13, 4, 0)
    out = format_ts(dt)
    assert out == "13:04"

def test_format_ts_string_fallback():
    out = format_ts("2026-04-25 13:04:22")
    assert "13:04" in out

def test_format_ts_none():
    assert format_ts(None) == ""

def test_sender_color_stable():
    c1 = sender_color("hanuman")
    c2 = sender_color("hanuman")
    assert c1 == c2

def test_sender_color_different():
    colors = {sender_color(n) for n in ["hanuman", "ganesha", "jeles", "heimdallr"]}
    assert len(colors) > 1

def test_sort_channels_pinned_first():
    channels = [
        {"name": "readme",       "unread": 0},
        {"name": "general",      "unread": 0},
        {"name": "architecture", "unread": 0},
        {"name": "zebra",        "unread": 0},
    ]
    sorted_ch = sort_channels(channels)
    names = [c["name"] for c in sorted_ch]
    assert names.index("general") < names.index("zebra")
    assert names.index("architecture") < names.index("zebra")
```

- [ ] **Step 2: Run to verify failure**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
python3 -m pytest tests/test_panes_chat.py -v 2>&1 | head -10
```

Expected: `ModuleNotFoundError` on `panes.chat`

- [ ] **Step 3: Create panes/chat.py**

```python
"""panes/chat.py — Grove channel chat pane with LISTEN/NOTIFY real-time.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import hashlib
import os
import select
from datetime import datetime

from rich.markup import escape as _e
from textual import on, work
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Input, Label, ListItem, ListView, RichLog, Static

import grove_reader

_SENDER_COLORS = ["cyan", "magenta", "yellow", "bright_green", "bright_blue", "bright_red", "bright_cyan"]
_CHANNEL_ORDER = ["general", "architecture", "handoffs", "readme"]


def sender_color(name: str) -> str:
    idx = int(hashlib.md5(name.encode()).hexdigest(), 16) % len(_SENDER_COLORS)
    return _SENDER_COLORS[idx]


def format_ts(ts) -> str:
    if ts is None:
        return ""
    if isinstance(ts, datetime):
        return ts.strftime("%H:%M")
    s = str(ts)
    return s[11:16] if len(s) >= 16 else s[:5]


def sort_channels(channels: list[dict]) -> list[dict]:
    order = {n: i for i, n in enumerate(_CHANNEL_ORDER)}
    return sorted(channels, key=lambda c: (order.get(c["name"], 99), c["name"]))


def _pg_conn():
    import psycopg2
    return psycopg2.connect(
        dbname=os.environ.get("WILLOW_PG_DB",   "willow_19"),
        user=os.environ.get("WILLOW_PG_USER", os.environ.get("USER", "")),
    )


class ChannelItem(ListItem):
    def __init__(self, channel: dict):
        super().__init__()
        self.channel = channel

    def compose(self):
        name   = self.channel["name"]
        unread = self.channel.get("unread", 0)
        suffix = f" [yellow bold]{unread}[/]" if unread else ""
        yield Label(f"# {name}{suffix}", markup=True)


class ChatPane(Container):
    DEFAULT_CSS = """
    ChatPane {
        layout: horizontal;
        height: 1fr;
    }
    ChatPane #channel-sidebar {
        width: 24;
        background: $panel;
        border-right: solid $primary-darken-3;
        height: 1fr;
    }
    ChatPane #channel-sidebar Label {
        padding: 0 1;
        color: $text-muted;
        text-style: bold;
    }
    ChatPane #msg-area {
        width: 1fr;
        height: 1fr;
        layout: vertical;
    }
    ChatPane #channel-title {
        height: 1;
        padding: 0 2;
        background: $panel;
        color: $accent;
        text-style: bold;
        border-bottom: solid $primary-darken-3;
    }
    ChatPane #msg-log {
        height: 1fr;
        padding: 1 2;
    }
    ChatPane #msg-input {
        height: 3;
        margin: 0 2 1 2;
        border: tall $primary-darken-2;
    }
    ChatPane #msg-input:focus {
        border: tall $accent;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._active_channel: str  = ""
        self._channels: list[dict] = []
        self._cursors:  dict       = {}
        self._listening            = False

    def compose(self):
        with Vertical(id="channel-sidebar"):
            yield Label("CHANNELS")
            yield ListView(id="channel-list")
        with Vertical(id="msg-area"):
            yield Static("", id="channel-title")
            yield RichLog(id="msg-log", highlight=False, markup=True, wrap=True)
            yield Input(placeholder="Message…", id="msg-input")

    def on_mount(self) -> None:
        self.set_interval(5, self._poll)
        self._poll()
        self._start_listener()

    def _poll(self) -> None:
        try:
            channels = grove_reader.grove_channels(last_seen_ids=self._cursors)
            self._channels = sort_channels(channels)
            lst = self.query_one("#channel-list", ListView)
            lst.clear()
            for ch in self._channels:
                lst.append(ChannelItem(ch))
            if not self._active_channel and self._channels:
                self._open_channel(self._channels[0]["name"])
        except Exception:
            pass

    @work(thread=True)
    def _start_listener(self) -> None:
        """Block in a thread listening for Postgres NOTIFY grove_channel."""
        self._listening = True
        try:
            import psycopg2
            conn = _pg_conn()
            conn.autocommit = True
            cur  = conn.cursor()
            cur.execute("LISTEN grove_channel")
            while self._listening:
                if select.select([conn], [], [], 1.0)[0]:
                    conn.poll()
                    while conn.notifies:
                        conn.notifies.pop(0)
                        self.app.call_from_thread(self._on_notify)
        except Exception:
            pass

    def _on_notify(self) -> None:
        if self._active_channel:
            self._load_messages(self._active_channel)

    def _open_channel(self, name: str) -> None:
        self._active_channel = name
        self.query_one("#channel-title", Static).update(f"# {name}")
        self._load_messages(name)

    def _load_messages(self, channel: str) -> None:
        try:
            msgs = grove_reader.grove_messages(channel, limit=100)
            log  = self.query_one("#msg-log", RichLog)
            log.clear()
            for m in msgs:
                sender  = m.get("sender", "?")
                content = m.get("content", "")
                ts      = format_ts(m.get("created_at"))
                color   = sender_color(sender)
                log.write(
                    f"[dim]{ts}[/dim]  [{color} bold]{sender:<14}[/{color} bold]  {_e(content)}"
                )
            if msgs:
                self._cursors[channel] = msgs[-1]["id"]
        except Exception:
            pass

    @on(ListView.Selected, "#channel-list")
    def _channel_selected(self, event: ListView.Selected) -> None:
        if isinstance(event.item, ChannelItem):
            self._open_channel(event.item.channel["name"])

    @on(Input.Submitted, "#msg-input")
    def _send_message(self, event: Input.Submitted) -> None:
        body = event.value.strip()
        if not body or not self._active_channel:
            return
        event.input.value = ""
        try:
            conn = _pg_conn()
            cur  = conn.cursor()
            cur.execute(
                "SELECT id FROM grove.channels WHERE name = %s LIMIT 1",
                (self._active_channel,),
            )
            row = cur.fetchone()
            if row:
                agent = os.environ.get("WILLOW_AGENT_NAME", "hanuman")
                cur.execute(
                    "INSERT INTO grove.messages (channel_id, sender, content) VALUES (%s, %s, %s)",
                    (row[0], agent, body),
                )
                conn.commit()
            conn.close()
        except Exception:
            pass
        self._load_messages(self._active_channel)

    def on_unmount(self) -> None:
        self._listening = False
```

- [ ] **Step 4: Run tests**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
python3 -m pytest tests/test_panes_chat.py -v
```

Expected: 7 PASS

- [ ] **Step 5: Add Chat tab to app.py**

In `app.py`, add:
```python
from panes.chat import ChatPane
```

In the `compose()` method, inside `TabbedContent`, add after the Overview tab:
```python
with TabPane("Chat", id="tab-chat"):
    yield ChatPane(id="chat-pane")
```

- [ ] **Step 6: Commit**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
git add panes/chat.py tests/test_panes_chat.py app.py
git commit -m "feat(chat): ChatPane — channels, messages, send, LISTEN/NOTIFY real-time"
```

---

## Task 7: TasksPane

**Files:**
- Create: `panes/tasks.py`
- Create: `tests/test_panes_tasks.py`
- Modify: `app.py` — add Tasks tab

- [ ] **Step 1: Write the tests**

Create `tests/test_panes_tasks.py`:

```python
"""tests/test_panes_tasks.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from unittest.mock import patch
from panes.tasks import fetch_tasks, status_color

def test_fetch_tasks_no_db():
    with patch("panes.tasks._pg_conn", side_effect=Exception("no db")):
        result = fetch_tasks()
    assert result["pending"] == 0
    assert result["running"] == 0
    assert result["done"]    == 0
    assert result["rows"]    == []

def test_status_color_complete():
    assert status_color("complete")   == "green"
    assert status_color("completed")  == "green"

def test_status_color_running():
    assert status_color("running")    == "yellow"

def test_status_color_pending():
    assert status_color("pending")    == "dim"
    assert status_color("queued")     == "dim"

def test_status_color_failed():
    assert status_color("failed")     == "red"
    assert status_color("error")      == "red"
```

- [ ] **Step 2: Run to verify failure**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
python3 -m pytest tests/test_panes_tasks.py -v 2>&1 | head -10
```

Expected: `ModuleNotFoundError` on `panes.tasks`

- [ ] **Step 3: Create panes/tasks.py**

```python
"""panes/tasks.py — Kart task queue pane.
b17: WGRV1  ΔΣ=42
"""
import os

from textual.containers import Container
from textual.widgets import DataTable, Label

from widgets.status_row import StatusRow


def _pg_conn():
    import psycopg2
    return psycopg2.connect(
        dbname=os.environ.get("WILLOW_PG_DB",   "willow_19"),
        user=os.environ.get("WILLOW_PG_USER", os.environ.get("USER", "")),
    )


def status_color(status: str) -> str:
    s = status.lower()
    if s in ("complete", "completed"):
        return "green"
    if s == "running":
        return "yellow"
    if s in ("failed", "error"):
        return "red"
    return "dim"


def fetch_tasks() -> dict:
    """Return task stats + recent rows. Never raises."""
    result = {"pending": 0, "running": 0, "done": 0, "rows": []}
    try:
        conn = _pg_conn()
        cur  = conn.cursor()
        cur.execute("""
            SELECT
                COUNT(*) FILTER (WHERE status IN ('pending','queued'))  AS pending,
                COUNT(*) FILTER (WHERE status = 'running')              AS running,
                COUNT(*) FILTER (WHERE status IN ('complete','completed','failed','error')) AS done
            FROM public.tasks
        """)
        row = cur.fetchone()
        result["pending"] = row[0] or 0
        result["running"] = row[1] or 0
        result["done"]    = row[2] or 0
        cur.execute("""
            SELECT id, status, cmd, created_at
            FROM public.tasks
            ORDER BY id DESC LIMIT 50
        """)
        result["rows"] = [
            {"id": r[0], "status": r[1], "cmd": r[2] or "", "ts": str(r[3])[:16]}
            for r in cur.fetchall()
        ]
        conn.close()
    except Exception:
        pass
    return result


class TasksPane(Container):
    def compose(self):
        yield Label("  Tasks", id="tasks-title")
        yield StatusRow("Running", id="stat-running")
        yield StatusRow("Pending", id="stat-pending")
        yield StatusRow("Done   ", id="stat-done")
        table = DataTable(id="tasks-table", cursor_type="row")
        table.add_columns("ID", "Status", "Command", "Time")
        yield table

    def on_mount(self) -> None:
        self.set_interval(10, self.refresh_data)
        self.refresh_data()

    def refresh_data(self) -> None:
        data  = fetch_tasks()
        table = self.query_one("#tasks-table", DataTable)
        table.clear()

        self.query_one("#stat-running", StatusRow).set_status(
            None, str(data["running"])
        )
        self.query_one("#stat-pending", StatusRow).set_status(
            data["pending"] == 0, str(data["pending"])
        )
        self.query_one("#stat-done", StatusRow).set_status(
            None, str(data["done"])
        )

        for row in data["rows"]:
            color = status_color(row["status"])
            table.add_row(
                str(row["id"]),
                f"[{color}]{row['status']}[/]",
                row["cmd"][:60],
                row["ts"],
            )
```

- [ ] **Step 4: Run tests**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
python3 -m pytest tests/test_panes_tasks.py -v
```

Expected: 5 PASS

- [ ] **Step 5: Add Tasks tab to app.py**

```python
from panes.tasks import TasksPane
```

In `compose()`, add:
```python
with TabPane("Tasks", id="tab-tasks"):
    yield TasksPane(id="tasks-pane")
```

Also add to `_do_refresh()`:
```python
try:
    self.query_one("#tasks-pane", TasksPane).refresh_data()
except Exception:
    pass
```

- [ ] **Step 6: Commit**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
git add panes/tasks.py tests/test_panes_tasks.py app.py
git commit -m "feat(tasks): TasksPane — Kart queue with pending/running/done stats"
```

---

## Task 8: AgentsPane

**Files:**
- Create: `panes/agents.py`
- Create: `tests/test_panes_agents.py`
- Modify: `app.py` — add Agents tab

- [ ] **Step 1: Write the tests**

Create `tests/test_panes_agents.py`:

```python
"""tests/test_panes_agents.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from panes.agents import agent_state, age_str

def test_agent_state_running():
    assert agent_state(60)   == ("running", "green")

def test_agent_state_idle():
    assert agent_state(300)  == ("idle",    "yellow")

def test_agent_state_stale():
    assert agent_state(1800) == ("stale",   "dim")

def test_agent_state_gone():
    assert agent_state(7200) == ("gone",    "dim")

def test_age_str_seconds():
    assert age_str(45)   == "45s"

def test_age_str_minutes():
    assert age_str(125)  == "2m"

def test_age_str_hours():
    assert age_str(7200) == "2h"
```

- [ ] **Step 2: Run to verify failure**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
python3 -m pytest tests/test_panes_agents.py -v 2>&1 | head -10
```

Expected: `ModuleNotFoundError` on `panes.agents`

- [ ] **Step 3: Create panes/agents.py**

```python
"""panes/agents.py — Active agent monitor pane.
b17: WGRV1  ΔΣ=42
"""
from textual.containers import Container
from textual.widgets import DataTable, Label

import grove_reader
from panes.chat import sender_color


def agent_state(age_secs: int) -> tuple[str, str]:
    if age_secs < 120:
        return "running", "green"
    if age_secs < 900:
        return "idle",    "yellow"
    if age_secs < 3600:
        return "stale",   "dim"
    return "gone", "dim"


def age_str(secs: int) -> str:
    if secs < 60:
        return f"{secs}s"
    if secs < 3600:
        return f"{secs // 60}m"
    return f"{secs // 3600}h"


class AgentsPane(Container):
    def compose(self):
        yield Label("  Agents", id="agents-title")
        table = DataTable(id="agents-table", cursor_type="row")
        table.add_columns("Agent", "State", "Last seen")
        yield table

    def on_mount(self) -> None:
        self.set_interval(15, self.refresh_data)
        self.refresh_data()

    def refresh_data(self) -> None:
        table  = self.query_one("#agents-table", DataTable)
        table.clear()
        agents = grove_reader.grove_agents()
        for a in agents:
            sender   = a["sender"]
            age_secs = a.get("age_secs", 9999)
            state, state_color = agent_state(age_secs)
            color    = sender_color(sender)
            table.add_row(
                f"[{color} bold]{sender}[/]",
                f"[{state_color}]{state}[/]",
                age_str(age_secs),
            )
```

- [ ] **Step 4: Run tests**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
python3 -m pytest tests/test_panes_agents.py -v
```

Expected: 7 PASS

- [ ] **Step 5: Add Agents tab to app.py**

```python
from panes.agents import AgentsPane
```

In `compose()`:
```python
with TabPane("Agents", id="tab-agents"):
    yield AgentsPane(id="agents-pane")
```

Add to `_do_refresh()`:
```python
try:
    self.query_one("#agents-pane", AgentsPane).refresh_data()
except Exception:
    pass
```

- [ ] **Step 6: Commit**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
git add panes/agents.py tests/test_panes_agents.py app.py
git commit -m "feat(agents): AgentsPane — active agents with state and age"
```

---

## Task 9: RoutingPane

**Files:**
- Create: `panes/routing.py`
- Create: `tests/test_panes_routing.py`
- Modify: `app.py` — add Routing tab

- [ ] **Step 1: Write the tests**

Create `tests/test_panes_routing.py`:

```python
"""tests/test_panes_routing.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from unittest.mock import patch
from panes.routing import fetch_routing, confidence_color

def test_fetch_routing_no_db():
    with patch("panes.routing._pg_conn", side_effect=Exception("no db")):
        rows = fetch_routing()
    assert rows == []

def test_confidence_color_high():
    assert confidence_color(0.95) == "green"

def test_confidence_color_medium():
    assert confidence_color(0.7) == "yellow"

def test_confidence_color_low():
    assert confidence_color(0.4) == "red"
```

- [ ] **Step 2: Run to verify failure**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
python3 -m pytest tests/test_panes_routing.py -v 2>&1 | head -10
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: Create panes/routing.py**

```python
"""panes/routing.py — Live routing decision feed pane.
b17: WGRV1  ΔΣ=42
"""
import os

from textual.containers import Container
from textual.widgets import DataTable, Label

import grove_reader
from panes.chat import sender_color


def _pg_conn():
    import psycopg2
    return psycopg2.connect(
        dbname=os.environ.get("WILLOW_PG_DB",   "willow_19"),
        user=os.environ.get("WILLOW_PG_USER", os.environ.get("USER", "")),
    )


def confidence_color(conf: float) -> str:
    if conf >= 0.85:
        return "green"
    if conf >= 0.6:
        return "yellow"
    return "red"


def fetch_routing(limit: int = 20) -> list[dict]:
    """Return recent routing decisions. Never raises."""
    try:
        return grove_reader.routing_decisions(limit=limit)
    except Exception:
        return []


class RoutingPane(Container):
    def compose(self):
        yield Label("  Routing — live decision feed", id="routing-title")
        table = DataTable(id="routing-table", cursor_type="row")
        table.add_columns("Time", "Prompt", "→ Target", "Conf")
        yield table

    def on_mount(self) -> None:
        self.set_interval(5, self.refresh_data)
        self.refresh_data()

    def refresh_data(self) -> None:
        table = self.query_one("#routing-table", DataTable)
        table.clear()
        for d in fetch_routing():
            ts      = d.get("ts")
            ts_str  = ts.strftime("%H:%M") if hasattr(ts, "strftime") else str(ts)[:5]
            snippet = (d.get("prompt_snippet") or "")[:50]
            target  = d.get("routed_to") or "?"
            conf    = float(d.get("confidence", 1.0))
            color   = sender_color(target)
            c_color = confidence_color(conf)
            table.add_row(
                ts_str,
                snippet,
                f"[{color} bold]{target}[/]",
                f"[{c_color}]{conf:.0%}[/]",
            )
```

- [ ] **Step 4: Run tests**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
python3 -m pytest tests/test_panes_routing.py -v
```

Expected: 4 PASS

- [ ] **Step 5: Add Routing tab to app.py**

```python
from panes.routing import RoutingPane
```

In `compose()`:
```python
with TabPane("Routing", id="tab-routing"):
    yield RoutingPane(id="routing-pane")
```

Add to `_do_refresh()`:
```python
try:
    self.query_one("#routing-pane", RoutingPane).refresh_data()
except Exception:
    pass
```

- [ ] **Step 6: Commit**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
git add panes/routing.py tests/test_panes_routing.py app.py
git commit -m "feat(routing): RoutingPane — live willow_route decision feed"
```

---

## Task 10: KnowledgePane

**Files:**
- Create: `panes/knowledge.py`
- Create: `tests/test_panes_knowledge.py`
- Modify: `app.py` — add Knowledge tab

- [ ] **Step 1: Write the tests**

Create `tests/test_panes_knowledge.py`:

```python
"""tests/test_panes_knowledge.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from unittest.mock import patch
from panes.knowledge import search_kb, truncate_text

def test_search_kb_no_db():
    with patch("panes.knowledge._pg_conn", side_effect=Exception("no db")):
        rows = search_kb("test query")
    assert rows == []

def test_search_kb_empty_query():
    rows = search_kb("")
    assert rows == []

def test_truncate_short():
    assert truncate_text("hello", 20) == "hello"

def test_truncate_long():
    result = truncate_text("a" * 100, 20)
    assert len(result) <= 23
    assert result.endswith("…")
```

- [ ] **Step 2: Run to verify failure**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
python3 -m pytest tests/test_panes_knowledge.py -v 2>&1 | head -10
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: Create panes/knowledge.py**

```python
"""panes/knowledge.py — Knowledge base search pane.
b17: WGRV1  ΔΣ=42
"""
import os

from textual import on
from textual.containers import Container
from textual.widgets import DataTable, Input, Label


def _pg_conn():
    import psycopg2
    return psycopg2.connect(
        dbname=os.environ.get("WILLOW_PG_DB",   "willow_19"),
        user=os.environ.get("WILLOW_PG_USER", os.environ.get("USER", "")),
    )


def truncate_text(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len] + "…"


def search_kb(query: str, limit: int = 50) -> list[dict]:
    """Full-text search against public.knowledge. Never raises."""
    if not query.strip():
        return []
    try:
        conn = _pg_conn()
        cur  = conn.cursor()
        cur.execute("""
            SELECT id, title, summary, domain, weight
            FROM public.knowledge
            WHERE (title ILIKE %s OR summary ILIKE %s)
              AND domain != 'archived'
            ORDER BY weight DESC NULLS LAST, id DESC
            LIMIT %s
        """, (f"%{query}%", f"%{query}%", limit))
        rows = cur.fetchall()
        conn.close()
        return [
            {"id": r[0], "title": r[1] or "", "summary": r[2] or "",
             "domain": r[3] or "", "weight": r[4] or 0}
            for r in rows
        ]
    except Exception:
        return []


class KnowledgePane(Container):
    def compose(self):
        yield Label("  Knowledge — search (Enter to run)", id="kb-title")
        yield Input(placeholder="Search…", id="kb-search")
        table = DataTable(id="kb-table", cursor_type="row")
        table.add_columns("ID", "Title", "Domain", "W")
        yield table

    @on(Input.Submitted, "#kb-search")
    def _run_search(self, event: Input.Submitted) -> None:
        query = event.value.strip()
        table = self.query_one("#kb-table", DataTable)
        table.clear()
        if not query:
            return
        for row in search_kb(query):
            table.add_row(
                str(row["id"]),
                truncate_text(row["title"],   50),
                row["domain"],
                str(row["weight"]),
            )
```

- [ ] **Step 4: Run tests**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
python3 -m pytest tests/test_panes_knowledge.py -v
```

Expected: 4 PASS

- [ ] **Step 5: Add Knowledge tab to app.py**

```python
from panes.knowledge import KnowledgePane
```

In `compose()`:
```python
with TabPane("Knowledge", id="tab-knowledge"):
    yield KnowledgePane(id="knowledge-pane")
```

- [ ] **Step 6: Commit**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
git add panes/knowledge.py tests/test_panes_knowledge.py app.py
git commit -m "feat(knowledge): KnowledgePane — KB full-text search"
```

---

## Task 11: Thin app.py wire-up + final CSS

This task finalises `app.py` — adds all bindings, tab order, CSS for the Discord color spec, and cleans up any remaining cruft.

**Files:**
- Modify: `app.py`

- [ ] **Step 1: Replace app.py with the final version**

`app.py` after all pane extractions should look like this (full replacement):

```python
#!/usr/bin/env python3
"""
app.py — Willow Grove (Textual dashboard).
b17: WGRV1  ΔΣ=42

Run: python3 app.py
"""
import os
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, TabbedContent, TabPane

from panes.overview  import OverviewPane
from panes.chat      import ChatPane
from panes.tasks     import TasksPane
from panes.agents    import AgentsPane
from panes.routing   import RoutingPane
from panes.knowledge import KnowledgePane
from panes.providers import ProvidersPane
from panes.skills    import SkillsPane
from panes.health    import HealthPane
from panes.logs      import LogsPane

WILLOW_ROOT = Path(os.environ.get("WILLOW_ROOT", Path.home() / "github" / "willow-1.9"))


class WillowGrove(App):
    CSS = """
    Screen { background: #0d1117; }

    Header {
        background: #161b22;
        color: #58a6ff;
        text-style: bold;
    }

    Footer { background: #161b22; }

    TabbedContent { height: 1fr; }
    TabPane       { height: 1fr; padding: 0; }

    WillowHero {
        height: 8;
        content-align: center middle;
        color: #3fb950;
        text-style: bold;
    }

    #overview-title, #tasks-title, #agents-title,
    #routing-title, #kb-title, #prov-title,
    #skills-title, #health-title, #logs-title {
        color: #58a6ff;
        padding: 1 2;
        text-style: bold;
    }

    StatusRow {
        padding: 0 4;
        height: 1;
    }

    Rule { margin: 1 0; color: #30363d; }

    DataTable {
        height: 1fr;
        margin: 0 2;
    }

    #skill-detail {
        height: 12;
        margin: 1 2;
        border: round #30363d;
        padding: 1;
        color: #8b949e;
    }

    Log {
        margin: 0 2;
        height: 1fr;
        border: round #30363d;
    }

    ChatPane #channel-sidebar {
        width: 26;
        background: #161b22;
        border-right: solid #30363d;
    }

    ChatPane #msg-log {
        height: 1fr;
        padding: 1 2;
    }
    """

    BINDINGS = [
        Binding("q",   "quit",    "Quit"),
        Binding("r",   "refresh", "Refresh"),
        Binding("1",   "switch_tab('tab-overview')",  "Overview",  show=False),
        Binding("2",   "switch_tab('tab-chat')",      "Chat",      show=False),
        Binding("3",   "switch_tab('tab-tasks')",     "Tasks",     show=False),
        Binding("4",   "switch_tab('tab-agents')",    "Agents",    show=False),
        Binding("5",   "switch_tab('tab-routing')",   "Routing",   show=False),
        Binding("6",   "switch_tab('tab-knowledge')", "Knowledge", show=False),
    ]

    TITLE     = "Willow Grove"
    SUB_TITLE = f"local-first AI stack — {WILLOW_ROOT}"

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent():
            with TabPane("Overview",  id="tab-overview"):
                yield OverviewPane(id="overview-pane")
            with TabPane("Chat",      id="tab-chat"):
                yield ChatPane(id="chat-pane")
            with TabPane("Tasks",     id="tab-tasks"):
                yield TasksPane(id="tasks-pane")
            with TabPane("Agents",    id="tab-agents"):
                yield AgentsPane(id="agents-pane")
            with TabPane("Routing",   id="tab-routing"):
                yield RoutingPane(id="routing-pane")
            with TabPane("Knowledge", id="tab-knowledge"):
                yield KnowledgePane(id="knowledge-pane")
            with TabPane("Providers", id="tab-providers"):
                yield ProvidersPane(id="providers-pane")
            with TabPane("Skills",    id="tab-skills"):
                yield SkillsPane(id="skills-pane")
            with TabPane("Health",    id="tab-health"):
                yield HealthPane(id="health-pane")
            with TabPane("Logs",      id="tab-logs"):
                yield LogsPane(id="logs-pane")
        yield Footer()

    def on_mount(self) -> None:
        self._do_refresh()
        self.set_interval(30, self._do_refresh)

    def _do_refresh(self) -> None:
        for pane_id, pane_class in [
            ("#overview-pane",  OverviewPane),
            ("#providers-pane", ProvidersPane),
            ("#skills-pane",    SkillsPane),
            ("#logs-pane",      LogsPane),
        ]:
            try:
                self.query_one(pane_id, pane_class).refresh_data()
            except Exception:
                pass

    def action_refresh(self) -> None:
        self._do_refresh()
        self.notify("Refreshed")

    def action_switch_tab(self, tab_id: str) -> None:
        try:
            self.query_one(TabbedContent).active = tab_id
        except Exception:
            pass


if __name__ == "__main__":
    WillowGrove().run()
```

- [ ] **Step 2: Run full test suite**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
python3 -m pytest tests/ -q
```

Expected: all tests pass

- [ ] **Step 3: Verify app imports cleanly**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
python3 -c "from app import WillowGrove; print('ok')"
```

Expected: `ok`

- [ ] **Step 4: Commit**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
git add app.py
git commit -m "feat(app): final wire-up — 10 tabs, Discord CSS, number-key nav"
```

---

## Phase Completion Checklist

Run before declaring the plan done:

- [ ] `python3 -m pytest tests/ -q` — all pass
- [ ] `python3 -c "from app import WillowGrove"` — no import errors
- [ ] `python3 app.py` — app launches, Hero animates, all 10 tabs navigate
- [ ] Chat tab: channels load, messages render, send works
- [ ] Tasks tab: table populates
- [ ] Agents tab: last-seen agents shown
- [ ] Routing tab: decision feed shows (may be empty if routing not active)
- [ ] Knowledge tab: search returns results
- [ ] Overview: CPU/mem/disk bars render, Hero animates
- [ ] Number keys 1-6 switch tabs

---

## Self-Review

**Spec coverage:**
- ✅ Animated willow Hero (`widgets/hero.py` — 10-frame 3-pose cycle)
- ✅ Chat tab with LISTEN/NOTIFY real-time (`panes/chat.py`)
- ✅ Tasks tab — Kart queue (`panes/tasks.py`)
- ✅ Agents tab — active agents with age/state (`panes/agents.py`)
- ✅ Routing tab — decision feed (`panes/routing.py`)
- ✅ Knowledge search (`panes/knowledge.py`)
- ✅ Overview sysinfo — CPU/mem/disk/temp (`panes/overview.py`)
- ✅ Discord-skin CSS — `#0d1117` bg, blurple accent, agent hash colors
- ✅ Number-key tab navigation (1-6)
- ✅ Existing tabs preserved (Providers, Skills, Health, Logs)

**Gaps:** The Discord 4-column layout (server strip + channel list + main + members) from the beauty spec is not implemented — this plan uses Textual's standard tab layout. That is a future visual pass once all features are working.

**Placeholder scan:** None found. All steps contain complete code.

**Type consistency:**
- `StatusRow.set_status(ok: bool | None, value: str)` — used consistently across all panes
- `sender_color(name: str) -> str` — defined in `panes/chat.py`, imported by `panes/agents.py` and `panes/routing.py`
- `_pg_conn()` — defined independently in each pane (not shared) to avoid circular imports
- `grove_reader.grove_channels()`, `.grove_messages()`, `.grove_agents()`, `.routing_decisions()` — all exist in `grove_reader.py`

---

ΔΣ=42
