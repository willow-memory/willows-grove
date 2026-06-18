"""panes/help.py — Keyboard reference for fresh-start shell.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static

from grove.theme_textual import PRIMARY, markup_bold_accent, markup_dim


def _section(title: str, body: str) -> str:
    return f"{markup_bold_accent()}{title}[/]\n\n{body}"


_OVERVIEW = _section(
    "Willow Grove",
    """Local-first AI workspace. One surface for messaging, task coordination,
knowledge, and agent management. Postgres holds the memory. Ollama runs the models.""",
)

_NAVIGATION = _section(
    "Navigation",
    """[bold]Home[/]       Desk + card launchers
[bold]Chat[/]       Grove channels — Discord-style sidebar
[bold]Projects[/]   Personal project list (SOIL)
[bold]Knowledge[/] Search Postgres KB atoms
[bold]Providers[/]  Ollama + cloud provider status
[bold]Settings[/]   Consent toggles + subsystem vitals
[bold]Help[/]       This panel""",
)

_SHORTCUTS = _section(
    "Keyboard Shortcuts",
    """[bold]q[/]       Quit
[bold]1–7[/]     Navigate Home / Chat / Projects / Knowledge /
            Providers / Settings / Help
[bold]: [/]      Chat mod command (when Chat is active)
[bold]r[/]       Refresh (Settings, Providers, MCP)
[bold]t[/]       Load MCP tools (MCP pane)
[bold]s x R[/]   Start / stop / restart grove MCP serve
[bold]e d[/]     Enable / disable provider (Providers pane)
[bold]Enter[/]   Toggle consent row / call MCP tool / submit forms""",
)

_PRIVACY = _section(
    "Privacy & Consent",
    f"""Willow runs locally. No data leaves your machine unless you explicitly
enable cloud features.

[bold]Internet[/]    Outbound internet connections.
[bold]Cloud LLM[/]   Prompts sent to cloud AI providers.
[bold]LAN[/]         Local network communication between devices.

Consent state is stored at {markup_dim()}~/.willow/settings.global.json[/] (mirrored to consent.json).""",
)


class HelpPane(VerticalScroll):
    DEFAULT_CSS = f"""
    HelpPane {{
        height: 1fr;
        padding: 1 2;
        color: {PRIMARY};
    }}
    HelpPane Static {{
        padding: 0 0 2 0;
    }}
    """

    def compose(self) -> ComposeResult:
        yield Static(_OVERVIEW, id="help-overview", markup=True)
        yield Static(_NAVIGATION, id="help-navigation", markup=True)
        yield Static(_SHORTCUTS, id="help-shortcuts", markup=True)
        yield Static(_PRIVACY, id="help-privacy", markup=True)

    def jump_to_section(self, section: str) -> None:
        from textual.css.query import NoMatches
        try:
            self.query_one(f"#help-{section}", Static).scroll_visible()
        except NoMatches:
            pass
