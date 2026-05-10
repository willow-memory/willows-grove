"""widgets/_hero_state.py — Shared runtime state between hero widgets.
b17: HERO1  ΔΣ=42
"""

_meadow_wind: str = "C"


def set_meadow_wind(pose: str) -> None:
    global _meadow_wind
    _meadow_wind = pose


def get_meadow_wind() -> str:
    return _meadow_wind
