---
title: "From one model to seven: Making TurboQuant model-portable"
date: 2026-03-31
type: explanation
summary: "turboquant-vllm started as a Molmo2-only proof of concept. v1.3.0 validates seven model families — but getting there meant rewriting Triton kernels for non-standard head dimensions and teaching the cache about sliding window attention."
tags:
  - ai
  - quantization
  - gpu
  - vision-language-model
  - inference-optimization
  - vllm
---

A compression algorithm that only works on one model isn't a tool — it's a demo. When [turboquant-vllm v1.0.0](/blog/2026-03-27-paper-to-pypi-in-72-hours-building-the-first-turboquant-vllm-plugin) shipped, it was validated on exactly one architecture: Molmo2. The algorithm worked, the numbers were real (3.76x KV compression, ~97% cosine similarity), but every model has its own attention geometry. Head dimensions vary. Some layers use sliding windows. Triton kernels crash when you hand them a dimension that isn't a power of two.

v1.3.0 validates seven model families: Molmo2, Llama 3.1, Mistral 7B, Qwen2.5, Phi-3-mini, Phi-4, Gemma-2, and Gemma-3. Getting there required two things: fused kernels that actually perform well in production (v1.2.0), and kernel-level changes to handle the architectural diversity across those families (v1.3.0).

## Fused kernels: decompress and attend in one pass

The v1.1.0 architecture had a clean separation: decompress the KV cache from TQ4 to FP16 in HBM, then run standard attention on the decompressed data. Clean, but wasteful — every decode step wrote decompressed values to HBM just to read them back immediately.

v1.2.0 introduced fused paged TQ4 kernels that eliminate that round trip. The decode kernel reads compressed blocks directly from vLLM's page table, decompresses in SRAM (nibble unpack → centroid gather → norm scale), and computes Q@K^T with online softmax — all in a single Triton kernel. No HBM writes of decompressed cache.

![Fused kernel data flow: v1.1 separate passes vs v1.2 single fused pass](/turboquant-fused-kernel-flow.svg)

The concrete impact: HBM traffic drops from 1,160 to 136 bytes per token — an 8.5x reduction. A separate INT8 tensor core prefill kernel handles the prefill path with the same fusion strategy.

This wasn't just a performance optimization. It was the foundation for everything that followed. CUDA graph buffer pre-allocation eliminated kernel launch latency for decode. Feature gating allowed the fused path to coexist with the original decompress-first path as a fallback. And when container benchmarks (Experiments 022–023) surfaced OOM bugs in the scratch buffers, the fixes (v1.2.1, v1.2.2) landed in hours because the architecture was clean enough to patch confidently.

## The portability problem: Triton and power-of-two

Here's what I didn't appreciate until I tried running TQ4 on Phi-3-mini: Triton's `tl.arange` requires power-of-two ranges. Molmo2 has head_dim=128 — a power of two. Phi-3-mini has head_dim=96. The kernels crashed at compile time.

The fix sounds simple — pad to the next power of two and mask the boundary. In practice, it touched all five Triton kernels: `flash_attention`, `flash_attention_tq4`, `flash_attention_tq4_kv`, `tq4_compress`, and `tq4_decompress`. Each needed a `_next_pow2` helper, `HEAD_DIM_PAD`/`HALF_D_PAD` constants, and `d_mask` boundary guards to prevent out-of-bounds reads during the fused decompression step.

Gemma-2 and Gemma-3 added another dimension — literally. head_dim=256 required tuning the flash attention autotune search space (adding `BLOCK_M=32` for SRAM optimization). The kernel works, but the autotune cost was real.

The throughput penalty for non-pow2 dimensions is ~5–15%, which is honest and documented. For head_dim=128 models — the majority — there's zero penalty.

## Sliding window attention: not all layers compress equally

Gemma models use mixed attention: some layers are global (full context), others use sliding windows (fixed context window with cache eviction). Compressing a sliding window layer's cache breaks the eviction semantics — the cache needs to discard old entries, not keep them in compressed form.

The solution is a bypass. When `CompressedDynamicCache` encounters a layer with `is_sliding=True` (from HuggingFace's `DynamicSlidingWindowLayer`), it skips compression entirely and delegates to the original cache update. Global layers compress normally.

![Model portability: how head_dim and attention type determine the kernel path](/turboquant-model-portability.svg)

The implementation required `None` padding in the compressed key/value lists for SWA gaps (to keep layer indices aligned), SWA-aware guards in `get_compressed`, `get_seq_length`, and `compression_stats`, and a diagnostic warning when a Gemma-family config is detected but the cache was created without the model config (which means no SWA metadata). Thirteen new tests cover the bypass, warnings, and downstream guards.

## Verification at scale

Model-by-model validation needed a repeatable process, not ad hoc benchmarking. The `verify` CLI (`python -m turboquant_vllm.verify --model <name> --bits 4`) loads any HuggingFace model, runs TQ4 compression on random Gaussian input, and reports per-layer cosine similarity against the uncompressed output. Pass threshold: 0.99.

All eight regression models pass:

- **Molmo2-4B** — VLM, head_dim=128, cosine 0.9951
- **Llama 3.1 8B** — text, head_dim=128, lossless at temperature=0
- **Mistral 7B** — text, head_dim=128, lossless at temperature=0
- **Qwen2.5-3B** — text, head_dim=128, cosine ≥0.99
- **Phi-3-mini** — text, head_dim=96 (non-pow2), cosine 0.9952
- **Phi-4** — text, head_dim=128, cosine ≥0.99
- **Gemma-2-2b** — text, head_dim=256 + SWA, cosine 0.9951
- **Gemma-3-4B-it** — text, head_dim=256 + SWA, cosine 0.9951

Experiment 024 pushed further: Llama 3.1 and Mistral 7B through the full vLLM backend with zero code changes. Short prompts, 960-token passage comprehension, 5-turn conversations with 1,200+ KV tokens — all 6/6 PASS on both models. KV capacity: 1.88x advantage over FP8 baseline. At 16K context, TQ4 serves 6x concurrent requests versus baseline's 3x.

## What this means

turboquant-vllm is no longer a single-model proof of concept. If your model uses head_dim 64–256 and runs on vLLM, there's a reasonable chance TQ4 compression works out of the box. The verify CLI takes thirty seconds to check.

The fused kernels, the non-pow2 padding, the SWA bypass — these are the kind of changes that don't show up in a changelog but determine whether a tool survives contact with the real model ecosystem. v1.0.0 proved the algorithm. v1.3.0 proved the engineering.

## What's next

- **Upstream vLLM contribution** — [vllm#38171](https://github.com/vllm-project/vllm/issues/38171) has 49 upvotes. The fused paged kernel architecture is the candidate for contribution.
- **Flash Attention kernel fusion** — full multi-layer correctness for the fused path, reducing decode overhead further.
- **VL-Cache stacking** — combining TQ4 KV compression with token pruning for multiplicative savings on VLMs.

---

*[PyPI](https://pypi.org/project/turboquant-vllm/) | [Docs](https://alberto-codes.github.io/turboquant-vllm/) | [GitHub](https://github.com/Alberto-Codes/turboquant-vllm)*
