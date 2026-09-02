"""The fleet port map — three services, three ports, one of them never fronted.

Until 2026-09-02 `grove/mcp_local.py --serve` and `willow-mcp --serve` BOTH
defaulted to 8765. Only one can bind, so a tunnel pointed at "the MCP port"
fronted whichever process won the race — an inferred endpoint, which is the
same defect class as the unset WILLOW_ROOT that left `gate.py` writable
(willow-mcp B-65).

The map, and why each line matters:

    8765  willow-mcp --serve      tunnelled — the ratified remote seat (KB 2026B306)
    8766  grove_serve.py desk     NEVER tunnelled — loopback only, sealed D4
    8767  grove/mcp_local.py      tunnelled as its own resource

A design document already told a builder to front `willow-mcp --serve` "at
127.0.0.1:8766" — wrong twice, and it would have published the desk page. These
tests exist so the numbers are asserted somewhere executable rather than only
described in prose that can drift.

These read the DECLARED default out of the source rather than importing the
module and inspecting `_PORT`. Several suites in this repo set `GROVE_MCP_PORT`
and reload `grove.mcp_local`, so runtime state depends on test order — the first
version of this file passed alone and failed in the full run for exactly that
reason. The declared default is what a fresh deployment gets, and it is what
this file is about.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

WILLOW_MCP_SERVE_PORT = 8765   # willow-mcp/src/willow_mcp/server.py
GROVE_DESK_PORT = 8766         # grove_serve.py, loopback-only (D4)
GROVE_MCP_PORT = 8767          # grove/mcp_local.py --serve


def _declared_mcp_port() -> int:
    src = (ROOT / "grove" / "mcp_local.py").read_text()
    m = re.search(r'os\.getenv\(\s*"GROVE_MCP_PORT"\s*,\s*"(\d+)"\s*\)', src)
    assert m, "GROVE_MCP_PORT default not found in grove/mcp_local.py"
    return int(m.group(1))


def _declared_launcher_port() -> int:
    src = (ROOT / "run_mcp.sh").read_text()
    m = re.search(r'GROVE_MCP_PORT="\$\{GROVE_MCP_PORT:-(\d+)\}"', src)
    assert m, "GROVE_MCP_PORT default not found in run_mcp.sh"
    return int(m.group(1))


def _declared_desk_port() -> int:
    src = (ROOT / "grove_serve.py").read_text()
    m = re.search(r"^DEFAULT_PORT = (\d+)", src, re.M)
    assert m, "DEFAULT_PORT not found in grove_serve.py"
    return int(m.group(1))


def test_grove_mcp_default_does_not_collide_with_willow_mcp():
    assert _declared_mcp_port() == GROVE_MCP_PORT
    assert _declared_mcp_port() != WILLOW_MCP_SERVE_PORT, (
        "Grove MCP is back on willow-mcp's port; only one can bind and a tunnel "
        "would front whichever process won the race"
    )


def test_grove_mcp_never_takes_the_loopback_only_desk_port():
    # 8766 is the desk page, sealed loopback-only. Nothing tunnelable may sit on
    # it — a design doc already got this wrong in a build instruction.
    assert _declared_mcp_port() != GROVE_DESK_PORT


def test_launcher_and_module_agree():
    # run_mcp.sh exports the default the module then reads. If they disagree,
    # the port depends on how the server was started, which is how a tunnel ends
    # up in front of something nobody chose.
    assert _declared_launcher_port() == _declared_mcp_port()


def test_desk_page_port_is_unchanged():
    assert _declared_desk_port() == GROVE_DESK_PORT


def test_the_three_ports_are_distinct():
    assert len({WILLOW_MCP_SERVE_PORT, GROVE_DESK_PORT, GROVE_MCP_PORT}) == 3
