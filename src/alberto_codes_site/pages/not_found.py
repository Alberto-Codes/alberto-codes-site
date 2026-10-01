"""Not-found page shown for any route the site does not have.

Reflex registers it at its ``404`` route; the static export writes it to
``404.html``, which GitHub Pages serves for every unknown path.
"""

import reflex as rx

from alberto_codes_site.components.button_link import button_link

NOT_FOUND_LINKS = [
    ("Home", "/"),
    ("Blog", "/blog"),
    ("Projects", "/projects"),
]


def not_found_page() -> rx.Component:
    """Render the 404 page with a short message and links back into the site.

    Returns:
        A container with the page title, a friendly message, and buttons to
        Home, Blog and Projects.

    Examples:
        ```python
        app.add_page(layout(not_found_page()), route="404")
        ```
    """
    return rx.container(
        rx.vstack(
            rx.box(height="4em"),
            rx.text("404", size="2", weight="medium", color=rx.color("blue", 11)),
            rx.heading("Page not found", as_="h1", size="8", weight="bold"),
            rx.separator(size="4", color_scheme="blue"),
            rx.text(
                "That link leads nowhere. The page may have moved, or the "
                "address may have a typo. These will get you back on track:",
                size="3",
                color=rx.color("slate", 11),
            ),
            rx.box(height="1em"),
            rx.flex(
                *[
                    button_link(
                        label,
                        href=href,
                        variant="solid" if index == 0 else "outline",
                        size="3",
                    )
                    for index, (label, href) in enumerate(NOT_FOUND_LINKS)
                ],
                spacing="4",
                wrap="wrap",
            ),
            rx.box(height="4em"),
            spacing="4",
            max_width="48em",
        ),
        size="3",
        padding_y="6",
    )
