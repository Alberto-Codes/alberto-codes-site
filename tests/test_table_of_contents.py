"""Long posts get a table of contents, and every heading gets an anchor link.

Issue #75. A post with ``TOC_MIN_SECTIONS`` or more H2s shows an "On this
page" block whose links point at the ids the headings actually render with;
these checks read each registered post's component tree and compiled markdown
without a build. Landing on a fragment in a browser, under the sticky header,
was checked against the static export (see the pull request).
"""

import json

import pytest
from reflex.components.component import Component
from reflex.components.markdown.markdown import Markdown

from alberto_codes_site.alberto_codes_site import app
from alberto_codes_site.headings import (
    SCROLL_MARGIN,
    Slugger,
    heading_ids,
    heading_label,
    heading_labels,
    heading_lines,
)
from alberto_codes_site.pages.blog import TOC_MIN_SECTIONS, _render_post

PAGES = {page.route: page.component for page in app._unevaluated_pages.values()}
POST_ROUTES = sorted(route for route in PAGES if route.startswith("blog/"))


def _walk(component: Component):
    """Yield every component in the tree, depth first, in document order."""
    yield component
    for child in component.children:
        if isinstance(child, Component):
            yield from _walk(child)


def _classes(component: Component) -> str:
    """Return a component's class name as plain text."""
    return str(component.class_name or "")


def _toc_targets(component: Component) -> list[str] | None:
    """Return the ids the table of contents links to, or None without one."""
    navs = [n for n in _walk(component) if n.tag == "nav" and "toc" in _classes(n)]
    if not navs:
        return None
    (nav,) = navs
    return [
        # A router link's target compiles to a JS string literal; decode it.
        json.loads(str(node.to)).removeprefix("#")
        for node in _walk(nav)
        if "toc-link" in _classes(node)
    ]


def _rendered_headings(component: Component) -> list[tuple[int, str]]:
    """List (level, id) for every heading the page's markdown runs render."""
    slugger = Slugger()
    headings: list[tuple[int, str]] = []
    for node in _walk(component):
        if isinstance(node, Markdown):
            source = node.children[0].contents._var_value
            ids = heading_ids(source, slugger)
            headings.extend(
                (level, ids[line]) for line, level, _ in heading_lines(source)
            )
    return headings


@pytest.mark.parametrize("route", POST_ROUTES)
def test_toc_links_match_the_rendered_heading_ids(route):
    """A long post's TOC lists its H2s and H3s by the ids they render with."""
    page = PAGES[route]
    headings = _rendered_headings(page)
    sections = [heading_id for level, heading_id in headings if level == 2]
    targets = _toc_targets(page)
    if len(sections) < TOC_MIN_SECTIONS:
        assert targets is None, f"/{route}: TOC on a short post"
        return
    assert targets == [heading_id for level, heading_id in headings if level in (2, 3)]


@pytest.mark.parametrize("route", POST_ROUTES)
def test_every_heading_has_a_named_anchor_link(route):
    """Each markdown run renders its headings with a labelled link to the id."""
    for node in _walk(PAGES[route]):
        if isinstance(node, Markdown):
            source = node.children[0].contents._var_value
            code = node._get_custom_code() or ""
            assert json.dumps(heading_labels(source)) in code
            assert "Link to section: " in code
            assert "heading-anchor" in code


def test_short_post_has_no_toc():
    """Fewer than four H2s: no table of contents."""
    body = "Intro.\n\n## One\n\nA.\n\n## Two\n\n### Two a\n\n## Three\n\nC.\n"
    assert _toc_targets(_render_post({"title": "T"}, body)) is None


def test_toc_nests_h3s_and_skips_deeper_headings():
    """Four H2s get a TOC; H3s follow their H2, H4s are left out."""
    body = "".join(
        f"## Part {n}\n\n### Detail {n}\n\n#### Fine {n}\n\n" for n in "1234"
    )
    targets = _toc_targets(_render_post({"title": "T"}, body))
    assert targets == [slug for n in "1234" for slug in (f"part-{n}", f"detail-{n}")]


def test_toc_is_a_labelled_nav_without_a_heading():
    """The block is a named landmark and adds nothing to the heading outline."""
    body = "".join(f"## Part {n}\n\n" for n in "1234")
    page = _render_post({"title": "T"}, body)
    (nav,) = [n for n in _walk(page) if n.tag == "nav"]
    assert nav.custom_attrs["aria-label"] == "On this page"
    assert not [
        n for n in _walk(nav) if n.tag and n.tag[0] == "h" and n.tag[1:].isdigit()
    ]


def test_headings_clear_the_sticky_header():
    """A fragment jump leaves room above the heading for the site header."""
    jsx = str(_render_post({"title": "T"}, "## One\n"))
    assert f'["scrollMarginTop"] : "{SCROLL_MARGIN}"' in jsx


@pytest.mark.parametrize(
    ("text", "label"),
    [
        ("Why it works", "Why it works"),
        ("The `vramfit` CLI", "The vramfit CLI"),
        ("See [the docs](https://x.y/z)", "See the docs"),
        ("**Bold** and ~~gone~~ text", "Bold and gone text"),
        ("snake_case stays", "snake_case stays"),
    ],
)
def test_heading_label_is_the_visible_text(text, label):
    """TOC entries and anchor names read as the heading does, minus syntax."""
    assert heading_label(text) == label
