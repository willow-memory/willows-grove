"""onescript_sign.py -- Grove's one way to reach the one script's signing rules.

The seal message, the public-only keyring rules, the HMAC seal and the pinned
Ed25519 verifier live once, by name, in the one script's ``onescript/sign.py``
(flatten-2 F14); Grove imports them through the one reach
(``onescript_reach.py``, the F6.5 bootstrap), as ``onescript_canon.py`` does
for the encodings. The operator: "Using the onescript at every path."

``sign().ed25519_verify(key, msg, sig)`` is the call. The reach is made on the
first call, not at import, so importing Grove never needs the one script.
Signing or verifying without it says ``unreachable`` (``Unreachable``, with the
reach's reason, naming ``ONESCRIPT_HOME``); it never falls back to a copy of
the check, because a verifier that is not the pinned one can disagree with the
peer's about a signature.

Key FILES stay where they are: ``u2u.identity`` still reads and writes the
0600 identity file; only the sign and verify steps come from here.
"""

from __future__ import annotations

import os
from pathlib import Path

from grove import onescript_reach

Unreachable = onescript_reach.Unreachable

_sign = None


def sign():
    """The one script's ``onescript.sign`` module."""
    global _sign
    if _sign is None:
        # the willow-bot the seat reads, as onescript_canon finds it
        got = os.environ.get("WILLOW_BOT_ROOT")
        home = Path(got).expanduser() / "one-script" if got else None
        _sign = onescript_reach.module("sign", home=home)
    return _sign
