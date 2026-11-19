"""Home page with hero, latest writing, current projects and areas of expertise."""

from datetime import date

import reflex as rx

from alberto_codes_site.components.button_link import button_link
from alberto_codes_site.components.meta_label import meta_list
from alberto_codes_site.layout import PAGE_COLUMN, PAGE_PADDING_Y
from alberto_codes_site.pages.blog import (
    _index_entry,
    _index_style,
    _load_posts,
    _series_label,
    published_posts,
)
from alberto_codes_site.series import build_series
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
]

# Each proof line is a measured result from the post it links to, so the
# figures are only as current as that post; refresh them from there, not from
# this page. typevet's 6 of 6 is the wrong-total row of the results table in
# the 2026-09-29 post. vramfit's 86,016 tokens on a 24 GiB card is the
# text-only row of the 2026-09-02 post. saucier's 151 sauces and 1909 printing
# are the v0.7.0 README census, also quoted on the saucier card in
# pages/projects.py, so the two move together.
TYPEVET = {
    "title": "typevet",
    "result": "6 of 6",
    "measure": "wrong totals caught",
    "proof": "Gemma 4 had accepted the same totals before it saw the receipt photos.",
    "href": "/blog/2026-09-29-gemma-was-sure-the-total-matched-it-had-not-seen-the-receipt",
}

BUILDING = [
    {
        "title": "vramfit",
        "result": "86,016",
        "measure": "tokens of text context",
        "proof": "Gemma 4 31B served that much context on a single 24 GiB graphics card.",
        "href": "/blog/2026-09-02-googles-4-bit-gemma-already-fit-my-card",
    },
    {
        "title": "saucier",
        "result": "151",
        "measure": "sauces catalogued",
        "proof": "Each entry traces back to a line in Escoffier’s 1909 cookbook.",
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


def _latest_writing(today: date | None = None) -> rx.Component:
    """Render the newest posts as rows of the blog index, with its styles.

    The rows are the blog index's own (``_index_entry``, ``_index_style``),
    so the two pages cannot drift apart: title and leader, date, the
    summary's first sentence, then the type and series marks.

    Args:
        today: The date to treat as now. Defaults to the build date.

    Returns:
        The ``ol`` of rows.
    """
    all_series = build_series(published_posts(_load_posts(), today=today))
    return rx.el.ol(
        *[
            _index_entry(meta, _series_label(meta, all_series))
            for meta in _latest_posts(today)
        ],
        class_name="latest-writing",
        style={
            **_index_style(),
            "& .index-entry:first-child .index-title": {
                "font_size": "clamp(1.4rem, 3vw, 2rem)",
                "line_height": "1.2",
            },
        },
    )


def _receipt_comparison() -> rx.Component:
    """Pair the original photo crop from typevet-receipt-swap.svg with its claim."""
    return rx.el.figure(
        rx.image(
            src="/typevet-receipt-total.jpg",
            alt="Receipt showing the printed total of 664,329.",
            width="100%",
            height="auto",
            aspect_ratio="520 / 142",
            display="block",
            loading="lazy",
            border_radius="var(--radius-2)",
        ),
        rx.el.figcaption(
            *[
                rx.vstack(
                    rx.text(label, size="2", color=rx.color("gray", 11)),
                    rx.text(
                        amount,
                        size="5",
                        weight="bold",
                        font_variant_numeric="tabular-nums",
                    ),
                    spacing="1",
                )
                for label, amount in (
                    ("Claimed total", "646,329"),
                    ("Receipt total", "664,329"),
                )
            ],
            display="grid",
            grid_template_columns="repeat(2, minmax(0, 1fr))",
            gap="var(--space-2)",
            padding_top="var(--space-3)",
        ),
        margin="0",
        min_width="0",
    )


def _building_card(
    project: dict, *, figure: rx.Component | None = None
) -> rx.Component:
    """Link a measured project result to its writeup."""
    result = rx.vstack(
        rx.heading(
            project["title"],
            as_="h3",
            size="3",
            weight="medium",
        ),
        rx.text(
            rx.text(
                project["result"],
                as_="span",
                size="7",
                weight="bold",
                display="block",
            ),
            project["measure"],
            size="2",
            weight="medium",
        ),
        rx.text(project["proof"], size="2", color=rx.color("gray", 11)),
        rx.link(
            "Read the writeup →",
            href=project["href"],
            aria_label=f"Read the writeup for {project['title']}",
            size="2",
            margin_top="auto",
            style={"&::after": {"content": '""', "position": "absolute", "inset": 0}},
        ),
        spacing="3",
        height="100%",
    )
    content = result
    if figure is not None:
        content = rx.grid(
            result,
            figure,
            columns=rx.breakpoints(initial="1", sm="2"),
            spacing="5",
            align="center",
        )
    return rx.card(
        content,
        width="100%",
        size="2",
        position="relative",
    )


def home_page() -> rx.Component:
    """Render the home page: hero, latest writing, projects and expertise."""
    years = years_at_wells_fargo()
    return rx.container(
        rx.vstack(
            rx.flex(
                rx.image(
                    src="/headshot.jpg",
                    alt="Alberto Nieto",
                    border_radius="var(--radius-4)",
                    width=rx.breakpoints(initial="4.5rem", sm="9rem"),
                    height=rx.breakpoints(initial="4.5rem", sm="9rem"),
                    object_fit="cover",
                    flex_shrink="0",
                ),
                rx.vstack(
                    rx.vstack(
                        rx.heading(
                            "Alberto Nieto",
                            as_="h1",
                            size="8",
                            weight="bold",
                        ),
                        rx.text(
                            "Generative AI Principal Engineer",
                            size="3",
                            weight="medium",
                            color=rx.color("gray", 11),
                        ),
                        spacing="1",
                    ),
                    rx.text(
                        "I started as a teller and taught myself to code.",
                        size=rx.breakpoints(initial="4", sm="5"),
                        weight="medium",
                        style={"text_wrap": "pretty"},
                    ),
                    rx.text(
                        "Now I design AI systems at work, and on my own time I build open "
                        "source tools that test what models actually do, then publish "
                        "the evidence.",
                        size="3",
                        color=rx.color("gray", 11),
                    ),
                    spacing="3",
                ),
                direction=rx.breakpoints(initial="column", sm="row-reverse"),
                gap=rx.breakpoints(initial="var(--space-4)", sm="var(--space-7)"),
                align="start",
                padding_top=rx.breakpoints(initial="0", sm="var(--space-5)"),
                width="100%",
            ),
            # These badges are claims about a career rather than a repository,
            # so no build can re-read them. Each is stated in full on the page
            # that owns it:
            #
            #   2x Top Performer    the 2006-2018 role in pages/experience.py,
            #                       "Two-time Top Performer award recipient
            #                       (2014, 2018)"
            #   3 Patents Pending   the current role in pages/experience.py,
            #                       "Co-inventor on three pending patent
            #                       applications". Three applications filed,
            #                       none granted; the About bio says the same
            #   N Years             years_at_wells_fargo() in tenure.py, whole
            #                       years since the 2000-08-14 start date,
            #                       recomputed on every build. About, Experience
            #                       and the meta descriptions use the same helper
            #   N PyPI Packages     the comment above PROJECTS in
            #                       pages/projects.py, which owns this figure
            #                       and names every page that repeats it
            rx.hstack(
                rx.hstack(
                    rx.icon("award", size=16, color=rx.color("gray", 11)),
                    rx.text("2x Top Performer", size="2", color=rx.color("gray", 11)),
                    spacing="1",
                    align="center",
                ),
                rx.hstack(
                    rx.icon("file-check", size=16, color=rx.color("gray", 11)),
                    rx.text("3 Patents Pending", size="2", color=rx.color("gray", 11)),
                    spacing="1",
                    align="center",
                ),
                rx.hstack(
                    rx.icon("building", size=16, color=rx.color("accent", 9)),
                    rx.text(
                        f"{years} years at Wells Fargo",
                        size="2",
                        color=rx.color("gray", 11),
                    ),
                    spacing="1",
                    align="center",
                ),
                rx.hstack(
                    rx.icon("package", size=16, color=rx.color("gray", 11)),
                    rx.text("8 PyPI Packages", size="2", color=rx.color("gray", 11)),
                    spacing="1",
                    align="center",
                ),
                spacing="5",
                # Two by two on phones, so the badges take two rows rather than
                # four and "Latest writing" stays near the top (issue #84).
                display=["grid", "grid", "flex", "flex", "flex"],
                grid_template_columns="repeat(2, auto)",
                row_gap="var(--space-3)",
                justify_content="start",
                align="center",
            ),
            rx.hstack(
                button_link("View Projects", href="/projects", size="3"),
                button_link("Contact Me", href="/contact", variant="outline", size="3"),
                spacing="4",
            ),
            rx.box(height="var(--space-2)"),
            rx.vstack(
                _section_heading("Latest writing", "All posts \u2192", "/blog"),
                _latest_writing(),
                id="latest-writing",
                scroll_margin_top="6rem",
                spacing="3",
                width="100%",
            ),
            rx.box(height="1em"),
            rx.vstack(
                _section_heading(
                    "What I'm building", "View all projects \u2192", "/projects"
                ),
                _building_card(TYPEVET, figure=_receipt_comparison()),
                rx.grid(
                    *[_building_card(project) for project in BUILDING],
                    columns=rx.breakpoints(initial="1", sm="2"),
                    spacing="3",
                    width="100%",
                ),
                spacing="3",
                width="100%",
                id="building",
                scroll_margin_top="5rem",
            ),
            rx.box(height="1em"),
            rx.heading("Areas of Expertise", as_="h2", size="3", weight="medium"),
            rx.box(
                meta_list(EXPERTISE_TAGS, size="2"),
                max_width=["100%", "100%", "32em", "32em", "32em"],
            ),
            spacing="4",
            align="start",
            min_height="85vh",
            **PAGE_COLUMN,
        ),
        size="3",
        padding_x=["var(--space-4)", "var(--space-4)", "0", "0", "0"],
        padding_y=PAGE_PADDING_Y,
    )
