"""The styled 404 page: registered, linked back into the site, kept unindexed.

The heading checks in `test_heading_structure.py` cover this route too; the
static export's `404.html` is checked by hand in the pull request.
"""

from alberto_codes_site.alberto_codes_site import MAIN_CONTENT_ID, app
from alberto_codes_site.pages import not_found_page
from alberto_codes_site.sitemap import sitemap_xml

PAGE = app._unevaluated_pages["404"]


def test_404_route_uses_the_custom_page():
    """The app supplies its own 404, so Reflex does not add its plain default."""
    rendered = str(PAGE.component.render())
    assert "Page not found" in rendered
    assert "404: Page not found" not in rendered


def test_404_page_has_the_shared_layout():
    """The skip link and the main landmark come from the shared layout."""
    rendered = str(PAGE.component.render())
    assert f"#{MAIN_CONTENT_ID}" in rendered
    assert "'name': '\"main\"'" in rendered


def test_404_page_links_home_blog_and_projects():
    """A lost visitor gets a way to Home, Blog and Projects in the page body."""
    rendered = str(not_found_page().render())
    for href in ('"/"', '"/blog"', '"/projects"'):
        assert href in rendered


def test_404_page_has_no_canonical_and_is_noindex():
    """No canonical link claims a real URL, and search engines skip the page."""
    rendered_meta = [
        str(m) if isinstance(m, dict) else str(m.render()) for m in PAGE.meta
    ]
    assert not any("canonical" in m for m in rendered_meta)
    assert {"name": "robots", "content": "noindex"} in PAGE.meta


def test_404_page_is_not_in_the_sitemap():
    """The sitemap lists real pages only."""
    xml_text = sitemap_xml(list(app._unevaluated_pages.values()))
    assert "<loc>" in xml_text
    assert "/404<" not in xml_text
