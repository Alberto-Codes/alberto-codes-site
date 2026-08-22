---
title: The 2-bit label was 4.5 bits inside. My 16 GiB card could tell.
date: 2026-08-22
type: explanation
summary: The smallest 2-bit-labeled build of Nemotron 3.5 Lightning is 17.54 GiB — it doesn't fit a 16 GiB card, and its label names 12 of 417 tensors. I measured the model stack by stack instead, and got a 15.76 GiB pack that serves fully on-card at 16k context and beats the shelf's build on both damage metrics, while 1.78 GiB smaller.
tags:
  - python
  - ai
  - quantization
  - llm
  - evaluation
  - vramfit
  - open source
---

I wanted [NVIDIA's Nemotron 3.5 Lightning](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16) — a 30-billion-parameter mixture-of-experts model — running entirely on a 16 GiB card. The smallest GGUF on the shelf is labeled `IQ2_XXS`, a 2-bit-class quantization, about as aggressively crushed as llama.cpp gets.

It is **17.54 GiB**. It does not fit.

That's not sloppiness, and it's not anyone's dishonesty. The label is doing the only thing it can: naming **12 of the file's 417 tensors**.

## A label is not a recipe

[Last time](/blog/2026-08-11-i-couldnt-tell-my-quantized-model-from-the-baseline), the villain was the preset — a fixed rule that never measures the model in front of it. (That post also builds quantization from first principles; if "GGUF" and "2-bit" are new words, start there.) This time the preset doesn't even get to run. llama.cpp's compact quant types work on rows whose width 256 divides, and this model's routed-expert tensors are 2688 and 1856 columns wide. 256 divides neither. So the quantizer falls back, silently, and rewrites every one of those tensors to `IQ4_NL` at **4.5 bits per weight**.

This model stores the 128 routed experts of one projection in one layer as a single tensor — an *expert stack*. Twenty-three MoE layers, an up and a down projection each: 46 stacks, and those **46 stacks hold 93% of the parameters**. The fallback quietly rewrites all 46. Ask for the most aggressive 2-bit build and you get 4.5-bit experts wearing a 2-bit name tag.

![A bar of Nemotron 3.5 Lightning by parameter share. 93% of it is the 46 expert stacks, and the shelf's build silently rewrites every one to IQ4_NL at 4.5 bits per weight. The IQ2_XXS label names 12 of the build's 417 tensors, and not one expert stack is among them. The result is a 2-bit-class label on a 17.54 GiB file.](/vramfit-label-vs-file.svg)

It's your abuelita's recipe again, one town over: the jar says what the jar has always said, and the kitchen has been quietly substituting an ingredient for years because the real one doesn't fit the pan. The dish still works. But if your table only seats 16 GiB, the label will not warn you — the smallest thing on the shelf simply doesn't fit, and the shelf's lower-labeled rungs are made of the same locked-out types, so they land at essentially the same size.

The person who published that build, [bartowski](https://huggingface.co/bartowski/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF), did nothing wrong — the fallback belongs to the quantizer, and it runs without asking. This post exists because the way past it is the same move as last time: stop reading labels, start measuring.

## Measure the stacks, not the layers

[vramfit](https://github.com/Alberto-Codes/vramfit) built a sensitivity map keyed to what this model actually is. Not per-layer — per *expert stack*, because a stack is the unit a GGUF pack assigns a precision to. Each of the 46 stacks was quantized alone, at each candidate precision, and the damage recorded: how far the model's output distribution shifts from the bf16 reference when only that group is crushed. 46 stacks × 2 candidate widths = 92 measured cells, each with its run-log line — wall clock, memory high-water mark, the number itself.

Two full scans ran, and the difference between them matters later: one weighted its 4-bit fits with the same importance matrix the shelf's build used, and one ran unassisted. [Both maps are published](https://huggingface.co/datasets/Alberto-Codes/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-sensitivity-maps), run logs beside them.

The dense weights — attention, Mamba-2, shared experts, embeddings, the output head — never entered the map at all. They're **7% of the parameters**, which makes generosity nearly free: the recipe pins every quantizable dense class at 8-bit and spends the real decisions where 93% of the model lives.

## The recipe a 16 GiB budget buys

The solver walks the map greedily by damage per byte saved, under the budget. What came out:

- **11 expert stacks at 2.25 bits per weight** (`Q2_0`) — all of them `down_proj` stacks, the ones the map priced cheapest, landing spread across the depth from layer 22 on rather than clustered. The figure marks each one; the recipe records them exactly.
- **The other 35 stacks at `Q4_0`** — 4.5 bits, same real rate as the shelf's fallback.
- **118 dense groups at `Q8_0`**, and 46 groups passed through at F16 — the Mamba-2 convolutions and router gates, classes llama.cpp's quantizer never touches.

![Two recipes for the same 46 expert stacks. The shelf's build spends 4.5 bits on all 46 via the fallback and carries an MTP block, landing at 17.54 GiB. This pack keeps 35 stacks at Q4_0 and demotes 11 down_proj stacks to Q2_0 at 2.25 bits, spread across the depth, landing at 15.76 GiB.](/vramfit-16gib-recipe.svg)

`Q2_0` is the reason this recipe is possible at all: a plain block format — one scale per block, no super-block, no 256-wide requirement — that llama.cpp merged on 2026-07-07. It gives the solver a real 2.25-bit rung on tensors the compact types refuse. (It also means the file needs a llama.cpp build that carries that merge — a build older than it refuses the file. The serve test ran b10326.)

The recipe isn't a magic constant. It records the full solve — the budget bytes, the nine pins, the 11-step demotion trace — so the solve replays from the artifact, and the pack rebuilds this file's bytes on one machine from the base checkpoint. Across machines the byte count can differ by tens of bytes (the GGUF metadata stores the imatrix path); the recipe, not the checksum, is the identity.

## fit16gib is a contract, not a boast

The name on the repo says `fit16gib`, and I want to be precise about what that claims, because "it fits" is exactly the kind of unweighed statement this project exists to replace.

![A 16 GiB card splits into a 15.776 GiB weight budget and a 0.224 GiB runtime reserve for KV cache, recurrent state, and compute. The packed file lands at 15.760 GiB, 16.09 MiB under the budget. The margin holds to 8 parallel sequences.](/vramfit-16gib-budget.svg)

The claim is: this file loads **fully offloaded** on a 16 GiB card, holds **16k of context**, and generates. It's a measured serve result under a stated configuration, not a promise about every runtime.

The test: a hard ballast cap held an RTX 4090 to 16,383 MiB visible, and llama.cpp b10326 (Vulkan) loaded the file with every layer offloaded — 53 of 53, 15,774.00 MiB of weights on the device, with the 357.00 MiB token embedding host-mapped, as llama.cpp always keeps it. `llama-server` answered a completion request from inside that envelope: 16,157.88 MiB of device buffers against the 16,383 visible. The buffers total more than the 0.224 GiB reserve because the server ran four slots and recurrent state grows per sequence — which is exactly the growth the margin exists to absorb. The published build cannot take this test: its 17.54 GiB of weights exceed the card before the first buffer allocates.

And if that 0.224 GiB reserve looks suspiciously small beside the multi-GiB context reserve of [publication #1](/blog/2026-08-11-i-couldnt-tell-my-quantized-model-from-the-baseline): this model is a Mamba-2 hybrid with six attention layers, so 16k of KV cache is 96.00 MiB. The reserve is measured buffers rounded up, not a guessed overhead.

The contract's edges, stated plainly:

- The margin absorbs recurrent-state growth to **8 parallel sequences**. Above 8, the claim is off.
- The test's 16,383 MiB is a ballast-capped 4090, not your card. A 16 GiB card driving a display, a different backend, or a runtime with different buffer sizes moves the envelope — the claim is the stated configuration, and the card states it.
- **No tokens-per-second figure appears here or on the card.** The serve ran on a VRAM-capped 4090, and a decode number from that method would read 1.4 to 3.5 times higher than real 16 GiB silicon delivers. Publishing it would be publishing a flattering lie.
- A 16 GiB owner can already run *bigger* builds today by spilling part of the weights to CPU and accepting slower decode. That is a real alternative, and the project has not measured its speed cost. This pack is the option that keeps every weight on the card; whether the trade favors it on your workload is genuinely unsettled.

## The scoreboard

Both damage metrics were ruled before the measurement ran, read together from one instrument: the **perplexity ratio** (how much worse than the f16 original the pack predicts held-out text) and **mean KL divergence** (how far its output probabilities drift from the original's). Held-out WikiText-2, 594 chunks — my 15.76 GiB pack against the shelf's 17.54 GiB build:

| Model | PPL / f16 ↓ | Mean KLD ↓ | Same top ↑ |
|---|---|---|---|
| **This pack** | 1.1611 | 0.2043 | 83.13% |
| `IQ2_XXS` (the shelf) | 1.3209 | 0.3703 | 76.09% |

Both ruled metrics at once: a perplexity ratio 0.16 lower and **44.8% lower mean KL divergence**, at **1.78 GiB fewer bytes**. Top-token agreement rides along uninvited — it wasn't ruled, and in publication #1 it was the metric that beat *me* — so it reports here, but it doesn't rank. Last time the win was 2.9% on one metric at matched size. This one isn't close.

Then the task slice — five benchmarks fixed before any run, full evaluation splits, both models on the same lane. A delta inside the combined standard error reports as a tie; Winogrande clears that bar by a whisker:

| Task | This pack | The shelf's build | Verdict |
|---|---|---|---|
| MMLU (5-shot) | 0.7651 | 0.6848 | **ahead, +8.0 points at 16.1σ** |
| HellaSwag (10-shot) | 0.8038 | 0.7652 | ahead (6.7σ) |
| GSM8K (5-shot) | 0.7839 | 0.7627 | ahead (1.3σ) |
| Winogrande (5-shot) | 0.7443 | 0.7261 | ahead (1.04σ, barely) |
| ARC-Challenge (25-shot) | 0.6630 | 0.6715 | tie (0.4σ) |

Four leads and a tie, from the smaller file. The one nominal deficit prints with its error bar.

One cell I won't fill: the shelf build's bits-per-parameter. Mine is 4.287; its bytes include a block mine omits (next section), so the division would run over different weights. An empty cell is more honest than a wrong one.

## The handicap ran the wrong way

The cleanest objection: *you used a different importance matrix.* No — both packs consumed **the same one**, bartowski's, 185 entries over 822 chunks. It stays [in his repository](https://huggingface.co/bartowski/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF), linked from my card at a pinned revision with its hash, because it's his work and a link with credit is the right way to use it.

And the assistance ran *against* me. His build quantizes **91.53%** of its bytes with the matrix's help. Mine: **74.44%** — no type takes an assisted fit at 2.25 bits on these row widths, and the 8-bit quantizer discards the matrix outright. The pack wins carrying less of the shared advantage.

Which raises the attribution question the second scan exists to answer: is the win the map's, or the matrix's? The unassisted map — measured without the importance matrix — agrees with the assisted one through every rank the solve reads, and yields the identical placement. The win credits the damage ranking, not the borrowed weighting.

## Placement was a decision, not a default

One more claim earned its keep before publication: that *where* the 11 cheap stacks land matters, and the map knows where.

The same campaign packed and measured **nine placements of the identical width mix** — the map-ranked one, a spread-map probe, three blind draws, a spread-matched control, a measured-map arm, a class-wise arm, and one deliberately inverted to sit on the stacks the map prices dearest. Same 11-at-2.25, 35-at-4.5 spend, nine different answers to "which eleven." The map-ranked placement measured the least damage of the nine; the worst arm measured **2.7 times** as much.

Same bytes, same widths, 2.7× spread in damage. Allocation decides — and the map ranked it correctly before any of the nine files existed.

## What I'm still not claiming

**This pack is missing a block the shelf's build has.** The base checkpoint ships multi-token-prediction layers; my conversion dropped them (`--no-mtp`), so speculative decoding off that block is unavailable from this file. The comparator carries its MTP block at Q4_0 — which is also part of why it's bigger. If MTP-based speculation matters to your serving stack, that's a real difference, not a detail.

**No speed claim survives this post.** Not mine — the capped-4090 method inflates it. Not the CPU-offload alternative's — nobody measured it. The honest sentence is: this is the only *fully-on-card* option I can prove exists at 16 GiB and 16k context, and how much that's worth over offloading is an open question I've chosen to leave open in public rather than settle with a number I don't have.

**Don't take the damage numbers on tour.** The sensitivity values are one scan's measurements in one frame. They rank stacks within this map, and that's all they do — comparing them across scans, calibration sets, or models is meaningless, and the dataset card says so in bold. Rank packed models by measured quality at a fixed model and budget, never by raw damage.

**And the ledger keeps growing.** Every claim above traces to [the evaluation record](https://github.com/Alberto-Codes/vramfit/blob/main/docs/explanation/evaluating-packed-models.md), the same public trail the [first publication](/blog/2026-08-11-i-couldnt-tell-my-quantized-model-from-the-baseline) started — including the arms that lost. The going standard for a published quant is still a checksum and a file size. A checksum proves the file is the file. These documents are the argument that it's any good.

## Where it lives

- **The model:** [NVIDIA-Nemotron-3.5-Lightning-30B-A3B-fit16gib-GGUF](https://huggingface.co/Alberto-Codes/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-fit16gib-GGUF) — a quantization of [NVIDIA's Nemotron 3.5 Lightning 30B-A3B](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16), under OpenMDW 1.1. The card carries the recipe, the serve log, the eval sidecars, and the reproduce commands.
- **The measurements:** [the sensitivity-map dataset](https://huggingface.co/datasets/Alberto-Codes/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-sensitivity-maps) — both scans, run logs beside them. Solve your own card's budget against it.
- **The how-to:** [fit a model to the GPU you actually have](/blog/2026-08-15-fit-a-model-to-the-gpu-you-actually-have) — the command-by-command version, for your own card and model.
- **The tool:** [vramfit](https://github.com/Alberto-Codes/vramfit) — scan, plan, validate, pack. MIT.

A week ago I [argued](/blog/2026-08-15-a-different-ceiling-is-a-different-recipe) that a different ceiling is a different recipe, on paper — and that for the 49B at 16 GiB, the honest answer was no dish at all. That model still doesn't fit a 16 GiB card. This is a different model, solved for that smaller ceiling from the start: a locked-out quant family, a stack-keyed map, and a recipe that looks nothing like last time's, because the model is nothing like last time's. The method didn't change. Measure, then solve.
