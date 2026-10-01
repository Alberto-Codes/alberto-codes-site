"""Open Graph and Twitter card metadata for every route.

Link previews on LinkedIn and X need absolute URLs, a large image and the
`og:*` / `twitter:*` tags. Reflex's `add_page` renders its ``image`` argument
as `og:image` only, so the rest arrive through its ``meta`` list.

The card images are committed PNGs under `src/assets/og/`, written by
`scripts/generate_og_images.py`; `tests/test_og_images.py` fails when a
published post has none.

Every route also carries a `<link rel="canonical">` (ADR-0004 points
syndicated copies at it) and, where one applies, a schema.org JSON-LD block.
Both travel as components in the same ``meta`` list: React hoists the
`<link>` into `<head>`, and the JSON-LD `<script>` stays in the prerendered
body, where crawlers read it just the same.

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

import json
from pathlib import Path

import reflex as rx

SITE_URL = "https://alberto.codes"
SITE_NAME = "alberto.codes"

OG_IMAGE_WIDTH = 1200
OG_IMAGE_HEIGHT = 630

# Served from the site root: `src/assets/og/<name>.png` -> `/og/<name>.png`.
OG_ASSET_DIR = Path(__file__).resolve().parent.parent / "assets" / "og"
SITE_IMAGE = "site.png"

AUTHOR_NAME = "Alberto Nieto"
# The home page heading and the footer's social links; keep them in step.
AUTHOR_JOB_TITLE = "Generative AI Principal Engineer"
AUTHOR_SAME_AS = (
    "https://github.com/Alberto-Codes",
    "https://www.linkedin.com/in/alberto-codes/",
)


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


def canonical_url(route: str) -> str:
    """Return the canonical absolute URL for a route.

    GitHub Pages answers both `/blog` and `/blog/` with a 200 and no
    redirect, so the form the sitemap lists wins: no trailing slash except
    on the root.

    Args:
        route: The page route, e.g. `/` or `/blog/<slug>`.

    Returns:
        The absolute URL shared by `og:url` and the canonical link.
    """
    return absolute_url(route if route == "/" else route.rstrip("/"))


def head_link(rel: str, href: str, **attrs: str) -> rx.Component:
    """Build a `<link>` for the ``meta`` list of ``add_page``.

    Args:
        rel: The link relation, e.g. `canonical` or `alternate`.
        href: The target URL.
        **attrs: Further attributes such as ``type`` or ``title``.

    Returns:
        A link component that React hoists into `<head>`.
    """
    return rx.el.link(rel=rel, href=href, **attrs)


def json_ld(data: dict) -> rx.Component:
    """Build a `<script type="application/ld+json">` for the ``meta`` list.

    The JSON goes in as raw inner HTML so React does not entity-escape its
    quotes, with `<` written as a JSON unicode escape so no value can close
    the script.

    Args:
        data: A schema.org object, including ``@context`` and ``@type``.

    Returns:
        A script component carrying the serialized JSON.
    """
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    return rx.el.script(
        type="application/ld+json",
        custom_attrs={"dangerouslySetInnerHTML": {"__html": payload}},
    )


def person_data() -> dict:
    """Return the schema.org `Person` for the site's author.

    Returns:
        A JSON-LD object with name, url, jobTitle and sameAs.
    """
    return {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": AUTHOR_NAME,
        "url": SITE_URL,
        "jobTitle": AUTHOR_JOB_TITLE,
        "sameAs": list(AUTHOR_SAME_AS),
    }


def blog_posting_data(
    *,
    route: str,
    title: str,
    description: str,
    date: str,
    image: str,
    updated: str | None = None,
) -> dict:
    """Return the schema.org `BlogPosting` for a post.

    Args:
        route: The post route, `/blog/<slug>`.
        title: The post title, used as the headline.
        description: The post summary.
        date: The frontmatter ``date``, `YYYY-MM-DD`.
        image: The post's card PNG file name under `src/assets/og/`.
        updated: The frontmatter ``updated`` date, when the post has one.

    Returns:
        A JSON-LD object; ``dateModified`` appears only with ``updated``.
    """
    url = canonical_url(route)
    data = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": title,
        "description": description,
        "datePublished": date,
        "author": {"@type": "Person", "name": AUTHOR_NAME, "url": SITE_URL},
        "image": absolute_url(f"/og/{image}"),
        "url": url,
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
    }
    if updated:
        data["dateModified"] = updated
    return data


def page_meta(
    *,
    route: str,
    title: str,
    description: str,
    image: str = SITE_IMAGE,
    og_type: str = "website",
    structured_data: dict | None = None,
) -> dict:
    """Build the ``image`` and ``meta`` keyword arguments for ``add_page``.

    Args:
        route: The page route, e.g. `/` or `/blog/<slug>`.
        title: The share title (no site suffix for posts).
        description: The share description.
        image: The PNG file name under `src/assets/og/`.
        og_type: `article` for posts, `website` otherwise.
        structured_data: A schema.org object to emit as JSON-LD, if any.

    Returns:
        A dict with ``image`` (absolute og:image URL) and ``meta`` (the
        remaining Open Graph and Twitter tags, the canonical link and any
        JSON-LD block).
    """
    image_url = absolute_url(f"/og/{image}")
    page_url = canonical_url(route)
    meta: list[dict | rx.Component] = [
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
        head_link("canonical", page_url),
    ]
    if structured_data is not None:
        meta.append(json_ld(structured_data))
    return {"image": image_url, "meta": meta}
