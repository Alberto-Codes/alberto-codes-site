"""Career tenure figures computed at build time rather than written by hand.

The site is static, so every page is rendered once per build. Deriving the
Wells Fargo tenure from a start date keeps the number right on each build
instead of waiting for someone to notice it has gone stale.

Examples:
    ```python
    from datetime import date

    from alberto_codes_site.tenure import years_at_wells_fargo

    years_at_wells_fargo(date(2026, 10, 1))  # 26
    ```
"""

from datetime import date

# First day at Wells Fargo. The career began in 1999 at Bank of America, which
# is why the earliest Experience role reads "1999 - 2006"; the tenure figure
# counts Wells Fargo alone.
WELLS_FARGO_START = date(2000, 8, 14)


def years_at_wells_fargo(today: date | None = None) -> int:
    """Return whole years at Wells Fargo as of ``today``.

    Args:
        today: The date to measure to. Defaults to the build date.

    Returns:
        Completed years since ``WELLS_FARGO_START``; the count rises on the
        anniversary itself.

    Examples:
        ```python
        years_at_wells_fargo(date(2026, 8, 13))  # 25
        years_at_wells_fargo(date(2026, 8, 14))  # 26
        ```
    """
    today = today or date.today()
    start = WELLS_FARGO_START
    before_anniversary = (today.month, today.day) < (start.month, start.day)
    return today.year - start.year - before_anniversary
