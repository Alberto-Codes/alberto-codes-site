"""Every route has one ``<h1>`` and post headings carry stable, unique ids.

Radix's Heading renders ``<h1>`` unless told otherwise, which once left the
home page with twelve of them (issue #70). These checks walk each registered
page's component tree without a build: a Heading's level is its ``as_`` prop
(``h1`` when unset), and a markdown run's headings come from its source, which
react-markdown renders at the level written. `scripts/check_heading_structure.py`
runs the same rules over a real static export.
"""

import json

import pytest
from reflex.components.component import Component
from reflex.components.markdown.markdown import Markdown
from reflex.components.radix.themes.typography.heading import Heading

from alberto_codes_site.alberto_codes_site import app
from alberto_codes_site.headings import Slugger, heading_ids, heading_lines

PAGES = {page.route: page.component for page in app._unevaluated_pages.values()}
POST_ROUTES = sorted(route for route in PAGES if route.startswith("blog/"))


def _level(heading: Heading) -> str:
    """Return the HTML tag a Heading renders as.

    Radix accepts only ``h1``-``h6`` for ``as`` and renders anything else, or
    nothing, as ``h1``. With ``as_child`` the heading's classes go to its child
    element instead, which renders as its own tag.
    """
    if heading.as_child is not None and str(heading.as_child) == "true":
        return heading.children[0].tag
    as_ = "" if heading.as_ is None else str(heading.as_).strip('"')
    return as_ if as_ in {f"h{n}" for n in range(1, 7)} else "h1"


def _walk(component: Component):
    """Yield every component in the tree, depth first, in document order."""
    yield component
    for child in component.children:
        if isinstance(child, Component):
            yield from _walk(child)


def _source(markdown: Markdown) -> str:
    """Return the markdown text a Markdown component was created with."""
    return markdown.children[0].contents._var_value


def _outline(component: Component) -> list[tuple[int, str | None]]:
    """List a page's headings in order as (level, id), markdown included."""
    outline: list[tuple[int, str | None]] = []
    slugger = Slugger()
    for node in _walk(component):
        if isinstance(node, Heading):
            tag = _level(node)
            if tag.startswith("h") and tag[1:].isdigit():
                outline.append((int(tag[1:]), None))
        elif isinstance(node, Markdown):
            source = _source(node)
            ids = heading_ids(source, slugger)
            outline.extend(
                (level, ids[line]) for line, level, _ in heading_lines(source)
            )
    return outline


def test_routes_were_found():
    """The walk covers the fixed pages and at least one post."""
    assert {"index", "about", "blog", "contact"} <= set(PAGES)
    assert POST_ROUTES


@pytest.mark.parametrize("route", sorted(PAGES))
def test_exactly_one_h1(route):
    """Each route, navbar and footer included, has a single page title."""
    levels = [level for level, _ in _outline(PAGES[route])]
    assert levels.count(1) == 1, f"/{route}: {levels.count(1)} h1 elements"


@pytest.mark.parametrize("route", sorted(PAGES))
def test_no_skipped_levels(route):
    """No heading is more than one level deeper than the one before it."""
    levels = [level for level, _ in _outline(PAGES[route])]
    assert levels[0] == 1, f"/{route}: first heading is h{levels[0]}"
    for before, after in zip(levels, levels[1:], strict=False):
        assert after <= before + 1, f"/{route}: h{before} followed by h{after}"


@pytest.mark.parametrize("route", POST_ROUTES)
def test_post_headings_have_unique_ids(route):
    """Every heading in a post body has an id, and no two ids collide."""
    ids = [heading_id for level, heading_id in _outline(PAGES[route]) if level > 1]
    assert ids, f"/{route}: no body headings"
    assert all(ids), f"/{route}: a body heading has no id"
    assert len(ids) == len(set(ids)), f"/{route}: duplicate heading ids"


@pytest.mark.parametrize("route", POST_ROUTES)
def test_post_heading_ids_reach_the_compiled_page(route):
    """Each markdown run's compiled component map carries that run's ids."""
    slugger = Slugger()
    for node in _walk(PAGES[route]):
        if isinstance(node, Markdown):
            source = _source(node)
            ids = heading_ids(source, slugger)
            code = node._get_custom_code() or ""
            assert json.dumps(ids) in code
            assert "node?.position?.start?.line" in code


@pytest.mark.parametrize(
    ("titles", "expected"),
    [
        (["Why it works"], ["why-it-works"]),
        (
            ["Why it works", "Why it works", "Why it works"],
            ["why-it-works", "why-it-works-1", "why-it-works-2"],
        ),
        (["The `vramfit` CLI"], ["the-vramfit-cli"]),
        (["See [the docs](https://x.y/z)"], ["see-the-docs"]),
        (["What 4.5 bits means — really?"], ["what-45-bits-means--really"]),
        (["a", "a-1", "a"], ["a", "a-1", "a-2"]),
    ],
)
def test_slugs_match_github_style(titles, expected):
    """Slugs follow github-slugger: lowercase, punctuation dropped, -N repeats."""
    slugger = Slugger()
    assert [slugger.slug(title) for title in titles] == expected


def test_headings_inside_code_fences_are_ignored():
    """A ``#`` line inside a fenced block is code, not a heading."""
    source = "## One\n\n```bash\n# a comment\n```\n\n~~~\n## not this\n~~~\n### Two\n"
    assert [(line, level) for line, level, _ in heading_lines(source)] == [
        (1, 2),
        (10, 3),
    ]


def test_ids_are_stable_across_builds():
    """Computing a post's ids twice gives the same answer."""
    route = POST_ROUTES[0]
    assert _outline(PAGES[route]) == _outline(PAGES[route])
