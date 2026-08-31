# b17: WGRV1 ΔΣ=42
"""tests/test_tester_onboarding_runnable.py — the first hour actually works.

``docs/TESTER_ONBOARDING.md`` is the first thing a new tester runs, in
order, from a clean machine. Three separate defects had accumulated in
it, and every one of them was invisible to the tree:

1. **Step 2 aborted on Debian.** ``pip install -r requirements.txt`` with
   no virtualenv fails with ``Cannot uninstall PyJWT 2.7.0, RECORD file
   not found`` — PyJWT arrives transitively through ``mcp``
   (``pyjwt[crypto]>=2.10.1``), pip resolves it forward, and cannot
   remove a copy ``apt`` installed because distro packages ship no
   ``RECORD``. The error names Debian, so it reads as a broken machine
   rather than a missing step (issue #14).
2. **Step 5 named a file that has never existed.** ``python3 app.py``.
   There is no ``app.py`` in this repository and no history of one;
   ``tests/test_documented_entrypoints_exist.py`` audits
   ``docs/grove-served-page.md`` only, so nothing covered this doc.
3. **A duplicated sanity-check block carried curly quotes.** ``psql -d
   “$WILLOW_PG_DB”`` does not execute — the shell has no idea what
   ``“`` is. A tester copy-pasting the first of the two identical
   sections got an error; the second copy, with straight quotes, worked.

The through-line is that a document can promise a machine state nobody
checks. This module checks the three properties that make the doc
runnable rather than merely present:

* the install step creates a virtualenv **before** it installs;
* every file the doc tells a tester to run exists on disk;
* no shell command carries a curly quote.

Follows the house pattern of ``tests/test_documented_entrypoints_exist.py``:
each audit is paired with a self-check asserting the parser actually
found something, because a regex that silently stops matching turns an
audit into a green no-op — which is the failure class this whole
document was suffering from.

Stdlib only. Reads the doc, touches no network and no database.
"""
from __future__ import annotations

import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC_PATH = os.path.join(ROOT, "docs", "TESTER_ONBOARDING.md")

#: Curly quotes. Inside a shell command these are literal characters, not
#: quoting — the command fails rather than doing something subtly wrong.
_SMART_QUOTES = "“”‘’"

#: `scripts/<name>` or `deploy/<name>`, with or without a leading `./`.
_SCRIPT_RE = re.compile(r"\b(scripts|deploy)/([A-Za-z0-9_.-]+)")

#: A bare `<name>.py` or `<name>.sql` token — the files a tester is told to
#: run or load. Deliberately not `python3 -m <module>`, which names an
#: importable module rather than a path.
_FILE_RE = re.compile(r"\b([A-Za-z0-9_./-]+\.(?:py|sql))\b")


def _doc_text() -> str:
    with open(DOC_PATH, encoding="utf-8") as fh:
        return fh.read()


def _bash_blocks() -> list[str]:
    """Every ```bash fenced block in the doc, as raw text."""
    blocks: list[str] = []
    current: list[str] | None = None
    for line in _doc_text().splitlines():
        if current is None:
            if line.strip().startswith("```bash"):
                current = []
            continue
        if line.strip() == "```":
            blocks.append("\n".join(current))
            current = None
            continue
        current.append(line)
    return blocks


class DocPresenceTests(unittest.TestCase):
    def test_doc_exists(self) -> None:
        self.assertTrue(os.path.isfile(DOC_PATH), f"missing {DOC_PATH}")

    def test_the_audit_actually_finds_command_blocks(self) -> None:
        """Guard against the fence parser silently matching nothing — the
        failure mode that turns this whole file into a green no-op."""
        blocks = _bash_blocks()
        self.assertGreaterEqual(
            len(blocks), 5,
            "found almost no ```bash blocks in TESTER_ONBOARDING.md — the "
            "fence parser has stopped matching and this file is no longer "
            "auditing anything",
        )
        joined = "\n".join(blocks)
        self.assertIn("pip install -r requirements.txt", joined)


class VirtualenvStepTests(unittest.TestCase):
    """Issue #14 — the install step must create a venv before installing."""

    def test_a_virtualenv_is_created(self) -> None:
        joined = "\n".join(_bash_blocks())
        self.assertIn(
            "python3 -m venv .venv", joined,
            "TESTER_ONBOARDING.md must tell a tester to create .venv — both "
            "run_mcp.sh and scripts/grove-serve-run resolve ./.venv/bin/python3 "
            "before falling back to the system interpreter, and a global "
            "install collides with the distro PyJWT on Debian (#14).",
        )

    def test_the_venv_comes_before_the_install(self) -> None:
        """Order is the whole point. A venv created afterwards is a venv
        with nothing in it, and the collision has already happened."""
        joined = "\n".join(_bash_blocks())
        venv_at = joined.find("python3 -m venv .venv")
        install_at = joined.find("pip install -r requirements.txt")
        self.assertNotEqual(venv_at, -1)
        self.assertNotEqual(install_at, -1)
        self.assertLess(
            venv_at, install_at,
            "the venv must be created BEFORE `pip install -r requirements.txt`",
        )


class DocumentedFilesExistTests(unittest.TestCase):
    """Every file the doc tells a tester to run is on disk.

    `python3 app.py` sat in step 5 pointing at a file that has never
    existed in this repository.
    """

    def _referenced(self) -> set[str]:
        text = _doc_text()
        refs = {f"{d}/{name}" for d, name in _SCRIPT_RE.findall(text)}
        refs |= {m.lstrip("./") for m in _FILE_RE.findall(text)}
        # Documentation links, not things a tester runs.
        return {r for r in refs if not r.endswith(".md")}

    def test_the_audit_actually_finds_references(self) -> None:
        refs = self._referenced()
        self.assertTrue(
            refs, "found no runnable file references in TESTER_ONBOARDING.md — "
            "the pattern has stopped matching",
        )
        self.assertIn("scripts/grove-serve-run", refs)
        self.assertIn("schema.sql", refs)

    def test_every_referenced_file_exists(self) -> None:
        missing = sorted(
            ref for ref in self._referenced()
            if not os.path.exists(os.path.join(ROOT, ref))
        )
        self.assertEqual(
            missing, [],
            f"TESTER_ONBOARDING.md names files that are not on disk: {missing}",
        )


class ShellCommandsAreExecutableTests(unittest.TestCase):
    """No curly quotes inside a shell command.

    A duplicated sanity-check section carried `psql -d “$WILLOW_PG_DB”`.
    Curly quotes are ordinary characters to the shell, so the command
    fails outright — and it failed only in the first of two otherwise
    identical blocks, which is exactly the kind of thing a reader
    assumes is their own typo.
    """

    def test_no_smart_quotes_in_bash_blocks(self) -> None:
        offenders = [
            line.strip()
            for block in _bash_blocks()
            for line in block.splitlines()
            if any(ch in line for ch in _SMART_QUOTES)
        ]
        self.assertEqual(
            offenders, [],
            "curly quotes inside a shell command do not quote anything — "
            f"the command fails as written: {offenders}",
        )

    def test_no_duplicated_section_headings(self) -> None:
        """The two identical sanity-check sections are how the broken copy
        survived: a reader who hit the failure scrolled on and found one
        that worked, and never reported it."""
        headings = [
            ln.strip() for ln in _doc_text().splitlines() if ln.startswith("## ")
        ]
        duplicates = sorted({h for h in headings if headings.count(h) > 1})
        self.assertEqual(
            duplicates, [], f"duplicated section headings: {duplicates}",
        )


if __name__ == "__main__":
    unittest.main()
