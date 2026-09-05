# Blog code scrollbars: browser validation

Chrome, 2026-09-05. Preview ran in the isolated implementation worktree on
3300/8300. Draft bodies were read unchanged from the two draft branches into
local fixtures outside `src/posts/`, then rendered through the production
`_render_post` function inside the same container/layout as `blog_post_page`.
Temporary fixture routes were removed before commit. No post or syndication
file was changed.

## Measurements for the PR body

At 1280 × 1000, the prose/code viewport is 880 px. Block numbers are one-based.

| Post | Block | Content width | Overflow before and after | After: thumb width × height |
| --- | ---: | ---: | ---: | ---: |
| Post 6 | 2 | 898 | 18 | 855 × 4 |
| Post 6 | 3 | 928 | 48 | 827 × 4 |
| Post 6 | 4 | 898 | 18 | 855 × 4 |
| Gemma | 3 | 1145 | 265 | 670 × 4 |
| Gemma | 7 | 978 | 98 | 785 × 4 |
| Gemma | 8 | 1095 | 215 | 701 × 4 |
| Gemma | 10 | 928 | 48 | 827 × 4 |
| Gemma | 11 | 978 | 98 | 785 × 4 |
| Gemma | 12 | 1115 | 235 | 688 × 4 |

Before: all blocks had `white-space: pre`, `overflow-x: auto`, and zero reserved
scrollbar height; overlay scrollbars were invisible. After: all 17 blocks retain
`white-space: pre`. The nine overflowing blocks have visible tracks and thumbs
at `scrollLeft = 0`, in both themes, without hovering or scrolling. The other
eight fit, and render no scrollbar element at all — the affordance appears
exactly where content is hidden. The scroll viewport now owns scrolling; the
inner `pre` takes its natural width.

The card is one box with one background. The scroll wrapper is transparent and
adds no padding, so the only painted background is the syntax theme's own on the
`pre`, clipped to the wrapper's 4 px radius. The 4 px track sits inside the
`pre`'s existing 16 px bottom padding — 4 px clear of the card edge and well
clear of text — so no extra bottom strip is needed.

Both claims are readable in the committed images. Scanning
[after-post6-light.png](after-post6-light.png) down x = 796 — a column with no
glyphs — through Post 6 card 2, which occupies y = 340–659:

    y 334–339   rgb(255, 255, 255)   page
    y 340–651   rgb(250, 250, 250)   card, one value, top edge downward
    y 652–655   rgb( 96, 100, 108)   thumb
    y 656–659   rgb(250, 250, 250)   card again — the 4 px clearance
    y 660–667   rgb(255, 255, 255)   page

One card colour from the top edge to the bottom edge, broken only by the thumb,
and exactly four card-coloured rows between the track and the card edge.
[after-post6-dark.png](after-post6-dark.png) gives the same rows with
rgb(40, 44, 52) and thumb rgb(176, 180, 186). The Vulkan pair repeats it on a
card at y = 200–352 with its track at y = 344–347.

The revision before this one painted the wrapper gray-3 and reserved a 12 px
strip, so the same kind of scan showed a second colour in the bottom 12 px of
every card — rgb(240, 240, 243) in light, rgb(33, 34, 37) in dark, against card
colours of rgb(250, 250, 250) and rgb(40, 44, 52). Those figures were read from
that revision's own committed screenshots and are kept under
`cardBackgroundColumn` in [measurements.json](measurements.json); the band is
gone from the images above.

Thumb/track colors use the site's gray tokens: light rgb(96, 100, 108) against
rgb(232, 232, 236), dark rgb(176, 180, 186) against rgb(39, 42, 45). Sampled over
an overflowing card, the thumb reads rgb(96, 100, 108) on rgb(250, 250, 250) in
light and rgb(176, 180, 186) on rgb(40, 44, 52) in dark, so the thumb — the part
that signals content is hidden — carries strong contrast in both. The track is
near-invisible in dark now that it sits on the code background rather than a
gray-3 strip; the thumb alone carries the affordance there.
See [measurements.json](measurements.json) for exact computed colors and every
block's dimensions, including non-overflowing blocks.

At 390 × 844 (358 px code viewport), all 17 draft blocks overflow and have visible
4 px thumbs. No document-level horizontal overflow occurs. Gemma was checked
in light mode and Post 6 in dark mode at this size. An existing published post,
`2026-09-04-i-cut-the-last-sauce-off-the-file`, was also checked: all four blocks
fit at desktop width and show no scrollbar.

Inline code has 0 px trailing padding throughout both drafts and the published
post. Following punctuation sits flush; ordinary prose retains its authored
whitespace. Browser range measurements found zero gap for same-line punctuation
(e.g. `v0.5.0`, `on the fire again`, `1 pint`, `2 oz.`). Visual inspection confirms
normal word separation. Syntax highlighting remains intact.

Interaction checks: focusing the second Post 6 viewport and pressing ArrowRight
moves it to `scrollLeft = 18`, its full range. The Vulkan download block reaches
`scrollLeft = 265`, its full range, including the complete tarball filename.

Ruff lint/format and ty checks passed for the changed Python module. This repo
has no pull-request CI; `deploy.yml` runs only on pushes to main. Pipeline and
Copilot review results are to be added during the Firstmate shipping handoff.

## Screenshots

Each after shot is captured at the same scroll offset as its before shot, so the
pair is directly comparable and every after shot contains at least one
overflowing card with a visible thumb. Offsets and the thumb rows read back out
of each PNG are recorded under `screenshotEvidence` in
[measurements.json](measurements.json). The pairs are pixel-aligned: scanning a
fixed column down each before/after pair returns the same card bands — Post 6
card 2 at y = 340–659 in both, Gemma's three cards at y = 170–249, 412–587 and
798–853 in both — with the only difference being the thumb rows the after shots
now contain.

- Post 6, `scrollY = 544`: [before](before-post6.png),
  [light after](after-post6-light.png), [dark after](after-post6-dark.png).
  Card 2, the `saucier show mornay` output that overflows by 18 px. In the before
  shot its `stirring` line runs into the right edge with no scrollbar; in the
  after shots the same card carries a thumb at y = 652–655.
- Gemma, `scrollY = 2726`: [before](before-gemma.png),
  [light after](after-gemma-light.png), [dark after](after-gemma-dark.png).
  Three cards in view — blocks 7 and 8 overflow by 98 px and 215 px and both gain
  thumbs, while block 9 (`nvidia-smi`) fits and correctly shows none, so the same
  image demonstrates both halves of `type="auto"`.
- Gemma Vulkan detail, `scrollY = 1565`:
  [light](after-gemma-vulkan-light.png), [dark](after-gemma-vulkan-dark.png).
  Block 3, the llama.cpp Vulkan download command — the worst overflow on the site
  at 265 px, and the case the brief singles out. `before-gemma.png` is not
  scrolled here, so this one has no before counterpart.

The draft Post 6 illustration is absent from this baseline checkout; its image
placeholder in the screenshot is unrelated to the code rendering change.

## Repeat the measurement

Open a post in Chrome with `chrome-devtools-axi`, resize to the dimensions above,
and evaluate the function in [measure.js](measure.js). Capture before interacting
with any scrollbar. Switch themes with the navbar toggle button and repeat —
forcing the `dark` class onto `.radix-themes` is not equivalent, because the
syntax highlighter picks its theme from Reflex's colour-mode state rather than
from CSS, so the code cards stay light while the page turns dark. Check each row:
`whiteSpace` is `pre`; and `visible` is true with nonzero thumb dimensions if and
only if `overflow` is nonzero — a row with `overflow` zero must report
`trackHeight` zero, because no scrollbar element is rendered for it.
`pageOverflow` must be zero. Scroll an overflowing viewport with the keyboard and
verify its maximum offset is reachable. Finally, scan a glyph-free pixel column
through a card in a screenshot and confirm it holds one rgb value from the first
code line to the card's bottom edge.
