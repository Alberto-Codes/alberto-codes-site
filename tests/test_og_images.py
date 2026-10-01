"""Every rendered page shares with an absolute, existing 1200x630 card.

The cards are committed rather than built in CI, so a new post that lands
without its PNG would share a broken preview. Generate missing cards with
`uv run python scripts/generate_og_images.py`.
"""

import pytest
from PIL import Image

from alberto_codes_site.pages.blog import _load_posts
from alberto_codes_site.social import (
    OG_ASSET_DIR,
    OG_IMAGE_HEIGHT,
    OG_IMAGE_WIDTH,
    SITE_IMAGE,
    SITE_URL,
    page_meta,
    post_image,
)

CARDS = [SITE_IMAGE] + [post_image(meta["slug"]) for meta, _ in _load_posts()]


@pytest.mark.parametrize("name", CARDS)
def test_card_exists_at_share_size(name: str) -> None:
    """The site card and each published post's card are 1200x630 PNGs."""
    path = OG_ASSET_DIR / name
    assert path.exists(), (
        f"missing {path}; run `uv run python scripts/generate_og_images.py` and commit it"
    )
    with Image.open(path) as image:
        assert image.format == "PNG"
        assert image.size == (OG_IMAGE_WIDTH, OG_IMAGE_HEIGHT)


def test_drafts_get_no_card() -> None:
    """Drafts never render, so they are not in the set that needs a card."""
    assert not any(name.startswith("draft-") for name in CARDS)


def test_page_meta_uses_absolute_urls() -> None:
    """og:image, twitter:image and og:url point at the production origin."""
    social = page_meta(
        route="/blog/x",
        title="T",
        description="D",
        image=post_image("x"),
        og_type="article",
    )
    tags = {
        m.get("property") or m.get("name"): m["content"]
        for m in social["meta"]
        if isinstance(m, dict)
    }
    assert social["image"] == f"{SITE_URL}/og/x.png"
    assert tags["twitter:image"] == social["image"]
    assert tags["og:url"] == f"{SITE_URL}/blog/x"
    assert tags["og:type"] == "article"
    assert tags["twitter:card"] == "summary_large_image"
    assert tags["og:image:width"] == "1200"
    assert tags["og:image:height"] == "630"
