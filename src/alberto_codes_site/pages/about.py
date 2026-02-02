"""About page with professional summary and key stats."""

import reflex as rx


def stat_card(value: str, label: str) -> rx.Component:
    """Render a stat card with a highlighted value and label.

    Args:
        value: The highlighted stat value (e.g. "25+").
        label: Description below the value (e.g. "Years of Experience").

    Returns:
        A card component displaying the stat.

    Examples:
        ```python
        stat_card("25+", "Years at Wells Fargo")
        ```
    """
    return rx.card(
        rx.vstack(
            rx.heading(value, size="7", weight="bold", color=rx.color("blue", 9)),
            rx.text(label, size="2", color=rx.color("slate", 10)),
            align="center",
            spacing="1",
        ),
        width="100%",
    )


def about_page() -> rx.Component:
    """Render the about page with professional summary and stats."""
    return rx.container(
        rx.vstack(
            rx.box(height="4em"),
            rx.heading("About Me", size="8", weight="bold"),
            rx.separator(size="4", color_scheme="blue"),
            rx.box(height="1em"),
            rx.hstack(
                rx.image(
                    src="/headshot.jpg",
                    alt="Alberto Nieto",
                    border_radius="var(--radius-3)",
                    width="12em",
                    height="12em",
                    object_fit="cover",
                    flex_shrink="0",
                    box_shadow="0 4px 12px rgba(0,0,0,0.15)",
                    display=rx.breakpoints(initial="none", md="block"),
                ),
                rx.vstack(
                    rx.text(
                        "I'm Alberto Nieto, a Generative AI Principal Engineer at "
                        "Wells Fargo with over 25 years at the company. My career "
                        "journey started in customer service and banking operations, "
                        "and through continuous learning and a passion for technology, "
                        "I've grown into a principal-level engineering role leading "
                        "enterprise AI initiatives.",
                        size="3",
                        color=rx.color("slate", 11),
                        line_height="1.8",
                    ),
                    rx.text(
                        "I'm a detail oriented individual who can relate technology "
                        "to business initiatives and use creativity to drive "
                        "solutions. I hold a Bachelor of Science in Accounting "
                        "Information Systems from DeVry University, and I bring a "
                        "unique perspective that bridges business and technology.",
                        size="3",
                        color=rx.color("slate", 11),
                        line_height="1.8",
                    ),
                    spacing="4",
                ),
                spacing="6",
                align="start",
                width="100%",
            ),
            rx.text(
                "I was recently named as a co-inventor on my first patent "
                "application. I'm a two-time Wells Fargo Top Performer "
                "award recipient and bilingual in English and Spanish.",
                size="3",
                color=rx.color("slate", 11),
                line_height="1.8",
            ),
            rx.box(height="2em"),
            rx.heading("By the Numbers", size="5", weight="medium"),
            rx.grid(
                stat_card("25+", "Years at Wells Fargo"),
                stat_card("Patent", "Co-Inventor"),
                stat_card("2x", "Top Performer Award"),
                stat_card("Principal", "Engineer Level"),
                columns=rx.breakpoints(initial="2", md="4"),
                spacing="4",
                width="100%",
            ),
            spacing="4",
            max_width="48em",
        ),
        size="3",
        padding_y="6",
    )
