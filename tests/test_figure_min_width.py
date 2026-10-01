"""A figure too small to read on a phone gets a minimum width and scrolls (#117).

``figure_min_width`` derives the width from the SVG itself: its ``viewBox``
width and its smallest ``font-size``. ADR-0005's 2026-10-01 (#117) amendment
records the rule; these tests pin the arithmetic and the two caps.
"""

import pytest

from alberto_codes_site.figures import (
    ASSETS_DIR,
    LABEL_MIN_PX,
    PHONE_COLUMN_PX,
    POST_COLUMN_PX,
    WIDE_FIGURE_CLASS,
    figure_min_width,
    inline_figure_html,
)


def _svg(width: float, *sizes: str) -> str:
    texts = "".join(f'<text font-size="{s}">x</text>' for s in sizes)
    return f'<svg viewBox="0 0 {width} 100">{texts}</svg>'


def test_min_width_holds_the_smallest_label_at_the_target_size():
    """840 wide with a 12px smallest label needs 840 * 11 / 12 = 770px."""
    assert figure_min_width(_svg(840, "14", "12", "15")) == 770


def test_css_font_sizes_count_too():
    """A size set in the figure's stylesheet counts like an attribute."""
    svg = '<svg viewBox="0 0 840 300"><style>.a { font-size: 12px; }</style></svg>'
    assert figure_min_width(svg) == 770


def test_mermaid_tooltip_rule_is_ignored():
    """The tooltip is never shown in a static figure, so its 12px is not a label."""
    svg = (
        '<svg viewBox="0 0 438 600"><style>'
        "#fig-x {font-size:16px;} #fig-x div.mermaidTooltip {font-size:12px;}"
        "</style></svg>"
    )
    # 438 * 11 / 16 = 301.1, under the phone column.
    assert figure_min_width(svg) is None


def test_a_figure_that_reads_on_the_phone_needs_nothing():
    """A figure whose labels already read in the phone column is left alone."""
    assert figure_min_width(_svg(PHONE_COLUMN_PX, str(LABEL_MIN_PX))) is None


def test_no_viewbox_or_no_font_size_needs_nothing():
    """Without a viewBox or a font size there is nothing to measure."""
    assert figure_min_width('<svg><text font-size="8">x</text></svg>') is None
    assert figure_min_width('<svg viewBox="0 0 2000 100"></svg>') is None


def test_capped_at_the_post_column_when_desktop_already_reads():
    """900 wide, 11px labels: 900px uncapped, but 10px holds at 880, so 880."""
    assert figure_min_width(_svg(900, "11")) == POST_COLUMN_PX


def test_not_capped_when_desktop_is_also_too_small():
    """980 wide, 10px labels: 9px at 880, so it keeps 1078 and scrolls there."""
    assert figure_min_width(_svg(980, "10")) == 1078


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("boto3-architecture-coverage.svg", 1582),
        ("saucier-mornay-procedure.svg", 1078),
        ("vramfit-16gib-budget.svg", 760),
        ("maker-checker-workflow.svg", None),
    ],
)
def test_real_figures(name, expected):
    """Spot-check the rule on figures the posts use."""
    assert figure_min_width((ASSETS_DIR / name).read_text()) == expected


def test_inlined_wide_figure_carries_its_width_and_class():
    """The inliner marks a wide figure and hands the page its width."""
    markup = inline_figure_html("saucier-cut-stream.svg", "alt")
    assert markup is not None
    assert f'class="post-figure {WIDE_FIGURE_CLASS}"' in markup
    assert 'style="--fig-min-width: 840px"' in markup


def test_inlined_narrow_figure_is_unchanged():
    """A figure that fits keeps the plain wrapper."""
    markup = inline_figure_html("receipt-chain.svg", "alt")
    assert markup is not None
    assert markup.startswith('<div class="post-figure" role="img"')
