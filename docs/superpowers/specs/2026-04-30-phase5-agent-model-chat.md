# Phase 5: Agent Model Chat — Design Spec
b17: WGRV1  ΔΣ=42

## Goal

Per-project agent channels in the Chat pane. Each channel can be assigned a Willow agent. When a user sends a message in an agent-backed channel, the message is dispatched to that agent via `willow_dispatch`. The agent writes its reply back to the same Grove channel. Both the user message and agent reply appear in the channel — Discord style.

## Architecture

DB-backed mapping: `grove.channels` gains an `agent_name` column. `channel_type = 'persona'` marks a channel as agent-backed. Regular channels have `NULL` for both. The assignment is **per-channel** (same agent for all participants).

**Send path:**
1. User types → message saved to `grove.messages` (existing behavior, unchanged)
2. `ChatPane` checks `_active_agent` (loaded when channel is opened)
3. If set: `willow_dispatch(to=agent_name, prompt=message, context_id=channel_name)`
4. Waiting indicator shows below channel title: `● waiting for {agent_name}…`
5. Agent writes reply to same grove channel → NOTIFY fires → `_load_messages` runs → reply appears
6. Waiting indicator clears on next NOTIFY for that channel

Non-persona channels skip steps 2–4 entirely.

## Schema

### Migration

```sql
ALTER TABLE grove.channels ADD COLUMN IF NOT EXISTS agent_name TEXT;
```

Applied in `grove_db.init_schema()` via `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` so both fresh installs and existing DBs are handled.

### Channel dict

`grove_reader.grove_channels()` returns `agent_name` (string or `None`) in each channel dict entry.

## Components

### `grove_db.py`

- Add `agent_name TEXT` to the `CREATE TABLE IF NOT EXISTS channels` DDL
- Add `ALTER TABLE grove.channels ADD COLUMN IF NOT EXISTS agent_name TEXT` after the `CREATE TABLE` so existing DBs are migrated on next boot

### `grove_reader.py`

Update `grove_channels()` SQL:
```sql
SELECT id, name, agent_name FROM grove.channels WHERE is_archived = FALSE ORDER BY id
```
Return `agent_name` in each channel dict. Gracefully handle older DBs where the column may not exist yet (catch exception, set `agent_name=None`).

### `panes/chat.py`

**`ChatPane`**

New instance variable: `_active_agent: str = ""`

`_open_channel(name)`:
- Pull `agent_name` from `self._channels` dict for the selected channel
- Set `self._active_agent = agent_name or ""`
- Update channel title: `# {name}` (regular) or `# {name}  [dim]· {agent_name}[/]` (persona)

`_send_message(event)`:
- After INSERT, if `self._active_agent`:
  - Call `willow_dispatch(to=self._active_agent, prompt=body, context_id=self._active_channel)` in a worker thread (never blocks the UI)
  - Update `#agent-status` Static to `f"● waiting for {self._active_agent}…"`
- Wrap dispatch in try/except — failure is silent, message is already saved

`_on_notify(notified_channels)`:
- Clear `#agent-status` when `_active_channel` is in `notified_channels`

New widget in `msg-area`: `Static("", id="agent-status", markup=True)` — 1 line, dim, sits between `#channel-title` and `#msg-log`.

**`ChannelItem`**

Render label with agent name when present:
- Regular: `# general`
- Persona: `# willow-grove  [dim]hanuman[/]`
- Persona + unread: `# willow-grove  [dim]hanuman[/]  [yellow bold]3[/]`

Same rendering applied in `ChannelList` (ContextPanel left panel).

## CSS additions (`panes/chat.py`)

```css
ChatPane #agent-status {
    height: 1;
    padding: 0 2;
    color: #8b949e;
}
```

## Error handling

- `willow_dispatch` failure: silent catch, message already saved, user is not blocked
- `agent_name` column absent on older DB: `grove_channels()` catches exception, returns `agent_name=None` for all channels
- Waiting indicator clears on any NOTIFY for the active channel (not just agent replies) — safe default

## Testing (`tests/test_chat.py` — new file)

Pure function tests, no DB or Textual required:

```python
def test_render_content_plain():
    assert render_content("hello world") == "hello world"

def test_render_content_image_prefix():
    result = render_content("[image: /tmp/foo.png]")
    assert "IMAGE" in result and "foo.png" in result

def test_format_ts_datetime():
    from datetime import datetime
    dt = datetime(2026, 4, 30, 14, 35, 0)
    assert format_ts(dt) == "14:35"

def test_format_ts_string():
    assert format_ts("2026-04-30 09:12:00") == "09:12"

def test_sort_channels_known_order():
    channels = [{"name": "architecture"}, {"name": "general"}, {"name": "readme"}]
    result = sort_channels(channels)
    assert [c["name"] for c in result] == ["general", "architecture", "readme"]

def test_sort_channels_unknown_last():
    channels = [{"name": "random"}, {"name": "general"}]
    result = sort_channels(channels)
    assert result[0]["name"] == "general"

def test_channel_item_label_no_agent():
    # label = "# general"
    ch = {"name": "general", "unread": 0, "agent_name": None}
    label = _build_channel_label(ch)
    assert label == "# general"

def test_channel_item_label_with_agent():
    ch = {"name": "willow-grove", "unread": 0, "agent_name": "hanuman"}
    label = _build_channel_label(ch)
    assert "willow-grove" in label and "hanuman" in label

def test_channel_item_label_unread_badge():
    ch = {"name": "general", "unread": 3, "agent_name": None}
    label = _build_channel_label(ch)
    assert "3" in label
```

`_build_channel_label(ch: dict) -> str` is extracted from `ChannelItem.compose()` as a pure function so it can be tested without Textual.

## Out of scope

- Creating/assigning agent channels from the UI (done manually in DB or via migration script for now)
- Streaming responses (agent writes one complete reply message)
- Thread replies
- Multiple agents per channel
