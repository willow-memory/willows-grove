"""panes/prs.py — Open pull requests pane via gh CLI.
b17: WGRV1  ΔΣ=42
"""
import subprocess
from pathlib import Path

from textual import work
from textual.containers import Container
from textual.message import Message
from textual.widgets import DataTable, Label


def fetch_open_prs(repo_path: str | None = None) -> list[dict]:
    cwd = repo_path or str(Path.home() / "github" / "safe-app-willow-grove")
    try:
        r = subprocess.run(
            ["gh", "pr", "list", "--state", "open",
             "--json", "number,title,author,updatedAt,headRefName"],
            capture_output=True, text=True, timeout=15, cwd=cwd,
        )
        if r.returncode != 0:
            return []
        import json
        data = json.loads(r.stdout or "[]")
        return [
            {
                "number": str(pr.get("number", "")),
                "title":  (pr.get("title") or "")[:60],
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
    def compose(self):
        yield Label("  Open Pull Requests", id="prs-title")
        table = DataTable(id="prs-table", cursor_type="row")
        table.add_columns("#", "Title", "Author", "Branch", "Updated")
        yield table

    def on_mount(self) -> None:
        self.set_interval(60, self._fetch)
        self._fetch()

    def refresh_data(self) -> None:
        self._fetch()

    @work(thread=True, exit_on_error=False)
    def _fetch(self) -> None:
        self.post_message(_PRsFetched(fetch_open_prs()))

    def on__prs_fetched(self, event: _PRsFetched) -> None:
        from textual.css.query import NoMatches
        try:
            table = self.query_one("#prs-table", DataTable)
        except NoMatches:
            return
        table.clear()
        if not event.prs:
            table.add_row("—", "No open PRs", "", "", "")
            return
        for pr in event.prs:
            table.add_row(
                pr["number"], pr["title"], pr["author"],
                pr["branch"], pr["updated"],
            )
