---
title: I ran TurboQuant on a vision model. The first output was garbage.
date: 2026-03-26
type: explanation
summary: I implemented Google's TurboQuant algorithm for KV cache compression and validated it on Molmo2 video inference on an RTX 4090 — 3.76x compression with near-identical output at 1.78x overhead.
tags:
  - python
  - ai
  - quantization
  - performance
  - open source
---

## The paper

Google published TurboQuant at ICLR 2026 — a method for compressing transformer KV caches from FP16 down to 3-4 bits per coordinate with near-optimal distortion. The theory is elegant: use Lloyd-Max optimal codebooks to quantize each coordinate independently after a random orthogonal rotation that spreads information across dimensions.

The paper validates on text-only LLMs — Gemma and Mistral. Other implementations have since appeared targeting LLMs on consumer hardware: [turboquant-pytorch](https://github.com/tonbistudio/turboquant-pytorch) on an RTX 3060, [turboquant_plus](https://github.com/TheTom/turboquant_plus) on Apple Silicon, and a native [llama.cpp integration](https://github.com/ggml-org/llama.cpp/discussions/20969). But as of March 2026, none of them target vision-language models or video input. I wanted to know if TurboQuant works on Molmo2 — Allen AI's open-source VLM — analyzing Seinfeld clips on a single RTX 4090. The TechCrunch coverage hit on March 25. My first commit was 11 PM that night. By 1:33 AM I had 3.76x compression validated on video.

## Why KV cache matters for video

When a vision model processes video, the KV cache grows fast. Molmo2 tokenizes each frame into ~81 visual tokens. A 30-second clip at 2fps produces ~11,000 tokens before the model generates a single word. At FP16, that's 1.6 GB of KV cache across 36 layers.

On a 24 GB RTX 4090, that 1.6 GB is budget you can't spend on longer clips, larger models, or higher frame rates. Compression directly translates to capability.

## Experiment 001: garbage

I built the full TurboQuant pipeline — Lloyd-Max codebook solver, two-stage quantizer, and a drop-in `DynamicCache` wrapper that compresses on write and decompresses on read. The paper recommends TurboQuantProd for keys: 2 bits for MSE quantization, 1 bit for QJL sign correction.

First test: ask Molmo2-4B "What is 2+2?"

| | Output |
|---|---|
| **Baseline** | "Four." |
| **TurboQuant** | "The number 222 is is a number..." (garbled repetition until max tokens) |

## What the paper assumes you have

You have a 3-bit budget per coordinate. The paper's recommended approach, TurboQuantProd, splits it: 2 bits for MSE quantization, 1 bit for QJL sign correction. That split makes sense when you have a custom attention kernel that uses `estimate_inner_product()` — QJL correction enables unbiased dot product estimation directly on compressed data.

But in drop-in mode, standard attention decompresses the keys first and computes `Q @ K.T` on the full vectors. QJL is invisible to standard attention. It's like spending a third of your ingredient budget on a garnish that never leaves the kitchen — the diner never sees it, and the dish suffers because you skimped on the protein.

![TurboQuant bit budget: splitting 3 bits into 2-bit MSE plus 1-bit QJL produces 87% cosine similarity and garbled output, while giving all 3 bits to MSE produces 95% cosine similarity and output identical to baseline](/turboquant-bit-budget.svg)

That means TurboQuantProd at 3 bits actually gives you 2-bit MSE reconstruction — roughly 87% cosine similarity. Compounded across 36 layers of autoregressive generation, 87% per layer cascades into noise.

The fix was one line: switch key compression from TurboQuantProd to TurboQuantMSE. Full 3-bit MSE gives ~95% cosine similarity. The same prompt now returned "Four." — identical to baseline. On an 11,000-token Seinfeld clip, both baseline and compressed produced coherent scene descriptions with only 1.3x overhead.

## The compression pipeline

![TurboQuant compression pipeline: KV tensors at FP16 (256 bytes per token) flow through norm extraction, Haar-random rotation, Lloyd-Max 4-bit scalar quantization, and nibble packing to produce uint8 indices plus fp32 norms at 68 bytes per token — 3.76x compression](/turboquant-kv-compression.svg)

Each KV vector gets its norm extracted (stored as fp32), gets rotated by a shared random orthogonal matrix to spread information across dimensions, then each coordinate is independently quantized using a Lloyd-Max optimal codebook. At 4 bits, two indices pack into one byte — standard bit-shift operations, no custom kernels.

## Nibble packing: the practical sweet spot

3-bit compression stored as uint8 gives only 1.94x — one 3-bit index per byte. Packing across byte boundaries requires custom kernels that don't exist in PyTorch or Triton. 4-bit is trivial: two indices per byte via bit shift. The extra bit also improves reconstruction quality.

| Mode | Bytes/token | Compression | Cosine similarity |
|------|-------------|-------------|-------------------|
| FP16 baseline | 256 | 1.0x | — |
| TQ3 (unpacked) | 132 | 1.94x | ~95% |
| **TQ4 (nibble-packed)** | **68** | **3.76x** | **~97%** |
| TQ3 (bit-packed) | 52 | 4.92x | ~95% |

TQ4 is the sweet spot: 3.76x compression with better quality than TQ3, using only standard PyTorch operations.

## Cutting the overhead in half

My first TQ4 implementation hit 3.76x compression but at 3.36x speed overhead — the cache wrapper re-dequantized all 11,000+ tokens at every layer at every decode step. That's like re-plating the entire service every time a new dish comes off the line. An 88 MB allocation plus a 128x128 rotation matmul, repeated 36 times per generated token.

The fix: maintain a running decompressed buffer and only dequantize the 1 new token per step — plate the new dish, leave the rest on the pass. Prefill still decompresses everything once, but decode drops from O(seq_len) to O(1) per step.

| Metric | Full dequant | Incremental |
|--------|-------------|-------------|
| Tokens/sec | 8.9 | **16.9** |
| Overhead | 3.36x | **1.78x** |
| Compression | 3.76x | 3.76x |

The first 100+ tokens match word-for-word between compressed and baseline output.

## Four things I learned the hard way

1. **FP16 norms are a trap.** At 10K+ tokens across 36 layers, fp16 norm precision loss compounds and flips low-confidence logits. Always use fp32 — it costs 2 extra bytes per vector.

2. **QJL is invisible in drop-in mode.** Without a fused attention kernel that operates directly on compressed data, the QJL correction does nothing. Give all bits to MSE.

3. **Peak VRAM is activation-dominated.** KV cache is ~9% of peak VRAM during prefill. During decode, the ratio shifts as the cache grows — that's where compression pays off. The savings are real in permanent storage but invisible to `torch.cuda.max_memory_allocated()` until sequences grow beyond prefill.

4. **Cache your Lloyd-Max codebooks.** A 36-layer model creates 64 compressors. Without `@lru_cache` on the scipy integration, startup takes 2+ minutes.

## From garbage to 3.76x

Two hours earlier, this pipeline produced "The number 222 is is a number..." Now it compresses 1.6 GB of vision-language KV cache into 435 MB with near-identical output quality. The fix that mattered most wasn't an optimization — it was understanding that QJL wastes a bit when you don't have a custom kernel.

A fused Triton kernel that computes `Q @ K.T` directly on compressed data already shows 17.8x speedup on micro-benchmarks. Multi-layer integration is blocked on full Flash Attention-style fusion — computing Q@K^T, softmax, and @V in a single kernel to avoid fp32/bf16 divergence compounding across 36 layers. That's the next milestone.

The code is MIT-licensed and works with any HuggingFace model:

```python
from transformers import DynamicCache
from turboquant_consumer import CompressedDynamicCache

cache = DynamicCache()
compressed = CompressedDynamicCache(cache, head_dim=128, bits=4)  # nibble-packed, 3.76x compression
# Pass cache to model.generate() — compression is transparent
```

The full implementation — 62 tests, five experiment logs, and a benchmark harness — is at [github.com/Alberto-Codes/turboquant-consumer](https://github.com/Alberto-Codes/turboquant-consumer).
