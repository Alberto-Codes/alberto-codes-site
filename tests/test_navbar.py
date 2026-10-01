"""The mobile menu dims the page, closes itself, and keeps focus inside.

Issue #38: the backdrop sat outside the drawer's portal, so it stayed in the
sticky header's stacking context, and following a link left the drawer open.
These checks walk the component tree without a build; the browser behaviour
(tap outside, Escape) is Vaul's and needs no backend in the static export.
"""

from reflex.components.component import Component
from reflex.components.radix.primitives.drawer import (
    DrawerClose,
    DrawerContent,
    DrawerOverlay,
    DrawerPortal,
    DrawerRoot,
    DrawerTitle,
)

from alberto_codes_site.components.navbar import NAV_LINKS, navbar


def _walk(component: Component):
    """Yield every component in the tree, depth first, in document order."""
    yield component
    for child in component.children:
        if isinstance(child, Component):
            yield from _walk(child)


def _drawer() -> DrawerRoot:
    """Return the navbar's one drawer root."""
    (root,) = [node for node in _walk(navbar()) if isinstance(node, DrawerRoot)]
    return root


def _targets(component: Component) -> set[str]:
    """Return every link target in a subtree, client routes and plain anchors.

    A Radix link keeps its route on the router link inside it (``to``); a
    plain anchor carries ``href``.
    """
    return {
        str(value).strip('"')
        for node in _walk(component)
        for value in (getattr(node, "to", None), getattr(node, "href", None))
        if value is not None
    }


def test_backdrop_is_portalled_with_the_panel():
    """The overlay renders in the portal, ahead of the panel it sits under."""
    root = _drawer()
    overlays = [node for node in _walk(root) if isinstance(node, DrawerOverlay)]
    assert len(overlays) == 1
    (portal,) = [node for node in _walk(root) if isinstance(node, DrawerPortal)]
    # The panel arrives wrapped in a theme, so find the child that holds it.
    holders = [
        index
        for index, child in enumerate(portal.children)
        if any(isinstance(node, DrawerContent) for node in _walk(child))
    ]
    assert portal.children.index(overlays[0]) < holders[0]


def test_every_menu_link_closes_the_drawer():
    """Each page link and the resume link sit inside a drawer close."""
    closes = [node for node in _walk(_drawer()) if isinstance(node, DrawerClose)]
    closing = set().union(*(_targets(close) for close in closes))
    assert {href for _, href in NAV_LINKS} | {"/Alberto_Nieto_Resume.pdf"} <= closing


def test_menu_dialog_has_a_name_and_takes_focus():
    """The dialog is named by a title, and focus moves into it on open."""
    root = _drawer()
    titles = [node for node in _walk(root) if isinstance(node, DrawerTitle)]
    assert len(titles) == 1
    assert root.custom_attrs.get("autoFocus") is True
