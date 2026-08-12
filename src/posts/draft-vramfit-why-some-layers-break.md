---
title: Why some layers break and others don't
date: 2026-08-11
type: explanation
summary: Crushing a transformer isn't uniform damage. Some layer groups shrug off 2 bits and others fall apart below 6 — and which ones sit at 2 bits decides whether the damage adds up or compounds.
tags:
  - python
  - ai
  - quantization
  - llm
  - vramfit
  - open source
---

> **DRAFT — not published.** Companion to the
> [explanation post](/blog/2026-08-11-i-couldnt-tell-my-quantized-model-from-the-baseline),
> which asserts this without explaining it.
> Rename to `YYYY-MM-DD-slug.md` to publish.

## The claim the first post skipped

The first post said "not all layers damage equally" and moved on. That
sentence is doing a lot of work and deserves its own piece, because the
interesting part is not *that* it is true — it is that the pattern is not
what a rule of thumb assumes, and that the layers interact.

## What a layer group actually is

**TODO:** plain-language explanation of transformer layers and the tensors
inside one. Keep it to what a reader needs: attention projections, the
feed-forward block, embeddings, the output head. No maths.

## Measuring fragility instead of assuming it

The scan crushes one group at a time and measures how far the output
distribution moves. That number is the group's price at that precision. Do
it for every group at every candidate precision and you have a price list.

**TODO:** describe the sensitivity map concretely. Use a figure from the
published dataset — it is public, so a real chart is possible here.

**Guardrail to respect:** never rank raw damage across scans. Different
scans sit in different frames. Only relative prices within one map are
meaningful.

## The part that broke my solver: damage doesn't add

This is the piece worth the whole post.

The solver treated per-group damage as additive — crush group A, crush
group B, expect roughly the sum. Two measurements in the same frame, with
near-identical predicted totals:

| Recipe | Predicted | Measured | Direction |
|---|---|---|---|
| 42 groups at 2 bits | 0.0940 | 1.1234 | compounds, 11.9x |
| 35 groups at 2 bits | 0.0946 | 0.0589 | cancels, 1.6x |

Same predicted total. Nineteen times apart in reality. **Which groups sit at
2 bits decides whether their damage compounds** — and converged measurements
alone steered the solver back to the safe region with no interaction
modelling at all.

**TODO:** explain super- vs sub-additive in plain terms. A cooking analogy
may work: two seasonings that are fine alone and inedible together.

## Where the fragility actually lives

**TODO:** the front-stack attention story. `attn_v` in the early layers is
the tensor that collapsed, and protecting it inside layers — rather than
promoting whole layers — is what closed the gap. This is also where the
preset was quietly right: the heuristic keeps `attn_v` at higher precision
everywhere, and nobody wrote down why.

## What is still not understood

Be explicit. The exact mechanism of the 2026-07-29 destroyed artifact was
never isolated — only bounded. Knife-edge chunks move under small
perturbations. One artifact is one sample.

## TODO before publishing

- [ ] Draw the sensitivity map figure from the public dataset
- [ ] Verify every number against the evidence page
- [ ] Decide whether the additivity table needs the frame caveat spelled out
- [ ] Keep it under 1500 words
