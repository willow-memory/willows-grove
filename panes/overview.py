"""panes/overview.py — Overview pane: status rows + sysinfo + Hero.
b17: WGRV1  ΔΣ=42
"""
import json
import os
import shutil
import urllib.request
from pathlib import Path

from textual.containers import Container
from textual.widgets import Label, Rule

from widgets.hero       import WillowHero
from widgets.status_row import StatusRow

SESSION_ANCHOR = Path.home() / ".willow" / "session_anchor.json"


def _http_get(url: str, timeout: int = 2) -> dict | None:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read())
    except Exception:
        return None


def _pg_conn():
    import psycopg2
    return psycopg2.connect(
        dbname=os.environ.get("WILLOW_PG_DB",   "willow_19"),
        user=os.environ.get("WILLOW_PG_USER", os.environ.get("USER", "")),
    )


def _pg_status() -> tuple[bool, int]:
    try:
        conn = _pg_conn()
        cur  = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM knowledge")
        count = cur.fetchone()[0]
        conn.close()
        return True, count
    except Exception:
        return False, 0


def _ollama_status() -> tuple[bool, list[str]]:
    data = _http_get("http://localhost:11434/api/tags")
    if not data:
        return False, []
    return True, [m["name"] for m in data.get("models", [])]


def _litellm_status() -> bool:
    return _http_get("http://localhost:4000/health") is not None


def _open_tasks() -> int:
    try:
        conn = _pg_conn()
        cur  = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM public.tasks WHERE status IN ('pending','queued')")
        count = cur.fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0


def _last_handoff() -> str:
    try:
        data = json.loads(SESSION_ANCHOR.read_text())
        return data.get("handoff_title", "—")
    except Exception:
        return "—"


def fetch_sysinfo() -> dict:
    """Return cpu/mem/disk/temp as int percentages. Never raises."""
    result = {"cpu": 0, "mem": 0, "disk": 0, "temp": 0}
    try:
        with open("/proc/stat") as f:
            parts = f.readline().split()
        vals  = [int(x) for x in parts[1:]]
        idle  = vals[3] + (vals[4] if len(vals) > 4 else 0)
        result["cpu"] = max(0, min(100, int((1 - idle / max(sum(vals), 1)) * 100)))
    except Exception:
        pass
    try:
        info: dict[str, int] = {}
        with open("/proc/meminfo") as f:
            for line in f:
                k, v = line.split(":", 1)
                info[k.strip()] = int(v.strip().split()[0])
        total = info.get("MemTotal", 1)
        avail = info.get("MemAvailable", total)
        result["mem"] = max(0, min(100, int((total - avail) / total * 100)))
    except Exception:
        pass
    try:
        usage = shutil.disk_usage("/")
        result["disk"] = max(0, min(100, int(usage.used / usage.total * 100)))
    except Exception:
        pass
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            result["temp"] = int(f.read().strip()) // 1000
    except Exception:
        pass
    return result


def _bar(pct: int, width: int = 10) -> str:
    filled = int(pct / 100 * width)
    return "█" * filled + "░" * (width - filled)


class OverviewPane(Container):
    def compose(self):
        yield WillowHero(id="hero")
        yield Rule()
        yield Label("  Willow System", id="overview-title")
        yield StatusRow("Postgres     ", id="stat-pg")
        yield StatusRow("Ollama       ", id="stat-ollama")
        yield StatusRow("LiteLLM      ", id="stat-litellm")
        yield StatusRow("Open tasks   ", id="stat-tasks")
        yield StatusRow("Last handoff ", id="stat-handoff")
        yield Rule()
        yield Label("  System", id="sysinfo-title")
        yield StatusRow("CPU          ", id="stat-cpu")
        yield StatusRow("Memory       ", id="stat-mem")
        yield StatusRow("Disk         ", id="stat-disk")
        yield StatusRow("Temp         ", id="stat-temp")

    def refresh_data(self) -> None:
        pg_up, atoms = _pg_status()
        self.query_one("#stat-pg", StatusRow).set_status(
            pg_up, f"{atoms:,} KB atoms" if pg_up else "NOT CONNECTED"
        )
        ollama_up, models = _ollama_status()
        self.query_one("#stat-ollama", StatusRow).set_status(
            ollama_up, f"{len(models)} models" if ollama_up else "unreachable"
        )
        lt_up = _litellm_status()
        self.query_one("#stat-litellm", StatusRow).set_status(
            lt_up, "localhost:4000" if lt_up else "not running"
        )
        tasks = _open_tasks()
        self.query_one("#stat-tasks", StatusRow).set_status(tasks == 0, str(tasks))
        self.query_one("#stat-handoff", StatusRow).set_status(None, _last_handoff())

        info = fetch_sysinfo()
        self.query_one("#stat-cpu",  StatusRow).set_status(
            info["cpu"]  < 90, f"{_bar(info['cpu'])}  {info['cpu']}%"
        )
        self.query_one("#stat-mem",  StatusRow).set_status(
            info["mem"]  < 90, f"{_bar(info['mem'])}  {info['mem']}%"
        )
        self.query_one("#stat-disk", StatusRow).set_status(
            info["disk"] < 90, f"{_bar(info['disk'])}  {info['disk']}%"
        )
        temp_ok = None if info["temp"] == 0 else info["temp"] < 80
        self.query_one("#stat-temp", StatusRow).set_status(
            temp_ok, f"{info['temp']}°C" if info["temp"] else "n/a"
        )
