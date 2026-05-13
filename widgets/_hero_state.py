"""widgets/_hero_state.py — Shared runtime state between hero widgets.
b17: HERO1  ΔΣ=42
"""
import random
import time as _time

_meadow_wind: str = "C"
_prompt_count: int = 0
_pigeon_pending: bool = False

# Bloop bloop — 1-in-500 per tick, freezes all animation briefly
_BLOOP_DURATION = 4   # ticks (~4.8s at 1.2s/tick)
_BLOOP_ODDS    = 500
_bloop_ticks: int = 0


def set_meadow_wind(pose: str) -> None:
    global _meadow_wind
    _meadow_wind = pose


def get_meadow_wind() -> str:
    return _meadow_wind


def increment_prompt() -> int:
    """Increment prompt counter; arms pigeon trigger at 17."""
    global _prompt_count, _pigeon_pending
    _prompt_count += 1
    if _prompt_count == 17:
        _pigeon_pending = True
    return _prompt_count


def trigger_pigeon() -> None:
    """Directly arm the pigeon (for testing / manual trigger)."""
    global _pigeon_pending
    _pigeon_pending = True


def pop_pigeon_trigger() -> bool:
    """Return True once and reset if the pigeon was armed."""
    global _pigeon_pending
    if _pigeon_pending:
        _pigeon_pending = False
        return True
    return False


# ── Bloop bloop ───────────────────────────────────────────────────────────────

def is_bloop() -> bool:
    return _bloop_ticks > 0


def maybe_bloop() -> bool:
    """Roll the die. Call once per main tick. Returns True if bloop just fired."""
    global _bloop_ticks
    if _bloop_ticks > 0:
        return False
    if random.randint(1, _BLOOP_ODDS) == 1:
        _bloop_ticks = _BLOOP_DURATION
        return True
    return False


def tick_bloop() -> None:
    """Decrement bloop countdown. Call once per main tick while blooping."""
    global _bloop_ticks
    if _bloop_ticks > 0:
        _bloop_ticks -= 1


def trigger_bloop() -> None:
    """Directly arm bloop (for testing)."""
    global _bloop_ticks
    _bloop_ticks = _BLOOP_DURATION


# ── Timed meadow message ──────────────────────────────────────────────────────

_timed_msg: str = ""
_timed_msg_expires: float = 0.0


def set_timed_msg(text: str, duration_s: float) -> None:
    global _timed_msg, _timed_msg_expires
    _timed_msg = text
    _timed_msg_expires = _time.time() + duration_s


def get_timed_msg() -> str:
    return _timed_msg if _time.time() < _timed_msg_expires else ""


# ── Gerald at midnight ────────────────────────────────────────────────────────

_GERALD_DURATION = 12   # ticks (~14s at 1.2s/tick — one slow pass)
_gerald_ticks: int = 0


def is_gerald() -> bool:
    return _gerald_ticks > 0


def gerald_frame() -> int:
    """Frame index (0-based) counting up from when Gerald started."""
    return _GERALD_DURATION - _gerald_ticks


def tick_gerald() -> None:
    global _gerald_ticks
    if _gerald_ticks > 0:
        _gerald_ticks -= 1


def start_gerald() -> None:
    global _gerald_ticks
    _gerald_ticks = _GERALD_DURATION


def trigger_gerald() -> None:
    start_gerald()
