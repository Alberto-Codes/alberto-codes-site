"""The `/llms.txt` index is generated from the site's own data (llmstxt.org)."""

import re
from datetime import date

from alberto_codes_site.alberto_codes_site import app  # noqa: F401  (writes the file)
from alberto_codes_site.llms import LLMS_FILE, RECENT_POST_COUNT, build_llms_txt
from alberto_codes_site.pages.blog import _load_posts, published_posts
from alberto_codes_site.pages.projects import PROJECTS

TEXT = build_llms_txt(_load_posts())
LINK = re.compile(r"^- \[[^\]]+\]\(([^)]+)\)", re.MULTILINE)


def test_import_writes_the_served_file():
    """Importing the app writes `src/assets/llms.txt`, which Reflex serves at the root."""
    assert LLMS_FILE.read_text(encoding="utf-8") == TEXT


def test_starts_with_h1_then_summary_blockquote():
    """The spec's order: an H1 name, then a `>` summary."""
    lines = TEXT.splitlines()
    assert lines[0] == "# Alberto Nieto"
    assert lines[2].startswith("> ")


def test_site_links_are_absolute():
    """Pages and posts link to https://alberto.codes; project links are https too."""
    pages = TEXT.split("## Pages\n", 1)[1].split("## Open source projects", 1)[0]
    posts = TEXT.split("## Selected posts\n", 1)[1]
    for url in LINK.findall(pages) + LINK.findall(posts):
        assert url.startswith("https://alberto.codes/"), url
    assert all(url.startswith("https://") for url in LINK.findall(TEXT))


def test_lists_every_open_source_project():
    """Each project card with a repository appears once."""
    for project in PROJECTS:
        if "github" in project:
            assert TEXT.count(f"- [{project['title']}](") == 1


def test_posts_are_the_newest_published():
    """The post list follows the blog, newest first, and skips future posts."""
    posts = _load_posts()
    newest = published_posts(posts)[:RECENT_POST_COUNT]
    section = TEXT.split("## Selected posts\n", 1)[1]
    urls = LINK.findall(section)
    assert urls == [f"https://alberto.codes/blog/{m['slug']}" for m, _ in newest]
    early = build_llms_txt(posts, today=date(2026, 3, 1))
    assert "2026-10-28" not in early
