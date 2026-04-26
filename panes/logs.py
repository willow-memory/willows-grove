"""panes/logs.py — Log tail pane.
b17: WGRV1  ΔΣ=42
"""
from pathlib import Path

from textual.containers import Container
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


class LogsPane(Container):
    def compose(self):
        yield Label("  Logs — ~/.willow/logs/ (most recent)", id="logs-title")
        yield Log(id="log-view", auto_scroll=True)

    def refresh_data(self) -> None:
        log = self.query_one("#log-view", Log)
        log.clear()
        for line in _tail_log(80):
            log.write_line(line)
