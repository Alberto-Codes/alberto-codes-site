"""Stable, GitHub-style slug ids for the headings in a post body.

The ids are computed in Python from the markdown source rather than by a
rehype plugin in the browser, so they are the same on every build, unique
across a whole post even when the body is split into several markdown runs
(figures are inlined between runs, ADR-0005), and testable without a build.
"""

import json
import re
from collections.abc import Callable, Iterable

import reflex as rx

# Reflex's default markdown heading sizes, kept so ids do not change the look.
_MARKDOWN_HEADING_SIZES = {1: "6", 2: "5", 3: "4", 4: "3", 5: "2", 6: "1"}

_ATX_HEADING = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?(?:[ \t]+#+)?[ \t]*$")
_FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_HTML_TAG = re.compile(r"<[^>]+>")
_NOT_SLUG_CHAR = re.compile(r"[^\w\- ]")


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
        plain = _HTML_TAG.sub("", _LINK.sub(r"\1", _IMAGE.sub("", text)))
        base = _NOT_SLUG_CHAR.sub("", plain.strip().lower()).replace(" ", "-")
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


def heading_component_map(ids: dict[int, str]) -> dict[str, Callable]:
    """Build `rx.markdown` heading renderers that carry the given ids.

    react-markdown passes each element's hast `node`, whose position is its
    line in the run, so the renderer looks its id up by that line.

    Args:
        ids: The line-to-id mapping from `heading_ids` for this run.

    Returns:
        A component map for the tags h1 to h6.
    """
    lookup = rx.Var(f"({json.dumps(ids)})[node?.position?.start?.line]")
    # Lambdas, not a named inner function: Reflex names a markdown component
    # map by hashing a rendered lambda but only the qualified name of a def,
    # so runs with different ids would otherwise share one map.
    return {
        f"h{level}": (
            lambda value, _level=level, _size=size: rx.heading(
                value,
                as_=f"h{_level}",
                size=_size,
                margin_y="0.5em",
                id=lookup,
            )
        )
        for level, size in _MARKDOWN_HEADING_SIZES.items()
    }
