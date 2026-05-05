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
from textual.containers import Container, Vertical
from textual.message import Message
from textual.widgets import Input, Label, ListItem, ListView, RichLog, Static

import grove_db
import grove_reader

_SENDER_COLORS = ["cyan", "magenta", "yellow", "bright_green",
                  "bright_blue", "bright_red", "bright_cyan"]
_AGENT_CHANNELS = {"auto", "hanuman", "loki", "heimdallr", "vishwakarma"}
_COORD_CHANNELS = {"fleet", "architecture", "handoffs", "general"}
_GROUP_LABELS   = {0: "AGENTS", 1: "COORDINATION", 2: "PROJECT"}


def sender_color(name: str) -> str:
    idx = int(hashlib.md5(name.encode()).hexdigest(), 16) % len(_SENDER_COLORS)
    return _SENDER_COLORS[idx]


_TYPED_CONTENT_PREFIXES = ("[image:", "[audio:", "[file:", "[code:")

def render_content(content: str) -> str:
    """Detect typed content prefix ([image: path], etc.) and render as plain text."""
    for prefix in _TYPED_CONTENT_PREFIXES:
        if content.startswith(prefix):
            kind = prefix[1:-1].upper()
            inner = content[len(prefix):]
            if inner.endswith("]"):
                inner = inner[:-1]
            path = inner.strip()
            ack = "✓" if os.path.exists(path) else "not found"
            return f"{kind}: {path} [{ack}]"
    return content


def format_ts(ts) -> str:
    if ts is None:
        return ""
    if isinstance(ts, datetime):
        return ts.strftime("%H:%M")
    s = str(ts)
    return s[11:16] if len(s) >= 16 else s[:5]


def _channel_group(name: str) -> tuple[int, str]:
    if name in _AGENT_CHANNELS:
        return (0, name)
    if name in _COORD_CHANNELS:
        return (1, name)
    return (2, name)


def sort_channels(channels: list[dict]) -> list[dict]:
    return sorted(channels, key=lambda c: _channel_group(c["name"]))


def _build_channel_label(ch: dict) -> str:
    """Build the markup label for a channel list item."""
    name        = ch["name"]
    unread      = ch.get("unread", 0)
    agent_name  = ch.get("agent_name")
    agent_part  = f"  [dim]{agent_name}[/]" if agent_name else ""
    unread_part = f"  [yellow bold]{unread}[/]" if unread else ""
    return f"# {name}{agent_part}{unread_part}"



class ChannelOpened(Message):
    """Posted by ChannelList when the user selects a channel."""
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name


class CursorAdvanced(Message):
    """Posted by ChatPane when it advances a channel cursor (marks messages read)."""
    def __init__(self, channel: str, last_id: int) -> None:
        super().__init__()
        self.channel = channel
        self.last_id = last_id


class ChannelItem(ListItem):
    def __init__(self, channel: dict):
        super().__init__()
        self.channel = channel

    def compose(self):
        yield Label(_build_channel_label(self.channel), markup=True)


class SectionHeader(ListItem):
    """Non-selectable group divider in the channel list."""
    def __init__(self, title: str) -> None:
        super().__init__(disabled=True)
        self._title = title

    def compose(self):
        yield Label(f"[dim]{self._title}[/]", markup=True)


class ChannelList(Vertical):
    """Standalone channel list widget — usable by ContextPanel independently of ChatPane."""

    DEFAULT_CSS = """
    ChannelList {
        width: 1fr;
        height: 1fr;
        background: $panel;
    }
    ChannelList #cl-label {
        padding: 1 1 0 1;
        color: $text-muted;
        text-style: bold;
    }
    ChannelList SectionHeader {
        background: $panel;
        padding: 1 1 0 1;
        color: $text-muted;
        text-style: bold;
    }
    ChannelList SectionHeader:hover {
        background: $panel;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._channels: list[dict] = []
        self._cursors:  dict       = {}
        self._cursors_initialized  = False

    def compose(self):
        yield Label("CHANNELS", id="cl-label")
        yield ListView(id="cl-channel-list")

    def on_mount(self) -> None:
        self.set_interval(5, self._poll)
        self._poll()

    @work(thread=True)
    def _poll(self) -> None:
        try:
            channels = grove_reader.grove_channels(last_seen_ids=self._cursors)
            if not self._cursors_initialized:
                for ch in channels:
                    self._cursors[ch["name"]] = ch.get("max_id", 0)
                self._cursors_initialized = True
                channels = grove_reader.grove_channels(last_seen_ids=self._cursors)
            new = sort_channels(channels)
            new_snap = [(c["name"], c.get("unread", 0)) for c in new]
            old_snap = [(c["name"], c.get("unread", 0)) for c in self._channels]
            if new_snap != old_snap:
                self._channels = new
                self.app.call_from_thread(self._rebuild_list, new)
        except Exception:
            pass

    def _rebuild_list(self, channels: list) -> None:
        lst = self.query_one("#cl-channel-list", ListView)
        lst.clear()
        current_group = -1
        for ch in channels:
            grp, _ = _channel_group(ch["name"])
            if grp != current_group:
                current_group = grp
                lst.append(SectionHeader(_GROUP_LABELS[grp]))
            lst.append(ChannelItem(ch))

    @on(ListView.Selected, "#cl-channel-list")
    def _channel_clicked(self, event: ListView.Selected) -> None:
        if isinstance(event.item, ChannelItem):
            self.post_message(ChannelOpened(event.item.channel["name"]))

    def on_cursor_advanced(self, event: CursorAdvanced) -> None:
        """Sync our unread cursor when ChatPane marks a channel as read."""
        self._cursors[event.channel] = event.last_id


class ChatPane(Container):
    DEFAULT_CSS = """
    ChatPane {
        layout: vertical;
        height: 1fr;
    }
    ChatPane #channel-title {
        height: 1;
        padding: 0 2;
        background: $panel;
        color: $accent;
        text-style: bold;
        border-bottom: solid $primary-darken-3;
    }
    ChatPane RichLog {
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
    ChatPane #agent-status {
        height: 1;
        padding: 0 2;
        color: #8b949e;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._active_channel: str  = ""
        self._active_agent:   str  = ""
        self._channels: list[dict] = []
        self._cursors:  dict       = {}
        self._cursors_initialized  = False
        self._listening            = False

    def compose(self):
        yield Static("Select a channel", id="channel-title")
        yield Static("", id="agent-status", markup=True)
        yield RichLog(id="msg-log", highlight=False, markup=True, wrap=True)
        yield Input(placeholder="Message…", id="msg-input")

    def on_mount(self) -> None:
        self.set_interval(5, self._poll)
        self._poll()
        self._start_listener()

    @work(thread=True)
    def _poll(self) -> None:
        try:
            channels = grove_reader.grove_channels(last_seen_ids=self._cursors)
            # On first poll only: initialize cursors to max_id so existing
            # messages don't count as unread, then re-fetch with those cursors
            # so the first render is accurate rather than flashing inflated counts.
            if not self._cursors_initialized:
                for ch in channels:
                    self._cursors[ch["name"]] = ch.get("max_id", 0)
                self._cursors_initialized = True
                channels = grove_reader.grove_channels(last_seen_ids=self._cursors)
            new_channels = sort_channels(channels)
            # Only rebuild the list when something actually changed — prevents
            # the 5s clear/rebuild cycle from causing visible flicker.
            new_snapshot = [(c["name"], c.get("unread", 0)) for c in new_channels]
            old_snapshot = [(c["name"], c.get("unread", 0)) for c in self._channels]
            if new_snapshot != old_snapshot:
                self._channels = new_channels
                self.app.call_from_thread(self._rebuild_channel_list, new_channels)
            auto_open = not self._active_channel and bool(new_channels)
            if auto_open:
                first = new_channels[0]["name"]
                self.app.call_from_thread(self._open_channel, first)
        except Exception:
            pass

    def _rebuild_channel_list(self, channels: list) -> None:
        pass  # channel list lives in ContextPanel's ChannelList widget

    @work(thread=True)
    def _start_listener(self) -> None:
        self._listening = True
        try:
            conn = grove_db.listen_connection()
            cur  = conn.cursor()
            # Cache channel_id → name
            cur.execute("SELECT id, name FROM grove.channels WHERE is_archived = FALSE")
            ch_map = {row[0]: row[1] for row in cur.fetchall()}
            cur.execute("LISTEN grove_channel")
            while self._listening:
                if select.select([conn], [], [], 1.0)[0]:
                    conn.poll()
                    notified_channels: set[str] = set()
                    while conn.notifies:
                        n = conn.notifies.pop(0)
                        try:
                            ch_id = int(n.payload)
                            if ch_id not in ch_map:
                                cur.execute("SELECT id, name FROM grove.channels WHERE is_archived = FALSE")
                                ch_map = {row[0]: row[1] for row in cur.fetchall()}
                            name = ch_map.get(ch_id)
                            if name:
                                notified_channels.add(name)
                        except (ValueError, TypeError):
                            pass
                    if notified_channels:
                        self.app.call_from_thread(self._on_notify, notified_channels)
        except Exception:
            pass

    def _on_notify(self, notified_channels: set[str]) -> None:
        if self._active_channel in notified_channels:
            self._clear_agent_status()
            self._load_messages(self._active_channel)
        # Badge counts for non-active channels update on the next scheduled
        # _poll (5s). Calling _poll here caused ListView flicker under load.

    def _clear_agent_status(self) -> None:
        from textual.css.query import NoMatches
        try:
            self.query_one("#agent-status", Static).update("")
        except NoMatches:
            pass

    def _open_channel(self, name: str) -> None:
        if name != self._active_channel:
            self._cursors.pop(name, None)  # force full reload on channel switch
        self._active_channel = name
        ch = next((c for c in self._channels if c["name"] == name), {})
        self._active_agent = ch.get("agent_name") or ""
        if self._active_agent:
            title = f"# {name}  [dim]· {self._active_agent}[/]"
        else:
            title = f"# {name}"
        self.query_one("#channel-title", Static).update(title)
        self._clear_agent_status()
        try:
            import soil as _soil
            _soil.put("willow-dashboard/active", "channel", {"name": name})
        except Exception:
            pass
        self._load_messages(name)

    @work(thread=True)
    def _dispatch_to_agent(self, agent: str, message: str, channel: str) -> None:
        """Post a dispatch request to #dispatch grove channel."""
        import json as _json
        conn = grove_db.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id FROM grove.channels WHERE name = 'dispatch' LIMIT 1"
            )
            row = cur.fetchone()
            if row:
                payload = _json.dumps({
                    "to":            agent,
                    "prompt":        message,
                    "reply_channel": channel,
                })
                cur.execute(
                    "INSERT INTO grove.messages (channel_id, sender, content)"
                    " VALUES (%s, %s, %s)",
                    (row[0], grove_reader.dashboard_grove_sender(), payload),
                )
                conn.commit()
        except Exception:
            pass
        finally:
            grove_db.release_connection(conn)

    @work(thread=True)
    def _load_messages(self, channel: str) -> None:
        try:
            since = self._cursors.get(channel, 0)
            if since == 0:
                msgs = grove_reader.grove_messages(channel, limit=100)
                self.app.call_from_thread(self._render_messages, channel, msgs, True)
            else:
                msgs = grove_reader.grove_messages(channel, limit=200, since_id=since)
                self.app.call_from_thread(self._render_messages, channel, msgs, False)
        except Exception:
            pass

    def _render_messages(self, channel: str, msgs: list, clear: bool) -> None:
        if channel != self._active_channel:
            return  # stale result — user switched channels while fetch was in flight
        try:
            log = self.query_one("#msg-log", RichLog)
            if clear:
                log.clear()
            for m in msgs:
                self._write_msg(log, m)
            if msgs:
                self._cursors[channel] = msgs[-1]["id"]
                self.post_message(CursorAdvanced(channel, msgs[-1]["id"]))
                try:
                    import soil as _soil
                    _soil.put("willow-dashboard/cursors", channel, {"last_id": msgs[-1]["id"]})
                except Exception:
                    pass
                try:
                    from panes.home import DeskPane
                    self.app.query_one(DeskPane)._fetch()
                except Exception:
                    pass
        except Exception:
            pass

    def _write_msg(self, log: RichLog, m: dict) -> None:
        sender  = m.get("sender", "?")
        content = m.get("content", "")
        ts      = format_ts(m.get("created_at"))
        color   = sender_color(sender)
        name    = (sender[:13] + "…") if len(sender) > 14 else f"{sender:<14}"
        log.write(
            f"[dim]{ts}[/dim]  [{color} bold]{name}[/{color} bold]  {_e(render_content(content))}"
        )

    def on_channel_opened(self, event: ChannelOpened) -> None:
        self._open_channel(event.name)

    @on(Input.Submitted, "#msg-input")
    def _send_message(self, event: Input.Submitted) -> None:
        body = event.value.strip()
        if not body or not self._active_channel:
            return
        event.input.value = ""
        conn = grove_db.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id FROM grove.channels WHERE name = %s LIMIT 1",
                (self._active_channel,),
            )
            row = cur.fetchone()
            if row:
                sender = grove_reader.dashboard_grove_sender()
                cur.execute(
                    "INSERT INTO grove.messages (channel_id, sender, content)"
                    " VALUES (%s, %s, %s)",
                    (row[0], sender, body),
                )
                conn.commit()
        except Exception:
            pass
        finally:
            grove_db.release_connection(conn)
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

    def on_unmount(self) -> None:
        self._listening = False
