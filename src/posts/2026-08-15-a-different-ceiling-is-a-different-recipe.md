---
title: A different ceiling is a different recipe. I finally checked.
date: 2026-08-15
type: explanation
summary: I claimed a smaller card gives you a different quantization recipe, not the same one squeezed, and then didn't prove it. Here's that claim run against the published price list — including the ceiling where the honest answer is that there's no dish.
tags:
  - python
  - ai
  - quantization
  - llm
  - vramfit
  - open source
---

Cost a braise for a forty-dollar plate and you're refining: better stock,
finish the sauce properly. Cost the same braise for twenty-eight and you're
not shaving every ingredient by thirty percent. You drop the saffron
entirely and keep the technique — a thin version of the dish is worse than a
different dish done right.

Cost it for fifteen and there's no version. The professional answer is to
say so before anyone shops.

I wrote something in [the last post](/blog/2026-08-11-i-couldnt-tell-my-quantized-model-from-the-baseline)
that I believed but hadn't checked:

> A 16 GiB card, or the same card serving twice the context, is a different
> ceiling and therefore a different recipe — not the same recipe squeezed.

Reasonable. Unproven. Only one ceiling had receipts, so I moved on. This is
me going back — and the sentence turns out to be too smooth. A different
ceiling isn't only a different recipe. Sometimes it's a question with no
answer at all.

## Why this is cheap to check

The expensive half of measuring a model is the scan. Crush one layer group
at a time, measure how far the output moves, write down the price. On a 49B
that's 37 hours.

But the scan doesn't know your card. It produces a **price list** — what
each layer group costs you at each precision — and that list is the same
whatever you plan to run it on. This is mise en place. Solving that list
against a memory ceiling is a separate step, and it takes seconds on a
laptop with no GPU.

So — one price list, three ceilings. The list is
[published](https://huggingface.co/datasets/Alberto-Codes/Llama-3_3-Nemotron-Super-49B-v1_5-sensitivity-maps),
so you can run this yourself.

## Your card's size isn't your budget

What the solver targets is what's left after the model's conversation memory
is reserved. On this model that's genuinely hard to eyeball — the attention
blocks are NAS-pruned and heterogeneous, so you can't infer the cost per
token from the parameter count.

```console
$ vramfit budget --vram 24GiB --context 16384 --model-config config.json
attention layers      49  (KV 200704 bytes/token, fp16)
VRAM total            24.00 GiB
- KV cache            3.06 GiB  (16384 tokens x 1 seq)
- runtime overhead    2.00 GiB
= weight budget       18.94 GiB
```

Three ceilings: the card I've got at the context I published against, a
smaller card, and my card serving twice the context.

![One 37-hour scan produces a price list. Solving it at three ceilings gives three different outcomes: a 24 GiB card at 16k context fits at 20.46 GiB, the same card at 32k context produces a different recipe at 17.13 GiB with 21 of 82 assignments changed, and a 16 GiB card produces no recipe at all because the smallest possible arrangement is 15.31 GiB against a 12.47 GiB budget.](/vramfit-three-ceilings.svg)

## What came back

|  | A: 24 GiB, 16k | B: 16 GiB, 16k | C: 24 GiB, 32k |
|---|---|---|---|
| weight budget | 20.47 GiB | 12.47 GiB | 17.41 GiB |
| recipe | 20.46 GiB | **none exists** | 17.13 GiB |
| predicted damage | 0.1215 | — | 0.2212 |
| bits used | 56x2, 13x3, 8x4, 5x8 | — | 71x2, 4x3, 6x4, 1x8 |

Column A reproduces the recipe I shipped, to the fourth decimal of predicted
damage — that is the control. Without it the other two columns are just
numbers I generated.

## The most useful column is the empty one

A 16 GiB card can't run this model. Not "runs badly." There is no recipe:

```text
error: no recipe fits the 12.47 GiB weight budget
       — minimum achievable is 15.31 GiB (2.85 GiB over)
```

This is the part I didn't anticipate when I wrote the original line.

A preset can't tell you this. Presets are fixed rules — you browse file
sizes, find one under your number, download it. It will load. Whether the
thing inside still works is something you discover later — subjectively, over
days of it being slightly off.

The solver's answer is arithmetic. Here is the smallest arrangement this
price list permits, here is your budget, the first is bigger by 2.85 GiB. One
command, no download.

Being told no quickly is most of what I want from a tool that costs 37 hours
when the answer is yes.

If that's your card, you have three real options and the tool won't pick for
you. Run a smaller model — a 27B or 32B at these precisions fits 16 GiB
comfortably. Rent a bigger card for the work that needs this one. Or accept
partial offload and a much slower model, which llama.cpp will do and vramfit
doesn't plan for. What you shouldn't do is download a preset that fits and
assume the fit means it works.

## What actually changed between A and C

Same card, twice the context. My claim was "a different recipe, not the same
recipe squeezed." The data says both, and neither.

- **21 of 82 assignments differ.** 61 are identical. So it is not a different
  recipe. It is also not the same one.
- **The level drops**, as you'd expect: 56 groups at 2-bit becomes 71.
- **The shape changes**, which I didn't expect. Of the 13 groups holding
  4-bit or better at 16k, only 7 keep it. The biggest mover is the embedding
  table, which falls from **8-bit to 3-bit**. It is the largest single object
  on the card, and the solver sells it to keep the layers alive. Layers 76
  through 78, the deepest three, drop from 4-bit to 2-bit together.

There is the saffron. At the tighter ceiling the solver doesn't shave
everything down a notch — it re-decides what's worth protecting at all, and
the first thing it gives up is the most expensive item on the counter.

I'd have guessed the opposite. I'd have guessed it protects the big table
and squeezes the many small layers, because that is what "make it smaller"
feels like it should mean. The measurement disagrees, and the measurement
has receipts.

## What a preset user does at each ceiling

This is what decides whether any of it is worth an afternoon.

At **A**, presets are fine. Honestly. `Q3_K_S` is 20.45 GiB against a
20.47 GiB budget — it fits with 20 MiB to spare, and the measured recipe
beats it by a margin you need instruments to see. That was the whole subject
of the last post.

At **C** the shelf runs out. Every published preset I measured for this model
overflows a 17.41 GiB budget. The smallest, `IQ3_XXS`, is 18.18 GiB and
misses by 0.77 GiB. So you take the next one down and wear the gap — at these
sizes, most of a bit per weight.

At **B** nothing works — and you learn it in one command instead of after a
download.

The pattern is simple enough: the further your real ceiling sits from the
sizes the shelf happens to stock, the more measuring pays. If your budget
lands on a preset, take the preset.

## One caveat, and it's the honest kind

Column C only exists because that solve was allowed to use 2-bit.

The artifact I published was planned on a price list with the 2-bit column
removed, under a rule that bars 2-bit until it's been priced in the runtime
rather than in the measurement frame
([ADR-0021](https://github.com/Alberto-Codes/vramfit/blob/main/docs/adr/0021-runtime-frame-measurement.md)
decision 4). On that list **both** B and C are infeasible — the floor is
20.06 GiB, and 32k of context leaves 17.41 GiB.

So under the policy the shipped artifact was actually built with, this model
serves 16k of context on a 24 GiB card and nothing else. Doubling the
context isn't a tuning exercise. It is a question about whether you trust
2-bit, and on a different model that question has since been measured and
answered no, at 4.1 times the reference perplexity.

I'd rather show you the column and tell you what it costs than quietly plan
with a width I've argued against everywhere else.

## What I'd say now

The original sentence wasn't wrong — it was underspecified in a way that hid
the good part.

"A different ceiling is a different recipe" sounds smooth — turn the dial,
get a different answer. What happens is that a quarter of the assignments
move, the solver's priorities reorder, and at some point the dial runs out
of travel and the honest output is an error message.

If I were writing that line again: **a different ceiling is a different
question, and sometimes it has no answer.**

---

*Part of a series on measuring quantization damage. Start with
[I couldn't tell my quantized model from the baseline](/blog/2026-08-11-i-couldnt-tell-my-quantized-model-from-the-baseline),
which is where the idea comes from. If you want to run this yourself,
[the walkthrough](/blog/2026-08-15-fit-a-model-to-the-gpu-you-actually-have)
takes the whole pipeline from install to a packed file. The full scoreboard
behind these numbers is still coming.*
