"""Front-matter values written as YAML quoted scalars render without quotes."""

import pytest

from alberto_codes_site.pages.blog import _load_posts, _parse_frontmatter


def _value(raw: str) -> str:
    meta, _ = _parse_frontmatter(f"---\ntitle: {raw}\n---\nBody.\n")
    return meta["title"]


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Plain title", "Plain title"),
        ('"Quoted: with a colon"', "Quoted: with a colon"),
        ("'Single quoted'", "Single quoted"),
        (r'"She said \"fit\""', 'She said "fit"'),
        (r'"A back\\slash"', r"A back\slash"),
        ("'It''s single'", "It's single"),
        ('"Only an opening quote', '"Only an opening quote'),
        ('Only a closing quote"', 'Only a closing quote"'),
        ('A "quoted" middle', 'A "quoted" middle'),
        ("\"Mismatched'", "\"Mismatched'"),
        ('"', '"'),
        ('""', ""),
    ],
)
def test_quoted_scalars_lose_their_quotes(raw, expected):
    """A matching outer pair is removed and unescaped; anything else is text."""
    assert _value(raw) == expected


@pytest.mark.parametrize("meta", [m for m, _ in _load_posts()], ids=lambda m: m["slug"])
def test_no_post_title_or_summary_is_wrapped_in_quotes(meta):
    """Every post's title and summary reach the pages without YAML quoting."""
    for key in ("title", "summary"):
        value = meta.get(key, "")
        assert value, key
        assert not (value[0] in "\"'" and value[-1] == value[0]), (key, value)
