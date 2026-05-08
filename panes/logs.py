"""panes/logs.py — Log tail pane.
b17: WGRV1  ΔΣ=42
"""
from pathlib import Path

from textual import work
from textual.containers import Container
from textual.message import Message
from textual.widgets import Label, Log

WILLOW_LOGS = Path.home() / ".willow" / "logs"


def _tail_log(lines: int = 80) -> list[str]:
    try:
        logs = sorted(WILLOW_LOGS.glob("*.log"),
                      key=lambda p: p.stat().st_mtime, reverse=True)
        if not logs:
            return ["No log files found in ~/.willow/logs/"]
        return logs[0].read_text().splitlines()[-lines:]
    except Exception as e:
        return [f"Log read error: {e}"]


class _LogsFetched(Message):
    def __init__(self, lines: list[str]) -> None:
        super().__init__()
        self.lines = lines


class LogsPane(Container):
    def compose(self):
        yield Label("  Logs — ~/.willow/logs/ (most recent)", id="logs-title")
        yield Log(id="log-view", auto_scroll=True)

    def on_mount(self) -> None:
        self.set_interval(30, self._fetch)
        self._fetch()

    def refresh_data(self) -> None:
        self._fetch()

    @work(thread=True, exit_on_error=False)
    def _fetch(self) -> None:
        self.post_message(_LogsFetched(_tail_log(80)))

    def on__logs_fetched(self, event: _LogsFetched) -> None:
        from textual.css.query import NoMatches
        try:
            log = self.query_one("#log-view", Log)
        except NoMatches:
            return
        log.clear()
        for line in event.lines:
            log.write_line(line)
