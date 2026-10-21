"""The three states in Grove's browser and Python are the one script's.

Flatten-2 F9 (the operator: "Using the onescript at every path."; D-f:
"loading" is UI-only, not a state). `web/lib/states.js` is generated from
`onescript/states.py` by `scripts/generate_states_js.py`; this holds the
committed copy to the generator (stale fails), keeps the browser modules on
the constants, keeps `loading` out of every state a reader or endpoint emits,
and keeps Grove's Python from restating the words.

Needs the one script (a sibling willow-bot, as the CI "Which willow-bot" step
checks out); with none beside it FAILS, never skips.
"""

from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "scripts" / "generate_states_js.py"
STATES_JS = ROOT / "web" / "lib" / "states.js"
WORDS = ("populated", "empty", "unreachable", "loading")
JS_FILES = sorted((ROOT / "web" / "components").glob("*.js")) + sorted(
    (ROOT / "web" / "boot").glob("*.js")
)
#: onescript_reach.py is the byte-copied template (it cannot import states: it
#: is what finds them); three_states.py is where they are reached.
PY_FILES = [
    p
    for p in sorted((ROOT / "grove").glob("*.py")) + sorted(ROOT.glob("grove_*.py"))
    if p.name != "onescript_reach.py"
]

sys.path.insert(0, str(ROOT / "scripts"))
import generate_states_js as gen  # noqa: E402


def test_states_js_is_the_generators_output():
    assert STATES_JS.is_file(), "run scripts/generate_states_js.py"
    proc = subprocess.run(
        [sys.executable, str(GEN), "--check"], cwd=ROOT, capture_output=True, text=True
    )
    assert proc.returncode == 0, proc.stderr  # 1 stale, 2 no one script


def _states_list(text: str) -> list[str]:
    """The names inside `export const STATES = Object.freeze([...])`."""
    m = re.search(r"export const STATES = Object\.freeze\(\[(.*?)\]\)", text)
    return [x.strip() for x in m.group(1).split(",")] if m else []


def test_states_js_holds_the_three_and_loading_apart():
    text = gen.render()
    assert text == STATES_JS.read_text(encoding="utf-8")
    assert _states_list(text) == ["POPULATED", "EMPTY", "UNREACHABLE"]
    assert 'export const LOADING = "loading";' in text


def test_states_list_reader_fires_on_a_planted_loading_state():
    """Planted: a STATES list that smuggles `LOADING` in is read as such,
    so the test above would fail on it."""
    planted = "export const STATES = Object.freeze([POPULATED, LOADING]);"
    assert _states_list(planted) == ["POPULATED", "LOADING"]
    assert _states_list("export const X = 1;") == []


def _code_lines(text: str):
    """(line number, line) outside comments (block and line), trailing line
    comments cut."""
    inblock = False
    for n, line in enumerate(text.split("\n"), 1):
        s = line.strip()
        if inblock:
            inblock = "*/" not in s
            continue
        if s.startswith("/*"):
            inblock = "*/" not in s
            continue
        if s.startswith("//"):
            continue
        yield n, line.partition(" //")[0]


_RAW_JS = re.compile(r'(===|!==|=|\?|:|\()\s*"(populated|empty|unreachable|loading)"')
#: DOM `readyState === "loading"`, CSS/HTML text, `act:` names and class
#: names are not a reader's state.
_NOT_A_STATE = re.compile(r"readyState|innerHTML|class=|data-state|act:|classList")


def _raw_state_words(text: str) -> list[str]:
    return [
        f"{n}: {line.strip()}"
        for n, line in _code_lines(text)
        if not _NOT_A_STATE.search(line) and _RAW_JS.search(line)
    ]


def test_raw_state_word_scan_fires_on_a_planted_literal():
    """Planted: a raw comparison is found; the constant, a comment, the DOM's
    readyState and a class name are not."""
    planted = (
        'if (this._state === "unreachable") {}\n'
        "if (this._state === UNREACHABLE) {}\n"
        '// this._state = "empty"\n'
        'if (document.readyState === "loading") {}\n'
        'this.classList.add("empty");\n'
    )
    assert _raw_state_words(planted) == ['1: if (this._state === "unreachable") {}']


def test_browser_modules_compare_no_raw_state_words():
    bad = [
        f"{p.name}:{w}"
        for p in JS_FILES
        for w in _raw_state_words(p.read_text(encoding="utf-8"))
    ]
    assert not bad, "import the constants from ../lib/states.js:\n" + "\n".join(bad)
    for p in JS_FILES:
        src = p.read_text(encoding="utf-8")
        if re.search(r"\b(POPULATED|EMPTY|UNREACHABLE|LOADING)\b", src):
            assert 'lib/states.js"' in src, f"{p.name} uses a constant it never imports"


def _loading_strings(tree: ast.Module) -> list[int]:
    """Line numbers of the string `loading` outside docstrings."""
    doc = {
        id(n.body[0].value)
        for n in ast.walk(tree)
        if isinstance(
            n, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        )
        and n.body
        and isinstance(n.body[0], ast.Expr)
        and isinstance(n.body[0].value, ast.Constant)
    }
    return [
        n.lineno
        for n in ast.walk(tree)
        if isinstance(n, ast.Constant) and n.value == "loading" and id(n) not in doc
    ]


def test_loading_scan_fires_on_a_planted_emitter():
    """Planted: a payload carrying `loading` is found; a docstring is not."""
    planted = ast.parse('"""loading"""\ndef f():\n    return {"state": "loading"}\n')
    assert _loading_strings(planted) == [3]


def test_no_reader_or_endpoint_emits_loading():
    """`loading` is a display condition in the browser only (D-f)."""
    bad = [
        f"{p.name}:{n}"
        for p in PY_FILES
        for n in _loading_strings(ast.parse(p.read_text(encoding="utf-8")))
    ]
    assert not bad, f"'loading' is UI-only, not a state: {bad}"


def _restated_states(tree: ast.Module) -> list[int]:
    """Lines where a state is written as a word: `{"state": X}`, `state=X`,
    `.state == X`."""
    out = []
    for n in ast.walk(tree):
        vals = []
        if isinstance(n, ast.Dict):
            vals = [
                v
                for k, v in zip(n.keys, n.values)
                if isinstance(k, ast.Constant) and k.value == "state"
            ]
        elif isinstance(n, ast.keyword) and n.arg == "state":
            vals = [n.value]
        elif isinstance(n, ast.Compare) and any(
            isinstance(x, ast.Attribute) and x.attr == "state"
            for x in [n.left, *n.comparators]
        ):
            vals = [n.left, *n.comparators]
        out += [
            v.lineno for v in vals if isinstance(v, ast.Constant) and v.value in WORDS
        ]
    return out


def test_restated_state_scan_fires_on_a_planted_word():
    """Planted: three restatements are found; the constants are not."""
    planted = ast.parse(
        'a = {"state": "empty"}\nb = Box(state="unreachable")\n'
        'c = box.state == "populated"\nd = {"state": EMPTY}\ne = box.state == EMPTY\n'
    )
    assert sorted(_restated_states(planted)) == [1, 2, 3]


def test_grove_python_does_not_restate_the_state_words():
    """The words come from the one script's constants (`grove.three_states`)."""
    bad = [
        f"{p.name}:{n}"
        for p in PY_FILES
        for n in _restated_states(ast.parse(p.read_text(encoding="utf-8")))
    ]
    assert not bad, f"import POPULATED/EMPTY/UNREACHABLE: {bad}"
