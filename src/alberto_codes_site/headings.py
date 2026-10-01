"""Stable, GitHub-style slug ids for the headings in a post body.

The ids are computed in Python from the markdown source rather than by a
rehype plugin in the browser, so they are the same on every build, unique
across a whole post even when the body is split into several markdown runs
(figures are inlined between runs, ADR-0005), and testable without a build.
The same ids feed a post's table of contents and each heading's anchor link
(issue #75, ADR-0003).
"""

import json
import re
from collections.abc import Callable, Iterable

import reflex as rx


def fragment_link(*children, **props) -> rx.Component:
    """Render a link to a fragment of the current page.

    It must be React Router's link, which `rx.el.a` renders: a plain `<a>`
    jump is a history entry the router did not make, so its scroll restoration
    puts the page back where it was. A router push scrolls the target into
    view, honouring its `scroll-margin-top`.

    Args:
        *children: The link's content.
        **props: Props for `rx.el.a`; `href` is ``#<id>``.

    Returns:
        The link component.
    """
    return rx.el.a(*children, **props)


# Reflex's default markdown heading sizes, kept so ids do not change the look.
_MARKDOWN_HEADING_SIZES = {1: "6", 2: "5", 3: "4", 4: "3", 5: "2", 6: "1"}

# Room above a heading that a fragment link scrolls to, so the sticky site
# header (about 57px tall) does not cover it.
SCROLL_MARGIN = "5rem"

_ATX_HEADING = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?(?:[ \t]+#+)?[ \t]*$")
_FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_HTML_TAG = re.compile(r"<[^>]+>")
_NOT_SLUG_CHAR = re.compile(r"[^\w\- ]")
_EMPHASIS = re.compile(r"[`*]|~~")
_SPACES = re.compile(r"\s+")


def _plain(text: str) -> str:
    """Drop a heading's images, link targets and HTML tags, keeping its words."""
    return _HTML_TAG.sub("", _LINK.sub(r"\1", _IMAGE.sub("", text)))


def heading_label(text: str) -> str:
    """Return a heading's text as a reader sees it, without markdown syntax.

    Args:
        text: The heading's inline markdown, without the leading hashes.

    Returns:
        The plain text, for a table of contents entry or an accessible name.

    Examples:
        ```python
        heading_label("The `vramfit` CLI")  # "The vramfit CLI"
        ```
    """
    return _SPACES.sub(" ", _EMPHASIS.sub("", _plain(text))).strip()


class Slugger:
    """Hand out GitHub-style slugs, suffixing repeats with -1, -2, and so on.

    Examples:
        ```python
        slugger = Slugger()
        slugger.slug("Why it works")  # "why-it-works"
        slugger.slug("Why it works")  # "why-it-works-1"
        ```
    """

    def __init__(self) -> None:
        """Start with no slugs taken."""
        self._seen: dict[str, int] = {}

    def slug(self, text: str) -> str:
        """Return a unique slug for a heading's markdown text.

        Args:
            text: The heading's inline markdown, without the leading hashes.

        Returns:
            The lowercase slug, unique among the slugs this instance returned.
        """
        base = _NOT_SLUG_CHAR.sub("", _plain(text).strip().lower()).replace(" ", "-")
        base = base or "section"
        candidate = base
        while candidate in self._seen:
            self._seen[base] += 1
            candidate = f"{base}-{self._seen[base]}"
        self._seen[candidate] = 0
        return candidate


def heading_lines(markdown: str) -> Iterable[tuple[int, int, str]]:
    """Yield each ATX heading outside fenced code as (line, level, text).

    Args:
        markdown: A markdown source string.

    Yields:
        The 1-based line number, the heading level and its inline text.
    """
    fence: str | None = None
    for number, line in enumerate(markdown.splitlines(), start=1):
        if match := _FENCE.match(line):
            marker = match.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                if not line.strip().lstrip(marker[0]):
                    fence = None
            continue
        if fence is not None:
            continue
        if match := _ATX_HEADING.match(line):
            yield number, len(match.group(1)), match.group(2) or ""


def heading_ids(markdown: str, slugger: Slugger) -> dict[int, str]:
    """Map each heading's line number in one markdown run to its slug id.

    Args:
        markdown: The markdown run, exactly as it is passed to `rx.markdown`.
        slugger: The slugger shared by every run of the same post.

    Returns:
        A mapping of 1-based line number to id.
    """
    return {line: slugger.slug(text) for line, _level, text in heading_lines(markdown)}


def heading_labels(markdown: str) -> dict[int, str]:
    """Map each heading's line number in one markdown run to its plain text.

    Args:
        markdown: The markdown run, exactly as it is passed to `rx.markdown`.

    Returns:
        A mapping of 1-based line number to `heading_label` text.
    """
    return {line: heading_label(text) for line, _level, text in heading_lines(markdown)}


def heading_component_map(
    ids: dict[int, str], labels: dict[int, str]
) -> dict[str, Callable]:
    """Build `rx.markdown` heading renderers that carry ids and anchor links.

    react-markdown passes each element's hast `node`, whose position is its
    line in the run, so the renderer looks its id and label up by that line.
    Each heading is wrapped with a sibling link to its own fragment, labelled
    "Link to section: <heading text>". The link sits beside the heading, not
    inside it, so the heading's accessible name stays its own text; the page
    style (`heading_anchor_style`) shows it on hover and keyboard focus.

    Args:
        ids: The line-to-id mapping from `heading_ids` for this run.
        labels: The line-to-text mapping from `heading_labels` for this run.

    Returns:
        A component map for the tags h1 to h6.
    """
    lookup = rx.Var(f"({json.dumps(ids)})[node?.position?.start?.line]")
    label = rx.Var(f"({json.dumps(labels)})[node?.position?.start?.line]")
    href = rx.Var(f"('#' + {lookup})")
    name = rx.Var(f"('Link to section: ' + {label})")
    # Lambdas, not a named inner function: Reflex names a markdown component
    # map by hashing a rendered lambda but only the qualified name of a def,
    # so runs with different ids would otherwise share one map.
    return {
        f"h{level}": (
            lambda value, _level=level, _size=size: rx.el.div(
                rx.heading(
                    value,
                    as_=f"h{_level}",
                    size=_size,
                    margin_y="0.5em",
                    id=lookup,
                ),
                fragment_link(
                    rx.icon("link", size=16, aria_hidden="true"),
                    href=href,
                    aria_label=name,
                    title=name,
                    class_name="heading-anchor",
                ),
                class_name="heading-wrap",
            )
        )
        for level, size in _MARKDOWN_HEADING_SIZES.items()
    }


def heading_anchor_style() -> dict:
    """Return the post body style for heading wrappers and their anchor links.

    The link is hidden until its heading is hovered or the link has keyboard
    focus. A touch screen has no hover, so there it always shows, muted. Every
    heading keeps clear of the sticky site header when a fragment scrolls to it.

    Returns:
        A style dict for the element that holds the post body.
    """
    return {
        "& :is(h1, h2, h3, h4, h5, h6)[id]": {"scroll_margin_top": SCROLL_MARGIN},
        "& .heading-wrap": {"position": "relative"},
        "& .heading-wrap > :is(h1, h2, h3, h4, h5, h6)": {
            "padding_inline_end": "2rem",
        },
        "& .heading-anchor": {
            "position": "absolute",
            "top": "0",
            "right": "0",
            "display": "inline-flex",
            "align_items": "center",
            "justify_content": "center",
            "width": "2rem",
            "height": "2rem",
            "border_radius": "var(--radius-2)",
            "color": rx.color("gray", 11),
            "opacity": "0",
        },
        "& .heading-wrap:hover .heading-anchor, & .heading-anchor:focus-visible": {
            "opacity": "1",
        },
        "& .heading-anchor:hover": {"color": rx.color("blue", 11)},
        "& .heading-anchor:focus-visible": {
            "outline": f"2px solid {rx.color('blue', 8)}",
            "outline_offset": "1px",
        },
        "@media (hover: none)": {"& .heading-anchor": {"opacity": "1"}},
    }
