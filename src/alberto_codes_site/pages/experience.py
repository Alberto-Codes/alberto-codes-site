"""Experience page with career timeline."""

import reflex as rx

from alberto_codes_site.layout import PAGE_COLUMN, PAGE_PADDING_Y
from alberto_codes_site.tenure import years_at_wells_fargo

ROLES = [
    {
        "title": "Principal Engineer (Executive Director)",
        "company": "Wells Fargo",
        "period": "Jul 2025 - Present",
        "location": "Phoenix, Arizona",
        "bullets": [
            "Created AI agent framework to automate line-of-business operations, "
            "adopted across multiple teams",
            "Fine-tuned Gemma 3 and Gemma 4 on internal documents, building the "
            "training set from a graph of entities and relationships, with "
            "held-out evaluation",
            "Building decision models for collections and customer-service "
            "next-best-action",
            "Built video processing pipeline handling thousands of videos daily",
            "Co-inventor on three pending patent applications",
            "Open source: shipped gepa-adk, docvet, adk-secure-sessions, "
            "saucier, vramfit, turboquant-vllm, typevet, and judgevet to PyPI",
        ],
    },
    {
        "title": "Senior Lead Analytics Consultant (Executive Director)",
        "company": "Wells Fargo",
        "period": "Jun 2022 - Jul 2025",
        "location": "Phoenix, Arizona",
        "bullets": [
            "Architected scalable OCR pipeline processing 500K+ documents using Gemini",
            "The team's go-to engineer for GenAI and agentic AI frameworks, "
            "including Google ADK and Pydantic-AI",
            "Built reusable data pipelines for document ingestion, OCR, and validation",
            "Designed modular, scalable architecture reused across multiple teams",
            "Implemented git-based dev workflow with peer reviews and release standards",
        ],
    },
    {
        "title": "Lead Analytics Consultant (AVP)",
        "company": "Wells Fargo",
        "period": "Jan 2018 - Jun 2022",
        "location": "Phoenix, Arizona",
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
            "Built and presented a SharePoint hosting solution",
        ],
    },
]


def timeline_item(role: dict) -> rx.Component:
    """Render a single timeline entry for a career role.

    Args:
        role: Dict with keys "title", "company", "period", "location", and "bullets".

    Returns:
        A timeline entry with one visible outcome and expandable role details.

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
    outcome, *other_work = role["bullets"]
    return rx.vstack(
        rx.text(
            f"{role['period']} · {role['company']}",
            size="2",
            color=rx.color("gray", 11),
        ),
        rx.heading(role["title"], as_="h2", size="4"),
        rx.text(outcome, size="3"),
        rx.el.details(
            rx.el.summary(
                "Role details",
                aria_label=f"Role details for {role['title']}",
                color=rx.color("accent", 11),
                cursor="pointer",
                font_weight="500",
            ),
            rx.text(role["location"], size="2", margin_top="var(--space-2)")
            if role["location"]
            else "",
            rx.el.ul(
                *[rx.el.li(bullet) for bullet in other_work],
                padding_inline_start="1.25em",
                list_style_type="disc",
            ),
            color=rx.color("gray", 11),
            font_size="var(--font-size-2)",
            line_height="1.6",
        ),
        width="100%",
        spacing="2",
        padding_y="var(--space-4)",
        border_top=f"1px solid {rx.color('gray', 6)}",
    )


def experience_page() -> rx.Component:
    """Render the experience page with career timeline."""
    return rx.container(
        rx.vstack(
            rx.heading("Experience", as_="h1", size="8", weight="bold"),
            rx.separator(size="4", color_scheme="gray"),
            rx.text(
                "From banking operations to enterprise AI, including "
                f"{years_at_wells_fargo()} years at Wells Fargo.",
                size="3",
                color=rx.color("gray", 11),
            ),
            rx.vstack(
                *[timeline_item(role) for role in ROLES],
                spacing="0",
                width="100%",
            ),
            rx.card(
                rx.vstack(
                    rx.heading("Education", as_="h2", size="4", weight="bold"),
                    rx.text(
                        "DeVry University",
                        size="3",
                        weight="medium",
                    ),
                    rx.text(
                        "Bachelor of Science, Accounting Information Systems",
                        size="2",
                        color=rx.color("gray", 11),
                    ),
                    spacing="1",
                ),
                width="100%",
            ),
            spacing="4",
            **PAGE_COLUMN,
        ),
        size="3",
        padding_y=PAGE_PADDING_Y,
    )
