---
title: I ran Nemotron Parse on a 4090. Then I checked the numbers.
date: 2026-10-26
type: explanation
summary: All 48 measured requests completed on my RTX 4090. One receipt's 79,500 came back as 79,300. A small CORD experiment shows what completion, text overlap and numeric recall each leave out.
tags:
  - ai
  - ocr
  - evaluation
  - local inference
---

The garlic pepper beef cost 79,500. Nemotron read it as 79,300.

The request completed normally. So did every other measured request in my
local document-parsing experiment. I checked the returned text against the
receipt image and the dataset annotations.

I ran NVIDIA's [Nemotron-3.5-Parse](https://huggingface.co/nvidia/Nemotron-3.5-Parse)
through [vLLM](https://github.com/vllm-project/vllm) on one RTX 4090, using
24 real receipts from
[CORD-v2](https://huggingface.co/datasets/naver-clova-ix/cord-v2), a public
dataset of receipt images with annotations for selected content.

Nemotron Parse returns document text with layout and class markers, including
table structure. This experiment evaluates the extracted text and numeric
strings. I did not measure layout or table-structure accuracy.

## Receipt 20: a changed digit

Receipt 20 and the two examples later in this post were the three
lowest-overlap cases selected for judge review, not representative samples.
The expected text comes from CORD's annotations. The Nemotron excerpts
come from the measured concurrency-one run. Both are saved in
[scores.json](https://github.com/Alberto-Codes/inference-lab/blob/1b412ff74cee4b60d07b17d24e41daef4df18335/evidence/cord-test-24/scores.json).
In each comparison, **Expected text** comes from CORD's annotations:
the dataset's answer key for selected receipt content, not a full-page
transcription. **Nemotron returned** is text from the model's saved response.
The photograph is the input image, so you can check the printed amounts too.
I have omitted coordinate and class markers from the excerpts.

| What I checked | Expected text — CORD | Nemotron returned |
|---|---|---|
| Garlic pepper beef price | `79,500` | `79,300` |
| Receipt total | `377,859` | `377 g EESF` |

**The price changed, and the total was not preserved.** I checked both
expected amounts against the photograph below. The table aligns excerpts
for comparison; it does not reproduce complete model-generated lines.

Nemotron returned the item names and prices in separate blocks. The price
above is excerpted from its amount column:
`64,500 79,300 69,500 64,500 47,600`.
The total entry quotes the damaged text in the total's image region;
it is not a reconstructed `TOTAL` field.

The output also added unrelated prose, including
`and then slice your oven until 100s`. The numeric check found 12 of 16
annotated strings; its missing list includes `79,500` and `377,859`.

**Input image — receipt 20**

![CORD test-020: garlic pepper beef is priced at 79,500, and the printed total is 377,859.](/nemotron-cord-test-020.jpg)

*CORD-v2 test row 20 (`test-020.jpg`), one of the three lowest-overlap cases.
Image: NAVER CLOVA and Park et al., [CORD (2019)](https://github.com/clovaai/cord),
[CORD-v2 dataset](https://huggingface.co/datasets/naver-clova-ix/cord-v2),
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Unmodified copy;
blurred regions are present in the source.*

## What I ran

I selected CORD-v2 test rows 0–23 before inference and kept the prompt fixed.
The [manifest](https://github.com/Alberto-Codes/inference-lab/blob/1b412ff74cee4b60d07b17d24e41daef4df18335/evidence/cord-test-24/manifest.json)
records the annotations, image hashes and pinned dataset revision.

The local server used [vLLM 0.26.0](https://github.com/vllm-project/vllm/releases/tag/v0.26.0)
and the [Nemotron Parse plugin 3.5.0.post7](https://huggingface.co/nvidia/Nemotron-3.5-Parse/blob/62cb1e4ba153d113ff64aaf2be6e068c377cf53c/pyproject.toml), with
bfloat16 weights on one GPU. My [4090 serving profile](https://github.com/Alberto-Codes/inference-lab/blob/1b412ff74cee4b60d07b17d24e41daef4df18335/docs/reference/serving.md)
used FlashAttention 2, disabled multi-token prediction and enabled eager
execution. A Python client sent each image to the server and saved the
returned text. The full configuration, model revision and GPU
record are in [results.json](https://github.com/Alberto-Codes/inference-lab/blob/1b412ff74cee4b60d07b17d24e41daef4df18335/evidence/cord-test-24/results.json).

I warmed each image once, then made one measured sweep with one request at
a time and another with four requests in flight. All 48 measured requests
completed with normal stop termination. The 24 warmup requests completed too.
The [request log](https://github.com/Alberto-Codes/inference-lab/blob/1b412ff74cee4b60d07b17d24e41daef4df18335/evidence/cord-test-24/requests.jsonl)
keeps all of them.

## Three different answers

The same 24 receipts were measured at each concurrency, for 48 requests
in total.

| Concurrent requests | Completed | Pages/s | Median latency | Diagnostic ROUGE-L F1 | Exact numeric-string recall |
|---|---|---|---|---|---|
| 1 | 24/24 | 2.12 | 415 ms | 0.801 | 212/241 (88.0%) |
| 4 | 24/24 | 5.99 | 634 ms | 0.802 | 212/241 (88.0%) |

Timing comes from [results.json](https://github.com/Alberto-Codes/inference-lab/blob/1b412ff74cee4b60d07b17d24e41daef4df18335/evidence/cord-test-24/results.json);
quality comes from the corrected [scores.json](https://github.com/Alberto-Codes/inference-lab/blob/1b412ff74cee4b60d07b17d24e41daef4df18335/evidence/cord-test-24/scores.json).

With four requests in flight, the 24-receipt sweep finished in 4.01 seconds
instead of 11.33: about six receipts per second instead of two. Median
response time rose from 415 to 634 ms. The batch finished sooner, while the
typical individual response took longer. Both sweeps matched 212 of 241
annotated numeric strings; that does not mean their outputs were identical.

Both sweeps used warmed image caches. The throughput timer includes client
scoring and evidence writes; latency covers HTTP inference and response
validation. One short sweep per setting describes this run, not sustained
serving capacity.

Completion tells me the request finished. ROUGE-L F1 measures ordered token
overlap, averaged across pages after removing formatting. Numeric recall
asks how many annotated numeric strings appeared in the output, counting
duplicates and preserving signs and separators exactly. It found 212 of 241.
It does not check whether a number belongs to the right field.

CORD's annotations cover selected content, not a full transcription of every
visible word. Extra visible text and a different reading order can lower
overlap without being recognition errors. These are diagnostic scores for
this pilot, not official CORD benchmark results or a financial accuracy rate.

I also had to correct my scorer. The first calculation counted LaTeX command
names as text. Offline rescoring removed those commands and table layout
syntax without repeating inference. `results.json` retains the initial
calculation; `scores.json` is the source for the quality figures above.

## Two more ways the scores can mislead

### Receipt 22: all the numbers, plus unrelated text

**Expected text — CORD annotations**

```text
2 [MD] SOFT STEAMED CHEESEC 20,000
2 [MD] SOFT STEAMED CHOCOCA 20,000
TOTAL 40,000 CASH 100,000 CHANGE 60,000
```

**Nemotron returned — selected excerpts**

The item and payment section:

```text
2 [MD] SOFT STEAMED CHEESEC20,000
2 [MD] SOFT STEAMED CHOCOCA20,000
TOTAL CASH CHANGE 40,000 100,000 60,000
```

Elsewhere in that same response, Nemotron also wrote:

```text
THE TOMOLE THANI THAT, HOME THANI
```

```text
SELLER AND BURGEMENT OF SPORING IN ALL HERETHING MEALS.
```

**All seven annotated numeric strings survived, but the response also
contained unrelated text.** The two item counts, two prices and three
payment amounts are present. That is what the numeric check establishes;
it does not establish correct field association or a clean transcription.

**Input image — receipt 22**

![CORD test-022: two item lines at 20,000 each, total 40,000, cash 100,000 and change 60,000.](/nemotron-cord-test-022.jpg)

*CORD-v2 test row 22 (`test-022.jpg`), one of the three lowest-overlap cases.
Image: NAVER CLOVA and Park et al., [CORD (2019)](https://github.com/clovaai/cord),
[CORD-v2 dataset](https://huggingface.co/datasets/naver-clova-ix/cord-v2),
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Unmodified copy;
blurred regions are present in the source.*

### Receipt 13: separators are part of the rule

| What I checked | Expected text — CORD | Nemotron returned |
|---|---|---|
| BASO KUAH line amount | `43.636` | `43,636` |
| Grand total | `51.300` | `51,300` |

**The digits in these amounts match, but the separators changed.** The
table aligns selected excerpts; the exact-string rule counts these as
mismatches.

The item row also shows a joined quantity and amount:

**Expected text — CORD annotations**

```text
BASO KUAH 1 43.636 43.636
```

**Nemotron returned — item-row excerpt, table separators retained**

```text
BASD KLAH & 1,43,636 & 43,636
```

The joined `1,43,636` is why treating the whole row as only a locale
conversion would be too generous. Across this receipt, the numeric check
found five of thirteen annotated strings. Accepting equivalent amounts
across locales would require a separate rule, applied deliberately.

**Input image — receipt 13**

![CORD test-013: BASO KUAH and mineral water, with dot-separated amounts including 43.636 and a grand total of 51.300.](/nemotron-cord-test-013.jpg)

*CORD-v2 test row 13 (`test-013.jpg`), one of the three lowest-overlap cases.
Image: NAVER CLOVA and Park et al., [CORD (2019)](https://github.com/clovaai/cord),
[CORD-v2 dataset](https://huggingface.co/datasets/naver-clova-ix/cord-v2),
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Unmodified copy;
blurred regions are present in the source.*

## Asking Gemma to check the text

I asked a local [Gemma](https://deepmind.google/models/gemma/) model to compare these
three Nemotron responses with the expected text. I used
[judgevet](https://alberto-codes.github.io/judgevet/), my typed judgment
client, to submit the scoring rubric. My library
[typevet](https://alberto-codes.github.io/typevet/) obtained Gemma's answer
probabilities from the local [llama.cpp](https://github.com/ggml-org/llama.cpp)
server. Gemma supplied the judgments; it saw the text, not the receipt images.

The saved review identifies the local model as `gemma-4-31b-kv9-text`.
The [typevet provider guide](https://alberto-codes.github.io/typevet/how-to/use-typevet-as-a-judgevet-provider/)
explains how these two libraries work together.

The [saved review](https://github.com/Alberto-Codes/inference-lab/blob/1b412ff74cee4b60d07b17d24e41daef4df18335/evidence/cord-test-24/judgevet-review.json)
uses an explicit rule: signs, digits, separators and percent signs must match.
It identified multiple numeric errors in receipt 20 and exact numeric
preservation in receipt 22. For receipt 13 it assigned 50.2% to exact
preservation and 49.4% to separator differences, despite the explicit rule.

Those probabilities are advisory, not accuracy percentages or ROUGE scores.
They have not been calibrated on these receipts. For the separator question,
the deterministic comparison already gives a direct answer. The second
model remained uncertain about a difference I could point to in the strings.

## Inspecting and repeating it

Start with [Inspect the saved experiment](https://alberto-codes.github.io/inference-lab/tutorials/first-result/).
It recalculates the scores and takes you to receipt 20's reference, output
and missing numbers. Setup needs Git, uv and an internet connection. After
setup, scoring uses the saved responses without a GPU or model server.

To repeat the receipt experiment on your GPU, follow the [receipt procedure](https://alberto-codes.github.io/inference-lab/how-to/evaluate-receipts/).
It covers input preparation, local serving, scoring and cleanup. The public
commands take explicit input and output paths and refuse to overwrite
existing evidence. Keep each new run in its own directory.

The parser procedure does not require an existing llama.cpp or Gemma server.
[Optional model review](https://alberto-codes.github.io/inference-lab/how-to/review-with-a-model/)
has setup instructions for judgevet, typevet and the local model server.
It asks for an explicit
server address and model ID. Deterministic scoring does not need that step.

The [results reference](https://alberto-codes.github.io/inference-lab/reference/receipt-results/)
explains the measurements and indexes the evidence. Those documentation
pages track `main`; the evidence links in this post pin the experiment
commit. Its [receipt procedure snapshot](https://github.com/Alberto-Codes/inference-lab/blob/1b412ff74cee4b60d07b17d24e41daef4df18335/docs/how-to/evaluate-receipts.md)
keeps the instructions for that revision available.

This is one fixed convenience subset, one model configuration and two short
measured sweeps. I did not test the whole CORD test split, another model or
whether cropping the blurred regions helps.

Companion experiment: [inference-lab v0.1.0](https://github.com/Alberto-Codes/inference-lab/releases/tag/v0.1.0)
— the local Nemotron Parse receipt pilot, with saved outputs and reproducible scoring.
