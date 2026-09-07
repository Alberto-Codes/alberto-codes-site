"""The PyPI package claim must say the same thing on every surface it appears on.

The home badge carries a count, the About paragraph names the packages and
repeats the count in words, and the current-role bullet on Experience names them
again. The provenance comment above ``PROJECTS`` in ``pages/projects.py`` records
that adding a package means editing all three; these checks fail when only some
of them are edited, which is how a count of six once ended up beside a list of
five names.
"""

import re

from alberto_codes_site.pages.about import about_page
from alberto_codes_site.pages.experience import ROLES
from alberto_codes_site.pages.home import home_page

NUMBER_WORDS = {
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}


def _rendered_text(component) -> list[str]:
    """Collect the literal strings a rendered component tree puts on the page."""
    found: list[str] = []

    def walk(node) -> None:
        for child in getattr(node, "children", None) or []:
            walk(child)
        contents = getattr(node, "contents", None)
        if contents is None:
            return
        text = str(contents).strip('"')
        if text:
            found.append(text.encode().decode("unicode_escape"))

    walk(component)
    return found


def _first_match(pattern: str, texts: list[str], what: str) -> re.Match[str]:
    for text in texts:
        match = re.search(pattern, text)
        if match:
            return match
    raise AssertionError(
        f"{what} is no longer on the page in the shape this check reads. "
        "If the copy was deliberately reshaped, update this test with it."
    )


def _split_names(listing: str) -> list[str]:
    """Split a prose list of package names into the names themselves."""
    items = re.split(r",\s*(?:and\s+)?|\s+and\s+", listing)
    return [item.split(" for ")[0].strip() for item in items if item.strip()]


def _home_badge_count() -> int:
    match = _first_match(
        r"(\d+) PyPI Packages", _rendered_text(home_page()), "The home page badge"
    )
    return int(match.group(1))


def _about_claim() -> tuple[list[str], int]:
    match = _first_match(
        r"including (.+?)\. All (\w+) are on PyPI",
        _rendered_text(about_page()),
        "The About paragraph's open source sentence",
    )
    return _split_names(match.group(1)), NUMBER_WORDS[match.group(2)]


def _experience_names() -> list[str]:
    bullets = [bullet for role in ROLES for bullet in role["bullets"]]
    match = _first_match(
        r"shipped (.+?) to PyPI", bullets, "The current-role open source bullet"
    )
    return _split_names(match.group(1))


def test_home_badge_count_matches_the_about_paragraph() -> None:
    badge = _home_badge_count()
    names, spelled_out = _about_claim()
    assert spelled_out == badge, (
        f"home badge says {badge} packages, About says {spelled_out}"
    )
    assert len(names) == badge, (
        f"home badge says {badge} packages, About names {len(names)}: {names}"
    )


def test_about_and_experience_name_the_same_packages() -> None:
    about_names, _ = _about_claim()
    experience_names = _experience_names()
    assert set(about_names) == set(experience_names), (
        f"About names {sorted(about_names)}, "
        f"the experience bullet names {sorted(experience_names)}"
    )
