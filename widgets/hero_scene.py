"""widgets/hero_scene.py — HeroScene: willow tree + flower field + info panel.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import shutil
from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static

from .hero import WillowHero


# ── Ground strip ─────────────────────────────────────────────────────────────

GROUND_LINE = "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

_FLOWERS    = ["✿", "✾", "❀", "⚘"]
_SEPARATORS = [" │ ", " ∿ ", " │ ", " ∿ ", " │ ", " ∿ ", " │ "]


def _make_scene(frame: int) -> str:
    n = len(_FLOWERS)
    parts: list[str] = []
    for i in range(8):
        parts.append(_FLOWERS[(frame + i) % n])
        if i < 7:
            parts.append(_SEPARATORS[i])
    return "  " + "".join(parts) + "  "


class GroundStrip(Static):
    """Animated flower meadow strip — 4-frame cycle, staggered wave."""

    DEFAULT_CSS = """
    GroundStrip {
        width: 1fr;
        height: 10;
        color: #3fb950;
        padding: 2 2 0 2;
        content-align: left bottom;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("", **kwargs)
        self._frame = 0

    def on_mount(self) -> None:
        self.set_interval(0.6, self._tick)
        self._redraw()

    def _tick(self) -> None:
        self._frame = (self._frame + 1) % len(_FLOWERS)
        self._redraw()

    def _redraw(self) -> None:
        self.update(f"{_make_scene(self._frame)}\n  {GROUND_LINE}")


# ── System info ───────────────────────────────────────────────────────────────

def _sysinfo() -> dict:
    """Read cpu/mem/disk/temp from /proc. Never raises."""
    r: dict = {"cpu": 0, "mem": 0, "disk": 0, "temp": 0}
    try:
        with open("/proc/stat") as f:
            parts = f.readline().split()
        vals = [int(x) for x in parts[1:]]
        idle = vals[3] + (vals[4] if len(vals) > 4 else 0)
        r["cpu"] = max(0, min(100, int((1 - idle / max(sum(vals), 1)) * 100)))
    except Exception:
        pass
    try:
        mem: dict[str, int] = {}
        with open("/proc/meminfo") as f:
            for line in f:
                k, v = line.split(":", 1)
                mem[k.strip()] = int(v.strip().split()[0])
        total = mem.get("MemTotal", 1)
        avail = mem.get("MemAvailable", total)
        r["mem"] = max(0, min(100, int((total - avail) / total * 100)))
    except Exception:
        pass
    try:
        u = shutil.disk_usage("/")
        r["disk"] = max(0, min(100, int(u.used / u.total * 100)))
    except Exception:
        pass
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            r["temp"] = int(f.read().strip()) // 1000
    except Exception:
        pass
    return r


# ── Info panel ────────────────────────────────────────────────────────────────

class HeroInfo(Static):
    """Right panel: wordmark · version · sysinfo · live clock."""

    DEFAULT_CSS = """
    HeroInfo {
        width: 24;
        height: 10;
        color: #8b949e;
        padding: 1 1 0 1;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("", **kwargs)
        self._sys: dict = {"cpu": 0, "mem": 0, "disk": 0, "temp": 0}

    def on_mount(self) -> None:
        self.set_interval(1.0, self._tick)
        self._tick()

    def _tick(self) -> None:
        self._sys = _sysinfo()
        self._redraw()

    def _redraw(self) -> None:
        now  = datetime.now()
        t    = now.strftime("%H:%M")
        d    = now.strftime("%a %b %-d")
        s    = self._sys
        temp = f"{s['temp']}°C" if s["temp"] else "n/a"
        self.update(
            "[bold #58a6ff]◈ Willow[/]\n"
            "[bold #58a6ff]  Grove[/]\n"
            "\n"
            "[dim]v0.1[/]  [#f0883e]BETA[/]\n"
            f"[dim]cpu {s['cpu']:3d}%  mem {s['mem']:3d}%[/]\n"
            f"[dim]disk {s['disk']:3d}%  {temp}[/]\n"
            "\n"
            f"[dim]{t} · {d}[/]"
        )


# ── Scene ─────────────────────────────────────────────────────────────────────

class HeroScene(Horizontal):
    """Full-width hero band: tree (left) · flowers (center) · info (right)."""

    DEFAULT_CSS = """
    HeroScene {
        height: 10;
        background: #0d1117;
        border-bottom: solid #30363d;
    }
    HeroScene WillowHero {
        width: 28;
    }
    """

    def compose(self) -> ComposeResult:
        yield WillowHero()
        yield GroundStrip()
        yield HeroInfo()
