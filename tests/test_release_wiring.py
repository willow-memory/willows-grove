# b17: WGRV1 ΔΣ=42
"""tests/test_release_wiring.py — release-please and the pr-title guard, held to
this repo's packaging.

C4-grove-release (fleet plan Wave 4; docs/ideas.md item 12). Three things
here are copies of a number or a list that lives elsewhere, and a copy that
drifts is a release that goes wrong silently:

* `pr-title.yml`'s `PACKAGED` tuple — the paths whose change is what
  `pip install willows-grove` delivers — must be exactly what pyproject's
  wheel `packages` and `force-include` ship, plus pyproject itself. The
  reconciler's own file says this is the one constant that must not be
  copied between repos; the test is what stops it being wrong here.
* `.release-please-manifest.json`'s version must be the hatch
  `fallback-version` (which `tests/test_version_changelog_sync.py` already
  holds to CHANGELOG.md's newest release), or the first release PR bumps
  from the wrong number.
* `release-please-config.json`'s `extra-files` must bump the two files
  release.yml refuses a mismatching tag against: the fallback-version and
  `safe-app-manifest.json`'s version.

The hidden set and the reasoning comments are held to the fleet's published
document by `tests/test_fleet_conventions.py`, not restated here.
"""

from __future__ import annotations

import ast
import json
import re
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PR_TITLE = REPO_ROOT / ".github" / "workflows" / "pr-title.yml"
PYPROJECT = REPO_ROOT / "pyproject.toml"
MANIFEST = REPO_ROOT / ".release-please-manifest.json"
RELEASE_CONFIG = REPO_ROOT / "release-please-config.json"
RELEASE_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "release-please.yml"

_PACKAGED_RE = re.compile(r"PACKAGED = \((?P<body>.*?)\)\n", re.DOTALL)
_FALLBACK_RE = re.compile(r'^\s*fallback-version\s*=\s*"([^"]+)"', re.MULTILINE)


def _workflow_packaged(workflow_text: str) -> set[str]:
    """The `PACKAGED` tuple as pr-title.yml's embedded Python declares it."""
    m = _PACKAGED_RE.search(workflow_text)
    assert m, "pr-title.yml declares no PACKAGED = (...) tuple"
    value = ast.literal_eval("(" + m.group("body") + ")")
    return set(value)


def _pyproject_packaged(pyproject_text: str) -> set[str]:
    """What the wheel ships, as pyproject declares it: each `packages` entry
    as a directory prefix, each `force-include` key as itself (a directory
    key gets its trailing slash), plus pyproject.toml."""
    wheel = tomllib.loads(pyproject_text)["tool"]["hatch"]["build"]["targets"]["wheel"]
    out = {f"{pkg}/" for pkg in wheel["packages"]}
    for key in wheel.get("force-include", {}):
        out.add(key if "." in Path(key).name else f"{key.rstrip('/')}/")
    out.add("pyproject.toml")
    return out


def _manifest_version(manifest_text: str) -> str:
    return json.loads(manifest_text)["."]


def _fallback_version(pyproject_text: str) -> str | None:
    m = _FALLBACK_RE.search(pyproject_text)
    return m.group(1) if m else None


def _extra_file_targets(config_text: str) -> set[tuple[str, str]]:
    """(path, jsonpath) for every structured extra-file the config bumps."""
    package = json.loads(config_text)["packages"]["."]
    return {
        (e["path"], e["jsonpath"])
        for e in package.get("extra-files", [])
        if isinstance(e, dict)
    }


_INPUT_RE = re.compile(r"^\s+(config-file|manifest-file):\s*(\S+)\s*$", re.MULTILINE)


def _action_inputs(workflow_text: str) -> dict[str, str]:
    """The `config-file:` / `manifest-file:` inputs the release-please step
    passes, by name — the two files the workflow cannot run without."""
    return {k: v for k, v in _INPUT_RE.findall(workflow_text)}


REQUIRED_EXTRA_FILES = {
    ("pyproject.toml", "$.tool.hatch.version.fallback-version"),
    ("safe-app-manifest.json", "$.version"),
}


# ── the real tree ────────────────────────────────────────────────────────────


def test_the_pr_title_guards_packaged_set_is_what_the_wheel_ships():
    declared = _workflow_packaged(PR_TITLE.read_text(encoding="utf-8"))
    shipped = _pyproject_packaged(PYPROJECT.read_text(encoding="utf-8"))
    assert declared == shipped, (
        f"pr-title.yml PACKAGED {sorted(declared)} != what pyproject ships {sorted(shipped)}"
    )


def test_the_manifest_version_is_the_hatch_fallback():
    assert _manifest_version(MANIFEST.read_text(encoding="utf-8")) == _fallback_version(
        PYPROJECT.read_text(encoding="utf-8")
    )


def test_the_config_bumps_both_files_the_release_workflow_checks():
    targets = _extra_file_targets(RELEASE_CONFIG.read_text(encoding="utf-8"))
    assert REQUIRED_EXTRA_FILES <= targets, (
        f"extra-files missing {REQUIRED_EXTRA_FILES - targets}"
    )


def test_the_release_workflow_names_the_config_and_manifest_that_exist():
    named = _action_inputs(RELEASE_WORKFLOW.read_text(encoding="utf-8"))
    assert named.get("config-file") == RELEASE_CONFIG.name and RELEASE_CONFIG.exists()
    assert named.get("manifest-file") == MANIFEST.name and MANIFEST.exists()


# ── the plants ───────────────────────────────────────────────────────────────

_PLANTED_PYPROJECT = """[tool.hatch.version]
fallback-version = "0.10.0"

[tool.hatch.build.targets.wheel]
packages = ["grove", "u2u"]

[tool.hatch.build.targets.wheel.force-include]
"grove_serve.py" = "grove_serve.py"
"web" = "web"
"""


def test_the_packaged_pin_fires_on_a_planted_guard_that_forgot_a_package():
    """Planted: a guard whose PACKAGED lists grove/ but not u2u/, against a
    pyproject that ships both plus a module and the web/ tree."""
    planted = 'x = 1\n          PACKAGED = (\n              "grove/", "grove_serve.py", "web/", "pyproject.toml",\n          )\n'
    assert _workflow_packaged(planted) == {
        "grove/",
        "grove_serve.py",
        "web/",
        "pyproject.toml",
    }
    shipped = _pyproject_packaged(_PLANTED_PYPROJECT)
    assert shipped == {"grove/", "u2u/", "grove_serve.py", "web/", "pyproject.toml"}
    assert _workflow_packaged(planted) != shipped


def test_the_manifest_pin_fires_on_a_planted_stale_manifest():
    """Planted: a manifest still at 0.9.0 under a pyproject whose fallback
    is 0.10.0 — the first release PR would bump from the wrong number."""
    assert _manifest_version('{".": "0.9.0"}') == "0.9.0"
    assert _fallback_version(_PLANTED_PYPROJECT) == "0.10.0"
    assert _manifest_version('{".": "0.9.0"}') != _fallback_version(_PLANTED_PYPROJECT)
    assert _fallback_version("[project]\nname = 'x'\n") is None


def test_the_extra_files_pin_fires_on_a_planted_config_that_bumps_only_one():
    """Planted: a config bumping the fallback-version but not
    safe-app-manifest.json — release.yml would refuse the tag."""
    planted = json.dumps(
        {
            "packages": {
                ".": {
                    "extra-files": [
                        {
                            "type": "toml",
                            "path": "pyproject.toml",
                            "jsonpath": "$.tool.hatch.version.fallback-version",
                        },
                        "version.txt",
                    ]
                }
            }
        }
    )
    targets = _extra_file_targets(planted)
    assert targets == {("pyproject.toml", "$.tool.hatch.version.fallback-version")}
    assert not REQUIRED_EXTRA_FILES <= targets


def test_the_inputs_pin_fires_on_a_planted_workflow_naming_a_missing_config():
    """Planted: a workflow whose release-please step names a config file
    this tree does not carry, and no manifest at all."""
    planted = "      - uses: googleapis/release-please-action@v5\n        with:\n          config-file: elsewhere.json\n"
    named = _action_inputs(planted)
    assert named == {"config-file": "elsewhere.json"}
    assert named.get("config-file") != RELEASE_CONFIG.name
    assert not (REPO_ROOT / named["config-file"]).exists()
    assert named.get("manifest-file") is None
