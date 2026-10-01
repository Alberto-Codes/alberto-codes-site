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

MENU_TITLE = "Menu"

# Black at half opacity dims the page in either theme: on the light page it
# reads as a shade, on the dark one it still pushes the content back.
MENU_BACKDROP = "rgba(0, 0, 0, 0.5)"

# Vaul slides the panel and fades the backdrop in; skip both for readers who
# have asked their system for less motion.
REDUCED_MOTION = {
    "@media (prefers-reduced-motion: reduce)": {
        "transition": "none !important",
        "animation": "none !important",
    },
}

# Out of sight but still announced: the menu dialog's accessible name.
VISUALLY_HIDDEN = {
    "position": "absolute",
    "width": "1px",
    "height": "1px",
    "padding": "0",
    "margin": "-1px",
    "overflow": "hidden",
    "clip": "rect(0, 0, 0, 0)",
    "white_space": "nowrap",
    "border": "0",
}


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


def _mobile_menu() -> rx.Component:
    """Render the hamburger button and the drawer it opens on small screens.

    The drawer is Vaul's, built on the Radix dialog, so the backdrop, the
    close on a tap outside or on Escape, and the focus trap all run in the
    browser with no backend, which the static export does not have. The
    backdrop lives in the portal beside the panel so it covers the whole page
    rather than only the sticky header's stacking context. Each entry is
    wrapped in a drawer close, so following a link also shuts the menu.

    Returns:
        The drawer root holding the trigger, backdrop and menu panel.
    """
    return rx.drawer.root(
        rx.drawer.trigger(
            rx.icon_button(
                rx.icon("menu"),
                aria_label="Open menu",
                variant="ghost",
                size="2",
                display=["flex", "flex", "none", "none", "none"],
            ),
        ),
        rx.drawer.portal(
            rx.drawer.overlay(background=MENU_BACKDROP, style=REDUCED_MOTION),
            rx.drawer.content(
                rx.drawer.title(MENU_TITLE, style=VISUALLY_HIDDEN),
                rx.el.nav(
                    rx.vstack(
                        *[
                            rx.drawer.close(
                                rx.link(
                                    label,
                                    href=href,
                                    size="4",
                                    underline="none",
                                    color=rx.color("slate", 11),
                                ),
                            )
                            for label, href in NAV_LINKS
                        ],
                        rx.drawer.close(
                            _resume_link(icon_size=16, size="2", width="100%"),
                        ),
                        rx.color_mode.button(size="2", aria_label=THEME_TOGGLE_LABEL),
                        spacing="4",
                        padding="1.5em",
                    ),
                    aria_label="Main menu",
                    width="100%",
                ),
                top="auto",
                left="auto",
                height="100%",
                width="16em",
                background_color=rx.color("gray", 2),
                border_left=f"1px solid {rx.color('gray', 4)}",
                style=REDUCED_MOTION,
            ),
        ),
        direction="right",
        # Vaul leaves focus on the trigger unless asked, which lets Tab walk
        # the hidden page behind the backdrop; move it into the panel instead.
        custom_attrs={"autoFocus": True},
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
                _mobile_menu(),
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
