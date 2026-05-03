"""panes/health.py — Health check pane.
b17: WGRV1  ΔΣ=42
"""
import os
import subprocess
from pathlib import Path

from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Label, RichLog

WILLOW_ROOT = Path(os.environ.get("WILLOW_ROOT", Path.home() / "github" / "willow-1.9"))


class HealthPane(Container):
    BINDINGS = [Binding("r", "run_health", "Run boot check")]

    def compose(self):
        yield Label("  Health  (r=run boot check)", id="health-title")
        yield RichLog(id="health-log", auto_scroll=True, markup=True)

    def action_run_health(self) -> None:
        log    = self.query_one("#health-log", RichLog)
        script = WILLOW_ROOT / "willow" / "fylgja" / "skills" / "scripts" / "system_health.py"
        log.clear()
        log.write("Running willow health boot…")
        try:
            result = subprocess.run(
                ["python3", str(script), "--check", "boot",
                 "--willow-dir", str(Path.home() / ".willow"),
                 "--repo",        str(WILLOW_ROOT)],
                capture_output=True, text=True, timeout=30,
            )
            for line in (result.stdout + result.stderr).splitlines():
                log.write(line)
        except Exception as e:
            log.write(f"[red]Error: {e}[/]")
