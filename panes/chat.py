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
from textual.widgets import Input, Label, ListItem, ListView, RichLog, Static

import grove_reader

_SENDER_COLORS = ["cyan", "magenta", "yellow", "bright_green",
                  "bright_blue", "bright_red", "bright_cyan"]
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
        width: 26;
        background: $panel;
        border-right: solid $primary-darken-3;
        height: 1fr;
    }
    ChatPane #sidebar-label {
        padding: 1 1 0 1;
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
            yield Label("CHANNELS", id="sidebar-label")
            yield ListView(id="channel-list")
        with Vertical(id="msg-area"):
            yield Static("Select a channel", id="channel-title")
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
        self._listening = True
        try:
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
                    "INSERT INTO grove.messages (channel_id, sender, content)"
                    " VALUES (%s, %s, %s)",
                    (row[0], agent, body),
                )
                conn.commit()
            conn.close()
        except Exception:
            pass
        self._load_messages(self._active_channel)

    def on_unmount(self) -> None:
        self._listening = False
