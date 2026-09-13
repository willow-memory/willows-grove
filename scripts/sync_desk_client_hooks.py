#!/usr/bin/env python3
# b17: GRVHK  ΔΣ=42
"""Compile hooks/client-hooks.json into Cursor + Claude Desk artifacts.

ONE neutral stack. Dialect event names differ; the event set and actions must
not (gap 651b4a1ccfab). Edits go in hooks/client-hooks.json; this script is the
only writer of .cursor/hooks.json hooks and .claude/settings.json hooks.

Usage:
  scripts/sync_desk_client_hooks.py          # write
  scripts/sync_desk_client_hooks.py --check  # exit 1 on drift
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_REL = "hooks/client-hooks.json"
CURSOR_OUT = ROOT / ".cursor" / "hooks.json"
CLAUDE_OUT = ROOT / ".claude" / "settings.json"


def _entry() -> dict[str, Any]:
    """Registry-shaped entry. Seat env prefers live .mcp.json, then process env."""
    env: dict[str, str] = {
        "WILLOW_HUMAN_ORCHESTRATOR": "1",
        "WILLOW_HANDOFF_PROJECT": "willows-grove",
    }
    mcp_path = ROOT / ".mcp.json"
    if mcp_path.is_file():
        try:
            data = json.loads(mcp_path.read_text(encoding="utf-8"))
            willow = (data.get("mcpServers") or {}).get("willow-mcp") or {}
            for key, val in (willow.get("env") or {}).items():
                if isinstance(key, str) and isinstance(val, str) and val.strip():
                    env[key] = val
        except (OSError, json.JSONDecodeError):
            pass
    for key in (
        "WILLOW_HOME",
        "WILLOW_STORE_ROOT",
        "WILLOW_KEYRING",
        "WILLOW_OPERATOR_VERIFIER",
        "WILLOW_MCP_PYTHON",
    ):
        if key not in env and os.environ.get(key, "").strip():
            env[key] = os.environ[key].strip()
    if "WILLOW_KEYRING" not in env and env.get("WILLOW_HOME"):
        env["WILLOW_KEYRING"] = f"{env['WILLOW_HOME']}/config/verifiers.json"
    return {
        "path": str(ROOT),
        "agent": "willow",
        "env": env,
        "wiring": {
            "claude_settings": "project",
            "claude_hooks": "tracked",
            "hook_manifest": MANIFEST_REL,
        },
    }


def _load_pw():
    try:
        from willow_mcp import project_wiring as pw
    except ImportError as exc:
        raise SystemExit(
            "sync_desk_client_hooks: willow_mcp.project_wiring required "
            f"(install willow-mcp / set WILLOW_MCP_PYTHON): {exc}"
        ) from exc
    return pw


def _manifest_for_client(manifest: dict[str, Any], client: str) -> dict[str, Any]:
    """Dialect strip: Claude has no fail_closed; keep it for Cursor compile."""
    if client != "claude":
        return manifest
    out = copy.deepcopy(manifest)
    for hook in out.get("hooks") or []:
        if isinstance(hook, dict) and hook.get("fail_closed") is True:
            del hook["fail_closed"]
    return out


def _manifest_with_runtime(
    pw: Any, entry: dict[str, Any], manifest: dict[str, Any]
) -> dict[str, Any]:
    """Fold runtime_env into manifest.env so one `env KEY=val` prefix carries both.

    ``_compile_hook_manifest`` only reads manifest.env (not entry.env). Cursor
    hook subprocesses inherit nothing from MCP, so WILLOW_HOME / KEYRING /
    WILLOW_MCP_PYTHON must be on the command line.
    """
    agent = str(entry.get("agent") or "willow")
    runtime = pw.runtime_env(agent, entry)
    runtime.setdefault("WILLOW_PROJECT_ROOT", str(ROOT))
    runtime.setdefault("CLAUDE_PROJECT_DIR", str(ROOT))
    menv = pw._manifest_env("willows-grove", entry, manifest)
    # Manifest seat keys win over runtime defaults; runtime fills HOME/KEYRING.
    full = {**runtime, **menv}
    # Drop keys _manifest_env always re-derives from agent/root, to avoid
    # feeding absolute WILLOW_APP_ID back through placeholder substitution.
    skip = {"WILLOW_APP_ID", "WILLOW_AGENT_NAME", "AGENT_NAME", "WILLOW_PROJECT_ROOT"}
    fake = copy.deepcopy(manifest)
    fake["env"] = {k: v for k, v in full.items() if k not in skip and isinstance(v, str)}
    return fake


def _compile(pw: Any, entry: dict[str, Any], client: str) -> dict[str, Any]:
    manifest = pw._load_hook_manifest("willows-grove", entry)
    if client == "cursor":
        manifest = _manifest_with_runtime(pw, entry, manifest)
    else:
        manifest = _manifest_for_client(manifest, client)
    compiled = pw._compile_hook_manifest(
        "willows-grove", entry, manifest, client=client
    )
    if client == "cursor":
        return {"version": 1, "hooks": compiled}
    return compiled

def _portable_claude_hooks(
    pw: Any, entry: dict[str, Any], compiled: dict[str, Any]
) -> dict[str, Any]:
    """Rewrite absolute compile paths to $CLAUDE_PROJECT_DIR / ${WILLOW_HOME}.

    ``.claude/settings.json`` is tracked; Cursor's hooks.json is gitignored.
    Machine-absolute prefixes must not land in the tracked file (PR 65 shape).
    """
    root = str(ROOT)
    home = (entry.get("env") or {}).get("WILLOW_HOME") or os.environ.get("WILLOW_HOME", "")
    out: dict[str, Any] = {}
    for event, entries in compiled.items():
        new_entries = []
        for entry_hook in entries:
            if not isinstance(entry_hook, dict):
                new_entries.append(entry_hook)
                continue
            nested = []
            for hook in entry_hook.get("hooks") or []:
                if not isinstance(hook, dict) or not isinstance(hook.get("command"), str):
                    nested.append(hook)
                    continue
                cmd = hook["command"]
                # Drop the absolute `env KEY=val …` prefix from the compiler;
                # portable seat env lives in settings.json "env" + a short prefix.
                if cmd.startswith("env "):
                    # last tokens: <grove-hook> <client> <action>
                    parts = cmd.split()
                    # find grove-hook path
                    idx = next(
                        (i for i, p in enumerate(parts) if p.endswith("hooks/grove-hook")),
                        None,
                    )
                    if idx is not None and idx + 2 < len(parts):
                        client, action = parts[idx + 1], parts[idx + 2]
                        cmd = (
                            'GROVE_SEAT_FILE="$CLAUDE_PROJECT_DIR/hooks/seat.md" '
                            'WILLOW_KEYRING="${WILLOW_HOME}/config/verifiers.json" '
                            f'"$CLAUDE_PROJECT_DIR/hooks/grove-hook" {client} {action}'
                        )
                    else:
                        cmd = cmd.replace(root, "$CLAUDE_PROJECT_DIR")
                        if home:
                            cmd = cmd.replace(home, "${WILLOW_HOME}")
                else:
                    cmd = cmd.replace(root, "$CLAUDE_PROJECT_DIR")
                    if home:
                        cmd = cmd.replace(home, "${WILLOW_HOME}")
                nested.append({**hook, "command": cmd})
            new_entries.append({**entry_hook, "hooks": nested})
        out[event] = new_entries
    return out


def _render_claude(pw: Any, entry: dict[str, Any]) -> dict[str, Any]:
    hooks = _portable_claude_hooks(pw, entry, _compile(pw, entry, "claude"))
    # Portable ambient env only — no machine-absolute vault paths in git.
    env = {
        "WILLOW_APP_ID": "willow",
        "WILLOW_AGENT_NAME": "willow",
        "AGENT_NAME": "willow",
        "WILLOW_HUMAN_ORCHESTRATOR": "1",
        "WILLOW_HANDOFF_PROJECT": "willows-grove",
        "WILLOW_KEYRING": "${WILLOW_HOME}/config/verifiers.json",
    }
    existing: dict[str, Any] = {}
    if CLAUDE_OUT.is_file():
        try:
            existing = json.loads(CLAUDE_OUT.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            existing = {}
    out = {k: v for k, v in existing.items() if k not in ("hooks", "env")}
    out["hooks"] = hooks
    out["env"] = env
    return out


def render() -> tuple[dict[str, Any], dict[str, Any]]:
    pw = _load_pw()
    entry = _entry()
    return _compile(pw, entry, "cursor"), _render_claude(pw, entry)


def _dump(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2, sort_keys=False) + "\n"


def write() -> None:
    cursor, claude = render()
    CURSOR_OUT.parent.mkdir(parents=True, exist_ok=True)
    CLAUDE_OUT.parent.mkdir(parents=True, exist_ok=True)
    CURSOR_OUT.write_text(_dump(cursor), encoding="utf-8")
    CLAUDE_OUT.write_text(_dump(claude), encoding="utf-8")
    print(f"wrote {CURSOR_OUT.relative_to(ROOT)}")
    print(f"wrote {CLAUDE_OUT.relative_to(ROOT)}")


def check() -> int:
    """Drift gate: tracked Claude hooks + event parity. Cursor is local-only."""
    rc = event_parity()
    if rc != 0:
        return rc
    if not CLAUDE_OUT.is_file():
        print(
            "sync_desk_client_hooks --check: missing .claude/settings.json; run without --check",
            file=sys.stderr,
        )
        return 1
    _, claude = render()
    got_l = json.loads(CLAUDE_OUT.read_text(encoding="utf-8"))
    drift = []
    if got_l.get("hooks") != claude.get("hooks"):
        drift.append(f"{CLAUDE_OUT.relative_to(ROOT)} (hooks)")
    if (got_l.get("env") or {}) != (claude.get("env") or {}):
        drift.append(f"{CLAUDE_OUT.relative_to(ROOT)} (env)")
    if CURSOR_OUT.is_file():
        cursor, _ = render()
        got_c = json.loads(CURSOR_OUT.read_text(encoding="utf-8"))
        if got_c != cursor:
            drift.append(f"{CURSOR_OUT.relative_to(ROOT)} (local)")
    if drift:
        print(
            "sync_desk_client_hooks --check: drift from hooks/client-hooks.json:\n  - "
            + "\n  - ".join(drift)
            + "\nRe-run: scripts/sync_desk_client_hooks.py",
            file=sys.stderr,
        )
        return 1
    print("sync_desk_client_hooks --check: ok")
    return 0


def event_parity() -> int:
    """Neutral events present in both compiled dialects (CI companion)."""
    pw = _load_pw()
    entry = _entry()
    manifest = pw._load_hook_manifest("willows-grove", entry)
    cursor = set(
        pw._compile_hook_manifest(
            "willows-grove", entry, manifest, client="cursor"
        ).keys()
    )
    claude_manifest = _manifest_for_client(manifest, "claude")
    claude = set(
        pw._compile_hook_manifest(
            "willows-grove", entry, claude_manifest, client="claude"
        ).keys()
    )
    # Map back to neutral via _HOOK_EVENTS
    neutral_from_cursor = {
        neutral
        for neutral, clients in pw._HOOK_EVENTS.items()
        if clients.get("cursor") in cursor
    }
    neutral_from_claude = {
        neutral
        for neutral, clients in pw._HOOK_EVENTS.items()
        if clients.get("claude") in claude
    }
    if neutral_from_cursor != neutral_from_claude:
        print(
            "event parity failed:\n"
            f"  cursor-only: {sorted(neutral_from_cursor - neutral_from_claude)}\n"
            f"  claude-only: {sorted(neutral_from_claude - neutral_from_cursor)}",
            file=sys.stderr,
        )
        return 1
    print(f"event parity ok: {sorted(neutral_from_cursor)}")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit 1 if compiled Desk hooks drift from client-hooks.json",
    )
    parser.add_argument(
        "--parity",
        action="store_true",
        help="assert Cursor and Claude compile the same neutral event set",
    )
    args = parser.parse_args(argv)
    if args.parity:
        return event_parity()
    if args.check:
        return check()
    write()
    return event_parity()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
