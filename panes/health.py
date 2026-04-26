"""panes/health.py — Health check pane.
b17: WGRV1  ΔΣ=42
"""
import os
import subprocess
from pathlib import Path

from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Label, Log

WILLOW_ROOT = Path(os.environ.get("WILLOW_ROOT", Path.home() / "github" / "willow-1.9"))


class HealthPane(Container):
    BINDINGS = [Binding("r", "run_health", "Run boot check")]

    def compose(self):
        yield Label("  Health  (r=run boot check)", id="health-title")
        yield Log(id="health-log", auto_scroll=True)

    def action_run_health(self) -> None:
        log    = self.query_one("#health-log", Log)
        script = WILLOW_ROOT / "willow" / "fylgja" / "skills" / "scripts" / "system_health.py"
        log.clear()
        log.write_line("Running willow health boot…")
        try:
            result = subprocess.run(
                ["python3", str(script), "--check", "boot",
                 "--willow-dir", str(Path.home() / ".willow"),
                 "--repo",        str(WILLOW_ROOT)],
                capture_output=True, text=True, timeout=30,
            )
            for line in (result.stdout + result.stderr).splitlines():
                color = ("green"  if "HEALTHY"  in line else
                         "red"    if "CRITICAL" in line else
                         "yellow" if "WARN"     in line else "")
                log.write_line(f"[{color}]{line}[/]" if color else line)
        except Exception as e:
            log.write_line(f"[red]Error: {e}[/]")
