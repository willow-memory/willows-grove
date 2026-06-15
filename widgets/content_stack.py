"""widgets/content_stack.py — center pane swapper for nav targets.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from contextlib import suppress

from textual.app import ComposeResult
from textual.containers import Container
from textual.css.query import NoMatches
from textual.widget import Widget

from panes.agents import AgentsPane
from panes.chat import ChatPane
from panes.git import GitStatusPane
from panes.help import HelpPane
from panes.home import HomeGrid
from panes.human import HumanPane
from panes.knowledge import KnowledgePane
from panes.mcp import MCPPane
from panes.prs import OpenPRsPane
from panes.projects import ProjectsPane
from panes.providers import ProvidersPane
from panes.routing import RoutingPane
from panes.settings import SettingsPane
from panes.tasks import TasksPane
from panes.think_map import ThinkMapPane
from panes.upstream import UpstreamPane
from panes.user_todos import UserTodosPane
from widgets.nav_bar import NAV_TARGETS

_REFRESH_TARGETS: dict[str, type[Widget]] = {
    "projects": ProjectsPane,
    "knowledge": KnowledgePane,
    "providers": ProvidersPane,
    "settings": SettingsPane,
}

_INTERNAL_PANES: dict[str, type[Widget]] = {
    "#pane-user-todos": UserTodosPane,
    "#pane-tasks": TasksPane,
    "#pane-agents": AgentsPane,
    "#pane-routing": RoutingPane,
    "#pane-mcp": MCPPane,
    "#pane-human": HumanPane,
    "#pane-git": GitStatusPane,
    "#pane-prs": OpenPRsPane,
    "#pane-upstream": UpstreamPane,
    "#pane-think-map": ThinkMapPane,
}


class ContentArea(Container):
    """Swaps Home grid, Chat pane, nav panes, and internal card panes."""

    DEFAULT_CSS = """
    ContentArea {
        width: 1fr;
        height: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        yield HomeGrid(id="pane-home")
        yield ChatPane(id="pane-chat")
        yield ProjectsPane(id="pane-projects")
        yield KnowledgePane(id="pane-knowledge")
        yield ProvidersPane(id="pane-providers")
        yield SettingsPane(id="pane-settings")
        yield HelpPane(id="pane-help")
        yield TasksPane(id="pane-tasks")
        yield AgentsPane(id="pane-agents")
        yield RoutingPane(id="pane-routing")
        yield MCPPane(id="pane-mcp")
        yield HumanPane(id="pane-human")
        yield GitStatusPane(id="pane-git")
        yield OpenPRsPane(id="pane-prs")
        yield UpstreamPane(id="pane-upstream")
        yield ThinkMapPane(id="pane-think-map")
        yield UserTodosPane(id="pane-user-todos")

    def _hide_internal_panes(self) -> None:
        for pane_id in _INTERNAL_PANES:
            with suppress(NoMatches):
                self.query_one(pane_id).display = False

    def _refresh_pane(self, pane: Widget) -> None:
        refresh = getattr(pane, "refresh_data", None)
        if callable(refresh):
            refresh()

    def show_target(self, target: str) -> None:
        for name in NAV_TARGETS:
            pane_id = f"pane-{name}"
            try:
                pane = self.query_one(f"#{pane_id}")
                pane.display = name == target
            except NoMatches:
                pass
        self._hide_internal_panes()
        try:
            self.query_one("#pane-chat", ChatPane).set_live(target == "chat")
        except NoMatches:
            pass
        cls = _REFRESH_TARGETS.get(target)
        if cls is not None:
            with suppress(NoMatches):
                self._refresh_pane(self.query_one(f"#pane-{target}", cls))

    def show_internal(self, pane_id: str) -> None:
        """Show an internal pane from a Home card — hides top-level nav panes."""
        for name in NAV_TARGETS:
            try:
                self.query_one(f"#pane-{name}").display = False
            except NoMatches:
                pass
        for pid, cls in _INTERNAL_PANES.items():
            try:
                pane = self.query_one(pid, cls)
                show = pane_id == pid
                pane.display = show
                if show:
                    self._refresh_pane(pane)
                    pane.focus()
            except NoMatches:
                pass
        try:
            self.query_one("#pane-chat", ChatPane).set_live(False)
        except NoMatches:
            pass
