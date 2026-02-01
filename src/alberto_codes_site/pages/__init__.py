"""Site pages for the alberto.codes portfolio.

Examples:
    Import and use a page:

    ```python
    from alberto_codes_site.pages import home_page

    app.add_page(home_page(), route="/")
    ```

See Also:
    [`alberto_codes_site.components`][alberto_codes_site.components]: Shared UI components.
"""

from .about import about_page as about_page
from .blog import blog_page as blog_page
from .blog import blog_post_page as blog_post_page
from .contact import contact_page as contact_page
from .experience import experience_page as experience_page
from .home import home_page as home_page
from .projects import projects_page as projects_page
