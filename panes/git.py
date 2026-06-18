"""panes/git.py — Git status for the Grove repo.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import subprocess
from contextlib import suppress

from rich.markup import escape as _e
from textual import work
from textual.binding import Binding
from textual.containers import Container
from textual.message import Message
from textual.widgets import Label, RichLog

from grove.paths import resolve_git_repo
from grove.theme_textual import ACCENT, DEGRADED, DOWN


def _run(cmd: list[str], cwd: str) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10, cwd=cwd)
        return r.stdout.strip() or r.stderr.strip() or "(no output)"
    except Exception as e:
        return f"error: {e}"


def fetch_git_status(repo_path: str | None = None) -> dict:
    cwd = repo_path or str(resolve_git_repo())
    short = _run(["git", "status", "--short"], cwd)
    log = _run(["git", "log", "--oneline", "-8"], cwd)
    branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd)
    dirty = len([line for line in short.splitlines() if line.strip()]) if short != "(no output)" else 0
    return {"branch": branch, "short": short, "log": log, "dirty": dirty, "cwd": cwd}


class _GitFetched(Message):
    def __init__(self, data: dict) -> None:
        super().__init__()
        self.data = data


class GitStatusPane(Container):
    BINDINGS = [Binding("r", "refresh_data", "Refresh")]

    DEFAULT_CSS = """
    GitStatusPane {
        height: 1fr;
        padding: 0 1;
    }
    GitStatusPane #git-title {
        height: 1;
        margin-bottom: 1;
    }
    GitStatusPane #git-log {
        height: 1fr;
    }
    """

    def compose(self):
        yield Label("  Git Status", id="git-title")
        yield RichLog(id="git-log", highlight=True, markup=True, wrap=True)

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        self._fetch()

    @work(thread=True, exit_on_error=False)
    def _fetch(self) -> None:
        self.post_message(_GitFetched(fetch_git_status()))

    def on__git_fetched(self, event: _GitFetched) -> None:
        try:
            self._apply(event.data)
        except Exception as exc:
            with suppress(Exception):
                log = self.query_one("#git-log", RichLog)
                log.clear()
                log.write(f"[red]error: {_e(str(exc))}[/]")

    def _apply(self, data: dict) -> None:
        log = self.query_one("#git-log", RichLog)
        log.clear()
        log.write(f"[bold {ACCENT}]branch:[/] {_e(data['branch'])}")
        log.write(f"[dim]{_e(data.get('cwd', ''))}[/]")
        log.write("")
        if data["short"] and data["short"] != "(no output)":
            log.write("[bold]working tree:[/]")
            for line in data["short"].splitlines():
                color = DOWN if line[:2].strip() else DEGRADED
                log.write(f"  [{color}]{_e(line)}[/]")
        else:
            log.write("[dim]working tree clean[/]")
        log.write("")
        log.write("[bold]recent commits:[/]")
        for line in data["log"].splitlines():
            parts = line.split(" ", 1)
            if len(parts) == 2:
                log.write(f"  [dim]{_e(parts[0])}[/] {_e(parts[1])}")
            else:
                log.write(f"  {_e(line)}")
