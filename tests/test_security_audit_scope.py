# tests/test_security_audit_scope.py — SECURITY_AUDIT.md's scope table must be
# a bijection with the tree it claims to audit.
#
# The 2026-05-06 revision claimed "Full" coverage of grove_serve.py and
# kart_worker.py and reported line-specific findings in both. Neither file is in
# this repository. The failure mode is not that someone lied — it is that
# nothing checked. This is the check: a source file nobody classified fails the
# suite, and a row naming a file that does not exist fails the suite.
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
AUDIT = REPO / "SECURITY_AUDIT.md"

# `| `path` | purpose | Coverage |`
ROW = re.compile(r"^\| `([^`]+)` \| (.*?) \| (Reviewed|Scanned|Out of scope — .+?) \|$", re.M)

COVERED_GLOBS = ("*.py", "*.sh")


def _tracked_sources() -> set[str]:
    """Every tracked source file the audit is required to classify."""
    proc = subprocess.run(
        ["git", "ls-files", *COVERED_GLOBS],
        cwd=REPO, capture_output=True, text=True,
    )
    if proc.returncode != 0:  # pragma: no cover - only if git is unavailable
        pytest.skip(f"git ls-files unavailable: {proc.stderr.strip()}")
    return {line for line in proc.stdout.split() if line}


def _scope_rows() -> list[tuple[str, str, str]]:
    return ROW.findall(AUDIT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def rows():
    found = _scope_rows()
    assert found, (
        "SECURITY_AUDIT.md has no parseable scope table. Expected rows shaped "
        "`| `path/to/file.py` | purpose | Reviewed|Scanned|Out of scope — reason |`."
    )
    return found


def test_every_tracked_source_file_appears_in_the_scope_table(rows):
    """A file must not be absent from the table."""
    listed = {path for path, _, _ in rows}
    missing = sorted(_tracked_sources() - listed)
    assert not missing, (
        "These tracked source files are audited by nobody — add a row to the "
        "SECURITY_AUDIT.md scope table marking each Reviewed, Scanned, or "
        f"'Out of scope — <reason>':\n  " + "\n  ".join(missing)
    )


def test_scope_table_names_no_file_that_does_not_exist(rows):
    """The table must not name files that do not exist.

    This is the grove_serve.py / kart_worker.py regression, directly.
    """
    listed = {path for path, _, _ in rows}
    phantom = sorted(p for p in listed if not (REPO / p).is_file())
    assert not phantom, (
        "SECURITY_AUDIT.md claims coverage of files that are not in this "
        "repository:\n  " + "\n  ".join(phantom)
    )


def test_scope_table_only_covers_tracked_sources(rows):
    """Rows must be tracked source files, not untracked or generated ones."""
    listed = {path for path, _, _ in rows}
    untracked = sorted(listed - _tracked_sources())
    assert not untracked, (
        "Scope rows that are not tracked *.py / *.sh files:\n  " + "\n  ".join(untracked)
    )


def test_no_duplicate_scope_rows(rows):
    listed = [path for path, _, _ in rows]
    dupes = sorted({p for p in listed if listed.count(p) > 1})
    assert not dupes, f"duplicated scope rows: {dupes}"


def test_every_row_states_a_purpose(rows):
    blank = sorted(path for path, purpose, _ in rows if not purpose.strip(" —-"))
    assert not blank, f"scope rows with no purpose: {blank}"


def test_out_of_scope_rows_carry_a_reason(rows):
    """'Out of scope' without a reason is how coverage gaps hide."""
    bad = sorted(
        path
        for path, _, coverage in rows
        if coverage.startswith("Out of scope") and len(coverage.split("—", 1)[1].strip()) < 10
    )
    assert not bad, f"out-of-scope rows with no substantive reason: {bad}"


def test_audit_does_not_certify_files_from_another_repo():
    """No finding may point at grove_serve.py or kart_worker.py as if present.

    They may be *named* in the corrections section explaining their withdrawal;
    what is banned is a line-number citation like `grove_serve.py:306`, which is
    what the previous revision reported.
    """
    lines = AUDIT.read_text(encoding="utf-8").splitlines()
    for absent in ("grove_serve.py", "kart_worker.py"):
        assert not (REPO / absent).exists(), (
            f"{absent} now exists — this guard and the audit's corrections "
            "section both need revisiting."
        )
        live = [
            line
            for line in lines
            if re.search(rf"{re.escape(absent)}:\d+", line)
            and "Withdrawn" not in line
        ]
        assert not live, (
            f"SECURITY_AUDIT.md cites line numbers in {absent}, which is not in "
            "this repository, outside a row marked Withdrawn:\n  "
            + "\n  ".join(live)
        )


def test_r5_and_r8_are_not_certified_as_clean():
    """R5 and R8 were the two false PASS/N-A ratings. Pin the corrections.

    R5 claimed serve mode was localhost-only by design; R8 claimed OAuth PKCE
    made the MCP tools auth-gated. Both were contradicted by code in the same
    tree. If either reverts to a bare PASS/N/A, this fails.
    """
    text = AUDIT.read_text(encoding="utf-8")
    rows = {}
    for check in ("R5", "R8"):
        row = re.search(rf"^\| {check} \| (.*?) \| (.*?) \| (.*?) \|$", text, re.M)
        assert row, f"no rubric row for {check} in SECURITY_AUDIT.md"
        rows[check] = (row.group(2), row.group(3))

    for check, (status, finding) in rows.items():
        assert "N/A" not in status, f"{check} must not be rated N/A: {finding!r}"
        if "PASS" in status:
            assert "Corrected" in finding or "was P0" in status, (
                f"{check} is rated {status!r} again with no correction: {finding!r}"
            )

    # The specific withdrawn wording must not come back as an active claim.
    r5_finding = rows["R5"][1]
    assert "not* localhost-only" in r5_finding or "localhost-only by design" not in r5_finding, (
        "R5 asserts 'localhost-only by design' again: " + r5_finding
    )
    r8_finding = rows["R8"][1]
    assert "token-gated" not in r8_finding or "Corrected" in r8_finding, (
        "R8 asserts 'token-gated' again with no correction: " + r8_finding
    )


def test_dns_rebinding_disable_is_still_recorded():
    """The audit's R5 correction must stay true to the code.

    If someone fixes _transport_security, the audit needs updating too — that
    is a good failure, not a bad one. It fired exactly once: on the branch that
    fixed it.

    Checks OPEN-ness, not mere mention. The original assertion was
    `disables == ("G-REBIND-01" in audit)`, which on a fix demands the finding
    be DELETED — contradicting this document's own rule that withdrawn and
    closed items stay recorded, so anyone who acted on the old text can see what
    changed. A finding marked Fixed is the correct end state and has to be a
    passing one.
    """
    sys.path.insert(0, str(REPO))
    source = (REPO / "grove" / "mcp_local.py").read_text(encoding="utf-8")
    audit = AUDIT.read_text(encoding="utf-8")
    disables = "enable_dns_rebinding_protection=False" in source

    assert "### G-REBIND-01" in audit, "the finding must stay recorded either way"
    block = audit[audit.index("### G-REBIND-01"):]
    status = block[block.index("**Status:**"):].splitlines()[0]
    open_finding = status.strip().endswith("Open")

    assert disables == open_finding, (
        "grove/mcp_local.py and SECURITY_AUDIT.md disagree about DNS-rebinding "
        f"protection (code disables={disables}, finding open={open_finding} "
        f"from status line {status!r})."
    )
