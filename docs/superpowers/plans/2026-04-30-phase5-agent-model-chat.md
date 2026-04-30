# Phase 5: Agent Model Chat — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add per-channel agent assignment to the Chat pane so messages in persona channels are dispatched to a Willow agent and the agent's reply appears in the same channel.

**Architecture:** `grove.channels` gains an `agent_name` column. When a user sends in a persona channel, the dashboard posts a dispatch message to the grove `#dispatch` channel with structured JSON (`{"to": agent, "prompt": message, "reply_channel": channel}`). The agent picks it up and writes its reply back to the persona channel. The existing LISTEN/NOTIFY pipeline delivers the reply to the UI with no extra code.

**Tech Stack:** Python 3, psycopg2, Textual, pytest

---

## Task 1: Pure functions + test file

**Files:**
- Modify: `panes/chat.py` (add `_build_channel_label`)
- Create: `tests/test_chat.py`

### Context

`panes/chat.py` currently builds channel labels inline inside `ChannelItem.compose()`. We need to extract this as a testable pure function `_build_channel_label(ch: dict) -> str` that accepts a channel dict with keys `name`, `unread`, and `agent_name`.

Current `ChannelItem.compose()` at the top of `panes/chat.py`:
```python
class ChannelItem(ListItem):
    def __init__(self, channel: dict):
        super().__init__()
        self.channel = channel

    def compose(self):
        name   = self.channel["name"]
        unread = self.channel.get("unread", 0)
        suffix = f" [yellow bold]{unread}[/]" if unread else ""
        yield Label(f"# {name}{suffix}", markup=True)
```

- [ ] **Step 1: Write the failing tests**

Create `tests/test_chat.py`:

```python
"""tests/test_chat.py
b17: WGRV1  ΔΣ=42
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from panes.chat import (
    render_content, format_ts, sort_channels, _build_channel_label
)
from datetime import datetime


def test_render_content_plain():
    assert render_content("hello world") == "hello world"


def test_render_content_image_prefix_existing(tmp_path):
    p = tmp_path / "foo.png"
    p.write_bytes(b"")
    result = render_content(f"[image: {p}]")
    assert "IMAGE" in result
    assert "foo.png" in result
    assert "✓" in result


def test_render_content_image_prefix_missing():
    result = render_content("[image: /nonexistent/foo.png]")
    assert "IMAGE" in result
    assert "not found" in result


def test_format_ts_datetime():
    dt = datetime(2026, 4, 30, 14, 35, 0)
    assert format_ts(dt) == "14:35"


def test_format_ts_string():
    assert format_ts("2026-04-30 09:12:00") == "09:12"


def test_format_ts_none():
    assert format_ts(None) == ""


def test_sort_channels_known_order():
    channels = [{"name": "architecture"}, {"name": "general"}, {"name": "readme"}]
    result = sort_channels(channels)
    assert [c["name"] for c in result] == ["general", "architecture", "readme"]


def test_sort_channels_unknown_appended_alphabetically():
    channels = [{"name": "random"}, {"name": "general"}, {"name": "zzz"}]
    result = sort_channels(channels)
    assert result[0]["name"] == "general"
    assert result[-1]["name"] == "zzz"


def test_build_channel_label_plain():
    ch = {"name": "general", "unread": 0, "agent_name": None}
    assert _build_channel_label(ch) == "# general"


def test_build_channel_label_unread():
    ch = {"name": "general", "unread": 3, "agent_name": None}
    label = _build_channel_label(ch)
    assert "# general" in label
    assert "3" in label


def test_build_channel_label_agent():
    ch = {"name": "willow-grove", "unread": 0, "agent_name": "hanuman"}
    label = _build_channel_label(ch)
    assert "# willow-grove" in label
    assert "hanuman" in label


def test_build_channel_label_agent_and_unread():
    ch = {"name": "willow-grove", "unread": 2, "agent_name": "hanuman"}
    label = _build_channel_label(ch)
    assert "# willow-grove" in label
    assert "hanuman" in label
    assert "2" in label
```

- [ ] **Step 2: Run tests — expect ImportError on `_build_channel_label`**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
python3 -m pytest tests/test_chat.py -v 2>&1 | head -30
```

Expected: `ImportError: cannot import name '_build_channel_label'`

- [ ] **Step 3: Add `_build_channel_label` to `panes/chat.py` and update `ChannelItem`**

Add this function immediately after `sort_channels` in `panes/chat.py`:

```python
def _build_channel_label(ch: dict) -> str:
    """Build the markup label for a channel list item."""
    name       = ch["name"]
    unread     = ch.get("unread", 0)
    agent_name = ch.get("agent_name")
    agent_part = f"  [dim]{agent_name}[/]" if agent_name else ""
    unread_part = f"  [yellow bold]{unread}[/]" if unread else ""
    return f"# {name}{agent_part}{unread_part}"
```

Update `ChannelItem.compose()` to use it:

```python
class ChannelItem(ListItem):
    def __init__(self, channel: dict):
        super().__init__()
        self.channel = channel

    def compose(self):
        yield Label(_build_channel_label(self.channel), markup=True)
```

- [ ] **Step 4: Run tests — all pass**

```bash
python3 -m pytest tests/test_chat.py -v
```

Expected: all 12 tests PASS

- [ ] **Step 5: Commit**

```bash
git add panes/chat.py tests/test_chat.py
git commit -m "feat(chat): extract _build_channel_label + test_chat.py"
```

---

## Task 2: Schema — `agent_name` column

**Files:**
- Modify: `grove_db.py`

### Context

`grove_db.init_schema()` creates the `grove.channels` table with this DDL (around line 76):

```python
cur.execute("""
    CREATE TABLE IF NOT EXISTS channels (
        id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        name            TEXT NOT NULL UNIQUE,
        channel_type    TEXT NOT NULL CHECK (channel_type IN ('direct','group','persona','broadcast')),
        description     TEXT,
        created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_archived     BOOLEAN DEFAULT FALSE
    )
""")
```

We need to:
1. Add `agent_name TEXT` to the DDL (for fresh installs)
2. Add an `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` after the CREATE (for existing DBs)

- [ ] **Step 1: Update the DDL in `grove_db.py`**

Change the `CREATE TABLE IF NOT EXISTS channels` block to:

```python
cur.execute("""
    CREATE TABLE IF NOT EXISTS channels (
        id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        name            TEXT NOT NULL UNIQUE,
        channel_type    TEXT NOT NULL CHECK (channel_type IN ('direct','group','persona','broadcast')),
        description     TEXT,
        agent_name      TEXT,
        created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_archived     BOOLEAN DEFAULT FALSE
    )
""")
```

- [ ] **Step 2: Add migration for existing DBs**

Immediately after the `CREATE TABLE IF NOT EXISTS channels` block (before the indexes), add:

```python
cur.execute("""
    ALTER TABLE channels ADD COLUMN IF NOT EXISTS agent_name TEXT
""")
```

- [ ] **Step 3: Verify schema applies cleanly**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
python3 -c "
import grove_db, psycopg2
conn = psycopg2.connect(dbname='willow_19', user='$(whoami)')
grove_db.init_schema(conn)
cur = conn.cursor()
cur.execute(\"SELECT column_name FROM information_schema.columns WHERE table_schema='grove' AND table_name='channels' ORDER BY ordinal_position\")
print([r[0] for r in cur.fetchall()])
conn.close()
"
```

Expected output includes `'agent_name'`.

- [ ] **Step 4: Commit**

```bash
git add grove_db.py
git commit -m "feat(db): add agent_name column to grove.channels"
```

---

## Task 3: `grove_reader` — return `agent_name` in channel dicts

**Files:**
- Modify: `grove_reader.py`

### Context

`grove_reader.grove_channels()` currently runs:

```python
cur.execute(
    "SELECT id, name FROM grove.channels "
    "WHERE is_archived = FALSE ORDER BY id"
)
channels = cur.fetchall()
result = []
for ch_id, name in channels:
    ...
    result.append({"id": ch_id, "name": name, "unread": unread, "max_id": max_id})
```

We need to also select `agent_name` and include it in each dict. If the column doesn't exist yet (older DB without migration), the query will fail — catch that and fall back to `agent_name=None` for all channels.

- [ ] **Step 1: Update `grove_channels()` in `grove_reader.py`**

Replace the SELECT and channel loop with:

```python
try:
    cur.execute(
        "SELECT id, name, agent_name FROM grove.channels "
        "WHERE is_archived = FALSE ORDER BY id"
    )
    channels = cur.fetchall()
    has_agent = True
except Exception:
    cur.execute(
        "SELECT id, name FROM grove.channels "
        "WHERE is_archived = FALSE ORDER BY id"
    )
    channels = [(row[0], row[1], None) for row in cur.fetchall()]
    has_agent = False

result = []
for row in channels:
    ch_id, name = row[0], row[1]
    agent_name  = row[2] if has_agent else None
    last_id = last_seen_ids.get(name, 0)
    cur.execute(
        "SELECT COUNT(*) FILTER (WHERE id > %s), COALESCE(MAX(id), 0) "
        "FROM grove.messages WHERE channel_id = %s AND is_deleted = 0",
        (last_id, ch_id),
    )
    r = cur.fetchone()
    unread = r[0] if r else 0
    max_id = r[1] if r else 0
    result.append({"id": ch_id, "name": name, "unread": unread,
                   "max_id": max_id, "agent_name": agent_name})
```

Note: the outer `try/except Exception: return []` already exists in `grove_channels()` — this inner try/except only wraps the first SELECT.

- [ ] **Step 2: Verify it runs without error**

```bash
python3 -c "
import grove_reader
channels = grove_reader.grove_channels()
for ch in channels:
    print(ch.get('name'), ch.get('agent_name'))
"
```

Expected: prints channel names, `agent_name` is `None` for all (no assignments yet).

- [ ] **Step 3: Commit**

```bash
git add grove_reader.py
git commit -m "feat(reader): return agent_name in grove_channels()"
```

---

## Task 4: `ChatPane` — agent dispatch + status indicator

**Files:**
- Modify: `panes/chat.py`

### Context

This task wires the agent dispatch into `ChatPane`. When a persona channel is opened, `_active_agent` is set. When the user sends a message, the message is saved to grove normally AND a dispatch message is posted to the `#dispatch` grove channel so the agent picks it up. A dim status line shows "● waiting for {agent}…" until the next NOTIFY arrives.

The dispatch is implemented as a direct Postgres INSERT into the `#dispatch` grove channel with a JSON payload — the same channel that `willow_dispatch` posts to. This requires no external dependencies.

Current `ChatPane.__init__` (around line 173):
```python
def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self._active_channel: str  = ""
    self._channels: list[dict] = []
    self._cursors:  dict       = {}
    self._cursors_initialized  = False
    self._listening            = False
```

Current `ChatPane.compose()` yields (in `msg-area`):
```python
yield Static("Select a channel", id="channel-title")
yield RichLog(id="msg-log", highlight=False, markup=True, wrap=True)
yield Input(placeholder="Message…", id="msg-input")
```

- [ ] **Step 1: Add `_active_agent` and `_agent_status` to `__init__`**

```python
def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self._active_channel: str  = ""
    self._active_agent:   str  = ""
    self._channels: list[dict] = []
    self._cursors:  dict       = {}
    self._cursors_initialized  = False
    self._listening            = False
```

- [ ] **Step 2: Add `#agent-status` Static to `compose()`**

Replace the `msg-area` compose block:

```python
with Vertical(id="msg-area"):
    yield Static("Select a channel", id="channel-title")
    yield Static("", id="agent-status", markup=True)
    yield RichLog(id="msg-log", highlight=False, markup=True, wrap=True)
    yield Input(placeholder="Message…", id="msg-input")
```

- [ ] **Step 3: Add CSS for `#agent-status` to `ChatPane.DEFAULT_CSS`**

Add after the `#channel-title` rule:

```css
ChatPane #agent-status {
    height: 1;
    padding: 0 2;
    color: #8b949e;
}
```

- [ ] **Step 4: Update `_open_channel` to set `_active_agent` and update title**

Replace the current `_open_channel`:

```python
def _open_channel(self, name: str) -> None:
    self._active_channel = name
    ch = next((c for c in self._channels if c["name"] == name), {})
    self._active_agent   = ch.get("agent_name") or ""
    if self._active_agent:
        title = f"# {name}  [dim]· {self._active_agent}[/]"
    else:
        title = f"# {name}"
    self.query_one("#channel-title", Static).update(title)
    self._clear_agent_status()
    self._load_messages(name)
```

- [ ] **Step 5: Add `_clear_agent_status` helper**

```python
def _clear_agent_status(self) -> None:
    from textual.css.query import NoMatches
    try:
        self.query_one("#agent-status", Static).update("")
    except NoMatches:
        pass
```

- [ ] **Step 6: Add `_dispatch_to_agent` worker**

```python
@work(thread=True)
def _dispatch_to_agent(self, agent: str, message: str, channel: str) -> None:
    """Post a dispatch request to #dispatch grove channel."""
    try:
        conn = _pg_conn()
        cur  = conn.cursor()
        cur.execute(
            "SELECT id FROM grove.channels WHERE name = 'dispatch' LIMIT 1"
        )
        row = cur.fetchone()
        if row:
            import json as _json
            payload = _json.dumps({
                "to":           agent,
                "prompt":       message,
                "reply_channel": channel,
            })
            cur.execute(
                "INSERT INTO grove.messages (channel_id, sender, content)"
                " VALUES (%s, %s, %s)",
                (row[0], "dashboard", payload),
            )
            conn.commit()
        conn.close()
    except Exception:
        pass
```

- [ ] **Step 7: Update `_send_message` to dispatch when `_active_agent` is set**

Replace the current `_send_message`:

```python
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
            sender = os.environ.get(
                "GROVE_SENDER",
                os.environ.get("GROVE_NAME", os.environ.get("USER", "sean")),
            )
            cur.execute(
                "INSERT INTO grove.messages (channel_id, sender, content)"
                " VALUES (%s, %s, %s)",
                (row[0], sender, body),
            )
            conn.commit()
        conn.close()
    except Exception:
        pass
    if self._active_agent:
        from textual.css.query import NoMatches
        try:
            self.query_one("#agent-status", Static).update(
                f"[dim]● waiting for {self._active_agent}…[/]"
            )
        except NoMatches:
            pass
        self._dispatch_to_agent(self._active_agent, body, self._active_channel)
    self._load_messages(self._active_channel)
```

- [ ] **Step 8: Update `_on_notify` to clear the status indicator**

Replace the current `_on_notify`:

```python
def _on_notify(self, notified_channels: set[str]) -> None:
    if self._active_channel in notified_channels:
        self._clear_agent_status()
        self._load_messages(self._active_channel)
```

- [ ] **Step 9: Run existing tests to confirm nothing broke**

```bash
python3 -m pytest tests/test_chat.py -v
```

Expected: all 12 tests PASS

- [ ] **Step 10: Smoke-test the app launches without error**

```bash
python3 -c "
import asyncio
async def test():
    from panes.chat import ChatPane
    from textual.app import App, ComposeResult
    class TestApp(App):
        def compose(self) -> ComposeResult:
            yield ChatPane()
    app = TestApp()
    async with app.run_test(headless=True) as pilot:
        pass
    print('OK')
asyncio.run(test())
"
```

Expected: `OK`

- [ ] **Step 11: Commit**

```bash
git add panes/chat.py
git commit -m "feat(chat): agent dispatch + waiting indicator for persona channels"
```

---

## Self-Review

**Spec coverage:**
- ✅ `agent_name` column added to schema (Task 2)
- ✅ ALTER TABLE migration for existing DBs (Task 2)
- ✅ `grove_channels()` returns `agent_name` (Task 3)
- ✅ `_build_channel_label` extracted and tested (Task 1)
- ✅ `ChannelItem` uses `_build_channel_label` — shows agent name (Task 1)
- ✅ `_active_agent` set on channel open (Task 4)
- ✅ Channel title shows `· agent_name` for persona channels (Task 4)
- ✅ Dispatch on send when `_active_agent` set (Task 4)
- ✅ `#agent-status` waiting indicator (Task 4)
- ✅ Indicator cleared on NOTIFY (Task 4)
- ✅ Error handling: dispatch failure is silent (Task 4)
- ✅ Error handling: older DB without `agent_name` column (Task 3)
- ✅ `ChannelList` in ContextPanel also uses `ChannelItem` — inherits agent label rendering automatically

**Note on `ChannelList`:** `ChannelList` in `panes/chat.py` also builds `ChannelItem` instances and calls `grove_channels()`. Since Task 3 adds `agent_name` to the returned dicts and Task 1 updates `ChannelItem.compose()` to use `_build_channel_label`, the left-panel channel list in ContextPanel gets agent labels for free — no separate task needed.
