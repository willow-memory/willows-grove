# b17: GRTBT ΔΣ=42
"""The act's narrator (box-build R12, R21; SPEC-documented §13 J7; C14-C16;
rival T13; W3b audit B5, S1, S2, S3, S4 and the N-probes). Every model here is
a deterministic fake: honest, lying, misattributing, inventing a fact, citing
an unserved row, quoting, refusing (ESCALATE), unreachable. No model is
reachable in this container and none is asked."""

from __future__ import annotations

import json

import pytest

from grove import table_boxes as tb
from grove.seat_boxes import Box, lore_box

TID = "a" * 64
SERVED = {
    "state": "populated",
    "why": "",
    "tables": [
        {
            "id": TID,
            "trust": "human-sealed",
            "rows": [
                {
                    "what": "verdict",
                    "where": "s1",
                    "session": "s",
                    "turn": 0,
                    "total": 11,
                    "verdict": "strong",
                    "reason": "2d6+3 = 11: 10+",
                },
                {
                    "what": "verdict",
                    "where": "s1",
                    "session": "s",
                    "turn": 1,
                    "total": 9,
                    "verdict": "weak",
                    "reason": "2d6+2 = 9: 7-9",
                },
                {
                    "what": "lore",
                    "where": "The Vale",
                    "fact": "The ferryman takes only salt.",
                },
                {
                    "what": "verdict",
                    "where": "s1",
                    "session": "s",
                    "fact_id": "s1::b3",
                    "verdict": "decision",
                    "reason": "a decision beat: the human seals it",
                },
                {"what": "seal", "who": "human", "subject": "proposal:" + "ab" * 32},
                {
                    "what": "verdict",
                    "where": "s1",
                    "session": "s",
                    "verdict": "escalate",
                    "reason": "off_menu: the model's pick was refused; code took act:Grit",
                    "pick": "act:Fly",
                    "took": "act:Grit",
                },
            ],
        }
    ],
}
R0, R1, L2 = f"{TID}_0", f"{TID}_1", f"{TID}_2"
GOOD = (
    f"You rolled 11 on turn 0, strong [{R0}], and 9 on turn 1, weak [{R1}]; "
    f"the ferryman takes only salt [{L2}]."
)
ROWS = [
    {
        "n": 3,
        "kind": "verdict",
        "what": "roll",
        "where": "s1",
        "scene": "s1",
        "beat": "b1",
        "session": "s",
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
        "session": "s",
        "turn": 1,
        "total": 6,
        "verdict": "miss",
        "reason": "2d6+1 = 6: 6-",
    },
    {
        "n": 7,
        "kind": "lore",
        "who": "desk",
        "where": "The Vale",
        "fact": "The ferryman takes only salt.",
        "proposal": "proposal:" + "cd" * 32,
    },
    {
        "n": 8,
        "kind": "lore",
        "who": "ratatosk",
        "where": "The Vale",
        "fact": "The ferryman is a dragon.",
        "proposal": "proposal:" + "00" * 32,
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
]


def boxes():
    return tb.served_boxes(SERVED)


def fake(text):
    def say(prompt):
        say.prompt = prompt
        return text

    return say


# ── the boxes ────────────────────────────────────────────────────────────────
def test_served_rows_become_boxes_with_served_ids_and_only_facts_are_facts():
    bs = boxes()
    assert [(b.id, b.label, b.kind) for b in bs] == [
        (R0, "roll", "pass"),
        (R1, "roll", "pass"),
        (L2, "lore", "pass"),
        (f"{TID}_3", "decision", "you"),
        (f"{TID}_4", "seal", "dec"),
        (f"{TID}_5", "escalate", "block"),
    ]
    assert [b.value for b in bs[:2]] == [
        "turn 0 rolled 11, strong",
        "turn 1 rolled 9, weak",
    ]
    assert [b.id for b in tb.facts(bs)] == [R0, R1, L2]
    assert [b.label for b in tb.shown(bs)] == ["decision", "seal", "escalate"]
    assert all(b.role == "" for b in bs)  # S1: no governance role; the kind tells
    for state in ("empty", "unreachable"):
        (b,) = tb.served_boxes({"state": state, "why": "nothing"})
        assert b.state == state and b.value.startswith(state) and not tb.is_fact(b)


def test_S4_the_escalate_box_never_shows_model_text():
    (b,) = [x for x in boxes() if x.label == "escalate"]
    assert b.value == tb.REFUSED and b.detail == "code took act:Grit"
    assert "Fly" not in f"{b.value} {b.detail}"


def test_S3_record_rows_are_code_only_and_raw_lore_needs_the_hosts_servable():
    bs = tb.scene_boxes(ROWS)
    assert [b.label for b in bs] == [
        "scene",
        "roll",
        "roll",
        "decision",
    ]  # no lore without servable
    assert all(b.role == tb.RECORD for b in bs if b.kind == "pass")
    assert tb.facts(bs) == [] and [b.id for b in tb.sayable(bs)] == ["r3s", "r3", "r5"]
    r = tb.narrate(bs, say=lambda p: (_ for _ in ()).throw(AssertionError("asked")))
    assert r["source"] == "code" and r["why"] == "no served fact box: code only"
    assert (
        r["code"]
        == "Scene s1 [r3s]. Turn 0 rolled 11, strong [r3]. Turn 1 rolled 6, miss [r5]."
    )
    # with the host's servable: the sealed lore row is a record box, the forged one is not
    bs = tb.scene_boxes(ROWS, servable=lambda row: row.get("who") == "desk")
    assert [b.value for b in bs if b.label == "lore"] == [
        "The ferryman takes only salt."
    ]
    assert not any("dragon" in b.value for b in bs)


def test_N9_a_lore_row_is_a_box_said_word_for_word():
    b = lore_box(
        {"fact": "The  miller counts\nnine stones.", "where": "The Mill"}, "r2"
    )
    assert b == Box(
        "r2", "pass", "lore", "The miller counts nine stones.", "of The Mill"
    )
    assert lore_box({"where": "x"}, "r3").state == "empty"
    assert tb.narrate([b])["code"] == "The miller counts nine stones [r2]."


def test_the_code_sentence_cites_every_fact_box_and_passes_its_own_checks():
    r = tb.narrate(boxes())
    assert r["source"] == "code" and r["why"] == "no model asked"
    assert r["code"] == (
        f"Turn 0 rolled 11, strong [{R0}]. Turn 1 rolled 9, weak [{R1}]. "
        f"The ferryman takes only salt [{L2}]."
    )
    assert tb.table_checks(r["code"], tb.facts(boxes())) == [True] * 6
    assert [b.label for b in r["shown"]] == ["decision", "seal", "escalate"]


# ── the model: honest and otherwise ──────────────────────────────────────────
def test_an_honest_rewrite_passes_all_checks_and_stands():
    say = fake(GOOD)
    r = tb.narrate(boxes(), "what happened?", say=say)
    assert r["source"] == "model" and r["sentence"] == GOOD and not r["struck"]
    assert r["checks"] == [True] * 6
    for tag in (f"[{TID}_3]", f"[{TID}_4]", f"[{TID}_5]"):
        assert tag not in say.prompt  # C16: shown boxes are never served to the model
    assert "seal" not in say.prompt.lower() and "refused" not in say.prompt.lower()


def test_T13_an_invented_roll_is_struck_and_code_stands():
    lying = GOOD.replace("rolled 11", "rolled 12")
    r = tb.narrate(boxes(), say=fake(lying))
    assert r["struck"] and r["source"] == "code" and r["sentence"] == r["code"]
    assert r["checks"][2] is False and "nothing the boxes lack" in r["why"]


def test_B5_misattributed_rolls_are_struck_per_clause():
    """Every number is some box's, so check 3 passes; the per-clause check
    sees 9/weak said of the box that holds 11/strong."""
    swapped = (
        f"You rolled 9 on turn 0, weak [{R0}], and 11 on turn 1, strong [{R1}]; "
        f"the ferryman takes only salt [{L2}]."
    )
    r = tb.narrate(boxes(), say=fake(swapped))
    assert r["checks"][2] is True and r["checks"][4] is False
    assert (
        r["struck"] and r["source"] == "code" and "each clause from its box" in r["why"]
    )


def test_B5_a_verdict_word_or_number_outside_any_clause_is_struck():
    r = tb.narrate(boxes(), say=fake(GOOD + " Strong."))
    assert r["struck"] and r["checks"][4] is False
    r = tb.narrate(boxes(), say=fake(GOOD[:-1] + ", and 11."))
    assert r["struck"] and r["checks"][4] is False
    # a verdict word in the clause of the box that holds it passes
    assert tb.check_clauses(
        f"strong on turn 0 [{R0}], weak on turn 1 [{R1}]", tb.facts(boxes())
    )


def test_B5_quotes_are_banned_in_table_narration():
    human = "did the human approve the decision, and was turn 1 a strong hit?"
    lie = (
        f'You rolled 11 on turn 0, strong [{R0}], and 9 on turn 1, "a strong hit" [{R1}]; '
        f'the ferryman takes only salt [{L2}], and "the human approve the decision".'
    )
    r = tb.narrate(boxes(), human, say=fake(lie))
    assert r["struck"] and r["checks"][3] is False and "no quotes" in r["why"]
    r = tb.narrate(
        boxes(), human, say=fake(GOOD[:-1] + ' and "was turn 1" [' + R1 + "].")
    )
    assert r["struck"] and r["checks"][3] is False  # even an exact human quote


def test_T13_a_word_the_boxes_lack_is_struck():
    r = tb.narrate(boxes(), say=fake(GOOD.replace("strong", "strong and bleeding")))
    assert r["struck"] and r["checks"][2] is False


def test_training_lore_is_struck():
    r = tb.narrate(boxes(), say=fake(GOOD + f" The palantír glows [{L2}]."))
    assert r["struck"] and r["checks"][2] is False and r["source"] == "code"


def test_a_cite_to_an_unserved_row_is_struck():
    r = tb.narrate(boxes(), say=fake(GOOD.replace(f"[{L2}]", f"[{L2}] [r99]")))
    assert r["struck"] and r["checks"][0] is False


def test_a_box_left_uncited_is_struck():
    r = tb.narrate(boxes(), say=fake(GOOD.replace(f" [{R1}]", "")))
    assert r["struck"] and r["checks"][1] is False


def test_fleet_noun_is_struck_including_plurals_and_possessives():
    for bad in (
        "Willow rolled",
        "Willows rolled",
        "Willow's rolled",
        "Nestors rolled",
        "Jeles rolled",
    ):
        r = tb.narrate(boxes(), say=fake(GOOD.replace("You rolled", bad)))
        assert r["struck"] and r["checks"][5] is False, bad
    assert tb.check_no_fleet_noun("the grove hums") is False
    assert tb.check_no_fleet_noun("a grovel") is True  # whole words only


def test_fleet_noun_the_world_itself_holds_is_exempt_but_not_its_plural():
    doc = {
        "state": "populated",
        "why": "",
        "tables": [
            {
                "id": "b" * 64,
                "trust": "human-sealed",
                "rows": [
                    {
                        "what": "verdict",
                        "where": "s1",
                        "turn": 0,
                        "total": 11,
                        "verdict": "strong",
                    },
                    {
                        "what": "lore",
                        "where": "The Vale",
                        "fact": "A willow leans over the ford.",
                    },
                ],
            }
        ],
    }
    bs = tb.served_boxes(doc)
    code = tb.narrate(bs)["code"]
    assert "willow" in code.lower()  # the world's own word, said by code
    r = tb.narrate(bs, say=fake(code))
    assert r["source"] == "model" and r["checks"][5] is True  # exempt: the box holds it
    r = tb.narrate(bs, say=fake(code.replace("A willow leans", "Willows lean")))
    assert r["struck"] and r["checks"][5] is False


def test_C16_a_narrated_seal_state_is_struck_by_the_vocabulary_and_the_cites():
    for tail in (f" The fact is sealed [{L2}].", f" Sealed by the human [{R0}]."):
        r = tb.narrate(boxes(), say=fake(GOOD + tail))
        assert r["struck"] and r["checks"][2] is False, tail
    r = tb.narrate(boxes(), say=fake(GOOD + f" Sealed [{TID}_4]."))
    assert r["struck"] and r["checks"][0] is False  # the seal box was never served
    r = tb.narrate(boxes(), say=fake(GOOD + f" The pick was refused [{TID}_5]."))
    assert r["struck"] and r["checks"][0] is False


def test_S2_earlier_is_filtered_through_facts_and_the_prompt_sees_the_same_set():
    bs = boxes()
    draft = Box(
        "draft",
        "pr",
        "set piece",
        "Gerald slides a napkin under the grille.",
        tb.DRAFT_DETAIL,
        role=tb.DRAFT,
    )
    gov = tb.shown(bs)
    prior = Box("p1", "pass", "roll", "turn 9 rolled 4, miss", "2d6+1 = 4: 6-")
    say = fake(
        GOOD[:-1] + ", and Gerald slides a napkin under the grille [draft], "
        f"decision waits on you [{TID}_3]."
    )
    r = tb.narrate(bs, say=say, earlier=[draft, *gov, prior])
    assert r["struck"] and r["checks"][0] is False  # draft and governance: never served
    assert "[draft]" not in say.prompt and f"[{TID}_3]" not in say.prompt
    assert "[p1]" in say.prompt  # the earlier fact box is in the prompt and the checks
    r = tb.narrate(
        bs, say=fake(GOOD[:-1] + ", and turn 9 rolled 4, miss [p1]."), earlier=[prior]
    )
    assert r["source"] == "model"
    r = tb.narrate(
        bs, say=fake(GOOD[:-1] + ", and turn 9 rolled 5, miss [p1]."), earlier=[prior]
    )
    assert r["struck"] and r["checks"][2] is False


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
        assert all(tb.is_fact(b) for b in fb)  # the draft sees fact boxes only
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


# ── round 3: R21 refined (value only, exact words), NIT-1, NIT-2, NIT-3 ───────
XDOC = {
    "state": "populated",
    "why": "",
    "tables": [
        {
            "id": "T1",
            "trust": "human-sealed",
            "rows": [
                {
                    "what": "verdict",
                    "verdict": "strong",
                    "turn": 0,
                    "total": 11,
                    "reason": "2d6+3 = 11: 10+",
                    "beat": "b1",
                    "session": "A",
                },
                {
                    "what": "verdict",
                    "verdict": "miss",
                    "turn": 1,
                    "total": 6,
                    "reason": "2d6+1 = 6: 6-",
                    "beat": "b2",
                    "session": "A",
                },
                {
                    "what": "lore",
                    "where": "The Vale",
                    "fact": "A clean hit takes nine coins from the ferryman.",
                },
            ],
        }
    ],
}
XGOOD = (
    "Turn 0 rolled 11, strong [T1_0]. Turn 1 rolled 6, miss [T1_1]. "
    "A clean hit takes nine coins from the ferryman [T1_2]."
)


def xnar(sentence):
    return tb.narrate(tb.served_boxes(XDOC), say=lambda p: sentence)


def test_the_honest_sentence_over_the_x_doc_stands():
    r = xnar(XGOOD)
    assert r["source"] == "model" and r["checks"] == [True] * 6
    r = xnar(
        "Looks like turn 0 rolled 11, strong [T1_0], and turn 1 rolled 6, miss [T1_1]; "
        "a clean hit takes nine coins from the ferryman [T1_2]."
    )
    assert r["source"] == "model"


@pytest.mark.parametrize(
    "lie",
    [
        # NEW-1: in-box number swaps (rows 1-3)
        XGOOD.replace("rolled 11, strong", "rolled 6, strong"),
        XGOOD.replace("rolled 11, strong", "rolled 1, strong"),
        XGOOD.replace("Turn 0 rolled 11", "Turn 11 rolled 0"),
        XGOOD.replace("rolled 11", "rolled 3"),
        XGOOD.replace("rolled 11", "rolled 10"),
        # NEW-2: spelled number, verdict synonym, inflection (rows 4-6)
        XGOOD.replace("rolled 11", "rolled nine"),
        XGOOD.replace("rolled 6, miss", "rolled 6, a clean hit"),
        XGOOD.replace("rolled 11, strong", "rolled 11 and missed"),
        XGOOD.replace("rolled 6, miss", "rolled 6, missing nothing"),
        # a detail word is code's, never a model clause's
        XGOOD.replace("rolled 11, strong", "rolled 11, strong, 2d6+3"),
        XGOOD.replace("rolled 11, strong", "rolled 11, strong on beat b1"),
        # a verdict word moved to a lore clause that holds none
        "Turn 0 rolled 11 [T1_0]. Turn 1 rolled 6 [T1_1]. A clean hit takes nine coins, strong [T1_2].",
        # a word from another box in this clause
        XGOOD.replace("rolled 6, miss", "rolled 6, miss, the ferryman"),
        # fleet nouns
        "Willow says " + XGOOD[0].lower() + XGOOD[1:],
        XGOOD[:-1] + ", safely.",
    ],
)
def test_R21_a_clause_says_only_its_own_box_value(lie):
    r = xnar(lie)
    assert r["struck"] and r["source"] == "code", lie


@pytest.mark.parametrize(
    "lie",
    [
        # NIT-2: two cites one clause / cite first / no cites
        "Turn 0 rolled 11, strong [T1_0] [T1_1]. A clean hit takes nine coins from the ferryman [T1_2].",
        "[T1_0] Turn 0 rolled 11, strong, turn 1 rolled 6, miss [T1_1]. "
        "A clean hit takes nine coins from the ferryman [T1_2].",
        "Turn 0 rolled 11, strong. Turn 1 rolled 6, miss.",
    ],
)
def test_NIT2_every_cite_needs_its_own_clause(lie):
    r = xnar(lie)
    assert r["struck"] and r["source"] == "code", lie


@pytest.mark.parametrize(
    "lie",
    [
        XGOOD.replace("strong", "«strong»"),
        XGOOD.replace("strong", "`strong`").replace("miss", "‘miss’"),
        XGOOD.replace("strong", "″strong″"),
        XGOOD.replace("strong", "'strong'"),
        XGOOD.replace("strong", "“strong”"),
    ],
)
def test_NIT1_every_quote_mark_is_banned(lie):
    r = xnar(lie)
    assert r["struck"] and r["checks"][3] is False, lie


def test_NIT1_an_apostrophe_inside_a_word_is_not_a_quote():
    assert tb.check_no_quotes("the ferryman's coins and don’t") is True
    assert tb.check_no_quotes("the 'coins'") is False
    assert tb.check_no_quotes("coins ' and") is False


def test_NIT3_served_boxes_skips_unpopulated_or_untrusted_tables():
    doc = {
        "state": "populated",
        "why": "",
        "tables": [
            {
                "id": "x",
                "trust": "untrusted",
                "state": "unreachable",
                "rows": [
                    {"what": "lore", "fact": "The ferryman is a dragon.", "where": "V"}
                ],
            },
            {
                "id": "y",
                "trust": "untrusted",
                "rows": [
                    {"what": "lore", "fact": "The ferryman is a troll.", "where": "V"}
                ],
            },
            {
                "id": "z",
                "trust": "human-sealed",
                "state": "unreachable",
                "rows": [
                    {"what": "lore", "fact": "The ferryman is a ghost.", "where": "V"}
                ],
            },
            {
                "id": "w",
                "trust": "human-sealed",
                "rows": [
                    {
                        "what": "lore",
                        "fact": "The ferryman takes only salt.",
                        "where": "V",
                    }
                ],
            },
        ],
    }
    assert [b.value for b in tb.facts(tb.served_boxes(doc))] == [
        "The ferryman takes only salt."
    ]


def test_record_boxes_never_reach_a_model_even_as_earlier_or_a_set_piece():
    rows = [
        {
            "n": 3,
            "kind": "verdict",
            "what": "roll",
            "where": "s1",
            "scene": "s1",
            "turn": 0,
            "total": 11,
            "verdict": "strong",
            "reason": "r",
        },
        {"n": 4, "kind": "lore", "where": "V", "fact": "unsealed dragon."},
    ]
    bx = tb.scene_boxes(rows, servable=lambda r: True)
    asked = []
    tb.narrate(bx, say=lambda p: asked.append(p) or "x")
    tb.narrate(tb.served_boxes(XDOC), say=lambda p: asked.append(p) or "x", earlier=bx)
    tb.set_piece_draft(
        lambda p, f: asked.append(repr([b.id for b in f])) or [], bx, "p"
    )
    assert not any("dragon" in a or "r3" in a for a in asked)


# ── round 4: R21b (H1 negators, H2 lore word for word, H4 total or verdict) ──
def xdoc(lore):
    d = json.loads(json.dumps(XDOC))
    d["tables"][0]["rows"][2]["fact"] = lore
    return d


def xnar2(sentence, lore=None):
    bx = tb.served_boxes(xdoc(lore) if lore else XDOC)
    return tb.narrate(bx, say=lambda p: sentence)


G1 = "Turn 1 rolled 6, miss [T1_1]."
LC = " A clean hit takes nine coins from the ferryman [T1_2]."


@pytest.mark.parametrize(
    "honest",
    [
        "Turn 0 rolled 11, strong [T1_0]. " + G1 + LC,
        "Rolled 11 on turn 0, strong [T1_0]. " + G1 + LC,
        "On turn 0 you rolled 11, strong [T1_0]. " + G1 + LC,
        "Turn 0 rolled 11, it's strong [T1_0]. " + G1 + LC,
        "Turn 0 rolled 11, strong, turn 0 [T1_0]. " + G1 + LC,
    ],
)
def test_R21b_honest_roll_clauses_still_stand(honest):
    assert xnar2(honest)["source"] == "model", honest


def test_R21b_honest_lore_with_digits_stands_word_for_word():
    lore = "The toll is 3 coins and 12 salt."
    r = xnar2(
        "Turn 0 rolled 11, strong [T1_0]. "
        + G1
        + " The toll is 3 coins and 12 salt [T1_2].",
        lore,
    )
    assert r["source"] == "model"
    r = xnar2(
        "Turn 0 rolled 11, strong [T1_0]. "
        + G1
        + "; the toll is 3 coins and 12 salt [T1_2].",
        lore,
    )
    assert r["source"] == "model"  # punctuation and case are not words


@pytest.mark.parametrize(
    "lie",
    [
        "Turn 0 rolled 11, not strong [T1_0]. " + G1 + LC,
        "Turn 0 rolled 11, strong [T1_0]. Turn 1 rolled 6, not miss [T1_1]." + LC,
        "Turn 0 rolled 11, strong [T1_0]. Turn 1 rolled 6, no miss [T1_1]." + LC,
        "Turn 0 rolled 11, but still strong [T1_0]. Turn 1 rolled 6, yet miss [T1_1]."
        + LC,
        "Turn 0 rolled 11, never strong [T1_0]. " + G1 + LC,
        "Turn 0 rolled 11, strong [T1_0]. " + G1 + LC[:-1] + ", not.",
        "Turn 0 didn't roll 11 [T1_0]. " + G1 + LC,
        "Turn 0's roll: 11, strong [T1_0]. " + G1 + LC,
    ],
)
def test_R21b_H1_negators_and_hedges_are_never_free(lie):
    r = xnar2(lie)
    assert r["struck"] and r["source"] == "code", lie


@pytest.mark.parametrize(
    "lore, clause",
    [
        ("The toll is 3 coins and 12 salt.", "The toll is 12 coins and 3 salt [T1_2]."),
        ("The toll is 3 coins and 12 salt.", "The toll is 3 coins and 3 salt [T1_2]."),
        ("The ferryman takes no salt.", "The ferryman takes salt [T1_2]."),
        ("The ferryman takes salt.", "The ferryman takes not salt [T1_2]."),
        ("The ferryman takes salt.", "Salt takes the ferryman [T1_2]."),
        ("The ferryman takes salt.", "Looks like the ferryman takes salt [T1_2]."),
        ("The ferryman takes salt.", "The ferryman [T1_2]."),
    ],
)
def test_R21b_H2_a_lore_clause_is_the_boxs_exact_value_or_struck(lore, clause):
    r = xnar2("Turn 0 rolled 11, strong [T1_0]. " + G1 + " " + clause, lore)
    assert r["struck"] and r["source"] == "code", clause
    assert r["checks"][4] is False


def test_R21b_H4_a_roll_clause_says_the_total_or_the_verdict():
    r = xnar2("Turn [T1_0]. " + G1 + LC)
    assert r["struck"] and r["checks"][4] is False
    r = xnar2("Turn 0 [T1_0]. " + G1 + LC)
    assert r["struck"] and r["checks"][4] is False
    assert xnar2("Strong [T1_0]. " + G1 + LC)["source"] == "model"
    assert xnar2("Rolled 11 [T1_0]. " + G1 + LC)["source"] == "model"


def test_R21b_lore_digit_as_a_turn_is_struck():
    r = xnar2(
        "Turn 3 rolled 11, strong [T1_0]. "
        + G1
        + " The toll is 3 coins and 12 salt [T1_2].",
        "The toll is 3 coins and 12 salt.",
    )
    assert r["struck"]


@pytest.mark.parametrize(
    "t, n",
    [
        ({"trust": "human-sealed"}, 1),
        ({"trust": "untrusted"}, 0),
        ({}, 0),
        ({"trust": "Human-Sealed"}, 0),
        ({"trust": "human-sealed", "state": "unreachable"}, 0),
        ({"trust": "human-sealed", "state": "empty"}, 0),
    ],
)
def test_NIT3_every_trust_and_state_shape(t, n):
    d = {
        "state": "populated",
        "tables": [
            {"id": "T", **t, "rows": [{"what": "lore", "where": "V", "fact": "x y."}]}
        ],
    }
    assert len(tb.facts(tb.served_boxes(d))) == n
