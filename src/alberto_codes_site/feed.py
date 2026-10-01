"""Full-content RSS 2.0 feed for the blog, served at `/feed.xml`.

The feed is generated whenever the app module is imported (`reflex run` and
`reflex export` both do this before Reflex copies `src/assets/` into the web
build), so it is rebuilt on every deploy and never committed: a future-dated
post joins the feed on the first build on or after its date. The output file,
`src/assets/feed.xml`, is gitignored.

Each item carries the post body rendered to HTML in ``content:encoded``. Links
and images in the body are rewritten to absolute URLs on the production
origin. Theme-aware figures (ADR-0005) are inlined into the site's pages, but
a feed reader has no site CSS, so the feed keeps them as ``<img>`` pointing at
the SVG file; the SVG's own `prefers-color-scheme` fallback styles it there.

Examples:
    ```python
    from alberto_codes_site.feed import build_feed
    from alberto_codes_site.pages.blog import _load_posts

    xml_text = build_feed(_load_posts())
    ```
"""

import re
import xml.etree.ElementTree as ET
from datetime import UTC, date, datetime
from email.utils import format_datetime
from pathlib import Path

from markdown_it import MarkdownIt

from alberto_codes_site.social import SITE_NAME, absolute_url

FEED_PATH = "/feed.xml"
FEED_URL = absolute_url(FEED_PATH)
FEED_FILE = Path(__file__).resolve().parent.parent / "assets" / "feed.xml"

CHANNEL_DESCRIPTION = (
    "Thoughts on AI engineering, Python, career growth, and technical leadership."
)

_CONTENT_NS = "http://purl.org/rss/1.0/modules/content/"
_ATOM_NS = "http://www.w3.org/2005/Atom"
ET.register_namespace("content", _CONTENT_NS)
ET.register_namespace("atom", _ATOM_NS)

# `src="/x"` / `href="/x"` (site-rooted, not protocol-relative) and `href="#x"`.
_ROOTED_ATTR = re.compile(r'(\s(?:src|href)=")(/(?!/)[^"]*)"')
_FRAGMENT_ATTR = re.compile(r'(\shref=")(#[^"]*)"')

_markdown = MarkdownIt("commonmark", {"html": True}).enable(["table", "strikethrough"])


def post_date(meta: dict) -> date | None:
    """Return a post's frontmatter date, or None when it is missing or malformed.

    Args:
        meta: The post's frontmatter.

    Returns:
        The parsed `YYYY-MM-DD` date, or None.
    """
    try:
        return date.fromisoformat(str(meta.get("date", "")).strip())
    except ValueError:
        return None


def published_posts(
    posts: list[tuple[dict, str]], *, today: date | None = None
) -> list[tuple[dict, str]]:
    """Keep only posts whose date has arrived.

    ``_load_posts`` already drops `draft-*.md` files; this also drops posts
    dated after ``today`` and posts without a valid date.

    Args:
        posts: ``(meta, body)`` pairs from ``_load_posts``.
        today: The build date; defaults to the current date.

    Returns:
        The published posts, newest first.
    """
    today = today or date.today()
    dated = [(post_date(m), m, b) for m, b in posts]
    kept = [(d, m, b) for d, m, b in dated if d is not None and d <= today]
    kept.sort(key=lambda item: item[0], reverse=True)
    return [(m, b) for _, m, b in kept]


def body_html(body: str, page_url: str) -> str:
    """Render a markdown post body to HTML with absolute links and images.

    Args:
        body: The post's markdown body.
        page_url: The post's absolute URL, used to resolve `#fragment` links.

    Returns:
        The HTML for ``content:encoded``.
    """
    rendered = _markdown.render(body)
    rendered = _ROOTED_ATTR.sub(lambda m: f'{m[1]}{absolute_url(m[2])}"', rendered)
    return _FRAGMENT_ATTR.sub(lambda m: f'{m[1]}{page_url}{m[2]}"', rendered)


def _rfc822(day: date) -> str:
    return format_datetime(datetime(day.year, day.month, day.day, tzinfo=UTC), True)


def build_feed(posts: list[tuple[dict, str]], *, today: date | None = None) -> str:
    """Build the RSS 2.0 document for the published posts.

    ``lastBuildDate`` is the newest published post's date rather than the clock
    time, so rebuilding unchanged content yields identical bytes.

    Args:
        posts: ``(meta, body)`` pairs from ``_load_posts``.
        today: The build date; posts dated after it are left out.

    Returns:
        The feed as an XML string with declaration.
    """
    items = published_posts(posts, today=today)

    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = SITE_NAME
    ET.SubElement(channel, "link").text = absolute_url("/blog")
    ET.SubElement(channel, "description").text = CHANNEL_DESCRIPTION
    ET.SubElement(channel, "language").text = "en-us"
    if items:
        newest = post_date(items[0][0])
        ET.SubElement(channel, "lastBuildDate").text = _rfc822(newest)
    ET.SubElement(
        channel,
        f"{{{_ATOM_NS}}}link",
        {"href": FEED_URL, "rel": "self", "type": "application/rss+xml"},
    )

    for meta, body in items:
        url = absolute_url(f"/blog/{meta.get('slug', '')}")
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = meta.get("title", "Untitled")
        ET.SubElement(item, "link").text = url
        ET.SubElement(item, "guid", {"isPermaLink": "true"}).text = url
        ET.SubElement(item, "pubDate").text = _rfc822(post_date(meta))
        ET.SubElement(item, "description").text = meta.get("summary", "")
        ET.SubElement(item, f"{{{_CONTENT_NS}}}encoded").text = body_html(body, url)

    ET.indent(rss)
    return ET.tostring(rss, encoding="unicode", xml_declaration=True) + "\n"


def write_feed(
    posts: list[tuple[dict, str]], path: Path = FEED_FILE, *, today: date | None = None
) -> Path:
    """Write the feed to the assets directory, skipping an unchanged file.

    Leaving an identical file untouched keeps `reflex run` from seeing a
    change on every import.

    Args:
        posts: ``(meta, body)`` pairs from ``_load_posts``.
        path: Where to write; `src/assets/feed.xml` by default.
        today: The build date; posts dated after it are left out.

    Returns:
        The path written.
    """
    xml_text = build_feed(posts, today=today)
    if not path.is_file() or path.read_text(encoding="utf-8") != xml_text:
        path.write_text(xml_text, encoding="utf-8")
    return path
