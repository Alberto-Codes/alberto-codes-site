"""Readable post dates, and the one rule for when a post was last updated.

Frontmatter dates are ISO `YYYY-MM-DD`. Pages show them as "1 Oct 2026"
inside ``<time datetime="2026-10-01">`` (issue #83), the same day-month-year
order the experience page's periods use.

A published post is a dated record: a claim that goes out of date gets a
``> Note YYYY-MM-DD:`` block appended rather than a rewrite (AGENTS.md). A
post's updated date is the later of its newest such note and its optional
frontmatter ``updated``, and only counts when it falls after the post's own
``date``. ``post_updated`` is the only place that rule lives: the post header's
"Updated" line, the sitemap ``<lastmod>`` and the JSON-LD ``dateModified`` all
read it.

Examples:
    ```python
    from alberto_codes_site.dates import post_updated, readable_date

    readable_date("2026-10-01")  # "1 Oct 2026"
    post_updated({"date": "2026-09-02"}, "> Note 2026-09-04: ...")  # "2026-09-04"
    ```
"""

import re
from datetime import date

import reflex as rx

_MONTHS = (
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
)

# A dated correction note: a blockquote line opening "Note YYYY-MM-DD:".
_NOTE = re.compile(r"^>\s*Note (\d{4}-\d{2}-\d{2}):", re.MULTILINE)


def parse_date(value: object) -> date | None:
    """Return the `YYYY-MM-DD` date in ``value``, or None when it does not parse.

    Args:
        value: A frontmatter value, usually a string.

    Returns:
        The date, or None.
    """
    try:
        return date.fromisoformat(str(value or "").strip())
    except ValueError:
        return None


def readable_date(value: object) -> str:
    """Return a `YYYY-MM-DD` date as "1 Oct 2026".

    Args:
        value: A frontmatter date.

    Returns:
        The readable date; the value unchanged when it does not parse.
    """
    day = parse_date(value)
    if day is None:
        return str(value or "")
    return f"{day.day} {_MONTHS[day.month - 1]} {day.year}"


def note_dates(body: str) -> list[date]:
    """Return the dates of a post body's ``> Note YYYY-MM-DD:`` blocks, in order.

    Args:
        body: The post's markdown.

    Returns:
        Each note's date; malformed dates are skipped.
    """
    found = (parse_date(m) for m in _NOTE.findall(body))
    return [d for d in found if d is not None]


def post_updated(meta: dict, body: str = "") -> str | None:
    """Return the date a post was last updated, or None when it never was.

    The later of the newest correction note in ``body`` and the frontmatter
    ``updated``, as `YYYY-MM-DD`, when it is after the post's ``date``.

    Args:
        meta: The post's frontmatter.
        body: The post's markdown.

    Returns:
        The updated date, or None.
    """
    candidates = note_dates(body)
    frontmatter = parse_date(meta.get("updated"))
    if frontmatter is not None:
        candidates.append(frontmatter)
    if not candidates:
        return None
    latest = max(candidates)
    published = parse_date(meta.get("date"))
    if published is not None and latest <= published:
        return None
    return latest.isoformat()


def time_el(value: object) -> rx.Component:
    """Render a date as ``<time datetime="YYYY-MM-DD">1 Oct 2026</time>``.

    Args:
        value: A frontmatter date.

    Returns:
        The ``time`` element; a malformed date is shown as written, with no
        ``datetime``.
    """
    day = parse_date(value)
    if day is None:
        return rx.el.time(str(value or ""))
    return rx.el.time(readable_date(day.isoformat()), date_time=day.isoformat())
