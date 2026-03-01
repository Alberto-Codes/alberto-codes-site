"""Home page with hero section and areas of expertise."""

import reflex as rx

EXPERTISE_TAGS = [
    "Generative AI & Agents",
    "Python",
    "Data Engineering & Pipelines",
    "Cloud (GCP, PCF)",
    "OCR & Document Intelligence",
    "CI/CD & DevOps",
    "Enterprise Architecture",
    "Technical Leadership",
]


def home_page() -> rx.Component:
    """Render the home page with hero section and expertise tags."""
    return rx.container(
        rx.vstack(
            rx.box(height="6em"),
            rx.image(
                src="/headshot.jpg",
                alt="Alberto Nieto",
                border_radius="100%",
                width=rx.breakpoints(initial="8em", md="10em"),
                height=rx.breakpoints(initial="8em", md="10em"),
                object_fit="cover",
                box_shadow="0 4px 12px rgba(0,0,0,0.15)",
            ),
            rx.text("Hello, I'm", size="4", color=rx.color("slate", 9)),
            rx.heading(
                "Alberto Nieto",
                size=rx.breakpoints(initial="7", md="9"),
                weight="bold",
            ),
            rx.heading(
                "Generative AI Principal Engineer",
                size=rx.breakpoints(initial="3", md="6"),
                weight="medium",
                color=rx.color("blue", 9),
                text_align="center",
            ),
            rx.text(
                "I started as a teller, taught myself to code, and spent "
                "25 years building my way to Principal Engineer. Now I "
                "design AI systems, ship open source tools, and bridge "
                "the gap between business problems and technical solutions.",
                size="3",
                color=rx.color("slate", 10),
                max_width=["100%", "100%", "36em", "36em", "36em"],
                text_align="center",
            ),
            rx.hstack(
                rx.hstack(
                    rx.icon("award", size=16, color=rx.color("blue", 9)),
                    rx.text("2x Top Performer", size="2", color=rx.color("slate", 10)),
                    spacing="1",
                    align="center",
                ),
                rx.hstack(
                    rx.icon("file-check", size=16, color=rx.color("blue", 9)),
                    rx.text(
                        "Patent Co-Inventor", size="2", color=rx.color("slate", 10)
                    ),
                    spacing="1",
                    align="center",
                ),
                rx.hstack(
                    rx.icon("building", size=16, color=rx.color("blue", 9)),
                    rx.text("25+ Years", size="2", color=rx.color("slate", 10)),
                    spacing="1",
                    align="center",
                ),
                rx.hstack(
                    rx.icon("package", size=16, color=rx.color("blue", 9)),
                    rx.text("3 PyPI Packages", size="2", color=rx.color("slate", 10)),
                    spacing="1",
                    align="center",
                ),
                spacing="5",
                flex_direction=["column", "column", "row", "row", "row"],
                align="center",
            ),
            rx.hstack(
                rx.link(
                    rx.button("View Projects", size="3"),
                    href="/projects",
                    underline="none",
                ),
                rx.link(
                    rx.button("Contact Me", variant="outline", size="3"),
                    href="/contact",
                    underline="none",
                ),
                spacing="4",
            ),
            rx.box(height="1em"),
            rx.heading("Areas of Expertise", size="3", weight="medium"),
            rx.flex(
                *[rx.badge(tag, variant="surface", size="2") for tag in EXPERTISE_TAGS],
                wrap="wrap",
                spacing="2",
                justify="center",
                max_width=["100%", "100%", "32em", "32em", "32em"],
            ),
            spacing="4",
            align="center",
            min_height="85vh",
            max_width="48em",
        ),
        size="3",
        padding_x=["4", "4", "0", "0", "0"],
        padding_y="6",
    )
