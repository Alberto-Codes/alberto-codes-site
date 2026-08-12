---
title: Fit a model to the GPU you actually have
date: 2026-08-11
type: how-to
summary: Measure a model's per-layer quantization damage, solve for a recipe that fits your card, and check the result before you trust it.
tags:
  - python
  - ai
  - quantization
  - llm
  - vramfit
  - open source
---

> **DRAFT — not published.** Sequel to the [explanation post](/blog/2026-08-11-i-couldnt-tell-my-quantized-model-from-the-baseline).
> Rename to `YYYY-MM-DD-slug.md` to publish. Do not ship until every command
> below has been run start to finish on a clean machine.

## Who this is for

You have a GPU with a fixed amount of memory. You want to run a model that
does not fit. You have already tried an off-the-shelf quantization and want
one fitted to your card instead of to the average card.

Assumed: comfortable with a terminal, `uv` installed, a CUDA GPU. Not
assumed: any quantization background — that is the
[explanation post](/blog/2026-08-11-i-couldnt-tell-my-quantized-model-from-the-baseline).

## Before you start

**TODO — verify each of these on a clean machine before publishing:**

- Install line and the extras split. Base install is typer + structlog only;
  `scan` and `pack` need extras (ADR-0005). Confirm exact extra names.
- llama.cpp build requirement for the pack step. The reference box uses a
  Vulkan build; state the minimum and how to point `--llama-cpp` at it.
- Disk needed. The scan writes a sensitivity map; the pack writes a
  ~20 GB artifact. State real figures.
- Time. The 49B scan took roughly a day on a 4090. State the honest number
  and give a small-model example that finishes in minutes.

## 1. Work out your real budget

The number that matters is not your card's size. It is your card's size
minus what the KV cache will need at the context length you plan to serve.

**TODO:** `vramfit budget` invocation and worked example. Show the 24 GiB
card → 20.47 GiB weight budget arithmetic from the acceptance target, since
that is the one with a public receipt.

**The centrepiece this post owes the reader — run it for real.** The
explanation post asserts that a different ceiling produces a different
recipe and stops there, because only the 24 GiB budget has measured
receipts. This post is where that gets demonstrated instead of claimed.

Plan the *same* sensitivity map at three budgets — a 24 GiB card, a 16 GiB
card, and the 24 GiB card serving 32k of context instead of 16k — and show
the three recipes side by side. Points to bring out:

- How many group assignments actually differ between them.
- Whether the solver's *shape* changes or only its level.
- What the preset user's alternative is at each ceiling: which stock quant
  they would have to pick, and how many bytes they leave on the table.

Planning is cheap — no scan, no pack, no GPU hours. Three solves against one
map. **Do not draw this from imagination; it is exactly the claim the
explanation post declined to make without data.**

## 2. Scan

Quantize one layer group at a time, measure how far the output distribution
moves, write the per-layer price list.

**TODO:** the `vramfit scan` command, what the calibration file should be,
and how long to expect. Cover the memory cap and `expandable_segments` — the
49B scan OOMs at 17 GiB and runs at 15 GiB.

**Callout worth keeping:** calibration length matters. 8k tokens was a pilot
that had not converged — re-planning the same budget on a 32k map flipped 41
of 82 assignments. 32k suffices at 3-bit and above.

## 3. Plan

**TODO:** the `vramfit plan` command. Explain `--protect` and
`--exclude-imatrix` in plain terms, since they are what closed the gap.

## 4. Pack

**TODO:** the `vramfit pack` command with `--imatrix`. Say clearly that the
importance matrix is not optional at 3-bit — it was ~81% of the original
deficit.

## 5. Check it before you trust it

Non-negotiable, and the reason is a real incident: a recipe once predicted
damage 1.44 and the packed artifact was **destroyed** — perplexity around
10⁶, top-token agreement 0.3%. Nothing between plan and pack would have
caught it.

**TODO:** the smoke test and the reconstruction check, and how to read them.

## When this is the wrong tool

Be honest here. Off-the-shelf quantizations are good, they are free, and they
are one download. This is worth it when your budget is unusual, when you need
to know the artifact has no cliffs, or when you want the evidence.

## TODO before publishing

- [ ] Run every command on a clean machine and paste real output
- [ ] Pick a small model so a reader can finish in under an hour
- [ ] Confirm all flags against `vramfit --help` at the released version
- [ ] Cross-link the explanation post and the sensitivity post
