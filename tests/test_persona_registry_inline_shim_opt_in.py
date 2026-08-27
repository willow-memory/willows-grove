# b17: WGRV1 ΔΣ=42
"""tests/test_persona_registry_inline_shim_opt_in.py — INVARIANTS.md §8 pin.

Fixture-based rendering (the inline `<script type="application/json">` shim
inside a `<grove-persona-registry>`) is opt-in — harness use only. A shim
present in the DOM MUST NOT shadow the live `/api/personas` endpoint unless
the element explicitly opts in via `data-fixture` (or `data-source="_inline"`).

This drives the real component module in a real browser (chromium via
Playwright) against a tiny static file server rooted at the repo, so the
module's own `fetch()` / customElements / shadow-DOM code paths run
unmodified — no jsdom, no mocked DOM.

Two cases (per the finding):
  (a) inline shim present, NO opt-in attribute  -> the element MUST fetch
      the live endpoint (mocked here to return a distinct marker payload)
      and getPersona() MUST reflect the live payload, not the shim.
  (b) inline shim present, `data-fixture` attribute present -> the element
      MUST use the inline shim payload and MUST NOT prefer the live fetch.

On the unfixed component (inline shim unconditionally wins), case (a) fails
because getPersona("willow") comes back with the shim's marker instead of
the live endpoint's marker.
"""
from __future__ import annotations

import functools
import http.server
import os
import threading
import unittest
from pathlib import Path

import pytest

# The Python playwright bindings are not in requirements.txt (the workflow
# installs the browser separately for the tests/e2e/*.spec.js suite). This
# Python-side test uses playwright as an integration harness; when the
# bindings are absent (CI, or a lean dev env), skip cleanly rather than
# raising ImportError at collection time. A follow-up will migrate this
# pin into a tests/e2e/*.spec.js spec so the Python-side dep goes away.
sync_playwright = pytest.importorskip(
    "playwright.sync_api",
    reason="playwright python bindings not installed",
).sync_playwright

# REPO_ROOT is overridable so this file can be pointed at a scratch checkout
# during fix verification; in the real tree it's two directories up from
# tests/.
_env_root = os.environ.get("GROVE_TEST_REPO_ROOT")
REPO_ROOT = Path(_env_root) if _env_root else Path(__file__).resolve().parent.parent

CHROMIUM_CANDIDATES = [
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
]


def _chromium_executable() -> str | None:
    for cand in CHROMIUM_CANDIDATES:
        if os.path.exists(cand):
            return cand
    return None


HARNESS_PATH = "/__inline_shim_opt_in_harness__.html"
HARNESS_HTML = """<!doctype html>
<html><head><meta charset="utf-8"></head>
<body>
<script type="module">
  import "/web/components/grove-persona-registry.js";
  window.__registryReady = true;
</script>
</body></html>
"""

LIVE_MARKER = "live-endpoint-payload"
SHIM_MARKER = "inline-shim-payload"

SHIM_JSON = (
    '{"schema":"fleet-personas/v1","personas":'
    '{"willow":{"marker":"' + SHIM_MARKER + '"}}}'
)

LIVE_JSON = (
    '{"schema":"fleet-personas/v1","personas":'
    '{"willow":{"marker":"' + LIVE_MARKER + '"}}}'
)

# Instantiates a <grove-persona-registry>, attaches the inline JSON shim
# child, optionally sets the opt-in attribute, appends it to the document
# (which fires connectedCallback -> _reload()), and resolves with
# getPersona("willow") once the registry settles.
CREATE_AND_WAIT_JS = """
async ({ optIn }) => {
  await customElements.whenDefined("grove-persona-registry");
  const el = document.createElement("grove-persona-registry");
  if (optIn === "data-fixture") {
    el.setAttribute("data-fixture", "");
  } else if (optIn === "data-source-inline") {
    el.setAttribute("data-source", "_inline");
  }
  const script = document.createElement("script");
  script.type = "application/json";
  script.textContent = window.__shimJson;
  el.appendChild(script);

  const settled = new Promise((resolve) => {
    el.addEventListener("registry-loaded", () => resolve(), { once: true });
    el.addEventListener("registry-unreachable", () => resolve(), { once: true });
  });

  document.body.appendChild(el);
  await settled;

  const row = el.getPersona("willow");
  return { row, state: el.state };
}
"""


class _StaticHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):  # noqa: N802 - stdlib override
        if self.path == HARNESS_PATH:
            body = HARNESS_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def log_message(self, *args, **kwargs):  # silence stdout spam
        pass


class _StaticServer:
    def __init__(self, root: Path) -> None:
        handler = functools.partial(_StaticHandler, directory=str(root))
        self._httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.port = self._httpd.server_address[1]
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)

    def __enter__(self) -> "_StaticServer":
        self._thread.start()
        return self

    def __exit__(self, *exc) -> None:
        self._httpd.shutdown()
        self._thread.join(timeout=3.0)

    def url(self, path: str) -> str:
        return f"http://127.0.0.1:{self.port}{path}"


@unittest.skipUnless(
    _chromium_executable(), "chromium not installed at expected path"
)
class PersonaRegistryInlineShimOptInTests(unittest.TestCase):
    """INVARIANTS.md §8 — inline shim is opt-in, never the default."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._pw = sync_playwright().start()
        cls._browser = cls._pw.chromium.launch(
            executable_path=_chromium_executable()
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls._browser.close()
        cls._pw.stop()

    def _run_case(self, optIn: str | None) -> dict:
        with _StaticServer(REPO_ROOT) as srv:
            page = self._browser.new_page()
            try:
                def _fulfill_live(route):
                    route.fulfill(
                        status=200,
                        content_type="application/json",
                        body=LIVE_JSON,
                    )

                page.route("**/api/personas", _fulfill_live)
                page.goto(srv.url(HARNESS_PATH))
                page.wait_for_function("window.__registryReady === true")
                page.evaluate("(json) => { window.__shimJson = json; }", SHIM_JSON)
                result = page.evaluate(CREATE_AND_WAIT_JS, {"optIn": optIn})
                return result
            finally:
                page.close()

    def test_default_no_opt_in_attr_uses_live_endpoint_not_shim(self) -> None:
        """(a) inline shim present, no opt-in attribute -> live fetch wins.

        This is the case that fails on the unfixed component: it always
        prefers the inline shim, so `row["marker"]` would come back as
        SHIM_MARKER instead of LIVE_MARKER.
        """
        result = self._run_case(optIn=None)
        self.assertEqual(result["state"], "populated")
        self.assertIsNotNone(result["row"])
        self.assertEqual(
            result["row"]["marker"],
            LIVE_MARKER,
            "default (no data-fixture / data-source=_inline) MUST fetch "
            "/api/personas, not the inline shim (INVARIANTS.md §8)",
        )

    def test_data_fixture_attr_opts_into_inline_shim(self) -> None:
        """(b) inline shim present + `data-fixture` attribute -> shim wins."""
        result = self._run_case(optIn="data-fixture")
        self.assertEqual(result["state"], "populated")
        self.assertIsNotNone(result["row"])
        self.assertEqual(result["row"]["marker"], SHIM_MARKER)


if __name__ == "__main__":
    unittest.main()
