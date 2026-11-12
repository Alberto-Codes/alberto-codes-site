# Product

<!-- impeccable:product-schema 1 -->

<!--
Written 2026-11-11 without an interview, at the owner's instruction.
Every statement is drawn from the repository (page copy, AGENTS.md, posts)
unless marked "Inferred", which marks a reading the owner has not confirmed.
-->

## Platform

web

## Users

- **Engineers reading one post.** They arrive from LinkedIn, a feed reader,
  search or a GitHub release note, usually on a phone, to read a single
  technical writeup about open models or open source tooling. Their job is
  to understand what was measured and decide whether to trust or reproduce
  it. (Inferred: the phone share and the arrival paths are not measured
  here; the site has share cards, an RSS feed and release notes that link
  back to posts.)
- **Professional peers and hiring readers.** They come to judge the author:
  the home, about, experience, projects and publications pages, and the
  resume PDF. (Inferred from those pages existing; no audience research.)

## Product Purpose

The personal site and technical blog of Alberto Nieto, a Generative AI
Principal Engineer. It publishes writeups of open source tools he builds on
his own time to test what models actually do, each with the evidence behind
its claims, alongside a professional profile. Success is a reader finishing
a post able to check the result for themselves. (Inferred: the success
definition.)

## Positioning

Claims come with their evidence. Posts report measured results, including
failed baselines, pin reproduce commands to a tagged release, and link to
that release. The home page states it as building tools "that test what
models actually do, then publish the evidence."

## Operating Context

- A static site: Reflex (Python) exported to GitHub Pages at alberto.codes.
  Deployment runs on every push to main.
- 37 posts as of 2026-11-11, written in Markdown under `src/posts/`, each
  with a link-preview card under `src/assets/og/`.
- Posts carry one of four types (tutorial, how-to, explanation, reference);
  31 of 37 are explanations.
- Seven series: Saucier, vramfit, docvet and docstring quality, TurboQuant
  on vision models, Measuring model confidence, AI pipeline plumbing,
  Encrypted ADK sessions.
- Posts hold long-form prose, code blocks, measurement tables, SVG figures
  and Mermaid diagrams.
- Each post is announced with a LinkedIn post, and a GitHub release that
  names the post as its writeup.

## Capabilities and Constraints

- No backend at runtime, no search, no comments, no analytics evident in
  the repository.
- Pages are prerendered, so any default state is baked into the HTML;
  viewport-dependent defaults must be done in CSS.
- Styling is written in Python against Radix Themes, plus one hand-written
  stylesheet, `src/assets/a11y.css`.
- Layout widths, heading structure, contrast of code tokens and other
  presentation rules are pinned by tests under `tests/`.
- Product-facing figures (package counts, project metrics, career facts)
  are hand-written on several pages and must change together; see
  AGENTS.md.

## Brand Commitments

- Name: Alberto.Codes.
- A published post is a dated record. Out-of-date claims get a dated note
  appended; the body is not rewritten.
- Posts are framed as personal curiosity and personal projects, never as a
  general method that resembles day-job work.
- Posts do not promise a next release or a next post.
- No AI attribution in published content, figures or commits.
- A post about a tagged release closes with one link to that release.

## Evidence on Hand

- Real posts with real measurements, tables and figures: `src/posts/`,
  `src/assets/`.
- Open source projects and PyPI packages, with provenance comments, in
  `src/alberto_codes_site/pages/projects.py`.
- Publications in `src/alberto_codes_site/pages/publications.py`.
- Career facts on the experience page; a headshot at
  `src/assets/headshot.jpg`; a resume PDF.
- Absent, and not to be invented: testimonials, reader numbers, traffic or
  audience data, logos of employers or clients.

## Product Principles

1. The evidence is the product: a table, figure or command that lets a
   reader check a claim outranks anything decorative.
2. Reading comes first: a post is a document, and nothing competes with
   its reading column.
3. A reader who arrives at one post should reach its first paragraph
   without effort, on a phone as well as a desktop.
4. Nothing on the site claims more than a post or a repository shows.
5. Published posts stay as they were written.

## Accessibility & Inclusion

The site already holds itself to WCAG AA in practice: a dedicated
`a11y.css`, tests for code-token contrast, heading structure and nested
interactive elements, and a Lighthouse accessibility score of 100 on the
home page, blog index and one post on 2026-11-11. (Inferred: AA as the
stated standard; no document names one.)
