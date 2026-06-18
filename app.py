#!/usr/bin/env python3
"""
app.py — Willow Grove dashboard (fresh start).
b17: WGRV1  ΔΣ=42

Wave 3: Discord ChatPane · MCP registry pane + grove.mcp_local restored.

Run: ./dev.sh  or  python3 app.py
MCP:  ./run_mcp.sh  or  ./run_mcp.sh --serve
"""
from __future__ import annotations

import logging
from contextlib import suppress
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.css.query import NoMatches
from textual.message import Message
from textual.widgets import Footer, Static
from textual import work

from grove.apps.vitals import fetch_vitals, format_vitals_markup
from grove.theme_textual import FRESH_SHELL_CSS, SECONDARY
from panes.chat import ChatPane
from panes.home import CardActivated, HomeGrid
from panes.think_map import ThinkMapNavigate, ThinkMapOpen, ThinkMapPane
from widgets.card_builder_modal import CardBuilderModal
from widgets.content_stack import ContentArea
from widgets.card_store import PLUS_CARD_ID
from widgets.context_panel import ContextPanel
from widgets.hero_scene import HeroScene
from widgets.nav_bar import NAV_TARGETS, NavBar, NavChanged

logging.basicConfig(
    filename=Path.home() / ".willow" / "grove_error.log",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
_log = logging.getLogger("grove.app")


class _VitalsData(Message):
    def __init__(self, text: str) -> None:
        super().__init__()
        self.text = text


class VitalsBar(Static):
    """Hidden ticker — pushes markup to NavBar #nav-vitals."""

    def on_mount(self) -> None:
        self.set_interval(15, self._fetch)
        self._fetch()

    @work(thread=True, exit_on_error=False)
    def _fetch(self) -> None:
        try:
            line = format_vitals_markup(fetch_vitals())
        except Exception:
            line = f"[dim {SECONDARY}]vitals unavailable[/]"
        self.post_message(_VitalsData(line))

    def on__vitals_data(self, event: _VitalsData) -> None:
        with suppress(NoMatches):
            self.app.query_one(NavBar).set_vitals(event.text)


class WillowGrove(App):
    CSS = FRESH_SHELL_CSS

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("1", "nav('home')", "Home"),
        Binding("2", "nav('chat')", "Chat"),
        Binding("3", "nav('projects')", "Projects"),
        Binding("4", "nav('knowledge')", "Knowledge"),
        Binding("5", "nav('providers')", "Providers"),
        Binding("6", "nav('settings')", "Settings"),
        Binding("7", "nav('help')", "Help"),
        Binding("colon", "chat_command", "Mod command", show=False, priority=True),
    ]

    TITLE = "Willow Grove"
    SUB_TITLE = "fresh start"

    def compose(self) -> ComposeResult:
        yield NavBar(id="nav-bar")
        yield HeroScene(id="hero-scene")
        with Horizontal(id="main-body"):
            yield ContextPanel(id="context-panel")
            yield ContentArea(id="content-area")
        yield VitalsBar(id="vitals-source")
        yield Footer()

    def on_mount(self) -> None:
        import grove_db
        grove_db.ensure_upstream_channel()
        self.action_nav("home")

    def _handle_exception(self, error: Exception) -> None:
        """Log to grove_error.log — skip Rich traceback overlay on exit."""
        _log.exception("unhandled exception: %s", error)
        self._return_code = 1
        if self._exception is None:
            self._exception = error
            self._exception_event.set()
        self._close_messages_no_wait()

    def _set_hero_expanded(self, expanded: bool) -> None:
        with suppress(NoMatches):
            self.query_one(HeroScene).set_expanded(expanded)

    def on_nav_changed(self, event: NavChanged) -> None:
        target = event.target
        if target not in NAV_TARGETS:
            return
        self._set_hero_expanded(target == "home")
        with suppress(NoMatches):
            self.query_one(NavBar).highlight(target)
        with suppress(NoMatches):
            self.query_one(ContextPanel).show_target(target)
        with suppress(NoMatches):
            self.query_one(ContentArea).show_target(target)

    def on_card_activated(self, event: CardActivated) -> None:
        target = event.nav_target
        if not target:
            return
        if target == PLUS_CARD_ID:
            self.push_screen(CardBuilderModal(), self._on_card_builder_dismiss)
            return
        if target.startswith("#pane-"):
            self._set_hero_expanded(False)
            with suppress(NoMatches):
                self.query_one(NavBar).highlight("home")
            with suppress(NoMatches):
                self.query_one(ContextPanel).show_target("home")
            with suppress(NoMatches):
                self.query_one(ContentArea).show_internal(target)
            return
        if target in NAV_TARGETS:
            self.action_nav(target)

    def action_nav(self, target: str) -> None:
        self.post_message(NavChanged(target))

    def _on_card_builder_dismiss(self, saved: bool) -> None:
        if saved:
            with suppress(NoMatches):
                self.query_one(HomeGrid).refresh_cards()

    def on_think_map_navigate(self, event: ThinkMapNavigate) -> None:
        self._set_hero_expanded(False)
        with suppress(NoMatches):
            self.query_one(NavBar).highlight("home")
        with suppress(NoMatches):
            self.query_one(ContextPanel).show_target("home")
        with suppress(NoMatches):
            self.query_one(ContentArea).show_internal("#pane-think-map")
        with suppress(NoMatches):
            self.query_one(ThinkMapPane).post_message(ThinkMapOpen(event.map_id))

    def action_chat_command(self) -> None:
        """`:` mod palette — priority so composer Input does not swallow colon."""
        with suppress(NoMatches):
            chat = self.query_one("#pane-chat", ChatPane)
            if chat.is_live():
                chat.action_command_line()


if __name__ == "__main__":
    from widgets.hero_db import init_db

    init_db()
    WillowGrove().run()
