"""tests/test_seed_html.py — unit tests for grove.seed_html.
b17: WGRV1  ΔΣ=42

Exercises the two string builders directly (no HTTP): heading + paragraph
rendering, correct anchor hrefs on the index cards, and — the paranoia
test — HTML entities in user-visible strings are escaped so the route
would stay safe if the seed source were ever swapped for something less
trusted than a local file.
"""
from __future__ import annotations

import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


from grove import seed_html  # noqa: E402


def _six_stub(bodies: dict[int, str] | None = None) -> list[dict[str, object]]:
    """Six well-formed movement dicts for the builders to render."""
    default = {
        1: "One.", 2: "Two.", 3: "Three.", 4: "Four.", 5: "Five.", 6: "Six.",
    }
    b = default if bodies is None else {**default, **bodies}
    return [
        {"n": 1, "slug": "the-covenant",   "title": "The Covenant",   "body": b[1]},
        {"n": 2, "slug": "be-the-other",   "title": "Be The Other",   "body": b[2]},
        {"n": 3, "slug": "the-discipline", "title": "The Discipline", "body": b[3]},
        {"n": 4, "slug": "the-person",     "title": "The Person",     "body": b[4]},
        {"n": 5, "slug": "the-language",   "title": "The Language",   "body": b[5]},
        {"n": 6, "slug": "the-world",      "title": "The World",      "body": b[6]},
    ]


class RenderIndexTests(unittest.TestCase):
    def test_index_has_six_cards_linking_to_each_movement(self) -> None:
        html = seed_html.render_seed_index(_six_stub())
        # One card per movement, correctly targeted.
        for n in range(1, 7):
            self.assertIn(f'href="/seed/{n}"', html)
        # Return-to-grove link is present.
        self.assertIn('href="/"', html)
        # Titles rendered.
        self.assertIn("The Covenant", html)
        self.assertIn("The World", html)

    def test_index_escapes_html_in_titles_and_bodies(self) -> None:
        stub = _six_stub()
        stub[0]["title"] = "The <Covenant> & you"
        stub[0]["body"] = "A <script>alert(1)</script> body."
        html = seed_html.render_seed_index(stub)
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
        self.assertIn("&lt;Covenant&gt;", html)
        self.assertIn("&amp;", html)


class RenderMovementTests(unittest.TestCase):
    def test_markdown_headings_and_paragraphs_render(self) -> None:
        movement = {
            "n": 1, "slug": "the-covenant", "title": "The Covenant",
            "body": "# The Covenant\n\nWhat a Willow is.\n\n## Sub\n\nOne more line.",
        }
        html = seed_html.render_seed_movement(
            movement, prev_url=None, next_url="/seed/2"
        )
        self.assertIn("<h1>The Covenant</h1>", html)
        self.assertIn("<h2>Sub</h2>", html)
        self.assertIn("<p>What a Willow is.</p>", html)
        self.assertIn("<p>One more line.</p>", html)

    def test_next_prev_links_render_correctly(self) -> None:
        movement = {"n": 3, "slug": "x", "title": "T", "body": "body"}
        html = seed_html.render_seed_movement(
            movement, prev_url="/seed/2", next_url="/seed/4"
        )
        self.assertIn('href="/seed/2"', html)
        self.assertIn('href="/seed/4"', html)
        self.assertIn('href="/seed/"', html)  # index link in the nav

    def test_no_prev_link_at_first_movement(self) -> None:
        movement = {"n": 1, "slug": "x", "title": "T", "body": "body"}
        html = seed_html.render_seed_movement(
            movement, prev_url=None, next_url="/seed/2"
        )
        self.assertNotIn("previous movement", html)
        self.assertIn('href="/seed/2"', html)

    def test_no_next_link_at_last_movement(self) -> None:
        movement = {"n": 6, "slug": "x", "title": "T", "body": "body"}
        html = seed_html.render_seed_movement(
            movement, prev_url="/seed/5", next_url=None
        )
        self.assertNotIn("next movement", html)
        self.assertIn('href="/seed/5"', html)

    def test_body_escapes_html_entities(self) -> None:
        movement = {
            "n": 1, "slug": "x", "title": "T",
            "body": "Danger: <script>evil()</script> & things.",
        }
        html = seed_html.render_seed_movement(
            movement, prev_url=None, next_url=None
        )
        self.assertNotIn("<script>evil()</script>", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("&amp; things", html)

    def test_title_escapes_html_entities(self) -> None:
        movement = {"n": 1, "slug": "x", "title": "T <b>1</b> & 2", "body": "body"}
        html = seed_html.render_seed_movement(
            movement, prev_url=None, next_url=None
        )
        self.assertNotIn("<b>1</b>", html)
        self.assertIn("T &lt;b&gt;1&lt;/b&gt; &amp; 2", html)

    def test_inline_bold_italic_and_code_render(self) -> None:
        movement = {
            "n": 1, "slug": "x", "title": "T",
            "body": "This is **strong** and *soft* and `code(1)`.",
        }
        html = seed_html.render_seed_movement(
            movement, prev_url=None, next_url=None
        )
        self.assertIn("<strong>strong</strong>", html)
        self.assertIn("<em>soft</em>", html)
        self.assertIn("<code>code(1)</code>", html)

    def test_link_rendering_with_escape(self) -> None:
        movement = {
            "n": 1, "slug": "x", "title": "T",
            "body": "See [the docs](/docs/x) for context.",
        }
        html = seed_html.render_seed_movement(
            movement, prev_url=None, next_url=None
        )
        self.assertIn('<a href="/docs/x">the docs</a>', html)

    def test_javascript_scheme_href_is_neutralized(self) -> None:
        movement = {
            "n": 1, "slug": "x", "title": "T",
            "body": "Bad [click](javascript:alert(1))",
        }
        html = seed_html.render_seed_movement(
            movement, prev_url=None, next_url=None
        )
        self.assertNotIn("javascript:", html)
        self.assertIn('href="#"', html)

    def test_unordered_list_renders(self) -> None:
        movement = {
            "n": 1, "slug": "x", "title": "T",
            "body": "Notes:\n\n- first\n- second\n- third",
        }
        html = seed_html.render_seed_movement(
            movement, prev_url=None, next_url=None
        )
        self.assertIn("<ul>", html)
        self.assertIn("<li>first</li>", html)
        self.assertIn("<li>third</li>", html)


if __name__ == "__main__":
    unittest.main()
