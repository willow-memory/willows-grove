"""grove/apps/mcp_registry.py — Read ~/.mcp.json and probe serve-mode health.
b17: WDASH  ΔΣ=42
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SERVE_PORT = int(os.environ.get("GROVE_MCP_PORT", "8765"))


def mcp_config_paths() -> list[Path]:
    """Search order — first existing file wins."""
    paths: list[Path] = []
    if env_path := os.environ.get("MCP_CONFIG", "").strip():
        paths.append(Path(env_path).expanduser())
    paths.extend([
        Path.home() / ".willow" / "mcp.json",
        Path.home() / ".cursor" / "mcp.json",
        Path.home() / ".mcp.json",
        _REPO_ROOT / ".mcp.json",
    ])
    willow_root = os.environ.get("WILLOW_ROOT", "").strip()
    if willow_root:
        paths.append(Path(willow_root).expanduser() / ".mcp.json")
    seen: set[Path] = set()
    out: list[Path] = []
    for p in paths:
        rp = p.resolve()
        if rp not in seen:
            seen.add(rp)
            out.append(p)
    return out


def read_mcp_config() -> tuple[Path | None, dict]:
    for path in mcp_config_paths():
        if path.is_file():
            try:
                return path, json.loads(path.read_text())
            except Exception:
                return path, {}
    return None, {}


def _transport_label(cfg: dict) -> str:
    if cfg.get("url"):
        return "http"
    if cfg.get("type") == "http":
        return "http"
    return "stdio"


def _endpoint_summary(cfg: dict) -> str:
    if url := (cfg.get("url") or "").strip():
        return url
    cmd = str(cfg.get("command", "")).strip()
    args = " ".join(str(a) for a in cfg.get("args", []))
    return f"{cmd} {args}".strip() or "(empty)"


def probe_serve_port(port: int | None = None) -> bool:
    """True when streamable-HTTP Grove MCP responds on localhost."""
    port = _SERVE_PORT if port is None else port
    url = f"http://127.0.0.1:{port}/mcp"
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=1) as resp:
            return resp.status < 500
    except urllib.error.HTTPError as e:
        return e.code < 500
    except Exception:
        return False


def list_servers(*, probe_stdio: bool = False) -> list[dict]:
    """Servers from the first readable MCP config file."""
    source, data = read_mcp_config()
    servers = data.get("mcpServers", {})
    if not isinstance(servers, dict):
        return []
    out: list[dict] = []
    for name, cfg in servers.items():
        if not isinstance(cfg, dict):
            continue
        transport = _transport_label(cfg)
        endpoint = _endpoint_summary(cfg)
        alive = False
        if transport == "http":
            alive = probe_serve_port()
        elif probe_stdio and transport == "stdio":
            from grove.apps.mcp_client import probe_stdio as _probe_stdio
            alive = _probe_stdio(cfg)
        elif name == "grove" and transport == "stdio":
            from grove.apps.mcp_process import serve_status
            alive = serve_status().get("up") or serve_status().get("running")
        out.append({
            "name": name,
            "transport": transport,
            "endpoint": endpoint,
            "alive": alive,
            "source": str(source) if source else "",
            "cfg": dict(cfg),
            "can_serve": name == "grove",
        })
    return out


def server_count() -> int:
    return len(list_servers())


def get_server(name: str) -> dict | None:
    for server in list_servers():
        if server["name"] == name:
            return server
    return None


def mcp_summary(*, probe_stdio: bool = False) -> dict:
    from grove.apps.mcp_process import serve_status

    servers = list_servers(probe_stdio=probe_stdio)
    serve = serve_status()
    return {
        "count": len(servers),
        "serve_up": serve.get("up") or probe_serve_port(),
        "serve": serve,
        "config_path": str(read_mcp_config()[0] or ""),
        "servers": servers,
    }
