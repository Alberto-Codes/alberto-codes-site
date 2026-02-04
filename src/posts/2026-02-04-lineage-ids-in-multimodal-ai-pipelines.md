---
title: Lineage IDs in Multimodal AI Pipelines
date: 2026-02-04
type: explanation
summary: The simplest way to keep images, videos, model calls, and outputs tied together across retries and fan-out.
tags:
  - ai pipelines
  - lineage
  - distributed systems
  - celery
  - observability
  - openai
---

Multimodal pipelines look clean on a whiteboard:

- pull images + companion JSON
- render images → video
- send video + JSON to an AI API
- store outputs

Then you ship it and reality shows up: retries, partial failures, parallel workers, version bumps, and the occasional "why does this output not match the input we think it does?"

This is where lineage IDs earn their keep.

If you’ve ever worked a dinner rush, it’s the same problem. Tickets keep printing, stations work in parallel, and sometimes you have to refire a dish. If your containers aren’t labeled and your tickets aren’t tracked, you end up staring at the pass thinking: **is this plate actually for table 12?**

## What “lineage” means (in practice)

Lineage is just **the ability to answer “where did this come from?”** at every step.

- Which image set produced this `video.mp4`?
- Which `video.mp4` + metadata produced this model response?
- Which response produced this `final.json` we shipped downstream?
- If we retried, which attempt “won” and why?

Queue dashboards and worker metrics tell you *what ran*. Lineage tells you *what the run touched* — the digital equivalent of a ticket number plus labels on every prep container.

> Rule of thumb: if you can’t answer “which exact bytes went into this model call?”, you don’t have lineage — you have hopeful logging.

## The shape of a lineage-aware pipeline

This is what you're aiming for: a `run_id` that propagates through workers, durable receipts that link inputs/outputs, and provider request IDs that let you correlate with the API vendor later.

![Lineage flow through a multimodal pipeline](/lineage-flow.svg)

## The minimum viable lineage model

Keep it boring. You only need a few identifiers.

| Name | What it identifies | Why it matters | Kitchen analogy |
| --- | --- | --- | --- |
| `run_id` | One end-to-end workflow instance (created once at ingest) | Correlates everything across fan-out and retries | Ticket number |
| `step` | A named transformation stage (`fetch_images`, `render_video`, `call_ai`, `persist_outputs`) | Lets you reason about progress and partial failures | Station (prep, sauté, expo) |
| `attempt` | The retry count for a step | Distinguishes first-run vs refires | Refire count |
| `artifact_id` | A stable identifier for bytes (often a content hash) | Prevents “same path, different bytes” confusion | Labeled batch / container |

If you already use a task queue, you’ll also have a `task_id` per task execution. That’s useful for ops, but it’s not a workflow lineage ID by itself.

## Lineage vs idempotency vs tracing

These concepts are related, but they solve different problems:

- **Lineage** — "What produced this?" — artifacts and transformations across the whole workflow
- **Idempotency** — "What if this runs twice?" — make retries and duplicates harmless
- **Tracing** — "Where did the time go?" — timelines, spans, latency, bottlenecks

In practice, you'll often reuse the same `run_id` as a correlation handle across all three, but keep the semantics separate:

- Don't use a queue `task_id` as your lineage key.
- Don't use an idempotency key as your run identifier (it's usually *step-scoped*).
- Don't assume provider request IDs replace your own identifiers (they're necessary, not sufficient).

## A file-first implementation (works before you have a DB)

You can get 80% of the value with a directory per run and a couple JSON “receipts”.

```text
runs/
  2026-02-04T18-41-12Z_d5c1.../          # run_id (timestamp + UUID, for easy sorting)
    manifest.json                        # one place to start
    inputs/
      frames/0001.jpg
      frames/0002.jpg
      metadata.json
    steps/
      010_fetch_images/
        receipt.json
      020_render_video/
        video.mp4
        receipt.json
      030_call_ai/
        request.json
        response.json
        receipt.json
      040_persist/
        outputs.json
        receipt.json
```

The only “rule” is: **every step writes a receipt that declares its inputs and outputs**.

Here’s what a step receipt can look like:

```json
{
  "run_id": "2026-02-04T18-41-12Z_d5c1f0b4e6b84aef9a7be8d07f2c3a1b",
  "step": "render_video",
  "attempt": 1,
  "started_at": "2026-02-04T18:41:15Z",
  "finished_at": "2026-02-04T18:41:22Z",
  "inputs": [
    {"path": "inputs/frames/0001.jpg", "sha256": "…"},
    {"path": "inputs/frames/0002.jpg", "sha256": "…"},
    {"path": "inputs/metadata.json", "sha256": "…"}
  ],
  "outputs": [
    {"path": "steps/020_render_video/video.mp4", "sha256": "…", "media_type": "video/mp4"}
  ]
}
```

That's lineage: a tiny, append-only audit trail you can reconstruct into a graph later.

![Receipt chain linking artifacts via content hashes](/receipt-chain.svg)

Each step's receipt links inputs to outputs via content hashes — forming a chain you can traverse in either direction.

### Why content hashes beat "whatever the filename was"

When you’re debugging, the most painful failure mode is “file A got overwritten by a retry, and now A points to different bytes than it did yesterday.”

In kitchen terms: someone reused the same unlabeled container, and now “sauce” could mean three different things depending on who touched it last.

If your `artifact_id` is a content hash (ex: SHA-256), you get:

- Deduplication for free (same bytes → same ID)
- Cheap integrity checks (hash mismatch = corruption/overwrite)
- A stable join key across systems (filesystem, object storage, DB, logs)

You can still store by filename; just **record the hash in the receipt** so you have a stable identifier.

Here’s a tiny standard-library helper for hashing and run IDs:

```python
import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path


def new_run_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    return f"{ts}_{uuid.uuid4().hex}"


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()
```

For large video files, hashing adds I/O overhead (you're reading every byte). For most pipelines the auditability is worth it — but if it becomes a bottleneck, faster non-cryptographic hashes like xxHash or BLAKE3 work fine for artifact IDs.

## Propagating lineage through a task queue

The most important operational discipline is simple:

> Generate `run_id` once, then pass it to every task and log line.

In task-queue terms, that usually means your task signature always includes `run_id`, and every task writes its receipt under `runs/<run_id>/steps/<step>/…`.

Retries are expected in at-least-once systems (I wrote more about that in [Task Queues, Idempotency, and AI Pipelines](/blog/2026-02-02-task-queues-idempotency-and-ai-pipelines)). Lineage doesn’t prevent duplicates — it makes duplicates understandable.

## Structured logs (the breadcrumbs between receipts)

Receipts are your durable audit trail. Logs are your high-volume timeline.

The simple rule: **every log line emitted by workers should include `run_id`, `step`, and `attempt`.** Then add fields that make debugging cheap, like:

- `task_id` (from your queue)
- `artifact_id` / `sha256` for important inputs/outputs
- provider request/response IDs for model calls

If you use structured logging (for example `structlog`), you’re aiming for events that look like this:

```python
import structlog


log = structlog.get_logger().bind(
    run_id=run_id,
    step=step,
    attempt=attempt,
    task_id=task_id,
)
log.info("step_started")
log.info("step_finished", output_sha256=output_sha256, duration_ms=duration_ms)
```

```json
{
  "event": "step_finished",
  "run_id": "2026-02-04T18-41-12Z_d5c1f0b4e6b84aef9a7be8d07f2c3a1b",
  "step": "render_video",
  "attempt": 1,
  "output_path": "steps/020_render_video/video.mp4",
  "output_sha256": "…",
  "duration_ms": 7421
}
```

## Correlating AI API calls (OpenAI or otherwise)

When you call an AI API, you want to keep three IDs tied together:

> For every model call, tie together: **your** `run_id`, **their** request ID, and the **exact bytes** you sent and received.

A concrete OpenAI example:

- Send your own ID via the `X-Client-Request-Id` request header (ASCII, ≤ 512 chars).
- Log/store the server-generated `x-request-id` response header.

A practical pattern is:

- `steps/030_call_ai/request.json`: the request payload you sent (or a redacted version)
- `steps/030_call_ai/response.json`: the raw response body you received
- `steps/030_call_ai/receipt.json`: a summary that links inputs/outputs + provider IDs

When the API supports it, also include your identifiers in the request (for example: request metadata, a `user` field, or custom headers in your own gateway). The goal is that support tickets and logs can be traced with either **your** `run_id` or **their** request/response ID. OpenAI documents this under [Debugging requests](https://platform.openai.com/docs/api-reference/authentication?api-mode=responses#debugging-requests).

For a provider call receipt, you’re usually trying to capture something like:

```json
{
  "run_id": "2026-02-04T18-41-12Z_d5c1f0b4e6b84aef9a7be8d07f2c3a1b",
  "step": "call_ai",
  "attempt": 1,
  "provider": "openai",
  "client_request_id": "run=2026-02-04T18-41-12Z_d5c1f0b4e6b84aef9a7be8d07f2c3a1b;step=call_ai;attempt=1",
  "provider_request_id": "…",
  "provider_response_id": "…",
  "inputs": [{"path": "steps/020_render_video/video.mp4", "sha256": "…"}],
  "outputs": [{"path": "steps/030_call_ai/response.json", "sha256": "…"}]
}
```

Even if you later move storage to S3/GCS and logs to Splunk/Datadog, that “receipt” pattern still holds. It’s just a join table you can grep.

## What you get from doing this early

- **Debugging that scales** — "this output is wrong" becomes "this run_id, this step, this exact artifact hash"
- **Safer retries** — you can see which attempt produced which bytes, and detect overwrites
- **Replayability** — pick a `run_id`, re-run starting at a step, and keep the old receipts for comparison
- **Auditing** — you can answer "what did we send to the model?" without guessing

## Common pitfalls

- Treating a queue `task_id` as a workflow ID (great for ops, terrible for lineage).
- Writing outputs to fixed paths without `attempt` or hashes (retries overwrite history).
- Adding correlation IDs to *some* steps but not all (you break the chain).
- Logging raw prompts/inputs instead of receipts + hashes (you create privacy risk and still can’t reliably join artifacts).

## Key takeaways

- Create a `run_id` once at ingest and propagate it everywhere (tasks, logs, artifacts).
- Treat every step like a station: write a receipt that names exact inputs and outputs.
- Prefer content hashes for `artifact_id` so retries and overwrites don’t blur history.
- Capture provider request/response IDs for model calls so you can correlate later.
- Start file-first; you can always move the same receipts into a DB or a catalog later.

## Closing thought

You don't need a data catalog or a dedicated lineage platform to start. A `run_id`, a couple receipts, and disciplined propagation through your tasks will save you days of debugging — and a lot of unnecessary model spend — once your pipeline hits the dinner rush.
