"""Regression: scripts/ci-security-grep.sh docstring must not claim a
pattern that PATTERN does not actually match.

Finding m34-security-grep-pattern-honesty: the "Patterns" section of the
script's header docstring listed ``input().*shell`` as a pattern the
sweep matches, but the ``PATTERN`` extended-regex variable defined later
in the file has no alternation for ``input(``. A docstring claim that
the code does not back up is exactly the kind of drift
docs/INVARIANTS.md §10 exists to catch: every claim needs a witness, and
here the witness (PATTERN) disagreed with the doc.

This test parses the docstring's bullet list and the PATTERN string
straight out of the shipped shell script and asserts every
docstring-claimed pattern is actually present in PATTERN. It fails on
the unfixed script (the ``input().*shell`` bullet has no counterpart in
PATTERN) and passes once the docstring is reconciled to describe only
what PATTERN matches.
"""

import re
from pathlib import Path

SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent
    / "scripts"
    / "ci-security-grep.sh"
)


def _read_script() -> str:
    return SCRIPT_PATH.read_text(encoding="utf-8")


def _docstring_claimed_patterns(text: str) -> list[str]:
    """Extract the pattern tokens listed under the '# Patterns' header.

    Each bullet looks like:
        #   - os.system(              — arbitrary shell invocation
    We pull out the text between '- ' and the run of 2+ spaces that
    precedes the em-dash description.
    """
    lines = text.splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == "# Patterns")
    except StopIteration:
        raise AssertionError("script has no '# Patterns' docstring header")
    try:
        end = next(
            i for i, l in enumerate(lines) if l.strip() == "# Allowlist"
        )
    except StopIteration:
        raise AssertionError("script has no '# Allowlist' docstring header")

    bullet_re = re.compile(r"^#\s+-\s+(\S.*?)\s{2,}—")
    claimed = []
    for line in lines[start:end]:
        m = bullet_re.match(line)
        if m:
            claimed.append(m.group(1).strip())
    assert claimed, "no pattern bullets parsed out of the docstring"
    return claimed


def _extract_pattern_variable(text: str) -> str:
    m = re.search(r"^PATTERN='(.*)'\s*$", text, flags=re.MULTILINE)
    assert m, "could not find PATTERN='...' assignment in the script"
    return m.group(1)


def _unescape(regex_source: str) -> str:
    # Drop backslash-escaping so a docstring's plain-text token
    # ("os.system(") can be matched as a substring of the regex source
    # ("os\.system\(" -> "os.system(").
    return re.sub(r"\\(.)", r"\1", regex_source)


def test_every_docstring_pattern_is_backed_by_PATTERN():
    text = _read_script()
    claimed = _docstring_claimed_patterns(text)
    pattern_raw = _extract_pattern_variable(text)
    pattern_decoded = _unescape(pattern_raw)

    unbacked = []
    for token in claimed:
        # A token like "subprocess.Popen(...shell=True" uses "..." as a
        # stand-in for the wildcard the real regex spells out
        # differently (e.g. "[^)]*"); check each side of it separately.
        fragments = [f for f in token.split("...") if f]
        if not all(fragment in pattern_decoded for fragment in fragments):
            unbacked.append(token)

    assert not unbacked, (
        "docstring claims pattern(s) with no counterpart in PATTERN: "
        f"{unbacked!r}. PATTERN was: {pattern_raw!r}"
    )
