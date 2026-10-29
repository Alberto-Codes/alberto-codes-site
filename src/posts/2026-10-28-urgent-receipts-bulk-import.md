---
title: I gave urgent receipts priority. The bulk import paid for it.
date: 2026-10-28
type: explanation
summary: Giving urgent receipts priority and reserved slots recovered most five-second deadlines. The bulk import completed less work and took longer to drain.
tags:
  - ai
  - ocr
  - performance
  - local inference
---

In one paired trial, 79 of 300 urgent receipt requests finished within five
seconds under FIFO. Giving urgent work priority and reserving two of eight
client dispatch slots raised that to 294. The bulk import paid for it: 40 fewer
normal completions, a longer drain, and 45 requests that expired before
dispatch.

The other two pairs showed the same direction. That is evidence for a
useful scheduling tradeoff in this workload. It is not a free capacity gain.

## Two consumers, one backend

A service desk needs a receipt read while someone waits. An accounting team
has a bulk import to finish. These are fictitious consumers, but their
competing requirements are concrete: the first needs a timely response; the
second needs its import completed.

I ran one [Nemotron Parse](https://huggingface.co/nvidia/Nemotron-3.5-Parse)
model on one RTX 4090. The model takes a receipt image and returns its text.
Each mixed trial scheduled
one urgent request per second for five minutes, plus a burst of 120 bulk
requests every 30 seconds. That made 300 urgent and 1,200 bulk requests.
The two consumers cycled independently through the same 56 CORD receipts.
The [method](https://github.com/Alberto-Codes/inference-lab/blob/v0.3.0/docs/explanation/shared-capacity-method.md)
records the document selection, including a receipt that failed repeatedly in
previous tests. Twenty other receipts remained reserved for later evaluation.

The five-second urgent deadline was fixed before any isolated or mixed
results. It represents an illustrative service-desk requirement. Earlier
light-load trials had roughly two-second p95 latency, which motivated the
starting target; the new isolated baseline checked its feasibility.

FIFO took waiting requests in arrival order. At equal scheduled times, the
bulk burst preceded the urgent request. The protected arm selected urgent
work first and limited bulk to six requests in flight. Bulk could not borrow
the two reserved slots. The six-request bulk cap stayed in place during
drain, after urgent arrivals stopped. Both arms allowed at most eight upstream requests.
This compared the combined effect of priority and reservation. It did not
isolate either mechanism with a separate ablation.

The mixed arms used the same arrival trace, document assignments, model
settings and 8,744-token output allowance. Every arm restarted the owned
parser and warmed all 56 inputs before measurement. These are warmed,
repeated inputs, not a fresh-document ingress benchmark. Preparation and
warmup were outside the measured window.

## Urgent requests nearly matched their performance when running alone

Each condition ran three times. All isolated baselines ran before the mixed
stage. Mixed order was FIFO then protected, protected then FIFO, and FIFO
then protected. Three repetitions expose some variation; they do not fully
balance position or establish a production tail guarantee.

| Repetition | Urgent alone: within 5 s | Mixed FIFO: within 5 s | Mixed protected: within 5 s | Protected gain over FIFO |
|---|---:|---:|---:|---:|
| 0 | 295/300 (98.3%) | 79/300 (26.3%) | 294/300 (98.0%) | 71.7 percentage points |
| 1 | 295/300 (98.3%) | 72/300 (24.0%) | 295/300 (98.3%) | 74.3 percentage points |
| 2 | 289/300 (96.3%) | 98/300 (32.7%) | 293/300 (97.7%) | 65.0 percentage points |

Every denominator includes **all 300 scheduled urgent requests**. Normal
completion means nonempty output with stop termination, not correct OCR.
Expired requests and truncated outputs count against attainment. Latency
starts at scheduled arrival and includes scheduling delay, queueing and
processing.

FIFO urgent deadline misses were 221, 228 and 202. Of those, 210, 217 and
196 expired while waiting; the rest completed normally after the deadline.
The protected arm had six, five and seven deadline misses. It dispatched
all urgent requests, but five or six outputs per trial truncated. The last
protected trial also had one late normal completion.

Successful urgent responses had p95 latency of 5.08–5.81 seconds under
FIFO and 2.26–2.41 seconds under protection. The all-outcome p95 ranges were
5.07–5.12 and 2.69–2.85 seconds respectively. Both views matter: rejecting
work quickly can otherwise make a latency distribution look better.

The third isolated urgent trial also exposed workstation timing noise.
Three requests expired without waiting for admission capacity, and three
normal completions missed the deadline. Recorded scheduled-arrival delay
reached 6.40 seconds. That observation is consistent with scheduler or host
jitter; it does not identify the cause. It remains in the baseline instead
of being rerun away. The protected policy did not establish 99% attainment,
even on these warmed inputs.

## Accounting paid in progress, waiting and expiry

The following counts include all normal bulk completions through drain.
Each trial scheduled 1,200 bulk requests.

| Pair | FIFO normal completions | Protected normal completions | Fewer with protection | Protected queue expiries | Final bulk outcome: FIFO / protected, seconds |
|---|---:|---:|---:|---:|---:|
| 0 | 1,175 | 1,135 | 40 | 45 | 319.87 / 352.56 |
| 1 | 1,176 | 1,127 | 49 | 52 | 320.93 / 353.93 |
| 2 | 1,179 | 1,132 | 47 | 47 | 318.82 / 353.11 |

Protection reduced normal bulk completions by 3.4–4.2% relative to the paired
FIFO count. FIFO had no bulk queue expiries. Its 25, 24 and 21 unsuccessful
bulk requests truncated. Protection had 20, 21 and 21 truncations, in
addition to the queue expiries. It left 65, 73 and 68 bulk requests without a
normal completion, compared with 25, 24 and 21 under FIFO.

**No trial completed the whole bulk import normally.** The last-outcome
times above describe how long the trial took to settle its remaining work.
They are not successful whole-job completion times; those remain unknown.
All six mixed trials drained before the 480-second absolute bound.

Bulk throughput also depends on the denominator:

| Pair | FIFO completions/s during arrivals | Protected during arrivals | FIFO including drain | Protected including drain |
|---|---:|---:|---:|---:|
| 0 | 3.917 | 3.380 | 3.673 | 3.219 |
| 1 | 3.920 | 3.367 | 3.664 | 3.184 |
| 2 | 3.930 | 3.397 | 3.698 | 3.206 |

Maximum observed bulk wait rose from 24.73–30.44 seconds to 60.05–60.29
seconds. The protected backlog reached its sixty-second deferral limit;
small overshoots reflect when the scheduler observed expiry. Protection
deferred 1,190 bulk requests in each trial, compared with 1,145–1,155 under
FIFO. These include requests that ultimately expired.

The reservation also left 171.17, 184.90 and 173.39 dispatch-slot seconds
unused while bulk work waited. This measures unused client admission slots,
not GPU idle time. One slot unused for one second contributes one slot-second.
The experiment cannot assign the observed benefit separately to priority,
reservation or a particular GPU execution mechanism.

For the stated service desk, the policy recovered most of the urgent-only
attainment. For accounting, a promise to finish every import would still
need a strategy for expired and truncated work. That recovery work was not
implemented or priced here. Whether this tradeoff is acceptable depends on
both consumers' requirements.

## A failed baseline stays in the evidence

The first two isolated bulk trials completed 1,178 and 1,176 requests
normally, with 22 and 24 truncations. Their drain-inclusive rates were
3.705 and 3.692 normal completions/s. These provide two usable bulk-capacity
baselines, not three.

The third isolated bulk trial had one connection failure. Backend execution
became uncertain, so the runner stopped new dispatch. It retained 406 normal
completions, nine truncations, one transport error and 784 explicit
`backend_uncertain` outcomes. All 1,200 scheduled requests remained accounted
for. This trial is excluded from capacity comparisons and was not silently
replaced. The later arms reset the owned parser before warmup.

A client losing its connection does not prove the backend stopped processing
its request. Releasing that slot and continuing would risk moving an
uncontrolled backlog into the model server. The mixed trials had no recorded
transport timeouts or HTTP failures. Their quality and deadline failures
remain separate.

## The policy did not make OCR correct

Protected urgent numeric-string recall was 81.0–81.5% against the partial
CORD references. Each protected trial had 213 scheduled urgent requests with
at least one missing annotated numeric string. This includes missing output
from failed generation. It is a diagnostic count, not 213 independently
verified receipt errors.

FIFO's aggregate urgent recall was much lower, at 22.2–27.6%, because most
urgent work expired without a response. That difference does not show that
priority changed the model's recognition ability. The bulk diagnostic also
includes work that never reached inference.

The [October 26 pilot](/blog/2026-10-26-nemotron-ocr-on-a-4090) already showed
a changed price in a normally completed response. Numeric-string recall
does not establish field association. CORD has partial annotations and known
label discrepancies. Repeating 56 receipts increases load, not independent
quality coverage. No verified-correct-output count is claimed here.

## Inspect the results

This post records the [v0.3.0 shared-capacity experiment](https://github.com/Alberto-Codes/inference-lab/tree/v0.3.0).
Its evidence and reproduction links use that immutable experiment snapshot.
The [current documentation](https://alberto-codes.github.io/inference-lab/)
follows `main` and can change as later experiments are added.

The [saved report](https://github.com/Alberto-Codes/inference-lab/blob/v0.3.0/evidence/shared-capacity-4090/report.json)
retains all twelve trial summaries, three mixed-policy pairs and the excluded
bulk-baseline comparisons. All 13,500 scheduled measured requests have outcomes;
warmup remains separate. The
[evidence bundle](https://github.com/Alberto-Codes/inference-lab/tree/v0.3.0/evidence/shared-capacity-4090)
includes the frozen protocol, archived raw responses, policy decisions,
telemetry, executable source and verification records.

The [offline reproduction guide](https://github.com/Alberto-Codes/inference-lab/blob/v0.3.0/docs/how-to/run-shared-capacity.md#reproduce-the-saved-measurement-without-a-gpu)
starts from the committed archive. It explains how to verify its hash, extract
the records, regenerate the report with the frozen source and run the independent
audit. It needs no receipt images, model weights or GPU. The
[review record](https://github.com/Alberto-Codes/inference-lab/blob/v0.3.0/docs/reference/shared-capacity-review.md)
records exact reproduction, service restoration and the limits of the validation.

The policy recovered most of the urgent-only deadline performance while
leaving more bulk work unfinished. That result applies to one backend,
one fixed combined policy and warmed, repeated receipts. It does not establish
fresh-document capacity or a production service guarantee.

Companion experiment: [inference-lab v0.3.0](https://github.com/Alberto-Codes/inference-lab/releases/tag/v0.3.0)
— the urgent-and-bulk admission experiment, with repeated paired trials,
retained failures and independently reproducible evidence.
