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
from urllib.parse import urlparse

import reflex as rx
from reflex.vars import Var

from alberto_codes_site.components.meta_label import meta_label
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
from alberto_codes_site.social import (
    AUTHOR_JOB_TITLE,
    AUTHOR_NAME,
    AUTHOR_SAME_AS,
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


def _type_badge(post_type: str, size: str = "1") -> rx.Component:
    """Render the Diataxis type as a label in its colour, not as a button."""
    color = DIATAXIS_COLORS.get(post_type, "gray")
    return meta_label(post_type, color_scheme=color, size=size)


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


# Light mode keeps react-syntax-highlighter's oneLight theme, but six of its
# token colours fall below 4.5:1 on its own #fafafa block background (issue
# #110). Each is darkened in HSL lightness only, hue and saturation kept, to
# the first whole-percent step that passes. The dark theme (oneDark) is
# untouched. tests/test_code_token_contrast.py holds the original colours and
# checks every ratio.
LIGHT_CODE_BACKGROUND = "#fafafa"
_LIGHT_CODE_COMMENT = "#71727a"  # was hsl(230, 4%, 64%)
_LIGHT_CODE_ORANGE = "#a76201"  # was hsl(35, 99%, 36%)
_LIGHT_CODE_RED = "#d93020"  # was hsl(5, 74%, 59%)
_LIGHT_CODE_GREEN = "#3f7e3e"  # was hsl(119, 34%, 47%)
_LIGHT_CODE_BLUE = "#2868f0"  # was hsl(221, 87%, 60%)
_LIGHT_CODE_CYAN = "#0179ad"  # was hsl(198, 99%, 37%)
LIGHT_CODE_TOKEN_COLOURS = {
    "comment": _LIGHT_CODE_COMMENT,
    "prolog": _LIGHT_CODE_COMMENT,
    "cdata": _LIGHT_CODE_COMMENT,
    "attr-name": _LIGHT_CODE_ORANGE,
    "class-name": _LIGHT_CODE_ORANGE,
    "boolean": _LIGHT_CODE_ORANGE,
    "constant": _LIGHT_CODE_ORANGE,
    "number": _LIGHT_CODE_ORANGE,
    "atrule": _LIGHT_CODE_ORANGE,
    "property": _LIGHT_CODE_RED,
    "tag": _LIGHT_CODE_RED,
    "symbol": _LIGHT_CODE_RED,
    "deleted": _LIGHT_CODE_RED,
    "important": _LIGHT_CODE_RED,
    "selector": _LIGHT_CODE_GREEN,
    "string": _LIGHT_CODE_GREEN,
    "char": _LIGHT_CODE_GREEN,
    "builtin": _LIGHT_CODE_GREEN,
    "inserted": _LIGHT_CODE_GREEN,
    "regex": _LIGHT_CODE_GREEN,
    "attr-value": _LIGHT_CODE_GREEN,
    "variable": _LIGHT_CODE_BLUE,
    "operator": _LIGHT_CODE_BLUE,
    "function": _LIGHT_CODE_BLUE,
    "url": _LIGHT_CODE_CYAN,
}
# The spread replaces a token class's whole style object, so an override has
# to restate everything else oneLight set on that class.
_LIGHT_CODE_ITALIC = {"comment"}
_LIGHT_CODE_THEME = (
    rx.code_block.themes.one_light.to(dict)
    .merge(
        Var.create(
            {
                token: {"color": colour}
                | ({"fontStyle": "italic"} if token in _LIGHT_CODE_ITALIC else {})
                for token, colour in LIGHT_CODE_TOKEN_COLOURS.items()
            }
            # oneLight fades namespace tokens to 0.8, which would undo the
            # ratios above.
            | {"namespace": {"opacity": 1}}
        )
    )
    ._replace(_var_type=rx.code_block.themes)
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
                theme=rx.color_mode_cond(
                    light=_LIGHT_CODE_THEME,
                    dark=rx.code_block.themes.one_dark,
                ),
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


# A post counts as related once it shares this many frontmatter tags (#74).
RELATED_MIN_SHARED_TAGS = 2
RELATED_MAX = 3

# The footer's profile links, in the order ``AUTHOR_SAME_AS`` keeps them.
GITHUB_URL, LINKEDIN_URL = AUTHOR_SAME_AS


def _post_tags(meta: dict) -> set[str]:
    """Return a post's frontmatter tags as a set (empty when it has none)."""
    tags = meta.get("tags", [])
    return set(tags) if isinstance(tags, list) else set()


def neighbour_posts(
    slug: str, posts: list[tuple[dict, str]]
) -> tuple[dict | None, dict | None]:
    """Return the published posts just older and just newer than ``slug``.

    Args:
        slug: The current post's slug.
        posts: The published posts, newest first, from ``published_posts``.

    Returns:
        ``(older, newer)`` frontmatter; either is None at that end of the list,
        and both are None when ``slug`` is not among ``posts``.
    """
    slugs = [m.get("slug") for m, _ in posts]
    if slug not in slugs:
        return None, None
    i = slugs.index(slug)
    newer = posts[i - 1][0] if i > 0 else None
    older = posts[i + 1][0] if i + 1 < len(posts) else None
    return older, newer


def related_posts(
    meta: dict, posts: list[tuple[dict, str]], exclude: set[str] | None = None
) -> list[dict]:
    """Rank other published posts by how many tags they share with ``meta``.

    A post needs ``RELATED_MIN_SHARED_TAGS`` shared tags to count; ties go to
    the newer post. The current post and the slugs in ``exclude`` (the
    older/newer links) are left out.

    Args:
        meta: The current post's frontmatter.
        posts: The published posts, from ``published_posts``.
        exclude: Slugs already linked from the post's end.

    Returns:
        Up to ``RELATED_MAX`` posts' frontmatter, best match first.
    """
    tags = _post_tags(meta)
    skip = {meta.get("slug"), *(exclude or ())}
    scored = [
        (len(tags & _post_tags(other)), post_date(other), other)
        for other, _ in posts
        if other.get("slug") not in skip
    ]
    scored = [
        item
        for item in scored
        if item[0] >= RELATED_MIN_SHARED_TAGS and item[1] is not None
    ]
    scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [other for _, _, other in scored[:RELATED_MAX]]


def discussion_label(url: str) -> str:
    """Name the link for a post's ``discussion_url``.

    Args:
        url: The discussion's address.

    Returns:
        "Discuss on r/<sub>" for a subreddit thread, else "Join the
        discussion".
    """
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    parts = [part for part in parsed.path.split("/") if part]
    on_reddit = host == "reddit.com" or host.endswith(".reddit.com")
    if on_reddit and len(parts) >= 2 and parts[0].lower() == "r":
        return f"Discuss on r/{parts[1]}"
    return "Join the discussion"


def _post_link(meta: dict, *children, **props) -> rx.Component:
    """Link to a post through the client-side router, as the index cards do."""
    return rx.link(
        *children,
        href=f"/blog/{meta.get('slug', '')}",
        underline="none",
        class_name="post-end-link",
        **props,
    )


def _neighbour(meta: dict | None, label: str, align: str) -> rx.Component:
    """Render one older/newer link: a small direction label over the title.

    An empty span holds the grid cell when there is no post that way.
    """
    if meta is None:
        return rx.el.span()
    return _post_link(
        meta,
        rx.el.span(label, class_name="post-end-label"),
        rx.el.span(meta.get("title", "Untitled"), class_name="post-end-title"),
        text_align=align,
    )


def _post_end(meta: dict, posts: list[tuple[dict, str]]) -> rx.Component:
    """Render the section that closes every post (issue #74).

    Older/newer links among the published posts, up to ``RELATED_MAX``
    related posts, a discussion link when the frontmatter has
    ``discussion_url``, and a one-line author note with profile links. Its
    labels are plain text, not headings, so the heading outline and the table
    of contents are unchanged.

    Args:
        meta: The current post's frontmatter.
        posts: The published posts, newest first.

    Returns:
        The section, kept to the reading column.
    """
    older, newer = neighbour_posts(meta.get("slug", ""), posts)
    related = related_posts(
        meta,
        posts,
        exclude={m.get("slug") for m in (older, newer) if m is not None},
    )
    parts: list[rx.Component] = []
    if older is not None or newer is not None:
        parts.append(
            rx.el.nav(
                _neighbour(older, "← Older", "left"),
                _neighbour(newer, "Newer →", "right"),
                aria_label="Older and newer posts",
                class_name="post-end-neighbours",
            )
        )
    if related:
        parts.append(
            rx.el.nav(
                rx.el.p("More on this", class_name="post-end-label"),
                rx.el.ul(
                    *[
                        rx.el.li(
                            _post_link(
                                other,
                                rx.el.span(
                                    other.get("title", "Untitled"),
                                    class_name="post-end-title",
                                ),
                            ),
                            rx.el.span(
                                f" · {other.get('date', '')}",
                                class_name="post-end-date",
                            ),
                        )
                        for other in related
                    ]
                ),
                aria_label="Related posts",
                class_name="post-end-related",
            )
        )
    discussion = str(meta.get("discussion_url", "")).strip()
    if discussion:
        parts.append(
            rx.el.p(
                rx.link(
                    discussion_label(discussion),
                    href=discussion,
                    is_external=True,
                    class_name="post-end-discussion",
                )
            )
        )
    parts.append(
        rx.el.div(
            rx.el.p(f"Written by {AUTHOR_NAME}, {AUTHOR_JOB_TITLE}."),
            rx.el.p(
                rx.link("About", href="/about"),
                rx.link("GitHub", href=GITHUB_URL, is_external=True),
                rx.link("LinkedIn", href=LINKEDIN_URL, is_external=True),
                # A file, not a route: skip client-side navigation.
                rx.link("RSS", href="/feed.xml", reload_document=True),
                class_name="post-end-profiles",
            ),
            class_name="post-end-author",
        )
    )
    return rx.el.div(
        *parts,
        class_name="post-end",
        style={
            **READING_COLUMN,
            "width": "100%",
            "margin_top": "var(--space-6)",
            "padding_top": "var(--space-5)",
            "border_top": f"1px solid {rx.color('gray', 5)}",
            "display": "flex",
            "flex_direction": "column",
            "gap": "var(--space-5)",
            "font_size": "var(--font-size-2)",
            "line_height": "var(--line-height-2)",
            "color": rx.color("slate", 11),
            "& p": {"margin": "0"},
            "& .post-end-neighbours": {
                "display": "grid",
                "grid_template_columns": "1fr 1fr",
                "gap": "var(--space-4)",
            },
            "& .post-end-neighbours .post-end-link": {
                "display": "flex",
                "flex_direction": "column",
                "gap": "var(--space-1)",
            },
            "& .post-end-label": {
                "font_size": "var(--font-size-1)",
                "color": rx.color("slate", 11),
            },
            "& .post-end-related .post-end-label": {"margin_bottom": "0.25em"},
            "& .post-end-title": {"color": rx.color("blue", 11)},
            "& .post-end-link:hover .post-end-title": {
                "text_decoration": "underline",
            },
            "& ul": {"list_style": "none", "margin": "0", "padding": "0"},
            "& li": {"margin": "0.4em 0"},
            "& .post-end-date": {"white_space": "nowrap"},
            "& .post-end-profiles": {
                "display": "flex",
                "flex_wrap": "wrap",
                "gap": "0 var(--space-4)",
                "margin_top": "var(--space-1)",
            },
            # These sit beside plain text; colour alone is under 3:1 against
            # it in dark mode, so underline them.
            "& :is(.post-end-profiles .rt-Link, .post-end-discussion, "
            "li .post-end-title)": {
                "text_decoration_line": "underline",
            },
            "& :is(.post-end-link, .rt-Link):focus-visible": {
                "outline": f"2px solid {rx.color('blue', 8)}",
                "outline_offset": "2px",
                "border_radius": "var(--radius-1)",
            },
        },
    )


def _render_post(
    meta: dict, body: str, posts: list[tuple[dict, str]] | None = None
) -> rx.Component:
    """Render a full blog post with metadata header and markdown body.

    The header and the body's running text keep to the reading measure, centred
    in the post column; figures, tables and code blocks use the full column. A
    post with ``TOC_MIN_SECTIONS`` or more H2s gets a table of contents between
    the header and the body, and every post closes with ``_post_end``.

    Args:
        meta: The post's frontmatter.
        body: The post's markdown.
        posts: The published posts, newest first, for the older/newer and
            related links; defaults to this post alone.

    Returns:
        The post's header, table of contents, body and end section.
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
            _type_badge(meta.get("type", "post"), size="2"),
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
        _post_end(meta, posts if posts is not None else [(meta, body)]),
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
                *[_type_badge(label, size="2") for label in DIATAXIS_COLORS],
                spacing="4",
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
                    _render_post(meta, body, posts),
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
