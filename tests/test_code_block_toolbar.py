"""Fenced code blocks carry a language label and a client-side copy button.

Issue #76. Markdown hands the ``pre`` renderer the block text as the JS
variable ``children`` and the fenced language as ``_language`` (empty when the
fence names none), so the label and the copy have to be decided in the
browser. These checks render ``_code_block`` with those same variables and
read the JSX it compiles to; the clipboard itself was proven in a browser
against the static export (see the pull request).
"""

from reflex.components.markdown.markdown import Markdown
from reflex.vars import Var

from alberto_codes_site.pages.blog import _code_block, _post_body

CHILDREN = Var(_js_expr="children", _var_type=str)
LANGUAGE = Var(_js_expr="_language", _var_type=str)


def _render() -> str:
    """Compile a code block the way the markdown ``pre`` map calls it."""
    return str(_code_block(CHILDREN, language=LANGUAGE))


def test_label_shows_the_fenced_language_only_when_there_is_one():
    """The label renders the fence's language, and nothing for a bare fence."""
    jsx = _render()
    assert 'jsx("span",{className:"code-language"},_language)' in jsx
    assert "isTrue(_language)" in jsx


def test_copy_button_is_a_named_keyboard_reachable_button():
    """The copy control is a native button named "Copy code"."""
    jsx = _render()
    button = jsx[jsx.index('jsx("button"') :]
    button = button[: button.index("jsx(LucideCopy")]
    assert '"aria-label":"Copy code"' in button
    assert 'type:"button"' in button
    # A native <button> with no tabIndex override is in the tab order.
    assert "tabIndex" not in button


def test_copy_writes_the_block_text_in_the_browser():
    """Clicking copies the block text client-side, with no server event."""
    jsx = _render()
    assert "onClick:(e) => {" in jsx
    assert "navigator.clipboard.writeText(children)" in jsx
    # No backend event: the static export has no server to send one to.
    assert "addEvents" not in jsx


def test_copy_feedback_swaps_the_icon_and_announces():
    """A copy swaps the icon to a check and announces "Copied"."""
    jsx = _render()
    assert "jsx(LucideCopy" in jsx and "jsx(LucideCheck" in jsx
    assert "button.dataset.copied = 'true'" in jsx
    assert '"aria-live":"polite"' in jsx and 'role:"status"' in jsx
    assert "status.textContent = 'Copied'" in jsx


def test_post_markdown_renders_code_through_the_toolbar():
    """A post's fenced code compiles through the toolbar renderer."""
    (wrapper,) = _post_body("```python\nprint(1)\n```\n")
    (markdown,) = wrapper.children
    assert isinstance(markdown, Markdown)
    pre = str(markdown.format_component_map()["pre"])
    assert '"aria-label":"Copy code"' in pre
    assert "navigator.clipboard.writeText(children)" in pre
