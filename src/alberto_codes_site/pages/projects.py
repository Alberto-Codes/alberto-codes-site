"""Projects page with card grid of key technical work."""

import reflex as rx

PROJECTS = [
    {
        "title": "gepa-adk",
        "description": (
            "Open-source Python library that evolves AI agent instructions "
            "automatically. Give it an agent and training examples, and it "
            "finds better prompts through iterative improvement using "
            "evolutionary optimization with Google ADK."
        ),
        "tags": ["Generative AI", "Google ADK", "Python", "PyPI"],
        "link": "https://pypi.org/project/gepa-adk/",
        "docs": "https://alberto-codes.github.io/gepa-adk/",
        "github": "https://github.com/Alberto-Codes/gepa-adk",
    },
    {
        "title": "AI Agent Framework",
        "description": (
            "Designed and built an enterprise generative AI agent framework "
            "adopted by multiple teams. Standardized how LLM-powered agents "
            "are built, tested, and deployed with built-in guardrails, "
            "observability, and prompt management."
        ),
        "tags": ["Generative AI", "LLM", "Python", "Architecture"],
    },
    {
        "title": "OCR Document Pipeline",
        "description": (
            "Architected a scalable document processing pipeline that "
            "handled 500K+ documents. Automated classification, data "
            "extraction, and validation, replacing a manual review process "
            "and significantly reducing turnaround time."
        ),
        "tags": ["OCR", "ML", "Python", "Cloud"],
    },
    {
        "title": "Video Processing Pipeline",
        "description": (
            "Built an automated video processing system for analysis and "
            "content extraction at enterprise scale. Designed the end-to-end "
            "architecture from ingestion through output delivery."
        ),
        "tags": ["Computer Vision", "Python", "Automation"],
    },
    {
        "title": "CI/CD Workflow Design",
        "description": (
            "Designed end-to-end CI/CD pipelines for ML model deployment "
            "across multiple environments. Established testing, versioning, "
            "and monitoring standards that became the team's baseline for "
            "all new projects."
        ),
        "tags": ["DevOps", "CI/CD", "MLOps", "Cloud"],
    },
]


def _project_links(link: str, docs: str, github: str) -> list[rx.Component]:
    """Build a list of link components for a project card.

    Args:
        link: URL to the project (e.g. PyPI). Empty string to omit.
        docs: URL to the documentation site. Empty string to omit.
        github: URL to the GitHub repository. Empty string to omit.

    Returns:
        A list containing an hstack of links, or an empty list.

    Examples:
        ```python
        _project_links(
            "https://pypi.org/project/gepa-adk/",
            "https://docs.example.com",
            "https://github.com/Alberto-Codes/gepa-adk",
        )
        ```
    """
    links = []
    if github:
        links.append(
            rx.link(
                rx.hstack(
                    rx.icon("github", size=14),
                    rx.text("GitHub", size="2"),
                    spacing="1",
                    align="center",
                ),
                href=github,
                is_external=True,
                color=rx.color("blue", 9),
                underline="hover",
            )
        )
    if link:
        links.append(
            rx.link(
                rx.hstack(
                    rx.icon("external-link", size=14),
                    rx.text("PyPI", size="2"),
                    spacing="1",
                    align="center",
                ),
                href=link,
                is_external=True,
                color=rx.color("blue", 9),
                underline="hover",
            )
        )
    if docs:
        links.append(
            rx.link(
                rx.hstack(
                    rx.icon("book-open", size=14),
                    rx.text("Docs", size="2"),
                    spacing="1",
                    align="center",
                ),
                href=docs,
                is_external=True,
                color=rx.color("blue", 9),
                underline="hover",
            )
        )
    if links:
        return [rx.hstack(*links, spacing="4")]
    return []


def project_card(project: dict) -> rx.Component:
    """Render a project card with title, description, and tags.

    Args:
        project: Dict with "title", "description", "tags", optional "link"/"docs"/"github".

    Returns:
        A card component displaying the project.

    Examples:
        ```python
        project_card(
            {"title": "My Project", "description": "Details", "tags": ["Python"]}
        )
        ```
    """
    title_el = rx.heading(project["title"], size="4", weight="bold")
    card = rx.card(
        rx.vstack(
            title_el,
            rx.text(
                project["description"],
                size="2",
                color=rx.color("slate", 11),
                line_height="1.7",
            ),
            rx.flex(
                *[
                    rx.badge(tag, variant="surface", size="1")
                    for tag in project["tags"]
                ],
                wrap="wrap",
                spacing="2",
            ),
            *(
                _project_links(
                    project.get("link", ""),
                    project.get("docs", ""),
                    project.get("github", ""),
                )
            ),
            spacing="3",
        ),
        width="100%",
    )
    return card


def projects_page() -> rx.Component:
    """Render the projects page with a card grid."""
    return rx.container(
        rx.vstack(
            rx.box(height="4em"),
            rx.heading("Projects", size="8", weight="bold"),
            rx.separator(size="4", color_scheme="blue"),
            rx.text(
                "Key technical work and initiatives.",
                size="3",
                color=rx.color("slate", 10),
            ),
            rx.box(height="1em"),
            rx.grid(
                *[project_card(p) for p in PROJECTS],
                columns=rx.breakpoints(initial="1", md="2"),
                spacing="4",
                width="100%",
            ),
            spacing="4",
            max_width="48em",
        ),
        size="3",
        padding_y="6",
    )
