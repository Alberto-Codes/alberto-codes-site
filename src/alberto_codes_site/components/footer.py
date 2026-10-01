"""Site footer component."""

import reflex as rx

from alberto_codes_site.components.navbar import SIDE_PADDING


def footer() -> rx.Component:
    """Render the site footer with copyright and social links."""
    return rx.box(
        rx.hstack(
            rx.text(
                "\u00a9 2026 Alberto Nieto. All rights reserved.",
                size="2",
                color=rx.color("slate", 11),
            ),
            rx.spacer(),
            rx.hstack(
                rx.link(
                    rx.icon("github", size=18),
                    href="https://github.com/Alberto-Codes",
                    is_external=True,
                    aria_label="GitHub",
                    color=rx.color("slate", 11),
                ),
                rx.link(
                    rx.icon("linkedin", size=18),
                    href="https://www.linkedin.com/in/alberto-codes/",
                    is_external=True,
                    aria_label="LinkedIn",
                    color=rx.color("slate", 11),
                ),
                spacing="4",
            ),
            width="100%",
            align="center",
            flex_direction=["column", "column", "row", "row", "row"],
            gap="4",
        ),
        padding_x=SIDE_PADDING,
        padding_y="var(--space-6)",
        border_top=f"1px solid {rx.color('gray', 4)}",
        width="100%",
    )
