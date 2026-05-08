"""widgets/secrets_add_modal.py — Interview modal for adding secrets to vault.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, Horizontal
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Input, Label, Static, Button


_ENV_VAR_RE = re.compile(r"^[A-Z_][A-Z0-9_]*$")


def _load_secret_detection():
    """Load the secret detection function from willow-1.9."""
    try:
        willow_root = os.environ.get("WILLOW_ROOT", str(Path.home() / "github" / "willow-1.9"))
        if willow_root not in sys.path:
            sys.path.insert(0, willow_root)
        from core.secret_prefixes import detect_secret
        return detect_secret
    except Exception:
        return None


class SecretAdded(Message):
    """Posted when a secret is successfully added to the vault."""
    def __init__(self, key: str) -> None:
        super().__init__()
        self.key = key


class SecretsAddModal(ModalScreen):
    """Interview modal for adding a new secret to the vault."""

    DEFAULT_CSS = """
    SecretsAddModal {
        align: center middle;
    }
    SecretsAddModal #sam-dialog {
        width: 60;
        height: 20;
        background: #0d1117;
        border: solid #30363d;
    }
    SecretsAddModal #sam-message {
        height: auto;
        padding: 1 2;
        text-align: center;
    }
    SecretsAddModal #sam-input {
        height: 3;
        margin: 1 2;
        border: tall #30363d;
    }
    SecretsAddModal #sam-input:focus {
        border: tall #58a6ff;
    }
    SecretsAddModal #sam-buttons {
        height: auto;
        display: none;
        margin: 1 2;
    }
    SecretsAddModal #sam-buttons.show {
        display: block;
    }
    SecretsAddModal #sam-status {
        height: auto;
        padding: 0 2 1 2;
        color: #8b949e;
        text-align: center;
    }
    """

    BINDINGS = [Binding("escape", "dismiss", "Cancel")]

    def __init__(self) -> None:
        super().__init__()
        self._stage: int = 0  # 0=key_name, 1=value, 2=confirm
        self._key_name: str = ""
        self._value: str = ""
        self._vault = None
        self._detect_secret = _load_secret_detection()

    def compose(self) -> ComposeResult:
        with Vertical(id="sam-dialog"):
            yield Static("Add a secret to the vault", id="sam-message", markup=False)
            yield Input(
                placeholder="Key name (e.g., API_KEY, DB_PASSWORD)",
                id="sam-input"
            )
            with Horizontal(id="sam-buttons"):
                yield Button("Cancel", id="sam-cancel", variant="error")
                yield Button("Confirm", id="sam-confirm", variant="success")
            yield Static("Must be uppercase alphanumeric + underscore", id="sam-status", markup=False)

    def on_mount(self) -> None:
        self._load_vault()
        self.query_one("#sam-input", Input).focus()

    def _load_vault(self) -> None:
        """Load the Vault instance — never raises."""
        try:
            willow_root = os.environ.get("WILLOW_ROOT", str(Path.home() / "github" / "willow-1.9"))
            import sys
            if willow_root not in sys.path:
                sys.path.insert(0, willow_root)
            from core.vault import Vault
            self._vault = Vault()
        except Exception:
            self._set_message("[red](vault unavailable)[/]")

    def _set_message(self, text: str) -> None:
        self.query_one("#sam-message", Static).update(text)

    def _set_status(self, text: str) -> None:
        self.query_one("#sam-status", Static).update(text)

    def _set_input(self, placeholder: str, value: str = "", password: bool = False) -> None:
        inp = self.query_one("#sam-input", Input)
        inp.value = value
        inp.placeholder = placeholder
        inp.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if self._stage == 0:
            self._handle_key_input(event.value.strip())
        elif self._stage == 1:
            self._handle_value_input(event.value.strip())
        elif self._stage == 2:
            self._handle_confirm(event.value.strip().lower())

    def _handle_key_input(self, key: str) -> None:
        """Validate and store key name."""
        if not key:
            self._set_status("[red]Key name cannot be empty[/]")
            return

        # Check if it looks like a secret key
        if self._detect_secret:
            detected = self._detect_secret(key)
            if detected:
                canonical_name, label = detected
                self._set_status(f"[red]That's a {label}, not a key name. Use a name like API_KEY[/]")
                return

        if not _ENV_VAR_RE.match(key):
            normalized = key.upper().replace(' ', '_').replace('-', '_')
            normalized = ''.join(c for c in normalized if c.isalnum() or c == '_')
            if normalized and _ENV_VAR_RE.match(normalized):
                self._set_status(f"[dim]i'll file this as: [bold]{normalized}[/bold][/]")
            else:
                self._set_status("[red]Must start with letter/underscore, use only A-Z, 0-9, _[/]")
            return

        # Check if key already exists
        if self._vault:
            try:
                existing = self._vault.list_keys()
                if key in existing:
                    self._set_status(f"[red]Key '{key}' already exists[/]")
                    return
            except Exception:
                pass

        self._key_name = key
        self._stage = 1
        self._set_message(f"Paste the value for `{key}`")
        self._set_status("[dim]Press Enter to confirm[/]")
        inp = self.query_one("#sam-input", Input)
        inp.value = ""
        inp.placeholder = "Paste secret value here"
        inp.focus()

    def _handle_value_input(self, value: str) -> None:
        """Store value and move to confirmation."""
        if not value:
            self._set_status("[red]Value cannot be empty[/]")
            return

        self._value = value
        self._stage = 2
        self._set_message(f"Store `{self._key_name}`?")
        self._set_status("[dim]Click to confirm or cancel[/]")
        self._show_buttons()

    def _handle_confirm(self, response: str = None) -> None:
        """Write secret to vault on confirmation."""
        if response is not None and response != "yes":
            self._set_status("[dim]Cancelled[/]")
            return

        if not self._vault:
            self._set_message("[red]Vault unavailable[/]")
            return

        try:
            self._vault.write(self._key_name, self._value)
            self._set_message(f"[green]✓ Stored `{self._key_name}`[/]")
            self._set_status("[dim]Closing... press Escape[/]")
            self.post_message(SecretAdded(self._key_name))
            # Auto-dismiss after a brief moment
            import asyncio
            async def _close():
                await asyncio.sleep(1.0)
                self.app.pop_screen()
            asyncio.create_task(_close())
        except Exception as e:
            self._set_message(f"[red]Error storing secret: {e}[/]")
            self._set_status("[dim]Press Escape to close[/]")

    def action_confirm(self) -> None:
        """Action for confirm button."""
        self._handle_confirm()

    def action_cancel_stage2(self) -> None:
        """Action for cancel button at stage 2."""
        self._stage = 1
        self._set_message(f"Paste the value for `{self._key_name}`")
        self._set_status("[dim]Press Enter to confirm[/]")
        self.query_one("#sam-input", Input).focus()
        self._hide_buttons()

    def _show_buttons(self) -> None:
        """Show confirmation buttons and hide input."""
        from textual.css.query import NoMatches
        try:
            inp = self.query_one("#sam-input", Input)
            inp.styles.display = "none"
        except NoMatches:
            pass
        try:
            buttons = self.query_one("#sam-buttons", Horizontal)
            buttons.add_class("show")
        except NoMatches:
            pass

    def _hide_buttons(self) -> None:
        """Hide confirmation buttons and show input."""
        from textual.css.query import NoMatches
        try:
            inp = self.query_one("#sam-input", Input)
            inp.styles.display = "block"
        except NoMatches:
            pass
        try:
            buttons = self.query_one("#sam-buttons", Horizontal)
            buttons.remove_class("show")
        except NoMatches:
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "sam-confirm":
            self.action_confirm()
        elif event.button.id == "sam-cancel":
            self.action_cancel_stage2()
