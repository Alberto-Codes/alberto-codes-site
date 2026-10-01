"""Every page links the app icons and web manifest, and the files exist (#82).

The links travel in the app's ``head_components``, which Reflex adds to the
head of every route. The static export copies `src/assets/` to the site root,
so each root-relative ``href`` must name a file there.
"""

import json
from pathlib import Path

import pytest
from PIL import Image

from alberto_codes_site.alberto_codes_site import app

ASSETS = Path(__file__).resolve().parent.parent / "src" / "assets"


def _head_links() -> list[dict[str, str]]:
    """Return each head ``<link>`` as a dict of its attributes."""
    links = []
    for component in app.head_components:
        rendered = component.render()
        if rendered.get("name") != '"link"':
            continue
        attrs = {}
        for prop in rendered["props"]:
            key, _, value = prop.partition(":")
            attrs[key] = value.strip('"')
        links.append(attrs)
    return links


def _link(rel: str, href: str) -> dict[str, str]:
    """Return the head link with this ``rel`` and ``href``, failing if absent."""
    matches = [a for a in _head_links() if a["rel"] == rel and a["href"] == href]
    assert matches, f'no <link rel="{rel}" href="{href}"> in the app head'
    return matches[0]


@pytest.mark.parametrize(
    ("rel", "href"),
    [
        ("icon", "/favicon.ico"),
        ("icon", "/favicon.svg"),
        ("apple-touch-icon", "/apple-touch-icon.png"),
        ("manifest", "/site.webmanifest"),
    ],
)
def test_head_links_an_existing_asset(rel: str, href: str) -> None:
    """Each icon and manifest link points at a file under `src/assets/`."""
    _link(rel, href)
    assert (ASSETS / href.lstrip("/")).is_file(), f"missing src/assets{href}"


def test_svg_favicon_declares_its_type() -> None:
    """Browsers skip an SVG icon link without the SVG media type."""
    assert _link("icon", "/favicon.svg").get("type") == "image/svg+xml"


def test_apple_touch_icon_is_180_square() -> None:
    """The touch icon is the 180x180 PNG iOS uses for share and home screen."""
    with Image.open(ASSETS / "apple-touch-icon.png") as image:
        assert image.format == "PNG"
        assert image.size == (180, 180)


def test_manifest_lists_existing_icons_at_their_sizes() -> None:
    """The manifest has the basics, and each icon exists at its stated size."""
    manifest = json.loads((ASSETS / "site.webmanifest").read_text())
    for key in ("name", "short_name", "theme_color", "background_color"):
        assert manifest.get(key), f"manifest has no {key}"
    assert manifest["display"] in {"browser", "minimal-ui"}
    sizes = set()
    for icon in manifest["icons"]:
        with Image.open(ASSETS / icon["src"].lstrip("/")) as image:
            assert f"{image.width}x{image.height}" == icon["sizes"]
            sizes.add(icon["sizes"])
    assert {"192x192", "512x512"} <= sizes
