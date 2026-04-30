"""panes/help.py — Help reference pane.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static

_OVERVIEW = """\
[bold #58a6ff]Willow Grove[/]

Local-first AI workspace. One surface for messaging, task coordination,
knowledge, and agent management. Everything runs on your machine.
Postgres holds the memory. Ollama runs the models. You hold the keys.\
"""

_NAVIGATION = """\
[bold #58a6ff]Navigation[/]

[bold]Home[/]       Dashboard — tasks, agents, active thoughts
[bold]Chat[/]       Grove channels — agent and human messaging
[bold]Projects[/]   Active projects and task queues
[bold]Knowledge[/]  Search and browse the knowledge base
[bold]Providers[/]  AI model providers — enable/disable
[bold]Health[/]     Subsystem status — pg, ollama, kart, SOIL
[bold]Settings[/]   Consent and security controls
[bold]Help[/]       This panel\
"""

_SHORTCUTS = """\
[bold #58a6ff]Keyboard Shortcuts[/]

[bold]q[/]       Quit
[bold]r[/]       Refresh
[bold]1–8[/]     Navigate to Home / Chat / Projects / Knowledge /
            Providers / Health / Settings / Help
[bold]e[/]       Enable selected provider (Providers pane)
[bold]d[/]       Disable selected provider (Providers pane)
[bold]Enter[/]   Confirm selection / toggle (nav rows, settings)
[bold]↑ ↓[/]     Move cursor (Knowledge search results)\
"""

_PRIVACY = """\
[bold #58a6ff]Privacy & Consent[/]

Willow runs locally. No data leaves your machine unless you explicitly
enable cloud features.

[bold]Internet[/]    Outbound internet connections. Off = fully air-gapped.
[bold]Cloud LLM[/]   Prompts sent to cloud AI providers (e.g. Anthropic).
                Off = local models only.
[bold]LAN[/]         Local network communication between your devices.
                Off = no outbound LAN traffic.

Consent state is stored at [dim]~/.willow/consent.json[/] and applies
system-wide to all apps installed through Willow Grove.

Authorization is enforced by the SAP gate — apps must present a
PGP-signed manifest to access any Willow tool.\
"""


class HelpPane(VerticalScroll):
    DEFAULT_CSS = """
    HelpPane {
        height: 1fr;
        padding: 1 2;
    }
    HelpPane Static {
        padding: 0 0 2 0;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static(_OVERVIEW,   id="help-overview",   markup=True)
        yield Static(_NAVIGATION, id="help-navigation", markup=True)
        yield Static(_SHORTCUTS,  id="help-shortcuts",  markup=True)
        yield Static(_PRIVACY,    id="help-privacy",    markup=True)

    def jump_to_section(self, section: str) -> None:
        from textual.css.query import NoMatches
        try:
            self.query_one(f"#help-{section}", Static).scroll_visible()
        except NoMatches:
            pass
