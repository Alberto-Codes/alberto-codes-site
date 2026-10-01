"""Pages share one centred column, and a post's running text keeps a measure.

Issue #78. The rendered line length (about 70 characters at 1440px wide) was
measured in a browser against the static export (see the pull request); these
checks read the JSX the pages compile to so the widths and the padding cannot
drift back.
"""

import re

import pytest

from alberto_codes_site.layout import PAGE_PADDING_Y, READING_WIDTH
from alberto_codes_site.pages.about import about_page
from alberto_codes_site.pages.blog import _render_post, blog_page, blog_post_page
from alberto_codes_site.pages.contact import contact_page
from alberto_codes_site.pages.experience import experience_page
from alberto_codes_site.pages.home import home_page
from alberto_codes_site.pages.not_found import not_found_page
from alberto_codes_site.pages.projects import projects_page
from alberto_codes_site.pages.publications import publications_page

PAGES = {
    "home": home_page,
    "about": about_page,
    "blog": blog_page,
    "contact": contact_page,
    "experience": experience_page,
    "not_found": not_found_page,
    "projects": projects_page,
    "publications": publications_page,
    "missing post": lambda: blog_post_page("no-such-post"),
}

# A padding or margin whose value is a bare non-zero number, such as the
# Radix step "6": browsers drop it as an invalid length.
UNITLESS = re.compile(r'\["(?:padding|margin)\w*"\] : "[1-9][0-9.]*"')


@pytest.mark.parametrize("page", PAGES.values(), ids=PAGES.keys())
def test_page_padding_is_a_css_length(page):
    """No page container passes a unitless padding or margin."""
    jsx = str(page())
    assert not UNITLESS.findall(jsx)
    assert f'["paddingTop"] : "{PAGE_PADDING_Y}"' in jsx


@pytest.mark.parametrize("page", PAGES.values(), ids=PAGES.keys())
def test_page_column_is_centred_at_the_shared_width(page):
    """Every page but a post centres its content in the same 48em column."""
    jsx = str(page())
    assert (
        '["maxWidth"] : "48em", ["width"] : "100%", '
        '["marginInlineStart"] : "auto", ["marginInlineEnd"] : "auto"'
    ) in jsx


def test_post_text_keeps_the_measure_and_wide_blocks_do_not():
    """Running text and the header cap at the measure; code and tables do not."""
    jsx = str(_render_post({"title": "T"}, "Text.\n\n- item\n\n| a |\n|---|\n| 1 |\n"))
    # The header.
    assert f'["maxWidth"] : "{READING_WIDTH}", ["marginInline"] : "auto"' in jsx
    # The body: text blocks are capped; tables, code and figures are not listed.
    assert (
        '["& :is(p:not(:has(> img)), h2, h3, h4, h5, h6, blockquote)"] : '
        f'({{ ["maxWidth"] : "{READING_WIDTH}", ["marginInline"] : "auto" }})'
    ) in jsx
    assert f'["maxWidth"] : "calc({READING_WIDTH} - 1.5rem)"' in jsx
