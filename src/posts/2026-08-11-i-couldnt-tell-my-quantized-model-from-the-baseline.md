---
title: I couldn't tell my quantized model from the baseline. The instruments could.
date: 2026-08-11
type: explanation
summary: I shrank a 93 GB model onto a 24 GB card by measuring which layers survive being crushed, instead of guessing. Then I couldn't tell the result from the standard quant by talking to it — which turns out to be the whole point.
tags:
  - python
  - ai
  - quantization
  - llm
  - evaluation
  - vramfit
  - open source
---

I asked two compressed copies of the same model fifteen questions each. Same questions, same settings, no randomness.

They scored **19 out of 25. Both of them.** And they didn't just tie — they *agreed*. Both got the same four facts wrong. Both wrote the same function with the same bug in it. One file was mine, built by measuring the model layer by layer. The other was the standard off-the-shelf quantization at that size, [bartowski's Q3_K_S](https://huggingface.co/bartowski/nvidia_Llama-3_3-Nemotron-Super-49B-v1_5-GGUF).

Chat with both and you'd find nothing, and conclude my work bought nothing.

It bought something. You just can't get at it by chatting — and why not is worth more than the result.

## The problem, if you've never met it

Nemotron Super 49B is about **93 GB** at full precision. An RTX 4090, a very good consumer card, has **24 GB**. The model has to fit entirely inside that to run well.

So you compress it. The weights are billions of numbers stored at 16 bits each; store them at 4 bits, or 3, and the file shrinks. That's quantization, and it's why you can run useful models at home at all.

The catch: crushing the numbers damages the model, and **not all parts damage equally.** Most layers take 3 bits without complaining. A few — the value projections at the front of the stack, and the very first block — need more, and crushing those degrades the whole thing in ways the file size never warns you about.

Here's what surprised me. Essentially every GGUF you can download picks precision from a small family of **presets** — fixed rules that branch on a few architectural details, but never measure *this* model's fragility or solve against *your* memory ceiling. (Some other formats do measure. EXL2 runs a per-layer error pass, though it targets an average bit rate rather than a hard VRAM budget.)

Those presets are your abuelita's recipe. A handful of this, cook it till it looks right. They genuinely work, they're the product of real craft, and the reasons they work were never written down — nobody checks the rule against the model in front of them, because the rule has always been good enough.

I wanted the America's Test Kitchen version. Same dish, weighed in grams, tested in kitchens that aren't hers, with the steps that matter separated from the ones that don't. Not a better rule. **No rule at all.**

## What compression actually takes away

One idea about how these models work explains everything else. It's the only technical thing in this post.

**A language model doesn't produce a word. It produces a probability distribution over every possible next word.** Tens of thousands of candidates, each with a score. "The capital of France is ___" might come out as *Paris* 94%, *the* 2%, *a* 1%, and a long tail of everything else. Only then does something pick one.

![Two probability curves over possible next words. Both peak on the same top word, so greedy decoding picks identically from either. Behind the peak the curves separate — that difference is what KL divergence measures.](/vramfit-distribution-shoulders.svg)

Now the trap is obvious. My fifteen questions used greedy decoding — always take the highest-scoring word. That reads **only the tip of the peak.** Two copies can agree on the top word often enough that fifteen questions cannot separate them, while the shape behind it has drifted.

Conversation samples the peak. Damage lives in the shoulders.

The instrument that sees the shoulders is **KL divergence** — how much two probability shapes differ. Point it at the original and a compressed copy across hundreds of pages, and you get one honest number: how far did this copy drift from what it was made from?

That's the number I optimize. Not vibes, and not a preset.

## Measure, then solve

[vramfit](https://github.com/Alberto-Codes/vramfit) crushes one layer group at a time to build a price list for this specific model, solves that against your memory ceiling, checks the real damage against its own prediction, and only then builds the file.

![Four steps. Scan produces a per-layer price list, plan turns it into a recipe under a memory ceiling, validate checks the real damage against the prediction and sends failures back to the solver, and pack builds the file.](/vramfit-pipeline.svg)

The output isn't a preset. It's a recipe fitted to one model and one card — and the "one card" part is where this really differs.

Your card's size is not your budget. A 24 GiB card doesn't give you 24 GiB for weights: the model also needs room for the conversation it's holding, and reserving 16k of context left me **20.47 GiB**. That remainder is what the solver targets, to the byte.

![A 24 GiB card split into 20.47 GiB for weights and 3.53 GiB reserved for 16k of context. The remainder is what the solver targets, and a different card or a longer context moves the line.](/vramfit-budget.svg)

A 16 GiB card, or the same card serving twice the context, is a different ceiling and therefore a different recipe — not the same recipe squeezed. With presets you browse fixed sizes and take whichever fits under your number, wearing whatever gap is left over. Here the number goes in the front.

At the same file size, the measured recipe drifts **less** from the original — a 2.9% smaller gap, tiny-sounding but far outside the measurement noise. It also beats the three i-quants that fit the same budget, and ties the baseline on five capability benchmarks, so the closer fit costs nothing the benchmarks can see.

There's a sharper payoff than a better average. An earlier candidate of mine passed every check and looked clean — until a page-by-page comparison found one page out of 564 where it fell off a cliff, diverging **more than fifty times** worse than the baseline on that text. One page, and nothing had flagged it. The published artifact is the first with no such page anywhere in the 564.

That's the foolproof part, and the real return on weighing your ingredients. Not a better score — a **known shape.**

## The part nobody publishes

Here's what I actually think the edge is, and it isn't the 2.9%.

### Five losses, and what each one bought

Before that recipe won, **it lost five times.**

| Full-loop attempt | Date | Result |
|---|---|---|
| First real attempt | 2026-07-29 | **Lost** — badly |
| Rematch, handicap removed | 2026-07-29 | **Lost again**, by less, for a different reason |
| Better-converged measurements | 2026-07-31 | **Lost** |
| More honest price list | 2026-08-02 | **Lost** |
| Most honest price list yet | 2026-08-06 | **Lost by the most** since the handicaps came off |
| Ban the most aggressive setting | 2026-08-06 | Tie on one metric, behind on the other |
| Pipeline builds its own winner | 2026-08-09 | **Won** |

Those are the full-loop runs. Several hand-built probes in between are left out, and several of those lost too.

Read the table as a diagnosis, not a confession — each loss eliminated a suspect. The first proved most of my deficit came from a weighting file the competition used and I didn't, not from my recipe at all. The second proved damage doesn't simply add up: crushing two layers together can hurt far more than crushing each alone, which broke an assumption at the center of my solver. The fifth killed my favorite theory — three rounds of better measurements produced three steps backwards, because the frame I measured in and the frame I shipped in disagreed.

Each loss was me finding a step nobody had written down. The weighting file and the way damage compounds were both things the preset had been quietly getting right for years without anybody saying so — the pinch of salt your abuelita never mentions because her hand does it automatically. The difference between an accident and a technique is whether somebody writes it down.

### The recipe I did not expect

I assumed measuring would produce something exotic — a wild, uneven allocation no rule of thumb would ever guess. It did, and those were the recipes that lost.

![Three bit allocations across 82 layer groups. The preset is a flat 3-bit band. My first attempt is jagged, with 38 groups pushed down to 2-bit, and it lost. The winner is almost flat 3-bit like the preset, with one group at 8-bit, plus a hatched strip marking one tensor kept at higher precision inside 47 of the layers.](/vramfit-recipe-shapes.svg)

Given honest prices, the solver walked back to almost exactly the shape the preset already had. Your abuelita was right about the dish. What the measurement found was the one step she never mentioned — a single tensor inside the layers, kept at higher precision, in 47 places. That strip is the entire difference between what I published and what everyone downloads.

So I didn't beat the preset by out-thinking it. I beat it by finding the one thing it was missing, and only after five losses told me where not to look. Tracking that down meant working out why the same tensor was fitted ten times worse in my files than in the competition's. I suspected my settings, then my toolchain version. Both innocent. The real cause was upstream and subtle, in how the compression maths behaves when the weighting file has extreme values. Not my bug — but mine to find.

### Why the losses are public

Every one of those losses is dated and numbered, with its receipts. Seventeen data points. Architecture decision records for the choices, an issue trail for the arguments, provenance and evaluation sidecars on the published files.

I don't think that's normal, and I think it should be. The going standard for a published quantized model is a checksum, a file size, and sometimes a single quality number. A checksum proves the file is the file. It proves nothing about whether the file is any good — and nothing about the five artifacts that didn't make it.

Weigh the ingredients. Write down the voyage.

## What I'm still not claiming

**The winning run was not a cold solve.** By the time the pipeline built the published artifact, I had hand-discovered three things and handed them to it as inputs: ban the most aggressive setting, protect one tensor across 47 layers, exclude four tensors from the weighting file. The solver reproduced the rest of the layout and made one forced trade of its own. "Measure instead of guessing" is true. "The machine worked it out by itself" is not — the measurements found those rules across five losing attempts, but a human read the measurements.

The baseline beats me on one metric — how often the top word matches the original — by half a point, and that has never flipped. I let KL carry the ranking anyway, because the top word is a one-bit summary that ignores how wrong the model is when it misses, while KL weights the whole shape. If you always decode greedily, take that half point seriously. If you sample, take the KL.

And one control was missing when I first published this. When both models got the same four facts wrong, the natural reading is that the mistakes come from the original rather than from either compression. Natural isn't measured. The 93 GB original had never answered those fifteen questions, because it doesn't fit the card. I said so here, [tracked it in the open](https://github.com/Alberto-Codes/vramfit/issues/143), and said that if the original got them *right*, that would be more interesting than the result I had.

**It got them wrong.** I ran it the same night. **93 GB** still doesn't fit **24 GB**, so most of the model ran on the CPU — about one word every three or four seconds, thirty-five minutes for fifteen answers. It missed the same four facts. It wrote the same function with the same bug, under the same comment promising it had avoided that exact bug. The mistakes come from the original. Neither compression caused them.

The original scored **20 out of 25** — one point above both copies. Each compression gave up exactly one further point, and they turned out to be the two points that already separated the copies from each other: one flubbed a size parser, the other expanded an acronym wrong. The original got both right.

One point is not nothing, and I won't round it to zero. Compression may have cost each copy that point. Fifteen questions, asked once, cannot tell you whether it did — one point out of twenty-five sits inside what the choice of questions alone can move. That's the same weakness that made the 19-19 tie a weak result, and it cuts the same way in both directions. The conversation can't see the difference. The measurement can.

I'd rather publish the gap named than the story clean. Naming it is also what made it cheap to close.

## Where it lives

- **The tool:** [vramfit](https://github.com/Alberto-Codes/vramfit) — scan, plan, validate, pack. MIT.
- **The model:** [the packed 49B](https://huggingface.co/Alberto-Codes/Llama-3_3-Nemotron-Super-49B-v1_5-fit24gib-GGUF) — a quantization of [NVIDIA's Nemotron Super 49B v1_5](https://huggingface.co/nvidia/Llama-3_3-Nemotron-Super-49B-v1_5), under the NVIDIA Open Model License. Built with Llama.
- **The measurements:** the [sensitivity-map dataset](https://huggingface.co/datasets/Alberto-Codes/Llama-3_3-Nemotron-Super-49B-v1_5-sensitivity-maps) — the per-layer price list the recipe was solved from.
- **The full ledger:** [all seventeen data points](https://github.com/Alberto-Codes/vramfit/blob/main/docs/explanation/evaluating-packed-models.md), every number and every loss.

Coming next: how to fit a model to the card you actually have, and why some layers break and others don't. It's also the second time I've come at quantization from the measurement end — the [first was TurboQuant on a vision model](/blog/2026-03-26-i-ran-turboquant-on-a-vision-model-the-first-output-was-garbage), where the first output was garbage for a reason no benchmark would have told me.
