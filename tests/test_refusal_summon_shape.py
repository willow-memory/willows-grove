# b17: WGRV1 ΔΣ=42
"""tests/test_refusal_summon_shape.py — refusal-summon boot module contract.

Executes ``web/boot/refusal-summon-boot.js`` in a Node subprocess against
minimal ``window`` / ``document`` / ``CustomEvent`` / ``fetch`` shims and
verifies the *behavior* the served page depends on (INVARIANTS.md §1 +
§8):

  * The boot module assigns ``window.groveNestorAsk``.
  * ``groveNestorAsk(claim)`` POSTs ``{"claim": ...}`` as JSON to
    ``/api/nestor/decide`` (the D11 endpoint).
  * A 503 response with ``state === "unreachable"`` dispatches exactly
    one ``nestor-refusal`` window ``CustomEvent`` whose ``detail`` is
    tagged ``mode: "unreachable"``. The 503 is NEVER silently swallowed
    — a comment or dead-code path carrying the right substrings can no
    longer satisfy this assertion.
  * A ``verdict === "refused"`` response dispatches exactly one
    ``nestor-refusal`` event whose ``detail`` is the verbatim
    ``refusal`` payload (V5 discipline — the boot does not reshape it).
  * A non-refused / non-unreachable verdict dispatches no
    ``nestor-refusal`` event.

If Node is not present at pytest time the suite is skipped cleanly.

Prior versions of this file slurped the JS as text and asserted static
regexes against it — the JS was never executed and toothless. This
rewrite is the Loki-audit regression (Grove v0.9 PR 12, finding M16).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOT_PATH = os.path.join(ROOT, "web", "boot", "refusal-summon-boot.js")


_HARNESS_JS = r"""// b17: WGRV1 ΔΣ=42
// Node harness for tests/test_refusal_summon_shape.py.
// Sets up window/document/CustomEvent/fetch shims, imports the boot
// module by absolute file:// URL, invokes its exported ask helper, and
// prints a single JSON line describing the dispatched events, the
// helper's return value, the captured fetch call, and whether the
// module assigned window.groveNestorAsk.
const scenario = process.argv[2];
const bootUrl = process.argv[3];

const events = [];
const win = {
  __groveRefusalBooted: false,
  addEventListener(name, handler) {
    this._listeners = this._listeners || {};
    (this._listeners[name] = this._listeners[name] || []).push(handler);
  },
  dispatchEvent(ev) {
    events.push({ type: ev.type, detail: ev.detail });
    return true;
  },
};
class FakeCustomEvent {
  constructor(type, init) {
    this.type = type;
    this.detail = (init && init.detail) || null;
  }
}
globalThis.window = win;
globalThis.document = {
  getElementById() { return null; },
  createElement() { return {}; },
  get body() { return null; },
};
globalThis.CustomEvent = FakeCustomEvent;

let captured = null;
globalThis.fetch = async (url, opts) => {
  captured = {
    url: url,
    method: (opts && opts.method) || null,
    body: (opts && opts.body) || null,
  };
  if (scenario === "unreachable") {
    return {
      ok: false,
      status: 503,
      async json() { return { state: "unreachable", reason: "nestor L4 down" }; },
    };
  }
  if (scenario === "refused") {
    return {
      ok: true,
      status: 200,
      async json() {
        return {
          verdict: "refused",
          refusal: { persona: "nestor", act: "seal", body: "no" },
        };
      },
    };
  }
  if (scenario === "populated") {
    return {
      ok: true,
      status: 200,
      async json() { return { verdict: "allowed" }; },
    };
  }
  throw new Error("unknown scenario: " + scenario);
};

const mod = await import(bootUrl);
if (typeof mod.__askForTest !== "function") {
  throw new Error("boot module does not export __askForTest");
}
const result = await mod.__askForTest("test claim");

process.stdout.write(JSON.stringify({
  events: events,
  result: result,
  fetch: captured,
  askAssigned: typeof win.groveNestorAsk === "function",
}) + "\n");
"""


def _node_bin() -> str | None:
    return shutil.which("node")


def _run_harness(scenario: str) -> dict:
    node = _node_bin()
    if node is None:
        raise unittest.SkipTest("node not available at pytest time")
    if not os.path.isfile(BOOT_PATH):
        raise AssertionError(f"boot module missing at {BOOT_PATH}")
    with tempfile.TemporaryDirectory() as tmp:
        harness_path = os.path.join(tmp, "harness.mjs")
        with open(harness_path, "w", encoding="utf-8") as fh:
            fh.write(_HARNESS_JS)
        boot_url = "file://" + BOOT_PATH
        proc = subprocess.run(
            [node, harness_path, scenario, boot_url],
            capture_output=True,
            text=True,
            timeout=30,
        )
    if proc.returncode != 0:
        raise AssertionError(
            "node harness failed "
            f"(scenario={scenario}, rc={proc.returncode}): "
            f"stdout={proc.stdout!r} stderr={proc.stderr!r}"
        )
    # The harness prints exactly one JSON line on stdout; Node module-
    # type warnings go to stderr. Take the last non-empty stdout line.
    lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
    if not lines:
        raise AssertionError(
            f"node harness produced no stdout (stderr={proc.stderr!r})"
        )
    try:
        return json.loads(lines[-1])
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"node harness stdout was not JSON: {lines[-1]!r} ({exc})"
        )


class RefusalSummonBehaviorTests(unittest.TestCase):
    """Exercise the boot module — no static-regex slurping."""

    def test_file_exists(self) -> None:
        self.assertTrue(
            os.path.isfile(BOOT_PATH),
            f"expected refusal-summon-boot module at {BOOT_PATH}",
        )

    def test_boot_assigns_grove_nestor_ask_on_window(self) -> None:
        out = _run_harness("populated")
        self.assertTrue(
            out["askAssigned"],
            "boot module must assign window.groveNestorAsk",
        )

    def test_fetch_hits_decide_endpoint_via_post_with_claim(self) -> None:
        out = _run_harness("populated")
        f = out["fetch"]
        self.assertEqual(
            f["url"],
            "/api/nestor/decide",
            "boot module must POST to /api/nestor/decide",
        )
        self.assertEqual(
            f["method"],
            "POST",
            "the /api/nestor/decide call must use method:POST",
        )
        body = json.loads(f["body"])
        self.assertEqual(
            body,
            {"claim": "test claim"},
            "the fetch body must carry the caller's claim under a `claim` key",
        )

    def test_unreachable_dispatches_nestor_refusal_with_mode_unreachable(self) -> None:
        # INVARIANTS.md §1: a 503 with state="unreachable" is a distinct
        # summon path — the 503 must not be silently swallowed and the
        # event must be tagged so the chip renders the subdued path.
        out = _run_harness("unreachable")
        refusals = [e for e in out["events"] if e["type"] == "nestor-refusal"]
        self.assertEqual(
            len(refusals),
            1,
            "expected exactly one nestor-refusal event on 503/unreachable "
            f"path, got: {out['events']!r}",
        )
        detail = refusals[0]["detail"]
        self.assertIsInstance(
            detail,
            dict,
            "the unreachable event detail must be an object payload",
        )
        self.assertEqual(
            detail.get("mode"),
            "unreachable",
            "the 503/unreachable branch must tag the CustomEvent detail "
            "with mode:'unreachable' (INVARIANTS §1)",
        )
        # The return value carries the raw endpoint body — the 503 is
        # surfaced, never collapsed into a bare {} or null.
        self.assertEqual(
            out["result"],
            {"state": "unreachable", "reason": "nestor L4 down"},
            "groveNestorAsk must return the raw unreachable body — the "
            "503 must not be swallowed",
        )

    def test_refused_dispatches_verbatim_refusal_payload(self) -> None:
        # V5: the refusal payload rides from fetch → CustomEvent → chip
        # unchanged. No paraphrase on our side.
        out = _run_harness("refused")
        refusals = [e for e in out["events"] if e["type"] == "nestor-refusal"]
        self.assertEqual(
            len(refusals),
            1,
            "expected exactly one nestor-refusal event on verdict=refused "
            f"path, got: {out['events']!r}",
        )
        self.assertEqual(
            refusals[0]["detail"],
            {"persona": "nestor", "act": "seal", "body": "no"},
            "the refused-branch event detail must be the verbatim "
            "refusal payload (V5 — no reshape)",
        )

    def test_populated_verdict_dispatches_no_event(self) -> None:
        # A non-refused, non-unreachable verdict is a quiet allow — the
        # chip must not summon.
        out = _run_harness("populated")
        refusals = [e for e in out["events"] if e["type"] == "nestor-refusal"]
        self.assertEqual(
            refusals,
            [],
            "no nestor-refusal event should fire on a non-refused "
            f"verdict, got: {out['events']!r}",
        )


if __name__ == "__main__":
    unittest.main()
