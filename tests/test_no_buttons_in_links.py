"""No route nests a ``<button>`` inside an ``<a>``, or an ``<a>`` inside one.

A button inside a link is two interactive elements in one, which assistive
technology announces confusingly and HTML forbids (issue #100). A link that
should look like a button renders as the anchor itself, through the button's
``as_child``. These checks walk each registered page's component tree without
a build: a Radix or HTML button renders ``<button>`` unless ``as_child`` hands
its styling to its child, and any anchor component renders ``<a>``.
"""

import pytest
from reflex.components.component import Component
from reflex.components.el.elements.forms import Button
from reflex.components.el.elements.inline import A

from alberto_codes_site.alberto_codes_site import app

PAGES = {page.route: page.component for page in app._unevaluated_pages.values()}


def _renders_button(component: Component) -> bool:
    """Return whether a component renders its own ``<button>`` element."""
    if not isinstance(component, Button):
        return False
    as_child = getattr(component, "as_child", None)
    return as_child is None or str(as_child) != "true"


def _nesting(component: Component, outer: str | None = None):
    """Yield (outer, inner) tags for each button or link inside the other."""
    tag = "a" if isinstance(component, A) else None
    tag = "button" if _renders_button(component) else tag
    if tag and outer and tag != outer:
        yield outer, tag
    for child in component.children:
        if isinstance(child, Component):
            yield from _nesting(child, outer or tag)


def test_routes_were_found():
    """The walk covers the pages that once nested buttons in links."""
    assert {"index", "projects"} <= set(PAGES)


@pytest.mark.parametrize("route", sorted(PAGES))
def test_no_button_inside_a_link(route):
    """Each route, navbar and footer included, keeps buttons and links apart."""
    nested = list(_nesting(PAGES[route]))
    assert not nested, f"/{route}: {nested}"
