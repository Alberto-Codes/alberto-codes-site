# ADR-0005: Theme-Aware Post Figures

## Status

Accepted

## Date

2026-10-01

## Context

Post figures are SVG files in `src/assets/`, embedded with markdown image
syntax (`![alt](/name.svg)`) and rendered by `rx.markdown` as `<img>`
(ADR-0003). None of the 51 responds to the site's theme:

- The older figures are transparent with pale fills and text (`#cbd5e1`,
  `#94a3b8`). They were drawn for a dark page and nearly vanish on the light
  theme.
- The typevet and Jev figures hard-code a dark card (`#1f2020`, text
  `#cccccc`, green `#7fb069`). On the light theme they read as a black slab.

The site has a manual light/dark toggle (`rx.color_mode.button` in the
navbar) that defaults to the system preference. Reflex's theme provider
(`.web/utils/react-theme.js`) puts the resolved mode on `<html>` as the class
`light` or `dark`, and Radix mirrors it on its root theme element. A reader
can therefore run the site in dark mode on a light OS, or the reverse.

The constraint that decides this: **an SVG loaded through `<img>` is a
separate document.** It cannot see the page's classes or its CSS custom
properties. A `prefers-color-scheme` query inside it answers for the OS, not
for the site's toggle.

Issue #68 asks for one style that works in both themes, without changing a
number, label or coordinate that encodes data, and without rasterising.

## Options considered

### (a) Inline token-carrying SVGs into the post HTML at render time

The renderer reads the SVG file in Python and emits its markup in place of
the `<img>`. Fills and strokes reference CSS custom properties
(`var(--fig-ink)` and so on) that the page sets per theme, keyed off the
`.dark` class.

- Follows the manual toggle exactly, because the figure is in the page's
  document.
- Server-rendered: the markup is a plain string handed to `rx.html`, so the
  static export (`reflex export`) writes the figure into each post's HTML.
  Verified in `.web/build/client/blog/<slug>/index.html`.
- Cost: figure bytes move from cacheable image requests into the page HTML
  (the largest pilot, the receipt photo figure, is 16 KB). Inlined figures
  share one document, so ids and `<style>` rules can collide; each migrated
  figure prefixes its ids with its file stem and scopes its own rules under a
  root id `fig-<stem>`. Each SVG must be readable at render time from
  `src/assets/`.
- Cost: `rx.markdown`'s `component_map` cannot do this. Its lambdas compile to
  JavaScript and receive the image `src` at runtime in the browser, not in
  Python, so they cannot read the file. Inlining therefore happens before
  markdown: the body is split at figure lines into markdown runs and figures,
  each rendered by its own component (see Decision). Checked against current
  Reflex docs (`rx.html` renders raw HTML through `dangerouslySetInnerHTML`;
  `component_map` maps elements to components).

### (b) `prefers-color-scheme` inside each SVG

Each SVG carries a `<style>` with light values and a dark media query.

- No renderer change; works when the SVG is opened on its own.
- Follows the OS, not the site toggle. A reader who picks dark on a light OS
  gets light figures on a dark page, which is the defect in a new place.
- Rejected as the mechanism. Kept as the standalone fallback (see Decision).

### (c) One neutral card that reads on both themes

Give every figure an opaque mid-tone card with its own ink.

- No renderer change, no toggle dependency.
- Always looks foreign on one of the two themes, and a card light enough to
  sit on white is a glare panel on the dark page. It is a compromise in both
  themes rather than a fit in either.
- Rejected.

## Decision

**Option (a), with option (b) as the standalone fallback.**

### Tokens

One set of figure colour tokens, defined once in
`src/alberto_codes_site/figures.py` (`FIGURE_TOKENS`):

| Token | Role | Light | Dark | Contrast vs `bg` (light / dark) |
|---|---|---|---|---|
| `bg` | figure card | `#f6f8fa` | `#1f2020` | — |
| `ink` | primary text | `#1f2328` | `#cccccc` | 14.84 / 10.17 |
| `muted` | secondary text, axes | `#59636e` | `#8f8f8f` | 5.74 / 5.05 |
| `grid` | grid lines, borders (non-text) | `#818b98` | `#707070` | 3.24 / 3.30 |
| `accent-1` | first series (blue) | `#0969da` | `#6cb6ff` | 4.88 / 7.60 |
| `accent-2` | second series (warm) | `#a85200` | `#d9894a` | 5.09 / 5.93 |
| `good` | semantic right / after | `#1a7f37` | `#7fb069` | 4.77 / 6.47 |
| `bad` | semantic wrong | `#cf222e` | `#e07a5f` | 5.03 / 5.54 |
| `accent-3` | third series (violet), added 2026-10-01 | `#8250df` | `#b083f0` | 4.74 / 5.72 |
| `*-soft` | tinted fills that carry text (`accent-1`, `accent-2`, `accent-3`, `good`, `bad`, `muted`) | pale tints | dark tints | `ink` on each: ≥ 13.07 / ≥ 7.22 |

Text-bearing tokens meet WCAG AA for text (4.5:1) against `bg` in each theme;
`grid` meets AA for non-text graphics (3:1). Only `ink` may sit on a soft
fill. `tests/test_figure_tokens.py` computes every ratio from the WCAG 2.x
luminance formula and fails if any drops below its threshold. The dark values
keep the typevet and Jev figures' existing look.

### Figure format

A migrated SVG carries, verbatim, the token block that
`figures.token_style_block()` generates. That block declares the tokens on
`svg:root` with a `prefers-color-scheme: dark` override. `svg:root` matches
only when the SVG is its own document (opened directly, or loaded as
`<img>` by a syndication copy or feed reader), so the figure still renders
correctly there, following the OS. Inlined in a post, it matches nothing, and
the values the page sets on `.post-figure` (light) and `.dark .post-figure`
(dark) take over.

Every colour in the figure is `var(--fig-<token>)`, in a `style` attribute
or in the figure's own `<style>` block, whose rules are scoped under
`#fig-<stem>`. A figure that was transparent gets a full-size `bg` card
rect, so its contrast is measured against a known background rather than
whichever page it lands on.

### Renderer

`figures.split_figures()` walks the post body and lifts out an image line
when all three hold: it references an `.svg` that carries the token block, it
stands alone as a paragraph, and it is outside a fenced code block. Each one
becomes
`<div class="post-figure" role="img" aria-label="<alt>">…svg…</div>`,
rendered with `rx.html`. The markdown runs between them are rendered with
`rx.markdown` as before. Posts have no footnotes or reference-style link
definitions, which are the only markdown constructs that would break across a
split. Any image that does not qualify stays in the markdown and renders as
`<img>`, unchanged. Migration is therefore one file at a time, and **post
bodies do not change**: the `![alt](/name.svg)` syntax is kept, and the alt
text becomes the inlined figure's accessible name.

### Migration

`scripts/theme_figure.py` rewrites one SVG from a colour→token map. It
prefixes ids, scopes the figure's `<style>`, adds the token block, and
optionally adds the card. Before writing, it compares the old and new element
trees and stops if anything other than colour, ids, the added style and the
card changed. `--sync` rewrites the token block in every migrated figure after
the values change.

`tests/test_figure_tokens.py` fails for any SVG a post references that
neither carries the token block nor appears in its `NOT_YET_MIGRATED`
allowlist. The allowlist is the visible to-do list. It fails as well when a
migrated or unreferenced file is still listed. The pilot migrated the three
typevet figures, the six Jev figures and the three figures of the 2026-09-02
Gemma 4 post. The rest are tracked in a child issue of #68.

## Consequences

### Positive

- Figures follow the site toggle, not only the OS, and stay correct when
  opened on their own.
- One source of colour values; contrast is computed, not eyeballed.
- Server-rendered HTML carries the figures, so they need no JavaScript to
  appear.
- Data geometry is protected by the migration script's tree comparison.

### Negative

- Inlined figures add their bytes to each post's HTML and are not cached
  separately.
- Two mechanisms coexist until the allowlist is empty: migrated figures
  inline, the rest still load as `<img>`.
- Mermaid-generated figures (those with a `.mmd` beside them) embed
  Mermaid's own `<style>` with nested selectors. Re-rendering from `.mmd`
  overwrites a migrated file, so those need a Mermaid theme that emits the
  tokens, or a re-run of the script after every render.
- A figure placed inside a paragraph, list or blockquote is not inlined.
  It renders as `<img>` and follows the OS rather than the toggle. Keep
  figures on their own line.

## Amendment 2026-10-01: the remaining 39 figures, and Mermaid

Issue #91 migrated the 39 figures left in `NOT_YET_MIGRATED`; the list is
empty. 23 of them are Mermaid renders (18 with a `.mmd` beside them, 5
without), 16 are hand-drawn.

**A third series token.** Six figures, four of them in the turboquant set,
use a violet node class as a category distinct from blue and amber, and
`vramfit-recipe-shapes` draws its 4-bit bars violet beside blue 8-bit bars.
Folding violet into an existing accent would merge two categories, so
`accent-3` and `accent-3-soft` were added. They sit in `TEXT_TOKENS` and
`SOFT_TOKENS`, so the contrast tests cover them like every other token.

**Mermaid route: the script, not `themeVariables`.** Mermaid derives many
colours from its theme variables (darkening, lightening, alpha), which fails
on `var()` strings, and a fresh render could move layout and break the
geometry comparison. `scripts/theme_figure.py` was extended instead, with
tests in `tests/test_theme_figure.py`:

- A root that already has an id (Mermaid's `my-svg`) is renamed to
  `fig-<stem>`; selectors written against it are rewritten rather than
  nested, and other id selectors in the stylesheet follow their renamed ids.
- Colours are normalised to `#rrggbb` before lookup, so `rgb()`, `rgba()`,
  `hsl()`, `white`, `black` and `lightgrey` are mapped like hex; an alpha is
  dropped because the token replaces the tint. Colour properties beyond
  `fill` and `stroke` are mapped too: `color`, `background`, `border`,
  `flood-color`. Any other named colour stops the script.
- A map key may be qualified by property (`fill:#3b82f6=accent-1-soft` beside
  `#3b82f6=accent-1`), because Mermaid reuses one colour as a fill in one node
  and a border in another.
- Mermaid's `@keyframes` are dropped: only edge-animation classes use them, and
  the script stops if any element carries one.
- The card goes behind everything painted, at the viewBox origin, because a
  sequence diagram draws before its `<style>` and starts at negative
  coordinates.
- The tree comparison now also compares text between elements, so a label in
  an HTML `foreignObject` cannot change.

Each figure's map is recorded in `scripts/figure_maps.toml`. **A re-render
from a `.mmd` overwrites the migrated SVG with Mermaid's own colours**, so
after every re-render run
`uv run python scripts/theme_figure.py src/assets/NAME.svg --recorded`. If the
render introduces a colour the record lacks, the script stops and names it;
add it to the record by role. A test fails if any `.mmd` lacks a record.

**Role choices worth knowing.** Saturated Mermaid fills became the soft tint of
their series and their borders the series colour. Where a figure also had pale
fills of the same hue (boto3, adk, docstring), the pale fills became the card,
outlined in the series colour, so tinted-versus-outlined keeps the
strong-versus-pale distinction. The saucier figures map their orange to
`accent-2`, as the Jev pilot did, since their text calls it orange. Inlined
Mermaid figures render at their own `max-width` instead of being stretched to
the column as `<img>` did, and the page now centres them.

## References

- [ADR-0003: Blog Infrastructure and Rendering](0003-blog-infrastructure.md)
- Issue #68, epic #66
- [WCAG 2.2 contrast (minimum), 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) and [non-text contrast, 1.4.11](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html)
