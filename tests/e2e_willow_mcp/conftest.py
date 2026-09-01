# b17: WGRV1 ΔΣ=42
"""Pytest fixtures for the willow-mcp mock e2e suite.

Cites ``docs/INVARIANTS.md`` §1 (three-state contract) and §10 (CI proves
the invariants). The ``mock_mcp_server`` fixture spins up
``mock_willow_mcp.build_app`` on an ephemeral loopback port in a
background thread, waits for /health, and hands tests a URL. Every
test also gets ``WILLOW_MCP_URL`` set on the environment so
``grove/journal_writer.py`` and ``grove/journal_reader.py`` reach the
mock over MCP Streamable HTTP at ``{WILLOW_MCP_URL}/mcp`` — the same
transport willow-mcp ``--serve`` exposes.

What this suite does and does not prove
---------------------------------------

The WRITE and READ halves are both real MCP tools: ``kb_journal`` and
``kb_journal_read`` exist in willow-mcp (landed 2026-09-01, issue #16).
A green read-back here is evidence the C11 seam speaks MCP end to end;
the mock pins that protocol for CI runs that deliberately omit upstream.
"""
from __future__ import annotations

import contextlib
import socket
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

# Make sure the repo root is importable so tests can `from grove import ...`
# regardless of how pytest was invoked (rootdir / pytest.ini / bare).
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# The mock lives next to conftest.py — same directory, not a package on
# the classic sys.path. Add the directory so `import mock_willow_mcp`
# resolves without a __init__.py.
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))


def _free_port() -> int:
    """Ask the kernel for an unused TCP port on localhost."""
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_until_up(url: str, timeout: float = 5.0) -> None:
    """Poll a URL until it returns 200, or raise after ``timeout``."""
    deadline = time.monotonic() + timeout
    last_err: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=0.5) as resp:
                if resp.status == 200:
                    return
        except (urllib.error.URLError, ConnectionError, OSError) as err:
            last_err = err
            time.sleep(0.05)
    raise RuntimeError(f"mock willow-mcp did not come up at {url}: {last_err!r}")


class _MockServer:
    """Handle for the running mock — carries URL and the shared store."""

    def __init__(self, url: str, server, thread, app) -> None:
        self.url = url
        self._server = server
        self._thread = thread
        self._app = app

    @property
    def store(self):
        """The mock's in-memory atom store — for direct inspection in tests."""
        from mock_willow_mcp import get_store  # type: ignore[import-not-found]

        return get_store()

    def post(self, path: str) -> None:
        """Fire-and-forget POST for /kill /restore /reset — tests only."""
        req = urllib.request.Request(self.url + path, data=b"", method="POST")
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            resp.read()

    def kill(self) -> None:
        """Convenience — flip the mock's kill flag."""
        self.post("/kill")

    def restore(self) -> None:
        """Convenience — clear the mock's kill flag."""
        self.post("/restore")

    def reset(self) -> None:
        """Convenience — wipe stored atoms and clear the kill flag."""
        self.post("/reset")

    def shutdown(self) -> None:
        """Ask uvicorn to stop; join the thread with a bounded timeout."""
        if self._server is not None:
            self._server.should_exit = True
        if self._thread is not None:
            self._thread.join(timeout=3.0)


@pytest.fixture(scope="session")
def mock_mcp_server():
    """Session-scoped mock willow-mcp on an ephemeral loopback port.

    One process-lifetime server; tests reset store state between runs
    via :meth:`_MockServer.reset` in the per-test fixture below.
    """
    import uvicorn
    from mock_willow_mcp import build_app  # type: ignore[import-not-found]

    app = build_app()
    port = _free_port()
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=port,
        log_level="error",
        access_log=False,
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{port}"
    _wait_until_up(url + "/health")
    handle = _MockServer(url=url, server=server, thread=thread, app=app)
    try:
        yield handle
    finally:
        handle.shutdown()


@pytest.fixture()
def mock_mcp(mock_mcp_server, monkeypatch):
    """Per-test wrapper: fresh store + WILLOW_MCP_URL set for MCP HTTP.

    Also resets ``journal_writer`` / ``journal_reader`` log-once latches
    and the willow-mcp client singleton so env changes take effect.
    """
    from grove import journal_reader, journal_writer
    from grove import willow_mcp_client

    # Reset atoms and kill flag before every test.
    mock_mcp_server.reset()

    # Point Grove's MCP HTTP transport at the mock base URL.
    monkeypatch.setenv("WILLOW_MCP_URL", mock_mcp_server.url)
    willow_mcp_client._reset_client_for_tests()

    # Reset log-once latches so ``self.assertLogs`` sees fresh emissions.
    journal_writer._reset_log_once_for_tests()
    journal_reader._reset_log_once_for_tests()

    return mock_mcp_server


__all__ = ["mock_mcp", "mock_mcp_server"]
