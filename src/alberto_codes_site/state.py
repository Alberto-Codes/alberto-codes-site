"""Shared application state for the alberto.codes site."""

import reflex as rx


class SiteState(rx.State):
    """Shared app state.

    Examples:
        ```python
        class SiteState(rx.State):
            theme: str = "dark"
        ```
    """

    pass
