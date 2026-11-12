"""Shared page widths, so every page lines up on the same centred column.

Each page is an ``rx.container(size="3")``, whose inner box is 880px wide.
Pages put their content in a column of ``PAGE_COLUMN`` inside it; a blog post
uses the full 880px so tables, figures and code blocks have room, and caps its
running text at ``READING_WIDTH``.

Examples:
    ```python
    import reflex as rx

    from alberto_codes_site.layout import PAGE_COLUMN, PAGE_PADDING_Y

    rx.container(
        rx.vstack(rx.heading("About"), **PAGE_COLUMN),
        size="3",
        padding_y=PAGE_PADDING_Y,
    )
    ```
"""

# Vertical padding of every page container. A bare Radix step such as "6" is
# not a CSS length, so browsers drop it; the space variable is.
PAGE_PADDING_Y = "var(--space-6)"

# The content column of every page but a blog post: 768px, centred.
PAGE_COLUMN = {"max_width": "48em", "width": "100%", "margin_x": "auto"}

# The measure of a post's running text: about 70 characters per line in the
# post body font, which is 18px on desktop (issue #78; the 16px/34rem first
# cut read narrow beside 880px figures). Set in rem rather than ch so that
# headings, whose ch is larger, share the paragraphs' left edge.
READING_WIDTH = "40rem"

# A post's running text from the md breakpoint up; phones keep the 16px base.
READING_FONT_SIZE = "1.125rem"

# Applied to a block that holds running text in a post: the reading measure,
# centred in the wider post column.
READING_COLUMN = {"max_width": READING_WIDTH, "margin_inline": "auto"}

# A post's full column: the inner width of the ``size="3"`` container, which
# tables, figures and code blocks may fill.
POST_COLUMN_WIDTH = "880px"

# A long post's contents become a rail in the right margin from this width.
# Measured with a 15px scrollbar: at 1400px the margin beside the 880px column
# is 252px, room for the gap, a rail of about 188px and a 2rem gutter; below
# it the rail would fall under 12rem and wrap most headings.
RAIL_MIN_VIEWPORT = "1400px"
RAIL_GAP = "2.5rem"
# The rail takes what the margin leaves after the gap and a 2rem gutter (100vw
# counts the scrollbar, which the gutter absorbs), up to 16rem.
RAIL_WIDTH = f"min(16rem, calc((100vw - {POST_COLUMN_WIDTH}) / 2 - {RAIL_GAP} - 2rem))"

# The widest a block of secondary text may run: an index summary, a
# publication's description, a page's introduction. In the site's sans the
# "0" is wider than the average letter, so 65ch sets about 80 characters to
# a line.
SUMMARY_MEASURE = "65ch"
