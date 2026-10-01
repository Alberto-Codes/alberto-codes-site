"""Open Graph and Twitter card metadata for every route.

Link previews on LinkedIn and X need absolute URLs, a large image and the
`og:*` / `twitter:*` tags. Reflex's `add_page` renders its ``image`` argument
as `og:image` only, so the rest arrive through its ``meta`` list.

The card images are committed PNGs under `src/assets/og/`, written by
`scripts/generate_og_images.py`; `tests/test_og_images.py` fails when a
published post has none.

Examples:
    ```python
    from alberto_codes_site.social import page_meta, post_image

    app.add_page(
        page,
        route="/blog/x",
        **page_meta(
            route="/blog/x",
            title="X",
            description="...",
            image=post_image("x"),
            og_type="article",
        ),
    )
    ```
"""

from pathlib import Path

SITE_URL = "https://alberto.codes"
SITE_NAME = "alberto.codes"

OG_IMAGE_WIDTH = 1200
OG_IMAGE_HEIGHT = 630

# Served from the site root: `src/assets/og/<name>.png` -> `/og/<name>.png`.
OG_ASSET_DIR = Path(__file__).resolve().parent.parent / "assets" / "og"
SITE_IMAGE = "site.png"


def post_image(slug: str) -> str:
    """Return the card image file name for a post slug.

    Args:
        slug: The post slug, i.e. its markdown file stem.

    Returns:
        The PNG file name under `src/assets/og/`.
    """
    return f"{slug}.png"


def absolute_url(path: str) -> str:
    """Join a site-root path onto the production origin.

    Args:
        path: A path starting with `/`.

    Returns:
        The absolute URL on https://alberto.codes.
    """
    return SITE_URL + path


def page_meta(
    *,
    route: str,
    title: str,
    description: str,
    image: str = SITE_IMAGE,
    og_type: str = "website",
) -> dict:
    """Build the ``image`` and ``meta`` keyword arguments for ``add_page``.

    Args:
        route: The page route, e.g. `/` or `/blog/<slug>`.
        title: The share title (no site suffix for posts).
        description: The share description.
        image: The PNG file name under `src/assets/og/`.
        og_type: `article` for posts, `website` otherwise.

    Returns:
        A dict with ``image`` (absolute og:image URL) and ``meta`` (the
        remaining Open Graph and Twitter tags).
    """
    image_url = absolute_url(f"/og/{image}")
    page_url = absolute_url(route if route == "/" else route.rstrip("/"))
    meta = [
        {"property": "og:title", "content": title},
        {"property": "og:description", "content": description},
        {"property": "og:type", "content": og_type},
        {"property": "og:url", "content": page_url},
        {"property": "og:site_name", "content": SITE_NAME},
        {"property": "og:image:width", "content": str(OG_IMAGE_WIDTH)},
        {"property": "og:image:height", "content": str(OG_IMAGE_HEIGHT)},
        {"property": "og:image:alt", "content": title},
        {"name": "twitter:card", "content": "summary_large_image"},
        {"name": "twitter:title", "content": title},
        {"name": "twitter:description", "content": description},
        {"name": "twitter:image", "content": image_url},
        {"name": "twitter:image:alt", "content": title},
    ]
    return {"image": image_url, "meta": meta}
