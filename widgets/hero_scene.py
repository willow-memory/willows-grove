"""widgets/hero_scene.py — HeroScene: willow tree + info panel + full-width meadow.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import logging
import random
import traceback
from datetime import datetime

from rich.markup import escape as rich_escape

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widgets import Static
from textual import work

from .hero import WillowHero
from grove.apps.hero_format import (
    format_collapsed_strip_markup,
    format_ground_footer_markup,
    format_hero_info_markup,
)
from grove.apps.hero_stats import fetch_hero_stats
from grove.theme_textual import ACCENT, DEGRADED, SECONDARY
from ._hero_state import (
    get_meadow_wind, pop_pigeon_trigger,
    is_bloop, maybe_bloop, tick_bloop, trigger_bloop,
    get_timed_msg, set_timed_msg,
    start_gerald,
)

log = logging.getLogger("hero_scene")


class HeroStatsUpdated(Message):
    """Live Grove + host stats for hero widgets."""

    def __init__(self, stats: dict) -> None:
        super().__init__()
        self.stats = stats


def _hero_expanded(widget: Static) -> bool:
    parent = widget.parent
    while parent is not None:
        if isinstance(parent, HeroScene):
            return parent.is_expanded()
        parent = getattr(parent, "parent", None)
    return True


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
        self._stats: dict | None = None

    def apply_stats(self, stats: dict) -> None:
        self._stats = stats
        if _hero_expanded(self):
            try:
                self._redraw()
            except Exception:
                log.error("GroundStrip.apply_stats crash:\n%s", traceback.format_exc())

    def on_mount(self) -> None:
        self.set_interval(1.2, self._tick)
        self._redraw()

    def _tick(self) -> None:
        if not _hero_expanded(self):
            return
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
            meadow = " " * pad + f"[{SECONDARY}]{rich_escape(msg)}[/]" + " " * (w - pad - len(msg))
            trunk  = _colorize_trunk(trunk_plain)
            ground = _colorize_ground(ground_plain)
            self.update(f"{trunk}\n{meadow}\n{ground}")
            return

        # Timed message — centered in meadow row, animation continues behind it
        timed = get_timed_msg()
        if timed:
            pad    = max(0, (w - len(timed)) // 2)
            meadow = " " * pad + f"[{DEGRADED} bold]{rich_escape(timed)}[/]" + " " * (w - pad - len(timed))
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
        if self._stats:
            ground = format_ground_footer_markup(self._stats)
        else:
            ground = _colorize_ground(ground_plain)

        self.update(f"{trunk}\n{meadow}\n{ground}")


# ── Info panel ────────────────────────────────────────────────────────────────


class HeroInfo(Static):
    """Right panel: WILLOW wordmark · Grove live stats · sysinfo · clock."""

    DEFAULT_CSS = """
    HeroInfo {
        width: 1fr;
        height: 7;
        padding: 0 1 0 1;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("", **kwargs)
        self._stats: dict | None = None

    def apply_stats(self, stats: dict) -> None:
        self._stats = stats
        if _hero_expanded(self):
            self._redraw()

    def on_mount(self) -> None:
        self.set_interval(1.0, self._tick_clock)

    def _tick_clock(self) -> None:
        if not _hero_expanded(self) or not self._stats:
            return
        self._redraw()

    def _redraw(self) -> None:
        try:
            if self._stats:
                self.update(format_hero_info_markup(self._stats))
            else:
                self.update(f"[dim {SECONDARY}]loading grove stats…[/]")
        except Exception:
            log.error("HeroInfo._redraw crash:\n%s", traceback.format_exc())


# ── Collapsed strip (non-Home nav) ────────────────────────────────────────────

class HeroCollapsedStrip(Static):
    """One-line hero: ⬡ time · grove state · meadow tick."""

    DEFAULT_CSS = """
    HeroCollapsedStrip {
        height: 1;
        width: 100%;
        padding: 0 1;
        display: none;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("", **kwargs)
        self._frame = 0
        self._stats: dict | None = None

    def apply_stats(self, stats: dict) -> None:
        self._stats = stats
        self._redraw()

    def on_mount(self) -> None:
        self.set_interval(2.0, self._tick)
        self._tick()

    def _tick(self) -> None:
        if _hero_expanded(self):
            return
        self._frame += 1
        self._redraw()

    def _redraw(self) -> None:
        try:
            w = max(24, self.size.width or 80)
            meadow = _make_meadow(self._frame, w, get_meadow_wind())
            stats = self._stats or {"grove_live": False, "grove_model": ""}
            self.update(format_collapsed_strip_markup(stats, meadow))
        except Exception:
            log.error("HeroCollapsedStrip._tick crash:\n%s", traceback.format_exc())


# ── Scene ─────────────────────────────────────────────────────────────────────

class HeroScene(Vertical):
    """Hero band: full on Home; collapsed strip on all other nav targets."""

    DEFAULT_CSS = """
    HeroScene {
        height: 10;
        background: #0a0f07;
        border-bottom: solid #1e3a1e;
    }
    HeroScene.collapsed {
        height: 2;
    }
    HeroScene.collapsed #hero-top,
    HeroScene.collapsed GroundStrip {
        display: none;
    }
    HeroScene.collapsed HeroCollapsedStrip {
        display: block;
    }
    HeroScene.expanded HeroCollapsedStrip {
        display: none;
    }
    #hero-top {
        height: 7;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._expanded = True
        self._cpu_snap: tuple[int, int] | None = None
        self._stats: dict | None = None

    def is_expanded(self) -> bool:
        return self._expanded

    def set_expanded(self, expanded: bool) -> None:
        """Toggle full hero (Home) vs one-line collapsed strip."""
        if expanded == self._expanded:
            return
        self._expanded = expanded
        self.set_class(expanded, "expanded")
        self.set_class(not expanded, "collapsed")

    def compose(self) -> ComposeResult:
        with Horizontal(id="hero-top"):
            yield HeroInfo()
            yield WillowHero()
        yield GroundStrip()
        yield HeroCollapsedStrip(id="hero-collapsed")

    def on_mount(self) -> None:
        self.set_class(True, "expanded")
        self.set_class(False, "collapsed")
        self.set_interval(5.0, self._poll_stats)
        self._poll_stats()

    @work(thread=True, exit_on_error=False)
    def _poll_stats(self) -> None:
        try:
            stats = fetch_hero_stats(self._cpu_snap)
            self._cpu_snap = stats.pop("cpu_snap")
            self.post_message(HeroStatsUpdated(stats))
        except Exception:
            log.error("HeroScene._poll_stats crash:\n%s", traceback.format_exc())

    def on_hero_stats_updated(self, event: HeroStatsUpdated) -> None:
        self._stats = event.stats
        for widget in self.query(HeroInfo):
            widget.apply_stats(event.stats)
        for widget in self.query(GroundStrip):
            widget.apply_stats(event.stats)
        for widget in self.query(HeroCollapsedStrip):
            widget.apply_stats(event.stats)
