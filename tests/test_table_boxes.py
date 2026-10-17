# b17: GRTBT ΔΣ=42
"""The act's narrator (box-build R12; SPEC-documented §13 J7; C14-C16; rival
T13). Every model here is a deterministic fake: honest, lying, inventing a
fact, citing an unserved row, refusing (ESCALATE), unreachable. No model is
reachable in this container and none is asked."""

from __future__ import annotations

import pytest

from grove import table_boxes as tb
from grove.seat_boxes import Box, lore_box

ROWS = [
    {"n": 1, "kind": "verdict", "what": "open", "verdict": "open", "where": None},
    {
        "n": 3,
        "kind": "verdict",
        "what": "roll",
        "where": "s1",
        "scene": "s1",
        "beat": "b1",
        "turn": 0,
        "total": 11,
        "verdict": "strong",
        "reason": "2d6+3 = 11: 10+",
    },
    {
        "n": 5,
        "kind": "verdict",
        "what": "roll",
        "where": "s1",
        "scene": "s1",
        "beat": "b2",
        "turn": 1,
        "total": 9,
        "verdict": "weak",
        "reason": "2d6+2 = 9: 7-9",
    },
    {
        "n": 7,
        "kind": "lore",
        "where": "The Vale",
        "fact": "The ferryman takes only salt.",
    },
    {
        "n": 9,
        "kind": "verdict",
        "what": "decision",
        "where": "s1",
        "fact_id": "s1::b3",
        "verdict": "decision",
        "reason": "a decision beat: the human seals it",
    },
    {"n": 11, "kind": "seal", "who": "human", "subject": "proposal:" + "ab" * 32},
]
GOOD = (
    "Scene s1 [r3s]: you rolled 11 on turn 0, strong [r3], and 9 on turn 1, "
    "weak [r5]; the ferryman takes only salt [r7]."
)


def boxes():
    return tb.scene_boxes(ROWS)


def fake(text):
    def say(prompt):
        say.prompt = prompt
        return text

    return say


# ── the boxes ────────────────────────────────────────────────────────────────
def test_roll_scene_and_lore_rows_become_boxes_with_the_rows_own_ids():
    bs = boxes()
    assert [(b.id, b.label) for b in bs] == [
        ("r3s", "scene"),
        ("r3", "roll"),
        ("r5", "roll"),
        ("r7", "lore"),
        ("r9", "decision"),
        ("r11", "seal"),
    ]
    assert [b.value for b in bs[1:3]] == [
        "turn 0 rolled 11, strong",
        "turn 1 rolled 9, weak",
    ]
    assert [b.id for b in tb.facts(bs)] == ["r3s", "r3", "r5", "r7"]
    assert [b.id for b in tb.shown(bs)] == ["r9", "r11"]
    assert all(b.role == tb.GOVERNANCE for b in tb.shown(bs))


def test_N9_a_lore_row_is_a_box_said_word_for_word():
    b = lore_box(
        {"fact": "The  miller counts\nnine stones.", "where": "The Mill"}, "r2"
    )
    assert b == Box(
        "r2", "pass", "lore", "The miller counts nine stones.", "of The Mill"
    )
    assert lore_box({"where": "x"}, "r3").state == "empty"
    assert tb.narrate([b])["code"] == "The miller counts nine stones [r2]."


def test_served_boxes_cite_served_ids():
    doc = {
        "state": "populated",
        "why": "",
        "tables": [
            {
                "id": "a" * 64,
                "rows": [
                    {
                        "what": "verdict",
                        "where": "s1",
                        "turn": 0,
                        "total": 11,
                        "verdict": "strong",
                    },
                    {"what": "lore", "where": "The Vale", "fact": "Salt."},
                ],
            }
        ],
    }
    bs = tb.served_boxes(doc)
    assert [b.id for b in bs] == ["a" * 64 + ".0", "a" * 64 + ".1"]
    assert all(b.id.startswith(doc["tables"][0]["id"]) for b in bs)
    for state in ("empty", "unreachable"):
        (b,) = tb.served_boxes({"state": state, "why": "nothing"})
        assert b.state == state and b.value.startswith(state)


def test_the_code_sentence_cites_every_fact_box_and_passes_its_own_checks():
    r = tb.narrate(boxes())
    assert r["source"] == "code" and r["why"] == "no model asked"
    assert r["code"] == (
        "Scene s1 [r3s]. Turn 0 rolled 11, strong [r3]. Turn 1 rolled 9, weak [r5]. "
        "The ferryman takes only salt [r7]."
    )
    assert tb.table_checks(r["code"], tb.facts(boxes())) == [
        True,
        True,
        True,
        "na",
        True,
        True,
    ]
    assert [b.id for b in r["shown"]] == ["r9", "r11"]


# ── the model: honest and otherwise ──────────────────────────────────────────
def test_an_honest_rewrite_passes_all_checks_and_stands():
    say = fake(GOOD)
    r = tb.narrate(boxes(), "what happened?", say=say)
    assert r["source"] == "model" and r["sentence"] == GOOD and not r["struck"]
    assert r["checks"] == [True, True, True, "na", True, True]
    assert (
        "[r9]" not in say.prompt and "[r11]" not in say.prompt
    )  # C16: never served to it
    assert "seal" not in say.prompt.lower()


def test_T13_an_invented_roll_is_struck_and_code_stands():
    lying = GOOD.replace("rolled 11", "rolled 12")
    r = tb.narrate(boxes(), say=fake(lying))
    assert r["struck"] and r["source"] == "code" and r["sentence"] == r["code"]
    assert r["checks"][2] is False and r["why"] == "struck: nothing the boxes lack"


def test_T13_a_word_the_boxes_lack_is_struck():
    r = tb.narrate(boxes(), say=fake(GOOD.replace("strong", "strong and bleeding")))
    assert r["struck"] and r["checks"][2] is False


def test_training_lore_is_struck():
    r = tb.narrate(boxes(), say=fake(GOOD + " The palantír glows [r7]."))
    assert r["struck"] and r["checks"][2] is False and r["source"] == "code"


def test_a_cite_to_an_unserved_row_is_struck():
    r = tb.narrate(boxes(), say=fake(GOOD.replace("[r7]", "[r7] [r99]")))
    assert r["struck"] and r["checks"][0] is False


def test_a_box_left_uncited_is_struck():
    r = tb.narrate(boxes(), say=fake(GOOD.replace(" [r5]", "")))
    assert r["struck"] and r["checks"][1] is False


def test_fleet_noun_is_struck():
    r = tb.narrate(boxes(), say=fake(GOOD.replace("you rolled", "Willow rolled")))
    assert r["struck"] and r["checks"][4] is False and "no fleet noun" in r["why"]
    assert tb.check_no_fleet_noun("the grove hums") is False
    assert tb.check_no_fleet_noun("a grovel") is True  # whole words only


def test_C16_a_narrated_seal_state_is_refused():
    for tail in (" The fact is sealed [r7].", " Sealed by the human [r3]."):
        r = tb.narrate(boxes(), say=fake(GOOD + tail))
        assert r["struck"] and r["checks"][5] is False, tail
        assert "no seal state narrated" in r["why"] and r["sentence"] == r["code"]
    # even with the seal box handed in, it is shown, never in the vocabulary
    r = tb.narrate(boxes(), say=fake(GOOD + " Sealed [r11]."))
    assert r["struck"] and r["checks"][0] is False  # r11 was never served


def test_a_models_ESCALATE_goes_to_the_human_and_code_stands():
    r = tb.narrate(boxes(), say=fake("ESCALATE: the boxes do not say who rolled"))
    assert r["escalated"] and r["source"] == "code" and not r["struck"]
    assert r["why"] == "the model escalated: the boxes do not say who rolled"
    assert r["checks"] is None


@pytest.mark.parametrize("err", [TimeoutError("ollama down"), ValueError("bad reply")])
def test_an_unreachable_model_falls_back_to_code(err):
    def down(prompt):
        raise err

    r = tb.narrate(boxes(), say=down)
    assert r["source"] == "code" and r["sentence"] == r["code"]
    assert r["why"].startswith("unreachable: " + type(err).__name__)
    assert r["checks"] is None and not r["struck"]


def test_a_silent_model_falls_back_to_code():
    r = tb.narrate(boxes(), say=fake("   "))
    assert r["source"] == "code" and r["why"] == "the model said nothing"


def test_no_fact_box_no_model_call():
    called = []
    r = tb.narrate(tb.shown(boxes()), say=lambda p: called.append(p) or "x")
    assert called == [] and r["sentence"] == "" and r["why"] == "no fact box to say"


# ── the set piece: a draft, never a fact ──────────────────────────────────────
def test_a_set_pieces_flowering_output_is_never_a_fact():
    def flower(prompt, fb):
        assert all(b.role == "" for b in fb)  # the draft sees fact boxes only
        return [
            {
                "path": "draft/scene.md",
                "data": "The lights  flicker.\n",
                "claim": "a scene",
            }
        ]

    d = tb.set_piece_draft(flower, boxes(), "voice the set piece")
    assert (
        d.role == tb.DRAFT
        and d.value == "The lights flicker."
        and d.detail == tb.DRAFT_DETAIL
    )
    assert not tb.is_fact(d)
    bs = [*boxes(), d]
    assert d not in tb.facts(bs) and d in tb.shown(bs)
    r = tb.narrate(bs, say=fake(GOOD + " The lights flicker [draft]."))
    assert (
        r["struck"] and r["checks"][0] is False
    )  # its words are not in the vocabulary
    assert "[draft]" not in r["code"]


def test_a_set_piece_escalate_or_crash_is_an_empty_or_unreachable_draft():
    d = tb.set_piece_draft(
        lambda p, b: [{"path": "ESCALATE", "data": "", "claim": "not mine"}],
        boxes(),
        "x",
    )
    assert d.state == "empty" and d.role == tb.DRAFT and "not mine" in d.value

    def crash(p, b):
        raise OSError("no cloud")

    d = tb.set_piece_draft(crash, boxes(), "x")
    assert d.state == "unreachable" and d.role == tb.DRAFT and "no cloud" in d.value
    d = tb.set_piece_draft(lambda p, b: "not rows", boxes(), "x")
    assert d.state == "empty" and "proposed nothing" in d.value
