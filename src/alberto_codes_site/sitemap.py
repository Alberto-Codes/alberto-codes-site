"""The `/sitemap.xml` generator, on the sitemap protocol's own namespace.

Reflex's `SitemapPlugin` writes ``xmlns="https://www.sitemaps.org/..."``, but
the protocol namespace is ``http://www.sitemaps.org/schemas/sitemap/0.9`` and
strict parsers reject anything else (issue #101). The plugin hard-codes it
with no option to change it, so `SitemapPlugin` here reuses Reflex's link
collection and XML writer and swaps the namespace before the file is saved,
in the same compile step that `reflex run` and `reflex export` already run.

Every registered page is listed. A page opts into ``<lastmod>`` through
``add_page(context=sitemap_context(...))``; blog posts pass their frontmatter
date, and the other routes omit it rather than claim a date nobody recorded.

Examples:
    In `rxconfig.py`:

    ```python
    from alberto_codes_site.sitemap import SitemapPlugin

    config = rx.Config(app_name="alberto_codes_site", plugins=[SitemapPlugin()])
    ```
"""

from collections.abc import Sequence
from datetime import date

from reflex.plugins import sitemap as reflex_sitemap

SITEMAP_NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"
_REFLEX_NAMESPACE = "https://www.sitemaps.org/schemas/sitemap/0.9"


def post_lastmod(meta: dict) -> str | None:
    """Return a post's ``<lastmod>`` value from its frontmatter.

    Args:
        meta: The post's frontmatter.

    Returns:
        The ``updated`` date when the post has a valid one, else its ``date``,
        as `YYYY-MM-DD`; None when neither parses.
    """
    for key in ("updated", "date"):
        try:
            return date.fromisoformat(str(meta.get(key, "")).strip()).isoformat()
        except ValueError:
            continue
    return None


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
