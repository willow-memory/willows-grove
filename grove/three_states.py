"""three_states.py -- the three states, from the one script (flatten-2 F9).

``POPULATED``, ``EMPTY``, ``UNREACHABLE`` and ``STATES`` are willow-bot's
``onescript/states.py``, reached only through ``grove/onescript_reach.py``;
Grove restates none of the words (the operator: "Using the onescript at every
path."). ``web/lib/states.js`` is generated from the same file
(``scripts/generate_states_js.py``). ``loading`` is UI-only, not a state (D-f).
With no one script beside, import stops with the reach's words: a reader that
cannot name its states has no honest answer to give.
"""

from __future__ import annotations

import os
from pathlib import Path

from grove import onescript_reach


def _one_script_states():
    """The three states, once: willow-bot's ``onescript/states.py`` (flatten
    F5, F-18; the operator: "2 a"), from the willow-bot the seat reads
    (``$WILLOW_BOT_ROOT``, else the one reach's rule: ``$ONESCRIPT_HOME``,
    else beside this repo; flatten-2 F6.5). With none beside, the seat stops
    at import and says where it looked, in the reach's words."""
    got = os.environ.get("WILLOW_BOT_ROOT")
    home = Path(got).expanduser() / "one-script" if got else None
    try:
        return onescript_reach.module("states", home=home)
    except onescript_reach.Unreachable as e:
        raise ImportError(f"unreachable: {e}") from e


_states = _one_script_states()


_states = _one_script_states()
STATES = _states.STATES
POPULATED, EMPTY, UNREACHABLE = _states.POPULATED, _states.EMPTY, _states.UNREACHABLE
checked = _states.checked
