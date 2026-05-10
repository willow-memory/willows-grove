"""widgets/hero_scene.py — HeroScene: willow tree + info panel + full-width meadow.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import random
import shutil
from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static

from .hero import WillowHero
from ._hero_state import get_meadow_wind


# ── Ground strip ─────────────────────────────────────────────────────────────

_BLOOMS = ["✿", "✾", "❀", "⚘"]

# Grass fill strings per wind direction — calm, leaning left, leaning right
_GRASS: dict[str, list[str]] = {
    "C": [",", ".", " ,", ", ", ".,", ", "],
    "L": ["\\", ".\\", " \\", ",\\", ".,", "\\,"],
    "R": ["/", "./", " /", ",/", ".,", "/,"],
}

# Ground line chars — slightly varied so it feels alive
_GROUND = ["~", "~", "~", "≈", "~", "~", "~", "~", "≈", "~"]



def _make_meadow(frame: int, width: int, wind: str = "C") -> str:
    """Sparse meadow — stable layout, blooms cycle independently per position."""
    # Layout seed changes slowly (every 10 ticks) so grass doesn't flicker
    layout_rng = random.Random((frame // 10) * 7919)
    grass_opts = _GRASS.get(wind, _GRASS["C"])
    cells = []
    x     = 0
    while x < width - 1:
        gap  = layout_rng.randint(8, 18)
        gstr = grass_opts[layout_rng.randint(0, len(grass_opts) - 1)]
        fill = (gstr * (gap // len(gstr) + 1))[:gap]
        cells.append(fill[:max(0, width - x - 1)])
        x += gap
        if x < width - 1:
            # each bloom cycles at its own pace — staggered by x position
            bloom_idx = (frame + x * 3) % (len(_BLOOMS) * 4) // 4
            cells.append(_BLOOMS[bloom_idx % len(_BLOOMS)])
            x += 1
    return "".join(cells)[:width]


def _make_ground(frame: int, width: int) -> str:
    """Ground line — mostly tildes with occasional ≈ ripple."""
    return "".join(_GROUND[(frame + i) % len(_GROUND)] for i in range(width))


class GroundStrip(Static):
    """Full-width meadow — sparse flowers, wind-reactive grass, rippling ground."""

    DEFAULT_CSS = """
    GroundStrip {
        height: 3;
        width: 100%;
        color: #3fb950;
        padding: 0;
        content-align: left bottom;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("", **kwargs)
        self._frame = 0

    def on_mount(self) -> None:
        self.set_interval(1.2, self._tick)
        self._redraw()

    def _tick(self) -> None:
        self._frame += 1  # unbounded — unique layout every ~12s
        self._redraw()

    def _redraw(self) -> None:
        w      = max(20, self.size.width or 120)
        meadow = _make_meadow(self._frame, w, get_meadow_wind())
        ground = _make_ground(self._frame, w)
        self.update(f"\n{meadow}\n{ground}")


# ── System info ───────────────────────────────────────────────────────────────

def _read_cpu_ticks() -> tuple[int, int]:
    """Return (idle_ticks, total_ticks) from /proc/stat."""
    try:
        with open("/proc/stat") as f:
            parts = f.readline().split()
        vals = [int(x) for x in parts[1:]]
        idle = vals[3] + (vals[4] if len(vals) > 4 else 0)  # idle + iowait
        return idle, sum(vals)
    except Exception:
        return 0, 1


def _sysinfo(prev_cpu: tuple[int, int]) -> tuple[dict, tuple[int, int]]:
    """Return (metrics_dict, new_cpu_snapshot) — CPU is a delta against prev_cpu."""
    r: dict = {"cpu": 0, "mem": 0, "disk": 0, "temp": 0}
    cur_idle, cur_total = _read_cpu_ticks()
    delta_total = cur_total - prev_cpu[1]
    delta_idle  = cur_idle  - prev_cpu[0]
    if delta_total > 0:
        r["cpu"] = max(0, min(100, int((1 - delta_idle / delta_total) * 100)))
    try:
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
    return r, (cur_idle, cur_total)


# ── Info panel ────────────────────────────────────────────────────────────────

# Sean's WILLOW wordmark from dashboard sketch — escaped for Rich markup
_WILLOW_ART = [
    r"_  _  _  __ __  __    _  _  _  _",
    r"\\ \\ \\ || ||  ||  / o\ \\ \\ \\ ",  # trailing space prevents \[/] markup escape
    r" \\/ \// || |_] |_} \__/  \\/ \//",
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
        self._prev_cpu: tuple[int, int] = _read_cpu_ticks()

    def on_mount(self) -> None:
        self.set_interval(1.0, self._tick)
        self._tick()

    def _tick(self) -> None:
        self._sys, self._prev_cpu = _sysinfo(self._prev_cpu)
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
