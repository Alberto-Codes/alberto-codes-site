"""The site's frame and type: current-page mark, index rows, rules and face.

These read the compiled component output and the shipped assets, so the
identity cannot drift back to cards, symmetric heading space, boxed tables or
a hosted font without a test failing.
"""

import re
from datetime import date
from pathlib import Path

import pytest

from alberto_codes_site.components.navbar import NAV_LINKS, is_current, navbar
from alberto_codes_site.headings import HEADING_SPACE_ABOVE, HEADING_SPACE_BELOW
from alberto_codes_site.pages.blog import (
    LEADER_CLOSE,
    TABLE_HAIRLINE,
    TABLE_HEAVY_RULE,
    TABLE_SCROLL_CLASS,
    TABLE_SCROLL_LABEL,
    _load_posts,
    _post_body,
    _render_post,
    _table,
    blog_page,
    published_posts,
)
from alberto_codes_site.pages.home import (
    LATEST_POST_COUNT,
    _latest_posts,
    _latest_writing,
)

ASSETS = Path(__file__).resolve().parent.parent / "src" / "assets"
FUTURE = date(2100, 1, 1)
CURRENT = '"aria-current":"page"'


@pytest.mark.parametrize(
    ("route", "label"),
    [
        ("/", "Home"),
        ("/about", "About"),
        ("/blog", "Blog"),
        ("/blog/2026-10-28-urgent-receipts-bulk-import", "Blog"),
        ("/blog/series/saucier", "Blog"),
        ("/contact", "Contact"),
    ],
)
def test_navigation_marks_only_the_current_page(route, label):
    """Exactly one entry is current in each nav (the bar and the phone menu)."""
    marked = [text for text, href in NAV_LINKS if is_current(href, route)]
    assert marked == [label]
    # Once in the desktop bar and once in the phone menu.
    assert str(navbar(current=route)).count(CURRENT) == 2


def test_navigation_without_a_route_marks_nothing():
    """The 404 page has no current entry."""
    assert CURRENT not in str(navbar())


def test_blog_index_is_an_index_not_cards():
    """Each published post is one index row under a year heading; no cards."""
    jsx = str(blog_page(today=FUTURE))
    posts = published_posts(_load_posts(), today=FUTURE)
    assert "RadixThemesCard" not in jsx
    assert jsx.count('className:"index-entry"') == len(posts)
    years = {str(m["date"])[:4] for m, _ in posts}
    for year in years:
        assert f'"aria-label":"Posts from {year}"' in jsx
    assert jsx.count('className:"index-leader"') == len(posts)


def test_home_latest_writing_is_index_rows_not_cards():
    """Home's latest posts are blog index rows, with the index's own styles."""
    jsx = str(_latest_writing(today=FUTURE))
    count = len(_latest_posts(today=FUTURE))
    assert count == LATEST_POST_COUNT
    assert "RadixThemesCard" not in jsx
    assert jsx.count('className:"index-entry"') == count
    assert jsx.count('className:"index-leader"') == count
    assert jsx.count('className:"index-summary"') == count
    # The same leader close as /blog, not a copy that could drift.
    assert f'["transition"] : "opacity {LEADER_CLOSE}"' in jsx
    assert '["& .index-entry:is(:hover, :focus-within) .index-leader::after"]' in jsx


def test_index_leader_closes_in_120ms_and_not_under_reduced_motion():
    """The signature change is one 120ms ease-out, removed for reduced motion."""
    jsx = str(blog_page(today=FUTURE))
    assert LEADER_CLOSE == "120ms ease-out"
    assert f'["transition"] : "opacity {LEADER_CLOSE}"' in jsx
    assert (
        '["@media (prefers-reduced-motion: reduce)"] : '
        '({ ["& .index-leader::after"] : ({ ["transition"] : "none" }) })'
    ) in jsx


def test_section_headings_have_more_space_above_than_below():
    """A body heading's top margin is larger than its bottom margin."""
    above = float(HEADING_SPACE_ABOVE.removesuffix("em"))
    below = float(HEADING_SPACE_BELOW.removesuffix("em"))
    assert above >= 3 * below
    (markdown,), _ = _post_body("## A\n\nText.\n")
    code = str(markdown._get_all_custom_code())
    assert (
        f'["marginTop"] : "{HEADING_SPACE_ABOVE}", '
        f'["marginBottom"] : "{HEADING_SPACE_BELOW}"'
    ) in code


def test_tables_are_ruled_like_printed_proportions():
    """Heavy rules above and below, a hairline under the head, no fills."""
    jsx = str(_render_post({"title": "T"}, "| a |\n|---|\n| 1 |\n"))
    assert f'["borderTop"] : "{TABLE_HEAVY_RULE}"' in jsx
    assert f'["borderBottom"] : "{TABLE_HEAVY_RULE}"' in jsx
    assert f'["& thead th"] : ({{ ["borderBottom"] : "{TABLE_HAIRLINE}" }})' in jsx
    assert "nth-child(even)" not in jsx
    assert '["& th"] : ({ ["fontWeight"] : "600" })' in jsx
    # Separate borders keep the rules outside the sticky first column.
    assert '["borderCollapse"] : "separate", ["borderSpacing"] : "0"' in jsx


def test_a_wide_table_is_a_named_focusable_region():
    """The scroll viewport takes Tab focus and has a name for screen readers."""
    jsx = str(_table("cells"))
    assert f'"aria-label":"{TABLE_SCROLL_LABEL}"' in jsx
    assert 'role:"region"' in jsx
    assert "tabIndex:0" in jsx
    assert f'className:"{TABLE_SCROLL_CLASS}"' in jsx


def test_a_scrolled_table_keeps_its_first_column_and_one_line_values():
    """First column sticks on the ground; phone body cells do not wrap."""
    jsx = str(_render_post({"title": "T"}, "| a | b |\n|---|---|\n| 1 | 2 |\n"))
    assert (
        '["& :is(th, td):first-child"] : ({ ["position"] : "sticky", '
        '["left"] : "0", ["backgroundColor"] : "var(--color-background)" })'
    ) in jsx
    assert (
        '["@media screen and (max-width: 767.98px)"] : '
        '({ ["& td"] : ({ ["whiteSpace"] : "nowrap" }) })'
    ) in jsx


def test_table_edge_shade_is_css_only_and_absent_when_it_fits():
    """A fixed shade under a scrolling cover, and a scroll-timeline left shade."""
    css = (ASSETS / "identity.css").read_text()
    rule = re.search(r"\.table-scroll > \.rt-ScrollAreaViewport \{(.*?)\n\}", css, re.S)
    assert rule is not None
    assert "no-repeat local" in rule.group(1)
    assert "no-repeat scroll" in rule.group(1)
    assert "@supports (animation-timeline: scroll())" in css
    assert "scroll-timeline: --table-scroll x" in css


def test_focus_ring_is_one_token_that_clears_three_to_one():
    """Grass 11 on the ground, the cloth mark on the cloth; never grass 8."""
    css = (ASSETS / "identity.css").read_text() + (ASSETS / "a11y.css").read_text()
    assert re.search(r"\.radix-themes \{[^}]*--focus-ring: var\(--accent-11\);", css)
    assert re.search(r"\.cloth \{[^}]*--focus-ring: var\(--cloth-mark\);", css)
    assert "outline: 2px solid var(--focus-ring);" in css
    assert "accent-8" not in css
    source = Path(__file__).resolve().parent.parent / "src" / "alberto_codes_site"
    for path in source.rglob("*.py"):
        assert "'accent', 8" not in path.read_text(), path


def test_heading_face_is_self_hosted_with_its_licence():
    """Besley ships as a local woff2 with its OFL text, swapped in, not hosted."""
    font = ASSETS / "fonts" / "Besley-wght.woff2"
    licence = ASSETS / "fonts" / "Besley-OFL.txt"
    assert font.read_bytes()[:4] == b"wOF2"
    assert "SIL Open Font License" in licence.read_text()
    css = (ASSETS / "identity.css").read_text()
    face = re.search(r'@font-face \{\s*font-family: "Besley";(.*?)\}', css, re.S)
    assert face is not None
    assert 'url("/fonts/Besley-wght.woff2")' in face.group(1)
    assert "font-display: swap" in face.group(1)
    assert "googleapis" not in css
    assert "--heading-font-family" in css
