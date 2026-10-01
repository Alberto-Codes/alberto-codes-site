"""Blog series: frontmatter membership, part order, published-only counting.

Issue #51. A post joins a series with ``series: <Display Title>``. These
checks read the real posts' frontmatter and each registered page's compiled
JSX, and render fixture posts, without a build. The look at 390px and 1440px
in both themes was checked against the static export (see the pull request).
"""

import json
import re
import xml.etree.ElementTree as ET
from datetime import date

import pytest
import reflex as rx

from alberto_codes_site import alberto_codes_site as site
from alberto_codes_site.alberto_codes_site import app
from alberto_codes_site.pages import blog
from alberto_codes_site.pages.blog import (
    _load_posts,
    _parse_frontmatter,
    _post_end,
    _render_post,
    published_posts,
)
from alberto_codes_site.series import (
    Series,
    build_series,
    series_of,
    series_slug,
    series_title,
)
from alberto_codes_site.sitemap import SITEMAP_NAMESPACE, sitemap_xml
from alberto_codes_site.social import SITE_URL, blog_posting_data

PAGES = {page.route: page.component for page in app._unevaluated_pages.values()}
PUBLISHED = published_posts(_load_posts())
SERIES = build_series(PUBLISHED)
SERIES_POSTS = [m for m, _ in PUBLISHED if series_title(m)]
STANDALONE = [m for m, _ in PUBLISHED if not series_title(m)]

# The membership decided for #51, by part count.
EXPECTED_SIZES = {
    "Saucier": 7,
    "vramfit": 6,
    "TurboQuant on vision models": 4,
    "docvet and docstring quality": 4,
    "Encrypted ADK sessions": 2,
    "AI pipeline plumbing": 2,
    "Measuring model confidence": 3,
}

TODAY = date(2026, 10, 1)


def _post(slug: str, day: str, series: str | None = None, **extra):
    """Build a fixture post as ``_load_posts`` would return it."""
    meta = {"slug": slug, "title": slug.title(), "date": day, **extra}
    if series is not None:
        meta["series"] = series
    return meta, "Body.\n"


def _links(jsx: str) -> list[str]:
    """List the router targets in compiled JSX, in document order."""
    return re.findall(r'to:"(/blog/[^"]*)"', jsx)


def _series_box(jsx: str) -> str:
    """Return the compiled series box of a post page, or "" when it has none."""
    start = jsx.find('className:"series-box"')
    if start < 0:
        return ""
    end = jsx.find('"aria-label":"On this page"', start)
    if end < 0:
        end = jsx.find("RadixThemesBox", start)
    return jsx[start:end]


def test_frontmatter_series_field_parses():
    """``series: <title>`` is a plain top-level key; blank means standalone."""
    meta, body = _parse_frontmatter(
        "---\ntitle: T\ndate: 2026-01-01\ntags:\n  - a\nseries: Saucier\n---\n\nB\n"
    )
    assert meta["series"] == "Saucier"
    assert meta["tags"] == ["a"]
    assert body == "B"
    assert series_title({"series": "  vramfit "}) == "vramfit"
    assert series_title({"series": ""}) is None
    assert series_title({}) is None


def test_real_series_membership():
    """Each series has the parts decided for #51; the rest are standalone."""
    assert {s.title: len(s) for s in SERIES} == EXPECTED_SIZES
    assert len(STANDALONE) == 4


def test_series_slugs_come_from_the_title():
    """The slug is the heading slugger's, so the page route is predictable."""
    assert series_slug("TurboQuant on vision models") == "turboquant-on-vision-models"
    assert {s.slug for s in SERIES} >= {"saucier", "vramfit", "encrypted-adk-sessions"}


def test_parts_are_numbered_by_date_then_slug():
    """Oldest part is Part 1; a date tie goes to the earlier file name."""
    posts = [
        _post("2026-01-03-c", "2026-01-03", "S"),
        _post("2026-01-02-b", "2026-01-02", "S"),
        _post("2026-01-02-a", "2026-01-02", "S"),
        _post("2026-01-04-alone", "2026-01-04"),
    ]
    (series,) = build_series(posts)
    assert [p["slug"] for p in series.parts] == [
        "2026-01-02-a",
        "2026-01-02-b",
        "2026-01-03-c",
    ]
    assert series.number("2026-01-02-b") == 2
    assert series.neighbours("2026-01-02-a") == (None, series.parts[1])
    assert series.neighbours("2026-01-03-c") == (series.parts[1], None)
    assert series_of(posts[3][0], [series]) is None


def test_two_titles_with_one_slug_are_rejected():
    """Two series may not share a page route."""
    with pytest.raises(ValueError, match="share"):
        build_series([_post("a", "2026-01-01", "A B"), _post("b", "2026-01-02", "a-b")])


@pytest.fixture
def fake_posts(tmp_path, monkeypatch):
    """Two published parts of one series and a third dated after the build."""
    for slug, day in [
        ("2026-09-01-one", "2026-09-01"),
        ("2026-09-15-two", "2026-09-15"),
        ("2026-10-02-three", "2026-10-02"),
    ]:
        (tmp_path / f"{slug}.md").write_text(
            f"---\ntitle: {slug}\ndate: {day}\nsummary: S.\ntype: explanation\n"
            "series: Fake Series\n---\n\nBody.\n"
        )
    monkeypatch.setattr(blog, "POSTS_DIR", tmp_path)
    return tmp_path


def test_future_part_is_neither_counted_nor_linked(fake_posts):
    """A part dated after the build date is absent from every series view."""
    posts = published_posts(blog._load_posts(), today=TODAY)
    (series,) = build_series(posts)
    assert len(series) == 2
    post = blog.blog_post_page("2026-09-15-two", today=TODAY)
    jsx = str(post)
    assert "Part 2 of 2 in " in jsx
    assert "2026-10-02-three" not in jsx
    assert "Last part of " in jsx
    page = str(blog.series_page("fake-series", today=TODAY))
    assert "A series in 2 parts, published from 2026-09-01 to 2026-09-15." in page
    assert "2026-10-02-three" not in page
    index = str(blog.blog_page(today=TODAY))
    assert "Part 1 of 2 \\u00b7 Fake Series" in index
    assert "2026-10-02-three" not in index


def test_series_routes_skip_future_parts(fake_posts, monkeypatch):
    """The series page is registered once, with the newest published date."""
    fresh = rx.App(enable_state=False)
    monkeypatch.setattr(site, "app", fresh)
    site.add_series_pages(today=TODAY)
    (page,) = fresh._unevaluated_pages.values()
    assert page.route == "blog/series/fake-series"
    assert page.context == {"sitemap": {"lastmod": "2026-09-15"}}


def test_series_routes_match_the_sitemap():
    """Every series has a sitemap entry whose lastmod is its newest part."""
    root = ET.fromstring(sitemap_xml(list(app._unevaluated_pages.values())).encode())
    ns = {"sm": SITEMAP_NAMESPACE}
    listed = {
        re.sub(r"^https?://[^/]+", "", url.findtext("sm:loc", namespaces=ns)): (
            url.findtext("sm:lastmod", namespaces=ns)
        )
        for url in root.findall("sm:url", ns)
        if "/blog/series/" in url.findtext("sm:loc", namespaces=ns)
    }
    assert listed == {s.route: s.last_date for s in SERIES}


@pytest.mark.parametrize("meta", SERIES_POSTS, ids=[m["slug"] for m in SERIES_POSTS])
def test_every_series_post_renders_the_box(meta):
    """The box shows the part number, the series link and adjacent parts."""
    series = series_of(meta, SERIES)
    jsx = str(PAGES[f"blog/{meta['slug']}"])
    box = _series_box(jsx)
    number = series.number(meta["slug"])
    assert f"Part {number} of {len(series)} in " in box
    previous, following = series.neighbours(meta["slug"])
    expected = [series.route]
    expected += [f"/blog/{previous['slug']}"] if previous else []
    expected += [f"/blog/{following['slug']}"] if following else []
    assert _links(box) == expected
    # The box sits above the body, after the header.
    assert jsx.find('className:"series-box"') < jsx.find('className:"post-end"')


@pytest.mark.parametrize("meta", STANDALONE, ids=[m["slug"] for m in STANDALONE])
def test_standalone_posts_have_no_series_box(meta):
    """A post without ``series`` has no box and no series block at its end."""
    jsx = str(PAGES[f"blog/{meta['slug']}"])
    assert 'className:"series-box"' not in jsx
    assert 'className:"post-end-series"' not in jsx


@pytest.mark.parametrize("series", SERIES, ids=[s.slug for s in SERIES])
def test_series_page_lists_parts_in_frontmatter_order(series):
    """The page links each part once, ordered by date then file name."""
    files = sorted(
        (m["date"], m["slug"]) for m, _ in PUBLISHED if series_title(m) == series.title
    )
    jsx = str(PAGES[series.route.lstrip("/")])
    assert _links(jsx) == [f"/blog/{slug}" for _, slug in files]
    for i, (_, slug) in enumerate(files, start=1):
        assert f"Part {i} of {len(files)}" in jsx


def test_end_section_leads_with_the_next_part():
    """A middle part's end opens with "Next in"; related skips linked parts."""
    tags = ["a", "b"]
    posts = published_posts(
        [
            _post("p3", "2026-03-01", "S", tags=tags),
            _post("other", "2026-02-15", tags=tags),
            _post("p2", "2026-02-01", "S", tags=tags),
            _post("p1", "2026-01-01", "S", tags=tags),
            _post("p0", "2025-12-01", "S", tags=tags),
        ],
        today=TODAY,
    )
    (series,) = build_series(posts)
    meta = next(m for m, _ in posts if m["slug"] == "p1")
    end = str(_post_end(meta, posts, series))
    assert end.index("Next in ") < end.index("Older")
    assert _links(end)[:2] == ["/blog/series/s", "/blog/p2"]
    related = end[end.index('"aria-label":"Related posts"') :]
    # p0 and p2 are linked by the series box; p2 is also the Newer link.
    assert _links(related) == ["/blog/p3", "/blog/other"]
    last = next(m for m, _ in posts if m["slug"] == "p3")
    assert "Last part of " in str(_post_end(last, posts, series))


def test_end_section_does_not_repeat_the_next_part_as_newer():
    """When the next part is also the newer post, it is linked once."""
    posts = published_posts(
        [
            _post("p3", "2026-03-01", "S"),
            _post("other", "2026-02-15"),
            _post("p2", "2026-02-01", "S"),
            _post("p1", "2026-01-01", "S"),
        ],
        today=TODAY,
    )
    (series,) = build_series(posts)
    p1 = next(m for m, _ in posts if m["slug"] == "p1")
    end = str(_post_end(p1, posts, series))
    assert _links(end).count("/blog/p2") == 1
    assert "Newer" not in end
    # p2's newer post is not its next part, so both stay.
    p2 = next(m for m, _ in posts if m["slug"] == "p2")
    end = str(_post_end(p2, posts, series))
    assert "Newer" in end
    assert "/blog/other" in _links(end) and "/blog/p3" in _links(end)


def test_render_post_without_a_series_has_no_series_parts():
    """A fixture post with no ``series`` renders exactly as before."""
    jsx = str(_render_post({"title": "T", "slug": "t", "date": "2026-01-01"}, "Hi."))
    assert 'className:"series-box"' not in jsx
    assert 'className:"post-end-series"' not in jsx


def test_blog_index_lists_series_and_labels_cards():
    """The index names each series with its size, and labels its cards."""
    jsx = str(PAGES["blog"])
    nav = jsx[jsx.index('"aria-label":"Series"') :]
    for series in SERIES:
        assert json.dumps(series.route) in nav
        parts = "1 part" if len(series) == 1 else f"{len(series)} parts"
        assert f" \\u00b7 {parts}" in nav
    for meta in SERIES_POSTS:
        series = series_of(meta, SERIES)
        label = f"Part {series.number(meta['slug'])} of {len(series)} \\u00b7 "
        assert f"{label}{series.title}" in jsx


def test_json_ld_names_the_series():
    """A part's BlogPosting is ``isPartOf`` its series; a standalone is not."""
    data = blog_posting_data(
        route="/blog/x",
        title="X",
        description="d",
        date="2026-01-01",
        image="x.png",
        series=("Saucier", "/blog/series/saucier"),
    )
    assert data["isPartOf"] == {
        "@type": "CreativeWorkSeries",
        "name": "Saucier",
        "url": f"{SITE_URL}/blog/series/saucier",
    }
    plain = blog_posting_data(
        route="/blog/x", title="X", description="d", date="2026-01-01", image="x.png"
    )
    assert "isPartOf" not in plain


def test_series_is_a_value():
    """``Series`` is frozen and sized by its published parts."""
    series = Series(title="S", slug="s", parts=({"slug": "a", "date": "2026-01-01"},))
    assert len(series) == 1
    assert series.route == "/blog/series/s"
    with pytest.raises(ValueError):
        series.number("missing")
