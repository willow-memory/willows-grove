#!/usr/bin/env python3
"""Seat intake wrapper — same as Jeles ``scripts/jeles-intake.py``.

Home: willows-grove/seat/willow. Point JELES_INTAKE_DIR or run from a cwd
where the seat intake tree is visible; default intake lives at
``seat/willow/jeles-intake/``.

    . $WILLOW_HOME/fleet.env
    python3 seat/willow/scripts/jeles-intake.py --probe-only
"""
from __future__ import annotations

import os
from pathlib import Path

# Prefer seat-local intake when the operator has not set an override.
_SEAT = Path(__file__).resolve().parents[1]
_INTAKE = _SEAT / "jeles-intake"
if _INTAKE.is_dir() and "JELES_INTAKE_DIR" not in os.environ:
    os.environ["JELES_INTAKE_DIR"] = str(_INTAKE)

from jeles.intake import main

if __name__ == "__main__":
    raise SystemExit(main())
