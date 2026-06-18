"""panes/stubs.py — placeholder panes until wave 3+.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from textual.widgets import Static

from grove.theme_textual import ACCENT, PRIMARY, SECONDARY

_STUB_COPY: dict[str, str] = {
    "projects": "Projects grid + internal pane launchers — wave 4.",
    "knowledge": "Knowledge nav + atom detail — wave 4.",
    "providers": "Provider health rows — wave 4.",
    "settings": "Consent toggles + health — wave 4.",
    "help": "Keyboard reference — wave 4.",
}


class StubPane(Static):
    """Minimal placeholder for non-Home nav targets."""

    def __init__(self, target: str, **kwargs) -> None:
        title = target.replace("_", " ").title()
        body = _STUB_COPY.get(target, "Coming soon.")
        super().__init__(
            f"[bold {ACCENT}]{title}[/]\n\n[{PRIMARY}]{body}[/]\n\n"
            f"[dim {SECONDARY}]Hero collapsed · {title} pane — wave 4.[/]",
            markup=True,
            **kwargs,
        )
