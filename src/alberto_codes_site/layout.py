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
