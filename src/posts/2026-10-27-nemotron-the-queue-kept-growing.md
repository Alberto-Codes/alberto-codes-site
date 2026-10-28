---
title: I sent my 4090 six receipts a second. The queue kept growing.
date: 2026-10-27
type: explanation
summary: Five incoming receipts a second kept the queue short. Six filled it during a five-minute run. The lower rate still timed out on one troublesome receipt.
tags:
  - ai
  - ocr
  - performance
  - local inference
---

In the first minute, receipts waited an average of 1.56 seconds before a
client worker started their request. By minute five, that wait had grown to 10.39
seconds. The queue filled and started refusing work.

I was sending six receipts a second to
[Nemotron Parse](https://huggingface.co/nvidia/Nemotron-3.5-Parse) on my RTX
4090. The model takes a receipt image and returns its text. Sending five
receipts a second kept the queue short for the same five minutes.
One extra receipt per second was enough to expose the difference.

The lower rate still had failures. Twenty-six requests timed out. Every one
was for the same receipt.

## Keep sending while the model is busy

The test measured what happened when receipts kept arriving at a fixed rate.
The client scheduled another receipt whether the earlier ones had finished
or not. At six per second, a new request was due roughly every 167
milliseconds. A slower response could not quietly slow down the test's
arrival rate.

I used 56 receipts from
[CORD-v2](https://huggingface.co/datasets/naver-clova-ix/cord-v2), rows 24–79
of its test split. One RTX 4090 ran Nemotron through
[vLLM](https://github.com/vllm-project/vllm), with the
[model and serving settings](https://github.com/Alberto-Codes/inference-lab/blob/3193fb28d46e875d4f39324d4ba743f058fb872c/serving/config.json)
fixed across the trials. Images were prepared and encoded before timing
began, so these measurements exclude document preparation.

![Scheduled arrivals enter a client queue with 64 waiting slots. A full queue rejects the new arrival. Sixteen client workers submit to a separate vLLM queue with up to eight active sequences. The chart measures delay from scheduled arrival to client worker start; the 30-second deadline also includes subsequent processing.](/nemotron-request-path.svg)

*The chart below measures delay before a client worker starts, including
scheduling delay. A request can then wait again inside vLLM.
[Runner and settings](https://github.com/Alberto-Codes/inference-lab/blob/3193fb28d46e875d4f39324d4ba743f058fb872c/docs/explanation/scaling-method.md).*

For the capacity tests, the client cycled through the same 56 receipts after
warming each image. These were **repeated, cached inputs**. Separate short
trials sent each new image once after resetting the parser's cache. Those
trials let me inspect responses to fresh inputs, but were too short to
establish sustained capacity for new documents.

## The fourth minute changed the result

The initial sweep tested two, four, six, eight and twelve incoming receipts
per second. Each rate ran three times, with a minute of arrivals followed by
time for outstanding requests to finish or expire.

At six per second, those short trials already showed waiting and timeouts,
but none rejected an arrival because the client queue was full. I then ran
five-minute checks at five and six per second.

![At six incoming receipts per second, average client queue wait rises from 1.56 seconds in minute one to 10.39 seconds in minute five. At five per second, it remains below 0.07 seconds.](/nemotron-scaling-queue.svg)

*Average delay from scheduled arrival until a client worker starts, including
scheduling delay. Full-queue rejections are excluded from the average and
counted separately. One five-minute trial per rate, using warmed, repeated receipts.
At six per second, the full queue rejected 13 arrivals in minute four and
two in minute five. The five-per-second run still had 26 timeouts.
Source: [per-minute audit](https://github.com/Alberto-Codes/inference-lab/blob/3193fb28d46e875d4f39324d4ba743f058fb872c/evidence/scaling-4090/stability-audit.json).*

| Five-minute run | Scheduled 5 receipts/s | Scheduled 6 receipts/s |
|---|---:|---:|
| Scheduled requests | 1,500 | 1,800 |
| Normal completions | 1,474 | 1,751 |
| Rejected because the queue was full | 0 | 15 |
| Timed out | 26 | 34 |

A normal completion here means nonempty output that ended with the model's
stop signal. It says nothing about whether the receipt was transcribed
correctly.

Six per second completed more work overall, but it also accumulated waiting
work. By the fourth minute, the bounded queue had started refusing arrivals.
The one-minute trials had understated that risk.

Five per second kept queueing low over the observed five minutes. That
puts the observed queue-stability boundary between the two tested rates for
this workload and configuration. Each longer condition ran once. Five per
second avoided a growing backlog, but its timeouts prevent calling it a
reliable service rate.

## One receipt kept running out of time

All 26 timeouts in the lower-rate run belonged to receipt 71. Separate
fresh-input trials returned unrelated repeated characters and exhausted
the output allowance for that same image.

![Receipt 71 input image beside two separate observations: in all three fresh-input trials, Nemotron repeated unrelated characters and reached its 8,744-token limit. In the five-minute run at five scheduled receipts per second, all 26 timeouts were this receipt; those requests have no returned bodies to inspect.](/nemotron-receipt-071-evidence.svg)

*Two different tests of the same image, not a reconstruction of the timed-out
responses. The [failure review](https://github.com/Alberto-Codes/inference-lab/blob/3193fb28d46e875d4f39324d4ba743f058fb872c/docs/reference/scaling-failures.md)
records source and output hashes. Visual checks were performed by Codex,
without independent human adjudication.*

*Image: NAVER CLOVA and Park et al., [CORD (2019)](https://github.com/clovaai/cord),
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
[Open the original receipt image](/nemotron-cord-test-071.png).
The image is unchanged, including the source blurring.*

In each of the first two fresh-input trials, this one receipt accounted for
about 49% of all returned output tokens. That is a count of generated output,
not a measurement of GPU time or evidence that this receipt caused the
queue to fill at six per second.

The same document failed repeatedly even at the rate that kept queueing low.
The longer run exposed two distinct problems: a backlog at six receipts per
second, and recurring timeouts at five.

## Inspect the results

This post records the [v0.2.0 scaling experiment](https://github.com/Alberto-Codes/inference-lab/tree/v0.2.0).
Its evidence, configuration and reproduction links are pinned to that
experiment's commit. The [current documentation](https://alberto-codes.github.io/inference-lab/)
follows `main` and can change as later experiments are added.

All 9,228 measured requests have a saved outcome, including rejections,
timeouts and outputs that reached their length limit. Those requests reused
56 documents; they are not 9,228 independent examples of receipt quality.

The [full results](https://github.com/Alberto-Codes/inference-lab/blob/3193fb28d46e875d4f39324d4ba743f058fb872c/docs/reference/scaling-results.md)
include the short saturation curve, resource counters and limitations.
The [reproduction guide](https://github.com/Alberto-Codes/inference-lab/blob/3193fb28d46e875d4f39324d4ba743f058fb872c/docs/how-to/run-scaling.md)
explains how to rerun the experiment or rescore saved responses without
running the model again. The earlier [24-receipt experiment](/blog/2026-10-26-nemotron-ocr-on-a-4090)
examines the separate question of whether normally completed responses
preserve the printed amounts.

Companion experiment: [inference-lab v0.2.0](https://github.com/Alberto-Codes/inference-lab/releases/tag/v0.2.0)
— the sustained receipt-load experiment, with saved request outcomes,
queue measurements and offline scoring.
