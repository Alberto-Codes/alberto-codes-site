"""Every post closes with older/newer links, related posts and an author line.

Issue #74. These checks read each registered post's component tree, and
render fixture posts, without a build. The look at 390px and 1440px in both
themes was checked against the static export (see the pull request).
"""

import json
from datetime import date

import pytest
from reflex.components.component import Component
from reflex.components.radix.themes.typography.heading import Heading

from alberto_codes_site.alberto_codes_site import app
from alberto_codes_site.feed import build_feed
from alberto_codes_site.pages.blog import (
    RELATED_MAX,
    _load_posts,
    _render_post,
    discussion_label,
    neighbour_posts,
    published_posts,
    related_posts,
)
from alberto_codes_site.social import AUTHOR_SAME_AS

PAGES = {page.route: page.component for page in app._unevaluated_pages.values()}
POST_ROUTES = sorted(route for route in PAGES if route.startswith("blog/"))


def _walk(component: Component):
    """Yield every component in the tree, depth first, in document order."""
    yield component
    for child in component.children:
        if isinstance(child, Component):
            yield from _walk(child)


def _post_end(component: Component) -> Component:
    """Return the page's one end-of-post section."""
    (end,) = [n for n in _walk(component) if "post-end" == str(n.class_name or "")]
    return end


def _nav(end: Component, label: str) -> Component | None:
    """Return the ``nav`` inside the end section with this accessible name."""
    navs = [
        n
        for n in _walk(end)
        if n.tag == "nav" and n.custom_attrs.get("aria-label") == label
    ]
    return navs[0] if navs else None


def _hrefs(component: Component) -> list[str]:
    """List the post routes a subtree links to, in order.

    Each link is a Radix link around a React Router link; read its target.
    """
    return [
        json.loads(str(n.children[0].to))
        for n in _walk(component)
        if "post-end-link" in str(n.class_name or "")
    ]


def _post(slug: str, day: str, tags: list[str], **extra) -> tuple[dict, str]:
    """Build a fixture post as ``_load_posts`` would return it."""
    return {"slug": slug, "title": slug.title(), "date": day, "tags": tags, **extra}, (
        "Body.\n"
    )


def test_every_post_route_is_found():
    """The parametrized checks below cover the real posts."""
    assert POST_ROUTES


@pytest.mark.parametrize("route", POST_ROUTES)
def test_every_post_ends_with_the_section(route):
    """Each post has the section, with the author line and profile links."""
    end = _post_end(PAGES[route])
    jsx = str(end)
    assert "Written by Alberto Nieto, Generative AI Principal Engineer." in jsx
    for href in ("/about", *AUTHOR_SAME_AS, "/feed.xml"):
        assert json.dumps(href) in jsx, f"/{route}: no link to {href}"
    assert not any(isinstance(n, Heading) for n in _walk(end))
    assert not any(n.tag in {f"h{i}" for i in range(1, 7)} for n in _walk(end))


@pytest.mark.parametrize("route", POST_ROUTES)
def test_older_and_newer_follow_the_published_order(route):
    """Older/newer point at the adjacent published posts, none at the ends."""
    posts = published_posts(_load_posts())
    slugs = [m["slug"] for m, _ in posts]
    i = slugs.index(route.removeprefix("blog/"))
    expected = []
    if i + 1 < len(slugs):
        expected.append(f"/blog/{slugs[i + 1]}")
    if i > 0:
        expected.append(f"/blog/{slugs[i - 1]}")
    nav = _nav(_post_end(PAGES[route]), "Older and newer posts")
    assert (_hrefs(nav) if nav is not None else []) == expected
    # The compiled JSX escapes the arrows.
    jsx = str(nav)
    assert (json.dumps("← Older")[1:-1] in jsx) == (i + 1 < len(slugs))
    assert (json.dumps("Newer →")[1:-1] in jsx) == (i > 0)


@pytest.mark.parametrize("route", POST_ROUTES)
def test_related_posts_skip_the_neighbours(route):
    """Related links never repeat the post itself or its older/newer links."""
    end = _post_end(PAGES[route])
    related = _nav(end, "Related posts")
    if related is None:
        return
    neighbours = _nav(end, "Older and newer posts")
    shown = _hrefs(related)
    assert 1 <= len(shown) <= RELATED_MAX
    assert f"/{route}" not in shown
    assert not set(shown) & set(_hrefs(neighbours) if neighbours else [])


def test_neighbours_skip_future_posts():
    """A post dated after the build date is never an older/newer link."""
    posts = published_posts(
        [
            _post("future", "2026-12-01", []),
            _post("new", "2026-09-01", []),
            _post("old", "2026-08-01", []),
        ],
        today=date(2026, 10, 1),
    )
    older, newer = neighbour_posts("new", posts)
    assert older["slug"] == "old"
    assert newer is None
    assert neighbour_posts("old", posts) == (None, posts[0][0])


def test_related_ranks_by_shared_tags_then_date():
    """Two shared tags is the floor; more shared tags, then newer, rank first."""
    current = _post("current", "2026-09-01", ["a", "b", "c", "d"])
    posts = [
        current,
        _post("one-tag", "2026-09-05", ["a"]),
        _post("two-old", "2026-01-01", ["a", "b"]),
        _post("two-new", "2026-06-01", ["c", "d"]),
        _post("three", "2026-02-01", ["a", "b", "c"]),
        _post("two-mid", "2026-03-01", ["b", "d"]),
        _post("neighbour", "2026-08-01", ["a", "b", "c", "d"]),
    ]
    ranked = related_posts(current[0], posts, exclude={"neighbour"})
    assert [m["slug"] for m in ranked] == ["three", "two-new", "two-mid"]


def test_related_block_is_left_out_when_nothing_qualifies():
    """A post with no qualifying matches has no related block at all."""
    current = _post("current", "2026-09-01", ["a", "b"])
    posts = [current, _post("other", "2026-08-01", ["a", "z"])]
    end = _post_end(_render_post(*current, posts))
    assert _nav(end, "Related posts") is None
    assert "More on this" not in str(end)


def test_discussion_url_renders_a_link():
    """A post with ``discussion_url`` links to it; one without does not."""
    url = "https://www.reddit.com/r/LocalLLaMA/comments/abc123/example/"
    with_link = _post("current", "2026-09-01", [], discussion_url=url)
    jsx = str(_post_end(_render_post(*with_link)))
    assert json.dumps(url) in jsx
    assert "Discuss on r/LocalLLaMA" in jsx

    without = _post("current", "2026-09-01", [])
    assert "Join the discussion" not in str(_post_end(_render_post(*without)))
    assert "Discuss on" not in str(_post_end(_render_post(*without)))


@pytest.mark.parametrize(
    ("url", "label"),
    [
        ("https://www.reddit.com/r/Python/comments/x/y/", "Discuss on r/Python"),
        ("https://old.reddit.com/r/LocalLLaMA/", "Discuss on r/LocalLLaMA"),
        ("https://reddit.com/r/vllm", "Discuss on r/vllm"),
        ("https://www.reddit.com/user/someone/", "Join the discussion"),
        ("https://notreddit.com/r/Python/", "Join the discussion"),
        ("https://news.ycombinator.com/item?id=1", "Join the discussion"),
    ],
)
def test_discussion_label(url, label):
    """Subreddit threads name the subreddit; anything else gets a plain label."""
    assert discussion_label(url) == label


def test_section_stays_out_of_the_feed():
    """The RSS items carry the post body only, not the end section."""
    xml = build_feed(_load_posts())
    assert "Written by" not in xml
    assert "More on this" not in xml
