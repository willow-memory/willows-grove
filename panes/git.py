"""panes/git.py — Git status pane for safe-app-willow-grove working directory.
b17: WGRV1  ΔΣ=42
"""
import subprocess
from pathlib import Path

from rich.markup import escape as _e
from textual import work
from textual.containers import Container
from textual.message import Message
from textual.widgets import Label, RichLog


def _run(cmd: list[str], cwd: str) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10, cwd=cwd)
        return r.stdout.strip() or r.stderr.strip() or "(no output)"
    except Exception as e:
        return f"error: {e}"


def fetch_git_status(repo_path: str | None = None) -> dict:
    cwd = repo_path or str(Path.home() / "github" / "safe-app-willow-grove")
    short  = _run(["git", "status", "--short"], cwd)
    log    = _run(["git", "log", "--oneline", "-8"], cwd)
    branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd)
    dirty  = len([l for l in short.splitlines() if l.strip()]) if short != "(no output)" else 0
    return {"branch": branch, "short": short, "log": log, "dirty": dirty}


class _GitFetched(Message):
    def __init__(self, data: dict) -> None:
        super().__init__()
        self.data = data


class GitStatusPane(Container):
    def compose(self):
        yield Label("  Git Status", id="git-title")
        yield RichLog(id="git-log", highlight=True, markup=True, wrap=True)

    def on_mount(self) -> None:
        self.set_interval(30, self._fetch)
        self._fetch()

    def refresh_data(self) -> None:
        self._fetch()

    @work(thread=True, exit_on_error=False)
    def _fetch(self) -> None:
        self.post_message(_GitFetched(fetch_git_status()))

    def on__git_fetched(self, event: _GitFetched) -> None:
        from textual.css.query import NoMatches
        try:
            log = self.query_one("#git-log", RichLog)
        except NoMatches:
            return
        log.clear()
        d = event.data
        log.write(f"[bold #58a6ff]branch:[/] {_e(d['branch'])}")
        log.write("")
        if d["short"] and d["short"] != "(no output)":
            log.write("[bold]working tree:[/]")
            for line in d["short"].splitlines():
                color = "red" if line[:2].strip() else "yellow"
                log.write(f"  [{color}]{_e(line)}[/]")
        else:
            log.write("[dim]working tree clean[/]")
        log.write("")
        log.write("[bold]recent commits:[/]")
        for line in d["log"].splitlines():
            parts = line.split(" ", 1)
            if len(parts) == 2:
                log.write(f"  [dim]{_e(parts[0])}[/] {_e(parts[1])}")
            else:
                log.write(f"  {_e(line)}")
