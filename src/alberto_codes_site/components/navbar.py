"""Top navigation bar component."""

import reflex as rx
from reflex.components.el.elements.inline import a as html_a

NAV_LINKS = [
    ("Home", "/"),
    ("About", "/about"),
    ("Experience", "/experience"),
    ("Projects", "/projects"),
    ("Publications", "/publications"),
    ("Blog", "/blog"),
    ("Contact", "/contact"),
]

THEME_TOGGLE_LABEL = "Toggle light and dark theme"


def _resume_link(*, icon_size: int, size: str, **props) -> rx.Component:
    """Render the resume download as a link styled like an outline button.

    The button renders as the anchor itself (``as_child``) so the header has
    no button nested inside a link. The anchor is a plain ``<a>``, since the
    PDF is a file, not a client-side route.

    Args:
        icon_size: The download icon size in pixels.
        size: The Radix button size.
        **props: Extra style props for the button, such as ``width``.

    Returns:
        An anchor to the resume PDF with outline-button styling.
    """
    return rx.button(
        html_a(
            rx.icon("download", size=icon_size),
            "Resume",
            href="/Alberto_Nieto_Resume.pdf",
            target="_blank",
            rel="noopener noreferrer",
        ),
        as_child=True,
        size=size,
        variant="outline",
        **props,
    )


def navbar() -> rx.Component:
    """Render the top navigation bar with links and mobile drawer."""
    return rx.box(
        rx.el.nav(
            rx.hstack(
                rx.link(
                    # A logo, not a heading: the heading look on a block span.
                    rx.heading(
                        rx.el.span("Alberto.Codes"),
                        as_child=True,
                        size="4",
                        weight="bold",
                        display="block",
                    ),
                    href="/",
                    underline="none",
                    color=rx.color("slate", 12),
                ),
                rx.spacer(),
                rx.hstack(
                    *[
                        rx.link(
                            label,
                            href=href,
                            size="2",
                            weight="medium",
                            underline="none",
                            color=rx.color("slate", 11),
                            _hover={"color": rx.color("slate", 12)},
                        )
                        for label, href in NAV_LINKS
                    ],
                    _resume_link(icon_size=14, size="1"),
                    rx.color_mode.button(size="1", aria_label=THEME_TOGGLE_LABEL),
                    spacing="5",
                    align="center",
                    display=["none", "none", "flex", "flex", "flex"],
                ),
                # Mobile menu
                rx.drawer.root(
                    rx.drawer.trigger(
                        rx.icon_button(
                            rx.icon("menu"),
                            aria_label="Open menu",
                            variant="ghost",
                            size="2",
                            display=["flex", "flex", "none", "none", "none"],
                        ),
                    ),
                    rx.drawer.overlay(),
                    rx.drawer.portal(
                        rx.drawer.content(
                            rx.el.nav(
                                rx.vstack(
                                    *[
                                        rx.link(
                                            label,
                                            href=href,
                                            size="4",
                                            underline="none",
                                            color=rx.color("slate", 11),
                                        )
                                        for label, href in NAV_LINKS
                                    ],
                                    _resume_link(icon_size=16, size="2", width="100%"),
                                    rx.color_mode.button(
                                        size="2", aria_label=THEME_TOGGLE_LABEL
                                    ),
                                    spacing="4",
                                    padding="6",
                                ),
                                aria_label="Main menu",
                            ),
                            top="auto",
                            left="auto",
                            height="100%",
                            width="16em",
                            background_color=rx.color("gray", 2),
                        ),
                    ),
                    direction="right",
                ),
                width="100%",
                align="center",
            ),
            aria_label="Main",
            width="100%",
        ),
        padding_x=["4", "4", "6", "8", "8"],
        padding_y="4",
        border_bottom=f"1px solid {rx.color('gray', 4)}",
        background_color=rx.color("gray", 2),
        position="sticky",
        top="0",
        z_index="10",
        width="100%",
    )
