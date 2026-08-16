---
title: Fit a model to the GPU you actually have
date: 2026-08-15
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

## Who this is for

You have a GPU with a fixed amount of memory. You want to run a model that
does not fit. You have already tried an off-the-shelf quantization and want
one fitted to your card instead of to the average card.

Assumed: comfortable with a terminal, a CUDA GPU. Not assumed: any
quantization background — that is the
[explanation post](/blog/2026-08-11-i-couldnt-tell-my-quantized-model-from-the-baseline).

Every command below was run start to finish on a clean rented 4090 with
nothing else on it. The output is pasted as it came back.

![Four steps. Scan produces a per-layer price list, plan turns it into a recipe under a memory ceiling, validate checks the real damage against the prediction and sends failures back to the solver, and pack builds the file.](/vramfit-pipeline.svg)

## Before you start

**Install.** The base install is small on purpose, so the planning step runs
on a laptop with no GPU. The heavy parts are extras
([ADR-0005](https://github.com/Alberto-Codes/vramfit/blob/main/docs/adr/0005-heavy-deps-as-extras.md)):

```bash
pip install vramfit           # plan and budget only, no torch
pip install "vramfit[scan]"   # adds torch + transformers, for scan and validate
pip install "vramfit[pack]"   # adds what llama.cpp's converter needs
```

That base install is nine packages — vramfit, `typer`, `structlog`, and
typer's own dependencies:

```text
Pygments, annotated-doc, markdown-it-py, mdurl, rich,
shellingham, structlog, typer, vramfit

>>> import torch
ModuleNotFoundError: No module named 'torch'
```

Two things that catch people. `vramfit validate` needs `[scan]`, not just
`scan` — it replays a whole recipe through the same meter. And `[pack]` does
**not** give you llama.cpp; it provisions the interpreter its converter script
needs. You build llama.cpp yourself and point at the checkout with
`--llama-cpp` ([ADR-0012](https://github.com/Alberto-Codes/vramfit/blob/main/docs/adr/0012-gguf-type-mapping.md)).

**Check that torch can actually see your card before anything else.** This
is the first thing that bites, and it isn't vramfit's doing. `pip` resolves
a torch build for whatever CUDA it feels like, and on a clean 4090 box with
a 12.8 driver I got a 13.0 build:

```text
$ python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
2.13.0+cu130 False
```

`nvidia-smi` says `CUDA Version: 12.8`, torch was built for 13.0, and so the
GPU may as well not exist. The fix is to name the index that matches your
driver:

```bash
pip install --force-reinstall torch --index-url https://download.pytorch.org/whl/cu128
```

```text
$ python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
2.11.0+cu128 True
```

Sixty seconds of checking against half an hour of a scan silently running on
CPU.

**Disk.** More than you expect, because the pipeline works through an
uncompressed intermediate — an f16 GGUF that everything quantizes from.

| | 3B walkthrough | 49B run |
|---|---|---|
| model weights | 5.8 GiB | 92 GiB |
| f16 GGUF | 5.75 GiB | 92.89 GiB |
| packed output | 2.41 GiB | 20.36 GiB |
| llama.cpp build | ~2 GiB | ~2 GiB |

Budget roughly 20 GiB free for a 3B and 115 GiB for a 49B. The f16 conversion
is the step that surprises people, not the model download.

**Time.** Measured, not estimated:

| step | 3B on a 4090 | 49B on a 4090 |
|---|---|---|
| scan | **52 min** (148 cells) | **37.0 hours** (328 cells) |
| plan | seconds | seconds |
| f16 convert | 2 min 12 s | ~1 hour |
| quantize | 24 s | 16 min 34 s |
| smoke test | seconds | seconds |

The 49B scan streams weights from host RAM, which is most of why it is 40
times slower per cell than a model that fits resident.

## 1. Work out your real budget

The number that matters is not your card's size. It is your card's size
minus what the KV cache will need at the context length you plan to serve.
`vramfit budget` does that arithmetic from the model's own `config.json`,
which matters here because this model's attention blocks are NAS-pruned and
heterogeneous — you can't eyeball the cost per token from the parameter
count.

```console
$ vramfit budget --vram 24GiB --context 16384 --model-config config.json
attention layers      49  (KV 200704 bytes/token, fp16)
VRAM total            24.00 GiB
- KV cache            3.06 GiB  (16384 tokens x 1 seq)
- runtime overhead    2.00 GiB
= weight budget       18.94 GiB
```

That remainder is what the solver targets, to the byte.

**Do this before anything else, because it can end the job right here.** Solving is
cheap — seconds, no GPU — so you can find out whether your ceiling is even
reachable before spending 37 hours on a scan. Run against a published price
list and the answer comes back immediately:

```text
error: no recipe fits the 12.47 GiB weight budget
       — minimum achievable is 15.31 GiB (2.85 GiB over)
```

That is a 16 GiB card being told this model will not fit, at any precision
this price list allows. Better to find out now than after the download.

If your budget does land on a stock preset's size, take the preset — this
whole pipeline buys you the most when your ceiling sits *between* the sizes
the shelf stocks. The companion post works three ceilings side by side, including where the
recipe's priorities reorder rather than just shrink.

## 2. Scan

Quantize one layer group at a time, measure how far the output distribution
moves, write the per-layer price list. This is the expensive step, and it
produces the artifact worth keeping.

You need a calibration text — a few hundred kilobytes of prose the meter
pushes through the model to see what moves. Any representative text works.
For a run you can compare against mine, take the one published beside the
49B maps:

```bash
curl -LO https://huggingface.co/datasets/Alberto-Codes/Llama-3_3-Nemotron-Super-49B-v1_5-sensitivity-maps/resolve/main/calibration.txt
```

That file is 754 KiB of WikiText-2, and it's the same one every number on
this page was measured with.

Here it is on Qwen2.5-3B-Instruct, which is small enough to finish while you
have lunch:

```bash
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
vramfit scan /path/to/Qwen2.5-3B-Instruct \
  --calibration calibration.txt \
  --max-tokens 32768 \
  --precisions 8,4,3,2 \
  --group-by layer \
  --out sensitivity.json
```

```text
[3/148] model.embed_tokens @ 3-bit damage 0.249366
[8/148] model.layers.0 @ 2-bit damage 0.905969
[20/148] model.layers.3 @ 2-bit damage 2.908759
...
[147/148] model.layers.35 @ 3-bit damage 0.077071
scanned 37 groups x 4 precisions over 32768 tokens -> sensitivity.json
```

It prints a line per cell, so you can tell it's alive. What you want to see
is 8-bit damage in the thousandths and 2-bit damage one to three orders
higher — that spread is the signal. If every precision costs about the same,
your calibration text is too short to have converged.

37 groups, 4 precisions, 148 cells, 52 minutes. Look at what it found before
you go further: `model.layers.3` costs 2.9088 at 2-bit and 0.0011 at 8-bit,
a factor of about 2,600 between the cheapest and dearest thing you can do to
one layer. That spread is the entire reason this tool exists.

The map is a property of the model, not of your machine. Scan once and you
can solve it against any ceiling later, on a laptop, without a GPU — which
is what makes step 3 cheap.

**The memory cap matters on bigger models.** The 3B above fits a 4090
resident and needs no cap at all. The 49B needs `--gpu-memory 15GiB` on the
same card, and dies at 17:

```text
error: scan halted at model.embed_tokens 8-bit: CUDA out of memory.
Tried to allocate 1.96 GiB ... (checkpoint keeps 0 cells)
```

The cap is lower than the card because the meter needs headroom *beside* the
weights for the reference activations. `expandable_segments` is in the
command above for the same reason — without it, fragmentation kills a cell
that would otherwise fit. A halted scan checkpoints, so `--resume` picks up
where it stopped.

**Calibration length is the setting people get wrong.** 8k tokens is a pilot
— not a scan. Re-planning the *same budget* on a 32k map instead of an 8k one
flipped **41 of 82 assignments** on the 49B, and predicted damage went from
0.4949 to 0.0940. 32k suffices at 3-bit and above. (The 3B walkthrough above
used 32k for the same reason.)

## 3. Plan

Solve the price list against your ceiling. Seconds, no GPU.

```bash
vramfit plan sensitivity.json --vram 4GiB --kv-headroom 1.5625GiB --out recipe.json
```

The thing worth understanding is that this does nothing interesting until
your ceiling actually squeezes. Same 3B map, four cards:

| card | weight budget | result | downgrades |
|---|---|---|---|
| 12 GiB | 9.44 GiB | 3.07 GiB, every group at 8-bit | 0 |
| 6 GiB | 3.44 GiB | 3.07 GiB, every group at 8-bit | 0 |
| 4 GiB | 2.44 GiB | 2.42 GiB, 19 at 8-bit and 18 at 4-bit | 18 |
| 3 GiB | 1.44 GiB | 1.43 GiB, 17 at 4-bit and 20 at 3-bit | 57 |

A 3B on a 12 GiB card is not a problem anyone has. Run this on a model that
genuinely doesn't fit, or you'll conclude the solver does nothing — it just
has nothing to decide. Predicted damage across those four rows runs 0.0340,
0.0340, 0.0861, 0.4973.

Two flags deserve plain explanations, because they're what closed the gap on
the published 49B artifact.

**`--protect "glob=bits"`** holds specific *tensors* at a precision floor
inside their group
([ADR-0022](https://github.com/Alberto-Codes/vramfit/blob/main/docs/adr/0022-within-layer-protections.md)).
A layer group is one assignment, but a layer isn't uniform — the attention
value projection can be the thing that breaks while the rest of the layer is
fine at 3-bit. Protection buys that one tensor back without paying for the
whole group. The published recipe carries 48 such pairs.

**`--exclude-imatrix "glob"`** quantizes a matched protected tensor *without*
its importance-matrix rows
([ADR-0023](https://github.com/Alberto-Codes/vramfit/blob/main/docs/adr/0023-imatrix-exclusions.md)).
It sounds backwards, and it's a remedy rather than a default: occasionally
the importance weighting makes a specific tensor's fit collapse, and the
reconstruction check below is what tells you which one.

## 4. Pack

```bash
vramfit pack recipe.json \
  --model /path/to/Qwen2.5-3B-Instruct \
  --llama-cpp /path/to/llama.cpp \
  --smoke-text smoke.txt \
  --out qwen3b-fit4gib.gguf
```

```text
converting /path/to/Qwen2.5-3B-Instruct -> qwen3b-f16.gguf (minutes at 3B scale)
packed 37 groups -> qwen3b-fit4gib.gguf (2.41 GiB), weight budget 2.44 GiB, margin 24.23 MiB under
smoke test: perplexity 16.0119 over 2 chunks, ceiling 1000 — passed
```

The run log records what actually happened, which is what you want six
months later:

```text
[gguf_converted] bytes=6178317216, reused=False, seconds=131.529
[model_packed]   base_type=Q4_K_S, output_tensor_type=q8_0, overrides=36, seconds=23.705
[size_checked]   fits=True, margin_bytes=25402464, weight_budget_bytes=2617245696
[smoke_tested]   chunks=2, passed=True, perplexity=16.0119, threshold=1000.0
```

Note `base_type`. The recipe drives every override, but the floor still maps
to a stock ftype, so a pack that goes wrong tends to go wrong by quietly
falling back to that floor rather than by failing.

**On bigger models the importance matrix stops being optional.** The 3B pack
above ran without one — `imatrix=None` in that log. At 3-bit on the 49B it
was the single largest contributor to closing the gap with the
baseline — the scoreboard puts it at about **81 % of the recipe's deficit**.
Pass it with `--imatrix`, which also lets pack run the per-tensor
reconstruction check below.

## 5. Check it before you trust it

Non-negotiable, and the reason is a real incident: a recipe once predicted
damage 1.44 and the packed artifact was **destroyed** — perplexity around
10⁶, top-token agreement 0.3 %. Nothing between plan and pack would have
caught it.

**The smoke test** (`--smoke-text`) runs a short perplexity pass on the
packed file and fails above a ceiling
([ADR-0017](https://github.com/Alberto-Codes/vramfit/blob/main/docs/adr/0017-post-pack-smoke-test.md)).
The 3B run above scored 16.0119 against a ceiling of 1000.

**That number is not a quality claim, and you shouldn't read it as one.**
The smoke test runs two chunks on the packed file and nothing else. It has
no f16 reference to compare against, so it can tell you the artifact still
produces language — it cannot tell you how much you lost. The ceiling looks
absurdly loose because it's a corpse detector: the 10⁶ artifact would have
tripped it instantly, and that is the whole job. Measuring what you actually
lost is `vramfit validate` and a real evaluation, which is the subject of
[the last post](/blog/2026-08-11-i-couldnt-tell-my-quantized-model-from-the-baseline).

**The reconstruction check** runs when you pack with `--imatrix` and
protections. It re-quantizes each protected tensor and measures how far it
moved, naming any tensor whose fit collapsed
([ADR-0022](https://github.com/Alberto-Codes/vramfit/blob/main/docs/adr/0022-within-layer-protections.md)).
On the 49B it took 4 min 36 s and passed. When it doesn't pass, the tensor it
names is the input to `--exclude-imatrix` from step 3.

Neither check tells you the artifact is *good*. They tell you it isn't
broken, which is the more urgent question.

## When this is the wrong tool

Off-the-shelf quantizations are good, they're free, and they're one download.
This is worth it when your budget is unusual, when you need to know the
artifact has no cliffs, or when you want the evidence.

The four-ceiling table in step 3 is the sharpest version of that test. If
your ceiling leaves the model comfortable, the solver has nothing to decide
and you should take a preset. The further your real ceiling sits from the
sizes the shelf happens to stock, the more this pays — and
[the companion post](/blog/2026-08-15-a-different-ceiling-is-a-different-recipe)
works that through on a model where the shelf runs out entirely.
