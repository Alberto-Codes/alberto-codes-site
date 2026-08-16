# dev.to cut: Fit a model to the GPU you actually have

Policy: [ADR-0004](../../adr/0004-syndication-and-canonical-urls.md).
Template: [syndication-cut.md](../../templates/syndication-cut.md).

---

## Publishing notes

**Canonical URL:** https://alberto.codes/blog/2026-08-15-fit-a-model-to-the-gpu-you-actually-have

**Platform:** dev.to — the canonical post is `type: how-to`, which ADR-0004
decision 2 routes here.

**Tags:** `python, ai, machinelearning, tutorial`

**Cover image:** https://alberto.codes/vramfit-pipeline.png

**Inline images, in order of appearance:**

1. `https://alberto.codes/vramfit-pipeline.png` — the four-step pipeline and
   what each step hands to the next. Also the cover.

**Word count:** 2,246 → 1,441

**What this cut drops, and why:**

- The nine-package base-install listing and the `[scan]` / `[pack]` extras
  distinction — install detail that matters once you've committed, not while
  deciding whether to.
- The 49B column of the disk and time tables. Two audiences in one table
  reads as noise here. The 49B survives as a single sentence of scale.
- `--protect` and `--exclude-imatrix`. Both need the within-layer model to
  make sense, and neither is reachable on a first run.
- The `[gguf_converted]` run-log block and the `base_type` explanation.
- The reconstruction check, which only fires with an importance matrix.
- All five ADR links. Replaced with one repo link.
- Internal cross-links to the two companion posts, absolutized to
  alberto.codes.

**Post-publish steps:**

- [ ] Confirm the "Originally published at" line renders under the title
- [ ] Flip `published: true` after the preview reads correctly
- [ ] Record the live URL below

**Published at:** _(pending)_ **on** _(pending)_

---

## Article

```yaml
---
title: Fit a model to the GPU you actually have
published: false
description: Measure a model's per-layer quantization damage, solve for a recipe that fits your card, and check the result before you trust it.
tags: python, ai, machinelearning, tutorial
cover_image: https://alberto.codes/vramfit-pipeline.png
canonical_url: https://alberto.codes/blog/2026-08-15-fit-a-model-to-the-gpu-you-actually-have
---
```

*Originally published at [alberto.codes](https://alberto.codes/blog/2026-08-15-fit-a-model-to-the-gpu-you-actually-have)
on 2026-08-15. That version is the one I keep corrected.*

You have a GPU with a fixed amount of memory. You want to run a model that
doesn't fit. You've already tried an off-the-shelf quantization and you want
one fitted to your card instead of to the average card.

That's what this walks through. Every command below ran start to finish on a
clean rented 4090 with nothing else on it, and the output is pasted as it
came back. The worked example is Qwen2.5-3B-Instruct, small enough to finish
while you have lunch. I've run the same pipeline on a 49B, and I'll mention
where the numbers change.

The tool is [vramfit](https://github.com/Alberto-Codes/vramfit). It's on PyPI.

![Four steps. Scan produces a per-layer price list, plan turns it into a recipe under a memory ceiling, validate checks the real damage against the prediction and sends failures back to the solver, and pack builds the file.](https://alberto.codes/vramfit-pipeline.png)

## Check that torch can see your card first

This is the thing that bites, and it isn't the tool's doing. `pip` resolves a
torch build for whatever CUDA it feels like. On a clean 4090 box with a 12.8
driver I got a 13.0 build:

```
$ python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
2.13.0+cu130 False
```

`nvidia-smi` said `CUDA Version: 12.8`, torch was built for 13.0, and the GPU
may as well not have existed. Name the index that matches your driver:

```bash
pip install --force-reinstall torch --index-url https://download.pytorch.org/whl/cu128
```

```
$ python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
2.11.0+cu128 True
```

Sixty seconds of checking against half an hour of a scan silently running on
CPU.

While you're here: budget more disk than you expect. The pipeline works
through an uncompressed f16 intermediate that everything else quantizes from.
For a 3B that's 5.75 GiB of intermediate on top of 5.8 GiB of weights — call
it 20 GiB free. The f16 conversion surprises people, not the model download.

## 1. Work out your real budget

The number that matters isn't your card's size. It's your card's size minus
what the KV cache needs at the context length you plan to serve.

```
$ vramfit budget --vram 24GiB --context 16384 --model-config config.json
attention layers      49  (KV 200704 bytes/token, fp16)
VRAM total            24.00 GiB
- KV cache            3.06 GiB  (16384 tokens x 1 seq)
- runtime overhead    2.00 GiB
= weight budget       18.94 GiB
```

That remainder is what the solver targets, to the byte.

**Do this before anything else, because it can end the job right here.**
Solving is cheap — seconds, no GPU — so you can find out whether your ceiling
is reachable at all before spending hours on a scan:

```
error: no recipe fits the 12.47 GiB weight budget
       — minimum achievable is 15.31 GiB (2.85 GiB over)
```

That's a 16 GiB card being told this model won't fit at any precision the
price list allows. Better to learn that now than after the download.

## 2. Scan

Quantize one layer group at a time, measure how far the output distribution
moves, write down the price. This is the expensive step, and it produces the
artifact worth keeping.

You need a calibration text — a few hundred kilobytes of prose the meter
pushes through the model. Any representative text works; I use 754 KiB of
WikiText-2.

```bash
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
vramfit scan /path/to/Qwen2.5-3B-Instruct \
  --calibration calibration.txt \
  --max-tokens 32768 \
  --precisions 8,4,3,2 \
  --group-by layer \
  --out sensitivity.json
```

```
[3/148] model.embed_tokens @ 3-bit damage 0.249366
[8/148] model.layers.0 @ 2-bit damage 0.905969
[20/148] model.layers.3 @ 2-bit damage 2.908759
...
[147/148] model.layers.35 @ 3-bit damage 0.077071
scanned 37 groups x 4 precisions over 32768 tokens -> sensitivity.json
```

37 groups, 4 precisions, 148 cells, 52 minutes. The same scan on a 49B is 328
cells and 37 hours, because it streams weights from host RAM instead of
holding them resident.

Look at what it found before going further. `model.layers.3` costs 2.9088 at
2-bit and 0.0011 at 8-bit — a factor of about 2,600 between the cheapest and
dearest thing you can do to one layer. That spread is the entire reason the
tool exists. If every precision costs about the same, your calibration text
is too short to have converged.

Two things that catch people:

**The memory cap matters on bigger models.** A 3B fits a 4090 resident and
needs nothing. A 49B needs `--gpu-memory 15GiB` on the same card and dies at
17, because the meter needs headroom *beside* the weights for reference
activations. `expandable_segments` is in the command above for the same
reason — without it, fragmentation kills a cell that would otherwise fit. A
halted scan checkpoints, so `--resume` picks up where it stopped.

**8k tokens is a pilot, not a scan.** Re-planning the same budget on a 32k
map instead of an 8k one flipped 41 of 82 assignments on the 49B, and
predicted damage went from 0.4949 to 0.0940.

The map is a property of the model, not of your machine. Scan once, then
solve it against any ceiling later — on a laptop, without a GPU.

## 3. Plan

```bash
vramfit plan sensitivity.json --vram 4GiB --kv-headroom 1.5625GiB --out recipe.json
```

Seconds, no GPU. And it does nothing interesting until your ceiling actually
squeezes. Same 3B map, four cards:

| card | weight budget | result | downgrades |
|---|---|---|---|
| 12 GiB | 9.44 GiB | 3.07 GiB, every group at 8-bit | 0 |
| 6 GiB | 3.44 GiB | 3.07 GiB, every group at 8-bit | 0 |
| 4 GiB | 2.44 GiB | 2.42 GiB, 19 at 8-bit and 18 at 4-bit | 18 |
| 3 GiB | 1.44 GiB | 1.43 GiB, 17 at 4-bit and 20 at 3-bit | 57 |

A 3B on a 12 GiB card is not a problem anyone has. Run this on a model that
genuinely doesn't fit, or you'll conclude the solver does nothing — it just
has nothing to decide. Predicted damage across those rows: 0.0340, 0.0340,
0.0861, 0.4973.

## 4. Pack

```bash
vramfit pack recipe.json \
  --model /path/to/Qwen2.5-3B-Instruct \
  --llama-cpp /path/to/llama.cpp \
  --smoke-text smoke.txt \
  --out qwen3b-fit4gib.gguf
```

```
converting /path/to/Qwen2.5-3B-Instruct -> qwen3b-f16.gguf
packed 37 groups -> qwen3b-fit4gib.gguf (2.41 GiB), weight budget 2.44 GiB, margin 24.23 MiB under
smoke test: perplexity 16.0119 over 2 chunks, ceiling 1000 — passed
```

You build llama.cpp yourself and point at the checkout. The tool provisions
the interpreter its converter script needs, not llama.cpp itself.

On bigger models the importance matrix stops being optional. The 3B pack
above ran without one. At 3-bit on the 49B it was the single largest
contributor to closing the gap with the baseline — about 81 % of the recipe's
deficit. Pass it with `--imatrix`.

## 5. Check it before you trust it

Non-negotiable, and the reason is a real incident: a recipe once predicted
damage 1.44 and the packed artifact was destroyed — perplexity around 10⁶,
top-token agreement 0.3 %. Nothing between plan and pack would have caught it.

The smoke test runs a short perplexity pass on the packed file and fails
above a ceiling. The 3B run scored 16.0119 against a ceiling of 1000.

**That number is not a quality claim, and you shouldn't read it as one.** The
smoke test runs two chunks and nothing else. It has no f16 reference to
compare against, so it can tell you the artifact still produces language — it
cannot tell you how much you lost. The ceiling looks absurdly loose because
it's a corpse detector: the 10⁶ artifact would have tripped it instantly, and
that's the whole job.

Measuring what you actually lost is a separate step and a real evaluation.

## When this is the wrong tool

Off-the-shelf quantizations are good, they're free, and they're one download.

The four-ceiling table in step 3 is the sharpest version of the test. If your
ceiling leaves the model comfortable, the solver has nothing to decide and
you should take a preset. The further your real ceiling sits from the sizes
the shelf happens to stock, the more this pays.

I worked three ceilings on the 49B side by side —
[including one where no recipe exists at all](https://alberto.codes/blog/2026-08-15-a-different-ceiling-is-a-different-recipe) —
and the surprise was that a tighter ceiling doesn't shave everything down a
notch. It re-decides what's worth protecting.
