"""Host/Origin allowlisting for the Streamable HTTP transport (G-REBIND-01).

`_transport_security()` used to return
`TransportSecuritySettings(enable_dns_rebinding_protection=False)` whenever
`GROVE_MCP_URL` was https:// — which is precisely the tunnelled deployment this
server is built to run in. So in the configuration that actually ships, there
was no host check and no origin check, and the only thing standing between a
stranger and the server was knowledge of the tunnel URL.

The stated reason was real: behind a tunnel the edge may forward
`Host: 127.0.0.1:8765` rather than the public hostname. That is an argument for
allowlisting both, which is what these pin.

The property under test, in one line: **there is no configuration in which
protection is off.**
"""
from __future__ import annotations

import importlib

import pytest

mcp_local = pytest.importorskip("grove.mcp_local")


def _settings(monkeypatch, url):
    """Reload the module under a given GROVE_MCP_URL — `_BASE_URL` is resolved
    at import time, so setting the env alone would not reach it."""
    if url is None:
        monkeypatch.delenv("GROVE_MCP_URL", raising=False)
    else:
        monkeypatch.setenv("GROVE_MCP_URL", url)
    m = importlib.reload(mcp_local)
    try:
        return m._transport_security()
    finally:
        # Leave the module as the rest of the suite expects to find it.
        monkeypatch.delenv("GROVE_MCP_URL", raising=False)
        importlib.reload(mcp_local)


@pytest.mark.parametrize("url", [
    None,
    "http://127.0.0.1:8765",
    "https://grove.example.ngrok.app",
    "https://grove.example.com:8443",
    "not a url",
    "",
])
def test_dns_rebinding_protection_is_never_disabled(monkeypatch, url):
    """The regression this file exists for. Fails against the old code for
    every https:// case, which was the deployment that mattered."""
    assert _settings(monkeypatch, url).enable_dns_rebinding_protection is True


def test_the_tunnel_host_is_allowlisted_not_waved_through(monkeypatch):
    t = _settings(monkeypatch, "https://grove.example.ngrok.app")
    assert "grove.example.ngrok.app" in t.allowed_hosts
    assert "https://grove.example.ngrok.app" in t.allowed_origins


def test_an_explicit_port_is_kept_because_the_host_header_carries_it(monkeypatch):
    """`Host` is host:port. Allowlisting the bare hostname would reject the
    very request the tunnel sends."""
    t = _settings(monkeypatch, "https://grove.example.com:8443")
    assert "grove.example.com:8443" in t.allowed_hosts


def test_loopback_survives_for_the_forwarded_host_case(monkeypatch):
    """The edge may forward `Host: 127.0.0.1:8765` instead of the public name —
    the original reason protection was switched off. Both are on the list, so
    neither case needs it off."""
    t = _settings(monkeypatch, "https://grove.example.ngrok.app")
    for h in ("127.0.0.1:*", "localhost:*", "[::1]:*"):
        assert h in t.allowed_hosts


@pytest.mark.parametrize("url", ["not a url", "", "ftp://elsewhere.example", "https://"])
def test_an_unusable_base_url_grants_nothing(monkeypatch, url):
    """An address that cannot be parsed is not a grant. The failure direction
    matters: falling back to "allow everything" is how the original defect read
    in the first place."""
    t = _settings(monkeypatch, url)
    assert t.enable_dns_rebinding_protection is True
    assert set(t.allowed_hosts) == {"127.0.0.1:*", "localhost:*", "[::1]:*"}


def test_a_plain_local_run_does_not_gain_a_public_host(monkeypatch):
    t = _settings(monkeypatch, "http://127.0.0.1:8765")
    assert all(
        h.startswith(("127.0.0.1", "localhost", "[::1]")) for h in t.allowed_hosts
    ), t.allowed_hosts
