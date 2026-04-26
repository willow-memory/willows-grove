# Grove OS Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a working Grove OS shell with tabs layout, vitals strip, chat app, and model switcher — all inside `willow-dashboard/grove/`.

**Architecture:** New `grove/` subdirectory alongside existing `dashboard.py`. Apps are self-contained classes with a common `App` base. `Shell` owns the curses loop, tab bar, and mouse routing. Existing `grove_reader.py` and `soil.py` are reused as-is for data.

**Tech Stack:** Python 3.11+, stdlib curses + mousemask, 256-color xterm palette, psycopg2 (existing dep), urllib (stdlib, Ollama API).

---

## File Map

| File | Responsibility |
|------|----------------|
| `grove/__init__.py` | Empty package marker |
| `grove/theme.py` | 256-color palette, color pair init, rounded borders, `safe_addstr` |
| `grove/apps/__init__.py` | Empty |
| `grove/apps/base.py` | `App` ABC — render / handle_key / handle_mouse / tick |
| `grove/apps/vitals.py` | Poll Postgres + Ollama + SOIL, render one-line strip |
| `grove/apps/models.py` | Ollama model list via urllib, Enter to set active model in SOIL |
| `grove/apps/chat.py` | Channel list (left) + message view (right) + input bar |
| `grove/layouts/__init__.py` | Empty |
| `grove/layouts/tabs.py` | Top tab bar + full-height content pane + bottom status strip |
| `grove/mouse.py` | `HitRegion` + `HitMap` — register regions, resolve click to app |
| `grove/shell.py` | `Shell` — curses init, mouse init, tab management, event loop |
| `grove/__main__.py` | Entry point: `python -m grove` |
| `tests/test_theme.py` | agent_color stability, border chars, color index lookup |
| `tests/test_vitals.py` | fetch_vitals() structure with mocked urllib + psycopg2 |
| `tests/test_models.py` | model list parse, active model set/get |
| `tests/test_chat.py` | channel unread count, message format, cursor advance |
| `tests/test_mouse.py` | HitMap register + resolve |
| `tests/test_shell_tabs.py` | tab navigation, key routing, resize |

---

## Task 1: Package skeleton + theme

**Files:**
- Create: `grove/__init__.py`
- Create: `grove/apps/__init__.py`
- Create: `grove/layouts/__init__.py`
- Create: `grove/theme.py`
- Create: `tests/test_theme.py`

- [ ] **Step 1: Create package markers**

```bash
touch /home/sean-campbell/github/willow-dashboard/grove/__init__.py
touch /home/sean-campbell/github/willow-dashboard/grove/apps/__init__.py
touch /home/sean-campbell/github/willow-dashboard/grove/layouts/__init__.py
```

- [ ] **Step 2: Write failing tests**

```python
# tests/test_theme.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from grove import theme

def test_agent_color_stable():
    c1 = theme.agent_color_index("hanuman")
    c2 = theme.agent_color_index("hanuman")
    assert c1 == c2

def test_agent_color_different_names():
    colors = {theme.agent_color_index(n) for n in ["hanuman","ganesha","jeles","heimdallr"]}
    assert len(colors) > 1

def test_border_chars_complete():
    b = theme.BORDERS
    for k in ("tl","tr","bl","br","h","v"):
        assert k in b
        assert len(b[k]) == 1

def test_status_glyph_known_states():
    assert theme.status_glyph("online")  == "●"
    assert theme.status_glyph("idle")    == "○"
    assert theme.status_glyph("busy")    == "◐"
    assert theme.status_glyph("unknown") == "·"

def test_truncate():
    assert theme.truncate("hello world", 5) == "hello"
    assert theme.truncate("hi", 10) == "hi"
    assert theme.truncate("hello world", 8) == "hello..."
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd /home/sean-campbell/github/willow-dashboard && python -m pytest tests/test_theme.py -v 2>&1 | tail -20
```
Expected: `ModuleNotFoundError` or `ImportError` on `from grove import theme`.

- [ ] **Step 4: Write `grove/theme.py`**

```python
"""grove/theme.py — 256-color palette, borders, draw helpers.
b17: WDASH  ΔΣ=42
"""
import curses
import hashlib

# ── 256-color xterm indices ───────────────────────────────────────────────────
_C = {
    "bg":        235,
    "border":    238,
    "secondary": 245,
    "primary":   253,
    "accent":    99,   # blurple
    "unread":    220,  # bright yellow
    "online":    77,   # green
    "idle":      243,
    "busy":      214,  # amber
    "healthy":   77,
    "degraded":  214,
    "down":      203,  # red
    "input_bg":  236,
}

# 7 stable agent hash colors (256-color)
_AGENT_PALETTE = [87, 213, 227, 120, 111, 203, 51]

# ── curses color pair indices (20+ to avoid clashing with dashboard.py) ───────
_PAIR = {
    "primary":   20,
    "secondary": 21,
    "accent":    22,
    "unread":    23,
    "online":    24,
    "idle":      25,
    "busy":      26,
    "healthy":   27,
    "degraded":  28,
    "down":      29,
    "border":    30,
    "input":     31,
}
# Agent pairs: 40-46
_AGENT_PAIR_BASE = 40

BORDERS = {"tl": "╭", "tr": "╮", "bl": "╰", "br": "╯", "h": "─", "v": "│"}

STATUS_GLYPHS = {"online": "●", "idle": "○", "busy": "◐", "unknown": "·"}


def status_glyph(state: str) -> str:
    return STATUS_GLYPHS.get(state, "·")


def agent_color_index(name: str) -> int:
    """Return a stable 256-color index for an agent name."""
    idx = int(hashlib.md5(name.encode()).hexdigest(), 16) % len(_AGENT_PALETTE)
    return _AGENT_PALETTE[idx]


def agent_pair(name: str) -> int:
    """Return curses color pair number for an agent name (40-46)."""
    idx = int(hashlib.md5(name.encode()).hexdigest(), 16) % len(_AGENT_PALETTE)
    return _AGENT_PAIR_BASE + idx


def truncate(text: str, width: int) -> str:
    if len(text) <= width:
        return text
    if width <= 3:
        return text[:width]
    return text[:width - 3] + "..."


def init_pairs() -> None:
    """Initialize all color pairs. Call once after curses.start_color()."""
    if not curses.has_colors():
        return
    curses.start_color()
    curses.use_default_colors()
    use256 = curses.COLORS >= 256

    def _pair(idx: str, fg_key: str):
        fg = _C[fg_key] if use256 else curses.COLOR_WHITE
        curses.init_pair(_PAIR[idx], fg, -1)

    _pair("primary",   "primary")
    _pair("secondary", "secondary")
    _pair("accent",    "accent")
    _pair("unread",    "unread")
    _pair("online",    "online")
    _pair("idle",      "idle")
    _pair("busy",      "busy")
    _pair("healthy",   "healthy")
    _pair("degraded",  "degraded")
    _pair("down",      "down")
    _pair("border",    "border")
    curses.init_pair(_PAIR["input"], _C["primary"] if use256 else curses.COLOR_WHITE,
                     _C["input_bg"] if use256 else -1)

    for i, color in enumerate(_AGENT_PALETTE):
        c = color if use256 else [curses.COLOR_CYAN, curses.COLOR_MAGENTA,
            curses.COLOR_YELLOW, curses.COLOR_GREEN, curses.COLOR_BLUE,
            curses.COLOR_RED, curses.COLOR_CYAN][i]
        curses.init_pair(_AGENT_PAIR_BASE + i, c, -1)


def pair(name: str) -> int:
    """Return curses.color_pair(n) for a named color."""
    return curses.color_pair(_PAIR[name])


def safe_addstr(win, y: int, x: int, text: str, attr: int = 0) -> None:
    """Write text clipped to window bounds. Swallows curses.error."""
    if win is None:
        return
    h, w = win.getmaxyx()
    if y < 0 or y >= h or x < 0 or x >= w:
        return
    clipped = text[:max(0, w - x - 1)]
    if not clipped:
        return
    try:
        win.addstr(y, x, clipped, attr)
    except curses.error:
        pass


def draw_rounded_box(win, y: int, x: int, h: int, w: int, attr: int = 0) -> None:
    """Draw a rounded-corner box."""
    safe_addstr(win, y,         x,         BORDERS["tl"] + BORDERS["h"] * (w - 2) + BORDERS["tr"], attr)
    safe_addstr(win, y + h - 1, x,         BORDERS["bl"] + BORDERS["h"] * (w - 2) + BORDERS["br"], attr)
    for row in range(1, h - 1):
        safe_addstr(win, y + row, x,         BORDERS["v"], attr)
        safe_addstr(win, y + row, x + w - 1, BORDERS["v"], attr)
```

- [ ] **Step 5: Run tests — expect pass**

```bash
cd /home/sean-campbell/github/willow-dashboard && python -m pytest tests/test_theme.py -v 2>&1 | tail -15
```
Expected: 5 passed.

- [ ] **Step 6: Commit**

```bash
cd /home/sean-campbell/github/willow-dashboard && git add grove/ tests/test_theme.py && git commit -m "feat(grove): package skeleton + theme system (256-color, rounded borders)"
```

---

## Task 2: App base class

**Files:**
- Create: `grove/apps/base.py`

- [ ] **Step 1: Write `grove/apps/base.py`**

```python
"""grove/apps/base.py — App abstract base class.
b17: WDASH  ΔΣ=42
"""
from abc import ABC, abstractmethod
import curses


class App(ABC):
    """Base class for all Grove apps.

    Lifecycle:
        shell.attach(win)  — called when shell assigns a curses subwindow
        app.tick()         — called on each poll cycle (data refresh)
        app.render()       — called when the pane needs redrawing
        app.handle_key(k)  — returns True if consumed
        app.handle_mouse() — returns True if consumed
    """
    id: str = ""
    label: str = ""

    def __init__(self) -> None:
        self._win = None
        self._focused: bool = False

    def attach(self, win) -> None:
        self._win = win

    def focus(self) -> None:
        self._focused = True

    def blur(self) -> None:
        self._focused = False

    @property
    def win(self):
        return self._win

    @property
    def focused(self) -> bool:
        return self._focused

    def size(self) -> tuple[int, int]:
        """Return (rows, cols) of attached window. (0,0) if unattached."""
        if self._win is None:
            return (0, 0)
        return self._win.getmaxyx()

    @abstractmethod
    def render(self) -> None:
        """Draw the app into self._win. Must not raise."""

    def handle_key(self, key: int) -> bool:
        """Handle a keypress. Return True if consumed."""
        return False

    def handle_mouse(self, y: int, x: int, btn: int) -> bool:
        """Handle a mouse event at window-relative (y, x). Return True if consumed."""
        return False

    def tick(self) -> None:
        """Refresh data. Called on each poll cycle. Must not raise."""
```

- [ ] **Step 2: Verify import works**

```bash
cd /home/sean-campbell/github/willow-dashboard && python -c "from grove.apps.base import App; print('ok')"
```
Expected: `ok`

- [ ] **Step 3: Commit**

```bash
cd /home/sean-campbell/github/willow-dashboard && git add grove/apps/base.py && git commit -m "feat(grove): App ABC"
```

---

## Task 3: VitalsApp

**Files:**
- Create: `grove/apps/vitals.py`
- Create: `tests/test_vitals.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_vitals.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from unittest.mock import patch, MagicMock
import json
from grove.apps.vitals import fetch_vitals, format_vitals_line

def test_fetch_vitals_structure():
    mock_tags = json.dumps({"models": [
        {"name": "yggdrasil:v9"}, {"name": "nomic-embed-text"}
    ]}).encode()
    mock_resp = MagicMock()
    mock_resp.read.return_value = mock_tags
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_resp):
        with patch("grove.apps.vitals._pg_ok", return_value=(True, "69k atoms")):
            with patch("grove.apps.vitals._soil_ok", return_value=True):
                v = fetch_vitals()

    assert "ollama" in v
    assert v["ollama"]["ok"] is True
    assert "yggdrasil:v9" in v["ollama"]["active"]
    assert "pg" in v
    assert "soil" in v

def test_format_vitals_line_healthy():
    v = {
        "pg":     {"ok": True,  "detail": "69k atoms"},
        "ollama": {"ok": True,  "active": "yggdrasil:v9", "count": 2},
        "soil":   {"ok": True},
        "kart":   {"ok": True,  "running": 3, "queued": 5},
    }
    line = format_vitals_line(v)
    assert "pg" in line
    assert "●" in line
    assert "yggdrasil" in line

def test_format_vitals_line_pg_down():
    v = {
        "pg":     {"ok": False, "detail": "ECONNREFUSED"},
        "ollama": {"ok": False, "active": "", "count": 0},
        "soil":   {"ok": False},
        "kart":   {"ok": False, "running": 0, "queued": 0},
    }
    line = format_vitals_line(v)
    assert "○" in line
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/sean-campbell/github/willow-dashboard && python -m pytest tests/test_vitals.py -v 2>&1 | tail -10
```
Expected: `ModuleNotFoundError` on `grove.apps.vitals`.

- [ ] **Step 3: Write `grove/apps/vitals.py`**

```python
"""grove/apps/vitals.py — System vitals strip app.
b17: WDASH  ΔΣ=42
"""
import json
import os
import urllib.request
import urllib.error
from pathlib import Path
from grove.apps.base import App
from grove import theme


def _pg_ok() -> tuple[bool, str]:
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname=os.environ.get("WILLOW_PG_DB", "willow_19"),
            user=os.environ.get("WILLOW_PG_USER", os.environ.get("USER", "")),
            connect_timeout=2,
        )
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM public.knowledge")
        count = cur.fetchone()[0]
        conn.close()
        return True, f"{count:,} atoms"
    except Exception as e:
        return False, str(e)[:30]


def _ollama_ok() -> dict:
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2) as r:
            data = json.loads(r.read())
        models = [m["name"] for m in data.get("models", [])]
        ygg = sorted([m for m in models if "yggdrasil" in m.lower()], reverse=True)
        active = ygg[0] if ygg else (models[0] if models else "")
        return {"ok": True, "active": active, "count": len(models)}
    except Exception:
        return {"ok": False, "active": "", "count": 0}


def _soil_ok() -> bool:
    store = Path(os.environ.get("WILLOW_STORE_ROOT",
                 str(Path.home() / ".willow" / "store")))
    return store.exists()


def _kart_ok() -> dict:
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname=os.environ.get("WILLOW_PG_DB", "willow_19"),
            user=os.environ.get("WILLOW_PG_USER", os.environ.get("USER", "")),
            connect_timeout=2,
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT
                COUNT(*) FILTER (WHERE status='running') AS running,
                COUNT(*) FILTER (WHERE status='queued')  AS queued
            FROM willow.tasks
        """)
        row = cur.fetchone()
        conn.close()
        return {"ok": True, "running": row[0] or 0, "queued": row[1] or 0}
    except Exception:
        return {"ok": False, "running": 0, "queued": 0}


def fetch_vitals() -> dict:
    pg_ok, pg_detail = _pg_ok()
    return {
        "pg":     {"ok": pg_ok, "detail": pg_detail},
        "ollama": _ollama_ok(),
        "soil":   {"ok": _soil_ok()},
        "kart":   _kart_ok(),
    }


def format_vitals_line(v: dict) -> str:
    """Return a one-line string for the vitals strip."""
    def dot(ok): return "●" if ok else "○"

    pg   = f"pg{dot(v['pg']['ok'])}"
    olla = f"olla{dot(v['ollama']['ok'])}"
    active = v['ollama'].get('active', '')
    model = active.split(':')[0].replace('yggdrasil', 'ygg') if active else '—'
    ver   = active.split(':')[-1] if ':' in active else ''
    model_str = f"{model}:{ver}" if ver else model

    kart = v.get('kart', {})
    kart_str = (f"kart {kart['running']}/{kart['running']+kart['queued']}"
                if kart.get('ok') else "kart○")
    soil_str = f"soil{dot(v['soil']['ok'])}"

    return f" {pg}  {olla}  {kart_str}  {soil_str}  {model_str}"


class VitalsApp(App):
    id = "vitals"
    label = "Vitals"

    def __init__(self):
        super().__init__()
        self._data: dict = {}
        self._line: str = " loading..."

    def tick(self) -> None:
        try:
            self._data = fetch_vitals()
            self._line = format_vitals_line(self._data)
        except Exception:
            self._line = " vitals unavailable"

    def render(self) -> None:
        if self._win is None:
            return
        self._win.erase()
        _, w = self._win.getmaxyx()
        # Render single line with health coloring
        v = self._data
        pg_ok = v.get("pg", {}).get("ok", False)
        attr = theme.pair("healthy") if pg_ok else theme.pair("degraded")
        theme.safe_addstr(self._win, 0, 0, self._line[:w - 1], attr)
        self._win.noutrefresh()

    def line(self) -> str:
        return self._line
```

- [ ] **Step 4: Run tests**

```bash
cd /home/sean-campbell/github/willow-dashboard && python -m pytest tests/test_vitals.py -v 2>&1 | tail -15
```
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
cd /home/sean-campbell/github/willow-dashboard && git add grove/apps/vitals.py tests/test_vitals.py && git commit -m "feat(grove): VitalsApp — pg/ollama/kart/soil strip"
```

---

## Task 4: ModelsApp

**Files:**
- Create: `grove/apps/models.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_models.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from unittest.mock import patch, MagicMock
import json
from grove.apps.models import list_models, get_active_model, set_active_model

def _mock_ollama(names):
    data = json.dumps({"models": [{"name": n} for n in names]}).encode()
    resp = MagicMock()
    resp.read.return_value = data
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp

def test_list_models_returns_names():
    with patch("urllib.request.urlopen", return_value=_mock_ollama(["yggdrasil:v9", "qwen2.5:3b"])):
        models = list_models()
    assert "yggdrasil:v9" in models
    assert "qwen2.5:3b" in models

def test_list_models_empty_on_error():
    with patch("urllib.request.urlopen", side_effect=Exception("refused")):
        models = list_models()
    assert models == []

def test_set_get_active_model():
    with patch("soil.put") as mock_put, patch("soil.get", return_value={"value": "qwen2.5:3b"}):
        set_active_model("qwen2.5:3b")
        mock_put.assert_called_once_with("willow-dashboard/config", "active_model", {"value": "qwen2.5:3b"})
        model = get_active_model()
    assert model == "qwen2.5:3b"

def test_get_active_model_default():
    with patch("soil.get", return_value=None):
        model = get_active_model()
    assert model == ""
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/sean-campbell/github/willow-dashboard && python -m pytest tests/test_models.py -v 2>&1 | tail -10
```
Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Write `grove/apps/models.py`**

```python
"""grove/apps/models.py — Local + API model switcher app.
b17: WDASH  ΔΣ=42
"""
import curses
import json
import urllib.request
import urllib.error
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import soil
from grove.apps.base import App
from grove import theme


def list_models() -> list[str]:
    """Return all Ollama model names."""
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3) as r:
            data = json.loads(r.read())
        return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def get_active_model() -> str:
    rec = soil.get("willow-dashboard/config", "active_model")
    return rec.get("value", "") if rec else ""


def set_active_model(name: str) -> None:
    soil.put("willow-dashboard/config", "active_model", {"value": name})


class ModelsApp(App):
    id = "models"
    label = "Models"

    def __init__(self):
        super().__init__()
        self._models: list[str] = []
        self._active: str = ""
        self._cursor: int = 0

    def tick(self) -> None:
        self._models = list_models()
        self._active = get_active_model()
        # Default active to first yggdrasil if unset
        if not self._active and self._models:
            ygg = [m for m in self._models if "yggdrasil" in m]
            self._active = ygg[0] if ygg else self._models[0]

    def render(self) -> None:
        if self._win is None:
            return
        self._win.erase()
        h, w = self._win.getmaxyx()
        border_attr = theme.pair("border")

        theme.draw_rounded_box(self._win, 0, 0, h, w, border_attr)
        theme.safe_addstr(self._win, 0, 2, " Models ", theme.pair("accent") | curses.A_BOLD)

        if not self._models:
            theme.safe_addstr(self._win, 2, 2, "Ollama unreachable", theme.pair("secondary"))
            self._win.noutrefresh()
            return

        local = [m for m in self._models if "nomic" not in m.lower()]
        row = 2
        theme.safe_addstr(self._win, row, 2, "Local (Ollama)", theme.pair("secondary"))
        row += 1

        for i, name in enumerate(local):
            if row >= h - 1:
                break
            is_active = name == self._active
            is_cursor = i == self._cursor and self._focused
            prefix = "▌ " if is_active else "  "
            attr = (theme.pair("accent") | curses.A_BOLD) if is_active else (
                   curses.A_REVERSE if is_cursor else theme.pair("primary"))
            short = theme.truncate(name, w - 6)
            theme.safe_addstr(self._win, row, 2, prefix + short, attr)
            row += 1

        if self._focused:
            theme.safe_addstr(self._win, h - 2, 2,
                "↑↓ move  Enter switch", theme.pair("secondary"))

        self._win.noutrefresh()

    def handle_key(self, key: int) -> bool:
        local = [m for m in self._models if "nomic" not in m.lower()]
        if key == curses.KEY_UP:
            self._cursor = max(0, self._cursor - 1)
            return True
        if key == curses.KEY_DOWN:
            self._cursor = min(len(local) - 1, self._cursor + 1)
            return True
        if key in (curses.KEY_ENTER, 10, 13):
            if 0 <= self._cursor < len(local):
                set_active_model(local[self._cursor])
                self._active = local[self._cursor]
            return True
        return False
```

- [ ] **Step 4: Run tests**

```bash
cd /home/sean-campbell/github/willow-dashboard && python -m pytest tests/test_models.py -v 2>&1 | tail -10
```
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
cd /home/sean-campbell/github/willow-dashboard && git add grove/apps/models.py tests/test_models.py && git commit -m "feat(grove): ModelsApp — Ollama model list + switch"
```

---

## Task 5: ChatApp

**Files:**
- Create: `grove/apps/chat.py`
- Create: `tests/test_chat.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_chat.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from unittest.mock import patch, MagicMock
from grove.apps.chat import format_message_header, advance_cursor, ChatApp

def test_format_message_header_includes_sender():
    hdr = format_message_header("hanuman", "13:04")
    assert "hanuman" in hdr
    assert "13:04" in hdr

def test_advance_cursor_updates():
    cursors = {"general": 0, "architecture": 5}
    advance_cursor(cursors, "architecture", 10)
    assert cursors["architecture"] == 10

def test_advance_cursor_no_regression():
    cursors = {"architecture": 10}
    advance_cursor(cursors, "architecture", 7)
    assert cursors["architecture"] == 10  # never goes backwards

def test_chat_app_initial_state():
    app = ChatApp()
    assert app.id == "chat"
    assert app._active_channel == ""
    assert app._cursors == {}
    assert app._messages == []
    assert app._channels == []
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/sean-campbell/github/willow-dashboard && python -m pytest tests/test_chat.py -v 2>&1 | tail -10
```
Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Write `grove/apps/chat.py`**

```python
"""grove/apps/chat.py — Grove channel chat app.
b17: WDASH  ΔΣ=42
"""
import curses
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import soil
import grove_reader
from grove.apps.base import App
from grove import theme

_CHANNEL_ORDER = ["general", "architecture", "handoffs", "readme"]
_SIDEBAR_W = 22


def format_message_header(sender: str, time_str: str) -> str:
    return f"  {sender}  {time_str}"


def advance_cursor(cursors: dict, channel: str, msg_id: int) -> None:
    """Advance last-seen cursor for a channel. Never goes backwards."""
    if msg_id > cursors.get(channel, 0):
        cursors[channel] = msg_id


def _load_cursors() -> dict:
    rec = soil.get("willow-dashboard/channel_cursors", "cursors")
    return dict(rec) if rec else {}


def _save_cursors(cursors: dict) -> None:
    soil.put("willow-dashboard/channel_cursors", "cursors", cursors)


class ChatApp(App):
    id = "chat"
    label = "Chat"

    def __init__(self):
        super().__init__()
        self._channels: list[dict] = []     # [{id, name, unread}]
        self._active_channel: str = ""
        self._messages: list[dict] = []     # [{id, sender, content, created_at}]
        self._cursors: dict = {}            # {channel_name: last_seen_id}
        self._input: list[str] = []
        self._scroll: int = 0              # message scroll offset

    def tick(self) -> None:
        try:
            self._cursors = _load_cursors()
            self._channels = grove_reader.grove_channels(last_seen_ids=self._cursors)
            # Sort: pinned order first, then alpha
            order = {n: i for i, n in enumerate(_CHANNEL_ORDER)}
            self._channels.sort(key=lambda c: (order.get(c["name"], 99), c["name"]))
            # Default to first channel
            if not self._active_channel and self._channels:
                self._active_channel = self._channels[0]["name"]
            if self._active_channel:
                self._messages = grove_reader.grove_messages(self._active_channel, limit=100)
        except Exception:
            pass

    def _open_channel(self, name: str) -> None:
        if name == self._active_channel:
            return
        self._active_channel = name
        self._scroll = 0
        self._messages = grove_reader.grove_messages(name, limit=100)
        # Advance cursor to latest message
        if self._messages:
            advance_cursor(self._cursors, name, self._messages[-1]["id"])
            _save_cursors(self._cursors)

    def render(self) -> None:
        if self._win is None:
            return
        self._win.erase()
        h, w = self._win.getmaxyx()

        # ── Sidebar ───────────────────────────────────────────────────────────
        sidebar_w = min(_SIDEBAR_W, w // 3)
        border_attr = theme.pair("border")

        theme.draw_rounded_box(self._win, 0, 0, h, sidebar_w, border_attr)
        theme.safe_addstr(self._win, 0, 2, " Channels ", theme.pair("accent") | curses.A_BOLD)

        row = 2
        for ch in self._channels:
            if row >= h - 1:
                break
            is_active = ch["name"] == self._active_channel
            unread = ch.get("unread", 0)

            if is_active:
                prefix = "▌"
                name_attr = theme.pair("accent") | curses.A_BOLD
            else:
                prefix = " "
                name_attr = theme.pair("primary") if unread else theme.pair("secondary")

            name_str = theme.truncate(f"# {ch['name']}", sidebar_w - 6)
            theme.safe_addstr(self._win, row, 1, prefix, theme.pair("accent") if is_active else 0)
            theme.safe_addstr(self._win, row, 2, name_str, name_attr)

            if unread:
                badge = str(unread)
                badge_x = sidebar_w - len(badge) - 2
                theme.safe_addstr(self._win, row, badge_x, badge,
                                  theme.pair("unread") | curses.A_BOLD)
            row += 1

        # ── Main pane ─────────────────────────────────────────────────────────
        main_x = sidebar_w + 1
        main_w = w - main_x
        if main_w < 10:
            self._win.noutrefresh()
            return

        theme.draw_rounded_box(self._win, 0, main_x, h, main_w, border_attr)
        ch_title = f" # {self._active_channel} " if self._active_channel else " Chat "
        theme.safe_addstr(self._win, 0, main_x + 2, ch_title,
                          theme.pair("primary") | curses.A_BOLD)

        # Messages — visible_rows = h - 4 (box top + box bottom + input bar + separator)
        visible_rows = h - 5
        msg_lines = []
        for msg in self._messages:
            ts = ""
            ca = msg.get("created_at")
            if ca:
                try:
                    ts = ca.strftime("%H:%M")
                except Exception:
                    ts = str(ca)[-8:-3]
            sender = msg.get("sender", "?")
            content = msg.get("content", "")
            msg_lines.append((sender, ts, content))

        # Apply scroll
        start = max(0, len(msg_lines) - visible_rows - self._scroll)
        visible = msg_lines[start: start + visible_rows]

        msg_row = 1
        for sender, ts, content in visible:
            if msg_row >= h - 3:
                break
            # Header line
            hdr = format_message_header(sender, ts)
            sender_pair = curses.color_pair(theme.agent_pair(sender))
            theme.safe_addstr(self._win, msg_row, main_x + 1,
                              f"  {sender}", sender_pair | curses.A_BOLD)
            theme.safe_addstr(self._win, msg_row, main_x + 2 + len(sender) + 2,
                              ts, theme.pair("secondary"))
            msg_row += 1
            # Body — wrap at main_w - 6
            body_w = max(10, main_w - 7)
            for i in range(0, len(content), body_w):
                if msg_row >= h - 3:
                    break
                theme.safe_addstr(self._win, msg_row, main_x + 4,
                                  content[i:i + body_w], theme.pair("primary"))
                msg_row += 1

        # Input bar
        input_y = h - 2
        input_inner_w = max(4, main_w - 4)
        input_str = "".join(self._input)
        placeholder = f"Message #{self._active_channel}..." if self._active_channel else "Select a channel"
        display = input_str if input_str else placeholder
        input_attr = theme.pair("input") if input_str else theme.pair("secondary")
        theme.safe_addstr(self._win, input_y - 1, main_x + 1, "─" * (main_w - 2), theme.pair("border"))
        theme.safe_addstr(self._win, input_y, main_x + 2,
                          theme.truncate(display, input_inner_w), input_attr)

        self._win.noutrefresh()

    def handle_key(self, key: int) -> bool:
        if key == curses.KEY_UP:
            self._scroll += 1
            return True
        if key == curses.KEY_DOWN:
            self._scroll = max(0, self._scroll - 1)
            return True
        if key == curses.KEY_BACKSPACE or key == 127:
            if self._input:
                self._input.pop()
            return True
        if key in (curses.KEY_ENTER, 10, 13):
            msg = "".join(self._input).strip()
            if msg and self._active_channel:
                self._send(msg)
            return True
        if 32 <= key <= 126:
            self._input.append(chr(key))
            return True
        return False

    def handle_mouse(self, y: int, x: int, btn: int) -> bool:
        """Click on sidebar channel row to open it."""
        sidebar_w = min(_SIDEBAR_W, self.size()[1] // 3)
        if x < sidebar_w and 2 <= y < 2 + len(self._channels):
            ch = self._channels[y - 2]
            self._open_channel(ch["name"])
            return True
        return False

    def _send(self, text: str) -> None:
        """Write message to grove.messages via direct SQL."""
        try:
            import psycopg2
            conn = grove_reader._pg_conn()
            cur = conn.cursor()
            cur.execute("SELECT id FROM grove.channels WHERE name = %s LIMIT 1",
                        (self._active_channel,))
            row = cur.fetchone()
            if row:
                agent = os.environ.get("WILLOW_AGENT_NAME", "hanuman")
                cur.execute(
                    "INSERT INTO grove.messages (channel_id, sender, content) VALUES (%s, %s, %s)",
                    (row[0], agent, text),
                )
                conn.commit()
            conn.close()
        except Exception:
            pass
        self._input.clear()
        self._messages = grove_reader.grove_messages(self._active_channel, limit=100)
```

- [ ] **Step 4: Run tests**

```bash
cd /home/sean-campbell/github/willow-dashboard && python -m pytest tests/test_chat.py -v 2>&1 | tail -10
```
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
cd /home/sean-campbell/github/willow-dashboard && git add grove/apps/chat.py tests/test_chat.py && git commit -m "feat(grove): ChatApp — channel list + message view + input"
```

---

## Task 6: Mouse hit map

**Files:**
- Create: `grove/mouse.py`
- Create: `tests/test_mouse.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_mouse.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from grove.mouse import HitRegion, HitMap

def test_hitmap_resolve_exact():
    hm = HitMap()
    hm.register(HitRegion(y=0, x=0, h=10, w=40, app_id="chat"))
    hit = hm.resolve(5, 20)
    assert hit == "chat"

def test_hitmap_resolve_miss():
    hm = HitMap()
    hm.register(HitRegion(y=0, x=0, h=10, w=40, app_id="chat"))
    hit = hm.resolve(15, 50)
    assert hit is None

def test_hitmap_last_registered_wins():
    hm = HitMap()
    hm.register(HitRegion(y=0, x=0, h=10, w=40, app_id="chat"))
    hm.register(HitRegion(y=0, x=0, h=10, w=40, app_id="models"))
    hit = hm.resolve(5, 20)
    assert hit == "models"

def test_hitmap_clear():
    hm = HitMap()
    hm.register(HitRegion(y=0, x=0, h=10, w=40, app_id="chat"))
    hm.clear()
    assert hm.resolve(5, 20) is None

def test_local_coords():
    hm = HitMap()
    hm.register(HitRegion(y=5, x=10, h=20, w=60, app_id="chat"))
    local = hm.local_coords(12, 25)
    assert local == (7, 15)  # 12-5=7, 25-10=15
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/sean-campbell/github/willow-dashboard && python -m pytest tests/test_mouse.py -v 2>&1 | tail -10
```
Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Write `grove/mouse.py`**

```python
"""grove/mouse.py — Hit region registry for mouse click routing.
b17: WDASH  ΔΣ=42
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class HitRegion:
    y: int
    x: int
    h: int
    w: int
    app_id: str


class HitMap:
    """Stores rectangular hit regions and resolves (y, x) clicks to app ids."""

    def __init__(self):
        self._regions: list[HitRegion] = []

    def register(self, region: HitRegion) -> None:
        self._regions.append(region)

    def clear(self) -> None:
        self._regions.clear()

    def resolve(self, y: int, x: int) -> Optional[str]:
        """Return app_id for the last-registered region containing (y, x)."""
        result = None
        for r in self._regions:
            if r.y <= y < r.y + r.h and r.x <= x < r.x + r.w:
                result = r.app_id
        return result

    def local_coords(self, y: int, x: int) -> tuple[int, int]:
        """Return (y, x) relative to the region that contains this click."""
        for r in reversed(self._regions):
            if r.y <= y < r.y + r.h and r.x <= x < r.x + r.w:
                return (y - r.y, x - r.x)
        return (y, x)
```

- [ ] **Step 4: Run tests**

```bash
cd /home/sean-campbell/github/willow-dashboard && python -m pytest tests/test_mouse.py -v 2>&1 | tail -10
```
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
cd /home/sean-campbell/github/willow-dashboard && git add grove/mouse.py tests/test_mouse.py && git commit -m "feat(grove): HitMap — mouse region registry"
```

---

## Task 7: Tabs layout

**Files:**
- Create: `grove/layouts/tabs.py`
- Create: `tests/test_shell_tabs.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_shell_tabs.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from grove.layouts.tabs import TabsLayout, TabBar

def test_tabbar_renders_labels():
    bar = TabBar(["Chat", "Journal", "Models"])
    text = bar.render_text(active=0, width=80)
    assert "Chat" in text
    assert "Journal" in text
    assert "Models" in text

def test_tabbar_active_bracketed():
    bar = TabBar(["Chat", "Journal"])
    text = bar.render_text(active=0, width=80)
    assert "[Chat]" in text

def test_tabbar_inactive_plain():
    bar = TabBar(["Chat", "Journal"])
    text = bar.render_text(active=0, width=80)
    assert "Journal" in text
    assert "[Journal]" not in text

def test_tabs_layout_regions():
    layout = TabsLayout(tab_labels=["Chat", "Models"], rows=40, cols=120)
    regions = layout.compute_regions()
    ids = {r["id"] for r in regions}
    assert "tabbar" in ids
    assert "content" in ids
    assert "status" in ids

def test_tabs_layout_content_fills_middle():
    layout = TabsLayout(tab_labels=["Chat"], rows=40, cols=120)
    regions = layout.compute_regions()
    content = next(r for r in regions if r["id"] == "content")
    # Content should not start at row 0 (tabbar is above)
    assert content["row"] > 0
    # Content should not end at last row (status strip below)
    assert content["row"] + content["h"] < 40
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/sean-campbell/github/willow-dashboard && python -m pytest tests/test_shell_tabs.py -v 2>&1 | tail -10
```
Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Write `grove/layouts/tabs.py`**

```python
"""grove/layouts/tabs.py — Tab bar layout: top bar + content pane + status strip.
b17: WDASH  ΔΣ=42
"""
import curses
from grove import theme


class TabBar:
    def __init__(self, labels: list[str]):
        self._labels = labels

    def render_text(self, active: int, width: int) -> str:
        parts = []
        for i, label in enumerate(self._labels):
            parts.append(f"[{label}]" if i == active else f" {label} ")
        return "  " + "  ".join(parts)

    def render(self, win, active: int, time_str: str = "") -> None:
        if win is None:
            return
        h, w = win.getmaxyx()
        win.erase()
        # Background
        win.bkgd(" ", theme.pair("border"))

        # Left: app name + tabs
        theme.safe_addstr(win, 0, 1, "⬡ Grove", theme.pair("accent") | curses.A_BOLD)
        x = 10
        for i, label in enumerate(self._labels):
            if x >= w - 20:
                break
            if i == active:
                attr = theme.pair("primary") | curses.A_BOLD | curses.A_REVERSE
                text = f"[{label}]"
            else:
                attr = theme.pair("secondary")
                text = f" {label} "
            theme.safe_addstr(win, 0, x, text, attr)
            x += len(text) + 1

        # Right: time
        if time_str:
            ts_x = max(x + 2, w - len(time_str) - 2)
            theme.safe_addstr(win, 0, ts_x, time_str, theme.pair("secondary"))

        win.noutrefresh()


class TabsLayout:
    """Compute region rects for the tabs layout given terminal size."""

    TAB_BAR_H = 1
    STATUS_H  = 1

    def __init__(self, tab_labels: list[str], rows: int, cols: int):
        self._labels = tab_labels
        self._rows = rows
        self._cols = cols

    def compute_regions(self) -> list[dict]:
        """Return list of {id, row, col, h, w} dicts."""
        content_h = max(1, self._rows - self.TAB_BAR_H - self.STATUS_H)
        return [
            {"id": "tabbar",  "row": 0, "col": 0,
             "h": self.TAB_BAR_H, "w": self._cols},
            {"id": "content", "row": self.TAB_BAR_H, "col": 0,
             "h": content_h, "w": self._cols},
            {"id": "status",  "row": self._rows - self.STATUS_H, "col": 0,
             "h": self.STATUS_H, "w": self._cols},
        ]
```

- [ ] **Step 4: Run tests**

```bash
cd /home/sean-campbell/github/willow-dashboard && python -m pytest tests/test_shell_tabs.py -v 2>&1 | tail -10
```
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
cd /home/sean-campbell/github/willow-dashboard && git add grove/layouts/tabs.py tests/test_shell_tabs.py && git commit -m "feat(grove): TabsLayout — tab bar + content pane + status strip"
```

---

## Task 8: Shell + entry point

**Files:**
- Create: `grove/shell.py`
- Create: `grove/__main__.py`

- [ ] **Step 1: Write `grove/shell.py`**

```python
"""grove/shell.py — Grove OS shell: curses init, event loop, tab management.
b17: WDASH  ΔΣ=42
"""
import curses
import threading
import time
from datetime import datetime

from grove import theme
from grove.mouse import HitMap, HitRegion
from grove.layouts.tabs import TabBar, TabsLayout
from grove.apps.base import App

POLL_INTERVAL = 1.0   # seconds between data ticks
MIN_COLS = 80
MIN_ROWS = 24


class Shell:
    def __init__(self, apps: list[App]):
        self._apps = apps
        self._tab_labels = [a.label for a in apps]
        self._active_idx = 0
        self._hitmap = HitMap()
        self._vitals_line = ""
        self._running = False

    @property
    def active_app(self) -> App:
        return self._apps[self._active_idx]

    def _set_tab(self, idx: int) -> None:
        if 0 <= idx < len(self._apps):
            self.active_app.blur()
            self._active_idx = idx
            self.active_app.focus()

    def run(self, stdscr) -> None:
        self._running = True
        curses.curs_set(0)
        stdscr.keypad(True)
        stdscr.timeout(100)  # 100ms input timeout → ~10 fps

        # Mouse
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)

        # Colors
        theme.init_pairs()
        stdscr.bkgd(" ", theme.pair("primary"))

        # Initial tick + focus
        self._apps[0].focus()
        self._tick_all()

        # Background tick thread
        tick_thread = threading.Thread(target=self._tick_loop, daemon=True)
        tick_thread.start()

        self._layout_and_render(stdscr)

        while self._running:
            key = stdscr.getch()
            rows, cols = stdscr.getmaxyx()

            if rows < MIN_ROWS or cols < MIN_COLS:
                stdscr.erase()
                msg = f"terminal too small — resize to {MIN_COLS}×{MIN_ROWS} or larger"
                theme.safe_addstr(stdscr, rows // 2, max(0, (cols - len(msg)) // 2),
                                  msg, theme.pair("degraded"))
                stdscr.refresh()
                if key in (ord("q"), ord("Q")):
                    break
                continue

            if key == curses.KEY_RESIZE:
                self._layout_and_render(stdscr)
                continue

            if key in (ord("q"), ord("Q")):
                self._running = False
                break

            # Number keys: switch tabs
            if ord("1") <= key <= ord("9"):
                self._set_tab(key - ord("1"))
                self._layout_and_render(stdscr)
                continue

            # Tab key: cycle tabs
            if key == ord("\t"):
                self._set_tab((self._active_idx + 1) % len(self._apps))
                self._layout_and_render(stdscr)
                continue

            # Mouse
            if key == curses.KEY_MOUSE:
                try:
                    _, mx, my, _, bstate = curses.getmouse()
                    app_id = self._hitmap.resolve(my, mx)
                    # Click on tab bar: switch tab
                    if app_id == "tabbar":
                        # Find which tab was clicked by re-scanning tab positions
                        x = 10
                        for i, label in enumerate(self._tab_labels):
                            text = f"[{label}]" if i == self._active_idx else f" {label} "
                            if x <= mx < x + len(text):
                                self._set_tab(i)
                                break
                            x += len(text) + 1
                    elif app_id == self.active_app.id:
                        ly, lx = self._hitmap.local_coords(my, mx)
                        self.active_app.handle_mouse(ly, lx, int(bstate))
                    self._render(stdscr)
                except curses.error:
                    pass
                continue

            # Route to active app
            if key != -1:
                consumed = self.active_app.handle_key(key)
                if consumed:
                    self._render(stdscr)

    def _tick_all(self) -> None:
        for app in self._apps:
            try:
                app.tick()
            except Exception:
                pass

    def _tick_loop(self) -> None:
        while self._running:
            time.sleep(POLL_INTERVAL)
            self._tick_all()

    def _layout_and_render(self, stdscr) -> None:
        rows, cols = stdscr.getmaxyx()
        layout = TabsLayout(self._tab_labels, rows, cols)
        regions = layout.compute_regions()
        self._hitmap.clear()

        for r in regions:
            try:
                win = stdscr.derwin(r["h"], r["w"], r["row"], r["col"])
            except curses.error:
                continue
            if r["id"] == "tabbar":
                self._hitmap.register(HitRegion(r["row"], r["col"], r["h"], r["w"], "tabbar"))
                ts = datetime.now().strftime("%H:%M:%S")
                TabBar(self._tab_labels).render(win, self._active_idx, ts)
            elif r["id"] == "content":
                self.active_app.attach(win)
                self._hitmap.register(
                    HitRegion(r["row"], r["col"], r["h"], r["w"], self.active_app.id))
                self.active_app.render()
            elif r["id"] == "status":
                self._hitmap.register(HitRegion(r["row"], r["col"], r["h"], r["w"], "status"))
                self._render_status(win)

        curses.doupdate()

    def _render(self, stdscr) -> None:
        self._layout_and_render(stdscr)

    def _render_status(self, win) -> None:
        if win is None:
            return
        _, w = win.getmaxyx()
        win.erase()
        win.bkgd(" ", theme.pair("border"))
        # Find vitals app if present
        vitals_line = ""
        for app in self._apps:
            if app.id == "vitals":
                vitals_line = app.line() if hasattr(app, "line") else ""
                break
        if not vitals_line:
            vitals_line = " Grove OS"
        theme.safe_addstr(win, 0, 0, theme.truncate(vitals_line, w - 1), theme.pair("secondary"))
        win.noutrefresh()
```

- [ ] **Step 2: Write `grove/__main__.py`**

```python
"""grove/__main__.py — Entry point: python -m grove
b17: WDASH  ΔΣ=42
"""
import curses
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grove.shell import Shell
from grove.apps.vitals import VitalsApp
from grove.apps.chat import ChatApp
from grove.apps.models import ModelsApp


def main():
    vitals = VitalsApp()
    chat   = ChatApp()
    models = ModelsApp()

    # Vitals runs in the status strip, not as a tab
    apps = [chat, models]

    shell = Shell(apps)
    # Attach vitals for status strip data
    shell._apps.append(vitals)
    shell._tab_labels = [a.label for a in apps]  # only chat + models in tabs

    try:
        curses.wrapper(shell.run)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Smoke test — launch Grove**

```bash
cd /home/sean-campbell/github/willow-dashboard && python -m grove
```
Expected: Grove OS launches. Tab bar shows `[Chat]  Models`. `q` quits cleanly. Mouse click on Models tab switches to model list.

- [ ] **Step 4: Run full test suite**

```bash
cd /home/sean-campbell/github/willow-dashboard && python -m pytest tests/ -v 2>&1 | tail -30
```
Expected: All tests pass. No import errors.

- [ ] **Step 5: Commit**

```bash
cd /home/sean-campbell/github/willow-dashboard && git add grove/shell.py grove/__main__.py && git commit -m "feat(grove): Shell event loop + __main__ entry — Phase 1 complete"
```

---

## Self-Review

**Spec coverage:**
- [x] `grove/` subdirectory with apps, layouts, theme ✓
- [x] VitalsApp — pg/ollama/kart/soil ✓
- [x] ChatApp — channel list + message view + input + mouse ✓
- [x] ModelsApp — Ollama list + switch ✓
- [x] TabsLayout — tab bar + content + status strip ✓
- [x] Shell — event loop + mouse + tab nav + resize ✓
- [x] 256-color palette ✓
- [x] Rounded borders ✓
- [x] `python -m grove` entry point ✓
- [ ] Journal app — Phase 2
- [ ] UTETY app — Phase 2
- [ ] Other layouts (discord, slack, mission-control) — Phase 2

**Placeholder scan:** None found.

**Type consistency:** `HitRegion` fields match between `mouse.py` registration and `shell.py` usage. `App.attach(win)` signature matches all call sites. `format_message_header` signature consistent between definition and tests.

---

ΔΣ=42
