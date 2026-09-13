"""ONE Desk hook stack: Cursor and Claude compile from hooks/client-hooks.json.

Gap 651b4a1ccfab — dialect names may differ; the event set must not.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

pw = pytest.importorskip(
    "willow_mcp.project_wiring",
    reason="willow-mcp compiles the Desk hook_manifest",
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "hooks" / "client-hooks.json"
SYNC = ROOT / "scripts" / "sync_desk_client_hooks.py"
CLAUDE = ROOT / ".claude" / "settings.json"
MCP_TEMPLATE = ROOT / "mcp.template.json"

ENTRY = {
    "path": str(ROOT),
    "agent": "willow",
    "wiring": {
        "claude_settings": "project",
        "claude_hooks": "tracked",
        "hook_manifest": "hooks/client-hooks.json",
    },
}


@pytest.fixture
def manifest():
    return pw._load_hook_manifest("willows-grove", ENTRY)


def test_client_hooks_loads_through_willow_mcp(manifest):
    assert manifest["version"] == 1
    assert manifest["command"] == "hooks/grove-hook"
    assert len(manifest["hooks"]) >= 6


def test_client_hooks_covers_the_full_ide_event_set(manifest):
    events = {h["event"] for h in manifest["hooks"]}
    assert events == {
        "session_start",
        "prompt_submit",
        "pre_compact",
        "pre_tool_use",
        "stop",
        "session_end",
    }


def test_pre_tool_use_is_willow_via_grove_hook_not_a_second_gate(manifest):
    """§7 preserved: PreToolUse rows are before_* actions that grove-hook
    delegates to willow_mcp.pre_tool_hook — one guard, one command."""
    tools = {h.get("tool") for h in manifest["hooks"] if h["event"] == "pre_tool_use"}
    assert tools == {"shell", "mcp", "write", "web", "task"}
    actions = {h["action"] for h in manifest["hooks"] if h["event"] == "pre_tool_use"}
    assert actions == {
        "before_bash",
        "before_mcp",
        "before_write",
        "before_web",
        "before_task",
    }


@pytest.mark.parametrize(
    "client,expected",
    [
        (
            "claude",
            {
                "SessionStart",
                "UserPromptSubmit",
                "PreCompact",
                "PreToolUse",
                "Stop",
                "SessionEnd",
            },
        ),
        (
            "cursor",
            {
                "sessionStart",
                "beforeSubmitPrompt",
                "preCompact",
                "preToolUse",
                "stop",
                "sessionEnd",
            },
        ),
    ],
)
def test_both_dialects_compile_the_same_neutral_set(manifest, client, expected):
    m = manifest
    if client == "claude":
        # Dialect strip — Claude has no fail_closed.
        m = json.loads(json.dumps(manifest))
        for hook in m["hooks"]:
            hook.pop("fail_closed", None)
    compiled = pw._compile_hook_manifest("willows-grove", ENTRY, m, client=client)
    assert set(compiled) == expected


def test_sync_script_parity_and_check():
    assert SYNC.is_file()
    parity = subprocess.run(
        [sys.executable, str(SYNC), "--parity"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert parity.returncode == 0, parity.stderr or parity.stdout
    # Regenerating then --check must be clean for tracked Claude hooks.
    write = subprocess.run(
        [sys.executable, str(SYNC)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert write.returncode == 0, write.stderr or write.stdout
    check = subprocess.run(
        [sys.executable, str(SYNC), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert check.returncode == 0, check.stderr or check.stdout


def test_tracked_claude_settings_are_portable():
    data = json.loads(CLAUDE.read_text(encoding="utf-8"))
    blob = json.dumps(data)
    assert str(ROOT) not in blob
    assert "$CLAUDE_PROJECT_DIR/hooks/grove-hook" in blob
    assert "${WILLOW_HOME}/config/verifiers.json" in blob
    assert "Stop" in data["hooks"]
    assert "UserPromptSubmit" in data["hooks"]
    assert "PreCompact" in data["hooks"]


def test_grove_hook_launcher_is_executable():
    cmd = ROOT / "hooks" / "grove-hook"
    assert cmd.is_file()
    assert cmd.stat().st_mode & 0o111
    body = ROOT / "hooks" / "grove_hook.py"
    assert body.is_file()


def _missing_needles(text: str, needles: tuple[str, ...]) -> list[str]:
    """Needles absent from ``text`` — membership scan for reinject contract."""
    return [n for n in needles if n not in text]


def test_reinject_names_codebase_memory_mcp():
    text = (ROOT / "hooks" / "grove_hook.py").read_text(encoding="utf-8")
    assert _missing_needles(text, ("codebase-memory-mcp", "search_graph")) == []


def test_missing_needles_fires_on_a_planted_absence():
    assert _missing_needles("only this", ("codebase-memory-mcp",)) == [
        "codebase-memory-mcp"
    ]


def test_mcp_template_wires_codebase_memory_for_every_desk_session():
    """Operator rule: every Cursor session in every repo should see CMM.

    Grove's tracked template is the Desk proof; fleet misses are a separate
    gap. ``codebase-memory-mcp install`` only puts Cursor in ~/.cursor/mcp.json
    — per-repo .mcp.json / mcp.template.json is what seats inherit.
    """
    data = json.loads(MCP_TEMPLATE.read_text(encoding="utf-8"))
    servers = data.get("mcpServers") or {}
    assert "codebase-memory-mcp" in servers
    block = servers["codebase-memory-mcp"]
    assert "codebase-memory-mcp" in block.get("command", "")
