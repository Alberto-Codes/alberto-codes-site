"""Contact page with a direct email address, profiles and resume."""

import reflex as rx

from alberto_codes_site.layout import PAGE_COLUMN, PAGE_PADDING_Y, READING_WIDTH

EMAIL_ADDRESS = "alberto.codes.dev@gmail.com"


def contact_page() -> rx.Component:
    """Render the primary email link and secondary profile and resume links."""
    return rx.container(
        rx.vstack(
            rx.box(height="4em"),
            rx.heading("Contact", as_="h1", size="8", weight="bold"),
            rx.separator(size="4", color_scheme="gray"),
            rx.vstack(
                rx.text("Email is the best way to reach me.", size="3"),
                rx.link(
                    EMAIL_ADDRESS,
                    href=f"mailto:{EMAIL_ADDRESS}",
                    reload_document=True,
                    size=rx.breakpoints(initial="5", md="7"),
                    weight="medium",
                    overflow_wrap="anywhere",
                    max_width="100%",
                ),
                spacing="1",
                margin_top="var(--space-3)",
                width="100%",
            ),
            rx.text(
                "Questions about a post, a bug in one of the open source tools, "
                "or a correction to something I measured are all welcome. For "
                "a bug or a feature request, an issue on the tool's GitHub "
                "repository reaches me just as well, and it helps the next "
                "person who runs into it.",
                size="3",
                color=rx.color("gray", 11),
                line_height="1.8",
                max_width=READING_WIDTH,
            ),
            rx.flex(
                *[
                    rx.link(
                        rx.icon(icon, size=16),
                        label,
                        href=href,
                        is_external=True,
                        display="inline-flex",
                        align_items="center",
                        gap="var(--space-2)",
                        padding_y="var(--space-2)",
                        size="2",
                        weight="medium",
                    )
                    for icon, label, href in (
                        ("github", "GitHub", "https://github.com/Alberto-Codes"),
                        (
                            "linkedin",
                            "LinkedIn",
                            "https://www.linkedin.com/in/alberto-codes/",
                        ),
                        ("file-text", "Resume (PDF)", "/Alberto_Nieto_Resume.pdf"),
                    )
                ],
                wrap="wrap",
                column_gap="var(--space-5)",
                padding_top="var(--space-2)",
                border_top=f"1px solid {rx.color('gray', 6)}",
                width="100%",
            ),
            spacing="4",
            **PAGE_COLUMN,
        ),
        size="3",
        padding_y=PAGE_PADDING_Y,
    )
