"""grove/apps/mcp_catalog.py — Annotated MCP registry + live-server drift.
b17: WDASH  ΔΣ=42

The dashboard's MCP pane shows *live* tools (by spawning the stdio server) and
*servers* (from .mcp.json). This module adds the third leg: the annotated
registry (sap/mcp_registry.json) that documents every tool's group, tier, and
description — the source of truth for how tools should be grouped and how loud
they should be (tier → visibility).

It also computes drift: what the registry documents but the live server does not
expose, and what the server exposes that the registry never documented. The gate
between intended surface and actual surface, made visible.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

# Tier → display rank. Lower = louder (lands on cockpit); higher = hidden by default.
TIER_RANK = {"minimal": 0, "core": 1, "standard": 2, "extended": 3}
DEFAULT_TIER = "standard"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def registry_paths() -> list[Path]:
    """Search order for the annotated registry. First existing wins.

    Primary strategy: derive from .mcp.json — the willow server command points at
    .../sap/unified_mcp.sh, so mcp_registry.json is its sibling. This survives
    non-standard checkout locations that a hardcoded path would miss.
    """
    out: list[Path] = []
    if env := os.environ.get("MCP_REGISTRY", "").strip():
        out.append(Path(env).expanduser())

    # Derive sap/ dir from the MCP server command in .mcp.json.
    for sap_dir in _sap_dirs_from_mcp_config():
        out.append(sap_dir / "mcp_registry.json")

    if willow_root := os.environ.get("WILLOW_ROOT", "").strip():
        out.append(Path(willow_root).expanduser() / "sap" / "mcp_registry.json")

    # Common checkout locations as a last resort.
    home = Path.home()
    out.extend([
        home / "github" / "willow-2.0" / "sap" / "mcp_registry.json",
        home / "willow-2.0" / "sap" / "mcp_registry.json",
    ])

    seen: set[Path] = set()
    uniq: list[Path] = []
    for p in out:
        rp = p.resolve()
        if rp not in seen:
            seen.add(rp)
            uniq.append(p)
    return uniq


def _sap_dirs_from_mcp_config() -> list[Path]:
    """Find sap/ directories referenced by server commands in the MCP config."""
    from grove.apps.mcp_registry import read_mcp_config

    _, data = read_mcp_config()
    servers = data.get("mcpServers", {})
    if not isinstance(servers, dict):
        return []
    dirs: list[Path] = []
    for cfg in servers.values():
        if not isinstance(cfg, dict):
            continue
        for arg in cfg.get("args", []):
            arg = str(arg)
            if "/sap/" in arg or arg.endswith("/sap"):
                # arg is like /…/willow-2.0/sap/unified_mcp.sh → take its sap/ dir
                p = Path(arg)
                sap = p.parent if p.parent.name == "sap" else None
                if sap is None and p.name == "sap":
                    sap = p
                if sap is not None:
                    dirs.append(sap)
    return dirs


def registry_path() -> Path | None:
    for p in registry_paths():
        if p.is_file():
            return p
    return None


def load_registry() -> dict:
    """Return the parsed annotated registry, or {} if not found / unreadable.

    Shape: {"groups": {group: desc}, "tools": {name: {group, tier?, description}}}
    """
    path = registry_path()
    if path is None:
        return {}
    try:
        data = json.loads(path.read_text())
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def tool_index() -> dict[str, dict]:
    """name → {group, tier, description} for every documented tool."""
    reg = load_registry()
    tools = reg.get("tools", {})
    if not isinstance(tools, dict):
        return {}
    out: dict[str, dict] = {}
    for name, meta in tools.items():
        if not isinstance(meta, dict):
            continue
        out[name] = {
            "group": meta.get("group", "?"),
            "tier": meta.get("tier", DEFAULT_TIER),
            "description": meta.get("description", ""),
        }
    return out


def groups() -> dict[str, str]:
    reg = load_registry()
    g = reg.get("groups", {})
    return g if isinstance(g, dict) else {}


def annotate(live_tools: list[dict]) -> list[dict]:
    """Enrich live tool dicts with registry group/tier; mark undocumented ones.

    Each returned tool gains: group, tier, tier_rank, documented (bool).
    Live description is preferred; registry description fills gaps.
    """
    idx = tool_index()
    out: list[dict] = []
    for tool in live_tools:
        name = tool.get("name", "")
        meta = idx.get(name)
        enriched = dict(tool)
        if meta:
            enriched["group"] = meta["group"]
            enriched["tier"] = meta["tier"]
            enriched["documented"] = True
            if not enriched.get("description"):
                enriched["description"] = meta["description"]
        else:
            enriched["group"] = "(undocumented)"
            enriched["tier"] = DEFAULT_TIER
            enriched["documented"] = False
        enriched["tier_rank"] = TIER_RANK.get(enriched["tier"], TIER_RANK[DEFAULT_TIER])
        out.append(enriched)
    return out


def drift(live_tool_names) -> dict:
    """Compare registry vs live surface.

    Returns {registry_only, live_only, matched, registry_total, live_total}.
    - registry_only: documented but the live server did not expose (stale doc or
      tool removed).
    - live_only: exposed but never documented (the registry needs an entry).
    """
    live = set(live_tool_names)
    registered = set(tool_index().keys())
    registry_only = sorted(registered - live)
    live_only = sorted(live - registered)
    matched = sorted(registered & live)
    return {
        "registry_only": registry_only,
        "live_only": live_only,
        "matched": matched,
        "registry_total": len(registered),
        "live_total": len(live),
    }
