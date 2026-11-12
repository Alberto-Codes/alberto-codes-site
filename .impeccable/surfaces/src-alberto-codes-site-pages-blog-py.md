---
version: 1
slug: "src-alberto-codes-site-pages-blog-py"
primary_target: "src/alberto_codes_site/pages/blog.py"
related_targets: []
---

# Surface brief: blog index and post page (and the site frame they share)

Scope: `/blog`, `/blog/<slug>`, plus the masthead, footer and theme tokens every page inherits.
Visitor mode: Read.
Audience and job: an engineer who arrived at one post, often on a phone, wants to understand what was measured and check it; a returning reader wants to find a post by year or series.
Content: 35 published posts, seven series, four post types; long-form prose, measurement tables, code, SVG figures.
Constraints: PRODUCT.md brand commitments; the 40rem reading column and 18px body stay; both light and dark themes; prerendered static export; WCAG AA; posts' Markdown is not edited.
Decision record: direction chosen 2026-11-11.
Unresolved: link-preview (OG) cards still carry the old look; table-of-contents position tracking is not built.
Amended 2026-11-11 after the finish review: the index shows each summary's first complete sentence, never a mid-word cut; the full summary stays on the post. The post's type-and-date line moved below the title.

## Direction contract

THESIS: The site is a working reference book of measured results, and the blog index is a book's index, not a feed. It refuses the developer-blog arrangement of identical bordered cards under default framework styling.

OWN-WORLD: A 1900s trade reference bound in bookcloth. A deep bottle-green cloth field owns the masthead and the footer in both themes; the ground is a green-tinted neutral, never cream. One ink, the cloth green, marks links and where the reader stands, and nothing else; post types are small-cap marks, not coloured badges. A Clarendon (Besley, self-hosted) sets the wordmark, titles, section openers and index entries; the system sans keeps the reading column. Tables are ruled like printed proportions: a heavy rule above and below, a hairline under the head, no vertical lines, tabular figures.

STORY: In one screen the reader sees a body of dated, checkable work, finds a post by year or series, and then reads it with the frame out of the way.

FIRST VIEWPORT: Index at 1440x900: the cloth band runs full width, wordmark left in Clarendon, navigation right with the current page marked. Below it, in the 48em column: the "Blog" title with RSS, one line of introduction, the series as a single run of links, then the first year heading and at least six index rows. Each row sets the title left in Clarendon, a dotted leader, and the date right in tabular figures, with the first sentence of its summary beneath and the type and series marks under that. At 390x844: band, title, and at least three entries. Post at 390x844: band, title, a dateline with the type mark and date, summary, and the first lines of body text.

SIGNATURE: On hover or keyboard focus an index row's dotted leader closes into a solid rule in the cloth green. Motion grammar: that one 120ms ease-out change, removed under reduced motion; nothing else moves.

RAISES: From the patent drawing sheet: one ink is reserved for what is under examination. From the cutting bench: state is a mark, not a hue. From the cathode numeral stack: the current choice is struck forward, so the navigation marks the page the reader is on.

FORM: A reference cookbook's index and its tables of proportions, candidate 7 of 7 on the ordered list; seed:c1ee9ccdd9d3452a.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
