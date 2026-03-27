---
title: "Paper to PyPI in 72 hours: Building the first TurboQuant vLLM plugin"
date: 2026-03-27
type: explanation
summary: "Google published TurboQuant at ICLR 2026 for text models. 72 hours later, turboquant-vllm was on PyPI — the first implementation validated on vision-language models and the first vLLM plugin. One flag to enable, 3.76x KV cache compression."
tags:
  - ai
  - quantization
  - gpu
  - vision-language-model
  - inference-optimization
  - vllm
---

There's a difference between nailing a recipe at home and running it on a restaurant line. At home you control the heat, the timing, the single plate going out. On the line, you need it to work with different stoves, multiple tickets firing at once, and a kitchen that wasn't built around your dish. The [first post](/blog/2026-03-26-i-ran-turboquant-on-a-vision-model-the-first-output-was-garbage) was the home kitchen version — implementing TurboQuant from the paper, finding what works and what breaks. This post is about getting it on the line.

Google published the [TurboQuant paper](https://arxiv.org/abs/2504.19874) on March 24, 2026. By March 27, `turboquant-vllm` was on PyPI serving compressed video inference through vLLM's OpenAI-compatible API. One flag to enable:

```bash
pip install turboquant-vllm[vllm]
vllm serve allenai/Molmo2-8B --attention-backend CUSTOM
```

3.76x KV cache compression. Near-identical output quality. No code changes.

This post is about the production journey — the decisions that turned a [research implementation](/blog/2026-03-26-i-ran-turboquant-on-a-vision-model-the-first-output-was-garbage) into a pip-installable plugin in 72 hours, and why nobody else has tested TurboQuant on vision-language models.

## The gap nobody filled

Every other TurboQuant implementation I could find — and there are [several](https://github.com/search?q=turboquant&type=repositories) — tests exclusively on text models: Qwen, Gemma, Mistral, Llama. Google's own paper benchmarks on Gemma, Mistral, and Llama-3.1-8B. Text only.

Vision-language models are a harder test case. A 12-second video clip through Molmo2-4B produces ~11,000 visual tokens — 10x longer than typical text prompts. That means 10x more KV cache memory, 10x more opportunities for precision bugs to compound across 36 transformer layers.

The existing VLM KV cache compression literature takes an entirely different approach: token pruning and sparsification (VL-Cache, Dynamic-LLaVA, ZipVL). These methods decide which tokens to *discard*. TurboQuant compresses the tokens you *keep*. They're complementary — you could stack TurboQuant on top of pruned caches for even greater savings.

Nobody had validated whether TurboQuant's vector quantization survives the visual token regime. Now someone has.

## What shipped

**turboquant-vllm 1.0.0** is a vLLM plugin, not a fork. It registers via `vllm.general_plugins` entry points — the same mechanism vLLM uses for official backends. Install it, pass `--attention-backend CUSTOM`, and the TQ4 backend handles everything:

![turboquant-vllm plugin architecture](/turboquant-vllm-architecture.svg)

1. **Compress** — Each new KV vector is rotated by a fixed orthogonal matrix, quantized to 4-bit Lloyd-Max centroids, and nibble-packed (two indices per byte)
2. **Store** — Compressed pages use 68 bytes per token per head, vs 256 for FP16
3. **Decompress** — Only new tokens are decompressed per decode step (incremental dequantization)
4. **Attend** — Standard Flash Attention runs on the decompressed cache

For HuggingFace users, `CompressedDynamicCache` wraps `DynamicCache` and compresses transparently on every `cache.update()`.

### The numbers

Molmo2-4B on RTX 4090, 11K visual tokens from a Seinfeld video clip:

| Metric | Baseline | TQ4 Compressed |
|--------|----------|----------------|
| KV cache | 1,639 MiB | **435 MiB (3.76x)** |
| Output quality | Detailed scene description | **Near-identical** (100+ tokens match word-for-word) |
| Decode overhead | — | 1.78x |

Molmo2-8B: same 3.76x compression ratio, correctly identifies all Seinfeld characters. Full 23-minute episode processed across 4 clips at 24 tok/s.

## Design decisions that mattered

### Plugin, not fork

Other vLLM TurboQuant efforts are forks (brittle, hard to update) or monkey-patches (fragile, version-dependent). `turboquant-vllm` uses vLLM's official plugin entry point:

```toml
[project.entry-points."vllm.general_plugins"]
tq4_backend = "turboquant_vllm.vllm:register_tq4_backend"
```

`pip install` registers the backend. `--attention-backend CUSTOM` activates it. No patching, no forking, no maintenance burden when vLLM updates.

### Incremental dequantization

The naive approach decompresses the entire KV cache at every layer at every decode step. For 11K tokens across 36 layers, that's 3.36x overhead.

The fix: decompress only the 1 new token per step, append it to a running buffer, let standard Flash Attention handle the rest. Overhead drops to 1.78x. This optimization isn't in the Google paper — it's what makes TQ4 practical for production serving.

### Cross-platform Triton

The fused kernels (compress, decompress, Q@K^T, Flash Attention + TQ4) run on both NVIDIA CUDA and AMD ROCm without code changes. I validated on a Radeon 890M iGPU — 84 of 84 GPU-parametrized tests pass with bit-identical math.

KV cache compression is most useful on memory-constrained hardware — exactly where AMD's consumer GPUs sit.

## Validation depth

The v1.0.0 release includes:

- **180+ tests** across 9 test files, 95%+ coverage
- **16 GPU experiments** — each building on the last, documenting failures alongside successes
- **Cross-platform validation** — NVIDIA RTX 4090 + AMD Radeon 890M (ROCm)
- **Production container test** — installed from PyPI into stock `vllm/vllm-openai:latest`, served Molmo2-8B video inference with zero errors
- **100% docstring coverage** enforced by [docvet](https://github.com/Alberto-Codes/docvet)

The experiment logs document failure modes nobody else has published: the [fp16 norms trap](/blog/2026-03-26-i-ran-turboquant-on-a-vision-model-the-first-output-was-garbage#four-things-i-learned-the-hard-way) at 10K+ tokens, QJL correction being invisible in standard attention, and multi-layer precision drift in fused kernels. These are landmines in every other implementation that hasn't hit 10K+ visual tokens.

## What's next

- **Upstream vLLM contribution** — there's an [open feature request](https://github.com/vllm-project/vllm/issues/38171) with 49 upvotes for TurboQuant support. The plugin is a staging ground.
- **Flash Attention fusion** — the fused Triton kernel achieves 17.8x on the Q@K^T micro-benchmark but needs full softmax+V fusion for multi-layer correctness
- **Stacking with token pruning** — combining TurboQuant compression with VL-Cache-style sparsification for multiplicative savings on VLMs

The full implementation, 16 experiment logs, and architecture docs are at [github.com/Alberto-Codes/turboquant-vllm](https://github.com/Alberto-Codes/turboquant-vllm).

```bash
pip install turboquant-vllm[vllm]
vllm serve your-model --attention-backend CUSTOM
```
