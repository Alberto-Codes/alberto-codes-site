"""Post dates read as "1 Oct 2026" inside ``<time datetime>``, with Updated dates.

Issue #83. Every registered page that shows a post date (the blog index,
home, each post, each series page) is walked without a build: each date is a
``time`` element with an ISO ``dateTime``, and no bare ISO date is left in
the page chrome. A post with a dated ``> Note YYYY-MM-DD:`` block shows
"Updated" with its latest note's date, and the sitemap ``<lastmod>`` and the
JSON-LD ``dateModified`` carry the same date, all from ``post_updated``.
"""

import re
import xml.etree.ElementTree as ET

import pytest
from reflex.components.component import Component
from reflex.components.datadisplay.code import CodeBlock
from reflex.components.markdown.markdown import Markdown

from alberto_codes_site.alberto_codes_site import app
from alberto_codes_site.dates import (
    note_dates,
    post_updated,
    readable_date,
    time_el,
)
from alberto_codes_site.pages.blog import _load_posts, published_posts
from alberto_codes_site.sitemap import SITEMAP_NAMESPACE, sitemap_xml

PAGES = {page.route: page for page in app._unevaluated_pages.values()}
POSTS = published_posts(_load_posts())
POST_ROUTES = {f"blog/{meta['slug']}": (meta, body) for meta, body in POSTS}
DATED_ROUTES = sorted(
    ["index", "blog", *POST_ROUTES, *(r for r in PAGES if r.startswith("blog/series/"))]
)
ISO = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
READABLE = re.compile(
    r"[1-9]\d? (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4}"
)


def _walk(component: Component, skip: tuple[type, ...] = ()):
    """Yield every component in the tree, depth first, leaving out ``skip``."""
    if isinstance(component, skip):
        return
    yield component
    for child in component.children:
        if isinstance(child, Component):
            yield from _walk(child, skip)


def _text(node: Component) -> str:
    """Return a ``Bare`` text node's string, without the JS quotes."""
    return str(node.contents).strip('"')


def _times(component: Component) -> list[tuple[str, str]]:
    """Return ``(dateTime, text)`` for each ``time`` element, in order."""
    found = []
    for node in _walk(component):
        if node.tag != "time":
            continue
        props = node.render()["props"]
        stamps = [p.split(":", 1)[1].strip('"') for p in props if "dateTime" in p]
        texts = [_text(c) for c in node.children if type(c).__name__ == "Bare"]
        found.append(((stamps or [""])[0], "".join(texts)))
    return found


def _component(route: str) -> Component:
    page = PAGES[route].component
    return page if isinstance(page, Component) else page()


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2026-10-01", "1 Oct 2026"),
        ("2026-03-27", "27 Mar 2026"),
        ("2026-12-31", "31 Dec 2026"),
        ("soon", "soon"),
    ],
)
def test_readable_date(value, expected):
    """ISO dates read as day, short month, year; anything else is kept."""
    assert readable_date(value) == expected


def test_time_element_carries_the_iso_date():
    """``time_el`` renders the readable text with the ISO ``dateTime``."""
    assert _times(time_el("2026-10-01")) == [("2026-10-01", "1 Oct 2026")]


@pytest.mark.parametrize(
    ("meta", "body", "expected"),
    [
        ({"date": "2026-09-02"}, "Body.", None),
        (
            {"date": "2026-09-02"},
            "> Note 2026-09-04: x\n\n> Note 2026-09-06: y",
            "2026-09-06",
        ),
        (
            {"date": "2026-09-02"},
            "> Note 2026-09-06: x\n\n> Note 2026-09-04: y",
            "2026-09-06",
        ),
        (
            {"date": "2026-09-02", "updated": "2026-09-10"},
            "> Note 2026-09-04: x",
            "2026-09-10",
        ),
        (
            {"date": "2026-09-02", "updated": "2026-09-03"},
            "> Note 2026-09-04: x",
            "2026-09-04",
        ),
        ({"date": "2026-09-02", "updated": "2026-09-05"}, "Body.", "2026-09-05"),
        ({"date": "2026-09-02", "updated": "2026-09-02"}, "Body.", None),
        ({"date": "2026-09-02", "updated": "soon"}, "Body.", None),
        ({"date": "2026-09-02"}, "A Note 2026-09-04: inline, not a block.", None),
    ],
)
def test_post_updated_takes_the_later_of_notes_and_frontmatter(meta, body, expected):
    """The later of the newest note and ``updated``, only when after ``date``."""
    assert post_updated(meta, body) == expected


@pytest.mark.parametrize("route", DATED_ROUTES)
def test_every_date_is_a_readable_time_element(route):
    """Each date shown is a ``time``; no bare ISO date is left in the chrome."""
    page = _component(route)
    times = _times(page)
    assert times, route
    for stamp, text in times:
        assert ISO.fullmatch(stamp), (route, stamp)
        assert text == readable_date(stamp), (route, stamp, text)
        assert READABLE.fullmatch(text), (route, text)
    # Post bodies are left as written; only the page chrome is checked.
    for node in _walk(page, skip=(Markdown, CodeBlock)):
        if type(node).__name__ == "Bare":
            assert not ISO.search(_text(node)), (route, _text(node)[:80])


@pytest.mark.parametrize("route", sorted(POST_ROUTES))
def test_post_header_shows_the_date_and_any_updated_date(route):
    """The header carries the post date, then "Updated" from ``post_updated``."""
    meta, body = POST_ROUTES[route]
    page = _component(route)
    assert _times(page)[0] == (meta["date"], readable_date(meta["date"]))
    updated_lines = [
        node for node in _walk(page) if "post-updated" in str(node.class_name or "")
    ]
    updated = post_updated(meta, body)
    if updated is None:
        assert not updated_lines, route
        return
    (line,) = updated_lines
    assert _text(line.children[0]) == "Updated "
    assert _times(line) == [(updated, readable_date(updated))]
    notes = note_dates(body)
    if notes:
        assert updated >= max(notes).isoformat()


def test_posts_with_notes_show_their_latest_note_date():
    """Every post carrying a dated note is shown as updated on its latest one."""
    noted = {r: (m, b) for r, (m, b) in POST_ROUTES.items() if note_dates(b)}
    assert noted, "expected at least one post with a dated note"
    for route, (meta, body) in noted.items():
        latest = max(note_dates(body)).isoformat()
        if not meta.get("updated"):
            assert post_updated(meta, body) == latest, route


def test_sitemap_and_json_ld_agree_with_the_header():
    """``<lastmod>`` and ``dateModified`` are the post's updated date."""
    ns = {"sm": SITEMAP_NAMESPACE}
    root = ET.fromstring(sitemap_xml(list(PAGES.values())).encode())
    lastmods = {
        re.sub(r"^https?://[^/]+/", "", url.findtext("sm:loc", namespaces=ns)): (
            url.findtext("sm:lastmod", namespaces=ns)
        )
        for url in root.findall("sm:url", ns)
    }
    for route, (meta, body) in POST_ROUTES.items():
        updated = post_updated(meta, body)
        assert lastmods[route] == (updated or meta["date"]), route
        (ld,) = [
            str(m.render())
            for m in PAGES[route].meta
            if isinstance(m, Component) and "ld+json" in str(m.render())
        ]
        modified = re.findall(r'dateModified\\+": \\+"([\d-]+)', ld)
        assert modified == ([updated] if updated else []), route
