"""Contact page with links to email, GitHub, and LinkedIn."""

import reflex as rx

from alberto_codes_site.layout import PAGE_COLUMN, PAGE_PADDING_Y, READING_WIDTH


def contact_link(icon_name: str, label: str, href: str) -> rx.Component:
    """Render a contact link card with an icon and label.

    Args:
        icon_name: Lucide icon name (e.g. "github", "mail").
        label: Display label for the link.
        href: URL or mailto link target.

    Returns:
        A clickable card component with icon and text.

    Examples:
        ```python
        contact_link("github", "GitHub", "https://github.com/Alberto-Codes")
        ```
    """
    return rx.link(
        rx.card(
            rx.hstack(
                rx.icon(icon_name, size=24, color=rx.color("blue", 9)),
                rx.vstack(
                    rx.text(label, size="3", weight="medium"),
                    rx.text(
                        href.replace("mailto:", "")
                        .replace("https://", "")
                        .replace("/Alberto_Nieto_Resume.pdf", "Download PDF"),
                        size="2",
                        color=rx.color("slate", 11),
                    ),
                    spacing="1",
                ),
                spacing="4",
                align="center",
            ),
            width="100%",
        ),
        href=href,
        is_external=True,
        underline="none",
        width="100%",
    )


def contact_page() -> rx.Component:
    """Render the contact page."""
    return rx.container(
        rx.vstack(
            rx.box(height="4em"),
            rx.heading("Contact", as_="h1", size="8", weight="bold"),
            rx.separator(size="4", color_scheme="blue"),
            rx.box(height="1em"),
            rx.text(
                "Email is the best way to reach me. Questions about a post, a "
                "bug in one of the open source tools, or a correction to "
                "something I measured are all welcome. For a bug or a feature "
                "request, an issue on the tool's GitHub repository reaches me "
                "just as well, and it helps the next person who runs into it.",
                size="3",
                color=rx.color("slate", 11),
                line_height="1.8",
                max_width=READING_WIDTH,
            ),
            rx.grid(
                contact_link(
                    "mail",
                    "Email",
                    "mailto:alberto.codes.dev@gmail.com",
                ),
                contact_link(
                    "github",
                    "GitHub",
                    "https://github.com/Alberto-Codes",
                ),
                contact_link(
                    "linkedin",
                    "LinkedIn",
                    "https://www.linkedin.com/in/alberto-codes/",
                ),
                contact_link(
                    "file-text",
                    "Resume",
                    "/Alberto_Nieto_Resume.pdf",
                ),
                columns=rx.breakpoints(initial="1", md="2"),
                spacing="3",
                width="100%",
            ),
            spacing="4",
            **PAGE_COLUMN,
        ),
        size="3",
        padding_y=PAGE_PADDING_Y,
    )
