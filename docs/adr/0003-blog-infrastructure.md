# ADR-0003: Blog Infrastructure and Rendering

## Status

Accepted

## Date

2026-02-01

## Context

ADR-0002 established the Diataxis framework as our blog content strategy. We now need to decide how blog posts are stored, rendered, and routed on the site. The site is built with Reflex (Python), and we want an approach that is simple to maintain, version-controlled, and doesn't require an external CMS or database.

Key requirements:

- Easy to author new posts (low friction for someone new to blogging)
- Posts version-controlled alongside the code
- Individual URLs per post for shareability and SEO
- Metadata for title, date, Diataxis type, summary, and tags
- Reading time estimates
- Support for code blocks, headings, and standard markdown features

## Decision

### Storage: Markdown files with YAML frontmatter

Posts are stored as `.md` files in `src/posts/`, named with the convention `YYYY-MM-DD-slug.md`. Each file includes YAML frontmatter:

```yaml
---
title: Why I Chose Reflex for My Portfolio Site
date: 2026-02-01
type: explanation
summary: A Python engineer's case for building a portfolio without JavaScript.
tags:
  - python
  - reflex
---
```

The body below the frontmatter is standard markdown rendered by `rx.markdown()` with GitHub Flavored Markdown (GFM) enabled.

### Diagrams: Pre-rendered SVGs

Mermaid diagrams cannot be rendered client-side in Reflex's static export because `rx.markdown` does not support Mermaid natively, `rx.script` injects into `<head>` via Helmet (race condition with React rendering), and React's `dangerouslySetInnerHTML` strips `<script>` tags. Instead, diagrams are pre-rendered to SVG files using the Mermaid CLI (`@mermaid-js/mermaid-cli`) and placed in `src/assets/`. Posts reference them with standard markdown image syntax: `![alt text](/diagram-name.svg)`.

Since 2026-10-01, an SVG that carries the shared figure tokens is inlined
into the post HTML at render time instead of loading as `<img>`, so it follows
the site's light/dark toggle. See
[ADR-0005](0005-theme-aware-post-figures.md).

### Routing

- `/blog` — Index page listing all posts as clickable cards, sorted by date descending
- `/blog/<slug>` — Individual post page with full rendered content, back link, and SEO meta tags

Routes for individual posts are registered dynamically at app startup by scanning the `src/posts/` directory.

### Blog index features

- Posts displayed as cards with title, summary, date, Diataxis type badge, and reading time
- Diataxis types color-coded: tutorial (green), how-to (orange), explanation (violet), reference (cyan)
- Diataxis legend shown at the top of the index page

### Individual post features

- Title rendered from frontmatter (not duplicated in markdown body)
- Diataxis type badge, date, and reading time in the header
- "Back to Blog" navigation link
- Per-post `<title>` and `<meta description>` tags for SEO

### Why not a database or CMS?

- Markdown files are simpler, require no infrastructure, and are git-tracked
- Content stays with the code — no external dependency
- Appropriate scale for a personal blog

## Amendment, 2026-09-05: code blocks render through a scroll area

Post bodies still go through `rx.markdown(use_gfm=True)`, but fenced code
blocks are no longer left to the browser. Two rendering defects were found in
the browser and corrected in `_render_post` and `_code_block`
(`src/alberto_codes_site/pages/blog.py`); the correction is recorded here
rather than by rewriting the decisions above.

- **Code blocks own their horizontal scrolling.** `component_map={"pre": ...}`
  wraps each highlighted block in a scroll area with a styled horizontal
  scrollbar, so a block wider than the prose column shows a visible thumb at
  rest. The previous default relied on the OS's overlay scrollbars, which stay
  invisible until a scroll happens, so a reader got no hint that the end of a
  line — a URL, a flag — was cut off.
- **Inline code carries no trailing padding.** The Radix default detached a
  following period or comma from the closing backtick.

Browser verification of both, including the measurement script and before/after
screenshots, is in
[docs/validation/site-pre-overflow/README.md](../validation/site-pre-overflow/README.md).

## Amendment, 2026-10-01: code blocks carry a language label and copy button

`_code_block` puts a bar above each block (issue #76): the fenced language on
the left, omitted when the fence names none, and a "Copy code" button on the
right. The bar sits above the scroll area rather than over the code, so the
button never covers a line on a phone and the block still scrolls sideways.
The site is a static export with no backend, so the copy is a plain `onClick`
that calls `navigator.clipboard.writeText` with the block text markdown passes
in; it flags the button for two seconds (copy icon swaps to a check) and
writes "Copied" to a polite live region. The highlighting theme is unchanged.
`tests/test_code_block_toolbar.py` checks the compiled structure.

## Amendment, 2026-10-01: running text keeps a reading measure

A post's column stays at the container's 880px, but its running text no longer
fills it (issue #78): at 16px a full-width line ran to about 116 characters.
The header and the body's paragraphs, headings, lists and blockquotes are
capped at `READING_WIDTH` (34rem) and centred, which measures about 71
characters per line at 1440px wide. Tables, code blocks, inlined figures and
image paragraphs still use the full 880px. The measure is set in rem rather
than `ch`, because `ch` grows with a heading's font size and would break the
shared left edge; lists keep their 1.5rem bullet indent inside it. The widths
live in `src/alberto_codes_site/layout.py`, which also holds the 48em column
every other page now centres, and the containers' vertical padding, which was
a bare Radix step (`"6"`) that browsers dropped and is now `var(--space-6)`.
`tests/test_page_widths.py` checks the compiled styles.

## Amendment, 2026-10-01: table of contents and heading links

A post with four or more H2s (`TOC_MIN_SECTIONS` in `pages/blog.py`) gets an
"On this page" block between the header and the body (issue #75); a shorter
post gets none. It lists the H2s in order with any H3s nested under their H2,
sits in the reading column, and is a `<details>` element, open on load, inside
`<nav aria-label="On this page">`. Its label is the `<summary>`, not a
heading, so the heading outline that `tests/test_heading_structure.py` checks
is unchanged. There is no scroll-spy and no sticky sidebar.

Every body heading also gets a link to its own fragment, labelled "Link to
section: <heading text>". It is a sibling of the heading inside a wrapper, not
a child, so the heading's accessible name stays its own text, and it follows
the heading in tab order. It is hidden until the heading is hovered or the link
has keyboard focus; on a device without hover (`@media (hover: none)`) it
always shows, in muted grey.

The TOC entries come from the same `Slugger` pass that gives the headings their
ids (`headings.py`, from #97), so they cannot disagree;
`tests/test_table_of_contents.py` checks that for every post. Both kinds of link
are React Router links (`rx.el.a`): a plain `<a>` jump creates a history entry
the router did not make, and its scroll restoration puts the page back where it
was. Headings carry `scroll-margin-top: 5rem`, so a fragment lands below the
sticky header (about 57px), whether it is clicked or opened as a fresh URL.

## Amendment, 2026-10-01: an end-of-post section

Every post closes with a light section (issue #74, `_post_end` in
`pages/blog.py`), in the reading column under a top border, in small text:

- **Older / newer:** "← Older" and "Newer →" with the adjacent posts' titles,
  in date order among *published* posts (`published_posts`), so a
  future-dated post is never linked. The oldest post has no Older link and the
  newest no Newer link.
- **More on this:** up to three posts that share at least two frontmatter
  `tags` with this one, ranked by the number shared, ties to the newer post,
  leaving out the post itself and its older/newer links. Title and date only;
  with no match the block is left out.
- **Author line:** "Written by Alberto Nieto, Generative AI Principal
  Engineer." with links to About, GitHub, LinkedIn and the RSS feed. The name,
  title and profile URLs come from `social.py`.
- **Discussion link:** an optional frontmatter field `discussion_url`. When set,
  the post links to it as "Discuss on r/<sub>" for a subreddit thread, else
  "Join the discussion".

The older/newer and related blocks are `<nav>` elements named by
`aria-label` and labelled with plain text, not headings, so the heading
outline and the table of contents are unchanged. Post links are React Router
links, as on the index cards. The section is page chrome only: it is not in
the RSS item bodies or the JSON-LD. There are no comments, popups, email
capture or generated summaries. `tests/test_post_end.py` checks every post.

## Amendment, 2026-10-01: series

A post joins a series with one optional frontmatter line, `series: <Display
Title>` (issue #51). Posts without it are standalone. The model lives in
`series.py`:

- **Parts** are the *published* posts (`published_posts`) carrying the same
  title, numbered oldest first by `date`, ties broken by file name. A
  future-dated part is neither counted nor linked until its date arrives.
- **Slug** comes from the title through the heading `Slugger`, so "TurboQuant
  on vision models" is `turboquant-on-vision-models`. Two titles that give the
  same slug fail the build.

Where a series shows:

- **In a part:** a compact box under the header, above the table of contents,
  in the reading column: "Part N of M in <series>", the series name linking its
  page, with "← Previous" and "Next →" to the adjacent parts. It is a `<nav>`
  named by `aria-label`, not a heading.
- **At a part's end:** the end section opens with "Next in <series>" and the
  next part's title, or "Last part of <series>" for the newest part. The
  older/newer links stay chronological. "More on this" leaves out the parts
  the box already links (the previous and next ones).
- **Series pages:** `/blog/series/<slug>`, one per series, registered through
  `add_page` like any page, so each has a canonical link, a share card (the
  site card) and a sitemap entry whose `<lastmod>` is the newest part's date.
  The page is an `<h1>` with the title, one sentence giving the part count and
  date range, and the parts in order as blog cards labelled "Part N of M". No
  description is written for a series.
- **Blog index:** a "Series" line under the type labels lists each series,
  newest first, with its part count, linking its page. Each card of a part
  carries a muted "Part N of M · <series>" label in the #79 plain-label style;
  it is plain text, since the whole card is already a link.

A part's `BlogPosting` JSON-LD carries `isPartOf`, a `CreativeWorkSeries` with
the series name and page URL. Series navigation is page chrome: it is not in
the RSS item bodies. `tests/test_series.py` checks the membership, numbering,
published-only counting, the routes against the sitemap, and the box on every
part.

## Consequences

### Positive

- Adding a post is just creating a `.md` file — minimal friction
- Posts are version controlled and diffable
- Each post gets its own URL with proper SEO metadata
- Diataxis type badges make content taxonomy visible to readers
- Reading time sets reader expectations

### Negative

- Posts are static at build/deploy time — no hot-reload of new posts without server restart
- No search, pagination, or tag filtering yet (acceptable at current scale, can be added later)
- Frontmatter parsing is minimal (top-level `key: value` plus simple lists like `tags:`). It is not a full YAML parser
- Diagrams require a manual pre-render step (`npx @mermaid-js/mermaid-cli -i input.mmd -o src/assets/output.svg`) before publishing
- All posts load into memory at startup — fine for dozens of posts, would need rethinking at hundreds

## References

- [ADR-0002: Blog Content Strategy Using the Diataxis Framework](0002-blog-content-strategy-diataxis.md)
- [Reflex Markdown Component](https://reflex.dev/docs/library/typography/markdown/)

## Amendment, 2026-10-01: a wider measure at 18px on desktop

The first measure (34rem of 16px text) read narrow on a desktop screen beside
880px figures. From the md breakpoint (768px) up, a post's paragraphs, list
items and blockquotes now set at 18px (`READING_FONT_SIZE`, 1.125rem), and
`READING_WIDTH` is 40rem (640px). That still measures about 74 characters per
line at 1440px wide, and figures, tables and code blocks step out only 120px
a side. Phones keep the 16px base, where the measure is wider than the screen
anyway. Tables and code blocks keep their own font sizes.
