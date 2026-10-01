"""Light-mode code token colours meet WCAG AA on the code block background.

Issue #110. Light mode keeps react-syntax-highlighter's oneLight theme and
overrides only the token colours that failed 4.5:1 on its #fafafa block
background; dark mode keeps oneDark untouched. ``ONE_LIGHT`` records oneLight's
own colours (react-syntax-highlighter 16.1.0) for every token class the
highlighter styles by name, so these checks cover the whole light palette, not
only the tokens Lighthouse flagged on a few posts.
"""

import colorsys

import pytest
from reflex.vars import Var
from test_figure_tokens import AA_TEXT, contrast

from alberto_codes_site.pages.blog import (
    LIGHT_CODE_BACKGROUND,
    LIGHT_CODE_TOKEN_COLOURS,
    _code_block,
)

# oneLight token colours as (hue, saturation %, lightness %).
_BASE = (230, 8, 24)
_COMMENT = (230, 4, 64)
_ORANGE = (35, 99, 36)
_KEYWORD = (301, 63, 40)
_RED = (5, 74, 59)
_GREEN = (119, 34, 47)
_BLUE = (221, 87, 60)
_CYAN = (198, 99, 37)
ONE_LIGHT = {
    "plain": _BASE,
    "doctype": _BASE,
    "punctuation": _BASE,
    "entity": _BASE,
    "keyword": _KEYWORD,
    **dict.fromkeys(("comment", "prolog", "cdata"), _COMMENT),
    **dict.fromkeys(
        ("attr-name", "class-name", "boolean", "constant", "number", "atrule"),
        _ORANGE,
    ),
    **dict.fromkeys(("property", "tag", "symbol", "deleted", "important"), _RED),
    **dict.fromkeys(
        ("selector", "string", "char", "builtin", "inserted", "regex", "attr-value"),
        _GREEN,
    ),
    **dict.fromkeys(("variable", "operator", "function"), _BLUE),
    "url": _CYAN,
}


def _hex(hsl: tuple[int, int, int]) -> str:
    """Return the #rrggbb a browser renders for ``hsl(h, s%, l%)``."""
    h, s, lightness = hsl
    rgb = colorsys.hls_to_rgb(h / 360, lightness / 100, s / 100)
    return "#" + "".join(f"{round(c * 255):02x}" for c in rgb)


def _hue_saturation(colour: str) -> tuple[float, float]:
    """Hue in degrees and saturation in percent of a #rrggbb colour."""
    r, g, b = (int(colour[i : i + 2], 16) / 255 for i in (1, 3, 5))
    h, _, s = colorsys.rgb_to_hls(r, g, b)
    return h * 360, s * 100


def _rendered(token: str) -> str:
    """The colour a token renders in light mode: override, else oneLight's."""
    return LIGHT_CODE_TOKEN_COLOURS.get(token, _hex(ONE_LIGHT[token]))


def test_background_is_one_lights_own():
    """The overrides were sized against the background oneLight paints."""
    assert _hex((230, 1, 98)) == LIGHT_CODE_BACKGROUND


@pytest.mark.parametrize("token", sorted(ONE_LIGHT))
def test_every_light_token_meets_aa(token):
    """Every token class oneLight colours reads at 4.5:1 or better."""
    ratio = contrast(_rendered(token), LIGHT_CODE_BACKGROUND)
    assert ratio >= AA_TEXT, f"{token} {_rendered(token)}: {ratio:.2f}"


@pytest.mark.parametrize("token", sorted(LIGHT_CODE_TOKEN_COLOURS))
def test_overrides_only_replace_failing_colours(token):
    """An override exists only where oneLight's own colour failed."""
    original = _hex(ONE_LIGHT[token])
    assert contrast(original, LIGHT_CODE_BACKGROUND) < AA_TEXT


@pytest.mark.parametrize("token", sorted(LIGHT_CODE_TOKEN_COLOURS))
def test_overrides_keep_the_hue(token):
    """An override is oneLight's colour, darker, not a different colour.

    Both sides are compared as rendered 8-bit colours, so the tolerance
    absorbs rounding, which moves the hue of the near-grey comment most.
    """
    hue, saturation = _hue_saturation(LIGHT_CODE_TOKEN_COLOURS[token])
    want_hue, want_saturation = _hue_saturation(_hex(ONE_LIGHT[token]))
    assert abs((hue - want_hue + 180) % 360 - 180) <= 2.5
    assert abs(saturation - want_saturation) <= 2.5


def test_code_block_switches_between_patched_light_and_stock_dark():
    """Light mode merges the overrides into oneLight; dark mode is oneDark."""
    jsx = str(_code_block(Var(_js_expr="children", _var_type=str)))
    style = jsx[jsx.index("style:((resolvedColorMode") :]
    style = style[: style.index(",wrapLongLines")]
    light, dark = style.rsplit(" : ", 1)
    assert "...oneLight" in light
    for colour in set(LIGHT_CODE_TOKEN_COLOURS.values()):
        assert colour in light
    assert dark == "oneDark)"
