"""Site footer component."""

import reflex as rx


def footer() -> rx.Component:
    """Render the site footer with copyright and social links."""
    return rx.box(
        rx.hstack(
            rx.text(
                "\u00a9 2026 Alberto Nieto. All rights reserved.",
                size="2",
                color=rx.color("slate", 9),
            ),
            rx.spacer(),
            rx.hstack(
                rx.link(
                    rx.icon("github", size=18),
                    href="https://github.com/Alberto-Codes",
                    is_external=True,
                    color=rx.color("slate", 9),
                ),
                rx.link(
                    rx.icon("linkedin", size=18),
                    href="https://www.linkedin.com/in/alberto-codes/",
                    is_external=True,
                    color=rx.color("slate", 9),
                ),
                spacing="4",
            ),
            width="100%",
            align="center",
            flex_direction=["column", "column", "row", "row", "row"],
            gap="4",
        ),
        padding_x=["4", "4", "6", "8", "8"],
        padding_y="6",
        border_top=f"1px solid {rx.color('gray', 4)}",
        width="100%",
    )
