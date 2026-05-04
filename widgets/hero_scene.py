"""widgets/hero_scene.py — HeroScene: willow tree + info panel + full-width meadow.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import random
import shutil
from datetime import datetime

from rich.markup import escape
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static

from .hero import WillowHero


# ── Ground strip ─────────────────────────────────────────────────────────────

_BLOOMS   = ["✿", "✾", "❀", "⚘", "✿", "❀"]
_GRASS    = [",", ".", ",,", " ,", ", "]
_GROUND   = "~" * 80


def _make_meadow(frame: int, width: int) -> str:
    """Organic meadow row — flowers at irregular intervals with grass between."""
    rng   = random.Random(frame * 7919)   # deterministic per frame
    cells = []
    x     = 0
    while x < width - 2:
        gap = rng.randint(2, 6)
        cells.append(_GRASS[rng.randint(0, len(_GRASS) - 1)] * max(1, gap // 2))
        x += gap
        if x < width - 2:
            cells.append(_BLOOMS[(frame + x) % len(_BLOOMS)])
            x += 1
    return "".join(cells)[:width]


class GroundStrip(Static):
    """Full-width meadow — irregular flowers + grass, single ground line."""

    DEFAULT_CSS = """
    GroundStrip {
        height: 3;
        color: #3fb950;
        padding: 0 0 0 0;
        content-align: left bottom;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("", **kwargs)
        self._frame = 0

    def on_mount(self) -> None:
        self.set_interval(0.8, self._tick)
        self._redraw()

    def _tick(self) -> None:
        self._frame = (self._frame + 1) % len(_BLOOMS)
        self._redraw()

    def _redraw(self) -> None:
        w = max(20, self.size.width or 80)
        meadow = _make_meadow(self._frame, w)
        ground = _GROUND[:w]
        self.update(f"\n{meadow}\n{ground}")


# ── System info ───────────────────────────────────────────────────────────────

def _sysinfo() -> dict:
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

# Sean's WILLOW wordmark from dashboard sketch — escaped for Rich markup
_WILLOW_ART = [
    escape("_  _  _  __ __  __    _  _  _  _"),
    escape("\\\\ \\\\ \\\\ || ||  ||  / o\\ \\\\ \\\\ \\\\"),
    escape(" \\\\/ \\\\// || |_] |_} \\\\__/  \\\\/ \\\\//"),
]


class HeroInfo(Static):
    """Right panel: WILLOW wordmark · sysinfo · live clock."""

    DEFAULT_CSS = """
    HeroInfo {
        width: 36;
        height: 7;
        color: #8b949e;
        padding: 0 1 0 1;
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
        art  = "\n".join(f"[bold #58a6ff]{l}[/]" for l in _WILLOW_ART)
        self.update(
            f"{art}\n"
            "\n"
            f"[dim]v0.1[/]  [#f0883e]BETA[/]  "
            f"[dim]cpu {s['cpu']:3d}%  mem {s['mem']:3d}%  "
            f"disk {s['disk']:3d}%  {temp}[/]\n"
            f"[dim]{t} · {d}[/]"
        )


# ── Scene ─────────────────────────────────────────────────────────────────────

class HeroScene(Vertical):
    """Hero band: top row (tree + info) over full-width meadow ground."""

    DEFAULT_CSS = """
    HeroScene {
        height: 10;
        background: #0d1117;
        border-bottom: solid #30363d;
    }
    #hero-top {
        height: 7;
    }
    """

    def compose(self) -> ComposeResult:
        with Horizontal(id="hero-top"):
            yield WillowHero()
            yield HeroInfo()
        yield GroundStrip()
