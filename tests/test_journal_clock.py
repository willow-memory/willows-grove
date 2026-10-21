"""The journal writer stamps from the one script's clock (flatten-2 F8; the
operator: "Using the onescript at every path."). With ``ONESCRIPT_NOW`` pinned,
``_now_iso`` is the pinned instant in the named ``seconds_z`` format
(``2026-10-20T12:00:00Z``), the bytes ``isoformat(timespec="seconds")`` with
``Z`` wrote before. With no one script reachable the writer says
``Unreachable`` (the route answers 503), naming ``ONESCRIPT_HOME``.

Locally, with no willow-bot beside, the first skips and says so; in CI (``CI``
is set) it fails instead, because the CI checks willow-bot out for this.
"""

import os
from pathlib import Path

import pytest

from grove import journal_writer, onescript_reach
from grove.errors import Unreachable


def test_now_iso_is_the_pinned_instant_in_seconds_z(monkeypatch):
    home = onescript_reach.where()["onescript"]
    if home is None or not (Path(home) / "onescript" / "clock.py").is_file():
        if os.environ.get("CI"):
            pytest.fail(f"CI has no willow-bot with a clock beside: {home}")
        pytest.skip(f"no willow-bot beside (set ONESCRIPT_HOME): {home}")
    monkeypatch.setenv("ONESCRIPT_NOW", "2026-10-20T12:00:00.123456Z")
    assert journal_writer._now_iso() == "2026-10-20T12:00:00Z"


def test_no_one_script_is_unreachable_with_why(monkeypatch, tmp_path):
    monkeypatch.setenv("ONESCRIPT_HOME", str(tmp_path / "nowhere"))
    with pytest.raises(Unreachable, match="ONESCRIPT_HOME"):
        journal_writer._now_iso()
