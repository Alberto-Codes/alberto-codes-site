"""Main app entry point with route definitions and shared layout.

This module sets up the Reflex application with all routes for the portfolio site,
including home, blog, projects, experience, about, and contact pages. It provides
a shared layout wrapper that applies consistent navbar and footer components across all pages.

Examples:
    The app is initialized and pages are added with the shared layout:

    ```python
    from alberto_codes_site.alberto_codes_site import app
    ```

See Also:
    :py:func:`layout` : Wraps page components with shared navbar and footer
    :py:func:`navbar` : Navigation bar component
    :py:func:`footer` : Footer component
"""

import reflex as rx
from reflex.components.el.elements.inline import a as html_a

from alberto_codes_site.components import footer, navbar
from alberto_codes_site.feed import FEED_URL, write_feed
from alberto_codes_site.pages import (
    about_page,
    blog_page,
    blog_post_page,
    contact_page,
    experience_page,
    home_page,
    projects_page,
    publications_page,
)
from alberto_codes_site.pages.blog import _load_posts
from alberto_codes_site.social import (
    SITE_IMAGE,
    blog_posting_data,
    page_meta,
    person_data,
    post_image,
)
from alberto_codes_site.tenure import years_at_wells_fargo

MAIN_CONTENT_ID = "main-content"


def layout(page: rx.Component) -> rx.Component:
    """Wrap a page component with the shared navbar and footer.

    The first focusable element is a skip link to the ``<main>`` landmark;
    it stays visually hidden until keyboard focus reaches it (see
    ``assets/a11y.css``). It is a plain ``<a>``, not ``rx.el.a``: that one
    is a React Router link, which resolves ``#main-content`` against the
    route and moves neither scroll nor focus.

    Args:
        page: The page content to wrap.

    Returns:
        A vstack with a skip link, navbar, page content in ``<main>``, and footer.

    Examples:
        ```python
        app.add_page(layout(home_page()), route="/")
        ```
    """
    return rx.vstack(
        html_a(
            "Skip to content",
            href=f"#{MAIN_CONTENT_ID}",
            class_name="skip-link",
        ),
        navbar(),
        rx.el.main(page, id=MAIN_CONTENT_ID, tab_index=-1, flex="1", width="100%"),
        footer(),
        spacing="0",
        min_height="100vh",
        overflow_x="hidden",
        width="100%",
    )


app = rx.App(
    overlay_component=rx.fragment,
    enable_state=False,
    head_components=[
        # Feed autodiscovery on every page (#41).
        rx.el.link(
            rel="alternate",
            type="application/rss+xml",
            title="alberto.codes",
            href=FEED_URL,
        ),
    ],
    stylesheets=["/a11y.css"],
)

# Rebuilt on every import so `reflex run` and `reflex export` both ship a
# feed that matches today's date; Reflex copies src/assets/ afterwards.
write_feed(_load_posts())


def add_page(
    page: rx.Component,
    *,
    route: str,
    title: str,
    description: str,
    share_title: str | None = None,
    image: str = SITE_IMAGE,
    og_type: str = "website",
    structured_data: dict | None = None,
) -> None:
    """Register a laid-out page with its share tags and canonical link.

    Args:
        page: The page content, wrapped in the shared layout here.
        route: The page route.
        title: The browser tab title.
        description: The meta description, reused for the share card.
        share_title: The title on the share card; defaults to ``title``.
        image: The card PNG under `src/assets/og/`; the site card by default.
        og_type: `article` for posts, `website` otherwise.
        structured_data: A schema.org object to emit as JSON-LD, if any.
    """
    social = page_meta(
        route=route,
        title=share_title or title,
        description=description,
        image=image,
        og_type=og_type,
        structured_data=structured_data,
    )
    app.add_page(
        layout(page),
        route=route,
        title=title,
        description=description,
        **social,
    )


add_page(
    home_page(),
    route="/",
    title="Alberto Nieto | Generative AI Principal Engineer",
    description=(
        "Alberto Nieto is a Generative AI Principal Engineer at Wells Fargo, "
        f"where he has spent {years_at_wells_fargo()} years in financial "
        "services technology."
    ),
    structured_data=person_data(),
)
add_page(
    about_page(),
    route="/about",
    title="About | Alberto Nieto",
    description=(
        "Learn about Alberto Nieto's career journey from customer service "
        "to Principal Engineer, co-inventor on two pending patents, and AI leader."
    ),
)
add_page(
    experience_page(),
    route="/experience",
    title="Experience | Alberto Nieto",
    description=(
        f"{years_at_wells_fargo()} years of progressive career growth at "
        "Wells Fargo spanning customer service, analytics, and AI "
        "engineering leadership."
    ),
)
add_page(
    projects_page(),
    route="/projects",
    title="Projects | Alberto Nieto",
    description=(
        "Technical projects including saucier, vramfit, and gepa-adk, "
        "open-source Python and AI tooling, and enterprise AI/ML initiatives."
    ),
)
add_page(
    publications_page(),
    route="/publications",
    title="Publications | Alberto Nieto",
    description=(
        "Published artifacts with their attribution and evidence, including "
        "a mixed-precision quantization of Nemotron Super 49B fitted to a "
        "24 GiB GPU."
    ),
)
add_page(
    blog_page(),
    route="/blog",
    title="Blog | Alberto Nieto",
    description="Thoughts on AI engineering, career growth, and technical leadership.",
)
# Register individual blog post routes
for _meta, _ in _load_posts():
    _slug = _meta.get("slug", "")
    _title = _meta.get("title", "Blog Post")
    _summary = _meta.get("summary", "")
    _route = f"/blog/{_slug}"
    add_page(
        blog_post_page(_slug),
        route=_route,
        title=f"{_title} | Alberto Nieto",
        description=_summary,
        share_title=_title,
        image=post_image(_slug),
        og_type="article",
        structured_data=blog_posting_data(
            route=_route,
            title=_title,
            description=_summary,
            date=_meta.get("date", ""),
            image=post_image(_slug),
            updated=_meta.get("updated"),
        ),
    )

add_page(
    contact_page(),
    route="/contact",
    title="Contact | Alberto Nieto",
    description="Get in touch with Alberto Nieto via email, GitHub, or LinkedIn.",
)
