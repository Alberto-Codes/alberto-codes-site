"""Experience page with career timeline."""

import reflex as rx

ROLES = [
    {
        "title": "Principal Engineer (Executive Director)",
        "company": "Wells Fargo",
        "period": "Jul 2025 - Present",
        "location": "Chandler, Arizona - Hybrid",
        "bullets": [
            "Lead generative AI engineering initiatives at enterprise scale",
            "Co-inventor on patent application",
            "Skills: Artificial Intelligence, Python, and more",
        ],
    },
    {
        "title": "Senior Lead Analytics Consultant (Executive Director)",
        "company": "Wells Fargo",
        "period": "Jun 2022 - Jul 2025",
        "location": "Chandler, Arizona - Hybrid",
        "bullets": [
            "Led analytics and AI-driven solutions for enterprise functions",
            "Skills: Git, Python, and more",
        ],
    },
    {
        "title": "Lead Analytic Consultant (AVP)",
        "company": "Wells Fargo",
        "period": "Jan 2018 - Jun 2023",
        "location": "",
        "bullets": [
            "Delivered analytics solutions and CI/CD workflow automation",
            "Skills: Pivotal Cloud Foundry (PCF), IBM UrbanCode Deploy, and more",
        ],
    },
    {
        "title": "Additional Roles (13 total at Wells Fargo)",
        "company": "Wells Fargo",
        "period": "2000 - 2018",
        "location": "",
        "bullets": [
            "Progressive career spanning customer service, operations, "
            "business analysis, and engineering",
            "Two-time Top Performer award recipient (2014, 2018)",
            "Built deep domain expertise in financial services technology",
        ],
    },
    {
        "title": "Customer Service Representative",
        "company": "Bank of America",
        "period": "Jun 1999 - Aug 2000",
        "location": "Phoenix, Arizona",
        "bullets": [
            "Operated cash drawer for various banking transactions",
            "Assisted with audit procedures",
        ],
    },
]


def timeline_item(role: dict) -> rx.Component:
    """Render a single timeline entry for a career role.

    Args:
        role: Dict with keys "title", "company", "period", "location", and "bullets".

    Returns:
        An hstack with timeline indicator and role card.

    Examples:
        ```python
        timeline_item(
            {
                "title": "Engineer",
                "company": "Acme",
                "period": "2020-2023",
                "location": "",
                "bullets": ["Led team"],
            }
        )
        ```
    """
    return rx.hstack(
        rx.vstack(
            rx.box(
                width="12px",
                height="12px",
                border_radius="50%",
                background_color=rx.color("blue", 9),
                flex_shrink="0",
            ),
            rx.box(
                width="2px",
                flex="1",
                background_color=rx.color("gray", 5),
            ),
            align="center",
            height="100%",
        ),
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.heading(role["title"], size="4", weight="bold"),
                    rx.spacer(),
                    rx.badge(role["period"], variant="surface", size="1"),
                    width="100%",
                    align="center",
                    flex_direction=["column", "column", "row", "row", "row"],
                    gap="2",
                ),
                rx.text(role["company"], size="2", color=rx.color("slate", 9)),
                *(
                    [
                        rx.text(
                            role["location"],
                            size="1",
                            color=rx.color("slate", 8),
                        )
                    ]
                    if role["location"]
                    else []
                ),
                rx.vstack(
                    *[
                        rx.hstack(
                            rx.text(
                                "\u2022",
                                color=rx.color("blue", 9),
                                flex_shrink="0",
                            ),
                            rx.text(bullet, size="2", color=rx.color("slate", 11)),
                            align="start",
                        )
                        for bullet in role["bullets"]
                    ],
                    spacing="1",
                ),
                spacing="2",
            ),
            width="100%",
        ),
        align="start",
        spacing="4",
        width="100%",
    )


def experience_page() -> rx.Component:
    """Render the experience page with career timeline."""
    return rx.container(
        rx.vstack(
            rx.box(height="4em"),
            rx.heading("Experience", size="8", weight="bold"),
            rx.separator(size="4", color_scheme="blue"),
            rx.text(
                "25+ years in financial services technology "
                "- from customer service to Principal Engineer.",
                size="3",
                color=rx.color("slate", 10),
            ),
            rx.box(height="1em"),
            rx.vstack(
                *[timeline_item(role) for role in ROLES],
                spacing="4",
                width="100%",
            ),
            rx.box(height="2em"),
            rx.card(
                rx.vstack(
                    rx.heading("Education", size="4", weight="bold"),
                    rx.text(
                        "DeVry University",
                        size="3",
                        weight="medium",
                    ),
                    rx.text(
                        "Bachelor of Science, Accounting Information Systems",
                        size="2",
                        color=rx.color("slate", 11),
                    ),
                    rx.text(
                        "1998 - 2003",
                        size="2",
                        color=rx.color("slate", 9),
                    ),
                    spacing="1",
                ),
                width="100%",
            ),
            spacing="4",
            max_width="48em",
        ),
        size="3",
        padding_y="6",
    )
