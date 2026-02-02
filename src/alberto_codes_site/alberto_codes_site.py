"""Main app entry point with route definitions and shared layout."""

import reflex as rx

from alberto_codes_site.components import footer, navbar
from alberto_codes_site.pages import (
    about_page,
    blog_page,
    blog_post_page,
    contact_page,
    experience_page,
    home_page,
    projects_page,
)
from alberto_codes_site.pages.blog import _load_posts


def layout(page: rx.Component) -> rx.Component:
    """Wrap a page component with the shared navbar and footer.

    Args:
        page: The page content to wrap.

    Returns:
        A vstack with navbar, page content, and footer.

    Examples:
        ```python
        app.add_page(layout(home_page()), route="/")
        ```
    """
    return rx.vstack(
        navbar(),
        rx.box(page, flex="1", width="100%"),
        footer(),
        spacing="0",
        min_height="100vh",
        overflow_x="hidden",
        width="100%",
    )


app = rx.App(
    overlay_component=rx.fragment,
    enable_state=False,
)
app.add_page(
    layout(home_page()),
    route="/",
    title="Alberto Nieto | Generative AI Principal Engineer",
    description=(
        "Alberto Nieto is a Generative AI Principal Engineer at Wells Fargo "
        "with 25+ years in financial services technology."
    ),
)
app.add_page(
    layout(about_page()),
    route="/about",
    title="About | Alberto Nieto",
    description=(
        "Learn about Alberto Nieto's career journey from customer service "
        "to Principal Engineer, patent co-inventor, and AI leader."
    ),
)
app.add_page(
    layout(experience_page()),
    route="/experience",
    title="Experience | Alberto Nieto",
    description=(
        "25+ years of progressive career growth at Wells Fargo spanning "
        "customer service, analytics, and AI engineering leadership."
    ),
)
app.add_page(
    layout(projects_page()),
    route="/projects",
    title="Projects | Alberto Nieto",
    description=(
        "Technical projects including gepa-adk, an open-source AI agent "
        "optimization library, and enterprise AI/ML initiatives."
    ),
)
app.add_page(
    layout(blog_page()),
    route="/blog",
    title="Blog | Alberto Nieto",
    description="Thoughts on AI engineering, career growth, and technical leadership.",
)
# Register individual blog post routes
for _meta, _ in _load_posts():
    _slug = _meta.get("slug", "")
    _title = _meta.get("title", "Blog Post")
    _summary = _meta.get("summary", "")
    app.add_page(
        layout(blog_post_page(_slug)),
        route=f"/blog/{_slug}",
        title=f"{_title} | Alberto Nieto",
        description=_summary,
    )

app.add_page(
    layout(contact_page()),
    route="/contact",
    title="Contact | Alberto Nieto",
    description="Get in touch with Alberto Nieto via email, GitHub, or LinkedIn.",
)
