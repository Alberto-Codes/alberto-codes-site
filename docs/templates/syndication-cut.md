# Syndication cut template

Copy this file to `docs/syndication/<platform>/<canonical-slug>.md` and fill
it in. Policy lives in
[ADR-0004](../adr/0004-syndication-and-canonical-urls.md) — read it once, then
work from this checklist.

The everything-above-the-`---` part is working notes for the person
publishing. Only the article body gets pasted into the platform.

---

## Before you write

- [ ] Canonical post is published and live at its final URL
- [ ] Platform matches the post's Diataxis type (ADR-0004 decision 2):
      how-to and tutorial to dev.to, explanation to Medium
- [ ] Every diagram rasterized to PNG and **deployed**, so the hotlink
      resolves. Verify with `curl -sI https://alberto.codes/<name>.png`

### Rasterizing a diagram

Use a browser. ImageMagick and librsvg silently drop Mermaid's
`<foreignObject>` labels and give you empty boxes. Check first:

```bash
grep -c foreignObject src/assets/<name>.svg   # non-zero means browser-only
```

```bash
# wrapper.html: background #0f172a, svg at natural width, height auto,
# overflow visible, 40px padding
google-chrome --headless=new --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=3 --window-size=<svg-width+120>,1400 \
  --screenshot=raw.png "file://$PWD/wrapper.html"
magick raw.png -trim +repage -bordercolor '#0f172a' -border 48 \
  src/assets/<name>.png
```

Never force the SVG's height. Mermaid computes `viewBox` against fonts the
rendering machine may lack, and a fixed height clips the bottom row.

---

## Publishing notes

**Canonical URL:** `https://alberto.codes/blog/<slug>`

**Platform:** dev.to | Medium

**Tags:** *(dev.to allows 4, lowercase, no spaces. Medium allows 5.)*

**Cover image:** `https://alberto.codes/<name>.png`

**Inline images, in order of appearance:**

1. `https://alberto.codes/<name>.png` — <what it shows>

**Word count:** <canonical> → <cut>

**What this cut drops, and why:**

- <section> — <reason>

**Post-publish steps:**

- [ ] dev.to: confirm `canonical_url` rendered — the page shows a
      "Originally published at" line under the title
- [ ] Medium: set the canonical URL in story settings. There is no front
      matter for it and it is the step most often missed
- [ ] Flip `published: true` (dev.to) once the preview reads correctly
- [ ] Record the live URL below

**Published at:** <url>  **on** <date>

---

## Article

```yaml
---
title: 
published: false
description: 
tags: 
cover_image: 
canonical_url: 
---
```

> Open with the pointer line. Required by ADR-0004 decision 3:
>
> *Originally published at [alberto.codes](<canonical-url>) on <date>. That
> version is the one I keep corrected.*

<!-- Body starts here. This is a rewrite, not an export:

     - Drop internal cross-links, or make them absolute to alberto.codes
     - Drop the caveats that only matter to someone actually running it
     - Collapse tables that serve two audiences into the one that reads here
     - Keep the commands if this is a how-to. They are why the reader came
     - Reference images as the full https://alberto.codes/... URL
-->
