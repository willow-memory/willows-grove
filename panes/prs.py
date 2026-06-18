"""panes/prs.py — Open pull requests via gh CLI.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import json
import subprocess
from contextlib import suppress

from textual import work
from textual.binding import Binding
from textual.containers import Container
from textual.message import Message
from textual.widgets import DataTable, Label

from grove.paths import resolve_git_repo
from grove.theme_textual import ACCENT


def fetch_open_prs(repo_path: str | None = None) -> list[dict]:
    cwd = repo_path or str(resolve_git_repo())
    try:
        r = subprocess.run(
            [
                "gh", "pr", "list", "--state", "open",
                "--json", "number,title,author,updatedAt,headRefName",
            ],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=cwd,
        )
        if r.returncode != 0:
            return []
        data = json.loads(r.stdout or "[]")
        return [
            {
                "number": str(pr.get("number", "")),
                "title": (pr.get("title") or "")[:60],
                "author": (pr.get("author") or {}).get("login", "?"),
                "branch": (pr.get("headRefName") or "")[:30],
                "updated": (pr.get("updatedAt") or "")[:10],
            }
            for pr in data
        ]
    except Exception:
        return []


class _PRsFetched(Message):
    def __init__(self, prs: list[dict]) -> None:
        super().__init__()
        self.prs = prs


class OpenPRsPane(Container):
    BINDINGS = [Binding("r", "refresh_data", "Refresh")]

    DEFAULT_CSS = f"""
    OpenPRsPane {{
        height: 1fr;
        padding: 0 1;
    }}
    OpenPRsPane #prs-title {{
        color: {ACCENT};
        text-style: bold;
        margin-bottom: 1;
    }}
    OpenPRsPane #prs-table {{
        height: 1fr;
    }}
    """

    def compose(self):
        yield Label("  Open Pull Requests", id="prs-title")
        table = DataTable(id="prs-table", cursor_type="row")
        table.add_columns(
            ("#", "num"),
            ("Title", "title"),
            ("Author", "author"),
            ("Branch", "branch"),
            ("Updated", "updated"),
        )
        yield table

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        self._fetch()

    @work(thread=True, exit_on_error=False)
    def _fetch(self) -> None:
        self.post_message(_PRsFetched(fetch_open_prs()))

    def on__prs_fetched(self, event: _PRsFetched) -> None:
        try:
            self._apply(event.prs)
        except Exception as exc:
            with suppress(Exception):
                self.query_one("#prs-title", Label).update(f"  PRs — error: {exc}")

    def _apply(self, prs: list[dict]) -> None:
        table = self.query_one("#prs-table", DataTable)
        table.clear()
        if not prs:
            table.add_row("—", "No open PRs (or gh unavailable)", "", "", "")
            return
        for pr in prs:
            table.add_row(
                pr["number"],
                pr["title"],
                pr["author"],
                pr["branch"],
                pr["updated"],
            )
