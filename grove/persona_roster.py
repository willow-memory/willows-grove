# b17: WGRV1 ΔΣ=42
"""Reader for the unified persona registry (D10 consumer).

``willow-memory/willow/fleet_personas.json`` — schema ``fleet-personas/v1``
— extends ``fleet.json`` with per-agent ``voice`` (register, mandate,
not_do), ``visual`` (color, sigil, color_token), ``emission_fields``,
and a ``canonical_file`` pointer per D10 in
``docs/design/willow-grove-premise.md``.

Three-state contract (see ``docs/INVARIANTS.md §1``):

* populated    — ``PersonaRoster.load()`` returns a roster with rows.
* empty        — ``PersonaRoster.load()`` returns a roster with no rows
                 (file present, ``agents`` / ``personas`` empty).
* unreachable  — ``PersonaRoster.load()`` raises ``Unreachable`` when
                 no registry file is found on any probe path.

INVARIANTS.md §2 supersedes the earlier D7 reading: absence is a state
AND it must render distinctly, so this module no longer returns ``None``
for "source not reached" — it raises. Callers translate that into a
503 response with ``state="unreachable"``.

Style: one small synchronous class, no threading or async. Writes are
governance acts (Article VIII) and belong to the charter — this module
never writes to the registry.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Iterable, Optional

from grove.errors import Unreachable

log = logging.getLogger(__name__)

SCHEMA_ID = "fleet-personas/v1"

# Module-level log-once flag. Reset by tests via ``persona_roster._logged_missing = False``.
_logged_missing = False


def _candidate_paths() -> list[Path]:
    """The three locations we probe, in preference order (D10 + D7)."""
    paths: list[Path] = []
    home = os.environ.get("WILLOW_HOME")
    if home:
        paths.append(
            Path(home).expanduser() / "willow-memory" / "willow" / "fleet_personas.json"
        )
    paths.append(Path.home() / "willow-memory" / "willow" / "fleet_personas.json")
    paths.append(Path.home() / ".willow" / "fleet_personas.json")
    return paths


def locate_personas_file() -> Optional[Path]:
    """Return the first existing registry file, or ``None``.

    Emits a single info log on absence (log-once discipline, matches
    ``grove/fleet_presence.py`` and the almanac-seam reference in
    D7 — ``hornbook-knowledge/oakenscrolls-office/almanac_seam.py``).
    """
    global _logged_missing
    for p in _candidate_paths():
        try:
            if p.is_file():
                return p
        except OSError:  # unreadable candidate — treat as absent
            continue
    if not _logged_missing:
        log.info(
            "persona_roster: fleet_personas.json not found in known "
            "locations ($WILLOW_HOME, ~/willow-memory, ~/.willow) — "
            "running as no-op (D7)."
        )
        _logged_missing = True
    return None


class PersonaRow(dict):
    """One persona row — dict payload plus attribute access on D10 keys.

    Grove's renderers read either shape (``row["role"]`` or ``row.role``);
    the six D10-mandated fields are surfaced as properties so a typo on
    a caller's side is a clean ``None`` rather than a KeyError, matching
    the D7 "absence is a state" posture.
    """

    @property
    def trust(self) -> Any:
        return self.get("trust")

    @property
    def role(self) -> Any:
        return self.get("role")

    @property
    def voice(self) -> Any:
        return self.get("voice")

    @property
    def visual(self) -> Any:
        return self.get("visual")

    @property
    def canonical_file(self) -> Any:
        return self.get("canonical_file")

    @property
    def emission_fields(self) -> Any:
        return self.get("emission_fields")


def _coerce_rows(agents: Any, path: Path) -> list[PersonaRow]:
    if not isinstance(agents, list):
        raise ValueError(
            f"persona_roster: {path} — 'agents' must be a list, got {type(agents).__name__}"
        )
    rows: list[PersonaRow] = []
    for entry in agents:
        if isinstance(entry, dict):
            rows.append(PersonaRow(entry))
    return rows


def _load_from_path(path: Path) -> list[PersonaRow]:
    """Parse + validate one registry file. Raises ValueError on schema drift.

    Tolerates both document shapes seen in the wild:

    * Flat wrapper: ``{"schema": "fleet-personas/v1", "agents": [...]}`` or
      ``{"schema": "fleet-personas/v1", "personas": {agent: row, ...}}``.
    * Charter (canonical on-disk) shape: ``{"_meta": {"schema": "...", ...},
      "willow": {...}, "heimdallr": {...}, ...}`` — schema is nested under
      ``_meta``, and every non-``_meta`` top-level key is an agent row.

    Both must load; the charter file at ``~/willow-memory/willow/
    fleet_personas.json`` is not migrated by Grove (D10 discipline — the
    charter is authoritative; readers adapt).
    """
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        raise ValueError(f"persona_roster: {path} is not valid JSON: {err}") from err
    if not isinstance(data, dict):
        raise ValueError(f"persona_roster: {path} — top level must be a JSON object")

    # Resolve schema id — check top-level first, then fall back to _meta.schema
    # for the charter shape.
    schema = data.get("schema")
    if schema is None:
        meta = data.get("_meta")
        if isinstance(meta, dict):
            schema = meta.get("schema")
    if schema != SCHEMA_ID:
        raise ValueError(
            f"persona_roster: {path} has schema {schema!r}; expected {SCHEMA_ID!r}. "
            "Unknown schema versions are rejected — bump this reader before consuming."
        )

    # Prefer the explicit wrapper keys when present.
    if "agents" in data:
        return _coerce_rows(data.get("agents"), path)
    if "personas" in data and isinstance(data.get("personas"), dict):
        return _coerce_rows_from_map(data["personas"], path)

    # Charter shape: every non-``_meta``/non-``schema`` top-level key is an
    # agent row. Inject the key as ``agent`` so ``PersonaRoster.get()`` can
    # look it up regardless of whether the row carries its own ``agent``
    # field.
    charter_agents: dict[str, Any] = {
        key: value
        for key, value in data.items()
        if key not in ("_meta", "schema") and isinstance(value, dict)
    }
    return _coerce_rows_from_map(charter_agents, path)


def _coerce_rows_from_map(agents: Any, path: Path) -> list[PersonaRow]:
    """Turn ``{agent: row, ...}`` into an ordered list of ``PersonaRow``s.

    The row's key is injected as the ``agent`` field when the row does not
    already carry one, so ``roster.get(name)`` lands regardless of shape.
    """
    if not isinstance(agents, dict):
        raise ValueError(
            f"persona_roster: {path} — expected an object mapping agent → row, "
            f"got {type(agents).__name__}"
        )
    rows: list[PersonaRow] = []
    for name, entry in agents.items():
        if not isinstance(entry, dict):
            continue
        row = PersonaRow(entry)
        if not row.get("agent"):
            row["agent"] = name
        rows.append(row)
    return rows


class PersonaRoster:
    """Read helper for the unified persona registry (fleet-personas/v1).

    Typical use::

        roster = PersonaRoster.load()
        if roster is None:
            return  # D7 — no registry present, render bare fleet.json
        willow = roster.get("willow")
        governors = roster.by_role("governance")

    The reader is offline and read-only (D10 warrant): writes to the
    registry are Article VIII amendments and go through the charter,
    not through Grove.
    """

    def __init__(
        self,
        path: Optional[str | os.PathLike] = None,
        rows: Optional[Iterable[PersonaRow]] = None,
    ) -> None:
        if rows is not None:
            self._path = Path(path) if path is not None else None
            self._rows = [r if isinstance(r, PersonaRow) else PersonaRow(r) for r in rows]
            return
        if path is None:
            resolved = locate_personas_file()
        else:
            resolved = Path(path).expanduser()
        self._path = resolved
        self._rows = _load_from_path(resolved) if resolved is not None else []

    @classmethod
    def load(cls) -> "PersonaRoster":
        """Locate + load. Raises ``Unreachable`` when no registry file exists.

        Three-state contract (INVARIANTS.md §1):

        * populated / empty → returns a ``PersonaRoster`` (rows may be []).
        * unreachable       → raises ``Unreachable`` with the probe list.

        Prior behavior returned ``None`` on absence and callers checked for
        it; INVARIANTS.md §2 supersedes that — the ``Unreachable`` sentinel
        is what the endpoint translates into a 503 payload.
        """
        path = locate_personas_file()
        if path is None:
            raise Unreachable(
                "no fleet_personas.json found in probe path "
                "($WILLOW_HOME/willow-memory/willow, ~/willow-memory/willow, ~/.willow)"
            )
        return cls(path=path)

    # ---- introspection ----
    @property
    def path(self) -> Optional[Path]:
        return self._path

    # ---- read helpers ----
    def all(self) -> list[PersonaRow]:
        """Every row, in the order the registry lists them (fleet order)."""
        return list(self._rows)

    def get(self, agent: str) -> Optional[PersonaRow]:
        """Return the row for ``agent``, or ``None`` if not present.

        Matches on the canonical ``agent`` key first, then falls back to
        ``name`` / ``id`` so a fleet.json shape lands the same lookup.
        """
        for row in self._rows:
            for key in ("agent", "name", "id"):
                value = row.get(key)
                if isinstance(value, str) and value == agent:
                    return row
        return None

    def by_role(self, role: str) -> list[PersonaRow]:
        """Filter rows by ``role``, in fleet order."""
        return [row for row in self._rows if row.get("role") == role]


__all__ = [
    "PersonaRoster",
    "PersonaRow",
    "SCHEMA_ID",
    "locate_personas_file",
]
