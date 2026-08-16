# ADR-0004: Syndicating Posts to Third-Party Platforms

## Status

Accepted

## Date

2026-08-15

## Context

Two posts published on 2026-08-15 raised a question the site has never
answered: when a post goes out to dev.to, Medium, or Hashnode as well as
alberto.codes, what exactly goes out, and what is the relationship between
the two copies?

There was no policy. There was one precedent —
`_bmad-output/implementation-artifacts/medium-boto3-deep-dive.md`, a
hand-made Medium cut of the March 2026 boto3 post — which happened to get
the important parts right (it recorded a canonical URL, listed its images,
and trimmed the source rather than exporting it) but recorded none of that
as a decision. The next cut would have re-derived it from scratch.

The risks worth designing against:

- **Duplicate-content ranking.** Two copies of the same article compete in
  search. Without a canonical pointer the syndicated copy can outrank the
  original on the author's own material.
- **Drift.** The canonical post gets corrected — as the 08-11 post was, twice
  — and the syndicated copy silently becomes wrong. `draft-vramfit-the-scoreboard.md`
  already flagged this failure mode for a different mirror and never resolved it.
- **Platform mismatch.** A 2,246-word command-by-command walkthrough and a
  1,469-word argument piece do not belong on the same platform, and deciding
  per-post invites deciding badly.
- **Assets.** No major platform accepts SVG in article bodies. Every diagram
  on this site is an SVG.

## Decision

### 1. alberto.codes is always canonical

Every syndicated copy sets the platform's canonical URL field to the
alberto.codes URL. dev.to takes `canonical_url` in front matter. Medium sets
it in story settings after publish, which means it is a post-publish step
that is easy to forget and must appear in the checklist.

The canonical post is the one that gets corrected. Corrections never fan out.

### 2. Platform is chosen by Diataxis type

The site already classifies every post (ADR-0002). That classification picks
the platform:

| Diataxis type | Platform | Why |
|---|---|---|
| how-to, tutorial | dev.to | The audience arrives wanting commands to run. Long walkthroughs perform well and get bookmarked. |
| explanation | Medium | Argument-driven, narrative, no commands. Medium's readership rewards that shape and punishes terminal output. |
| reference | neither | Reference material belongs with the thing it documents. |

This is a default, not a law. Overriding it is fine; deciding it fresh each
time is what this row exists to prevent.

### 3. A cut is a rewrite, and it is frozen

A syndicated copy is a **cut**: a shorter piece rewritten for its platform,
not an export of the canonical markdown. Cuts drop internal cross-links,
collapse tables that carry two audiences at once, and lose the caveats that
only matter to a reader who will actually run the thing.

Once published, a cut is frozen. It carries its publish date and a pointer
home, and it is never re-synced. If the canonical post changes materially,
the correct action is a note on the cut pointing at the canonical version,
or deletion — never a silent edit to match.

Every cut opens with a pointer line naming alberto.codes as the original.

### 4. Cuts are tracked in `docs/syndication/`

Path: `docs/syndication/<platform>/<canonical-slug>.md`.

They are version-controlled because a frozen public copy whose text exists
nowhere in the repo cannot be audited later. They live outside `src/` because
`src/posts/` is scanned at app startup and anything that looks like a post
would be routed and published.

The boto3 Medium cut stays where it is. It is grandfathered, not a pattern.

### 5. Images are rasterized to PNG and served from alberto.codes

No platform accepts SVG in an article body. Every diagram is rendered to PNG
at 3× and hotlinked from `https://alberto.codes/<name>.png` rather than
uploaded to the platform. Hotlinking keeps one copy of each asset, so a fixed
diagram fixes everywhere at once — the one exception to the freeze in
decision 3, and an acceptable one because an image cannot drift into
contradicting prose the way text can.

PNGs are committed beside their SVG source in `src/assets/`.

**Rasterize through a browser, not through ImageMagick or librsvg.** Mermaid
emits node labels as `<foreignObject>` HTML when `htmlLabels` is on. Browsers
render it; ImageMagick and librsvg drop it silently and produce a diagram of
empty boxes with no text and no error. `vramfit-three-ceilings.svg` carries 30
`foreignObject` elements and zero `<text>`, and converted to a blank flowchart
on the first attempt. The working command:

```bash
google-chrome --headless=new --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=3 --window-size=<w+120>,1400 \
  --screenshot=out.raw.png "file://<wrapper>.html"
magick out.raw.png -trim +repage -bordercolor '#0f172a' -border 48 out.png
```

The wrapper sets `background:#0f172a`, gives the SVG its natural width with
`height:auto`, and must leave `overflow:visible`. Mermaid's `viewBox` height
is computed against fonts the rendering machine may not have — Trebuchet MS is
absent on most Linux boxes — so a fixed height clips the bottom row.

Background is `#0f172a` to match the site, which also means the image carries
its own background and reads correctly in both light and dark mode on the
destination platform.

## Consequences

### Positive

- Search treats alberto.codes as the original for every syndicated post.
- Platform choice is decided once, not per post.
- Freezing removes an unbounded maintenance obligation. A syndicated copy is
  a snapshot, and says so.
- Hotlinked images mean one asset to fix, and no per-platform upload step.
- The rasterizing procedure is recorded, including the failure that produced
  a silently blank diagram.

### Negative

- A frozen cut can contradict a corrected canonical post. Mitigated by the
  pointer line, not solved by it. The judgment call — annotate or delete —
  stays manual.
- Medium's canonical URL is a post-publish step with no front-matter
  equivalent, so it can be forgotten. The checklist carries it.
- Rasterizing needs a browser on the machine doing the render, which is a
  heavier dependency than `mmdc` alone.
- Two representations of every diagram (SVG for the site, PNG for
  syndication) must be regenerated together when a diagram changes.

## References

- [ADR-0002: Blog Content Strategy Using the Diataxis Framework](0002-blog-content-strategy-diataxis.md)
- [ADR-0003: Blog Infrastructure and Rendering](0003-blog-infrastructure.md)
- [Cut template](../templates/syndication-cut.md)
- [dev.to front matter reference](https://dev.to/p/editor_guide)
