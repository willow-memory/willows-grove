"""panes/agents.py — Active agent monitor pane.
b17: WGRV1  ΔΣ=42
"""
from textual.containers import Container
from textual.widgets import DataTable, Label

import grove_reader
from panes.chat import sender_color


def agent_state(age_secs: int) -> tuple[str, str]:
    if age_secs < 120:   return "running", "green"
    if age_secs < 900:   return "idle",    "yellow"
    if age_secs < 3600:  return "stale",   "dim"
    return "gone", "dim"


def age_str(secs: int) -> str:
    if secs < 60:    return f"{secs}s"
    if secs < 3600:  return f"{secs // 60}m"
    return f"{secs // 3600}h"


class AgentsPane(Container):
    def compose(self):
        yield Label("  Agents", id="agents-title")
        table = DataTable(id="agents-table", cursor_type="row")
        table.add_columns("Agent", "State", "Last seen")
        yield table

    def on_mount(self) -> None:
        self.set_interval(15, self.refresh_data)
        self.refresh_data()

    def refresh_data(self) -> None:
        table = self.query_one("#agents-table", DataTable)
        table.clear()
        for a in grove_reader.grove_agents():
            sender   = a["sender"]
            age_secs = a.get("age_secs", 9999)
            state, state_color = agent_state(age_secs)
            color = sender_color(sender)
            table.add_row(
                f"[{color} bold]{sender}[/]",
                f"[{state_color}]{state}[/]",
                age_str(age_secs),
            )
