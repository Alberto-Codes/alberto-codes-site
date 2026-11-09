"""The `/sitemap.xml` generator, on the sitemap protocol's own namespace.

Reflex's `SitemapPlugin` writes ``xmlns="https://www.sitemaps.org/..."``, but
the protocol namespace is ``http://www.sitemaps.org/schemas/sitemap/0.9`` and
strict parsers reject anything else (issue #101). The plugin hard-codes it
with no option to change it, so `SitemapPlugin` here reuses Reflex's link
collection and XML writer and swaps the namespace before the file is saved,
in the same compile step that `reflex run` and `reflex export` already run.

Every registered page is listed with a ``<lastmod>``, passed through
``add_page(context=sitemap_context(...))``. Blog posts pass their updated
date (``post_updated``) or else their frontmatter date, and series pages
their newest part's date. A static page passes the last commit date of the
files that render it (``commit_date``), plus the newest post's date where it
lists posts. The deploy checks out full history so those dates are real.

Examples:
    In `rxconfig.py`:

    ```python
    from alberto_codes_site.sitemap import SitemapPlugin

    config = rx.Config(app_name="alberto_codes_site", plugins=[SitemapPlugin()])
    ```
"""

import subprocess
from collections.abc import Sequence
from pathlib import Path

from reflex.plugins import sitemap as reflex_sitemap

from alberto_codes_site.dates import parse_date, post_updated

SITEMAP_NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"
_REFLEX_NAMESPACE = "https://www.sitemaps.org/schemas/sitemap/0.9"
_REPO_ROOT = Path(__file__).resolve().parents[2]


def commit_date(*paths: Path) -> str | None:
    """Return the date of the last commit that touched any of ``paths``.

    Args:
        paths: Source files that render a page.

    Returns:
        The committer date as `YYYY-MM-DD`, or None outside a git checkout
        or when no commit touched the files.
    """
    result = subprocess.run(
        ["git", "log", "-1", "--format=%cs", "--", *map(str, paths)],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() or None


def latest(*dates: str | None) -> str | None:
    """Return the newest of some `YYYY-MM-DD` dates, ignoring None.

    Args:
        dates: ISO dates, any of which may be None.

    Returns:
        The latest date, or None when none is given.
    """
    return max((d for d in dates if d), default=None)


def post_lastmod(meta: dict, body: str = "") -> str | None:
    """Return a post's ``<lastmod>`` value.

    Args:
        meta: The post's frontmatter.
        body: The post's markdown, for its dated correction notes.

    Returns:
        The post's updated date (``post_updated``) when it has one, else its
        ``date``, as `YYYY-MM-DD`; None when neither parses.
    """
    updated = post_updated(meta, body)
    if updated:
        return updated
    published = parse_date(meta.get("date"))
    return published.isoformat() if published else None


def sitemap_context(lastmod: str | None) -> dict | None:
    """Build the ``context`` argument of ``app.add_page`` for a sitemap entry.

    Args:
        lastmod: A `YYYY-MM-DD` date, or None to leave ``<lastmod>`` out.

    Returns:
        ``{"sitemap": {"lastmod": lastmod}}``, or None when there is no date.
    """
    return {"sitemap": {"lastmod": lastmod}} if lastmod else None


def sitemap_xml(unevaluated_pages: Sequence) -> str:
    """Render the sitemap for the registered pages.

    Args:
        unevaluated_pages: The app's ``_unevaluated_pages`` values.

    Returns:
        The sitemap XML, on the protocol namespace.
    """
    links = reflex_sitemap.generate_links_for_sitemap(unevaluated_pages)
    xml_text = reflex_sitemap.generate_xml(links)
    return xml_text.replace(
        f'xmlns="{_REFLEX_NAMESPACE}"', f'xmlns="{SITEMAP_NAMESPACE}"', 1
    )


def sitemap_task(unevaluated_pages: Sequence) -> tuple[str, str]:
    """Return the sitemap's output path and content for Reflex's save step.

    Args:
        unevaluated_pages: The app's ``_unevaluated_pages`` values.

    Returns:
        The path under `.web/public` and the XML to write there.
    """
    return str(reflex_sitemap.Constants.FILE_PATH), sitemap_xml(unevaluated_pages)


class SitemapPlugin(reflex_sitemap.SitemapPlugin):
    """Reflex's sitemap plugin, writing the protocol's ``http://`` namespace."""

    def pre_compile(self, **context):
        """Queue the sitemap write before compilation.

        Args:
            context: The plugin context Reflex passes to ``pre_compile``.
        """
        context["add_save_task"](sitemap_task, context.get("unevaluated_pages", []))
