"""widgets/hero_scene.py — HeroScene: willow tree + info panel + full-width meadow.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import logging
import random
import shutil
import time
import traceback
from datetime import datetime

from rich.markup import escape as rich_escape

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static

from grove.theme_textual import SECONDARY

from .hero import WillowHero
from ._hero_state import (
    get_meadow_wind, pop_pigeon_trigger,
    is_bloop, maybe_bloop, tick_bloop, trigger_bloop,
    get_timed_msg, set_timed_msg,
    start_gerald,
)

log = logging.getLogger("hero_scene")


# ── Ground strip ─────────────────────────────────────────────────────────────

_BLOOMS = ["✿", "✾", "❀", "⚘"]

# Summer bloom colors — pink wild rose, orange marigold, yellow buttercup, lavender clover
_BLOOM_COLORS: dict[str, str] = {
    "✿": "#f9a8d4",
    "✾": "#fb923c",
    "❀": "#fde68a",
    "⚘": "#c4b5fd",
}

# Mo Willems pigeon — walks across the meadow at prompt 17
# head on trunk row (above grass), body+legs combined on meadow row
_PIGEON_HEAD = "  o> "           # 5 chars — head + beak (trunk row)
_PIGEON_BOTS = ("(II) ", "(JI) ", "(IJ) ")  # body + walking legs (meadow row, 3 frames)

_PIGEON_COLORS: dict[str, str] = {
    "o": "#fbbf24",   # beady eye — sunlight gold
    "(": "#94a3b8",   # body — slate blue-gray
    ")": "#94a3b8",
    "_": "#94a3b8",   # belly
    ">": "#e2e8f0",   # beak — off-white
    "I": "#94a3b8",   # legs (uppercase I, not pipe)
    "J": "#94a3b8",   # bent leg
}

_PIGEON_SPEED = 3.0   # chars per tick (1.2s tick → ~2.5 chars/sec)


def _overlay(base: str, pos: int, text: str) -> str:
    """Replace chars in plain string at pos..pos+len(text)."""
    pos = max(0, pos)
    if pos >= len(base):
        return base
    end = min(len(base), pos + len(text))
    return base[:pos] + text[:end - pos] + base[end:]


def _colorize_trunk(line: str) -> str:
    """Colorize trunk row: ║ bark brown, pigeon head chars blue-gray/gold."""
    out = []
    for ch in line:
        if ch == "║":
            out.append("[#a16207]║[/]")
        elif ch in _PIGEON_COLORS:
            out.append(f"[{_PIGEON_COLORS[ch]}]{ch}[/]")
        else:
            out.append(ch)
    return "".join(out)


def _colorize_meadow(line: str) -> str:
    """Colorize meadow: blooms/pigeon per-char; batch plain grass so \\ never prefixes a tag."""
    out: list[str] = []
    plain: list[str] = []

    def flush_plain() -> None:
        if plain:
            out.append(f"[{SECONDARY}]{rich_escape(''.join(plain))}[/]")
            plain.clear()

    for ch in line:
        if ch in _BLOOM_COLORS:
            flush_plain()
            out.append(f"[bold {_BLOOM_COLORS[ch]}]{ch}[/]")
        elif ch in _PIGEON_COLORS:
            flush_plain()
            out.append(f"[{_PIGEON_COLORS[ch]}]{ch}[/]")
        else:
            plain.append(ch)
    flush_plain()
    return "".join(out)


def _colorize_ground(line: str) -> str:
    """Colorize ground: ≈ ripple deeper green, pigeon legs blue-gray."""
    out = []
    for ch in line:
        if ch == "≈":
            out.append("[#65a30d]≈[/]")
        elif ch == "|":
            out.append("[#94a3b8]|[/]")
        else:
            out.append(ch)
    return "".join(out)

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
        color: #16a34a;
        padding: 0;
        content-align: left bottom;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("", **kwargs)
        self._frame        = 0
        self._pigeon_active = False
        self._pigeon_x     = -4.0

    def on_mount(self) -> None:
        self.set_interval(1.2, self._tick)
        self._redraw()

    def _tick(self) -> None:
        # Roll the bloop die — one roller for the whole widget set
        maybe_bloop()

        if is_bloop():
            tick_bloop()
            try:
                self._redraw()
            except Exception:
                log.error("GroundStrip._tick(bloop) crash:\n%s", traceback.format_exc())
            return

        self._frame += 1

        # ── Time-based triggers ────────────────────────────────────────────────
        now = datetime.now()

        # Gerald at midnight (00:00) — headless rotisserie chicken in the crown
        if now.hour == 0 and now.minute == 0 and now.second < 2:
            from .hero_db import can_fire, fire, register_egg
            register_egg("egg-gerald", "Gerald at midnight", cooldown_s=86400)
            if can_fire("egg-gerald"):
                fire("egg-gerald")
                start_gerald()

        # 1:42 — CAN YOU HEAR TAOS NOW (21 chars, 21 seconds)
        if now.hour in (1, 13) and now.minute == 42 and now.second < 2:
            from .hero_db import can_fire, fire, register_egg
            register_egg("egg-142", "1:42", cooldown_s=3600)
            if can_fire("egg-142"):
                fire("egg-142")
                set_timed_msg("CAN YOU HEAR TAOS NOW", 21)

        # Hotdog at 0.318 — embed backfill queue counter
        from .hero_db import get_counter, can_fire as _can_fire, fire as _fire, register_egg as _reg
        if get_counter("embed_backfill_queue") == 318:
            _reg("egg-hotdog", "Hotdog at 0.318", cooldown_s=300)
            if _can_fire("egg-hotdog"):
                _fire("egg-hotdog")
                set_timed_msg("(≡) 0.318", 10)

        # ── Pigeon ────────────────────────────────────────────────────────────
        if pop_pigeon_trigger():
            self._pigeon_active = True
            self._pigeon_x = -4.0
        if self._pigeon_active:
            self._pigeon_x += _PIGEON_SPEED
            w = max(20, self.size.width or 120)
            if self._pigeon_x > w + 4:
                self._pigeon_active = False

        try:
            self._redraw()
        except Exception:
            log.error("GroundStrip._tick crash (frame=%d):\n%s", self._frame, traceback.format_exc())

    def _redraw(self) -> None:
        w = max(20, self.size.width or 120)

        # Build plain text for all three rows
        meadow_plain = _make_meadow(self._frame, w, get_meadow_wind())
        ground_plain = _make_ground(self._frame, w)
        tx = w - 13
        trunk_plain = (" " * max(0, tx) + "║" + " " * max(0, w - tx - 1))[:w] if 0 <= tx < w else " " * w

        # Bloop bloop — replace meadow with centered deflated text, hold scene frozen
        if is_bloop():
            msg    = "Bloop bloop."
            pad    = max(0, (w - len(msg)) // 2)
            meadow = " " * pad + f"[#8b949e]{msg}[/]" + " " * (w - pad - len(msg))
            trunk  = _colorize_trunk(trunk_plain)
            ground = _colorize_ground(ground_plain)
            self.update(f"{trunk}\n{meadow}\n{ground}")
            return

        # Timed message — centered in meadow row, animation continues behind it
        timed = get_timed_msg()
        if timed:
            pad    = max(0, (w - len(timed)) // 2)
            meadow = " " * pad + f"[bold #f0883e]{timed}[/]" + " " * (w - pad - len(timed))
            trunk  = _colorize_trunk(trunk_plain)
            ground = _colorize_ground(ground_plain)
            self.update(f"{trunk}\n{meadow}\n{ground}")
            return

        # Overlay pigeon: head above grass (trunk row), body+legs in grass (meadow row)
        if self._pigeon_active:
            px   = int(self._pigeon_x)
            body = _PIGEON_BOTS[self._frame % len(_PIGEON_BOTS)]
            trunk_plain  = _overlay(trunk_plain,  px, _PIGEON_HEAD)
            meadow_plain = _overlay(meadow_plain, px, body)

        trunk  = _colorize_trunk(trunk_plain)
        meadow = _colorize_meadow(meadow_plain)
        ground = _colorize_ground(ground_plain)

        self.update(f"{trunk}\n{meadow}\n{ground}")


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

# USER's WILLOW wordmark from dashboard sketch — escaped for Rich markup
_WILLOW_ART = [
    r"_  _  _  __ __  __    _  _  _  _",
    r"\\ \\ \\ || ||  ||  / o\ \\ \\ \\ ",  # trailing space prevents \[/] markup escape
    r" \\/ \// || |_] |_} \__/  \\/ \//",
]


class HeroInfo(Static):
    """Right panel: WILLOW wordmark · sysinfo · live clock."""

    DEFAULT_CSS = """
    HeroInfo {
        width: 1fr;
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
        try:
            if not is_bloop():
                self._sys, self._prev_cpu = _sysinfo(self._prev_cpu)
                self._redraw()
        except Exception:
            log.error("HeroInfo._tick crash:\n%s", traceback.format_exc())

    def _redraw(self) -> None:
        try:
            now  = datetime.now()
            t    = now.strftime("%H:%M")
            d    = now.strftime("%a %b %-d")
            s    = self._sys
            temp = f"{s['temp']}°C" if s["temp"] else "n/a"
            art  = "\n".join(f"[bold #f59e0b]{l}[/]" for l in _WILLOW_ART)
            self.update(
                f"{art}\n"
                "\n"
                f"[dim]v0.1[/]  [#f0883e]BETA[/]  "
                f"[dim]cpu {s['cpu']:3d}%  mem {s['mem']:3d}%  "
                f"disk {s['disk']:3d}%  {temp}[/]\n"
                f"[dim]{t} · {d}[/]"
            )
        except Exception:
            log.error("HeroInfo._redraw crash:\n%s", traceback.format_exc())


# ── Scene ─────────────────────────────────────────────────────────────────────

class HeroScene(Vertical):
    """Hero band: top row (tree + info) over full-width meadow ground."""

    DEFAULT_CSS = """
    HeroScene {
        height: 10;
        background: #0a0f07;
        border-bottom: solid #1e3a1e;
    }
    #hero-top {
        height: 7;
    }
    """

    def compose(self) -> ComposeResult:
        with Horizontal(id="hero-top"):
            yield HeroInfo()
            yield WillowHero()
        yield GroundStrip()
