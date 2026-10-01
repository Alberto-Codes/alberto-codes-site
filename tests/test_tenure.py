"""The Wells Fargo tenure figure turns over on the anniversary, not before."""

from datetime import date

import pytest

from alberto_codes_site.tenure import years_at_wells_fargo


@pytest.mark.parametrize(
    ("today", "years"),
    [
        (date(2026, 8, 13), 25),
        (date(2026, 8, 14), 26),
        (date(2026, 10, 1), 26),
        (date(2027, 8, 13), 26),
        (date(2027, 8, 14), 27),
    ],
)
def test_years_at_wells_fargo_counts_completed_years(today: date, years: int) -> None:
    """The count rises on the anniversary itself and not a day before."""
    assert years_at_wells_fargo(today) == years


def test_years_at_wells_fargo_defaults_to_today() -> None:
    """With no date given, the helper measures to the build date."""
    assert years_at_wells_fargo() == years_at_wells_fargo(date.today())
