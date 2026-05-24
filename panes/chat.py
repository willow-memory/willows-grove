"""panes/chat.py — Discord social layout: server · channels · transcript · members + DMs.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import logging
import select
from contextlib import suppress

from rich.text import Text
from textual import on, work
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.css.query import NoMatches
from textual.message import Message
from textual.widgets import Input, Label, ListItem, ListView, Static
from textual.events import Key

import grove_db
import grove_reader
import soil
from grove.theme_textual import ACCENT, BG, BORDER, HEALTHY, INPUT_BG, PRIMARY, SECONDARY
from panes.chat_format import (
    _build_channel_label,
    composer_placeholder,
    format_channel_title,
    format_message_block,
    format_member_row,
    is_direct_channel,
    format_ts,
    member_presence_glyph,
    partition_channels,
    peer_from_dm,
    render_content,
    sort_channels,
)
from panes.chat_admin import can_archive_channel
from panes.chat_commands import COMMAND_HINT, execute_mod_command
from panes.chat_persona import get_reply_override, grove_dispatch_to_agent
from panes.chat_modals import ChannelCreateModal, CommandPanelModal

_log = logging.getLogger("grove.chat")

# Test compatibility — tests import from panes.chat
__all__ = [
    "format_ts",
    "render_content",
    "sort_channels",
    "_build_channel_label",
    "ChatPane",
]


def _chat_pane_from(widget) -> "ChatPane | None":
    node = widget
    for _ in range(8):
        if node is None:
            return None
        if isinstance(node, ChatPane):
            return node
        node = getattr(node, "parent", None)
    return None


class ComposerInput(Input):
    """Message composer — `:` opens mod command instead of inserting text."""

    BINDINGS = [
        Binding("colon", "open_command", "Mod command", show=False, priority=True),
    ]

    def check_consume_key(self, key: str, character: str | None) -> bool:
        if key in ("colon", ":") or character == ":":
            return False
        return super().check_consume_key(key, character)

    def action_open_command(self) -> None:
        pane = _chat_pane_from(self)
        if pane and pane.is_live() and not pane._command_mode:
            pane.action_command_line()

    async def _on_key(self, event: Key) -> None:
        if event.key in ("colon", ":") or event.character == ":":
            pane = _chat_pane_from(self)
            if pane and pane.is_live() and not pane._command_mode:
                event.stop()
                event.prevent_default()
                pane.action_command_line()
                return
        await super()._on_key(event)


class CommandInput(Input):
    """Mod command line (`:` opens this). Esc cancels."""

    def check_consume_key(self, key: str, character: str | None) -> bool:
        if key == "escape":
            return False
        return super().check_consume_key(key, character)

    async def _on_key(self, event: Key) -> None:
        if event.key == "escape":
            pane = _chat_pane_from(self)
            if pane:
                pane._exit_command_mode()
            event.prevent_default()
            event.stop()
            return
        await super()._on_key(event)


class MessageRow(Static):
    can_focus = False

    DEFAULT_CSS = f"""
    MessageRow {{
        height: auto;
        padding: 0 0 1 0;
    }}
    MessageRow:hover {{
        background: {INPUT_BG};
    }}
    MessageRow.-selected {{
        background: #1a2433;
        border-left: tall {ACCENT};
        padding-left: 1;
    }}
    MessageRow.-copied {{
        background: #1a2f1a;
    }}
    """

    def __init__(
        self,
        message_id: int,
        plain: str,
        markup: str,
        *,
        flags: set[str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(markup, markup=True, **kwargs)
        self.message_id = message_id
        self._plain = plain
        self._flags = flags or set()

    def on_click(self) -> None:
        log = self.parent
        if isinstance(log, MessageLog):
            log.select_row(self)


class MessageLog(VerticalScroll):
    can_focus = True

    DEFAULT_CSS = f"""
    MessageLog {{
        height: 1fr;
        background: {BG};
        padding: 1 2;
    }}
    MessageLog:focus {{
        outline: none;
    }}
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._msgs: list[dict] = []
        self._sel = -1
        self._width = 72

    def _rows(self) -> list[MessageRow]:
        return [c for c in self.children if isinstance(c, MessageRow)]

    def load_messages(self, msgs: list[dict], *, width: int = 72) -> None:
        self.remove_children()
        self._msgs = list(msgs)
        self._width = width
        self._sel = len(msgs) - 1 if msgs else -1
        prev_sender: str | None = None
        prev_ts = None
        for m in msgs:
            plain, markup = format_message_block(
                m.get("sender", "?"),
                m.get("content", ""),
                m.get("created_at"),
                width=width,
                prev_sender=prev_sender,
                prev_ts=prev_ts,
                flags=m.get("flags"),
            )
            self.mount(
                MessageRow(
                    int(m.get("id") or 0),
                    plain,
                    markup,
                    flags=set(m.get("flags") or ()),
                )
            )
            prev_sender = m.get("sender", "?")
            prev_ts = m.get("created_at")
        self._highlight()
        self.scroll_end(animate=False)

    def append_message(self, msg: dict, *, width: int = 72, prev_sender=None, prev_ts=None) -> None:
        self._width = width
        plain, markup = format_message_block(
            msg.get("sender", "?"),
            msg.get("content", ""),
            msg.get("created_at"),
            width=width,
            prev_sender=prev_sender,
            prev_ts=prev_ts,
            flags=msg.get("flags"),
        )
        self._msgs.append(msg)
        self._sel = len(self._msgs) - 1
        self.mount(
            MessageRow(
                int(msg.get("id") or 0),
                plain,
                markup,
                flags=set(msg.get("flags") or ()),
            )
        )
        self._highlight()
        self.scroll_end(animate=False)

    def select_row(self, row: MessageRow) -> None:
        rows = self._rows()
        if row in rows:
            self._sel = rows.index(row)
            self._highlight()
            row.scroll_visible()

    def move_selection(self, delta: int) -> None:
        if not self._msgs:
            return
        self._sel = max(0, min(len(self._msgs) - 1, self._sel + delta))
        self._highlight()
        rows = self._rows()
        if 0 <= self._sel < len(rows):
            rows[self._sel].scroll_visible()

    def selected_message(self) -> dict | None:
        if self._sel < 0 or self._sel >= len(self._msgs):
            return None
        return self._msgs[self._sel]

    def selected_id(self) -> int | None:
        msg = self.selected_message()
        if not msg:
            return None
        mid = msg.get("id")
        return int(mid) if mid is not None else None

    def update_selected_flags(self, flag: str, on: bool) -> None:
        if self._sel < 0 or self._sel >= len(self._msgs):
            return
        flags = self._msgs[self._sel].setdefault("flags", set())
        if on:
            flags.add(flag)
        else:
            flags.discard(flag)
        self._rerender_row(self._sel)

    def remove_selected(self) -> None:
        if self._sel < 0 or self._sel >= len(self._msgs):
            return
        rows = self._rows()
        if self._sel < len(rows):
            rows[self._sel].remove()
        del self._msgs[self._sel]
        self._sel = min(self._sel, len(self._msgs) - 1)
        self._highlight()

    def copy_selected(self) -> str:
        rows = self._rows()
        if 0 <= self._sel < len(rows):
            plain = rows[self._sel]._plain
            self.app.copy_to_clipboard(plain)
            rows[self._sel].add_class("-copied")
            self.set_timer(0.4, lambda: rows[self._sel].remove_class("-copied"))
            return plain
        return ""

    def _rerender_row(self, index: int) -> None:
        if index < 0 or index >= len(self._msgs):
            return
        m = self._msgs[index]
        prev_sender = self._msgs[index - 1].get("sender") if index > 0 else None
        prev_ts = self._msgs[index - 1].get("created_at") if index > 0 else None
        plain, markup = format_message_block(
            m.get("sender", "?"),
            m.get("content", ""),
            m.get("created_at"),
            width=self._width,
            prev_sender=prev_sender,
            prev_ts=prev_ts,
            flags=m.get("flags"),
        )
        rows = self._rows()
        if index < len(rows):
            rows[index].update(markup)
            rows[index]._plain = plain
            rows[index]._flags = set(m.get("flags") or ())

    def _highlight(self) -> None:
        for i, row in enumerate(self._rows()):
            row.set_class(i == self._sel, "-selected")


class ChannelOpened(Message):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name


class DmOpened(Message):
    def __init__(self, peer: str) -> None:
        super().__init__()
        self.peer = peer


class CursorAdvanced(Message):
    def __init__(self, channel: str, last_id: int) -> None:
        super().__init__()
        self.channel = channel
        self.last_id = last_id


class ServerStrip(Static):
    """Discord server rail — WILLOW home."""

    DEFAULT_CSS = f"""
    ServerStrip {{
        width: 6;
        min-width: 6;
        max-width: 6;
        height: 1fr;
        background: {BG};
        border-right: solid {BORDER};
        content-align: center top;
        padding: 1 0;
        color: {HEALTHY};
    }}
    ServerStrip:hover {{
        color: {ACCENT};
    }}
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("[bold]⬡[/]", markup=True, **kwargs)


class ChannelItem(ListItem):
    def __init__(self, channel: dict, *, active: bool = False):
        super().__init__()
        self.channel = channel
        self._active = active

    def compose(self):
        yield Label(_build_channel_label(self.channel, active=self._active), markup=True)


class SectionHeader(ListItem):
    def __init__(self, title: str) -> None:
        super().__init__(disabled=True)
        self._title = title

    def compose(self):
        yield Label(f"[dim {SECONDARY}]{self._title}[/]", markup=True)


class MemberItem(ListItem):
    def __init__(self, sender: str, age_secs: int, *, bound: bool = False):
        super().__init__()
        self.sender = sender
        self.age_secs = age_secs
        self.bound = bound

    def compose(self):
        yield Label(
            format_member_row(self.sender, self.age_secs, bound=self.bound),
            markup=True,
        )


class ChannelList(Vertical):
    """Text channels + direct messages (Discord sidebar)."""

    DEFAULT_CSS = f"""
    ChannelList {{
        width: 24;
        min-width: 24;
        max-width: 24;
        height: 1fr;
        background: {INPUT_BG};
        border-right: solid {BORDER};
    }}
    ChannelList #cl-guild-label {{
        padding: 1 1 0 1;
        color: {PRIMARY};
        text-style: bold;
    }}
    ChannelList SectionHeader {{
        background: {INPUT_BG};
        padding: 0 1;
    }}
    ChannelList SectionHeader:hover {{
        background: {INPUT_BG};
    }}
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._channels: list[dict] = []
        self._cursors: dict = {}
        self._cursors_initialized = False
        self._active_channel: str = ""

    def compose(self):
        yield Label(
            "WILLOW  [dim]n new · d archive · : mod · a/A · j/k · x f r s u[/]",
            id="cl-guild-label",
            markup=True,
        )
        yield ListView(id="cl-channel-list")

    def on_mount(self) -> None:
        self.set_interval(5, self._poll)

    def _pane_live(self) -> bool:
        chat = _chat_pane_from(self)
        return bool(chat and chat.is_live())

    def refresh_unread(self) -> None:
        self._poll_unread()

    @work(thread=True, exit_on_error=False)
    def _poll_unread(self) -> None:
        if not self._pane_live():
            return
        try:
            channels = grove_reader.grove_channels(last_seen_ids=self._cursors)
            new = sort_channels(channels)
            new_snap = [(c["name"], c.get("unread", 0)) for c in new]
            old_snap = [(c["name"], c.get("unread", 0)) for c in self._channels]
            if new_snap != old_snap:
                self._channels = new
                self.app.call_from_thread(self._rebuild_list, new)
        except Exception:
            pass

    @work(thread=True, exit_on_error=False)
    def _poll(self) -> None:
        if not self._pane_live():
            return
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

    def set_active_channel(self, name: str) -> None:
        if name == self._active_channel:
            return
        self._active_channel = name
        if self._channels:
            self._rebuild_list(self._channels)

    def _rebuild_list(self, channels: list) -> None:
        lst = self.query_one("#cl-channel-list", ListView)
        composer_had_focus = False
        chat = _chat_pane_from(self)
        if chat:
            with suppress(NoMatches):
                composer_had_focus = chat.query_one("#msg-input", Input).has_focus
        lst.clear()
        text_ch, dm_ch = partition_channels(channels)
        if text_ch:
            lst.append(SectionHeader("Text channels"))
            for ch in text_ch:
                lst.append(ChannelItem(ch, active=ch["name"] == self._active_channel))
        if dm_ch:
            lst.append(SectionHeader("Direct Messages"))
            for ch in dm_ch:
                lst.append(ChannelItem(ch, active=ch["name"] == self._active_channel))
        if chat:
            if chat.is_live() and chat._active_channel:
                chat.call_after_refresh(chat._focus_composer)
            elif composer_had_focus:
                chat.call_after_refresh(chat._focus_composer)

    @on(ListView.Selected, "#cl-channel-list")
    def _channel_clicked(self, event: ListView.Selected) -> None:
        if isinstance(event.item, ChannelItem):
            self.post_message(ChannelOpened(event.item.channel["name"]))
            chat = _chat_pane_from(self)
            if chat:
                chat.call_after_refresh(chat._focus_composer)

    def on_cursor_advanced(self, event: CursorAdvanced) -> None:
        self._cursors[event.channel] = event.last_id


class MemberList(Vertical):
    """Online / idle agents — click to open DM."""

    DEFAULT_CSS = f"""
    MemberList {{
        width: 18;
        min-width: 18;
        max-width: 18;
        height: 1fr;
        background: {INPUT_BG};
        border-left: solid {BORDER};
    }}
    MemberList #ml-label {{
        padding: 1 1 0 1;
        color: {SECONDARY};
        text-style: bold;
    }}
    MemberList SectionHeader {{
        background: {INPUT_BG};
        padding: 0 1;
    }}
    """

    def compose(self):
        yield Label("Members  a bind · A takeover", id="ml-label")
        yield ListView(id="ml-member-list")

    def on_mount(self) -> None:
        self.set_interval(10, self._poll)
        self._poll()

    def _pane_live(self) -> bool:
        chat = _chat_pane_from(self)
        return bool(chat and chat.is_live())

    @work(thread=True, exit_on_error=False)
    def _poll(self) -> None:
        if not self._pane_live():
            return
        try:
            agents = grove_reader.grove_member_roster()
            me = grove_reader.dashboard_grove_sender().lower()
            agents = [a for a in agents if a.get("sender", "").lower() != me.lower()]
            bound = ""
            chat = _chat_pane_from(self)
            if chat:
                bound = (chat._active_agent or "").lower()
            self.app.call_from_thread(self._rebuild, agents, bound)
        except Exception:
            pass

    def _rebuild(self, agents: list[dict], bound_agent: str = "") -> None:
        lst = self.query_one("#ml-member-list", ListView)
        lst.clear()
        online = [a for a in agents if member_presence_glyph(a.get("age_secs", 9999)) == "●"]
        idle = [a for a in agents if a not in online]
        if online:
            lst.append(SectionHeader("Online"))
            for a in online:
                sender = a["sender"]
                lst.append(
                    MemberItem(
                        sender,
                        a.get("age_secs", 9999),
                        bound=bool(bound_agent and sender.lower() == bound_agent),
                    )
                )
        if idle:
            lst.append(SectionHeader("Idle"))
            for a in idle:
                sender = a["sender"]
                lst.append(
                    MemberItem(
                        sender,
                        a.get("age_secs", 9999),
                        bound=bool(bound_agent and sender.lower() == bound_agent),
                    )
                )
        if not agents:
            lst.append(SectionHeader("No members yet"))
            lst.append(SectionHeader("Click to open DM"))

    @on(ListView.Selected, "#ml-member-list")
    def _member_clicked(self, event: ListView.Selected) -> None:
        if isinstance(event.item, MemberItem):
            self.post_message(DmOpened(event.item.sender))


class ChatPane(Container):
    """Discord social: server · channels · transcript · members."""

    BINDINGS = [
        Binding("i", "focus_composer", "Compose", show=False),
        Binding("/", "focus_composer", "Compose", show=False),
        Binding("escape", "focus_channels", "Channels", show=False),
        Binding("m", "focus_members", "Members", show=False),
        Binding("t", "focus_transcript", "Transcript", show=False),
        Binding("j", "msg_down", "Next msg", show=False),
        Binding("k", "msg_up", "Prev msg", show=False),
        Binding("x", "msg_delete", "Delete msg", show=False),
        Binding("f", "msg_flag_urgent", "Urgent", show=False),
        Binding("r", "msg_flag_reply", "Needs reply", show=False),
        Binding("s", "msg_flag_star", "Star", show=False),
        Binding("upper_r", "msg_flag_resolve", "Resolve", show=False),
        Binding("u", "mark_read", "Mark read", show=False),
        Binding("y", "msg_copy", "Copy msg", show=False),
        Binding("colon", "command_line", "Mod command", show=False),
        Binding("a", "bind_selected_member", "Bind agent", show=False),
        Binding("upper_a", "takeover_channel", "Takeover", show=False),
        Binding("n", "new_channel", "New channel"),
        Binding("d", "archive_channel", "Archive"),
    ]

    DEFAULT_CSS = f"""
    ChatPane {{
        layout: vertical;
        height: 1fr;
        width: 1fr;
    }}
    ChatPane #chat-body {{
        layout: horizontal;
        height: 1fr;
        width: 1fr;
    }}
    ChatPane #chat-main {{
        width: 1fr;
        height: 1fr;
        layout: vertical;
    }}
    ChatPane #channel-title {{
        height: 1;
        padding: 0 2;
        background: {INPUT_BG};
        color: {ACCENT};
        text-style: bold;
        border-bottom: solid {BORDER};
    }}
    ChatPane #agent-status {{
        height: 1;
        padding: 0 2;
        color: {SECONDARY};
    }}
    ChatPane #msg-input {{
        height: 3;
        min-height: 3;
        margin: 0 2 1 2;
        border: tall {BORDER};
    }}
    ChatPane #msg-input:focus {{
        border: tall {ACCENT};
    }}
    ChatPane #cmd-input {{
        height: 3;
        min-height: 3;
        margin: 0 2 0 2;
        border: tall {ACCENT};
        display: none;
    }}
    ChatPane #cmd-input.-visible {{
        display: block;
    }}
    ChatPane #msg-input.-hidden {{
        display: none;
    }}
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._active_channel: str = ""
        self._active_ch: dict = {}
        self._active_agent: str = ""
        self._cursors: dict = {}
        self._cursors_initialized = False
        self._listening = False
        self._listener_started = False
        self._live = False
        self._last_sender: str | None = None
        self._last_ts = None
        self._rendered_ids: set[int] = set()
        self._archive_pending: str = ""
        self._delete_pending_id: int | None = None
        self._command_mode = False

    def is_live(self) -> bool:
        return self._live

    def set_live(self, live: bool) -> None:
        if live == self._live:
            return
        self._live = live
        if not live:
            self._listening = False
            with suppress(NoMatches):
                self.query_one("#msg-input", Input).disabled = True
            return
        with suppress(NoMatches):
            self.query_one("#msg-input", Input).disabled = False
        if not self._listener_started:
            self._listener_started = True
            self._start_listener()
        self._poll()
        with suppress(NoMatches):
            self.query_one("#chat-channel-list", ChannelList)._poll()
        with suppress(NoMatches):
            self.query_one("#chat-members", MemberList)._poll()
        if self._active_channel:
            self.call_after_refresh(self._focus_composer)

    def compose(self):
        with Horizontal(id="chat-body"):
            yield ServerStrip(id="server-strip")
            yield ChannelList(id="chat-channel-list")
            with Vertical(id="chat-main"):
                yield Static("Select a channel", id="channel-title", markup=True)
                yield Static("", id="agent-status", markup=True)
                yield MessageLog(id="msg-log")
                yield CommandInput(placeholder=COMMAND_HINT, id="cmd-input", disabled=True)
                yield ComposerInput(placeholder="Select a channel…", id="msg-input", disabled=True)
            yield MemberList(id="chat-members")

    def open_dm(self, peer: str) -> None:
        """Open or create a direct message with peer."""
        ch = grove_reader.grove_get_or_create_dm(peer)
        if ch.get("name"):
            self._open_channel(ch["name"], ch)
            self._refresh_sidebar()

    def _refresh_sidebar(self) -> None:
        with suppress(NoMatches):
            cl = self.query_one("#chat-channel-list", ChannelList)
            cl._cursors_initialized = False
            cl._poll()

    def _flash_status(self, text: str) -> None:
        """Plain status line — never parse Rich markup from dynamic text."""
        with suppress(NoMatches):
            self.query_one("#agent-status", Static).update(Text(text))

    def _flash_status_dim(self, text: str) -> None:
        """Dim hint on the status line (still plain text, no markup parse)."""
        with suppress(NoMatches):
            self.query_one("#agent-status", Static).update(Text(text, style="dim"))

    def _log_command_error(self, message: str, *, exc: BaseException | None = None) -> None:
        if exc is not None:
            _log.exception("chat command: %s", message)
        else:
            _log.warning("chat command: %s", message)
        self._flash_status("")

    def _log_command_ok(self, message: str) -> None:
        _log.info("chat command: %s", message)
        short = message if len(message) <= 56 else f"{message[:53]}..."
        self._flash_status(short)

    def _clear_archive_pending(self) -> None:
        self._archive_pending = ""

    def _clear_delete_pending(self) -> None:
        self._delete_pending_id = None

    def _enter_command_mode(self) -> None:
        if not self._live or self._command_mode:
            return
        self._command_mode = True
        with suppress(NoMatches):
            cmd = self.query_one("#cmd-input", CommandInput)
            msg = self.query_one("#msg-input", ComposerInput)
            msg.value = ""
            cmd.value = ""
            cmd.disabled = False
            cmd.add_class("-visible")
            cmd.styles.display = "block"
            msg.add_class("-hidden")
            msg.styles.display = "none"
            self._flash_status_dim("mod command · Esc cancel · :help")
            self.app.set_focus(cmd, scroll_visible=True)
            cmd.cursor_position = 0

    def _exit_command_mode(self) -> None:
        if not self._command_mode:
            return
        self._command_mode = False
        with suppress(NoMatches):
            cmd = self.query_one("#cmd-input", CommandInput)
            msg = self.query_one("#msg-input", ComposerInput)
            cmd.value = ""
            cmd.disabled = True
            cmd.remove_class("-visible")
            cmd.styles.display = "none"
            msg.remove_class("-hidden")
            msg.styles.display = "block"
            if self._live and self._active_channel:
                msg.disabled = False
                self._focus_composer()

    def action_command_line(self) -> None:
        self._enter_command_mode()

    def _show_command_panel(self, title: str, body: str) -> None:
        _log.info("chat command panel (%s):\n%s", title, body)
        self.app.push_screen(CommandPanelModal(title, body))

    def _apply_command_result(self, result: dict) -> None:
        msg = result.get("message", "")
        if not result.get("ok"):
            self._log_command_error(msg or result.get("error", "command failed"))
            return
        if result.get("show_panel") and msg:
            title = str(result.get("panel_title") or "Mod command")
            self._show_command_panel(title, msg)
            self._flash_status("")
        elif result.get("log_only"):
            if msg:
                _log.info("chat command detail:\n%s", msg)
            self._flash_status("ok")
        elif msg:
            self._log_command_ok(msg)
        else:
            self._flash_status("ok")

        if result.get("mark_read_id") is not None and self._active_channel:
            last_id = int(result["mark_read_id"])
            self._cursors[self._active_channel] = last_id
            self.post_message(CursorAdvanced(self._active_channel, last_id))
            with suppress(Exception):
                soil.put(
                    "willow-dashboard/cursors",
                    self._active_channel,
                    {"last_id": last_id},
                )

        if result.get("refresh"):
            self._refresh_sidebar()

        if result.get("refresh_persona"):
            self._refresh_persona_ui()

        if result.get("clear_waiting"):
            self._clear_agent_status()

        open_ch = result.get("open_channel")
        if open_ch:
            self._open_channel(str(open_ch))

    def _run_command(self, line: str) -> None:
        try:
            result = execute_mod_command(line, active_channel=self._active_channel)
            self._apply_command_result(result)
        except Exception as exc:
            self._log_command_error(f"{line!r} failed", exc=exc)
        finally:
            self._exit_command_mode()

    def action_focus_members(self) -> None:
        with suppress(NoMatches):
            self.query_one("#ml-member-list", ListView).focus(scroll_visible=False)

    def _selected_member(self) -> str | None:
        with suppress(NoMatches):
            lst = self.query_one("#ml-member-list", ListView)
            child = lst.highlighted_child
            if child and isinstance(child, MemberItem):
                return child.sender
        return None

    def action_bind_selected_member(self) -> None:
        if not self._live or not self._active_channel:
            return
        if is_direct_channel(self._active_ch):
            self._flash_status_dim("not a group channel")
            return
        agent = self._selected_member()
        if not agent:
            self._flash_status_dim("m then j/k, a to bind")
            return
        result = grove_reader.grove_set_channel_agent(self._active_channel, agent)
        if not result.get("ok"):
            self._log_command_error(result.get("error", "bind failed"))
            return
        self._log_command_ok(f"agent → {result.get('agent', agent)}")
        self._refresh_persona_ui()

    def action_takeover_channel(self) -> None:
        result = execute_mod_command("takeover", active_channel=self._active_channel)
        self._apply_command_result(result)

    def _refresh_persona_ui(self) -> None:
        name = self._active_channel
        if not name:
            return
        try:
            channels = grove_reader.grove_channels(last_seen_ids=self._cursors)
            ch = next((c for c in channels if c["name"] == name), None)
            if ch:
                self._active_ch = ch
                self._active_agent = self._agent_for_channel(ch)
        except Exception:
            pass
        reply = get_reply_override(name)
        self.query_one("#channel-title", Static).update(
            format_channel_title(self._active_ch, reply_override=reply)
        )
        with suppress(NoMatches):
            inp = self.query_one("#msg-input", ComposerInput)
            inp.placeholder = composer_placeholder(self._active_ch or None)
        self._refresh_sidebar()
        with suppress(NoMatches):
            self.query_one("#chat-members", MemberList)._poll()

    def _set_waiting(self, agent: str) -> None:
        t = Text()
        t.append("● waiting for ", style="dim")
        t.append(agent)
        t.append("…", style="dim")
        routed = get_reply_override(self._active_channel)
        if routed and routed != self._active_channel:
            t.append(f"  → #{routed}", style="dim")
        with suppress(NoMatches):
            self.query_one("#agent-status", Static).update(t)

    def action_focus_transcript(self) -> None:
        with suppress(NoMatches):
            self.query_one("#msg-log", MessageLog).focus(scroll_visible=False)

    def action_msg_up(self) -> None:
        if not self._live:
            return
        with suppress(NoMatches):
            self.query_one("#msg-log", MessageLog).move_selection(-1)

    def action_msg_down(self) -> None:
        if not self._live:
            return
        with suppress(NoMatches):
            self.query_one("#msg-log", MessageLog).move_selection(1)

    def action_msg_copy(self) -> None:
        if not self._live:
            return
        with suppress(NoMatches):
            self.query_one("#msg-log", MessageLog).copy_selected()

    def _toggle_message_flag(self, flag: str) -> None:
        if not self._live:
            return
        with suppress(NoMatches):
            log = self.query_one("#msg-log", MessageLog)
            mid = log.selected_id()
            if not mid:
                self._flash_status_dim("select a message (j/k)")
                return
            result = grove_reader.grove_message_toggle_flag(mid, flag)
            if not result.get("ok"):
                _log.warning("flag %s failed: %s", flag, result.get("error", "unknown"))
                self._flash_status("")
                return
            log.update_selected_flags(flag, bool(result.get("on")))
            state = "on" if result.get("on") else "off"
            self._flash_status(f"{flag} {state}")

    def action_msg_flag_urgent(self) -> None:
        self._toggle_message_flag("urgent")

    def action_msg_flag_reply(self) -> None:
        self._toggle_message_flag("needs-reply")

    def action_msg_flag_star(self) -> None:
        self._toggle_message_flag("starred")

    def action_msg_flag_resolve(self) -> None:
        self._toggle_message_flag("resolved")

    def action_msg_delete(self) -> None:
        if not self._live:
            return
        with suppress(NoMatches):
            log = self.query_one("#msg-log", MessageLog)
            mid = log.selected_id()
            if not mid:
                self._flash_status_dim("select a message (j/k)")
                return
            if self._delete_pending_id != mid:
                self._delete_pending_id = mid
                self._flash_status_dim("Press x again to delete message")
                self.set_timer(3.0, self._clear_delete_pending)
                return
            self._delete_pending_id = None
            result = grove_reader.grove_message_delete(mid)
            if not result.get("ok"):
                _log.warning("delete message failed: %s", result.get("error", "unknown"))
                self._flash_status("")
                return
            log.remove_selected()
            self._rendered_ids.discard(mid)
            self._flash_status("message deleted")

    def action_mark_read(self) -> None:
        if not self._live or not self._active_channel:
            return
        result = grove_reader.grove_mark_channel_read(self._active_channel)
        if not result.get("ok"):
            _log.warning("mark read failed: %s", result.get("error", "unknown"))
            self._flash_status("")
            return
        last_id = int(result.get("last_id") or 0)
        self._cursors[self._active_channel] = last_id
        self.post_message(CursorAdvanced(self._active_channel, last_id))
        with suppress(Exception):
            soil.put("willow-dashboard/cursors", self._active_channel, {"last_id": last_id})
        self._refresh_sidebar()
        self._flash_status(f"marked read · id {last_id}")

    def action_new_channel(self) -> None:
        if not self._live:
            return

        def _done(raw: str | None) -> None:
            if not raw:
                return
            result = grove_reader.grove_create_text_channel(raw)
            if not result.get("ok"):
                _log.warning("create channel failed: %s", result.get("error", "unknown"))
                self._flash_status("")
                return
            ch = result["channel"]
            self._refresh_sidebar()
            self._open_channel(ch["name"], ch)

        self.app.push_screen(ChannelCreateModal(), _done)

    def action_archive_channel(self) -> None:
        if not self._live or not self._active_channel:
            return
        name = self._active_channel
        if not can_archive_channel(name):
            _log.warning("cannot archive channel: %s", name)
            self._flash_status("")
            return
        if self._archive_pending != name:
            self._archive_pending = name
            self._flash_status_dim(f"Press d again to archive {name}")
            self.set_timer(3.0, self._clear_archive_pending)
            return
        self._archive_pending = ""
        result = grove_reader.grove_archive_channel(name)
        if not result.get("ok"):
            _log.warning("archive channel failed: %s", result.get("error", "unknown"))
            self._flash_status("")
            return
        self._active_channel = ""
        self._active_ch = {}
        self._refresh_sidebar()
        self._open_channel("general")

    def _resolve_channel(self, name: str) -> dict:
        with suppress(Exception):
            cl = self.query_one("#chat-channel-list", ChannelList)
            found = next((c for c in cl._channels if c["name"] == name), None)
            if found:
                return found
        return {"name": name, "channel_type": "group"}

    def _agent_for_channel(self, ch: dict) -> str:
        if ch.get("agent_name"):
            return ch["agent_name"]
        peer = peer_from_dm(ch.get("name", ""))
        return peer or ""

    def _focus_composer(self) -> None:
        if not self._live:
            return
        with suppress(NoMatches):
            inp = self.query_one("#msg-input", Input)
            inp.disabled = False
            inp.placeholder = composer_placeholder(self._active_ch or None)
            self.app.set_focus(inp, scroll_visible=True)

    def action_focus_composer(self) -> None:
        self._focus_composer()

    def action_focus_channels(self) -> None:
        with suppress(NoMatches):
            self.query_one("#cl-channel-list", ListView).focus(scroll_visible=False)

    def on_mount(self) -> None:
        self.set_interval(5, self._poll)

    @work(thread=True, exit_on_error=False)
    def _poll(self) -> None:
        if not self._live or self._active_channel:
            return
        try:
            channels = grove_reader.grove_channels(last_seen_ids=self._cursors)
            text_ch, _ = partition_channels(channels)
            pick = text_ch[0]["name"] if text_ch else (sort_channels(channels)[0]["name"] if channels else "")
            if pick:
                pick_ch = next((c for c in channels if c["name"] == pick), None)
                self.app.call_from_thread(self._open_channel, pick, pick_ch)
        except Exception:
            pass

    @work(thread=True, exit_on_error=False)
    def _start_listener(self) -> None:
        if not self._live:
            return
        self._listening = True
        try:
            conn = grove_db.listen_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM grove.channels WHERE is_archived = FALSE")
            ch_map = {row[0]: row[1] for row in cur.fetchall()}
            cur.execute("LISTEN grove_channel")
            while self._listening:
                if select.select([conn], [], [], 1.0)[0]:
                    conn.poll()
                    notified: set[str] = set()
                    while conn.notifies:
                        n = conn.notifies.pop(0)
                        try:
                            ch_id = int(n.payload)
                            if ch_id not in ch_map:
                                cur.execute(
                                    "SELECT id, name FROM grove.channels WHERE is_archived = FALSE"
                                )
                                ch_map = {row[0]: row[1] for row in cur.fetchall()}
                            name = ch_map.get(ch_id)
                            if name:
                                notified.add(name)
                        except (ValueError, TypeError):
                            pass
                    if notified:
                        self.app.call_from_thread(self._on_notify, notified)
        except Exception:
            pass

    def _on_notify(self, notified_channels: set[str]) -> None:
        watch = {self._active_channel}
        reply = get_reply_override(self._active_channel)
        if reply:
            watch.add(reply)
        if watch & notified_channels:
            self._clear_agent_status()
            if self._active_channel in notified_channels:
                self._load_messages(self._active_channel)
        with suppress(NoMatches):
            self.query_one("#chat-channel-list", ChannelList).refresh_unread()
        with suppress(NoMatches):
            self.query_one("#chat-members", MemberList)._poll()

    def _clear_agent_status(self) -> None:
        with suppress(NoMatches):
            self.query_one("#agent-status", Static).update("")

    def _open_channel(self, name: str, ch: dict | None = None) -> None:
        if name != self._active_channel:
            self._cursors.pop(name, None)
            self._last_sender = None
            self._last_ts = None
            self._rendered_ids.clear()
        self._active_channel = name
        self._active_ch = ch or self._resolve_channel(name)
        self._active_agent = self._agent_for_channel(self._active_ch)
        with suppress(Exception):
            self.query_one("#chat-channel-list", ChannelList).set_active_channel(name)
        self.query_one("#channel-title", Static).update(
            format_channel_title(
                self._active_ch,
                reply_override=get_reply_override(name),
            )
        )
        self._clear_agent_status()
        with suppress(Exception):
            soil.put("willow-dashboard/active", "channel", {"name": name})
        self._load_messages(name)
        self.call_after_refresh(self._focus_composer)

    @work(thread=True, exit_on_error=False)
    def _dispatch_to_agent(self, agent: str, message: str, channel: str) -> None:
        result = grove_dispatch_to_agent(agent, message, source_channel=channel)
        if not result.get("ok"):
            _log.warning("dispatch failed: %s", result.get("error", "unknown"))

    @work(thread=True, exit_on_error=False)
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
            return
        try:
            log = self.query_one("#msg-log", MessageLog)
            width = max(40, (log.size.width or 72) - 4)
            if clear:
                log.load_messages(msgs, width=width)
                self._rendered_ids = {m["id"] for m in msgs if m.get("id")}
                if msgs:
                    self._last_sender = msgs[-1].get("sender", "?")
                    self._last_ts = msgs[-1].get("created_at")
                else:
                    self._last_sender = None
                    self._last_ts = None
            else:
                for m in msgs:
                    mid = m.get("id")
                    if mid is not None and mid in self._rendered_ids:
                        continue
                    log.append_message(
                        m,
                        width=width,
                        prev_sender=self._last_sender,
                        prev_ts=self._last_ts,
                    )
                    if mid is not None:
                        self._rendered_ids.add(mid)
                    self._last_sender = m.get("sender", "?")
                    self._last_ts = m.get("created_at")
            if msgs:
                self._cursors[channel] = msgs[-1]["id"]
                self.post_message(CursorAdvanced(channel, msgs[-1]["id"]))
                with suppress(Exception):
                    soil.put("willow-dashboard/cursors", channel, {"last_id": msgs[-1]["id"]})
                with suppress(Exception):
                    from panes.home import DeskPane

                    self.app.query_one(DeskPane)._fetch()
        except Exception:
            pass

    def on_channel_opened(self, event: ChannelOpened) -> None:
        event.stop()
        self._open_channel(event.name)

    def on_dm_opened(self, event: DmOpened) -> None:
        event.stop()
        self.open_dm(event.peer)

    @on(Input.Submitted, "#cmd-input")
    def _submit_command(self, event: Input.Submitted) -> None:
        line = event.value.strip()
        event.input.value = ""
        if not line:
            self._exit_command_mode()
            return
        self._run_command(line)

    def on_key(self, event) -> None:
        if self._command_mode and event.key == "escape":
            self._exit_command_mode()
            event.prevent_default()
            event.stop()

    @on(Input.Submitted, "#msg-input")
    def _send_message(self, event: Input.Submitted) -> None:
        body = event.value.strip()
        event.input.value = ""
        if not body or not self._active_channel:
            return
        if body == ":":
            self._enter_command_mode()
            return
        if body.startswith(":"):
            self._run_command(body)
            return
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
        self._load_messages(self._active_channel)
        if self._active_agent:
            self._set_waiting(self._active_agent)
            self._dispatch_to_agent(self._active_agent, body, self._active_channel)

    def on_unmount(self) -> None:
        self._listening = False
