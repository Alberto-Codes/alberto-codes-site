# dev.to cut: Serve Gemma 4 31B on a 24 GiB card with the context it was packed for

Policy: [ADR-0004](../../adr/0004-syndication-and-canonical-urls.md).
Template: [syndication-cut.md](../../templates/syndication-cut.md).

---

## Before you write

- [ ] Canonical post is published and live at its final URL
- [ ] **This post is not already on another platform.** ADR-0004 decision 0:
      one piece, one platform
- [ ] Platform matches the post's Diataxis type (ADR-0004 decision 2):
      how-to to dev.to
- [ ] No diagram in this post, so nothing to rasterize. A cover image is
      still needed for the feed card; see the note under **Cover image**

---

## Publishing notes

**Canonical URL:** https://alberto.codes/blog/2026-09-06-serve-gemma-4-31b-on-a-24-gib-card-with-the-context-it-was-packed-for

**Platform:** dev.to — the canonical post is `type: how-to`, which ADR-0004
decision 2 routes here.

**Tags:** `ai, machinelearning, llm, tutorial`

**Cover image:** none in the post. The canonical post carries no diagram.
Options: reuse `src/assets/vramfit-pipeline.png` (already used for the
08-15 cut, so the two cuts would share a cover) or rasterize one of the
2026-09-02 explanation post's SVGs (`vramfit-24gib-kv-geometry.svg` is the
one that shows the context trade). Decide before publishing.

**Inline images, in order of appearance:** none.

**Word count:** 1,523 → 742 (prose, excluding code blocks and front matter)

**What this cut drops, and why:**

- The CUDA build-from-source path. dev.to readers want one install
  command; the Vulkan tarball is the frame the numbers were measured on.
  The CUDA path survives as one sentence pointing at the repo how-to.
- Step 5's "load one rung higher" reproduction and the frame explanation.
  That is the caveat that only matters to someone comparing boundaries
  across boxes. One sentence keeps the idea.
- The throughput aside in step 4.
- The "Where the numbers come from" list. Replaced with the card link and
  the explanation-post link, absolutized.
- The rented-H100 pointer paragraph.
- Internal cross-links absolutized to alberto.codes.

### Entering it on dev.to (v2 editor)

The v2 editor does **not** parse front matter. Use the front-matter block
below as a checklist and fill each field by hand:

- [ ] **Title** — its own input, above the tags
- [ ] **Body** — paste everything *after* the front matter block
- [ ] **Tags** — type each one followed by a comma so it commits as a chip.
      Do not set the field's value in one go
- [ ] **Canonical URL** — behind **Advanced Options**. A `🔗 Canonical` badge
      appears in the footer when it registers
- [ ] **Cover image** — upload only, there is no URL field
- [ ] **Preview** and read it before doing anything else

**There is no draft flag in v2.** `published: false` protects nothing here —
**Publish** publishes immediately. **Save Draft** is the only park button.

**Post-publish steps:**

- [ ] Confirm the "Originally published at" line renders under the title
- [ ] Record the live URL below

**Published at:** <url>  **on** <date>

This cut is frozen once published. If the canonical post changes
materially, annotate or delete — do not edit it to match.

---

## Article

```yaml
---
title: Serve Gemma 4 31B on a 24 GiB card with the context it was packed for
published: false
description: Download the published fit24gib pack, install llama.cpp at the pinned build, and serve it at 86,016 tokens of text context or 73,728 with an image aboard. Every flag comes from the model card.
tags: ai, machinelearning, llm, tutorial
cover_image: 
canonical_url: https://alberto.codes/blog/2026-09-06-serve-gemma-4-31b-on-a-24-gib-card-with-the-context-it-was-packed-for
---
```

*Originally published at [alberto.codes](https://alberto.codes/blog/2026-09-06-serve-gemma-4-31b-on-a-24-gib-card-with-the-context-it-was-packed-for)
on 2026-09-06. That version is the one I keep corrected.*

You have a 24 GiB card and you want to run Gemma 4 31B on it with as much
context as the card will hold. You want the server up.

This assumes a Linux box with a 24 GiB NVIDIA card, a working driver, and a
terminal. It does not assume any quantization background. The argument for
why a 14.92 GiB pack beats the 16.44 GiB official build on this card is
[a separate post](https://alberto.codes/blog/2026-09-02-googles-4-bit-gemma-already-fit-my-card),
and the evidence is on
[the model card](https://huggingface.co/Alberto-Codes/gemma-4-31B-it-fit24gib-GGUF).

Every number below is a published measurement, taken on an RTX 4090 running
llama.cpp b10362 on 2026-08-31. Your card is a different box, and the last
section is about what to do when a number does not reproduce.

## Before you start

**Disk.** The decoder is 14.92 GiB and the projector sidecar is 629 MiB.
Call it 20 GiB free with the llama.cpp tarball.

**Two files, one artifact.** The decoder alone serves text. Images need the
sidecar too.

**The license.** The weights carry the
[Gemma 4 license note](https://ai.google.dev/gemma/docs/gemma_4_license).

**The build is part of the claim.** The boundaries were measured at
llama.cpp b10362. A newer build allocates the KV cache its own way and may
land a rung higher or lower. Pin the build first.

## 1. Download the pack

The repo is public. No token needed.

```bash
uv tool install "huggingface_hub[cli]"
mkdir -p ~/models && cd ~/models
hf download Alberto-Codes/gemma-4-31B-it-fit24gib-GGUF \
  gemma-4-31B-it-fit24gib.gguf gemma-4-31B-it-mmproj-q4km.gguf \
  --local-dir .
```

| File | Bytes | Size |
|---|---|---|
| `gemma-4-31B-it-fit24gib.gguf` | 16,015,862,144 | 14.92 GiB |
| `gemma-4-31B-it-mmproj-q4km.gguf` | 659,537,504 | 629 MiB |

The card publishes the decoder's hash:

```bash
sha256sum gemma-4-31B-it-fit24gib.gguf
# 2a7bd7a7be6979c858258618ab576db573a7b671b45ee5e9785247341b8c3b1e
```

## 2. Install llama.cpp b10362

The [b10362 release](https://github.com/ggml-org/llama.cpp/releases/tag/b10362)
ships a Linux Vulkan build, and Vulkan b10362 is the backend the 24 GiB
boundaries were measured on:

```bash
cd ~
curl -LO https://github.com/ggml-org/llama.cpp/releases/download/b10362/llama-b10362-bin-ubuntu-vulkan-x64.tar.gz
tar xzf llama-b10362-bin-ubuntu-vulkan-x64.tar.gz
export BIN=~/llama-b10362
"$BIN/llama-server" --version
```

The version line reads `version: 10362 (4801e3c56)`. If you want CUDA,
build that commit from source with `-DGGML_CUDA=ON`; the vramfit repo's
[H100 how-to](https://github.com/Alberto-Codes/vramfit/blob/main/docs/how-to/serve-gemma-4-fit24gib-on-a-rented-h100.md)
has the exact commands. A different backend is a different frame, so treat
the boundaries below as the rung to test first, not a promise.

## 3. Serve text at the measured boundary

```bash
M=~/models
"$BIN/llama-server" -m "$M/gemma-4-31B-it-fit24gib.gguf" \
  -c 86016 -ngl 99 -np 1 --port 8991 > server.log 2>&1 &
```

Three flags carry the claim.

- `-c 86016` is the measured text boundary. The next rung, 90,112, fails
  to load.
- `-ngl 99` offloads every layer.
- `-np 1` is one slot. The b10362 server defaults to four, which on this
  geometry adds about 2,400 MiB of sliding-window cache and fails loads
  that fit at one.

Wait for `model loaded` in the log, then hit the health route. Do not wait
on `all slots are idle`; the CUDA build never prints it.

```bash
until grep -q "model loaded" server.log; do sleep 2; done
curl -s localhost:8991/health
```

The reply is `{"status":"ok"}`.

## 4. Send one request

```bash
curl -s localhost:8991/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "messages": [{"role": "user", "content": "In one sentence, what is a sliding-window attention layer?"}],
    "max_tokens": 64
  }' | python3 -c 'import json,sys; print(json.load(sys.stdin)["choices"][0]["message"]["content"])'
```

That answers from inside the 86,016-token envelope. It does not tell you
what a full envelope costs to decode: the card's boundary check decoded
five tokens, and throughput at the boundary is unmeasured.

## 5. Read the VRAM numbers back

```bash
nvidia-smi --query-gpu=memory.used,memory.free --format=csv
```

At the 86,016 boundary on the 4090 the load passed with 143 MiB free. That
is what a fit bar looks like: the card is full, and the next rung is the
one that fails. If you see a few gigabytes free, one of the three flags
above is not doing what you think, most often a default `-np 4` from a
wrapper script.

The boundary belongs to the box, the build, the backend, and the VRAM free
before load together. The card calls that the frame and prints it beside
every number. Write yours down the same way.

## 6. Serve images

```bash
"$BIN/llama-server" -m "$M/gemma-4-31B-it-fit24gib.gguf" \
  --mmproj "$M/gemma-4-31B-it-mmproj-q4km.gguf" \
  -c 73728 -ngl 99 -np 1 --mtmd-batch-max-tokens 264 \
  --port 8991 > server.log 2>&1 &
```

- `-c 73728` is the measured one-image boundary. The next rung, 77,824,
  loads and then fails at encode time.
- `--mtmd-batch-max-tokens 264` caps the encode batch at one 1280×720
  image. Without it the server packs up to 1,024 image tokens into one
  encode graph, two images share a graph, and the graph asks for 328 MiB
  against a 150.63 MiB one-image reserve. That crashed the server on the
  second image. With the cap, the same ladder filled the window to a clean
  context refusal.

Keep about 200 MiB free beyond the load. The image encode allocates at
request time, and this build crashes on that failure instead of refusing.

Write the image request to a file first. A base64 screenshot is bigger than
the single-argument limit a Linux shell allows.

```bash
python3 - <<'PY'
import base64, json
img = base64.b64encode(open("screenshot.png", "rb").read()).decode()
json.dump({"max_tokens": 64, "messages": [{"role": "user", "content": [
    {"type": "text", "text": "What is on this screen?"},
    {"type": "image_url", "image_url": {"url": "data:image/png;base64," + img}},
]}]}, open("req.json", "w"))
PY
curl -s localhost:8991/v1/chat/completions -H 'Content-Type: application/json' \
  -d @req.json | python3 -c 'import json,sys; print(json.load(sys.stdin)["choices"][0]["message"]["content"])'
```

One 768×768 image costs 256 decoder tokens on this pack. One 1280×720
screenshot costs 271 with its wrapper.

## What you should see

Measured 2026-08-31, RTX 4090, llama.cpp b10362 Vulkan, `-ngl 99 -np 1`,
4,096-token rungs:

| Serving shape | This pack | Google's QAT Q4_0 |
|---|---|---|
| Text only, max load | **86,016** (fails at 90,112) | 65,536 (fails at 69,632) |
| One image aboard, max load | **73,728** (encode fails at 77,824) | 49,152 (encode fails at 53,248) |

The gain is 20,480 tokens of text and 24,576 with an image, on that frame.

## If it does not fit

1. **Drop one rung.** Try 81,920 for text, 69,632 with an image. The
   81,920 text rung reproduced on 2026-08-31 with 465 MiB free at load.
2. **Check `-np`.** A wrapper that sets slots for you costs about 2,400
   MiB on this geometry.
3. **Check what else holds the card.** The ladders ran with 23,629 to
   23,631 MiB free before each load. A rung is about 320 MiB, so a browser
   or a second model can cost one.
4. **Serving images: keep the encode-batch cap.** It is the fix, not a
   tuning knob.
5. **A different backend is a different frame.** Measure your own ladder
   and report the frame with the number.

What you have at the end is not the card's number. It is a boundary
measured on your own box, with its frame written beside it, which is the
only kind of number the card ever claimed. The card, the recipe, and the
hashes live at
[gemma-4-31B-it-fit24gib-GGUF](https://huggingface.co/Alberto-Codes/gemma-4-31B-it-fit24gib-GGUF);
the tool is [vramfit](https://github.com/Alberto-Codes/vramfit).
