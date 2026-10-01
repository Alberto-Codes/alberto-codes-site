"""Blog page with markdown post rendering and individual post routes.

A post is published once its frontmatter ``date`` is on or before the build
date (``published_posts``). The blog index, home's "Latest writing", the post
routes (and so the sitemap) and the RSS feed all apply that one rule. Pages
are built when the app module is imported, so a future-dated post stays
hidden until the first build on or after its date; deploys rebuild.
"""

import math
from datetime import date
from pathlib import Path

import reflex as rx
from reflex.vars import Var

from alberto_codes_site.figures import figure_page_style, split_figures
from alberto_codes_site.headings import (
    Slugger,
    fragment_link,
    heading_anchor_style,
    heading_component_map,
    heading_ids,
    heading_label,
    heading_labels,
    heading_lines,
)
from alberto_codes_site.layout import (
    PAGE_COLUMN,
    PAGE_PADDING_Y,
    READING_COLUMN,
    READING_WIDTH,
)

POSTS_DIR = Path(__file__).resolve().parent.parent.parent / "posts"

DIATAXIS_COLORS = {
    "tutorial": "green",
    "how-to": "orange",
    "explanation": "violet",
    "reference": "cyan",
}


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse minimal YAML-style frontmatter from a markdown string.

    Supports:
    - Top-level `key: value` pairs
    - Simple lists:
      ```yaml
      tags:
        - a
        - b
      ```
    """
    metadata: dict = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            current_list_key: str | None = None
            for line in parts[1].strip().splitlines():
                if not line.strip():
                    continue

                if current_list_key is not None and line.lstrip().startswith("- "):
                    item = line.split("- ", 1)[1].strip()
                    existing_val = metadata.get(current_list_key, "")
                    if isinstance(existing_val, str):
                        metadata[current_list_key] = []
                    if isinstance(metadata[current_list_key], list):
                        metadata[current_list_key].append(item)
                    continue

                if ":" in line and not line.startswith("  "):
                    key, val = line.split(":", 1)
                    key = key.strip()
                    val = val.strip()
                    metadata[key] = val
                    current_list_key = key if val == "" else None
            body = parts[2].strip()
    return metadata, body


def _reading_time(text: str) -> int:
    """Estimate reading time in minutes (assuming 200 wpm)."""
    words = len(text.split())
    return max(1, math.ceil(words / 200))


def _load_posts() -> list[tuple[dict, str]]:
    """Load all markdown posts sorted by date descending.

    Files named `draft-*.md` are work in progress and never render. Rename a
    draft to `YYYY-MM-DD-slug.md` to publish it. Future-dated posts are still
    returned here (their share cards are committed ahead of time); pass the
    result through ``published_posts`` before showing it.
    """
    posts = []
    if POSTS_DIR.exists():
        for f in sorted(POSTS_DIR.glob("*.md"), reverse=True):
            if f.name.startswith("draft-"):
                continue
            meta, body = _parse_frontmatter(f.read_text())
            meta.setdefault("slug", f.stem)
            meta["reading_time"] = _reading_time(body)
            posts.append((meta, body))
    return posts


def post_date(meta: dict) -> date | None:
    """Return a post's frontmatter date, or None when it is missing or malformed.

    Args:
        meta: The post's frontmatter.

    Returns:
        The parsed `YYYY-MM-DD` date, or None.
    """
    try:
        return date.fromisoformat(str(meta.get("date", "")).strip())
    except ValueError:
        return None


def published_posts(
    posts: list[tuple[dict, str]], *, today: date | None = None
) -> list[tuple[dict, str]]:
    """Keep only posts whose date has arrived.

    ``_load_posts`` already drops `draft-*.md` files; this also drops posts
    dated after ``today`` and posts without a valid date.

    Args:
        posts: ``(meta, body)`` pairs from ``_load_posts``.
        today: The build date; defaults to the current date.

    Returns:
        The published posts, newest first.
    """
    today = today or date.today()
    dated = [(post_date(m), m, b) for m, b in posts]
    kept = [(d, m, b) for d, m, b in dated if d is not None and d <= today]
    kept.sort(key=lambda item: item[0], reverse=True)
    return [(m, b) for _, m, b in kept]


def _type_badge(post_type: str) -> rx.Component:
    """Render a colored badge for the Diataxis type."""
    color = DIATAXIS_COLORS.get(post_type, "gray")
    return rx.badge(post_type, variant="surface", size="1", color_scheme=color)


def _post_card(meta: dict) -> rx.Component:
    """Render a blog post summary card linking to the full post."""
    return rx.link(
        rx.card(
            rx.vstack(
                rx.hstack(
                    _type_badge(meta.get("type", "post")),
                    rx.text(
                        meta.get("date", ""),
                        size="1",
                        color=rx.color("slate", 11),
                    ),
                    rx.text(
                        f"{meta.get('reading_time', 1)} min read",
                        size="1",
                        color=rx.color("slate", 11),
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.heading(
                    meta.get("title", "Untitled"),
                    as_="h2",
                    size="4",
                    weight="bold",
                ),
                rx.text(
                    meta.get("summary", ""),
                    size="2",
                    color=rx.color("slate", 11),
                ),
                spacing="2",
            ),
            width="100%",
            _hover={"box_shadow": "0 2px 8px rgba(0,0,0,0.1)"},
        ),
        href=f"/blog/{meta.get('slug', '')}",
        underline="none",
        width="100%",
    )


COPY_FEEDBACK_MS = 2000


def _copy_handler(code: Var) -> Var:
    """Return a client-side click handler that copies ``code``.

    The export has no backend, so the copy runs in the browser. On success the
    button carries ``data-copied`` for two seconds, which swaps its icon to a
    check, and the block's live region announces "Copied".
    """
    return Var(
        "(e) => { const button = e.currentTarget;"
        f" navigator.clipboard.writeText({code}).then(() => {{"
        " const status = button.parentElement.querySelector('[role=status]');"
        " button.dataset.copied = 'true'; status.textContent = 'Copied';"
        " clearTimeout(button._copiedTimer);"
        " button._copiedTimer = setTimeout(() => {"
        " delete button.dataset.copied; status.textContent = ''; }"
        f", {COPY_FEEDBACK_MS}); }}); }}"
    )


def _code_toolbar(code: Var, language: object) -> rx.Component:
    """Render the bar above a code block: fenced language and a copy button.

    The bar sits above the code rather than over it, so the button never
    covers code text on a phone. A block fenced without a language gets no
    label; the button is always there.
    """
    language = Var.create(language if language is not None else "")
    return rx.el.div(
        rx.cond(
            language,
            rx.el.span(language, class_name="code-language"),
            rx.el.span(),
        ),
        rx.el.button(
            rx.icon("copy", size=14, class_name="code-copy-idle"),
            rx.icon("check", size=14, class_name="code-copy-done"),
            type="button",
            aria_label="Copy code",
            title="Copy code",
            class_name="code-copy",
            custom_attrs={"onClick": _copy_handler(code)},
        ),
        rx.el.span(role="status", aria_live="polite", class_name="code-copy-status"),
        class_name="code-toolbar",
    )


def _code_block(value: object, **props) -> rx.Component:
    """Keep console columns intact with a scrollbar independent of OS settings.

    A toolbar above the block shows the fenced language and a copy button.
    """
    code = Var.create(value)
    return rx.box(
        _code_toolbar(code, props.get("language")),
        rx.scroll_area(
            rx.code_block(
                value,
                **props,
                wrap_long_lines=False,
                min_width="100%",
                width="max-content",
            ),
            type="auto",
            scrollbars="horizontal",
            width="100%",
            style={
                # Syntax-highlighter themes set these inline; only the viewport
                # scrolls.
                "& pre": {
                    "margin": "0 !important",
                    "overflow": "visible !important",
                    "border_radius": "0 !important",
                },
                "& .rt-ScrollAreaScrollbar": {"background": rx.color("gray", 4)},
                "& .rt-ScrollAreaThumb": {"background": rx.color("gray", 11)},
            },
        ),
        class_name="code-figure",
        width="100%",
        margin_y="1em",
        border_radius="var(--radius-2)",
        position="relative",
        overflow="hidden",
        border=f"1px solid {rx.color('gray', 5)}",
        style={
            "& .code-toolbar": {
                "display": "flex",
                "align_items": "center",
                "justify_content": "space-between",
                "gap": "0.5em",
                "padding": "0.25em 0.25em 0.25em 0.75em",
                "background": rx.color("gray", 3),
                "border_bottom": f"1px solid {rx.color('gray', 5)}",
            },
            "& .code-language": {
                "font_family": "var(--code-font-family)",
                "font_size": "var(--font-size-1)",
                "color": rx.color("gray", 11),
            },
            "& .code-copy": {
                "display": "inline-flex",
                "align_items": "center",
                "justify_content": "center",
                "min_width": "32px",
                "min_height": "32px",
                "padding": "0",
                "border": "none",
                "border_radius": "var(--radius-2)",
                "background": "transparent",
                "color": rx.color("gray", 11),
                "cursor": "pointer",
            },
            "& .code-copy:hover": {"background": rx.color("gray", 5)},
            "& .code-copy:focus-visible": {
                "outline": f"2px solid {rx.color('blue', 8)}",
                "outline_offset": "1px",
            },
            # Announced to screen readers only.
            "& .code-copy-status": {
                "position": "absolute",
                "width": "1px",
                "height": "1px",
                "overflow": "hidden",
                "clip_path": "inset(50%)",
                "white_space": "nowrap",
            },
            "& .code-copy-done": {"display": "none", "color": rx.color("green", 11)},
            "& .code-copy[data-copied] .code-copy-idle": {"display": "none"},
            "& .code-copy[data-copied] .code-copy-done": {"display": "block"},
        },
    )


def _table(*children, **props) -> rx.Component:
    """Let a wide table scroll sideways instead of clipping on a phone."""
    return rx.scroll_area(
        rx.el.table(*children, **props, style={"min_width": "100%"}),
        type="auto",
        scrollbars="horizontal",
        width="100%",
        margin_y="1.5em",
        style={
            "& .rt-ScrollAreaScrollbar": {"background": rx.color("gray", 4)},
            "& .rt-ScrollAreaThumb": {"background": rx.color("gray", 11)},
        },
    )


# A post gets a table of contents once it has this many H2 sections (#75).
TOC_MIN_SECTIONS = 4

# One table of contents entry: heading level, plain text, and the heading's id.
TocEntry = tuple[int, str, str]


def _post_body(body: str) -> tuple[list[rx.Component], list[TocEntry]]:
    """Render a post body, inlining theme-aware figures between markdown runs.

    A figure carrying the shared token block (ADR-0005) is inlined so the
    site's theme reaches it; every other image stays inside the markdown.
    Headings get slug ids that are unique across all runs of the post, and the
    same ids are returned, in document order, for the table of contents.
    """
    slugger = Slugger()
    components: list[rx.Component] = []
    outline: list[TocEntry] = []
    for kind, content in split_figures(body):
        if kind == "figure":
            components.append(rx.html(content))
            continue
        ids = heading_ids(content, slugger)
        outline.extend(
            (level, heading_label(text), ids[line])
            for line, level, text in heading_lines(content)
        )
        components.append(
            rx.markdown(
                content,
                use_gfm=True,
                component_map={
                    **heading_component_map(ids, heading_labels(content)),
                    "pre": _code_block,
                    "table": _table,
                },
            )
        )
    return components, outline


def _toc_link(entry: TocEntry) -> rx.Component:
    """Render one table of contents link to a heading's fragment."""
    _level, text, heading_id = entry
    return fragment_link(text, href=f"#{heading_id}", class_name="toc-link")


def _table_of_contents(outline: list[TocEntry]) -> rx.Component | None:
    """Render the "On this page" block for a post with enough sections.

    H2s are listed in order, each with its H3s nested beneath it; deeper
    headings are left out. The block is a ``nav`` named by its label rather
    than a heading, so the post's heading outline is unchanged. It is a
    ``details`` element, open on load, that a reader can fold away.

    Args:
        outline: The post's headings from ``_post_body``.

    Returns:
        The block, or None when the post has fewer than ``TOC_MIN_SECTIONS``
        H2s.
    """
    sections: list[tuple[TocEntry, list[TocEntry]]] = []
    for entry in outline:
        if entry[0] == 2:
            sections.append((entry, []))
        elif entry[0] == 3 and sections:
            sections[-1][1].append(entry)
    if len(sections) < TOC_MIN_SECTIONS:
        return None
    items = [
        rx.el.li(
            _toc_link(section),
            *([rx.el.ol(*[rx.el.li(_toc_link(s)) for s in subs])] if subs else []),
        )
        for section, subs in sections
    ]
    return rx.el.nav(
        rx.el.details(
            rx.el.summary("On this page", class_name="toc-summary"),
            rx.el.ol(*items),
            open=True,
        ),
        aria_label="On this page",
        class_name="toc",
        width="100%",
        style={
            **READING_COLUMN,
            "border_left": f"3px solid {rx.color('gray', 6)}",
            "padding": "0.25em 0 0.25em 1em",
            "& .toc-summary": {
                "cursor": "pointer",
                "font_size": "var(--font-size-2)",
                "font_weight": "600",
                "color": rx.color("gray", 11),
            },
            "& ol": {"list_style": "none", "margin": "0", "padding": "0"},
            "& details > ol": {"margin_top": "0.5em"},
            "& ol ol": {"padding_inline_start": "1em"},
            "& li": {"margin": "0.25em 0"},
            "& .toc-link": {
                "font_size": "var(--font-size-2)",
                "line_height": "var(--line-height-2)",
                "color": rx.color("blue", 11),
                "text_decoration": "none",
            },
            "& .toc-link:hover": {"text_decoration": "underline"},
            "& :is(.toc-link, .toc-summary):focus-visible": {
                "outline": f"2px solid {rx.color('blue', 8)}",
                "outline_offset": "2px",
                "border_radius": "var(--radius-1)",
            },
        },
    )


def _render_post(meta: dict, body: str) -> rx.Component:
    """Render a full blog post with metadata header and markdown body.

    The header and the body's running text keep to the reading measure, centred
    in the post column; figures, tables and code blocks use the full column. A
    post with ``TOC_MIN_SECTIONS`` or more H2s gets a table of contents between
    the header and the body.
    """
    body_components, outline = _post_body(body)
    toc = _table_of_contents(outline)
    header = rx.vstack(
        rx.link(
            rx.hstack(
                rx.icon("arrow-left", size=14),
                rx.text("Back to Blog", size="2"),
                spacing="1",
                align="center",
            ),
            href="/blog",
            underline="none",
            color=rx.color("blue", 11),
        ),
        rx.box(height="1em"),
        rx.hstack(
            _type_badge(meta.get("type", "post")),
            rx.text(meta.get("date", ""), size="2", color=rx.color("slate", 11)),
            rx.text(
                f"{meta.get('reading_time', 1)} min read",
                size="2",
                color=rx.color("slate", 11),
            ),
            spacing="2",
            align="center",
        ),
        rx.heading(
            meta.get("title", "Untitled"),
            as_="h1",
            size="7",
            weight="bold",
        ),
        rx.text(
            meta.get("summary", ""),
            size="3",
            color=rx.color("slate", 11),
            style={"font-style": "italic"},
        ),
        rx.separator(size="4", color_scheme="blue"),
        spacing="4",
        width="100%",
        **READING_COLUMN,
    )
    return rx.vstack(
        header,
        *([toc] if toc is not None else []),
        rx.box(
            *body_components,
            width="100%",
            style={
                **figure_page_style(),
                **heading_anchor_style(),
                # Running text keeps to the measure; a paragraph that holds
                # an image is a figure and keeps the full width. A heading's
                # wrapper keeps it too, so its anchor link sits at the edge
                # of the measure.
                "& :is(p:not(:has(> img)), h2, h3, h4, h5, h6, blockquote)": (
                    READING_COLUMN
                ),
                "& div.heading-wrap": READING_COLUMN,
                # Lists keep their 1.5rem bullet indent inside the measure.
                "& :is(ul, ol)": {
                    "max_width": f"calc({READING_WIDTH} - 1.5rem)",
                    "margin_inline_start": (
                        f"calc(max(0px, (100% - {READING_WIDTH}) / 2) + 1.5rem)"
                    ),
                },
                "& :not(pre) > code": {"padding_inline_end": "0"},
                # Body links sit in running text; colour alone is under 3:1
                # against it in dark mode, so underline them.
                "& .rt-Link": {"text_decoration_line": "underline"},
                "& table": {
                    "border_collapse": "collapse",
                },
                "& th, & td": {
                    "border": "1px solid var(--gray-6)",
                    "padding": "0.75em 1em",
                    "text_align": "left",
                },
                "& th": {
                    "background": "var(--gray-3)",
                    "font_weight": "600",
                },
                "& tr:nth-child(even)": {
                    "background": "var(--gray-2)",
                },
                "& blockquote": {
                    "border_left": "3px solid var(--blue-8)",
                    "background": "var(--gray-2)",
                    "padding": "0.75em 1.25em",
                    "margin": "1.5em 0",
                    "border_radius": "0 4px 4px 0",
                },
                "& blockquote p": {
                    "color": "var(--gray-11)",
                    "font_style": "italic",
                },
                "& blockquote > :first-child": {
                    "margin_top": "0",
                },
                "& blockquote > :last-child": {
                    "margin_bottom": "0",
                },
            },
        ),
        spacing="4",
        width="100%",
    )


def blog_page(today: date | None = None) -> rx.Component:
    """Render the blog index page listing the published posts.

    Args:
        today: The build date; posts dated after it are left out.

    Returns:
        The blog index, or a placeholder when nothing is published yet.
    """
    posts = published_posts(_load_posts(), today=today)

    if not posts:
        return rx.container(
            rx.vstack(
                rx.box(height="4em"),
                rx.heading("Blog", as_="h1", size="8", weight="bold"),
                rx.separator(size="4", color_scheme="blue"),
                rx.box(height="4em"),
                rx.vstack(
                    rx.icon("notebook-pen", size=48, color=rx.color("slate", 7)),
                    rx.heading(
                        "Coming Soon", as_="h2", size="6", color=rx.color("slate", 9)
                    ),
                    rx.text(
                        "I'm working on sharing thoughts on AI engineering, "
                        "career growth, and technical leadership.",
                        size="3",
                        color=rx.color("slate", 11),
                        text_align="center",
                        max_width="24em",
                    ),
                    align="center",
                    spacing="4",
                ),
                spacing="4",
                align="center",
                min_height="60vh",
                **PAGE_COLUMN,
            ),
            size="3",
            padding_y=PAGE_PADDING_Y,
        )

    return rx.container(
        rx.vstack(
            rx.box(height="4em"),
            rx.hstack(
                rx.heading("Blog", as_="h1", size="8", weight="bold"),
                rx.link(
                    "RSS",
                    href="/feed.xml",
                    # A file, not a route: skip client-side navigation.
                    reload_document=True,
                    size="2",
                    color=rx.color("blue", 11),
                ),
                align="baseline",
                justify="between",
                width="100%",
            ),
            rx.separator(size="4", color_scheme="blue"),
            rx.box(height="1em"),
            rx.text(
                "Thoughts on AI engineering, Python, career growth, and "
                "technical leadership — organized using the Diataxis framework.",
                size="3",
                color=rx.color("slate", 11),
            ),
            rx.hstack(
                *[
                    rx.badge(
                        label,
                        variant="surface",
                        size="2",
                        color_scheme=color,
                    )
                    for label, color in DIATAXIS_COLORS.items()
                ],
                spacing="2",
                wrap="wrap",
            ),
            rx.box(height="1em"),
            *[_post_card(m) for m, _ in posts],
            spacing="4",
            **PAGE_COLUMN,
        ),
        size="3",
        padding_y=PAGE_PADDING_Y,
    )


def blog_post_page(slug: str, today: date | None = None) -> rx.Component:
    """Render an individual blog post by slug.

    Args:
        slug: The post's slug.
        today: The build date; a post dated after it renders as not found.

    Returns:
        The post page, or a not-found page.
    """
    posts = published_posts(_load_posts(), today=today)
    for meta, body in posts:
        if meta.get("slug") == slug:
            return rx.container(
                rx.vstack(
                    rx.box(height="4em"),
                    _render_post(meta, body),
                    spacing="4",
                    width="100%",
                ),
                size="3",
                padding_y=PAGE_PADDING_Y,
            )
    # Post not found
    return rx.container(
        rx.vstack(
            rx.box(height="4em"),
            rx.heading("Post Not Found", as_="h1", size="7", weight="bold"),
            rx.text(
                "Sorry, that post doesn't exist.", size="3", color=rx.color("slate", 11)
            ),
            rx.link("Back to Blog", href="/blog", color=rx.color("blue", 11)),
            spacing="4",
            align="center",
            min_height="60vh",
            **PAGE_COLUMN,
        ),
        size="3",
        padding_y=PAGE_PADDING_Y,
    )
