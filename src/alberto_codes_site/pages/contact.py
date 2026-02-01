"""Contact page with links to email, GitHub, and LinkedIn."""

import reflex as rx


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
                        color=rx.color("slate", 9),
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
            rx.heading("Contact", size="8", weight="bold"),
            rx.separator(size="4", color_scheme="blue"),
            rx.text(
                "Feel free to reach out.",
                size="3",
                color=rx.color("slate", 10),
            ),
            rx.box(height="2em"),
            rx.vstack(
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
                    "https://www.linkedin.com/in/alberto-nieto-5937511",
                ),
                contact_link(
                    "file-text",
                    "Resume",
                    "/Alberto_Nieto_Resume.pdf",
                ),
                spacing="3",
                width="100%",
                max_width="28em",
            ),
            spacing="4",
            max_width="48em",
        ),
        size="3",
        padding_y="6",
    )
