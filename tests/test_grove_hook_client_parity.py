"""Sealed Grove acts must have a live client-hooks path that reaches them.

Proposal §6 / plan Slice A: today only sealed↔wiring.json is pinned
(`test_grove_hook_wiring_generated.py`). This file pins the other half —
every sealed (event, action) must map to a client-hooks.json live action
that eventually invokes that Grove function.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEALED = ROOT / "governance" / "decisions" / "grove-hook-rows-sealed.json"
CLIENT = ROOT / "hooks" / "client-hooks.json"

# Sealed Grove act → live client-hooks action that covers it.
# Composites: session_start covers orient; before_stop covers gate;
# session_end covers deposit.
_SEALED_COVERED_BY: dict[tuple[str, str], str] = {
    ("session_start", "orient"): "session_start",
    ("prompt_submit", "reinject"): "reinject",
    ("pre_compact", "reinject"): "reinject",
    ("stop", "gate"): "before_stop",
    ("session_end", "deposit"): "session_end",
}


def test_every_sealed_row_has_a_live_client_action():
    sealed = json.loads(SEALED.read_text(encoding="utf-8"))
    client = json.loads(CLIENT.read_text(encoding="utf-8"))
    live_actions = {
        (row["event"], row["action"])
        for row in client.get("hooks", [])
        if isinstance(row, dict)
    }
    live_by_action = {action for (_ev, action) in live_actions}

    rows = sealed.get("rows") or []
    assert rows, "sealed record must have rows"
    for row in rows:
        event = row["event"]
        action = row["action"]
        cover = _SEALED_COVERED_BY.get((event, action))
        assert cover is not None, (
            f"no parity mapping for sealed ({event!r}, {action!r}) — "
            "extend _SEALED_COVERED_BY when a new sealed row lands"
        )
        assert cover in live_by_action, (
            f"sealed ({event}, {action}) needs live action {cover!r}; "
            f"client-hooks has {sorted(live_by_action)}"
        )
        # Event must also appear under the covering action (or same event).
        matching = [
            (ev, act)
            for (ev, act) in live_actions
            if act == cover and (ev == event or cover != action)
        ]
        assert matching, (
            f"sealed event {event!r} not paired with covering action {cover!r}"
        )


def test_stop_live_action_is_before_stop_not_gate():
    """Stop is composite: client fires before_stop, which calls gate()."""
    client = json.loads(CLIENT.read_text(encoding="utf-8"))
    stop_actions = [
        row["action"] for row in client.get("hooks", []) if row.get("event") == "stop"
    ]
    assert stop_actions == ["before_stop"]
