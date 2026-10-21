# b17: WGRV1 ΔΣ=42
"""tests/test_three_states.py — ``grove/three_states.py`` itself, both ways (flatten-2 F9).

``tests/test_grove_serve_no_one_script.py`` drives the whole page with no one
script; this imports ``grove.three_states`` directly. Present: the state names
are bound and are the one script's own constants. Absent (the operator,
2026-10-21: "start and say unreachable"): the module still imports, ``ABSENT``
holds the reach's ``unreachable`` with why, and asking for a state name raises
ImportError in the reach's words. Each runs in a subprocess so one answer can't
leak into the other through ``sys.modules``.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_PROBE = r"""
import json, sys
sys.path.insert(0, sys.argv[1])
from grove import three_states as ts
out = {"absent": ts.ABSENT}
for name in ("STATES", "POPULATED", "EMPTY", "UNREACHABLE", "checked"):
    try:
        v = getattr(ts, name)
        out[name] = list(v) if name == "STATES" else (v("populated") if name == "checked" else v)
    except ImportError as e:
        out[name] = ["ImportError", str(e)]
try:
    ts.NOT_A_STATE
except AttributeError:
    out["other"] = "AttributeError"
except ImportError:
    out["other"] = "ImportError"
print(json.dumps(out))
"""


def _probe(home: str) -> dict:
    env = {k: v for k, v in os.environ.items() if k not in ("WILLOW_BOT_ROOT", "PYTHONPATH")}
    env["ONESCRIPT_HOME"] = home
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    r = subprocess.run(
        [sys.executable, "-c", _PROBE, ROOT],
        capture_output=True,
        text=True,
        env=env,
        cwd=ROOT,
        timeout=120,
        check=False,
    )
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


class TestThreeStates(unittest.TestCase):
    def test_present_the_names_are_bound_and_absent_is_none(self):
        home = os.environ.get("ONESCRIPT_HOME") or os.path.join(
            os.path.dirname(ROOT), "willow-bot", "one-script"
        )
        if not home or not os.path.isfile(os.path.join(home, "onescript", "states.py")):
            self.fail(f"the one script is not beside (set ONESCRIPT_HOME): {home!r}")
        out = _probe(home)
        self.assertIsNone(out["absent"])
        self.assertEqual(out["STATES"], ["populated", "empty", "unreachable"])
        self.assertEqual(
            [out["POPULATED"], out["EMPTY"], out["UNREACHABLE"]],
            ["populated", "empty", "unreachable"],
        )
        self.assertEqual(out["checked"], "populated")
        self.assertEqual(out["other"], "AttributeError")

    def test_absent_holds_the_reachs_unreachable_and_the_names_raise_importerror(self):
        with tempfile.TemporaryDirectory() as empty:
            out = _probe(os.path.join(empty, "no-one-script"))
        self.assertEqual(out["absent"]["state"], "unreachable")
        self.assertIn("ONESCRIPT_HOME", out["absent"]["reason"])
        for name in ("STATES", "POPULATED", "EMPTY", "UNREACHABLE", "checked"):
            kind, why = out[name]
            self.assertEqual(kind, "ImportError", name)
            self.assertIn("unreachable", why)
            self.assertIn("ONESCRIPT_HOME", why)
        self.assertEqual(out["other"], "AttributeError")


if __name__ == "__main__":
    unittest.main()
