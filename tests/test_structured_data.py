"""Canonical links, JSON-LD and robots.txt for search engines.

The static export is checked by hand in the pull request; these tests pin
the helpers in `alberto_codes_site.social` that feed it.
"""

import json
from pathlib import Path

import pytest

from alberto_codes_site.pages.blog import _load_posts
from alberto_codes_site.social import (
    AUTHOR_SAME_AS,
    SITE_URL,
    blog_posting_data,
    canonical_url,
    json_ld,
    page_meta,
    person_data,
    post_image,
)

ASSETS = Path(__file__).resolve().parent.parent / "src" / "assets"
FOOTER = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "alberto_codes_site"
    / "components"
    / "footer.py"
)


def _rendered(component) -> str:
    """Return a component's compiled JSX as a string."""
    return str(component.render())


@pytest.mark.parametrize(
    ("route", "url"),
    [
        ("/", "https://alberto.codes/"),
        ("/blog", "https://alberto.codes/blog"),
        ("/blog/", "https://alberto.codes/blog"),
        ("/blog/x", "https://alberto.codes/blog/x"),
    ],
)
def test_canonical_url_drops_trailing_slash_except_root(route: str, url: str) -> None:
    """Canonical URLs match the sitemap's form: no trailing slash but `/`."""
    assert canonical_url(route) == url


def test_page_meta_canonical_agrees_with_og_url() -> None:
    """Every page carries one canonical link, equal to its og:url."""
    meta = page_meta(route="/blog/", title="Blog", description="d")["meta"]
    og_url = next(m["content"] for m in meta if m.get("property") == "og:url")
    links = [_rendered(m) for m in meta if not isinstance(m, dict)]
    assert len(links) == 1
    assert '"canonical"' in links[0]
    assert f'"{og_url}"' in links[0]


def test_page_meta_appends_json_ld_only_when_given() -> None:
    """Pages without structured data get no JSON-LD block."""
    plain = page_meta(route="/about", title="t", description="d")["meta"]
    with_ld = page_meta(
        route="/", title="t", description="d", structured_data=person_data()
    )["meta"]
    assert len(with_ld) == len(plain) + 1
    assert "application/ld+json" in _rendered(with_ld[-1])


def test_json_ld_escapes_script_close() -> None:
    """A `</script>` inside a value cannot end the block early."""
    rendered = _rendered(json_ld({"headline": "a </script> b"}))
    assert "</script>" not in rendered
    assert "u003c/script>" in rendered


def test_person_data_has_required_fields() -> None:
    """The home page Person names the author, the site and the footer links."""
    data = person_data()
    assert data["@context"] == "https://schema.org"
    assert data["@type"] == "Person"
    assert data["name"] == "Alberto Nieto"
    assert data["url"] == SITE_URL
    assert data["jobTitle"] == "Generative AI Principal Engineer"
    assert data["sameAs"] == list(AUTHOR_SAME_AS)
    json.dumps(data)


def test_same_as_matches_footer_links() -> None:
    """The Person's sameAs repeats the footer's profile links, so the two cannot drift."""
    footer = FOOTER.read_text()
    for url in AUTHOR_SAME_AS:
        assert f'href="{url}"' in footer


POSTS = [meta for meta, _ in _load_posts()]


@pytest.mark.parametrize("meta", POSTS, ids=[m["slug"] for m in POSTS])
def test_blog_posting_for_every_post(meta: dict) -> None:
    """Each published post's BlogPosting has the fields Google asks for."""
    slug = meta["slug"]
    route = f"/blog/{slug}"
    data = blog_posting_data(
        route=route,
        title=meta["title"],
        description=meta["summary"],
        date=meta["date"],
        image=post_image(slug),
        updated=meta.get("updated"),
    )
    assert data["@type"] == "BlogPosting"
    assert data["headline"] == meta["title"]
    assert data["datePublished"] == meta["date"]
    assert data["author"] == {
        "@type": "Person",
        "name": "Alberto Nieto",
        "url": SITE_URL,
    }
    assert data["image"] == f"{SITE_URL}/og/{slug}.png"
    assert data["mainEntityOfPage"]["@id"] == canonical_url(route)
    assert ("dateModified" in data) == bool(meta.get("updated"))
    json.dumps(data)


def test_blog_posting_date_modified_from_updated() -> None:
    """An `updated` frontmatter date becomes dateModified."""
    data = blog_posting_data(
        route="/blog/x",
        title="X",
        description="d",
        date="2026-01-01",
        image="x.png",
        updated="2026-02-01",
    )
    assert data["dateModified"] == "2026-02-01"


def test_robots_txt_allows_all_and_points_at_sitemap() -> None:
    """robots.txt, served from the site root, names the absolute sitemap."""
    lines = (ASSETS / "robots.txt").read_text().splitlines()
    assert "User-agent: *" in lines
    assert "Allow: /" in lines
    assert f"Sitemap: {SITE_URL}/sitemap.xml" in lines
