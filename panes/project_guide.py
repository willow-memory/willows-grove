"""panes/project_guide.py — Project Guide pane.
Reads SAFE app catalog, lets user select a project, chats with ganas2.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from rich.markup import escape as _e
from textual import work
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.message import Message
from textual.widgets import DataTable, Input, Label, Rule, Static

_STORE_ROOT   = Path(os.environ.get("SAFE_APP_STORE_ROOT", Path.home() / "github" / "safe-app-store"))
_CATALOG_PATH = _STORE_ROOT / "catalog.json"

_SYSTEM_PROMPT = (
    "You are ganas2, a fast cloud agent in the Willow fleet. "
    "You help USER think through his SAFE app projects: status, next steps, "
    "blockers, design decisions. Be direct, brief, and specific. "
    "One paragraph max unless more is explicitly requested."
)


def _load_catalog() -> list[dict]:
    try:
        return json.loads(_CATALOG_PATH.read_text()).get("apps", [])
    except Exception:
        return []


class _CatalogLoaded(Message):
    def __init__(self, apps: list[dict]) -> None:
        super().__init__()
        self.apps = apps


class _ResponseReady(Message):
    def __init__(self, text: str) -> None:
        super().__init__()
        self.text = text


class ProjectGuidePane(Container):
    """Left: SAFE app catalog list. Right: ganas2 chat about the selected project."""

    DEFAULT_CSS = """
    ProjectGuidePane {
        width: 1fr;
        height: 1fr;
        layout: horizontal;
    }
    ProjectGuidePane #pg-left {
        width: 28;
        height: 1fr;
        border-right: solid #30363d;
    }
    ProjectGuidePane #pg-left-title {
        color: #58a6ff;
        text-style: bold;
        padding: 0 1;
    }
    ProjectGuidePane #pg-app-list {
        width: 1fr;
        height: 1fr;
    }
    ProjectGuidePane #pg-right {
        width: 1fr;
        height: 1fr;
        padding: 1 2;
    }
    ProjectGuidePane #pg-agent-tag {
        color: #3fb950;
        text-style: bold;
        text-align: right;
        width: 1fr;
    }
    ProjectGuidePane #pg-project-name {
        color: #58a6ff;
        text-style: bold;
    }
    ProjectGuidePane #pg-project-desc {
        color: #8b949e;
        margin-bottom: 1;
    }
    ProjectGuidePane #pg-chat-log {
        width: 1fr;
        height: 1fr;
        color: #c9d1d9;
        margin-bottom: 1;
    }
    ProjectGuidePane #pg-input {
        width: 1fr;
        border: solid #30363d;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._apps: list[dict] = []
        self._selected: dict | None = None
        self._history: list[str] = []

    def compose(self) -> ComposeResult:
        with Vertical(id="pg-left"):
            yield Label("SAFE APPS", id="pg-left-title")
            yield Rule()
            yield DataTable(id="pg-app-list", cursor_type="row", show_header=False)
        with Vertical(id="pg-right"):
            yield Label("● ganas2", id="pg-agent-tag", markup=False)
            yield Label("← select a project", id="pg-project-name", markup=False)
            yield Label("", id="pg-project-desc", markup=False)
            yield Rule()
            yield Static("[dim]Ask anything about this project.[/]", id="pg-chat-log", markup=True)
            yield Input(placeholder="Ask ganas2 about this project…", id="pg-input")

    def on_mount(self) -> None:
        self._load_catalog()

    @work(thread=True, exit_on_error=False)
    def _load_catalog(self) -> None:
        self.post_message(_CatalogLoaded(_load_catalog()))

    def on__catalog_loaded(self, event: _CatalogLoaded) -> None:
        from textual.css.query import NoMatches
        self._apps = event.apps
        try:
            table = self.query_one("#pg-app-list", DataTable)
            table.add_column("App", width=24)
            for app in self._apps:
                table.add_row(_e(app.get("name", app.get("id", "?"))[:24]))
        except NoMatches:
            pass

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        idx = event.cursor_row
        if 0 <= idx < len(self._apps):
            self._selected = self._apps[idx]
            self._history = []
            self._render_project()

    def _render_project(self) -> None:
        from textual.css.query import NoMatches
        if not self._selected:
            return
        name = self._selected.get("name", self._selected.get("id", "?"))
        desc = self._selected.get("description", "")
        try:
            self.query_one("#pg-project-name", Label).update(name)
            self.query_one("#pg-project-desc", Label).update(desc)
            self.query_one("#pg-chat-log", Static).update(
                "[dim]Ask anything about this project.[/]"
            )
        except NoMatches:
            pass

    def on_input_submitted(self, event: Input.Submitted) -> None:
        prompt = event.value.strip()
        if not prompt or not self._selected:
            return
        event.input.clear()
        self._history.append(f"[bold #c9d1d9]you:[/] {_e(prompt)}")
        self._update_log("[dim]ganas2 thinking…[/]")
        self._ask(prompt)

    @work(thread=True, exit_on_error=False)
    def _ask(self, prompt: str) -> None:
        import sys
        import os
        willow_root = os.environ.get("WILLOW_ROOT", str(Path.home() / "willow-2.0"))
        if willow_root not in sys.path:
            sys.path.insert(0, willow_root)
        # ganas_client lives alongside app.py in the Grove root
        grove_root = Path(__file__).parent.parent
        if str(grove_root) not in sys.path:
            sys.path.insert(0, str(grove_root))
        import ganas_client
        app   = self._selected or {}
        ctx   = (
            f"Project: {app.get('name', '?')}\n"
            f"Description: {app.get('description', '')}\n"
            f"Repo: {_STORE_ROOT / 'apps' / app.get('id', '')}"
        )
        reply = ganas_client.chat(_SYSTEM_PROMPT, f"{ctx}\n\nQuestion: {prompt}")
        self.post_message(_ResponseReady(reply))

    def on__response_ready(self, event: _ResponseReady) -> None:
        self._history.append(f"[bold #3fb950]ganas2:[/] {_e(event.text)}")
        self._update_log("\n".join(self._history))

    def _update_log(self, content: str) -> None:
        from textual.css.query import NoMatches
        try:
            self.query_one("#pg-chat-log", Static).update(content)
        except NoMatches:
            pass
