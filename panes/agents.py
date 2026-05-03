"""panes/agents.py — Active agent monitor pane.
b17: WGRV1  ΔΣ=42
"""
from textual import work
from textual.containers import Container
from textual.message import Message
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


class _AgentsFetched(Message):
    def __init__(self, agents: list[dict]) -> None:
        super().__init__()
        self.agents = agents


class AgentsPane(Container):
    def compose(self):
        yield Label("  Agents", id="agents-title")
        table = DataTable(id="agents-table", cursor_type="row")
        table.add_columns("Agent", "State", "Last seen")
        yield table

    def on_mount(self) -> None:
        self.set_interval(15, self._fetch)
        self._fetch()

    @work(thread=True)
    def _fetch(self) -> None:
        agents = grove_reader.grove_agents()
        self.post_message(_AgentsFetched(agents))

    def on__agents_fetched(self, event: _AgentsFetched) -> None:
        from textual.css.query import NoMatches
        try:
            table = self.query_one("#agents-table", DataTable)
        except NoMatches:
            return
        table.clear()
        for a in event.agents:
            sender   = a["sender"]
            age_secs = a.get("age_secs", 9999)
            state, state_color = agent_state(age_secs)
            color = sender_color(sender)
            table.add_row(
                f"[{color} bold]{sender}[/]",
                f"[{state_color}]{state}[/]",
                age_str(age_secs),
            )
