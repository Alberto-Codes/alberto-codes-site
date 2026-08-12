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

They scored **19 out of 25. Both of them.** And they didn't just tie — they *agreed*. Both got the same four facts wrong. Both wrote the same function with the same bug in it. One of those two files was mine, built by measuring the model layer by layer. The other was the standard off-the-shelf quantization at that size — [bartowski's Q3_K_S](https://huggingface.co/bartowski/nvidia_Llama-3_3-Nemotron-Super-49B-v1_5-GGUF), from a repo with far more users than mine will ever have.

If you chatted with both, you would find nothing, and you would conclude my work bought nothing.

It bought something. You just can't get at it by chatting — and understanding why is worth more than the result itself.

## The problem, if you've never met it

Large language models are big. Nemotron Super 49B — the one I care about — is about **93 GB** at full precision. A very good consumer graphics card, an RTX 4090, has **24 GB** of memory. The model has to fit entirely in there to run well.

So you compress it. The weights are billions of numbers stored at 16 bits each; store them at 4 bits, or 3, and the file shrinks. This is called quantization, and it's why you can run useful models at home at all.

The catch: crushing the numbers damages the model, and **not all parts damage equally.** Most layers take 3 bits without complaining. A few — the value projections in the front of the stack, and the very first block — need more, and if you crush those the whole thing degrades in ways the file size never warns you about.

Here's the part that surprised me when I started. Essentially every GGUF you can download — the format most people run at home — picks precision from a small family of **presets**. The presets branch on a few architectural details, but none of them measure *this* model's fragility, and none of them solve against *your* memory ceiling. (Other formats do measure: EXL2 runs a per-layer error pass before choosing. It targets an average bit rate rather than a hard VRAM budget, which is a different question from the one I had.)

Those presets are your abuelita's recipe. A handful of this, cook it till it looks right. They genuinely work, they're the product of real craft and years of taste, and the reasons they work were never written down. Nobody checks whether the rule is right *for the specific model in front of them*, because the rule has always been good enough.

What I wanted was the America's Test Kitchen version. Same dish, but weighed in grams, tested in kitchens that aren't hers, with the steps that actually matter separated from the ones that don't. Not a better rule. **No rule at all** — measure this model, solve for this budget, write down what you find.

## What compression actually takes away

To see why chatting can't find the difference, you need one idea about how these models work. It's the only technical thing in this post, and it's worth the two minutes.

**A language model doesn't produce a word. It produces a probability distribution over every possible next word.** Tens of thousands of candidates, each with a score. "The capital of France is ___" might come out as *Paris* 94%, *the* 2%, *a* 1%, and a long tail of everything else. Only then does something pick one.

![Two probability curves over possible next words. Both peak on the same top word, so greedy decoding picks identically from either. Behind the peak the curves separate — that difference is what KL divergence measures.](/vramfit-distribution-shoulders.svg)

Now the trap becomes obvious. When I ran my fifteen questions, I used greedy decoding — always take the single highest-scoring word. That reads **only the tip of the peak.** Two copies of a model can agree on the top word often enough that fifteen questions cannot separate them, while the shape behind it has drifted noticeably.

Conversation samples the peak. Damage lives in the shoulders.

The instrument that sees the shoulders is **KL divergence** — a standard measure of how much two probability shapes differ. Point it at the original 93 GB model and a compressed copy, run it across hundreds of pages of text, and you get a single honest number: how far did this copy drift from what it was made from?

That is the number I optimize. Not vibes, and not a preset.

## Measure, then solve

The tool is called [vramfit](https://github.com/Alberto-Codes/vramfit). It crushes one layer group at a time to build a price list for this specific model, solves that against your memory ceiling, checks the real damage against its own prediction, and only then builds the file.

![Four steps. Scan produces a per-layer price list, plan turns it into a recipe under a memory ceiling, validate checks the real damage against the prediction and sends failures back to the solver, and pack builds the file.](/vramfit-pipeline.svg)

The output isn't a preset. It's a recipe fitted to one model and one card — change the budget and you get a different answer, because the arithmetic changes.

At the same file size, the measured recipe drifts **less** from the original — a 2.9% smaller gap, which sounds tiny but sits far outside the measurement noise. It also beats the three i-quants that fit the same budget, and ties the baseline on five capability benchmarks, so the closer fit costs nothing the benchmarks can see.

There's a sharper payoff than a better average, though. An earlier candidate of mine passed every check and looked clean — until a page-by-page comparison found a single page out of 564 where it fell off a cliff, diverging **more than fifty times** worse than the baseline on that one text. One page, and nothing had flagged it. The published artifact is the first with no such page anywhere in the 564.

That's the foolproof part, and it's the real return on weighing your ingredients. Not a better score — a **known shape.**

## The part nobody publishes

Here's what I actually think the edge is, and it isn't the 2.9%.

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

Read that table as a diagnosis, not a confession. Each loss eliminated a suspect. The first proved most of my deficit came from a weighting file the competition used and I didn't — not from my recipe at all. The second proved that damage doesn't simply add up: crushing two layers together can hurt far more than crushing each alone, which broke an assumption sitting at the center of my solver. The fifth killed my favorite theory outright — three rounds of better measurements produced three steps backwards, because the frame I measured in and the frame I shipped in disagreed.

Every one of those losses was me finding a step nobody had written down. The weighting file and the way damage compounds were both things the preset had been quietly getting right for years without anybody saying so — the equivalent of the pinch of salt your abuelita never mentions because her hand does it automatically. The difference between an accident and a technique is whether somebody writes it down.

Here is the part I did not see coming. I assumed measuring would produce something exotic — a wild, uneven allocation that no rule of thumb would ever guess. It did, and those were the recipes that lost.

![Three bit allocations across 82 layer groups. The preset is a flat 3-bit band. My first attempt is jagged, with 38 groups pushed down to 2-bit, and it lost. The winner is almost flat 3-bit like the preset, with one group at 8-bit, plus a hatched strip marking one tensor kept at higher precision inside 47 of the layers.](/vramfit-recipe-shapes.svg)

Given honest prices, the solver walked back to almost exactly the shape the preset already had. Your abuelita was right about the dish. What the measurement found was one step she never mentioned — a single tensor inside the layers, kept at higher precision, in 47 places. That strip is the entire difference between the artifact I published and the one everyone downloads.

Which reframes the whole exercise. I did not beat the preset by out-thinking it. I beat it by finding the one thing it was missing, and I only found that after five losses told me where not to look.

The win, when it came, wasn't a cleverer solve. It was tracking down why that same tensor, in the layers at the front of the stack, was fitted ten times worse in my files than in the competition's. I suspected my settings, then my toolchain version. Both innocent. The real cause was upstream and subtle, in how the compression maths behaves when the weighting file has extreme values. Not my bug — but mine to find.

Every one of those losses is public, dated, and numbered, with its receipts. Seventeen data points. Architecture decision records for the choices, an issue trail for the arguments, provenance and evaluation sidecars on the published files.

I don't think that's normal, and I think it should be. The going standard for a published quantized model is a checksum, a file size, and sometimes a single quality number. A checksum proves the file is the file. It proves nothing about whether the file is any good — and it tells you nothing about the five artifacts that didn't make it.

Weigh the ingredients. Write down the voyage.

## What I'm still not claiming

**The winning run was not a cold solve.** By the time the pipeline built the artifact I published, I had already hand-discovered three things and handed them to it as inputs: ban the most aggressive setting outright, protect one specific tensor across 47 layers, and exclude four tensors from the weighting file. The solver reproduced the rest of the layout and made one forced trade of its own. So "measure instead of guessing" is true, and "the machine figured it all out by itself" is not. The measurements found those three rules across five losing attempts — but a human read the measurements.

The baseline beats me on one metric — how often the top word matches the original — by half a point, and that has never flipped. I let KL carry the ranking anyway, because the top word is a one-bit summary that ignores how wrong the model is when it misses, while KL weights the whole shape. If you always decode greedily, take that half point seriously. If you sample, take the KL.

And one control is missing. When both models got the same four facts wrong, the natural reading is that the mistakes come from the original model rather than from either compression. Natural isn't measured. The 93 GB original never answered those fifteen questions, because it doesn't fit the card and needs its own night on a slower lane. It's [tracked in the open](https://github.com/Alberto-Codes/vramfit/issues/143), and if the original gets them *right*, the result is more interesting than the one I have: both compressions damaged recall the same way.

I'd rather publish the gap named than the story clean.

## Where it lives

- **The tool:** [vramfit](https://github.com/Alberto-Codes/vramfit) — scan, plan, validate, pack. MIT.
- **The model:** [the packed 49B](https://huggingface.co/Alberto-Codes/Llama-3_3-Nemotron-Super-49B-v1_5-fit24gib-GGUF) — a quantization of [NVIDIA's Nemotron Super 49B v1_5](https://huggingface.co/nvidia/Llama-3_3-Nemotron-Super-49B-v1_5), under the NVIDIA Open Model License. Built with Llama.
- **The measurements:** the [sensitivity-map dataset](https://huggingface.co/datasets/Alberto-Codes/Llama-3_3-Nemotron-Super-49B-v1_5-sensitivity-maps) — the per-layer price list the recipe was solved from.
- **The full ledger:** [all seventeen data points](https://github.com/Alberto-Codes/vramfit/blob/main/docs/explanation/evaluating-packed-models.md), every number and every loss.

Coming next: how to fit a model to the card you actually have, why some layers break and others don't, and the missing control above. This is also the second time I've come at quantization from the measurement end — the [first was TurboQuant on a vision model](/blog/2026-03-26-i-ran-turboquant-on-a-vision-model-the-first-output-was-garbage), where the first output was garbage for a reason no benchmark would have told me.
