"""Site footer component."""

import reflex as rx

from alberto_codes_site.components.navbar import SIDE_PADDING


def footer() -> rx.Component:
    """Render the site footer, on the same cloth as the masthead.

    The cloth colours live in ``assets/identity.css`` (``.cloth``).
    """
    return rx.box(
        rx.hstack(
            rx.text(
                "© 2026 Alberto Nieto. All rights reserved.",
                size="2",
                color="var(--cloth-ink)",
            ),
            rx.spacer(),
            rx.hstack(
                rx.link(
                    rx.icon("github", size=18),
                    href="https://github.com/Alberto-Codes",
                    is_external=True,
                    aria_label="GitHub",
                    color="var(--cloth-ink)",
                ),
                rx.link(
                    rx.icon("linkedin", size=18),
                    href="https://www.linkedin.com/in/alberto-codes/",
                    is_external=True,
                    aria_label="LinkedIn",
                    color="var(--cloth-ink)",
                ),
                spacing="4",
            ),
            width="100%",
            align="center",
            flex_direction=["column", "column", "row", "row", "row"],
            gap="4",
        ),
        class_name="cloth",
        padding_x=SIDE_PADDING,
        padding_y="var(--space-6)",
        width="100%",
    )
