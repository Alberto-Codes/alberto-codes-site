"""Projects page with card grid of key technical work."""

import reflex as rx

# Every figure below is hand-copied from another repository. This site is a
# static build with no runtime fetch, so the numbers cannot read themselves and
# will rot silently unless re-read. Where each one comes from:
#
#   saucier counts   the "state this tag represents" census in the saucier
#                    release notes, which is what `uv run saucier parse` prints
#                    and what the saucier README leads with
#   vramfit points   the last "## The Nth data point" heading in vramfit's
#                    evidence ledger, docs/explanation/evaluating-packed-models.md
#   release counts   gh api /repos/Alberto-Codes/<repo>/releases --paginate
#   dependency count the [project] dependencies array in that repo's
#                    pyproject.toml, not its README, which lags
#   docvet rules     the "What It Checks" section of the docvet README
#
# Download counts have no agreed source and are not refreshed here; pypistats
# reports recent windows, not the lifetime totals these appear to be.
#
# Two figures are not hand-copied from another repository, but are read off
# this repository instead:
#
#   pypi packages    the count of entries below carrying a pypi.org "link",
#                    five today. It appears as "N PyPI Packages" on the home
#                    page; the same list is spelled out on the About page, in
#                    the current-role bullet in pages/experience.py, and in the
#                    /projects meta description in alberto_codes_site.py, so a
#                    sixth package means editing all four.
#   published packs  the PUBLICATIONS entries with kind "Quantized model" in
#                    src/alberto_codes_site/pages/publications.py, three today,
#                    which is what the vramfit entry below counts.
PROJECTS = [
    {
        "title": "saucier",
        "description": (
            "Reads two printings of one cookbook and returns a catalogue of "
            "sauces, every claim traceable to the line it came from. 151 "
            "preparations in the 1909 witness, 57 that state a parent, 94 "
            "that state no base at all — the measured bar anything cleverer "
            "has to beat. Deterministic extraction behind four layers with "
            "no runtime dependencies, so a model can be added later without "
            "touching the provenance guarantees. Corpus committed, so a "
            "clone runs offline. Counts are the v0.6.0 README census. MIT."
        ),
        "tags": [
            "Python",
            "PyPI",
            "Architecture",
            "CLI",
            "Open Source",
        ],
        "link": "https://pypi.org/project/saucier/",
        "docs": "https://alberto-codes.github.io/saucier/",
        "github": "https://github.com/Alberto-Codes/saucier",
    },
    {
        "title": "vramfit",
        "description": (
            "Fits large open models onto one GPU by measuring which layers "
            "survive being crushed. Scans per-layer quantization damage, "
            "solves a mixed-precision recipe against a hard VRAM budget, "
            "then packs it. Three published packs, each measured against "
            "its baseline with the losing numbers printed: Nemotron Super "
            "49B on a 24 GiB card, Nemotron 3.5 Lightning 30B-A3B entirely "
            "on a 16 GiB card, and Gemma 4 31B solved for 86k tokens of "
            "context beside Google's own 4-bit build. Twenty recorded "
            "data points in the evidence ledger, losses included. MIT."
        ),
        "tags": [
            "Generative AI",
            "Quantization",
            "LLM",
            "Python",
            "PyPI",
            "Open Source",
        ],
        "link": "https://pypi.org/project/vramfit/",
        "github": "https://github.com/Alberto-Codes/vramfit",
        "model": "https://huggingface.co/Alberto-Codes",
    },
    {
        "title": "gepa-adk",
        "description": (
            "Evolves AI agent instructions automatically using genetic "
            "algorithms. Async-first engine built on Google ADK with "
            "hexagonal architecture and protocol-based interfaces. "
            "17 releases, ~4,900 downloads. Apache-2.0."
        ),
        "tags": ["Generative AI", "Google ADK", "Python", "PyPI"],
        "link": "https://pypi.org/project/gepa-adk/",
        "docs": "https://alberto-codes.github.io/gepa-adk/",
        "github": "https://github.com/Alberto-Codes/gepa-adk",
    },
    {
        "title": "adk-secure-sessions",
        "description": (
            "The compliance gateway for Google ADK \u2014 encrypted session "
            "storage in 5 minutes. Drop-in replacement that encrypts state "
            "and conversation history at rest using Fernet, closing the "
            "encryption gap for PHI, PII, and financial data. "
            "4 dependencies. Apache-2.0."
        ),
        "tags": ["Generative AI", "Google ADK", "Security", "Python", "PyPI"],
        "link": "https://pypi.org/project/adk-secure-sessions/",
        "github": "https://github.com/Alberto-Codes/adk-secure-sessions",
    },
    {
        "title": "docvet",
        "description": (
            "Python docstring quality vetting that catches what linters miss. "
            "31 rules across presence, completeness, accuracy, rendering, "
            "and visibility \u2014 including git-based staleness detection via "
            "diff and blame. Production/Stable, ~3,300 downloads. MIT."
        ),
        "tags": ["Python", "CLI", "Code Quality", "PyPI", "Open Source"],
        "link": "https://pypi.org/project/docvet/",
        "docs": "https://alberto-codes.github.io/docvet/",
        "github": "https://github.com/Alberto-Codes/docvet",
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


def _project_links(
    link: str, docs: str, github: str, model: str = ""
) -> list[rx.Component]:
    """Build a list of link components for a project card.

    Args:
        link: URL to the project (e.g. PyPI). Empty string to omit.
        docs: URL to the documentation site. Empty string to omit.
        github: URL to the GitHub repository. Empty string to omit.
        model: URL to a published model or dataset on Hugging Face. Empty
            string to omit.

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
    if model:
        links.append(
            rx.link(
                rx.hstack(
                    rx.icon("box", size=14),
                    rx.text("Hugging Face", size="2"),
                    spacing="1",
                    align="center",
                ),
                href=model,
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
        project: Dict with "title", "description", "tags", and optional
            "link"/"docs"/"github"/"model".

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
                    project.get("model", ""),
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
            rx.box(height="1em"),
            rx.card(
                rx.hstack(
                    rx.vstack(
                        rx.heading(
                            "Want to collaborate?",
                            size="4",
                            weight="bold",
                        ),
                        rx.text(
                            "Check out my GitHub for more projects, or get in touch.",
                            size="2",
                            color=rx.color("slate", 11),
                        ),
                        spacing="1",
                    ),
                    rx.spacer(),
                    rx.hstack(
                        rx.link(
                            rx.button(
                                rx.icon("github", size=16),
                                "GitHub",
                                size="2",
                                variant="outline",
                            ),
                            href="https://github.com/Alberto-Codes",
                            is_external=True,
                            underline="none",
                        ),
                        rx.link(
                            rx.button("Contact Me", size="2"),
                            href="/contact",
                            underline="none",
                        ),
                        spacing="3",
                    ),
                    width="100%",
                    align="center",
                    flex_direction=["column", "column", "row", "row", "row"],
                    gap="4",
                ),
                width="100%",
            ),
            spacing="4",
            max_width="48em",
        ),
        size="3",
        padding_y="6",
    )
