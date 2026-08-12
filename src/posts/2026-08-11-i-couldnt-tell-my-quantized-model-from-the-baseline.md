---
title: I couldn't tell my quantized model from the baseline. The instruments could.
date: 2026-08-11
type: explanation
summary: I built vramfit to fit Nemotron Super 49B on a 24 GiB RTX 4090 with measured damage instead of heuristics. It lost the head-to-head five times before it won. Then a conversational probe tied 19-19 against the baseline — which is the best argument for measuring I have.
tags:
  - python
  - ai
  - quantization
  - llm
  - evaluation
  - open source
---

## Fifteen questions, 19 to 19

I put two quantized copies of the same 49-billion-parameter model side by side and asked them the same fifteen questions.

One was mine: a mixed-precision recipe, measured layer by layer, solved against a hard 24 GiB budget. The other was the size-matched baseline everyone actually downloads — bartowski's Q3_K_S, a heuristic quant with far more users than mine will ever have.

I scored 25 points across factual recall, acronym expansion, and code executed against a fixed test suite. Greedy decoding throughout — temperature 0, top-k 1, seed 1234 — so nothing below is sampling luck.

**Nineteen to nineteen.**

They did not merely tie. They *agreed*. Both dropped the same four factual fields: three release years, each one year early, plus Qwen2.5's developer, where both named the model family instead of Alibaba. On the coding task both wrote `merge_intervals` with the same shallow copy and then mutated the caller's inner lists through it. Same defect, reached by the same reasoning.

The two points that separated them went one each way. The baseline expanded RoPE as "Relative Position Encoding." Mine wrote `dict_keys + dict_keys` in a size parser, a Python 2 habit that raises `TypeError` on contact.

So if you download both and chat with them, you will find nothing. You will conclude the measured recipe bought nothing.

You would be wrong — and that is the most useful result this project has produced.

## You cannot taste a quantization

Two cooks send out the same dish. At the table it tastes the same, and a diner with fifteen bites has no way to say otherwise. Send both to a lab against the original recipe and one is measurably closer — different fat ratio, different reduction, closer to the thing it was copied from. The diner isn't wrong about the taste. The diner is measuring the wrong thing.

That is exactly the gap here.

| Instrument | Mine | Baseline Q3_K_S |
|---|---|---|
| File size (budget: fits a 24 GiB card) | 20.36 GiB | 20.45 GiB |
| Perplexity, full WikiText-2 (564 chunks) | 8.517 ± 0.063 | 8.532 ± 0.064 |
| **Mean KL divergence vs the f16 original, 564 chunks** | **0.2873** | 0.2959 |
| Chunks where it holds the lower KL | **369 of 564 (65 %)** | — |
| Top-token agreement | 82.9 % | **83.4 %** |
| Fifteen-question probe | 19 / 25 | 19 / 25 |

The KL divergence line is the one that matters, and it is a 7.8σ paired result. It asks a question no conversation can: across 564 chunks of held-out text, how closely does the quantized model's entire output distribution track the 92.9 GiB f16 original it was compressed from?

Fifteen questions sample that distribution fifteen times. A 7.8σ separation over half a million tokens is not something a spot check can see — not because the spot check is sloppy, but because it is measuring taste while the claim is about fidelity.

There is a second question worth asking, and I ran it separately: does the compressed model still *do things*. Five task benchmarks — MMLU, GSM8K, HellaSwag, Winogrande, ARC-Challenge — came back five statistical ties against the baseline, none past 0.8σ. Equal capability, closer distribution, in a smaller file. That is the claim, and none of it is reachable by reading answers and forming an impression.

## The part I'd rather not publish

Here is the ledger the project actually ran, on the acceptance target — Nemotron Super 49B, 92.9 GiB at full precision, onto a 24 GiB RTX 4090.

| Attempt | Date | Result vs the baseline |
|---|---|---|
| First full loop | 2026-07-29 | **Lost** by 1.39 perplexity |
| Importance-matrix rematch | 2026-07-29 | **Lost again**, by less, for a different reason |
| Converged sensitivity map | 2026-07-31 | **Lost** — 0.62 behind |
| Honestly-priced map | 2026-08-02 | **Lost** |
| Assisted-priced map | 2026-08-06 | **Lost by the most yet** |
| 2-bit banned outright | 2026-08-06 | Tie |
| Pipeline packs its own winner | 2026-08-09 | **Won — 7.8σ** |

Five losses. The fifth was the worst artifact of the whole run, produced by the most carefully measured map I had. That one stung.

I am publishing the ledger because it is the only reason to believe the win. A project that shows you one green number has told you nothing about how many red ones it discarded to get there. Every loss above is on the public evidence page with its receipts, its date, and what it eliminated.

And they eliminated a lot:

- **Loss one located the real gap.** I packed my own uniform Q3_K_S from the same base with no importance matrix. It landed within 352 bytes of the baseline's size and still trailed it by 1.12 perplexity. The importance matrix — not my recipe — accounted for roughly 81 % of the deficit. Against same-conditions competition the measured mix was 0.26 behind, not 1.39.
- **Loss two proved damage doesn't simply add.** The solver predicted 0.0940 damage for a recipe; measured, it came in at 1.1234 — super-additive by 11.9×. Two days later a converged map produced a recipe with the *same* predicted total that measured sub-additive by 1.6×. Which layers you push to 2 bits decides whether their damage compounds. That result now gates every pack: a super-additive validation means solve again, not pack.
- **Loss five killed my favorite hypothesis.** Better price data was supposed to produce a better recipe. It produced the worst one on record. Honest inputs do not guarantee honest outputs when the frame you measure in and the frame you ship in disagree.
- **The win came from a bug in my own pack path, not a better solve.** The baseline fit one class of attention tensor ten times cleaner than anything I quantized — same tensor, same type, same base model, same importance matrix. I suspected quantizer flags, then toolchain vintage. Both were innocent: the relevant source was byte-identical across a year of releases. The actual cause was importance-matrix rows with extreme dynamic range across columns. Fixing that, and letting the pipeline apply the fix itself with no hand-edited flags, produced the artifact that won.

Five losses bought four facts. That is a reasonable exchange rate, and it is why the harness exists.

## What I'm not claiming

The baseline still wins top-token agreement by half a point, and that has never flipped.

The probe categories were chosen adversarially — each one is a place an earlier, unrecorded pass had suggested the baseline led. That lead did not survive greedy decoding. The selection cuts both ways: the tie says nothing about categories nobody probed.

And there is a control I have not run. When both models drop the same four fields and write the same bug, the natural reading is that the mistakes come from the base model rather than from either compression. Natural is not measured. The f16 original never answered those fifteen questions, because at 92.9 GiB it does not fit the card and needs its own night on a CPU lane. Until that runs, the reading stays a reading. It is [tracked in the open](https://github.com/Alberto-Codes/vramfit/issues/143), and if the f16 gets those fields *right*, the result is more interesting than the one I have: both quantizations damaged recall the same way.

I would rather ship the gap named than ship the story clean.

## Where it lives

- **The tool:** [vramfit on GitHub](https://github.com/Alberto-Codes/vramfit) — scan, plan, validate, pack. MIT.
- **The model:** [Llama-3_3-Nemotron-Super-49B-v1_5-fit24gib-GGUF](https://huggingface.co/Alberto-Codes/Llama-3_3-Nemotron-Super-49B-v1_5-fit24gib-GGUF), with the evaluation numbers as a machine-readable sidecar.
- **The measurements:** the [sensitivity-map dataset](https://huggingface.co/datasets/Alberto-Codes/Llama-3_3-Nemotron-Super-49B-v1_5-sensitivity-maps) — the per-layer damage figures the recipe was solved from.
- **The full ledger:** [seventeen data points](https://github.com/Alberto-Codes/vramfit/blob/main/docs/explanation/evaluating-packed-models.md), 2026-07-28 through 2026-08-11, wins and losses in order.

The ecosystem's habit is to ship a quantized model with a checksum and a vibe. A checksum proves the file is the file. It proves nothing about whether the file is any good. I think a publication should carry both — provenance *and* evidence — and the fifteen-question tie is the cleanest demonstration I have of why the second one has to be measured rather than felt.

Next: the missing f16 control, then the same loop on a Qwen-class model, which only ships if it wins a head-to-head of its own.
