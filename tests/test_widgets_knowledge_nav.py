"""tests/test_widgets_knowledge_nav.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from widgets.knowledge_nav import KnowledgeAtomSelected, KnowledgeNav


def test_atom_selected_stores_id():
    msg = KnowledgeAtomSelected(42)
    assert msg.atom_id == 42
    assert msg.title == ""
    assert msg.summary == ""


def test_atom_selected_optional_teaser_fields():
    msg = KnowledgeAtomSelected(7, title="Hello", summary="World")
    assert msg.atom_id == 7
    assert msg.title == "Hello"
    assert msg.summary == "World"


def test_knowledge_nav_constructs():
    nav = KnowledgeNav()
    assert nav._rows == []
    assert nav._cursor == -1
