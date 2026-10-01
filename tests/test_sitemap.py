"""The sitemap is on the protocol namespace and lists every registered route.

Reflex's own plugin writes an ``https://`` namespace (issue #101). These
checks render the sitemap from the app's registered pages, the same input the
export uses, without a build or the network.
"""

import re
import xml.etree.ElementTree as ET

import pytest

from alberto_codes_site.alberto_codes_site import app
from alberto_codes_site.sitemap import (
    SITEMAP_NAMESPACE,
    SitemapPlugin,
    post_lastmod,
    sitemap_task,
    sitemap_xml,
)
from rxconfig import config

NS = {"sm": SITEMAP_NAMESPACE}
PAGES = list(app._unevaluated_pages.values())
ROOT = ET.fromstring(sitemap_xml(PAGES).encode())
URLS = ROOT.findall("sm:url", NS)


def _path(loc: str) -> str:
    """Return a sitemap ``loc`` as a route, without origin or slashes."""
    return re.sub(r"^https?://[^/]+", "", loc).strip("/")


def test_config_uses_the_namespace_fixing_plugin():
    """Rxconfig registers this module's plugin, not Reflex's."""
    plugins = [p for p in config.plugins if "Sitemap" in type(p).__name__]
    assert len(plugins) == 1
    assert isinstance(plugins[0], SitemapPlugin)


def test_root_is_urlset_on_the_protocol_namespace():
    """The root ``urlset`` is on the ``http://`` protocol namespace."""
    assert ROOT.tag == f"{{{SITEMAP_NAMESPACE}}}urlset"
    assert 'xmlns="https://' not in sitemap_xml(PAGES)


def test_task_writes_the_public_sitemap():
    """The save task writes the rendered sitemap to `sitemap.xml`."""
    path, xml_text = sitemap_task(PAGES)
    assert path.endswith("sitemap.xml")
    assert xml_text == sitemap_xml(PAGES)


def test_sitemap_lists_every_registered_route():
    """Each registered route but the 404 page appears exactly once."""
    listed = sorted(_path(url.findtext("sm:loc", namespaces=NS)) for url in URLS)
    registered = sorted(
        "" if p.route == "index" else p.route for p in PAGES if p.route != "404"
    )
    assert listed == registered


def test_every_post_has_a_lastmod_and_nothing_else_does():
    """Posts carry a `YYYY-MM-DD` lastmod; other routes omit it."""
    for url in URLS:
        route = _path(url.findtext("sm:loc", namespaces=NS))
        lastmod = url.findtext("sm:lastmod", namespaces=NS)
        if route.startswith("blog/"):
            assert lastmod is not None, route
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", lastmod), (route, lastmod)
        else:
            assert lastmod is None, route


@pytest.mark.parametrize(
    ("meta", "expected"),
    [
        ({"date": "2026-03-05"}, "2026-03-05"),
        ({"date": "2026-03-05", "updated": "2026-04-01"}, "2026-04-01"),
        ({"date": "2026-03-05", "updated": "soon"}, "2026-03-05"),
        ({"date": "March"}, None),
        ({}, None),
    ],
)
def test_post_lastmod_prefers_a_valid_updated_date(meta, expected):
    """A valid ``updated`` wins over ``date``; nothing valid gives None."""
    assert post_lastmod(meta) == expected
