"""tests/test_chat_composer.py — composer colon → mod command."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from panes.chat import ComposerInput


def test_composer_does_not_consume_colon():
    inp = ComposerInput()
    assert inp.check_consume_key("colon", ":") is False
    assert inp.check_consume_key("a", "a") is True


def test_command_input_does_not_consume_escape():
    from panes.chat import CommandInput

    inp = CommandInput()
    assert inp.check_consume_key("escape", None) is False
