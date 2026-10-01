"""Post figures follow the site theme through one shared set of colour tokens.

ADR-0005 records why: a figure loaded through ``<img>`` cannot see the site's
light/dark toggle, so a figure carrying the token block is inlined at render
time and takes its colours from CSS custom properties the page sets per theme.

These checks hold the line while the migration is partway done. Every SVG a
post references either carries the token block or sits in
``NOT_YET_MIGRATED``, which is the visible to-do list. Migrating a figure
means running ``scripts/theme_figure.py`` on it and deleting its line here.
"""

import re

import pytest

from alberto_codes_site.figures import (
    ASSETS_DIR,
    FIGURE_TOKENS,
    GRAPHIC_TOKENS,
    SOFT_TOKENS,
    TEXT_TOKENS,
    figure_page_style,
    split_figures,
    token_style_block,
    uses_tokens,
)
from alberto_codes_site.pages.blog import POSTS_DIR

# Figures still on hard-coded colours. Shrink this list; never grow it: a new
# figure is drawn on the tokens from the start.
NOT_YET_MIGRATED = {
    "adk-session-data-flow.svg",
    "bidirectional-verification.svg",
    "blocking-comparison.svg",
    "boto3-architecture-coverage.svg",
    "boto3-event-system.svg",
    "deterministic-vs-probabilistic.svg",
    "docstring-quality-layers.svg",
    "evolution-loop.svg",
    "lineage-flow.svg",
    "maker-checker-workflow.svg",
    "param-drift-lifecycle.svg",
    "receipt-chain.svg",
    "redelivery-lifecycle.svg",
    "saucier-aurore-ambiguity.svg",
    "saucier-cut-stream.svg",
    "saucier-derived-waterfall.svg",
    "saucier-espaqnole-mother.svg",
    "saucier-mornay-procedure.svg",
    "saucier-one-record.svg",
    "saucier-perigueux-page-break.svg",
    "saucier-stated-chain-line-1437.svg",
    "saucier-two-books-one-reader.svg",
    "saucier-unstated-chain-resolved.svg",
    "saucier-unstated-chain.svg",
    "saucier-veto-gate.svg",
    "turboquant-bit-budget.svg",
    "turboquant-container-architecture.svg",
    "turboquant-fused-kernel-flow.svg",
    "turboquant-kv-compression.svg",
    "turboquant-model-portability.svg",
    "turboquant-vllm-architecture.svg",
    "vramfit-16gib-budget.svg",
    "vramfit-16gib-recipe.svg",
    "vramfit-budget.svg",
    "vramfit-distribution-shoulders.svg",
    "vramfit-label-vs-file.svg",
    "vramfit-pipeline.svg",
    "vramfit-recipe-shapes.svg",
    "vramfit-three-ceilings.svg",
}

AA_TEXT = 4.5
AA_GRAPHIC = 3.0
HEX = re.compile(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b")


def _luminance(colour: str) -> float:
    """WCAG 2.x relative luminance of a #rrggbb colour."""
    channels = [int(colour[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [
        c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(a: str, b: str) -> float:
    """WCAG 2.x contrast ratio between two #rrggbb colours."""
    hi, lo = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def _referenced_svgs() -> set[str]:
    names: set[str] = set()
    for post in POSTS_DIR.glob("*.md"):
        names.update(re.findall(r"\]\(/([\w.-]+\.svg)\)", post.read_text()))
    return names


def _migrated() -> list[str]:
    return sorted(_referenced_svgs() - NOT_YET_MIGRATED)


def test_both_themes_define_the_same_tokens():
    """Light and dark carry the same token names, and every token has a role."""
    assert FIGURE_TOKENS["light"].keys() == FIGURE_TOKENS["dark"].keys()
    roles = set(TEXT_TOKENS) | set(GRAPHIC_TOKENS) | set(SOFT_TOKENS) | {"bg"}
    assert roles == set(FIGURE_TOKENS["light"])


@pytest.mark.parametrize("mode", ["light", "dark"])
@pytest.mark.parametrize("token", TEXT_TOKENS)
def test_text_tokens_meet_aa_against_the_figure_background(mode, token):
    """Text-bearing tokens hold 4.5:1 against the figure background."""
    tokens = FIGURE_TOKENS[mode]
    assert contrast(tokens[token], tokens["bg"]) >= AA_TEXT


@pytest.mark.parametrize("mode", ["light", "dark"])
@pytest.mark.parametrize("token", GRAPHIC_TOKENS)
def test_graphic_tokens_meet_aa_against_the_figure_background(mode, token):
    """Non-text graphics such as grid lines hold 3:1."""
    tokens = FIGURE_TOKENS[mode]
    assert contrast(tokens[token], tokens["bg"]) >= AA_GRAPHIC


@pytest.mark.parametrize("mode", ["light", "dark"])
@pytest.mark.parametrize("soft", SOFT_TOKENS)
def test_ink_meets_aa_on_every_soft_fill(mode, soft):
    """Ink is the only text allowed on a soft fill, and it holds 4.5:1 there."""
    tokens = FIGURE_TOKENS[mode]
    assert contrast(tokens["ink"], tokens[soft]) >= AA_TEXT


def test_page_style_sets_the_same_values_as_the_svg_block():
    """The page and the standalone SVG block read from one source of values."""
    style = figure_page_style()
    for mode, selector in (
        ("light", "& .post-figure"),
        ("dark", ".dark & .post-figure"),
    ):
        for token, value in FIGURE_TOKENS[mode].items():
            assert style[selector][f"--fig-{token}"] == value
            assert f"--fig-{token}: {value};" in token_style_block()


def test_every_referenced_svg_uses_the_tokens_or_is_listed():
    """A figure a post uses is on the tokens, or is on the visible to-do list."""
    offenders = sorted(
        name
        for name in _referenced_svgs() - NOT_YET_MIGRATED
        if not uses_tokens((ASSETS_DIR / name).read_text())
    )
    assert offenders == [], f"not on the figure tokens and not allowlisted: {offenders}"


def test_allowlist_holds_only_unmigrated_referenced_figures():
    """A migrated or unused figure leaves the to-do list."""
    referenced = _referenced_svgs()
    stale = sorted(
        name
        for name in NOT_YET_MIGRATED
        if name not in referenced or uses_tokens((ASSETS_DIR / name).read_text())
    )
    assert stale == [], f"remove these from NOT_YET_MIGRATED: {stale}"


@pytest.mark.parametrize("name", _migrated())
def test_migrated_figure_has_no_hard_coded_colour(name):
    """Outside the token block, a migrated figure names no colour of its own."""
    text = (ASSETS_DIR / name).read_text().replace(token_style_block(), "")
    text = re.sub(r"data:[^\"']+", "", text)
    text = re.sub(r"&#x?[0-9a-fA-F]+;", "", text)
    assert HEX.findall(text) == []


@pytest.mark.parametrize("name", _migrated())
def test_migrated_figure_ids_cannot_collide_once_inlined(name):
    """Inlined figures share one document, so every id carries the file stem."""
    stem = name.removesuffix(".svg")
    text = (ASSETS_DIR / name).read_text()
    ids = re.findall(r'\sid="([^"]+)"', text)
    assert ids[0] == f"fig-{stem}"
    assert all(i.startswith(f"{stem}-") for i in ids[1:])
    rules = re.findall(r"<style>(?!/\*)(.*?)</style>", text, re.S)
    for css in rules:
        for selector in re.findall(r"([^{}]+)\{", css):
            for part in selector.split(","):
                assert part.strip().startswith(f"#fig-{stem}"), part


def test_split_inlines_migrated_figures_and_leaves_the_rest_as_markdown():
    """Only migrated figures on their own paragraph, outside code, are inlined."""
    migrated, unmigrated = _migrated()[0], sorted(NOT_YET_MIGRATED)[0]
    body = (
        "Intro.\n\n"
        f"![A migrated figure](/{migrated})\n\n"
        f"![An old figure](/{unmigrated})\n\n"
        "```\n"
        f"![In a code block](/{migrated})\n"
        "```\n"
    )
    segments = split_figures(body)
    kinds = [kind for kind, _ in segments]
    assert kinds == ["markdown", "figure", "markdown"]
    figure = segments[1][1]
    assert 'role="img" aria-label="A migrated figure"' in figure
    assert unmigrated in segments[2][1]
    assert f"/{migrated})" in segments[2][1]


def test_a_figure_inside_a_paragraph_is_not_lifted_out():
    """An image sharing a paragraph with text stays in the markdown."""
    name = _migrated()[0]
    body = f"Text on the line above\n![A figure](/{name})\n"
    assert split_figures(body) == [("markdown", body)]
