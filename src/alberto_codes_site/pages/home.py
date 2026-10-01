"""Home page with hero, latest writing, current projects and areas of expertise."""

from datetime import date

import reflex as rx

from alberto_codes_site.components.button_link import button_link
from alberto_codes_site.components.meta_label import meta_list
from alberto_codes_site.layout import PAGE_COLUMN, PAGE_PADDING_Y
from alberto_codes_site.pages.blog import _load_posts, published_posts
from alberto_codes_site.tenure import years_at_wells_fargo

LATEST_POST_COUNT = 3

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

# Each proof line is a measured result from the post it links to, so the
# figures are only as current as that post; refresh them from there, not from
# this page. typevet's 6 of 6 is the wrong-total row of the results table in
# the 2026-09-29 post. vramfit's 86,016 tokens on a 24 GiB card is the
# text-only row of the 2026-09-02 post. saucier's 151 sauces and 1909 printing
# are the v0.7.0 README census, also quoted on the saucier card in
# pages/projects.py, so the two move together.
BUILDING = [
    {
        "title": "typevet",
        "proof": (
            "Typed answers from open models, about text and photos. With a "
            "receipt photo attached, Gemma 4 caught 6 of 6 wrong totals it had "
            "passed as text."
        ),
        "href": "/blog/2026-09-29-gemma-was-sure-the-total-matched-it-had-not-seen-the-receipt",
    },
    {
        "title": "vramfit",
        "proof": (
            "Fits large open models onto one GPU. Gemma 4 31B on a 24 GiB "
            "card, serving 86,016 tokens of context."
        ),
        "href": "/blog/2026-09-02-googles-4-bit-gemma-already-fit-my-card",
    },
    {
        "title": "saucier",
        "proof": (
            "Reads two printings of a 1909 cookbook and catalogues 151 sauces, "
            "every claim traced to the line it came from."
        ),
        "href": "/blog/2026-09-08-the-scan-lost-one-letter-and-crowned-a-derivative",
    },
]


def _latest_posts(today: date | None = None) -> list[dict]:
    """Return the newest published posts, skipping any dated after ``today``.

    Args:
        today: The date to treat as now. Defaults to the build date.

    Returns:
        Up to ``LATEST_POST_COUNT`` post metadata dicts, newest first.

    Examples:
        ```python
        _latest_posts(date(2026, 10, 1))[0]["slug"]
        ```
    """
    published = published_posts(_load_posts(), today=today)
    return [meta for meta, _body in published[:LATEST_POST_COUNT]]


def _section_heading(title: str, link_text: str, href: str) -> rx.Component:
    """Render a section heading with a trailing link to the full listing."""
    return rx.flex(
        rx.heading(title, as_="h2", size="5", weight="medium"),
        rx.link(link_text, href=href, size="2", weight="medium"),
        justify="between",
        align="baseline",
        wrap="wrap",
        gap="2",
        width="100%",
    )


def _latest_post_card(meta: dict) -> rx.Component:
    """Render a compact post card: date, title and a two-line summary."""
    return rx.link(
        rx.card(
            rx.vstack(
                rx.text(meta.get("date", ""), size="1", color=rx.color("slate", 11)),
                rx.heading(
                    meta.get("title", "Untitled"), as_="h3", size="3", weight="bold"
                ),
                rx.text(
                    meta.get("summary", ""),
                    size="2",
                    color=rx.color("slate", 11),
                    style={
                        "display": "-webkit-box",
                        "-webkit-line-clamp": "2",
                        "-webkit-box-orient": "vertical",
                        "overflow": "hidden",
                    },
                ),
                spacing="1",
            ),
            width="100%",
            _hover={"box_shadow": "0 2px 8px rgba(0,0,0,0.1)"},
        ),
        href=f"/blog/{meta.get('slug', '')}",
        underline="none",
        width="100%",
    )


def _building_card(project: dict) -> rx.Component:
    """Render a project card with its one-line proof, linking to the writeup."""
    return rx.link(
        rx.card(
            rx.vstack(
                rx.heading(project["title"], as_="h3", size="4", weight="bold"),
                rx.text(project["proof"], size="2", color=rx.color("slate", 11)),
                rx.spacer(),
                rx.text(
                    "Read the writeup \u2192",
                    size="2",
                    weight="medium",
                    color=rx.color("blue", 11),
                ),
                spacing="2",
                height="100%",
            ),
            width="100%",
            height="100%",
            _hover={"box_shadow": "0 2px 8px rgba(0,0,0,0.1)"},
        ),
        href=project["href"],
        underline="none",
        width="100%",
    )


def home_page() -> rx.Component:
    """Render the home page: hero, latest writing, projects and expertise."""
    years = years_at_wells_fargo()
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
            rx.text("Hello, I'm", size="4", color=rx.color("slate", 11)),
            rx.heading(
                "Alberto Nieto",
                as_="h1",
                size=rx.breakpoints(initial="7", md="9"),
                weight="bold",
            ),
            rx.heading(
                rx.el.p("Generative AI Principal Engineer"),
                as_child=True,
                size=rx.breakpoints(initial="3", md="6"),
                weight="medium",
                color=rx.color("blue", 11),
                text_align="center",
            ),
            rx.text(
                "I started as a teller, taught myself to code, and spent "
                f"{years} years building my way to Principal Engineer. Now I "
                "design AI systems at work, and on my own time I build open "
                "source tools that test what models actually do, then publish "
                "the evidence.",
                size="3",
                color=rx.color("slate", 11),
                max_width=["100%", "100%", "36em", "36em", "36em"],
                text_align="center",
            ),
            # These badges are claims about a career rather than a repository,
            # so no build can re-read them. Each is stated in full on the page
            # that owns it:
            #
            #   2x Top Performer    the 2006-2018 role in pages/experience.py,
            #                       "Two-time Top Performer award recipient
            #                       (2014, 2018)"
            #   2 Patents Pending   the current role in pages/experience.py,
            #                       "Co-inventor on two pending patent
            #                       applications". Two applications filed, none
            #                       granted; the About bio says the same
            #   N Years             years_at_wells_fargo() in tenure.py, whole
            #                       years since the 2000-08-14 start date,
            #                       recomputed on every build. The paragraph
            #                       above, the About and Experience pages and
            #                       the meta descriptions read the same helper
            #   N PyPI Packages     the comment above PROJECTS in
            #                       pages/projects.py, which owns this figure
            #                       and names every page that repeats it
            rx.hstack(
                rx.hstack(
                    rx.icon("award", size=16, color=rx.color("blue", 9)),
                    rx.text("2x Top Performer", size="2", color=rx.color("slate", 11)),
                    spacing="1",
                    align="center",
                ),
                rx.hstack(
                    rx.icon("file-check", size=16, color=rx.color("blue", 9)),
                    rx.text("2 Patents Pending", size="2", color=rx.color("slate", 11)),
                    spacing="1",
                    align="center",
                ),
                rx.hstack(
                    rx.icon("building", size=16, color=rx.color("blue", 9)),
                    rx.text(f"{years} Years", size="2", color=rx.color("slate", 11)),
                    spacing="1",
                    align="center",
                ),
                rx.hstack(
                    rx.icon("package", size=16, color=rx.color("blue", 9)),
                    rx.text("8 PyPI Packages", size="2", color=rx.color("slate", 11)),
                    spacing="1",
                    align="center",
                ),
                spacing="5",
                # Two by two on phones, so the badges take two rows rather than
                # four and "Latest writing" stays near the top (issue #84).
                display=["grid", "grid", "flex", "flex", "flex"],
                grid_template_columns="repeat(2, auto)",
                row_gap="var(--space-3)",
                justify_content="center",
                align="center",
            ),
            rx.hstack(
                button_link("View Projects", href="/projects", size="3"),
                button_link("Contact Me", href="/contact", variant="outline", size="3"),
                spacing="4",
            ),
            rx.box(height="2em"),
            rx.vstack(
                _section_heading("Latest writing", "All posts \u2192", "/blog"),
                *[_latest_post_card(meta) for meta in _latest_posts()],
                spacing="3",
                width="100%",
            ),
            rx.box(height="1em"),
            rx.vstack(
                _section_heading(
                    "What I'm building", "View all projects \u2192", "/projects"
                ),
                rx.grid(
                    *[_building_card(project) for project in BUILDING],
                    columns=rx.breakpoints(initial="1", sm="3"),
                    spacing="3",
                    width="100%",
                ),
                spacing="3",
                width="100%",
            ),
            rx.box(height="1em"),
            rx.heading("Areas of Expertise", as_="h2", size="3", weight="medium"),
            rx.box(
                meta_list(EXPERTISE_TAGS, size="2", justify="center"),
                max_width=["100%", "100%", "32em", "32em", "32em"],
            ),
            spacing="4",
            align="center",
            min_height="85vh",
            **PAGE_COLUMN,
        ),
        size="3",
        padding_x=["var(--space-4)", "var(--space-4)", "0", "0", "0"],
        padding_y=PAGE_PADDING_Y,
    )
