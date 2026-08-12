"""Top navigation bar component."""

import reflex as rx

NAV_LINKS = [
    ("Home", "/"),
    ("About", "/about"),
    ("Experience", "/experience"),
    ("Projects", "/projects"),
    ("Publications", "/publications"),
    ("Blog", "/blog"),
    ("Contact", "/contact"),
]


def navbar() -> rx.Component:
    """Render the top navigation bar with links and mobile drawer."""
    return rx.box(
        rx.hstack(
            rx.link(
                rx.heading("Alberto.Codes", size="4", weight="bold"),
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
                rx.link(
                    rx.button(
                        rx.icon("download", size=14),
                        "Resume",
                        size="1",
                        variant="outline",
                    ),
                    href="/Alberto_Nieto_Resume.pdf",
                    is_external=True,
                    underline="none",
                ),
                rx.color_mode.button(size="1"),
                spacing="5",
                align="center",
                display=["none", "none", "flex", "flex", "flex"],
            ),
            # Mobile menu
            rx.drawer.root(
                rx.drawer.trigger(
                    rx.icon_button(
                        rx.icon("menu"),
                        variant="ghost",
                        size="2",
                        display=["flex", "flex", "none", "none", "none"],
                    ),
                ),
                rx.drawer.overlay(),
                rx.drawer.portal(
                    rx.drawer.content(
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
                            rx.link(
                                rx.button(
                                    rx.icon("download", size=16),
                                    "Resume",
                                    size="2",
                                    variant="outline",
                                    width="100%",
                                ),
                                href="/Alberto_Nieto_Resume.pdf",
                                is_external=True,
                                underline="none",
                                width="100%",
                            ),
                            rx.color_mode.button(size="2"),
                            spacing="4",
                            padding="6",
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
        padding_x=["4", "4", "6", "8", "8"],
        padding_y="4",
        border_bottom=f"1px solid {rx.color('gray', 4)}",
        background_color=rx.color("gray", 2),
        position="sticky",
        top="0",
        z_index="10",
        width="100%",
    )
