"""The RSS feed is well-formed, absolute, and leaves out posts not yet dated."""

import xml.etree.ElementTree as ET
from datetime import date

from alberto_codes_site.feed import FEED_URL, build_feed, write_feed
from alberto_codes_site.pages.blog import _load_posts
from alberto_codes_site.social import SITE_URL

CONTENT = "{http://purl.org/rss/1.0/modules/content/}encoded"
ATOM_LINK = "{http://www.w3.org/2005/Atom}link"
TODAY = date(2026, 10, 1)

FAKE_POSTS = [
    (
        {
            "slug": "2026-10-02-from-the-future",
            "title": "Not yet",
            "date": "2026-10-02",
            "summary": "Tomorrow's post.",
        },
        "Should not appear.",
    ),
    (
        {
            "slug": "2026-10-01-today",
            "title": "Today & <tags>",
            "date": "2026-10-01",
            "summary": "Published today.",
        },
        "See [the blog](/blog), [below](#end) and [GitHub](https://github.com).\n\n"
        "![A chart](/chart.svg)\n\n"
        "| a | b |\n|---|---|\n| 1 | 2 |\n\n"
        "```\nx < y && ]]>\n```\n",
    ),
    (
        {
            "slug": "2026-09-01-older",
            "title": "Older",
            "date": "2026-09-01",
            "summary": "Last month.",
        },
        "Plain.",
    ),
    ({"slug": "undated", "title": "No date"}, "Never in the feed."),
]


def _channel(xml_text: str) -> ET.Element:
    root = ET.fromstring(xml_text.encode("utf-8"))
    assert root.tag == "rss" and root.get("version") == "2.0"
    return root.find("channel")


def test_future_dated_and_undated_posts_are_excluded() -> None:
    """Only posts dated on or before the build date appear, newest first."""
    channel = _channel(build_feed(FAKE_POSTS, today=TODAY))
    links = [item.findtext("link") for item in channel.findall("item")]
    assert links == [
        f"{SITE_URL}/blog/2026-10-01-today",
        f"{SITE_URL}/blog/2026-09-01-older",
    ]


def test_future_post_joins_once_its_date_arrives() -> None:
    """The same source yields the future post on the next day's build."""
    channel = _channel(build_feed(FAKE_POSTS, today=date(2026, 10, 2)))
    assert len(channel.findall("item")) == 3


def test_channel_and_item_fields() -> None:
    """The channel and each item carry the required RSS 2.0 fields."""
    channel = _channel(build_feed(FAKE_POSTS, today=TODAY))
    assert channel.findtext("link") == f"{SITE_URL}/blog"
    assert channel.findtext("language") == "en-us"
    assert channel.findtext("lastBuildDate") == "Thu, 01 Oct 2026 00:00:00 GMT"
    self_link = channel.find(ATOM_LINK)
    assert self_link.get("rel") == "self" and self_link.get("href") == FEED_URL

    item = channel.find("item")
    assert item.findtext("title") == "Today & <tags>"
    assert item.findtext("guid") == item.findtext("link")
    assert item.find("guid").get("isPermaLink") == "true"
    assert item.findtext("pubDate") == "Thu, 01 Oct 2026 00:00:00 GMT"
    assert item.findtext("description") == "Published today."


def test_body_html_has_absolute_urls_and_survives_escaping() -> None:
    """Links and figures in content:encoded point at the production origin."""
    item = _channel(build_feed(FAKE_POSTS, today=TODAY)).find("item")
    html = item.findtext(CONTENT)
    assert f'href="{SITE_URL}/blog"' in html
    assert f'href="{SITE_URL}/blog/2026-10-01-today#end"' in html
    assert 'href="https://github.com"' in html
    assert f'<img src="{SITE_URL}/chart.svg" alt="A chart"' in html
    assert "<table>" in html
    assert "x &lt; y &amp;&amp; ]]&gt;" in html
    assert 'href="/' not in html and 'src="/' not in html
    assert "<svg" not in html


def test_real_feed_parses_and_every_url_is_absolute() -> None:
    """The feed built from the real posts parses and links only absolutely."""
    channel = _channel(build_feed(_load_posts()))
    items = channel.findall("item")
    assert items
    for item in items:
        assert item.findtext("link").startswith(f"{SITE_URL}/blog/")
        html = item.findtext(CONTENT)
        assert html
        assert 'href="/' not in html and 'src="/' not in html
        assert "<svg" not in html


def test_drafts_are_not_in_the_feed() -> None:
    """`draft-*.md` files never reach the feed."""
    links = [
        i.findtext("link") for i in _channel(build_feed(_load_posts())).iter("item")
    ]
    assert not any("/blog/draft-" in link for link in links)


def test_write_feed_is_stable(tmp_path) -> None:
    """Rebuilding unchanged content leaves the file's bytes untouched."""
    path = tmp_path / "feed.xml"
    write_feed(FAKE_POSTS, path, today=TODAY)
    first = path.read_bytes()
    mtime = path.stat().st_mtime_ns
    write_feed(FAKE_POSTS, path, today=TODAY)
    assert path.read_bytes() == first
    assert path.stat().st_mtime_ns == mtime
