"""widgets/card_builder_modal.py — Heimdallr card builder interview modal.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import json
import os
import re
import select

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Input, RichLog, Static

import grove_reader

_CARD_DEF_RE = re.compile(r"```card-def\s*\n(.*?)\n```", re.DOTALL)

_INTRO_PROMPT = (
    "The user wants to add a new card to their Willow Grove dashboard. "
    "Interview them: ask what they want to track, suggest from the available "
    "catalog (git-status, open-prs, build, todos) if relevant, then produce "
    "a ```card-def JSON block with at minimum 'id' and 'label' fields."
)


def _pg_conn():
    import psycopg2
    return psycopg2.connect(
        dbname=os.environ.get("WILLOW_PG_DB",   "willow_19"),
        user=os.environ.get("WILLOW_PG_USER", os.environ.get("USER", "")),
    )


class CardDefDetected(Message):
    """Posted when a valid card-def block is detected and saved to SOIL."""
    def __init__(self, card: dict) -> None:
        self.card = card
        super().__init__()


class CardBuilderModal(ModalScreen):
    """Heimdallr interview modal — chat log + input + card-def detection."""

    DEFAULT_CSS = """
    CardBuilderModal {
        align: center middle;
    }
    CardBuilderModal #cb-dialog {
        width: 80;
        height: 40;
        background: #0d1117;
        border: solid #30363d;
    }
    CardBuilderModal #cb-log {
        height: 1fr;
        padding: 1 2;
    }
    CardBuilderModal #cb-status {
        height: 1;
        padding: 0 2;
        color: #8b949e;
    }
    CardBuilderModal #cb-input {
        height: 3;
        margin: 0 2 1 2;
        border: tall #30363d;
    }
    CardBuilderModal #cb-input:focus {
        border: tall #58a6ff;
    }
    """

    BINDINGS = [Binding("escape", "dismiss", "Close")]

    def __init__(self) -> None:
        super().__init__()
        self._channel_id: int | None = None
        self._cursor:     int        = 0
        self._listening:  bool       = False
        self._card_saved: bool       = False

    def compose(self) -> ComposeResult:
        with Vertical(id="cb-dialog"):
            yield RichLog(id="cb-log", highlight=False, markup=True, wrap=True)
            yield Static("[dim]Connecting to Heimdallr…[/]", id="cb-status", markup=True)
            yield Input(placeholder="Message Heimdallr…", id="cb-input")

    def on_mount(self) -> None:
        self._setup()

    @work(thread=True)
    def _setup(self) -> None:
        channel_id = self._get_or_create_channel()

        if channel_id is None:
            self.app.call_from_thread(
                self._set_status, "[red]Could not connect to #card-builder — check grove_error.log[/]"
            )
            return

        self._channel_id = channel_id

        msgs = grove_reader.grove_messages("card-builder", limit=20)
        self.app.call_from_thread(self._load_history, msgs)

        if not msgs:
            self._dispatch_intro(channel_id)

        self._start_listener()

    def _get_or_create_channel(self) -> int | None:
        """Upsert #card-builder then return its id. Returns None on any DB error."""
        import logging
        try:
            conn = _pg_conn()
            cur  = conn.cursor()
            cur.execute("""
                INSERT INTO grove.channels (name, channel_type, description, agent_name)
                VALUES ('card-builder', 'group', 'Heimdallr card builder interview', 'heimdallr')
                ON CONFLICT (name) DO NOTHING
            """)
            conn.commit()
            cur.execute("SELECT id FROM grove.channels WHERE name = 'card-builder' LIMIT 1")
            row = cur.fetchone()
            conn.close()
            return row[0] if row else None
        except Exception as exc:
            logging.getLogger(__name__).error("card-builder channel error: %s", exc)
            return None

    def _dispatch_intro(self, channel_id: int) -> None:
        try:
            conn = _pg_conn()
            cur  = conn.cursor()
            cur.execute("SELECT id FROM grove.channels WHERE name = 'dispatch' LIMIT 1")
            row = cur.fetchone()
            if row:
                payload = json.dumps({
                    "to":            "heimdallr",
                    "prompt":        _INTRO_PROMPT,
                    "reply_channel": "card-builder",
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

    def _load_history(self, msgs: list[dict]) -> None:
        log = self.query_one("#cb-log", RichLog)
        log.clear()
        for m in msgs:
            self._append_message(m)
        if msgs:
            self._cursor = msgs[-1]["id"]
        self._set_status("[dim]Waiting for Heimdallr…[/]")

    def _append_message(self, m: dict) -> None:
        from panes.chat import format_ts, render_content, sender_color
        sender  = m.get("sender", "?")
        content = m.get("content", "")
        ts      = format_ts(m.get("created_at"))
        color   = sender_color(sender)
        log = self.query_one("#cb-log", RichLog)
        log.write(
            f"[dim]{ts}[/dim]  [{color} bold]{sender:<14}[/{color} bold]  {render_content(content)}"
        )

    def _set_status(self, text: str) -> None:
        from textual.css.query import NoMatches
        try:
            self.query_one("#cb-status", Static).update(text)
        except NoMatches:
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
                        n = conn.notifies.pop(0)
                        try:
                            if int(n.payload) == self._channel_id:
                                self.app.call_from_thread(self._on_notify)
                        except (ValueError, TypeError):
                            pass
        except Exception:
            pass

    def _on_notify(self) -> None:
        msgs = grove_reader.grove_messages("card-builder", limit=50)
        new_msgs = [m for m in msgs if m["id"] > self._cursor]
        for m in new_msgs:
            self._append_message(m)
            self._scan_for_card_def(m.get("content", ""))
        if new_msgs:
            self._cursor = new_msgs[-1]["id"]

    def _scan_for_card_def(self, body: str) -> None:
        match = _CARD_DEF_RE.search(body)
        if not match:
            return
        try:
            raw = json.loads(match.group(1))
        except json.JSONDecodeError:
            self._set_status("[red]card-def block contained invalid JSON — waiting for correction…[/]")
            return

        from widgets.card_store import validate_card_def, save_card
        card = validate_card_def(raw)
        if card is None:
            self._set_status("[red]card-def missing required fields (id, label) — waiting…[/]")
            return

        save_card(card)
        self._card_saved = True
        self._post_confirmation(card["label"])
        self._set_status(f"[green]Card '{card['label']}' saved.[/] Press Esc to close or continue.")
        self.post_message(CardDefDetected(card))

    def _post_confirmation(self, label: str) -> None:
        if self._channel_id is None:
            return
        try:
            conn = _pg_conn()
            cur  = conn.cursor()
            sender = os.environ.get("GROVE_SENDER") or os.environ.get("USER", "dashboard")
            cur.execute(
                "INSERT INTO grove.messages (channel_id, sender, content)"
                " VALUES (%s, %s, %s)",
                (self._channel_id, sender,
                 f"Card '{label}' saved. Press Esc to close or continue the conversation."),
            )
            conn.commit()
            conn.close()
        except Exception:
            pass

    def on_input_submitted(self, event: Input.Submitted) -> None:
        body = event.value.strip()
        if not body or self._channel_id is None:
            return
        event.input.value = ""
        sender = os.environ.get("GROVE_SENDER") or os.environ.get("USER", "sean")
        try:
            conn = _pg_conn()
            cur  = conn.cursor()
            cur.execute(
                "INSERT INTO grove.messages (channel_id, sender, content)"
                " VALUES (%s, %s, %s)",
                (self._channel_id, sender, body),
            )
            conn.commit()
            conn.close()
        except Exception:
            pass

    def on_unmount(self) -> None:
        self._listening = False
