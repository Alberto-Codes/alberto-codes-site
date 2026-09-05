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
eight fit. The scroll viewport now owns scrolling; the inner `pre` takes its
natural width. The dedicated 12 px bottom strip keeps the 4 px track clear of text.

Thumb/track colors use the site's gray tokens: light rgb(96, 100, 108) against
rgb(232, 232, 236), dark rgb(176, 180, 186) against rgb(39, 42, 45).
See [measurements.json](measurements.json) for exact computed colors and every
block's dimensions, including non-overflowing blocks.

At 390 × 844 (358 px code viewport), all 17 draft blocks overflow and have visible
4 px thumbs. No document-level horizontal overflow occurs. Gemma was checked
in light mode and Post 6 in dark mode at this size. An existing published post,
`2026-09-04-i-cut-the-last-sauce-off-the-file`, was also checked: all four blocks
fit at desktop width.

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

- Post 6: [before](before-post6.png), [light after](after-post6-light.png),
  [dark after](after-post6-dark.png).
- Gemma: [before](before-gemma.png), [light after](after-gemma-light.png),
  [dark after](after-gemma-dark.png).

The draft Post 6 illustration is absent from this baseline checkout; its image
placeholder in the screenshot is unrelated to the code rendering change.

## Repeat the measurement

Open a post in Chrome with `chrome-devtools-axi`, resize to the dimensions above,
and evaluate the function in [measure.js](measure.js). Capture before interacting
with any scrollbar. Toggle the navbar theme button and repeat. Check each row:
`whiteSpace` is `pre`; either `overflow` is zero or `visible` is true with nonzero
thumb dimensions. `pageOverflow` must be zero. Scroll an overflowing viewport
with the keyboard and verify its maximum offset is reachable.
