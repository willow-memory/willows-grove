"""three_states.py -- the three states, from the one script (flatten-2 F9).

``POPULATED``, ``EMPTY``, ``UNREACHABLE`` and ``STATES`` are willow-bot's
``onescript/states.py``, reached only through ``grove/onescript_reach.py``;
Grove restates none of the words (the operator: "Using the onescript at every
path."). ``web/lib/states.js`` is generated from the same file
(``scripts/generate_states_js.py``). ``loading`` is UI-only, not a state (D-f).
With no one script beside, ``ABSENT`` holds the reach's answer and the state
names are an ImportError in the reach's words: the served page starts and says
``unreachable`` (``grove_serve``); the seat stops, as it did.
"""

from __future__ import annotations

import os
from pathlib import Path

from grove import onescript_reach


def _home():
    """The willow-bot the seat reads: ``$WILLOW_BOT_ROOT``, else the one
    reach's rule (``$ONESCRIPT_HOME``, else beside this repo; flatten-2 F6.5)."""
    got = os.environ.get("WILLOW_BOT_ROOT")
    return Path(got).expanduser() / "one-script" if got else None


def _one_script_states():
    """willow-bot's ``onescript/states.py`` itself (``scripts/generate_states_js.py``
    reads it), or an ImportError in the reach's words when it isn't beside."""
    try:
        return onescript_reach.module("states", home=_home())
    except onescript_reach.Unreachable as e:
        raise ImportError(f"unreachable: {e}") from e


_NAMES = ("STATES", "POPULATED", "EMPTY", "UNREACHABLE", "checked")

try:
    _states = onescript_reach.module("states", home=_home())
except onescript_reach.Unreachable as e:
    _states, _why = None, str(e)

if _states is not None:
    #: None while the one script is in reach.
    ABSENT = None
    STATES = _states.STATES
    POPULATED, EMPTY = _states.POPULATED, _states.EMPTY
    UNREACHABLE = _states.UNREACHABLE
    checked = _states.checked
else:
    # The operator, 2026-10-21: "start and say unreachable". The page still
    # starts with no one script beside it, and says so in the reach's own
    # words: ``ABSENT`` is the reach's answer (its ``state`` word comes from
    # ``onescript_reach``, the one script's byte-copied template), so Grove
    # still restates nothing. Asking for a state name here is an ImportError
    # in the reach's words, as before, so the seat stops where it did.
    _r = onescript_reach.reach(home=_home(), law=False)
    ABSENT = {"state": _r["state"], "reason": _r.get("why") or _why}

    def __getattr__(name):
        if name in _NAMES:
            raise ImportError(f"unreachable: {_why}")
        raise AttributeError(name)
