"""Blog series: posts that share a frontmatter ``series`` title (issue #51).

A post joins a series with one frontmatter line, ``series: <Display Title>``.
The series slug, and so its page at ``/blog/series/<slug>``, comes from that
title through the same ``Slugger`` that gives headings their ids. Parts are
numbered by date, oldest first, with ties broken by slug (the file name).

Callers pass *published* posts (``published_posts`` in ``pages/blog.py``), so
a future-dated part is neither counted nor linked until its date arrives.

Examples:
    ```python
    from alberto_codes_site.series import build_series, series_of

    all_series = build_series(published)
    series = series_of(meta, all_series)
    if series is not None:
        print(f"Part {series.number(meta['slug'])} of {len(series)}")
    ```
"""

from dataclasses import dataclass

from alberto_codes_site.headings import Slugger

SERIES_ROUTE_PREFIX = "/blog/series"


def series_title(meta: dict) -> str | None:
    """Return a post's ``series`` title, or None when it has none.

    Args:
        meta: The post's frontmatter.

    Returns:
        The stripped title, or None when the field is missing or blank.
    """
    title = meta.get("series")
    if not isinstance(title, str):
        return None
    return title.strip() or None


def series_slug(title: str) -> str:
    """Return the URL slug for a series title.

    Args:
        title: The series display title.

    Returns:
        The heading-style slug, such as ``turboquant-on-vision-models``.
    """
    return Slugger().slug(title)


@dataclass(frozen=True)
class Series:
    """One series and its published parts, oldest first.

    Attributes:
        title: The display title from the frontmatter.
        slug: The URL slug derived from the title.
        parts: Each part's frontmatter, in part order.
    """

    title: str
    slug: str
    parts: tuple[dict, ...]

    def __len__(self) -> int:
        """Return the number of published parts."""
        return len(self.parts)

    @property
    def route(self) -> str:
        """Return the series page route, ``/blog/series/<slug>``."""
        return f"{SERIES_ROUTE_PREFIX}/{self.slug}"

    @property
    def first_date(self) -> str:
        """Return the first part's frontmatter date."""
        return str(self.parts[0].get("date", ""))

    @property
    def last_date(self) -> str:
        """Return the newest part's frontmatter date."""
        return str(self.parts[-1].get("date", ""))

    def number(self, slug: str) -> int:
        """Return a part's 1-based number.

        Args:
            slug: The part's post slug.

        Returns:
            Its position in the series, counting from 1.

        Raises:
            ValueError: When the slug is not a part of this series.
        """
        for i, part in enumerate(self.parts, start=1):
            if part.get("slug") == slug:
                return i
        raise ValueError(f"{slug!r} is not a part of {self.title!r}")

    def neighbours(self, slug: str) -> tuple[dict | None, dict | None]:
        """Return the parts just before and just after ``slug``.

        Args:
            slug: The part's post slug.

        Returns:
            ``(previous, next)`` frontmatter; either is None at that end.
        """
        i = self.number(slug) - 1
        previous = self.parts[i - 1] if i > 0 else None
        following = self.parts[i + 1] if i + 1 < len(self.parts) else None
        return previous, following


def build_series(posts: list[tuple[dict, str]]) -> list[Series]:
    """Group posts into series by their ``series`` title.

    Args:
        posts: ``(meta, body)`` pairs, already filtered by ``published_posts``.

    Returns:
        Every series with at least one part, the one with the newest part
        first.

    Raises:
        ValueError: When two different titles give the same slug.
    """
    grouped: dict[str, list[dict]] = {}
    for meta, _ in posts:
        title = series_title(meta)
        if title is not None:
            grouped.setdefault(title, []).append(meta)
    found: list[Series] = []
    slugs: dict[str, str] = {}
    for title, parts in grouped.items():
        slug = series_slug(title)
        if slug in slugs:
            raise ValueError(f"series {title!r} and {slugs[slug]!r} share {slug!r}")
        slugs[slug] = title
        parts.sort(key=lambda m: (str(m.get("date", "")), str(m.get("slug", ""))))
        found.append(Series(title=title, slug=slug, parts=tuple(parts)))
    found.sort(key=lambda s: (s.last_date, s.slug), reverse=True)
    return found


def series_of(meta: dict, all_series: list[Series]) -> Series | None:
    """Return the series a post belongs to, if any.

    Args:
        meta: The post's frontmatter.
        all_series: The series from ``build_series``.

    Returns:
        The post's series, or None for a standalone post or one whose series
        does not list it (a future-dated part).
    """
    title = series_title(meta)
    for series in all_series:
        if series.title == title and any(
            p.get("slug") == meta.get("slug") for p in series.parts
        ):
            return series
    return None
