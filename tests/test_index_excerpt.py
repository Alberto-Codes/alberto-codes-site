"""The blog index shows each summary's first complete sentence.

The excerpt is derived from the front-matter summary; the post page and the
feeds keep the full summary.
"""

import pytest

from alberto_codes_site.pages.blog import _load_posts, first_sentence, published_posts

_OPENERS = {'"': '"', "“": "”"}


@pytest.mark.parametrize(
    ("summary", "expected"),
    [
        ("It fit. Then it broke.", "It fit."),
        ("Did it fit? Yes.", "Did it fit?"),
        ("It fit! 24 GiB was enough.", "It fit!"),
        ('It said "fit." Then it broke.', 'It said "fit."'),
        ("It fit (barely.) Then it broke.", "It fit (barely.)"),
        ('It fit. "Then" it broke.', "It fit."),
        ("v0.5.0 shipped. Then more.", "v0.5.0 shipped."),
        ("At 4.5 bits it fits. Then not.", "At 4.5 bits it fits."),
        ("It is 17.54 GiB at 3.76x. Then not.", "It is 17.54 GiB at 3.76x."),
        ("It ended. v0.6.0 records more.", "It ended. v0.6.0 records more."),
        ("One sentence only, with no end", "One sentence only, with no end"),
        ("Only one sentence.", "Only one sentence."),
        ('"Quoted first. Second."', '"Quoted first."'),
        ("“Curly first. Second.”", "“Curly first.”"),
        ('"Whole quoted summary."', '"Whole quoted summary."'),
    ],
)
def test_first_sentence(summary, expected):
    """Sentences end at . ! ? before a capital, digit or quote, never in a number."""
    assert first_sentence(summary) == expected


@pytest.mark.parametrize(
    "meta", [m for m, _ in published_posts(_load_posts())], ids=lambda m: m["slug"]
)
def test_every_excerpt_is_a_whole_sentence_from_its_summary(meta):
    """Non-empty, ends a sentence or a quote, and starts the summary."""
    summary = meta.get("summary", "").strip()
    excerpt = first_sentence(summary)
    assert excerpt
    assert excerpt[-1] in '.!?"”’)'
    prefix = excerpt
    closer = _OPENERS.get(summary[:1])
    if closer and not summary.startswith(excerpt) and excerpt.endswith(closer):
        prefix = excerpt[: -len(closer)]  # the closing mark added for balance
    assert summary.startswith(prefix)
