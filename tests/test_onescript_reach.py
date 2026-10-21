"""The one reach's bootstrap copy in Grove (flatten-2 F6.5): it is willow-bot's
template byte for byte, Grove's two former shims (``seat_boxes``,
``seat_cli.load_bot``) say the reach's words, and an installed copy with no
checkout and no env names ``ONESCRIPT_HOME``.

The template is ``onescript/reach_bootstrap.py`` in the one script, found the
way the copy finds it. Locally, with no willow-bot beside, the parity test
skips and says so; in CI (``CI`` is set) it fails instead, because the CI
checks willow-bot out for exactly this.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from grove import onescript_reach, seat_cli

COPY = Path(onescript_reach.__file__).resolve()


def _bot_home():
    got = os.environ.get("WILLOW_BOT_ROOT")
    return Path(got) / "one-script" if got else onescript_reach.where()["onescript"]


def _beside_or_say_why(path):
    if path is not None and path.is_file():
        return
    if os.environ.get("CI"):
        pytest.fail(f"CI has no willow-bot to hold the copy to: {path}")
    pytest.skip(f"no willow-bot beside (set WILLOW_BOT_ROOT): {path}")


def test_the_copy_is_the_template_byte_for_byte():
    home = _bot_home()
    template = home / "onescript" / "reach_bootstrap.py" if home else None
    _beside_or_say_why(template)
    assert COPY.read_bytes() == template.read_bytes()


def test_it_reaches_the_one_script_when_beside():
    home = _bot_home()
    _beside_or_say_why(home / "onescript" / "reach.py" if home else None)
    assert onescript_reach.module("states", home=home).STATES[-1] == "unreachable"


def test_it_says_unreachable_when_not(tmp_path):
    got = onescript_reach.reach(home=tmp_path / "nowhere")
    assert got["state"] == "unreachable"
    assert "ONESCRIPT_HOME" in got["why"] and "nowhere" in got["why"]
    with pytest.raises(onescript_reach.Unreachable):
        onescript_reach.module("states", home=tmp_path / "nowhere")


def test_load_bot_says_the_reaches_words(tmp_path):
    with pytest.raises(seat_cli.SeatUnavailable) as e:
        seat_cli.load_bot(tmp_path)
    assert (
        str(e.value)
        == "unreachable: " + onescript_reach.reach(home=tmp_path / "one-script")["why"]
    )


def test_installed_with_no_checkout_and_no_env_it_names_the_variable(tmp_path):
    lone = tmp_path / "onescript_reach.py"
    lone.write_bytes(COPY.read_bytes())
    code = (
        "import onescript_reach as r; got = r.reach(); "
        "assert got['state'] == 'unreachable', got; print(got['why'])"
    )
    env = {
        k: v
        for k, v in os.environ.items()
        if k not in ("ONESCRIPT_HOME", "ONESCRIPT_GROVE")
    }
    out = subprocess.run(
        [sys.executable, "-c", code],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )
    assert out.returncode == 0, out.stderr
    assert "ONESCRIPT_HOME" in out.stdout
