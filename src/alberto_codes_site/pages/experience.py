"""Experience page with career timeline."""

import reflex as rx

ROLES = [
    {
        "title": "Principal Engineer (Executive Director)",
        "company": "Wells Fargo",
        "period": "Jul 2025 - Present",
        "location": "Chandler, Arizona - Hybrid",
        "bullets": [
            "Lead generative AI engineering initiatives presented to CTO weekly",
            "Created AI agent framework to automate line-of-business operations",
            "Built video processing pipeline handling thousands of videos daily",
            "Co-inventor on patent application",
            "Open source: shipped gepa-adk, docvet, and adk-secure-sessions to PyPI",
        ],
    },
    {
        "title": "Senior Lead Analytics Consultant (Executive Director)",
        "company": "Wells Fargo",
        "period": "Jun 2022 - Jul 2025",
        "location": "Chandler, Arizona - Hybrid",
        "bullets": [
            "Team's resident expert in GenAI and Agentic AI frameworks "
            "including Google ADK and Pydantic-AI",
            "Architected scalable OCR pipeline processing 500K+ documents using Gemini",
            "Built reusable data pipelines for document ingestion, OCR, and validation",
            "Designed modular, scalable architecture reused across multiple teams",
            "Implemented git-based dev workflow with peer reviews and release standards",
        ],
    },
    {
        "title": "Lead Analytics Consultant (AVP)",
        "company": "Wells Fargo",
        "period": "Jan 2018 - Jun 2022",
        "location": "Chandler, Arizona",
        "bullets": [
            "Delivered analytics solutions and CI/CD workflow automation",
            "Onboarded applications to Cloud Foundry with Splunk logging "
            "and security compliance",
            "Created dynamic databases for automated and manual data ingestion",
        ],
    },
    {
        "title": "Technology Manager & Systems Engineer (AVP)",
        "company": "Wells Fargo",
        "period": "2006 - 2018",
        "location": "Phoenix, Arizona",
        "bullets": [
            "Led 8-9 technicians supporting end-user technology across four "
            "admin sites",
            "Led desktop OS migrations and provided onsite hardware swap support",
            "Created business intelligence reporting for regulatory compliance",
            "Two-time Top Performer award recipient (2014, 2018)",
        ],
    },
    {
        "title": "Operations & Banking (early career)",
        "company": "Wells Fargo / Bank of America",
        "period": "1999 - 2006",
        "location": "Phoenix, Arizona",
        "bullets": [
            "Progressed from teller to operations analyst to leadership "
            "development program in 5 years",
            "Selected for Wells Fargo Leadership Development Program (2004-2005)",
            "Presented SharePoint hosting solution to technology executive leadership",
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
                "From banking operations to enterprise AI "
                "\u2014 a 25-year career built at Wells Fargo.",
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
