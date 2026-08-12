---
title: The vramfit scoreboard, in full
date: 2026-08-11
type: reference
summary: Every measured comparison behind the published 49B artifact — the instruments, the windows, the numbers, and the losses — in one lookup table.
tags:
  - quantization
  - llm
  - evaluation
  - vramfit
  - open source
---

> **DRAFT — not published.** Public-facing mirror of the project's evidence
> page. Rename to `YYYY-MM-DD-slug.md` to publish.
>
> **Open question for the maintainer:** does this post earn its place? The
> [evidence page](https://github.com/Alberto-Codes/vramfit/blob/main/docs/explanation/evaluating-packed-models.md)
> already exists, is public, and is the authoritative record. A second copy
> risks drifting out of sync — the exact failure mode the project's
> one-record rule exists to prevent. Options: (a) publish this as a stable
> snapshot with a prominent "canonical version lives here" pointer,
> (b) replace it with a short orientation post that teaches readers how to
> *read* the evidence page, or (c) drop it. **(b) looks strongest.**

## What each tier measures

| Tier | Instrument | What it answers |
|---|---|---|
| 1 | Perplexity, full WikiText-2 (564 chunks) | The community's lingua franca. Comparable to every published card. |
| 2 | KL divergence vs the f16 original | How closely does this copy track what it was made from? The project's own ranking metric. |
| 3 | Task benchmarks (MMLU, GSM8K, HellaSwag, Winogrande, ARC-C) | Does it still perform tasks at all? |

**TODO:** explain why tier 2 rules, and why perplexity on near-calibration
text measures affinity rather than fidelity — the ninth data point caught a
baseline scoring *below* the f16 reference, which is the tell.

## The publication candidate against every in-budget rival

**TODO:** reproduce the five-row table (candidate, Q3_K_S, IQ3_XS, IQ3_XXS,
UD-IQ3_XXS) with size beside quality. Size matters here: the i-quants are
0.9–2.2 GiB smaller, which is a real advantage at a tighter budget.

## The seventeen data points

**TODO:** one row each — date, what ran, verdict, what it eliminated. Keep
the losses. The elimination sequence is the point.

## Reading notes

**TODO:**
- Never rank raw damage across scans (different frames).
- Paired per-chunk tests, not interval overlap, for the KLD comparison.
- Where the receipts live and what each file is.

## TODO before publishing

- [ ] Resolve the open question above first — do not write this until then
- [ ] If it ships, add a dated "snapshot of" line and a canonical pointer
- [ ] Decide a refresh policy, or state explicitly that it is frozen
