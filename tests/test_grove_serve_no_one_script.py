# b17: WGRV1 ΔΣ=42
"""tests/test_grove_serve_no_one_script.py — the page starts without the one script.

The operator, 2026-10-21: "start and say unreachable". With no one script
beside (``ONESCRIPT_HOME`` names an empty place, ``WILLOW_BOT_ROOT`` unset),
``grove_serve`` still imports and builds its app; ``/`` serves the page, every
reader answers the reach's own ``unreachable`` with why (503), ``/health`` says
``ok: false``, and the events socket says it once and closes. Run in a
subprocess so the missing one script can't leak into other tests' imports.
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
from starlette.testclient import TestClient
import grove_serve
c = TestClient(grove_serve.build_app())
out = {
    "index": c.get("/").status_code,
    "personas": [c.get("/api/personas").status_code, c.get("/api/personas").json()],
    "journal_post": c.post("/api/journal", json={}).status_code,
    "health": c.get("/health").json(),
}
with c.websocket_connect("/events/willow") as ws:
    out["events"] = ws.receive_json()
print(json.dumps(out))
"""


class TestNoOneScript(unittest.TestCase):
    def test_the_page_starts_and_says_unreachable(self):
        with tempfile.TemporaryDirectory() as empty:
            env = {k: v for k, v in os.environ.items() if k != "WILLOW_BOT_ROOT"}
            env["ONESCRIPT_HOME"] = os.path.join(empty, "no-one-script")
            r = subprocess.run(
                [sys.executable, "-c", _PROBE, ROOT],
                capture_output=True,
                text=True,
                env=env,
                cwd=ROOT,
                timeout=120,
            )
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertEqual(out["index"], 200)
        status, body = out["personas"]
        self.assertEqual(status, 503)
        self.assertEqual(body["state"], "unreachable")
        self.assertIn("ONESCRIPT_HOME", body["reason"])
        self.assertEqual(out["journal_post"], 503)
        self.assertIs(out["health"]["ok"], False)
        self.assertEqual(out["health"]["one_script"], body)
        self.assertEqual(out["events"], body)


if __name__ == "__main__":
    unittest.main()
