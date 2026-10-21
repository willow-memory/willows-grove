"""onescript_canon.py -- Grove's one way to reach the canonical-bytes encodings.

The encodings live once, by name, in the one script's ``onescript/canon.py``
(flatten-2 F7); Grove imports them through the one reach
(``onescript_reach.py``, the F6.5 bootstrap). The operator: "Using the
onescript at every path."

``family("sorted_spaced_ascii")(obj)`` is the call. The reach is made on the
first call, not at import, so importing Grove never needs the one script.
Hashing or signing without it says ``unreachable`` (``Unreachable``, with the
reach's reason, naming ``ONESCRIPT_HOME``); it never falls back to a copy of
the ``json.dumps`` call, because a digest computed any other way would not be
the persisted one.
"""

from __future__ import annotations

import os
from pathlib import Path

from grove import onescript_reach

Unreachable = onescript_reach.Unreachable

_canon = None


def family(name: str):
    """One of ``onescript.canon``'s named encodings."""
    global _canon
    if _canon is None:
        # the willow-bot the seat reads, as seat_boxes finds it: $WILLOW_BOT_ROOT,
        # else the one reach's rule ($ONESCRIPT_HOME, else beside this repo)
        got = os.environ.get("WILLOW_BOT_ROOT")
        home = Path(got).expanduser() / "one-script" if got else None
        _canon = onescript_reach.module("canon", home=home)
    return _canon.get(name)
