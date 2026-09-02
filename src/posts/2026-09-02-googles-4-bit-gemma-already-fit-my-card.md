---
title: Google's 4-bit Gemma already fit my card. I wanted the context it left on the table.
date: 2026-09-02
type: explanation
summary: The official Q4_0 build of Gemma 4 31B is 16.44 GiB and fits a 24 GiB card with room to spare, so "it fits" was never the claim. I measured the decoder layer by layer, solved a 14.92 GiB pack that ties Google's build on four held-out benchmarks and wins one, and let the freed bytes buy context — 86,016 served tokens against 65,536, and 73,728 against 49,152 with an image aboard.
tags:
  - python
  - ai
  - quantization
  - llm
  - multimodal
  - evaluation
  - vramfit
  - open source
---

[Gemma 4 31B](https://huggingface.co/google/gemma-4-31B-it) ships with something the last two models didn't have: an official quantization. Google publishes a [quantization-aware-trained Q4_0 GGUF](https://huggingface.co/google/gemma-4-31B-it-qat-q4_0-gguf), trained toward 4-bit deployment on purpose, at **16.44 GiB**. On a 24 GiB card it loads with seven and a half gigabytes to spare.

So for the first time in this series, "it fits" isn't a claim anyone needs to make. The question is what those spare gigabytes are worth — and on this model, they're worth more than usual.

## What a gigabyte of weights buys here

Everything a card holds past the weights goes to the KV cache, the per-token memory that grows with context. Gemma 4 31B's decoder has **60 layers, and 50 of them are sliding-window**: each one sees the last 1,024 tokens and no more, so once a sequence passes that window its cache stops growing. Only the **10 global layers** keep growing with context.

That makes the price of context small and flat. Measured at the runtime — llama.cpp b10362, not the config file — a token of context costs **81,920 bytes** once the windows saturate, plus a fixed 1,200 MiB pool per sequence for the fifty windowed layers. (The config's arithmetic says half that per token, because Gemma stores one tensor for both keys and values; the runtime allocates both anyway, and the runtime is what runs.) A gigabyte of weights freed is about **13,100 tokens** of context bought.

![A 24 GiB card, twice. Google's QAT Q4_0 holds 16.44 GiB of weights and serves 65,536 tokens of text context. This pack holds 14.92 GiB and serves 86,016. The gap in weights is 1.5 GiB; the gap in served context is 20,480 tokens. Both are measured load boundaries on an RTX 4090, llama.cpp b10362, one sequence, 4,096-token rungs, measured 2026-08-31.](/vramfit-24gib-kv-geometry.svg)

## The budget is the claim

That inverts how [vramfit](https://github.com/Alberto-Codes/vramfit) had been thinking. Publications [#1](/blog/2026-08-11-i-couldnt-tell-my-quantized-model-from-the-baseline) and [#2](/blog/2026-08-22-the-2-bit-label-was-4-5-bits-inside) asked how few bytes a model could survive. This one asks the other direction: pick the context you want, subtract, and give the weights whatever's left. Nine gigabytes of KV headroom on a 24 GiB card leaves 15 GiB for weights — call that arm kv9. That's the one that shipped. An eleven-gigabyte headroom leaves 13 GiB, and that arm is the more interesting story, because it lost.

## Measuring a model that only speaks in turns

Before either arm could be solved, the meter had to be fixed. This checkpoint is instruction-tuned and quantization-aware-trained, and it is *channel-locked*: it has only ever seen text inside its chat frame. Feed it raw prose and it prices it as noise. On the calibration corpus, the same tool read a perplexity in the thousands on bare text and **37.39** on the identical text wrapped in the model's turn markers.

A sensitivity map measured on the raw distribution would price every layer against text no user ever sends. So every measurement in this campaign — the scan, the importance matrix, the perplexity and divergence readings — ran inside one fixed model-turn frame: 357 blocks of public-domain text, 182,404 tokens, the turn markers parsed as the control tokens they are. One trap that step caught: the bf16 conversion had emitted `<|turn>` as an ordinary token, and only a token count exposed it.

The map itself is keyed per decoder layer, 60 layers and the token embedding, because this is a dense model and a layer is the unit the pack addresses. The vision tower never entered it. A text-measured map licenses no vision claim, and that gap gets its own measurement below.

## The recipe: cheap early, protected deep

The solver walked the map greedily by damage per byte saved, under the 15 GiB weight budget, over Google's [QAT-unquantized checkpoint](https://huggingface.co/google/gemma-4-31B-it-qat-q4_0-unquantized) — the weights Google annealed toward 4-bit before quantizing them. What came out:

- **6 layers at `Q2_K`** — layers 1 through 5, and 11. The map priced the early layers cheapest.
- **9 layers at `Q3_K`** — layer 0, 6 through 10, and 12 through 14.
- **45 layers at `Q4_K`** — layers 15 through 59. The solve spent its budget protecting depth.
- The token embedding and the output head at `Q4_K`.

![Sixty decoder layers in a strip. Layers 1 to 5 and 11 sit at Q2_K, layer 0, 6 to 10, and 12 to 14 at Q3_K, and layers 15 to 59 at Q4_K. Beside the strip, the two shipped files: the 14.92 GiB decoder and the 629 MiB projector sidecar.](/vramfit-24gib-recipe.svg)

The packed decoder is **14.92 GiB**, 86.08 MiB under budget, with the recipe's 81-step trace beside it. Google's build is one preset applied uniformly; this one buys forty-five protected layers by spending fifteen cheap ones, and still lands a gigabyte and a half lighter.

Images need a second file: the *projector*, the encoder that turns pixels into tokens the decoder can read. It ships beside the decoder as a sidecar, and it gets priced below.

## The metric that pointed backwards

The 13 GiB arm, kv11, was the aggressive point, and on the lingua-franca metric it *won*. Perplexity ratio against the bf16 reference, in frame:

| Arm | Weights | PPL / bf16 ↓ | Mean KLD ↓ | Same top ↑ |
|---|---|---|---|---|
| kv11 (13 GiB) | 12.92 GiB | **1.0390** | 0.1352 | 86.35% |
| **kv9 (15 GiB, shipped)** | 14.92 GiB | 1.0681 | 0.0446 | 92.04% |
| Google's QAT Q4_0 | 16.44 GiB | 1.1043 | **0.0420** | **92.32%** |

Read the columns against each other. Perplexity ratio ranks the three packs in one order; every fidelity metric ranks them in the *opposite* order. kv11 has the best perplexity ratio and **3.2 times the divergence** of Google's build. A perplexity-only scoreboard would have shipped the wrong file.

![Three packs, two rankings. Perplexity ratio orders kv11, kv9, then QAT. Mean KL divergence orders QAT, kv9, then kv11. The two orderings are exactly reversed, and the held-out benchmarks below break the tie.](/vramfit-24gib-two-arms.svg)

The held-out benchmarks arbitrated, and they sided with divergence. Five tasks fixed before any run, full evaluation splits, every arm on the same lane. A delta inside the combined standard error is a tie:

| Task | kv9 (shipped) | Google's QAT Q4_0 | Verdict |
|---|---|---|---|
| MMLU (5-shot) | **71.36** | 70.20 | **win, +1.15 against a combined σ of 0.53** |
| GSM8K (5-shot) | 92.34 | 92.42 | tie |
| HellaSwag (10-shot) | 58.71 | 59.34 | tie (−0.63 against 0.69) |
| Winogrande (5-shot) | 68.27 | 68.03 | tie |
| ARC-Challenge (25-shot) | 61.77 | 61.09 | tie |

Four ties and a win, from the lighter file. kv11 took the same slice and lost HellaSwag outright, **−2.33 points against a combined σ of 0.69**, with four ties around it. Its divergence showed up on exactly one task, which is one more than the shipping bar allows. kv11 would have served the most context of the three, and it stays [on the record](https://github.com/Alberto-Codes/vramfit/issues/423) as the arm that measured too much damage to publish.

Two honest asymmetries travel with the first table. Google's build holds a slightly better mean KL divergence and top-token agreement than the shipped pack; the two text metrics disagree at the margin, and the benchmarks are what settle it. And that table is measured on the pack's own calibration frame — the same corpus its importance matrix consumed — which leans the in-frame numbers toward my pack. The held-out slice is the check on that.

## What the bytes bought, served

Computed capacity is arithmetic. Served capacity is a ladder: load the file at a context size, step up 4,096 tokens, repeat until the load fails. Both packs ran the ladder on the same RTX 4090, the same day, under the same idle desktop, llama.cpp b10362 Vulkan, one sequence:

| Serving shape | This pack | Google's QAT Q4_0 | Gain |
|---|---|---|---|
| Text only | **86,016** tokens | 65,536 | +20,480 (+31.25%) |
| One image aboard | **73,728** tokens | 49,152 | +24,576 (+50%) |

The image row moves two variables at once — my decoder *and* my converted projector — so the card also prints the one-variable version: behind Google's own BF16 projector, this pack serves an image at 69,632 tokens, still +41.7%. The projector conversion adds the last 4,096.

`fit24gib` is a contract, not a boast, and the boundary has edges:

- **It moves with the frame.** The 2026-08-28 ladder found 81,920 for text; three days later, in a different frame, the same file passed 86,016. The boundary moves with the box's idle VRAM share. Both are real, and the card names both.
- **Pass `-np 1`.** The server defaults to four slots, which adds about 2,400 MiB of sliding-window cache on this geometry and fails loads that fit at one.
- **Keep about 200 MiB free when serving images**, and cap the encode batch at one image. The image-encode buffer allocates at request time, and this server build crashes on that failure instead of refusing.
- **The ladder is a fit bar, not a speed bar.** The boundary check decoded five tokens. Throughput at 86,016 tokens is unmeasured.

Throughput at the boundary is unmeasured, but throughput at a working context is not, and it's the number I refused to print last time. Both quantized arms ran the same 20-task subset at 8,192 tokens of context on the 4090, the target card: **47.8 tokens per second for this pack against 43.3** for Google's. On an H100 the order flipped, with Google's build 15% ahead. Twenty generations, one slot, my pack's answers averaging 20 tokens to Google's 48 — a measured number on the card the claim is about, with its caveats attached.

## The vision claim had to be earned separately

The map measured text. A multimodal card that says nothing about images would be leaving the most likely use unpriced, and a card that infers image quality from text damage would be guessing. So the campaign measured it: a BF16 reference decoder generated greedily over ten held-out 768×768 images, and each quantized arm was teacher-forced along the reference's sequence, reading a truncated top-20 KL divergence at the server boundary (the server caps its probability list at 20, so this is not a full-vocabulary number). Positions that carry image content are scored apart from the chat-frame policy tokens that dominate the average.

Content-class results, 120 positions:

| Arm | Mean KLD ↓ | p95 ↓ | Same top ↑ |
|---|---|---|---|
| **This pack, as shipped** | 0.0050 | **0.0193** | 99.2% |
| This pack, Google's BF16 projector | 0.0045 | 0.0239 | 99.2% |
| Google's QAT Q4_0, Google's BF16 projector | 0.0373 | 0.1928 | 97.5% |

**7.5 times below Google's build, 47 times above the instrument's noise floor** (1.07e-4, measured by scoring an arm against its own greedy output). The reference ran on CPU — a second instrument — so these read as divergence from the reference, never as same-instrument damage; only the pack-against-Q4_0 comparison shares one instrument.

That measurement is also what priced the projector. Google's ships in BF16 at 1,145 MiB. Run through llama-quantize's `Q4_K_M` recipe it lands at **629 MiB** — and holds not one `Q4_K` tensor, because every quantizable tensor in it falls back on this geometry to `Q5_0` or `Q8_0`. The recipe name labels the command, not the contents. The cost was 0.0045 to 0.0050 on the content mean; the return was 482 MiB at load and one rung of context. It shipped.

Then a second campaign put the bound somewhere real: **1,349 GUI screenshots** at 1280×720 from a public computer-use dataset, three arms on one H100. On image-content positions this pack diverges less than Google's build — 0.0973 against 0.1143 at the mean, and a median 3.6 times lower. Read that as a bound, not a separation: this campaign measured no noise floor, and a prompt-prefix difference between the three files rides inside the mean margin. On a task-identification score, no arm separates: the BF16 reference itself scored 49.9%, my pack 51.2%, Google's 51.4% (from a 512-token regeneration, after every one of its 48-token answers ended mid-thought), all inside a 6.9% judge noise floor. One screenshot against a whole task's name is a ceiling the reference can't clear either.

## What I'm still not claiming

**The sensitivity map and the importance matrix are not published.** Publications #1 and #2 shipped their maps as datasets; this one ships the recipe, the run log, the evaluation sidecars, and both campaign records, but the map and the matrix stay in the run archive. The recipe replays the type placement from the base checkpoint. Without the map, `vramfit plan` cannot re-solve this model for a different budget, and without the matrix a rebuild reproduces the placement but not this file's exact bytes.

**Google's build is the comparator, not the shelf.** It is the vendor's own artifact and the obvious baseline. No claim here covers the other GGUFs of this model on the Hub.

**The vision numbers bound divergence, not safety.** Quantization compresses every tensor with one lossy procedure and can shift any behavior. The tables are the measured bound on that shift over text, ten images, and 1,349 screenshots. Read the card as a damage disclosure. Deploy the pack with whatever protections you'd give the base model.

**Damage values don't travel.** The map's 0.184 predicted damage is one scan's number in one frame. It ranks layers within this map and nothing else.

## Where it lives

- **The model:** [gemma-4-31B-it-fit24gib-GGUF](https://huggingface.co/Alberto-Codes/gemma-4-31B-it-fit24gib-GGUF) — two files, one artifact. The decoder serves text alone; add the projector sidecar for images. The card carries the recipe, the serve ladders, the eval sidecars, both campaign records, and the reproduce commands. Apache 2.0, under the Gemma 4 license note.
- **The tool:** [vramfit v0.4.0](https://github.com/Alberto-Codes/vramfit/releases/tag/v0.4.0) — what this campaign forced: per-layer KV geometry in the model shape, KV priced at the runtime's measured allocation, a `capacity` readout that turns a packed recipe back into tokens, the projector sidecar and vision line in `pack` and `budget`, and the framed-calibration script. MIT.
- **The policy:** [ADR-0030](https://github.com/Alberto-Codes/vramfit/blob/v0.4.0/docs/adr/0030-vision-budget-sidecar.md) — how a vision tower enters the budget, and what a text-measured map may and may not claim.
- **The how-to:** [fit a model to the GPU you actually have](/blog/2026-08-15-fit-a-model-to-the-gpu-you-actually-have) — the command-by-command version.

Last time the villain was a label that hid a fallback. This time there was no villain. Google's build is good, it fits, and it's the first comparator in this series I'd happily run. The only thing wrong with it was the seven and a half gigabytes it wasn't using — and the only way to find out what they were worth was to measure, solve, and serve the ladder until it failed.
