---
name: Alberto.Codes
description: A working reference book of measured results, bound in bottle-green cloth.
colors:
  cloth: "#1f4a2b"
  cloth-ink: "#f4f8f5"
  cloth-ink-muted: "#cfdcd2"
  cloth-mark: "#94ce9a"
  cloth-rule: "rgba(244, 248, 245, 0.32)"
  cloth-hover: "rgba(244, 248, 245, 0.1)"
  link-ink: "#2a7e3b"
  focus-ring: "#2a7e3b"
  ground: "#f7f9f8"
  ink: "#1a211e"
  ink-muted: "#5f6563"
  separator-dot: "#868e8b"
  rule-hairline: "#b8bcba"
  rule-year: "#cbcfcd"
  rule-soft: "#d7dad9"
  code-border: "#dfe2e0"
  code-surface: "#eef1f0"
typography:
  display:
    fontFamily: "Besley, Besley Fallback Georgia, Besley Fallback Noto, Besley Fallback Times, Georgia, serif"
    fontSize: "35px"
    fontWeight: 700
    lineHeight: "40px"
    letterSpacing: "-0.01em"
  headline:
    fontFamily: "Besley, Besley Fallback Georgia, Besley Fallback Noto, Besley Fallback Times, Georgia, serif"
    fontSize: "1.5rem"
    fontWeight: 700
    lineHeight: 1.25
    letterSpacing: "-0.005em"
  subhead:
    fontFamily: "Besley, Besley Fallback Georgia, Besley Fallback Noto, Besley Fallback Times, Georgia, serif"
    fontSize: "1.25rem"
    fontWeight: 700
    lineHeight: 1.25
    letterSpacing: "-0.005em"
  year:
    fontFamily: "Besley, Besley Fallback Georgia, Besley Fallback Noto, Besley Fallback Times, Georgia, serif"
    fontSize: "20px"
    fontWeight: 700
    lineHeight: "26px"
    fontFeature: "lnum"
  wordmark:
    fontFamily: "Besley, Besley Fallback Georgia, Besley Fallback Noto, Besley Fallback Times, Georgia, serif"
    fontSize: "20px"
    fontWeight: 700
    lineHeight: "26px"
  title:
    fontFamily: "Besley, Besley Fallback Georgia, Besley Fallback Noto, Besley Fallback Times, Georgia, serif"
    fontSize: "1.125rem"
    fontWeight: 600
    lineHeight: 1.3
    letterSpacing: "0"
  body:
    fontFamily: "-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, system-ui, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 400
  summary:
    fontFamily: "-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, system-ui, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 400
    lineHeight: 1.55
  meta:
    fontFamily: "-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: "20px"
    fontFeature: "tnum"
  mark:
    fontFamily: "-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, system-ui, sans-serif"
    fontSize: "12px"
    fontWeight: 600
    lineHeight: "16px"
    letterSpacing: "0.05em"
    fontFeature: "c2sc, smcp"
  nav:
    fontFamily: "-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 500
    lineHeight: "20px"
rounded:
  focus: "3px"
  control: "4px"
  table: "0px"
spacing:
  space-1: "4px"
  space-2: "8px"
  space-4: "16px"
  space-5: "24px"
  space-6: "32px"
  heading-above: "2em"
  heading-below: "0.5em"
components:
  masthead:
    backgroundColor: "{colors.cloth}"
    textColor: "{colors.cloth-ink}"
    typography: "{typography.wordmark}"
    padding: "16px 32px"
  nav-link:
    textColor: "{colors.cloth-ink-muted}"
    typography: "{typography.nav}"
    padding: "0.25em 0"
  nav-link-hover:
    textColor: "{colors.cloth-ink}"
  nav-link-current:
    textColor: "{colors.cloth-ink}"
  cloth-button:
    backgroundColor: "transparent"
    textColor: "{colors.cloth-ink}"
    rounded: "{rounded.control}"
  cloth-button-hover:
    backgroundColor: "{colors.cloth-hover}"
  footer:
    backgroundColor: "{colors.cloth}"
    textColor: "{colors.cloth-ink}"
    padding: "32px 32px"
  index-entry:
    textColor: "{colors.ink}"
    typography: "{typography.title}"
    padding: "0.3em 0"
  index-entry-hover:
    textColor: "{colors.link-ink}"
  type-mark:
    textColor: "{colors.ink-muted}"
    typography: "{typography.mark}"
  link:
    textColor: "{colors.link-ink}"
  code-block:
    backgroundColor: "{colors.code-surface}"
    textColor: "{colors.ink-muted}"
    rounded: "{rounded.control}"
  proportion-table:
    textColor: "{colors.ink}"
    typography: "{typography.meta}"
    rounded: "{rounded.table}"
    padding: "0.75em 1em"
---

# Design System: Alberto.Codes

## Overview

**Creative North Star: "The Clothbound Trade Reference"**

The site reads as an early-1900s trade reference: a bottle-green cloth binding at the top and bottom of every page, a cool green-gray paper between, a Clarendon for the things a reader looks up, and a plain sans for the reading itself. Posts are entries in an index, not cards in a feed; data is set as printed tables of proportions. The frame is there to be found and then forgotten.

Density is a reference book's: tight index rows, a 48em page column, a 40rem reading measure inside an 880px post column that tables, figures and code are allowed to fill. Colour is spent sparingly. One green ink marks what can be followed and where the reader stands; everything else is graphite on paper. The cloth is identical in light and dark themes, so the binding never changes while the paper does.

Motion is a single gesture: an index row's dotted leader closes into a solid rule. Nothing else on the site animates beyond the table of contents' disclosure caret.

**Key Characteristics:**
- A fixed bottle-green cloth band for masthead and footer in both themes.
- A green-tinted neutral ground (Radix sage), never cream, never pure white.
- Besley, a self-hosted variable Clarendon, for wordmark, titles, section headings and index entries; system sans for everything read at length.
- One accent ink (Radix grass step 11) for links, hover and the current page.
- Kinds are set as small-cap marks, never as coloured badges or chips.
- Tables ruled like printed proportions: heavy rule above and below, hairline under the head, no verticals, no fills, tabular figures.

## Colors

A green-bound book: a deep cloth, a cool sage paper, graphite ink, and one living green for what can be followed.

Colour values in the frontmatter are the light-theme resolutions. In source they are written as Radix steps (`var(--accent-N)`, `var(--gray-N)`, `rx.color(...)`) on the theme `accent_color="grass"`, `gray_color="sage"` (`alberto_codes_site.py`), so the dark theme swaps each step for its dark counterpart; the six cloth properties are literal custom properties in `src/assets/identity.css` and do not change between themes.

### Primary
- **Bottle-Green Cloth** (`--cloth`, identity.css): the masthead and footer field. Sits between grass 11 and grass 12 of the light scale. Used for nothing else.
- **Cloth Ink** (`--cloth-ink`): wordmark, current nav entry, footer text and icons on the cloth (about 9:1).
- **Cloth Ink, Muted** (`--cloth-ink-muted`): nav entries at rest (about 7:1).
- **Cloth Mark** (`--cloth-mark`, equal to light grass 7): the underline beneath the current page and focus rings on the cloth (about 5:1).
- **Cloth Rule** and **Cloth Hover** (`--cloth-rule`, `--cloth-hover`): the 1px inset outline of buttons on the cloth, and their hover wash.

### Secondary
- **Grass Link Ink** (`var(--accent-11)`, grass 11; dark theme resolves to grass 11 dark): every link, the hovered index entry, the leader's closed rule, the RSS link, the copy confirmation, the text caret. Clears 4.5:1 on the ground in both themes.
- **Grass Focus Ring** (`var(--accent-11)`): 2px focus outlines on the ground.
- **Selection** (`var(--accent-a5)`): text selection wash, keeping the text's own colour.

### Neutral
- **Sage Paper** (`var(--gray-2)` as `--color-background`, light theme only; dark keeps Radix's dark background): the page ground.
- **Graphite Ink** (`var(--gray-12)`): titles, index entries at rest, the heavy table rules, inline code text.
- **Muted Graphite** (`var(--gray-11)`): summaries, dates, marks, datelines, captions, secondary text.
- **Separator Dot** (`var(--gray-9)`): the middots between items in a run.
- **Hairline** (`var(--gray-8)`): the index leader's dots, the table head's hairline, blockquote rule, scrollbar thumb on the page.
- **Year Rule** (`var(--gray-7)`): the rule under each year heading.
- **Soft Rule** (`var(--gray-6)`): the rules closing the series box and the table of contents.
- **Code Border** and **Code Surface** (`var(--gray-5)`, `var(--gray-3)`): code block frame and its header strip; inline code sits on `var(--gray-a3)`.

### Named Rules
**The One Ink Rule.** The accent green marks only what can be followed (links) and where the reader stands (hover, current page, focus). Inline code, kinds, dates and decoration never take it.

**The Fixed Binding Rule.** The cloth and its five companion values are literals, identical in both themes. Never re-express them as Radix steps that would flip in dark mode.

## Typography

**Display Font:** Besley, self-hosted variable (wght 400-900, Latin subset, `src/assets/fonts/Besley-wght.woff2`, SIL OFL), with three metric-matched fallbacks (Georgia, Noto Serif, Times/Liberation Serif) then Georgia, serif. Supplied to Radix as `--heading-font-family` and preloaded in the document head.
**Body Font:** the Radix system sans stack.
**Label/Mono Font:** the Radix code stack (Menlo, Consolas) for code only.

**Character:** A sturdy slab-serif Clarendon carries the things a reader scans for, and an unremarkable sans carries the reading, so the type tells look-up from read-through at a glance.

### Hierarchy
- **Display** (700, 35px from 30em (480px) up / 28px on phones, 40px line): the page title, "Blog" and a post's title. Balanced wrapping on every heading.
- **Headline** (700, 1.5rem desktop / 1.375rem phone, 1.25): post section headings (h2), with 2em above and 0.5em below. h3 is 1.25rem / 1.1875rem; h4 1.125rem / 1.0625rem; each stays above the 18px body.
- **Year** (700, 20px, lining figures): the year heads of the index, over a 1px rule.
- **Wordmark** (700, 20px): "Alberto.Codes" on the cloth.
- **Title** (600, 1.125rem, 1.3, no tracking): index entries.
- **Body** (400, 1.125rem from 768px, 1rem below): running text and lists, held to the 40rem measure.
- **Summary** (400, body size, 1.55, muted ink): a post's standfirst; never smaller than the body.
- **Meta** (400, 14px, 20px line, tabular figures): dates, index summaries, series runs, table cells on phones.
- **Mark** (600, 12px on the index / 14px in a dateline, all small caps, 0.05em): a post's kind, the table-of-contents summary.
- **Nav** (500, 14px): masthead navigation.

### Named Rules
**The Look-Up Face Rule.** Besley sets only what a reader looks up: wordmark, page and post titles, section headings, years, index entries. Navigation, labels, tables and running text stay in the sans.

**The Struck Kind Rule.** A kind is told apart by its letterforms (small caps in muted ink), never by a hue or a filled chip.

## Layout

Every page sits in a Radix `size="3"` container (880px inner) with `var(--space-6)` padding above and below (`src/alberto_codes_site/layout.py`). Ordinary pages and the blog index use a centred 48em column. A post uses the full 880px so tables, figures and code blocks can spread, while its header, paragraphs, headings, lists and blockquotes keep to a centred 40rem measure (about 70 characters at 18px). Index summaries cap at 65ch.

The masthead is sticky, with side padding `var(--space-4)` on phones and `var(--space-6)` from the md breakpoint; headings reached by fragment links carry a 5rem scroll margin so the band does not cover them.

The one responsive hinge is 768px. Below it: body at 16px, headings one step down, the index has no leader and puts the date beside the marks, titles balance; table cells shrink to 14px with 0.5em 0.625em padding. Above it: body at 18px, the leader is drawn, the date sits right-aligned on the title's last line, table cells at 0.75em 1em.

The index is tight on purpose: rows carry 0.3em of block padding, the intro, legend and series run share `space-1` gaps so the first year heading lands high on the first screen.

## Elevation & Depth

Flat. There are no shadows anywhere in the system; depth is the binding itself. The cloth band is the only filled plane, and on the page everything is separated by rules: heavy (2px graphite) for tables, hairlines for heads, soft rules to close the series box and contents. The only shadow-like value is the 1px inset outline on buttons sitting on the cloth, which reads as a rule, not a lift.

### Named Rules
**The Ruled, Not Raised Rule.** Separate with a rule or with space, never with a shadow or a card fill.

## Shapes

Square by default. Tables have no radius and no fills. Radii appear only on controls and their focus: 3px (`var(--radius-1)`) on focus outlines around index rows and links, 4px (`var(--radius-2)`) on code blocks, the copy button and buttons. Lines are the dominant form: dotted 2px leaders, 2px heavy rules, 1px hairlines, the 2px underline under the current page.

## Components

### Masthead and Footer (the cloth)
- **Character:** the book's binding, fixed in both themes.
- **Masthead:** sticky, `class_name="cloth"`, wordmark left in Besley, navigation right in 14px sans; the resume link and theme toggle sit at the end.
- **Footer:** the same cloth, copyright left, GitHub and LinkedIn icons right in cloth ink.

### Navigation
- **Rest:** muted cloth ink, no underline, 0.25em block padding with a transparent 2px bottom border.
- **Hover:** full cloth ink.
- **Current:** each prerendered page bakes `aria-current="page"` on its entry; it takes full cloth ink and a 2px cloth-mark underline. Post and series pages mark Blog.
- **Phone:** a drawer on the ground; the current entry is 600 weight with a 2px grass-11 underline offset 0.3em.

### Buttons
- **On the cloth:** transparent with a 1px inset cloth-rule outline, cloth ink text, hover wash `--cloth-hover` on hover-capable devices; ghost icon buttons drop the outline.
- **Solid (on the ground):** accent 9 darkened 22% with black, 30% on hover, so white text clears 4.5:1 (`a11y.css`).
- **Focus:** 2px accent-11 outline, offset 2px; cloth-mark on the cloth.

### Index Entry (signature)
- **Character:** a line from a book's index.
- **Structure:** Besley title left, a dotted 2px hairline leader from the title's last word to the date, date right in 14px tabular figures; beneath, the summary's first sentence in muted 14px sans; beneath that, the kind and series as small-cap marks separated by middots.
- **Hover / Focus:** the whole row is the hit area. The title turns grass 11 and the leader closes into a solid 2px grass-11 rule over 120ms ease-out; keyboard focus draws a 2px accent-11 ring around the row. Under reduced motion the change is immediate.
- **Grouping:** rows are grouped under year headings, newest first.

### Proportion Table
- **Style:** collapsed borders, 2px graphite rule above and below, 1px hairline under the head, no verticals, no fills, tabular figures; head cells at 600.

### Code Block
- **Style:** 4px radius, 1px code-border frame, a code-surface header strip holding the language in 12px mono and a 32px copy button. Inline code is graphite on `var(--gray-a3)`, never accent.

### Series Box and Contents
- **Style:** both sit in the reading measure, closed by a soft 1px rule. The contents summary is a small-cap 14px mark with a CSS caret; entries are grass-11 links on hairline-ruled lines. Series links in runs are underlined because colour alone falls under 3:1 in dark mode.

## Do's and Don'ts

### Do:
- **Do** take every page colour from the Radix grass and sage steps, and the binding from the six `--cloth*` literals in `identity.css`.
- **Do** underline links that sit in running text or runs (0.2em offset, 1px), since the grass ink alone falls under 3:1 against dark-theme text.
- **Do** set headings in Besley through `--heading-font-family` so `rt-Heading` picks it up; keep its fallback stack intact so wraps do not move on swap.
- **Do** keep a post's running text in the 40rem measure and let tables, figures and code use the 880px column.
- **Do** rule tables heavy-hairline-heavy with tabular figures.
- **Do** remove the leader transition under `prefers-reduced-motion`.

### Don't:
- **Don't** colour a kind, tag or status; set it as a small-cap mark in muted ink.
- **Don't** put the accent on inline code, dates, headings at rest or decoration.
- **Don't** wrap posts in bordered cards or give surfaces shadows.
- **Don't** set a cream or warm ground; the paper is sage.
- **Don't** add vertical rules or zebra fills to tables.
- **Don't** add motion beyond the leader's close and the contents caret.

### Known gaps

Recorded so they are not mistaken for rules. Link-preview (OG) images in `src/assets/og/` still carry the previous look and do not yet show the cloth or Besley. The table of contents does not track scroll position. Pages other than the blog index and posts inherit the theme, the cloth and the shared columns but have not been restructured into this world; their internal layouts are not evidence for this system.
