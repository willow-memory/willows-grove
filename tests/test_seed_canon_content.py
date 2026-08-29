# b17: WGRV1 ΔΣ=42
"""tests/test_seed_canon_content.py — pins /seed/{1..6} to the real canon.

INVARIANTS.md §9 ("Seed reads real canon"): the ``/seed/`` route renders
content from the seed's ``canon/`` dir when the probe path resolves. The
canon now lives in this repo at ``governance/seed/canon/`` (relocated
from the archived charter repository per ``governance/README.md``), so
it is the in-repo fallback rung of ``grove.seed_reader``'s probe order
and resolves with no ``$WILLOW_HOME`` set at all. This suite boots
``grove_serve`` on an ephemeral loopback port and asserts each of the
six movement pages renders content derived verbatim from the
corresponding ``NN-*.md`` source file. Titles are read from the source
file's first ``# `` heading — never hardcoded — so a rename in the
canon reaches this test through the file, not through a lie in the
assertion.

Stdlib only. Restores every mutated env var in ``tearDown`` so the rest
of the suite is unaffected.
"""
from __future__ import annotations

import contextlib
import os
import re
import socket
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


from grove import seed_reader  # noqa: E402

CANON_ROOT = seed_reader._IN_REPO_SEED_PATH / "canon"
CANON_FILES = (
    "00-the-covenant.md",
    "01-be-the-other.md",
    "02-the-discipline.md",
    "03-the-person.md",
    "04-the-language.md",
    "05-the-world.md",
)


def _free_port() -> int:
    with contextlib.closing(
        socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_until_up(url: str, timeout: float = 5.0) -> None:
    deadline = time.monotonic() + timeout
    last_err: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=0.5) as resp:
                if resp.status == 200:
                    return
        except (urllib.error.URLError, ConnectionError, OSError) as e:
            last_err = e
            time.sleep(0.05)
    raise RuntimeError(f"grove_serve did not come up at {url}: {last_err!r}")


class _ServerHarness:
    """Boot uvicorn on an ephemeral port with `env` merged into os.environ.

    The harness stores/restores every touched env var so the process
    lands back where it started when the ``with`` block exits — the
    seed reader consults ``WILLOW_HOME`` at every ``load_movements()``,
    so leaking it would poison other tests.
    """

    def __init__(self, env: dict[str, str] | None = None) -> None:
        self.env = dict(env or {})
        self.port = _free_port()
        self.host = "127.0.0.1"
        self._server = None
        self._thread: threading.Thread | None = None
        self._saved: dict[str, str | None] = {}

    def __enter__(self) -> "_ServerHarness":
        for k, v in self.env.items():
            self._saved[k] = os.environ.get(k)
            os.environ[k] = v

        # Force a fresh seed_reader state so its log-once flag doesn't
        # eat this test's INFO line if a prior test emitted one.
        import importlib

        from grove import seed_reader

        importlib.reload(seed_reader)

        import uvicorn

        import grove_serve

        importlib.reload(grove_serve)

        config = uvicorn.Config(
            grove_serve.build_app(),
            host=self.host,
            port=self.port,
            log_level="error",
            access_log=False,
        )
        self._server = uvicorn.Server(config)
        self._thread = threading.Thread(target=self._server.run, daemon=True)
        self._thread.start()
        _wait_until_up(f"http://{self.host}:{self.port}/health")
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._server is not None:
            self._server.should_exit = True
        if self._thread is not None:
            self._thread.join(timeout=3.0)
        for k, v in self._saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def url(self, path: str) -> str:
        return f"http://{self.host}:{self.port}{path}"

    def get(self, path: str) -> tuple[int, str]:
        with urllib.request.urlopen(self.url(path), timeout=3.0) as resp:
            return resp.status, resp.read().decode("utf-8")


def _h1_from_source(canon_path: Path) -> str:
    """Return the first ``# `` heading of a canon markdown file.

    Never hardcoded — read directly from the source. This is what the
    task's discipline pins: the test's expected title comes from the
    file, so a rename in the canon reaches the test through the tree.
    """
    text = canon_path.read_text(encoding="utf-8")
    for line in text.splitlines():
        m = re.match(r"^#\s+(.+?)\s*#*\s*$", line.strip())
        if m:
            return m.group(1).strip()
    raise AssertionError(f"no '# ' heading in {canon_path}")


class SeedCanonContentIntegrationTests(unittest.TestCase):
    """/seed/{1..6} render real canon content — one test per movement."""

    def setUp(self) -> None:
        if not CANON_ROOT.is_dir():
            self.skipTest(
                f"real canon not present at {CANON_ROOT}; the in-repo canon"
                " should always be present after the seed relocation"
            )
        for name in CANON_FILES:
            self.assertTrue(
                (CANON_ROOT / name).is_file(),
                f"expected canon file {name} in {CANON_ROOT}",
            )

    def test_seed_index_lists_all_six_movements(self) -> None:
        # No $WILLOW_HOME needed — the in-repo canon at governance/seed/
        # is the reliable fallback rung.
        env: dict[str, str] = {}
        with _ServerHarness(env=env) as srv:
            status, body = srv.get("/seed/")
        self.assertEqual(status, 200)
        # Six chapter links.
        for n in range(1, 7):
            self.assertIn(f'href="/seed/{n}"', body)

    def _assert_movement_matches_source(
        self, n: int, canon_name: str
    ) -> None:
        canon_path = CANON_ROOT / canon_name
        expected_h1 = _h1_from_source(canon_path)  # e.g. "0 · The Covenant"
        # Also the "title half" — the piece after any leading "N · " —
        # so the assertion is robust to whether the reader keeps the
        # number prefix or drops it. Both halves have to appear.
        m = re.match(r"^\s*\d+\s*·\s*(.+?)\s*$", expected_h1)
        title_only = m.group(1) if m else expected_h1

        # No $WILLOW_HOME needed — the in-repo canon at governance/seed/
        # is the reliable fallback rung.
        env: dict[str, str] = {}
        with _ServerHarness(env=env) as srv:
            status, body = srv.get(f"/seed/{n}")

        self.assertEqual(
            status, 200, f"/seed/{n} did not return 200 for {canon_name}"
        )
        # The rendered body carries the source file's H1 verbatim (the
        # markdown renderer emits it as <h1>0 · The Covenant</h1> etc.).
        self.assertIn(
            expected_h1,
            body,
            f"/seed/{n} missing source H1 {expected_h1!r} from {canon_name}",
        )
        # And the title-only fragment is present too, so a reader that
        # strips the numeric prefix still passes.
        self.assertIn(title_only, body)
        # Sanity: prev/next nav references the neighbors.
        if n > 1:
            self.assertIn(f'href="/seed/{n - 1}"', body)
        if n < 6:
            self.assertIn(f'href="/seed/{n + 1}"', body)

    def test_seed_1_matches_the_covenant(self) -> None:
        self._assert_movement_matches_source(1, "00-the-covenant.md")

    def test_seed_2_matches_be_the_other(self) -> None:
        self._assert_movement_matches_source(2, "01-be-the-other.md")

    def test_seed_3_matches_the_discipline(self) -> None:
        self._assert_movement_matches_source(3, "02-the-discipline.md")

    def test_seed_4_matches_the_person(self) -> None:
        self._assert_movement_matches_source(4, "03-the-person.md")

    def test_seed_5_matches_the_language(self) -> None:
        self._assert_movement_matches_source(5, "04-the-language.md")

    def test_seed_6_matches_the_world(self) -> None:
        self._assert_movement_matches_source(6, "05-the-world.md")


class SeedHtmlEscapingIntegrationTest(unittest.TestCase):
    """A synthetic canon dir with <, >, & in the body must render escaped.

    Uses a temp WILLOW_HOME so the real canon on the box isn't touched.
    """

    def test_lt_gt_amp_are_escaped_in_rendered_body(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            home = root / "home"
            seed = home / "seed"
            canon = seed / "canon"
            canon.mkdir(parents=True)
            # Synthetic six-movement set — movement 3 carries the
            # dangerous characters so we can pin escaping specifically.
            payload = "syn <marker> & test <script>alert(1)</script> end"
            files = [
                ("00-the-covenant.md",   "# T0\n\nbody0"),
                ("01-be-the-other.md",   "# T1\n\nbody1"),
                ("02-the-discipline.md", f"# T2\n\n{payload}"),
                ("03-the-person.md",     "# T3\n\nbody3"),
                ("04-the-language.md",   "# T4\n\nbody4"),
                ("05-the-world.md",      "# T5\n\nbody5"),
            ]
            for name, body in files:
                (canon / name).write_text(body, encoding="utf-8")

            env = {"WILLOW_HOME": str(home)}
            with _ServerHarness(env=env) as srv:
                status, body_html = srv.get("/seed/3")

        self.assertEqual(status, 200)
        # Escaped forms present.
        self.assertIn("&lt;marker&gt;", body_html)
        self.assertIn("&amp;", body_html)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", body_html)
        # And the raw script tag is NOT present — the load-bearing check.
        self.assertNotIn("<script>alert(1)</script>", body_html)
        self.assertNotIn("<marker>", body_html)


if __name__ == "__main__":
    unittest.main()
