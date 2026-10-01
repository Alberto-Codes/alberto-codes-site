"""The /blog index says what each Diataxis post type means (issue #49).

The meanings sit beside the labels in a definition list, always visible,
rather than in a hover tooltip that touch and keyboard readers cannot reach.
"""

from datetime import date

from alberto_codes_site.pages import blog

DESCRIPTIONS = {
    "tutorial": "learn by doing, step by step",
    "how-to": "solve one specific problem",
    "explanation": "understand why something works",
    "reference": "look up the details",
}


def _index() -> str:
    """Render /blog as of a date after every post."""
    return str(blog.blog_page(today=date(2100, 1, 1)))


def test_blog_index_renders_every_type_description():
    """Each type's label and its plain description appear on /blog."""
    rendered = _index()
    for label, description in DESCRIPTIONS.items():
        assert f'"{label}"' in rendered
        assert description in rendered


def test_legend_is_a_definition_list():
    """The legend is one ``<dl>`` with a term and description per type."""
    rendered = _index()
    assert rendered.count('jsx("dl"') == 1
    assert rendered.count('jsx("dt"') == len(DESCRIPTIONS)
    assert rendered.count('jsx("dd"') == len(DESCRIPTIONS)


def test_every_type_has_a_description():
    """A type added to the colour map needs a description too."""
    assert set(blog.DIATAXIS_DESCRIPTIONS) == set(blog.DIATAXIS_COLORS)
