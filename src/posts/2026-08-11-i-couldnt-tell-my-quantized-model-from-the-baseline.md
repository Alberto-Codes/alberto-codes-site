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

They scored **19 out of 25. Both of them.** And they didn't just tie — they *agreed*. Both got the same four facts wrong. Both wrote the same function with the same bug in it. One of those two files was mine, built by measuring the model layer by layer. The other was the standard off-the-shelf quantization that thousands of people download.

If you chatted with both, you would find nothing, and you would conclude my work bought nothing.

It bought something. You just can't get at it by chatting — and understanding why is worth more than the result itself.

## The problem, if you've never met it

Large language models are big. Nemotron Super 49B — the one I care about — is about **93 GB** at full precision. A very good consumer graphics card, an RTX 4090, has **24 GB** of memory. The model has to fit entirely in there to run well.

So you compress it. The weights are billions of numbers stored at 16 bits each; store them at 4 bits, or 3, and the file shrinks. This is called quantization, and it's why you can run useful models at home at all.

The catch: crushing the numbers damages the model, and **not all parts damage equally.** Some layers shrug off being cut to 2 bits. Others — attention projections, the first and last blocks — fall apart below 6.

Here's the part that surprised me when I started. Essentially every quantized model you can download picks precision by **preset** — a fixed rule, the same one, applied to every model regardless of what's inside it.

Those presets are your abuelita's recipe. A handful of this, cook it till it looks right. They genuinely work, they're the product of real craft and years of taste, and the reasons they work were never written down. Nobody checks whether the rule is right *for the specific model in front of them*, because the rule has always been good enough.

What I wanted was the America's Test Kitchen version. Same dish, but weighed in grams, tested in kitchens that aren't hers, with the steps that actually matter separated from the ones that don't. Not a better rule. **No rule at all** — measure this model, solve for this budget, write down what you find.

## What compression actually takes away

To see why chatting can't find the difference, you need one idea about how these models work. It's the only technical thing in this post, and it's worth the two minutes.

**A language model doesn't produce a word. It produces a probability distribution over every possible next word.** Tens of thousands of candidates, each with a score. "The capital of France is ___" might come out as *Paris* 94%, *the* 2%, *a* 1%, and a long tail of everything else. Only then does something pick one.

![Two probability curves over possible next words. Both peak on the same top word, so greedy decoding picks identically from either. Behind the peak the curves separate — that difference is what KL divergence measures.](/vramfit-distribution-shoulders.svg)

Now the trap becomes obvious. When I ran my fifteen questions, I used greedy decoding — always take the single highest-scoring word. That reads **only the tip of the peak.** Two copies of a model can agree on the top word essentially every time while the shape behind it has drifted noticeably.

Conversation samples the peak. Damage lives in the shoulders.

The instrument that sees the shoulders is **KL divergence** — a standard measure of how much two probability shapes differ. Point it at the original 93 GB model and a compressed copy, run it across hundreds of pages of text, and you get a single honest number: how far did this copy drift from what it was made from?

That is the number I optimize. Not vibes, and not a preset.

## Measure, then solve

The tool is called [vramfit](https://github.com/Alberto-Codes/vramfit), and it does three things.

**Scan.** Crush one layer group at a time and measure how far the output shape moves. The result is a sensitivity map — a per-layer price list for this specific model, showing exactly which parts are fragile and which are cheap.

**Plan.** Now it's a budget problem, and a solver handles it. Given the price list and a hard memory ceiling, spend bits where the scan says they matter, and crush where it says they don't.

**Pack.** Apply the recipe, then check the artifact before trusting it.

The output isn't a preset. It's a recipe fitted to one model and one card. Give it a different budget and you get a different answer, because the arithmetic changes.

Against the standard quantization at the same file size, the measured recipe drifts **less** from the original — a 2.9% smaller gap, which sounds tiny but sits far outside the measurement noise. On five standard capability benchmarks the two are statistically tied, so the closer fit costs nothing. It's the first result in the project's lane where a measured recipe beats a preset on the deciding metric.

There's a sharper payoff than a better average, though. An earlier candidate of mine passed every check and looked clean — until a page-by-page comparison found a single page out of 564 where it fell off a cliff, diverging **fifty times** worse than the baseline on that one text. One page, and nothing had flagged it. The published artifact is the first with no such page anywhere.

That's the foolproof part, and it's the real return on weighing your ingredients. Not a better score — a **known shape.** You cannot find a cliff by chatting with a model, and you cannot find it in an average either.

## The part nobody publishes

Here's what I actually think the edge is, and it isn't the 2.9%.

Before that recipe won, **it lost five times.**

| Full-loop attempt | Date | Result |
|---|---|---|
| First real attempt | 2026-07-29 | **Lost** — badly |
| Rematch, handicap removed | 2026-07-29 | **Lost again**, by less, for a different reason |
| Better-converged measurements | 2026-07-31 | **Lost** |
| More honest price list | 2026-08-02 | **Lost** |
| Most honest price list yet | 2026-08-06 | **Lost by the most yet** |
| Ban the most aggressive setting | 2026-08-06 | Tie on one metric, behind on the other |
| Pipeline builds its own winner | 2026-08-09 | **Won** |

Read that table as a diagnosis, not a confession. Each loss eliminated a suspect. The first proved most of my deficit came from a weighting file the competition used and I didn't — not from my recipe at all. The second proved that damage doesn't simply add up: crushing two layers together can hurt far more than crushing each alone, which broke an assumption sitting at the center of my solver. The fifth killed my favorite theory outright — better measurements produced the *worst* model of the five, because the frame I measured in and the frame I shipped in disagreed.

In 1807 a Norwegian trading family shipped casks of aquavit to the East Indies and failed to sell any of it. The barrels sailed home unsold, and when the Lysholms tasted the returned spirit it was better than what they'd sent — months in oak on a rolling deck, two equator crossings of heat and humidity. The voyage had been doing something nobody designed it to do. [Linie Aquavit](https://www.norwegianamerican.com/snaps-visa-norways-equatorial-aquavit/) has crossed the equator and back in every bottle since.

Every one of those five losses was me finding a voyage. A weighting file, the way damage compounds, and eventually the real culprit — none of them were written down anywhere, and the preset had been quietly getting them right for years. The difference between an accident and a technique is whether somebody wrote it down.

The win, when it came, wasn't a cleverer solve. It was tracking down why one specific kind of layer in my files was fitted ten times worse than in the competition's. I suspected my settings, then my toolchain version. Both innocent. The real cause was upstream and subtle, in how the compression maths behaves when the weighting file has extreme values. Not my bug — but mine to find.

Every one of those losses is public, dated, and numbered, with its receipts. Seventeen data points. Architecture decision records for the choices, an issue trail for the arguments, provenance and evaluation sidecars on the published files.

I don't think that's normal, and I think it should be. The going standard for a published quantized model is a checksum, a file size, and sometimes a single quality number. A checksum proves the file is the file. It proves nothing about whether the file is any good — and it tells you nothing about the four artifacts that didn't make it.

Weigh the ingredients. Write down the voyage.

## What I'm still not claiming

The baseline beats me on one metric — how often the top word matches the original — by half a point, and that has never flipped. I let KL carry the ranking anyway, because the top word is a one-bit summary that ignores how wrong the model is when it misses, while KL weights the whole shape. If you always decode greedily, take that half point seriously. If you sample, take the KL.

And one control is missing. When both models got the same four facts wrong, the natural reading is that the mistakes come from the original model rather than from either compression. Natural isn't measured. The 93 GB original never answered those fifteen questions, because it doesn't fit the card and needs its own night on a slower lane. It's [tracked in the open](https://github.com/Alberto-Codes/vramfit/issues/143), and if the original gets them *right*, the result is more interesting than the one I have: both compressions damaged recall the same way.

I'd rather publish the gap named than the story clean.

## Where it lives

- **The tool:** [vramfit](https://github.com/Alberto-Codes/vramfit) — scan, plan, pack. MIT.
- **The model:** [the packed 49B](https://huggingface.co/Alberto-Codes/Llama-3_3-Nemotron-Super-49B-v1_5-fit24gib-GGUF) — a quantization of [NVIDIA's Nemotron Super 49B v1_5](https://huggingface.co/nvidia/Llama-3_3-Nemotron-Super-49B-v1_5), under the NVIDIA Open Model License. Built with Llama.
- **The measurements:** the [sensitivity-map dataset](https://huggingface.co/datasets/Alberto-Codes/Llama-3_3-Nemotron-Super-49B-v1_5-sensitivity-maps) — the per-layer price list the recipe was solved from.
- **The full ledger:** [all seventeen data points](https://github.com/Alberto-Codes/vramfit/blob/main/docs/explanation/evaluating-packed-models.md), every number and every loss.

Coming next: how to fit a model to the card you actually have, why some layers break and others don't, and the missing control above. This is also the second time I've come at quantization from the measurement end — the [first was TurboQuant on a vision model](/blog/2026-03-26-i-ran-turboquant-on-a-vision-model-the-first-output-was-garbage), where the first output was garbage for a reason no benchmark would have told me.
