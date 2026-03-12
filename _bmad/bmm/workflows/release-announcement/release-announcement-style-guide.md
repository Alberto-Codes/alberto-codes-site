# Release Announcement Style Guide

Self-contained voice, format, and template rules for every Alberto-Codes release announcement platform. A fresh agent should need nothing else to run the workflow. Do not consult the design brief or any external planning document — everything needed is in this file.

---

## Voice Principles

These five principles apply to every platform. All drafts start here.

1. **Lead with the problem, not the version number.** Nobody cares about v1.2.0. They care about what they can do now that they couldn't do before.
2. **Show, don't list.** Code examples beat bullet points. Before/after beats feature names.
3. **Be honest about tradeoffs.** Acknowledging limitations builds trust faster than cheerleading.
4. **One release, one narrative.** Every platform tells the same story in its native language — distilled, not copy-pasted.
5. **End with forward motion.** What's coming next gives readers a reason to stay engaged.

---

## LinkedIn

**Audience:** Engineering managers, peers, collaborators
**Length:** ~1300 characters
**Tone:** Direct, technical, respects reader's intelligence

### Voice Rules

- Open with a concrete insight or counter-intuitive statement — no warm-up, no "Excited to announce."
- Problem-first: establish the pain before the solution
- Short paragraphs (2–3 sentences max)
- URL-only CTA — just the raw link, no "click here"
- 4 hashtags maximum, no more
- Food/cooking metaphor is a personal brand element — use it when it fits naturally, never force it
- Version numbers never appear in the opener

### Confirmed Real Example (authoritative voice reference)

```
Duplicates aren't a bug — they're a feature of your queue.

If you're building AI pipelines with task queues, you've probably accepted at-least-once
delivery. What you might not have accepted yet: that means your pipeline will process the
same task more than once.

Worker crashes, visibility timeouts, late acks — all of them produce duplicates. And in AI
pipelines, duplicates aren't just an inconvenience. They're wasted tokens, redundant API
calls, and inflated invoices.

The fix is straightforward: idempotency keys at each stage. A few lines of code that check
"did I already do this?" before firing an expensive embedding or extraction call.

I wrote up the full explanation — how duplicates happen, why dead-letter queues protect
throughput, and why retries cost more when LLMs are involved.

https://alberto.codes/blog/2026-02-02-task-queues-idempotency-and-ai-pipelines

#DistributedSystems #AIEngineering #TaskQueues #Python
```

Key observations from this example: direct hook as first line, problem established in sentences 2-3, solution named concisely, URL as the only CTA, 4 hashtags, no food metaphor (used selectively). Match this energy.

### Fuzzy Template

```
[Hook — surprising, relatable, or counter-intuitive statement. 1-2 sentences.]

[Problem context — why this matters to the reader. 2-3 sentences.]

[Solution — what shipped and why it matters. 1-2 short paragraphs.]

[CTA — raw URL to blog post only]

#Hashtag1 #Hashtag2 #Hashtag3 #Hashtag4
```

### Anti-Patterns

- Feature dump bullet lists
- "Excited to announce" or similar warm-up phrases
- Version number in opener
- 5+ hashtags
- "Click here" or "Check it out" before the link

---

## X / Twitter

**Audience:** Developer community, fast-scrolling
**Length:** Thread of 3–5 tweets
**Tone:** Bold, confident, no hedging

### Voice Rules

- Tweet 1 must stand alone as a complete thought — hook without the thread
- Bold statement or question that creates curiosity
- Max 5 tweets — if you need more, the story isn't focused enough
- Link only in the last tweet (CTA tweet)
- 2–3 hashtags in CTA tweet only

### Fuzzy Template

```
🧵 Tweet 1 (Hook): [Bold statement or provocative question. Standalone. No link.]

Tweet 2 (Show): [Key feature or change. 1-2 sentences. Code snippet if it fits 280 chars.]

Tweet 3 (Depth): [One design decision or tradeoff. Why you built it this way.]

Tweet 4 (CTA): [Link to blog post + 2-3 hashtags]
```

### Anti-Patterns

- "1/ " opener without an actual hook
- Threads longer than 5 tweets
- Links in every tweet
- Passive voice or hedging ("might", "could possibly")

---

## dev.to

**Audience:** Developers actively learning
**Length:** 800–1200 words
**Tone:** Technical depth with accessibility. Honest about limitations.

### Voice Rules

- `canonical_url` pointing to alberto.codes is required — never publish without it
- Cross-link to docs and GitHub
- Lead with the problem, include real code examples
- Don't bury the install command — surface it early
- Max 4 tags in frontmatter

### Frontmatter Template

```yaml
---
title: [Action-oriented or "Why we..." framing — not just "v1.2.0 Released"]
published: true
tags: [python, relevant, topic, tags]
description: [One-line hook for previews]
canonical_url: https://alberto.codes/blog/{slug}
---
```

### Section Structure

```markdown
[Hook — what problem does this release solve?]

## What Changed
[Feature walkthrough with real code examples]

## Why This Design
[Architecture decisions, tradeoffs, alternatives rejected]

## Getting Started
[pip install command + minimal working example]

## What's Next
[2-3 roadmap bullets]

---
*[PyPI](link) | [Docs](link) | [GitHub](link)*
```

### Anti-Patterns

- Pasting the raw changelog
- No code examples
- Burying the install command at the end
- Missing `canonical_url`
- More than 4 tags

---

## GitHub Discussion

**Audience:** Existing users and contributors
**Length:** 150–400 words
**Tone:** Community-first. Match the voice of the target repo's prior discussions.

### Voice Rules

- Check Step 1d discovery output for this repo's existing discussion voice before drafting
- Install/upgrade command must be present
- Link to full changelog
- For breaking changes: before/after code is required

### Fuzzy Template

~~~markdown
## [Project] v[X.Y.Z]

[1-2 sentence narrative summary — what changed and why it matters]

### Highlights
- **[Feature]** — [one-line impact for users]
- **[Feature]** — [one-line impact for users]

### Breaking Changes *(if applicable)*
[Before/after code block]

### Install / Upgrade
```
pip install project==X.Y.Z
```

### What's Next
[1-2 bullets on near-term roadmap]

**Full changelog:** [link]
~~~

### Anti-Patterns

- Walls of text with no structure
- Missing install command
- No changelog link
- Ignoring the voice of existing repo discussions

---

## alberto.codes Blog

**Audience:** Professional audience following your work
**Length:** 1000–1500 words
**Tone:** Most authentic voice — conversational, opinionated, shows tradeoffs honestly
**Output:** `src/posts/YYYY-MM-DD-{slug}.md`

### Voice Rules

- Every post declares a Diataxis type — never "mixed" or undefined
- One release can produce multiple posts if the content naturally splits (e.g., a "why we built it" + a "how to use it" guide)
- All five frontmatter fields are required: `title`, `date`, `type`, `summary`, `tags`
- `type` must be one of: `explanation`, `how-to`, `tutorial`, `reference`

### Frontmatter Schema

```yaml
---
title: [Descriptive — not just "v1.2.0 Released"]
date: YYYY-MM-DD
type: explanation|how-to|tutorial|reference
summary: [One-line hook]
tags:
  - project-name
  - python
  - relevant-topic
---
```

### Diataxis Type Selection

| Release Content | Diataxis Type | Example Title Pattern |
|---|---|---|
| New feature with "why" story | `explanation` | "Why [Project] Needed [Feature]" |
| New API or usage pattern | `how-to` | "How to [Do Thing] with [Project]" |
| Milestone release (v1.0, v2.0) | `tutorial` | "Build [X] in [N] Minutes with [Project]" |
| Benchmarks, specs, comparisons | `reference` | "[Project] [Feature] Comparison" |

### Section Structure by Type

| Type | Sections |
|---|---|
| `explanation` | What We Built → Design Decisions → Who This Is For |
| `how-to` | Prerequisites → Steps → Verification → Troubleshooting |
| `tutorial` | What You'll Build → Setup → Step-by-step → What You Learned |
| `reference` | Overview → Comparison Table → Specifications → API Surface |

### Anti-Patterns

- Pasting the raw changelog as the post body
- No code examples
- Tutorial that doesn't guarantee success if followed exactly
- Missing any of the five required frontmatter fields

---

## Cross-Platform Coordination

### Content Flow

All platforms tell the same story — distilled, not copy-pasted:

```
Blog (canonical) → dev.to (canonical_url points back) → LinkedIn (distilled) → X (punchy) → GitHub Discussion (community)
```

### Canonical URL Construction

1. Blog post slug = `YYYY-MM-DD-{title-in-kebab-case}` (derived from `date` + `title`)
2. Canonical URL = `https://alberto.codes/blog/{slug}`
3. This URL is locked at the end of Step 3 and passed to Step 4 (dev.to) for `canonical_url` frontmatter

**Example:** A post titled "Why docvet Needed CLI-First Design" published 2026-03-08 → slug: `2026-03-08-why-docvet-needed-cli-first-design` → canonical: `https://alberto.codes/blog/2026-03-08-why-docvet-needed-cli-first-design`

### Blog Slug Derivation Rule

- Lowercase the title
- Replace spaces with hyphens
- Strip punctuation except hyphens
- Prepend the publish date: `YYYY-MM-DD-{slug}`

---

## Party Mode Agent Selection

When invoking party mode per platform, the SM channels the agents listed below — maintaining their personas inline within the response, not as a literal slash command.

| Platform | Agents | Why |
|---|---|---|
| Blog (explanation) | Architect + Tech Writer | Architecture narrative + clarity |
| Blog (how-to) | Dev + Tech Writer | Code accuracy + step structure |
| Blog (tutorial) | Dev + Tech Writer | Working examples + progressive disclosure |
| Blog (reference) | Dev + Architect | Specs + design decisions |
| dev.to | Dev + Tech Writer | Code depth + accessibility |
| LinkedIn | PM + Architect | Value proposition + credibility |
| X/Twitter | Quick Flow Solo Dev + Storyteller | Punchy + narrative arc |
| GitHub Discussion | SM + PM | Community voice + roadmap context |

---

## Sister Project Voice Reference

Use these patterns when drafting GitHub Discussions and tailoring tone for each repo.

### docvet — Discovery & Accessibility

- 13 announcements — most sophisticated discussion voice
- Every feature gets: context → code example → user impact → install command → links
- Pattern: problem → feature → impact → install → links
- Audience expects detailed technical context, not just a changelog

### adk-secure-sessions — Architecture & Trust

- 2 announcements — longer-form architecture narratives
- Pattern: what changed → what didn't change → SECURITY.md link
- Audience cares about trust boundaries and backward compatibility

### gepa-adk — Concise & Technical

- 2 announcements — minimal prose, maximum signal
- Emoji categories for sections (✨ Features, 🐛 Fixes, ⚠️ Breaking)
- Breaking changes front-and-center, install command prominent
- Pattern: highlights → breaking changes → install → changelog link
