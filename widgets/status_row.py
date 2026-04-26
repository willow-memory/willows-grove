"""widgets/status_row.py — StatusRow widget + helpers.
b17: WGRV1  ΔΣ=42
"""
from textual.widgets import Static


def dot(ok: bool | None) -> str:
    if ok is True:  return "●"
    if ok is False: return "○"
    return "◌"


def color_for_ok(ok: bool | None) -> str:
    if ok is True:  return "green"
    if ok is False: return "red"
    return "yellow"


class StatusRow(Static):
    """One-line status indicator: [●] label  value"""

    def __init__(self, label: str, **kwargs):
        super().__init__(**kwargs)
        self._label = label

    def set_status(self, ok: bool | None, value: str) -> None:
        color = color_for_ok(ok)
        d     = dot(ok)
        self.update(f"[{color}]{d}[/] [bold]{self._label}[/]  {value}")
