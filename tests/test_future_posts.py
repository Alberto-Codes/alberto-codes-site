"""A post dated after the build date is hidden everywhere; one dated today is not.

The blog index, home's "Latest writing", the registered post routes (which
Reflex turns into the sitemap) and the RSS feed share one date rule
(``published_posts``). The build date is injected so the test never depends
on the real clock.
"""

from datetime import date

import pytest
import reflex as rx

from alberto_codes_site import alberto_codes_site as site
from alberto_codes_site.feed import build_feed
from alberto_codes_site.pages import blog, home
from alberto_codes_site.social import SITE_URL

TODAY = date(2026, 10, 1)
TODAY_SLUG = "2026-10-01-published-today"
FUTURE_SLUG = "2026-10-02-dated-tomorrow"


def _write_post(directory, slug: str, day: str) -> None:
    (directory / f"{slug}.md").write_text(
        f"---\ntitle: {slug}\ndate: {day}\nsummary: A fake post.\n"
        "type: explanation\n---\n\nBody text.\n"
    )


@pytest.fixture
def fake_posts(tmp_path, monkeypatch):
    """Point the blog loader at a directory holding today's and tomorrow's post."""
    _write_post(tmp_path, TODAY_SLUG, "2026-10-01")
    _write_post(tmp_path, FUTURE_SLUG, "2026-10-02")
    monkeypatch.setattr(blog, "POSTS_DIR", tmp_path)
    return tmp_path


def test_blog_index_hides_future_posts(fake_posts) -> None:
    """The /blog index lists today's post and not tomorrow's."""
    rendered = str(blog.blog_page(today=TODAY))
    assert f"/blog/{TODAY_SLUG}" in rendered
    assert FUTURE_SLUG not in rendered


def test_home_latest_hides_future_posts(fake_posts) -> None:
    """Home's "Latest writing" lists today's post and not tomorrow's."""
    slugs = [meta["slug"] for meta in home._latest_posts(TODAY)]
    assert slugs == [TODAY_SLUG]


def test_post_routes_hide_future_posts(fake_posts, monkeypatch) -> None:
    """Only today's post gets a route, so only it reaches the sitemap."""
    app = rx.App(enable_state=False)
    monkeypatch.setattr(site, "app", app)
    site.add_post_pages(today=TODAY)
    routes = {page.route for page in app._unevaluated_pages.values()}
    assert routes == {f"blog/{TODAY_SLUG}"}


def test_feed_hides_future_posts(fake_posts) -> None:
    """The feed carries today's post and not tomorrow's."""
    xml_text = build_feed(blog._load_posts(), today=TODAY)
    assert f"{SITE_URL}/blog/{TODAY_SLUG}" in xml_text
    assert FUTURE_SLUG not in xml_text


def test_drafts_and_future_posts_still_load(fake_posts) -> None:
    """The loader keeps future posts (their share cards ship early); drafts never load."""
    _write_post(fake_posts, "draft-unfinished", "2026-09-01")
    slugs = {meta["slug"] for meta, _ in blog._load_posts()}
    assert slugs == {TODAY_SLUG, FUTURE_SLUG}
