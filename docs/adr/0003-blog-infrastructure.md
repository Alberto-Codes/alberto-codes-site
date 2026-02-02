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
- Frontmatter parsing is custom and basic — doesn't handle nested YAML (tags as list). Could upgrade to a YAML parser if needed
- Diagrams require a manual pre-render step (`npx @mermaid-js/mermaid-cli -i input.mmd -o src/assets/output.svg`) before publishing
- All posts load into memory at startup — fine for dozens of posts, would need rethinking at hundreds

## References

- [ADR-0002: Blog Content Strategy Using the Diataxis Framework](0002-blog-content-strategy-diataxis.md)
- [Reflex Markdown Component](https://reflex.dev/docs/library/typography/markdown/)
