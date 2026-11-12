"""Metadata labels: tags, kinds and periods that read as text, not buttons.

A bordered, padded pill reads as something to press. Nothing on the site
filters by tag yet (issue #79), so a tag is set as small muted text, and a
run of tags as an inline list with middots between the items. A label that
names a kind, such as a post's Diataxis type, is a small-cap mark in the
same muted ink: the kind shows in its letterforms, not in a hue.

Examples:
    ```python
    from alberto_codes_site.components.meta_label import meta_label, meta_list

    meta_list(["Python", "CLI"])
    meta_label("tutorial", mark=True)
    ```
"""

import reflex as rx

# Separator drawn between list items. The empty alternative text after the
# slash keeps screen readers from announcing it.
_MIDDOT = '"\\00B7" / ""'

# Room each middot takes before its item, and how far a left-aligned list is
# pulled past its clipping box so the line-opening middots fall outside it.
_SEPARATOR_WIDTH = "1.25em"


def meta_label(
    text: str,
    mark: bool = False,
    size: str = "1",
) -> rx.Component:
    """Render one metadata label as plain inline text.

    Args:
        text: The label's text.
        mark: Set the label as a small-cap mark, for a kind such as a post's
            Diataxis type. A mark is told apart by its letterforms, not by a
            colour; it stays in the muted gray ink.
        size: The Radix text size.

    Returns:
        A span of small text with the default cursor.
    """
    mark_style = (
        {
            "font_variant_caps": "all-small-caps",
            "letter_spacing": "0.05em",
            "font_weight": "600",
        }
        if mark
        else {}
    )
    return rx.text(
        text,
        as_="span",
        size=size,
        color=rx.color("gray", 11),
        cursor="default",
        white_space="nowrap",
        class_name="meta-mark" if mark else None,
        style=mark_style,
    )


def meta_list(
    items: list[str],
    size: str = "1",
    justify: str = "start",
) -> rx.Component:
    """Render a run of tags as an inline list.

    A left-aligned list puts a middot before every item and pulls the list
    one separator's width past its clipping box, so the middot that would
    open each wrapped line is cut off. A centred list has no fixed line
    start to clip at, so its items are separated by a wider gap instead.

    Args:
        items: The tags, in display order.
        size: The Radix text size of each tag.
        justify: How wrapped lines align: ``"start"`` or ``"center"``.

    Returns:
        An unstyled list whose items wrap as whole words.
    """
    centred = justify == "center"
    style = {
        "display": "flex",
        "flex_wrap": "wrap",
        "align_items": "baseline",
        "justify_content": justify,
        "column_gap": "1.25em" if centred else "0",
        "row_gap": "0.25em",
        "list_style": "none",
        "margin": "0",
        "padding": "0",
    }
    if not centred:
        style["margin_inline_start"] = f"-{_SEPARATOR_WIDTH}"
        style["& > li::before"] = {
            "content": _MIDDOT,
            "display": "inline-block",
            "width": _SEPARATOR_WIDTH,
            "text_align": "center",
            "color": rx.color("gray", 9),
        }
    items_list = rx.el.ul(
        *[rx.el.li(meta_label(item, size=size)) for item in items], style=style
    )
    return rx.box(items_list, overflow="hidden", cursor="default", width="100%")
