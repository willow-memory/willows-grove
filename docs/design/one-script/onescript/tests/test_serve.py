"""serve: only the tables in scope, by ids the model can't guess."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from onescript import gate, serve  # noqa: E402
from onescript.record import Record  # noqa: E402

HUMAN_KEY = b"passkey-in-a-coat-pocket"
SERVE_KEY = b"the-runs-serve-key"

IN = {"rows": [{"who": "hanuman", "what": "write"}], "source": "record.jsonl@n=4"}
ALSO = {"rows": [{"who": "willow", "what": "seal"}], "source": "record.jsonl@n=9"}
OUT = {"rows": [{"who": "operator", "what": "PIN 4471"}], "source": "vault@n=1"}


def clock():
    n = iter(range(10**6))
    return lambda: f"2026-10-07T00:00:{next(n):06d}Z"


def box(tmp_path):
    return Record(tmp_path, clock(), "v", gate.token())


def seal(rec, subject):
    hum = gate.human(subject, gate.sign(HUMAN_KEY, "seal", subject), HUMAN_KEY)
    rec.append("seal", hum, subject=subject)


def scoped(rec, *tables):
    ids = [serve.table_id(t) for t in tables]
    seal(rec, serve.scope_subject(ids))
    return ids


def test_only_the_scope_is_served_and_the_rest_is_never_named(tmp_path):
    rec = box(tmp_path)
    ids = scoped(rec, IN, ALSO)
    doc = serve.serve(rec, [IN, ALSO, OUT], ids, SERVE_KEY)
    assert doc["state"] == "populated"
    assert len(doc["tables"]) == 2
    raw = (tmp_path / serve.OUT).read_text()
    assert "PIN 4471" not in raw and "vault" not in raw
    assert serve.table_id(OUT) not in raw
    assert set(json.loads(raw)) == {"state", "why", "tables"}  # no count of the rest


def test_served_ids_are_keyed_never_the_content_hash(tmp_path):
    rec = box(tmp_path)
    ids = scoped(rec, IN)
    doc = serve.serve(rec, [IN], ids, SERVE_KEY)
    raw = (tmp_path / serve.OUT).read_text()
    assert ids[0] not in raw
    assert doc["tables"][0]["id"] == serve.served_id(SERVE_KEY, ids[0])
    assert doc["tables"][0]["id"] != serve.served_id(b"another-key", ids[0])


def test_no_scope_serves_nothing_and_says_why(tmp_path):
    doc = serve.serve(box(tmp_path), [IN], None, SERVE_KEY)
    assert doc == {"state": "empty", "why": doc["why"], "tables": []}
    assert "no scope" in doc["why"]


def test_an_unsealed_scope_serves_nothing(tmp_path):
    rec = box(tmp_path)
    doc = serve.serve(rec, [IN], [serve.table_id(IN)], SERVE_KEY)
    assert doc["state"] == "empty" and doc["tables"] == []
    assert "no human seal" in doc["why"]


def test_a_seal_binds_to_the_exact_set_never_a_wider_one(tmp_path):
    rec = box(tmp_path)
    scoped(rec, IN)  # sealed {IN}
    wider = [serve.table_id(IN), serve.table_id(OUT)]
    doc = serve.serve(rec, [IN, OUT], wider, SERVE_KEY)
    assert doc["state"] == "empty"
    assert "PIN 4471" not in (tmp_path / serve.OUT).read_text()


def test_a_forged_seal_never_reaches_the_record(tmp_path):
    subject = serve.scope_subject([serve.table_id(IN)])
    try:
        gate.human(subject, gate.sign(b"not-the-key", "seal", subject), HUMAN_KEY)
    except gate.Refused:
        pass
    else:
        raise AssertionError("a forged seal verified")


def test_a_sealed_table_that_is_missing_is_unreachable_not_empty(tmp_path):
    rec = box(tmp_path)
    ids = scoped(rec, IN, ALSO)
    doc = serve.serve(rec, [IN], ids, SERVE_KEY)
    assert doc["state"] == "unreachable" and doc["tables"] == []


def test_trust_comes_from_the_record_not_the_table(tmp_path):
    rec = box(tmp_path)
    ids = scoped(rec, IN, ALSO)
    seal(rec, serve.table_id(ALSO))
    claims = {**IN, "trust": "human-sealed"}  # a table can't label itself
    doc = serve.serve(rec, [claims, ALSO], ids, SERVE_KEY)
    trust = {t["source"]: t["trust"] for t in doc["tables"]}
    assert trust == {IN["source"]: "untrusted", ALSO["source"]: "human-sealed"}


def test_a_table_without_a_receipt_fails_the_whole_serve(tmp_path):
    rec = box(tmp_path)
    ids = scoped(rec, IN)
    doc = serve.serve(rec, [IN, {"rows": [], "source": ""}], ids, SERVE_KEY)
    assert doc["state"] == "empty" and "receipt" in doc["why"]


def test_every_serve_is_recorded_with_where_and_the_file_is_in_the_pile(tmp_path):
    rec = box(tmp_path)
    ids = scoped(rec, IN)
    doc = serve.serve(rec, [IN], ids, SERVE_KEY)
    row = rec.rows()[-1]
    assert row["kind"] == "serve" and row["where"] == serve.OUT
    assert row["served"] == [doc["tables"][0]["id"]]
    assert row["scope"] == serve.scope_subject(ids)
    ptr = {i["where"]: i for i in rec.pile()["items"]}[serve.OUT]
    assert ptr["sha"] == row["sha"] and ptr["provenance"] == "third-party"
    assert rec.verify_chain() == []


def test_a_cite_outside_the_served_file_is_link_fail(tmp_path):
    rec = box(tmp_path)
    ids = scoped(rec, IN)
    doc = serve.serve(rec, [IN], ids, SERVE_KEY)
    good = doc["tables"][0]["id"]
    guessed = serve.served_id(SERVE_KEY, serve.table_id(OUT))
    fails = serve.check_cites(doc, [good, guessed, ids[0]])
    assert [f["cite"] for f in fails] == [guessed, ids[0]]
    assert {f["verdict"] for f in fails} == {"link_fail"}
