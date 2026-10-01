"""About page with a professional summary."""

import reflex as rx

from alberto_codes_site.layout import PAGE_COLUMN, PAGE_PADDING_Y
from alberto_codes_site.tenure import years_at_wells_fargo


def about_page() -> rx.Component:
    """Render the about page with a headshot and professional summary."""
    return rx.container(
        rx.vstack(
            rx.box(height="4em"),
            rx.heading("About Me", as_="h1", size="8", weight="bold"),
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
                        f"Wells Fargo with {years_at_wells_fargo()} years at the "
                        "company. My career "
                        "journey started in customer service and banking operations, "
                        "and through continuous learning and a passion for technology, "
                        "I've grown into a principal-level engineering role leading "
                        "enterprise AI initiatives.",
                        size="3",
                        color=rx.color("slate", 11),
                        line_height="1.8",
                    ),
                    rx.text(
                        "I hold a Bachelor of Science in Accounting Information "
                        "Systems from DeVry University, which gives me a perspective "
                        "that bridges business and technology. I'm a co-inventor on "
                        "two pending patent applications, I'm a "
                        "two-time Top Performer award recipient, and I'm bilingual "
                        "in English and Spanish.",
                        size="3",
                        color=rx.color("slate", 11),
                        line_height="1.8",
                    ),
                    rx.text(
                        "Outside of my enterprise work, I build and publish open "
                        "source Python tools \u2014 including docvet for docstring "
                        "quality, adk-secure-sessions for encrypted AI agent "
                        "storage, gepa-adk for evolutionary prompt optimization, "
                        "saucier for provenance-traced recipe extraction, "
                        "vramfit for fitting large models onto one GPU, "
                        "turboquant-vllm for KV cache compression, typevet "
                        "for typed answers from open models, and judgevet "
                        "for TypeSafe's Jev. All eight are on PyPI.",
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
            spacing="4",
            **PAGE_COLUMN,
        ),
        size="3",
        padding_y=PAGE_PADDING_Y,
    )
