"""Blog page with markdown post rendering and individual post routes."""

import math
from pathlib import Path

import reflex as rx

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
    """Load all markdown posts sorted by date descending."""
    posts = []
    if POSTS_DIR.exists():
        for f in sorted(POSTS_DIR.glob("*.md"), reverse=True):
            meta, body = _parse_frontmatter(f.read_text())
            meta.setdefault("slug", f.stem)
            meta["reading_time"] = _reading_time(body)
            posts.append((meta, body))
    return posts


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
                        color=rx.color("slate", 9),
                    ),
                    rx.text(
                        f"{meta.get('reading_time', 1)} min read",
                        size="1",
                        color=rx.color("slate", 9),
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.heading(
                    meta.get("title", "Untitled"),
                    size="4",
                    weight="bold",
                ),
                rx.text(
                    meta.get("summary", ""),
                    size="2",
                    color=rx.color("slate", 10),
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


def _render_post(meta: dict, body: str) -> rx.Component:
    """Render a full blog post with metadata header and markdown body."""
    return rx.vstack(
        rx.link(
            rx.hstack(
                rx.icon("arrow-left", size=14),
                rx.text("Back to Blog", size="2"),
                spacing="1",
                align="center",
            ),
            href="/blog",
            underline="none",
            color=rx.color("blue", 9),
        ),
        rx.box(height="1em"),
        rx.hstack(
            _type_badge(meta.get("type", "post")),
            rx.text(meta.get("date", ""), size="2", color=rx.color("slate", 9)),
            rx.text(
                f"{meta.get('reading_time', 1)} min read",
                size="2",
                color=rx.color("slate", 9),
            ),
            spacing="2",
            align="center",
        ),
        rx.heading(
            meta.get("title", "Untitled"),
            size="7",
            weight="bold",
        ),
        rx.text(
            meta.get("summary", ""),
            size="3",
            color=rx.color("slate", 10),
            style={"font-style": "italic"},
        ),
        rx.separator(size="4", color_scheme="blue"),
        rx.box(
            rx.markdown(body, use_gfm=True),
            width="100%",
        ),
        spacing="4",
        width="100%",
    )


def blog_page() -> rx.Component:
    """Render the blog index page listing all posts."""
    posts = _load_posts()

    if not posts:
        return rx.container(
            rx.vstack(
                rx.box(height="4em"),
                rx.heading("Blog", size="8", weight="bold"),
                rx.separator(size="4", color_scheme="blue"),
                rx.box(height="4em"),
                rx.vstack(
                    rx.icon("notebook-pen", size=48, color=rx.color("slate", 7)),
                    rx.heading("Coming Soon", size="6", color=rx.color("slate", 9)),
                    rx.text(
                        "I'm working on sharing thoughts on AI engineering, "
                        "career growth, and technical leadership.",
                        size="3",
                        color=rx.color("slate", 10),
                        text_align="center",
                        max_width="24em",
                    ),
                    align="center",
                    spacing="4",
                ),
                spacing="4",
                align="center",
                min_height="60vh",
            ),
            size="3",
            padding_y="6",
        )

    return rx.container(
        rx.vstack(
            rx.box(height="4em"),
            rx.heading("Blog", size="8", weight="bold"),
            rx.separator(size="4", color_scheme="blue"),
            rx.box(height="1em"),
            rx.text(
                "Thoughts on AI engineering, Python, career growth, and "
                "technical leadership — organized using the Diataxis framework.",
                size="3",
                color=rx.color("slate", 10),
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
            max_width="48em",
        ),
        size="3",
        padding_y="6",
    )


def blog_post_page(slug: str) -> rx.Component:
    """Render an individual blog post by slug."""
    posts = _load_posts()
    for meta, body in posts:
        if meta.get("slug") == slug:
            return rx.container(
                rx.vstack(
                    rx.box(height="4em"),
                    _render_post(meta, body),
                    spacing="4",
                    max_width="48em",
                ),
                size="3",
                padding_y="6",
            )
    # Post not found
    return rx.container(
        rx.vstack(
            rx.box(height="4em"),
            rx.heading("Post Not Found", size="7", weight="bold"),
            rx.text(
                "Sorry, that post doesn't exist.", size="3", color=rx.color("slate", 10)
            ),
            rx.link("Back to Blog", href="/blog", color=rx.color("blue", 9)),
            spacing="4",
            align="center",
            min_height="60vh",
        ),
        size="3",
        padding_y="6",
    )
