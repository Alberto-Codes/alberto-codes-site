"""Shared UI components for the site layout.

Examples:
    Use in a page layout:

    ```python
    from alberto_codes_site.components import navbar, footer


    def layout(page):
        return rx.vstack(navbar(), page, footer())
    ```

See Also:
    [`alberto_codes_site.pages`][alberto_codes_site.pages]: Page components.
"""

from .footer import footer as footer
from .navbar import navbar as navbar
