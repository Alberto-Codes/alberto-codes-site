# ADR-0004: Which Platform Carries Which Post

## Status

Accepted

## Date

2026-08-15

## Context

Two posts published on 2026-08-15 raised a question the site has never
answered: what goes on dev.to, what goes on Medium, and what stays here?

The reflex answer — all of it, everywhere — is the one to reject. It is the
ad campaign that buys every channel and runs the same spot on each. The real
question is which audience each platform holds and which piece of writing
that audience came for.

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
- **Broadcasting.** The reflex when a post is finished is to push it
  everywhere. That is the campaign that runs one creative on every channel.
  It competes with itself in search, and it tells anyone following on two
  platforms that one of them is redundant.
- **Assets.** No major platform accepts SVG in article bodies. Every diagram
  on this site is an SVG.

## Decision

### 0. One piece, one platform. Distribution is not duplication.

This governs every decision below it.

A platform is a niche with an audience that came there for a reason.
dev.to readers arrive wanting something to run. Medium readers arrive
wanting an argument. r/LocalLLaMA arrives wanting the artifact and the
numbers. Pushing one piece through all of them is the campaign that runs
identical creative on every channel — it reads as broadcast, it competes
with itself in search, and it teaches the audience that following you on
two platforms is redundant.

So the default is: **each platform gets the piece that belongs on it, and
nothing else goes there.** The how-to lives on dev.to. The explanation
lives on Medium. alberto.codes carries everything, because the site is the
record rather than a channel.

Syndicating the same piece twice is the exception. It needs a reason
beyond reach — a genuinely different audience that will not encounter the
other copy. Absent that reason, the answer is not a second cut of the same
post. It is a different post, or nothing.

**The anti-pattern to watch for is a surface checklist**: one item of
content and a list of platforms to push it through. Whenever that shape
appears in an issue, the fix is to ask what each surface should carry,
not how to adapt one thing to all of them.

The decisions below apply to the exception. They are the mechanics for
when a piece does travel, not an argument that it should.

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

Read this as an assignment, not a permission. A post goes to **its** row and
does not visit the others. The table's job is to stop the same piece from
appearing in two places, as much as to pick where it appears once.

This is a default, not a law. Overriding it is fine. Deciding it fresh each
time, or ignoring it because a checklist says otherwise, is what it exists to
prevent.

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
at 3× and written into the cut as `https://alberto.codes/<name>.png`. The URL
must resolve at publish time, so the PNG has to be committed and deployed
before the cut is pasted anywhere.

**Do not expect that URL to stay live in the published copy.** Measured on
dev.to 2026-08-15: at publish it fetched the image and rehosted it under
`dev-to-uploads.s3.amazonaws.com`, keeping the alt text and dropping the
alberto.codes URL from the page entirely. The published post has its own copy.
Fixing the PNG here will not change it.

So images freeze exactly like text does, which makes decision 3 simpler
rather than harder — a cut is a snapshot, images included. Re-publishing is
the only way to update one, and that is rarely worth it.

**Cover images are the exception, and they get uploaded.** A cover is
platform chrome, not article content — it appears in the feed and the social
card, never in the body. dev.to's v2 editor offers no URL field for it at
all, so hotlinking is not available even in principle. Upload the same PNG
that lives in `src/assets/`. A cover that drifts from the canonical post
costs nothing, because no argument rests on it.

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

## Amendment, 2026-08-15: dev.to ships a v2 editor with no front matter

The decisions above were written assuming dev.to's markdown editor, where a
cut pastes as one block and `canonical_url`, `tags`, and `cover_image` parse
from YAML front matter. The account's editor is **v2**, which has none of
that. Publishing the first cut found this, and the correction is recorded
here rather than by rewriting the decisions.

What changes:

- **Front matter is not parsed.** Pasted as-is it renders as literal text at
  the top of the post. The cut's front matter block becomes a reference for
  filling fields by hand, not something to paste.
- **Each value has its own UI field.** Title and body are separate inputs.
  Tags are a chip widget that commits an entry on a typed comma — setting the
  field's value wholesale offers all four as one combined tag, which is
  wrong. Canonical URL lives behind **Advanced Options**, and a `🔗 Canonical`
  badge in the footer confirms it registered.
- **`published: false` protects nothing.** There is no draft flag in v2.
  **Publish** publishes immediately. **Save Draft** is the only way to park a
  post, and until one of them is clicked nothing exists server-side — closing
  the tab loses the work.
- **Cover images upload only**, per the amended decision 5.

The cut file keeps its front matter block regardless. It is the record of
what the field values should be, it stays correct for Medium and for any
platform that does parse it, and a v2 session reads it as a checklist.

## Consequences

### Positive

- Search treats alberto.codes as the original for every syndicated post.
- Platform choice is decided once, not per post.
- Freezing removes an unbounded maintenance obligation. A syndicated copy is
  a snapshot, and says so.
- One rasterized PNG per diagram serves every destination, with no
  per-platform upload step for inline images.
- The rasterizing procedure is recorded, including the failure that produced
  a silently blank diagram.
- Images freeze with the text rather than drifting from it, because the
  platform rehosts them. The freeze in decision 3 needs no exception.

### Negative

- A frozen cut can contradict a corrected canonical post. Mitigated by the
  pointer line, not solved by it. The judgment call — annotate or delete —
  stays manual.
- Medium's canonical URL is a post-publish step with no front-matter
  equivalent, so it can be forgotten. The checklist carries it.
- Rasterizing needs a browser on the machine doing the render, which is a
  heavier dependency than `mmdc` alone.
- dev.to's v2 editor has no draft flag, so the safety the cut's
  `published: false` was meant to provide does not exist. A misplaced click
  publishes. The checklist compensates; the editor does not.
- Field-by-field entry is slower and easier to get wrong than one paste. The
  tag widget in particular fails silently by accepting a combined tag that
  looks plausible.
- Two representations of every diagram (SVG for the site, PNG for
  syndication) must be regenerated together when a diagram changes.

## References

- [ADR-0002: Blog Content Strategy Using the Diataxis Framework](0002-blog-content-strategy-diataxis.md)
- [ADR-0003: Blog Infrastructure and Rendering](0003-blog-infrastructure.md)
- [Cut template](../templates/syndication-cut.md)
- [dev.to front matter reference](https://dev.to/p/editor_guide)
