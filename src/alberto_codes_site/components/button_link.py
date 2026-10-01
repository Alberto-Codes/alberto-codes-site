"""Links that look like buttons, without a button nested inside a link."""

import reflex as rx
from reflex.components.el.elements.inline import a as html_a
from reflex.components.react_router.dom import ReactRouterLink


def button_link(
    *children: rx.Component | str,
    href: str,
    is_external: bool = False,
    **props,
) -> rx.Component:
    """Render a link styled as a Radix button.

    The button renders as the anchor itself (``as_child``), the same pattern
    as the header's resume link, so the page has no ``<button>`` inside an
    ``<a>``. An internal route keeps client-side navigation through the
    router's link; an external one is a plain anchor that opens a new tab.

    Args:
        *children: The button's contents, such as an icon and a label.
        href: The route or URL the link points to.
        is_external: Whether to open ``href`` in a new tab.
        **props: Button props, such as ``size`` and ``variant``.

    Returns:
        An anchor with button styling.
    """
    if is_external:
        anchor = html_a(
            *children, href=href, target="_blank", rel="noopener noreferrer"
        )
    else:
        anchor = ReactRouterLink.create(*children, to=href)
    return rx.button(anchor, as_child=True, **props)
