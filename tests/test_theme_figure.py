"""The figure migration script handles Mermaid output and keeps its record honest.

``scripts/theme_figure.py`` moves an SVG onto the shared figure tokens
(ADR-0005). Mermaid renders need more than the hand-drawn figures did: the
root already has an id that its stylesheet selects on, colours arrive as
``rgb()``, ``hsl()`` and named colours in ``color`` and ``background``
properties as well as ``fill``, and the stylesheet carries ``@keyframes``.
``scripts/figure_maps.toml`` records the map each figure was migrated with, so
a Mermaid figure re-rendered from its ``.mmd`` can be migrated again.
"""

import importlib.util
import re
import tomllib
from pathlib import Path

import pytest

from alberto_codes_site.figures import ASSETS_DIR, FIGURE_TOKENS, uses_tokens

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "theme_figure", ROOT / "scripts" / "theme_figure.py"
)
theme_figure = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(theme_figure)

RECORD = tomllib.loads((ROOT / "scripts" / "figure_maps.toml").read_text())

# A trimmed Mermaid flowchart: root id and selectors, keyframes, rgba and hsl
# values, a named colour, inline label colours with !important, an HTML label
# inside foreignObject, and a marker referenced by url().
MERMAID = """<svg id="my-svg" width="100%" xmlns="http://www.w3.org/2000/svg" \
style="max-width: 200px; background-color: white;" viewBox="0 0 200 100">\
<style>#my-svg{font-family:arial;fill:#333;}\
@keyframes dash{to{stroke-dashoffset:0;}}\
#my-svg .edgePath .path{stroke:lightgrey;stroke-width:2px;}\
#my-svg .labelBkg{background-color:rgba(232, 232, 232, 0.5);}\
#my-svg .cluster rect{fill:hsl(60, 100%, 93.5%);stroke:#aaaa33;}\
#my-svg .good&gt;*{fill:#d4edda!important;stroke:#28a745!important;}</style>\
<g><marker id="my-svg_pointEnd"><path d="M 0 0 L 10 5 z"/></marker>\
<path d="M0,0L10,10" class="flowchart-link" marker-end="url(#my-svg_pointEnd)"/>\
<g class="node good" id="flowchart-A-0"><rect class="basic" x="1" y="2" width="50" \
height="20" style="fill:#d4edda !important;stroke:#28a745 !important"/>\
<foreignObject width="50" height="20"><div xmlns="http://www.w3.org/1999/xhtml" \
style="display: table-cell; color: rgb(51, 51, 51);"><span class="nodeLabel" \
style="color:#333 !important"><p>Accept <b>it</b> now</p></span></div>\
</foreignObject></g></g></svg>"""

MERMAID_MAP = {
    "#333333": "ink",
    "#d3d3d3": "muted",
    "#e8e8e8": "muted-soft",
    "#ffffde": "muted-soft",
    "#aaaa33": "grid",
    "#d4edda": "good-soft",
    "#28a745": "good",
    "background-color:#ffffff": "bg",
}


@pytest.fixture
def mermaid_svg(tmp_path: Path) -> Path:
    """Write the sample Mermaid render where the script expects a figure."""
    path = tmp_path / "sample-flow.svg"
    path.write_text(MERMAID)
    return path


def test_canonical_folds_every_colour_spelling():
    """Hex shorthand, names, rgb() and hsl() all reduce to one #rrggbb key."""
    assert theme_figure.canonical("#FFF") == "#ffffff"
    assert theme_figure.canonical("white") == "#ffffff"
    assert theme_figure.canonical("rgb(255, 255, 255)") == "#ffffff"
    assert theme_figure.canonical("rgba(30, 41, 59, 0.5)") == "#1e293b"
    assert theme_figure.canonical("hsl(0, 0%, 100%)") == "#ffffff"
    assert theme_figure.canonical("hsl(-160, 0%, 93.3333333333%)") == "#eeeeee"


def test_a_property_qualified_key_wins_for_that_property_only():
    """``color:#fff=ink`` beside ``#fff=bg`` maps text and fills apart."""
    mapping = theme_figure.parse_map(["#ffffff=bg", "color:white=ink"])
    out = theme_figure._recolour_decls("color:#fff;fill:#fff", mapping)
    assert out == "color:var(--fig-ink);fill:var(--fig-bg)"


def test_mermaid_render_migrates_with_its_own_root_and_selectors(mermaid_svg):
    """The root id becomes fig-<stem>, and nothing names a colour of its own."""
    mapping = theme_figure.parse_map([f"{k}={v}" for k, v in MERMAID_MAP.items()])
    new = theme_figure.migrate(mermaid_svg, mapping, card=True)
    root = re.search(r"<svg\b[^>]*>", new)[0]
    assert 'id="fig-sample-flow"' in root
    assert "my-svg" not in new.replace("sample-flow-my-svg", "")
    assert "@keyframes" not in new
    assert 'marker-end="url(#sample-flow-my-svg_pointEnd)"' in new
    assert 'id="sample-flow-flowchart-A-0"' in new
    css = re.findall(r"<style>(?!/\*)(.*?)</style>", new, re.S)[0]
    for selector in re.findall(r"([^{}]+)\{", css):
        for part in selector.split(","):
            assert part.strip().startswith("#fig-sample-flow")
    assert "fill:var(--fig-good-soft) !important" in new
    assert "color: var(--fig-ink)" in new
    assert "background-color: var(--fig-bg)" in new
    assert theme_figure._leftover_colours(new) == []
    # The card sits behind everything painted, right after the leading style.
    assert re.search(r"</style>\s*<rect x=\"0\" y=\"0\" width=\"100%\"", new)


def test_an_unmapped_colour_stops_the_script(mermaid_svg):
    """Leaving lightgrey out of the map is an error, not a silent leftover."""
    mapping = {k: v for k, v in MERMAID_MAP.items() if k != "#d3d3d3"}
    with pytest.raises(SystemExit, match="lightgrey"):
        theme_figure.migrate(
            mermaid_svg,
            theme_figure.parse_map([f"{k}={v}" for k, v in mapping.items()]),
            card=True,
        )


def test_a_moved_coordinate_or_changed_label_is_refused():
    """The tree comparison catches geometry and text, not only colour."""
    old = MERMAID
    for new in (
        MERMAID.replace('x="1" y="2"', 'x="1" y="3"'),
        MERMAID.replace("Accept <b>it</b> now", "Accept <b>it</b> later"),
    ):
        with pytest.raises(SystemExit):
            theme_figure._assert_same_geometry(old, new, "sample-flow")


def test_keyframes_in_use_are_not_dropped():
    """Mermaid's keyframes go only when no element uses an edge animation."""
    animated = MERMAID.replace('class="flowchart-link"', 'class="edge-animation-fast"')
    with pytest.raises(SystemExit, match="edge animation"):
        theme_figure._drop_unused_keyframes(animated)


def test_every_mermaid_figure_has_a_recorded_map():
    """A figure with a .mmd beside it can be migrated again after a re-render."""
    for mmd in sorted(ASSETS_DIR.glob("*.mmd")):
        name = mmd.with_suffix(".svg").name
        assert name in RECORD, f"{name} has no entry in scripts/figure_maps.toml"


@pytest.mark.parametrize("name", sorted(RECORD))
def test_recorded_maps_name_real_tokens_and_migrated_figures(name):
    """Every record names known tokens, and its figure is on the tokens."""
    for key, token in RECORD[name]["map"].items():
        assert token in FIGURE_TOKENS["light"], f"{name}: {key} -> {token}"
    assert uses_tokens((ASSETS_DIR / name).read_text())


@pytest.mark.parametrize(
    "name",
    sorted(p.name for p in ASSETS_DIR.glob("*.svg") if uses_tokens(p.read_text())),
)
def test_no_migrated_figure_keeps_an_rgb_hsl_or_named_colour(name):
    """The hex check misses rgb(), hsl() and names; this one does not."""
    text = (ASSETS_DIR / name).read_text()
    assert theme_figure._leftover_colours(text) == []
