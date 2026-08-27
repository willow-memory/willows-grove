# b17: WGRV1 ΔΣ=42
"""Grove-side wrapper around ``fleet_presence`` — announce + roster (D7).

``fleet_presence`` (safe-app-store/libs/fleet-presence) is the fleet's
shared "one memory" seam: apps ``announce()`` a small presence atom
into the shared vault and ``roster()`` back what everyone else has
announced. Grove uses it under the ``"grove"`` app_id so the seat
shows up in the fleet's own memory alongside every other app.

Per D7 the seam is an add-on: if ``fleet_presence`` is not importable,
we log-once and every *write* call (``announce_grove`` / ``withdraw``)
becomes a silent no-op returning ``False``. The *reader* ``roster()``
is bound by INVARIANTS.md §1 three-state: it returns a list (populated
OR empty) OR raises ``grove.errors.Unreachable``. A bare ``[]`` from
``roster()`` means "seam reached, nobody announcing" — never "seam
absent" and never "seam raised".
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from grove.errors import Unreachable

log = logging.getLogger(__name__)

APP_ID = "grove"

_import_error: Optional[BaseException] = None
_logged_missing = False

try:  # add-on probe — one try, cached; matches oakenscrolls almanac_seam.
    import fleet_presence as _fp  # type: ignore[import-not-found]
except Exception as err:  # noqa: BLE001 — any import error is an absent add-on
    _fp = None  # type: ignore[assignment]
    _import_error = err


def _available() -> bool:
    global _logged_missing
    if _fp is not None:
        return True
    if not _logged_missing:
        log.info("fleet_presence not installed (%s) — Grove runs without presence (D7).", _import_error)
        _logged_missing = True
    return False


def announce_grove(summary: str, counts: Optional[dict[str, int]] = None) -> bool:
    """Publish Grove's presence atom into the shared vault.

    Returns ``True`` if the write landed, ``False`` if the seam is
    absent OR the shared store simply is not reachable (the
    library's own standalone-safe no-op). Writes have no empty case
    per §1, so a bool return is faithful to the contract.
    """
    if not _available():
        return False
    try:
        return bool(_fp.announce(APP_ID, summary, counts or {}))
    except Exception as err:  # noqa: BLE001 — never raise into Grove UI
        log.warning("fleet_presence.announce failed: %s", err)
        return False


def roster() -> list[dict[str, Any]]:
    """Return the current fleet-presence atoms (one per announcing app).

    INVARIANTS.md §1 three-state reader:

    * populated  → non-empty ``list[dict]`` from the seam
    * empty      → ``[]`` — seam reached, no app announcing
    * unreachable→ raises ``grove.errors.Unreachable`` — add-on not
      importable, or the seam's own ``roster()`` raised.

    A bare ``[]`` is reserved for the actually-empty store. The two
    unreachable branches used to collapse into ``[]`` — Loki M7 — and
    that made "no fleet reachable" look identical to "fleet reached,
    nobody home." §1 forbids that; both are ``Unreachable`` now.
    """
    if not _available():
        raise Unreachable(
            f"fleet_presence add-on not installed: {_import_error}"
        )
    try:
        rows = _fp.roster()
    except Exception as err:  # noqa: BLE001 — seam failure is unreachable, not empty
        log.warning("fleet_presence.roster failed: %s", err)
        raise Unreachable(f"fleet_presence.roster failed: {err}") from err
    return list(rows) if rows else []


def withdraw() -> bool:
    """Soft-withdraw Grove's own presence atom (states, not deletions)."""
    if not _available():
        return False
    withdraw_fn = getattr(_fp, "withdraw", None)
    if withdraw_fn is None:
        return False
    try:
        return bool(withdraw_fn(APP_ID))
    except Exception as err:  # noqa: BLE001
        log.warning("fleet_presence.withdraw failed: %s", err)
        return False


__all__ = ["APP_ID", "announce_grove", "roster", "withdraw"]
