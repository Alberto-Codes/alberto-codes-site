---
title: Serve Gemma 4 31B on a 24 GiB card with the context it was packed for
date: 2026-09-06
type: how-to
summary: Download the published fit24gib pack, install llama.cpp at the build the numbers were measured on, and serve it at 86,016 tokens of text context or 73,728 with an image aboard. Every flag comes from the model card or the vramfit repo's own serve how-to, and the section at the end says what to do when your card does not reach the boundary.
tags:
  - ai
  - llm
  - quantization
  - multimodal
  - vramfit
  - open source
---

## Who this is for

You have a 24 GiB card and you want to run Gemma 4 31B on it with as
much context as the card will hold. You have read, or do not care
about, the argument for why a 14.92 GiB pack beats the 16.44 GiB
official build on this card. You want the server up.

Assumed: a Linux box with a 24 GiB NVIDIA card, a working driver, and
a terminal. Not assumed: any quantization background. The why is
[the explanation post](/blog/2026-09-02-googles-4-bit-gemma-already-fit-my-card),
and the evidence is on
[the model card](https://huggingface.co/Alberto-Codes/gemma-4-31B-it-fit24gib-GGUF).
This post repeats none of it.

Every number below is a published measurement, taken on an RTX 4090
running llama.cpp b10362 on 2026-08-31. Your card is a different box,
and the last section is about what to do when a number does not
reproduce.

## Before you start

**Disk.** The decoder is 14.92 GiB and the projector sidecar is
629 MiB. The llama.cpp build or tarball adds a few GiB. Call it
20 GiB free.

**Two files, one artifact.** The decoder alone serves text. Images
need the sidecar too. Both download in one command below.

**The license.** The weights carry the
[Gemma 4 license note](https://ai.google.dev/gemma/docs/gemma_4_license).
Read it before you serve them to anyone but yourself.

**The build is part of the claim.** The boundaries on the card were
measured at llama.cpp b10362. A newer build allocates the KV cache
its own way and may land a rung higher or lower. Pin the build first,
reproduce the boundary, then move if you want to.

## 1. Download the pack

The repo is public. No token needed.

```bash
uv tool install "huggingface_hub[cli]"
mkdir -p ~/models && cd ~/models
hf download Alberto-Codes/gemma-4-31B-it-fit24gib-GGUF \
  gemma-4-31B-it-fit24gib.gguf gemma-4-31B-it-mmproj-q4km.gguf \
  --local-dir .
```

What lands:

| File | Bytes | Size |
|---|---|---|
| `gemma-4-31B-it-fit24gib.gguf` | 16,015,862,144 | 14.92 GiB |
| `gemma-4-31B-it-mmproj-q4km.gguf` | 659,537,504 | 629 MiB |

Check the decoder before you trust it. The card publishes the hash:

```bash
sha256sum gemma-4-31B-it-fit24gib.gguf
# 2a7bd7a7be6979c858258618ab576db573a7b671b45ee5e9785247341b8c3b1e
```

## 2. Install llama.cpp b10362

Two ways. The first is the same build number and the same backend the
card's boundaries were measured on. The second is the path the repo's
rented-H100 how-to takes.

**Prebuilt Vulkan tarball.** The
[b10362 release](https://github.com/ggml-org/llama.cpp/releases/tag/b10362)
ships a Linux Vulkan build:

```bash
cd ~
curl -LO https://github.com/ggml-org/llama.cpp/releases/download/b10362/llama-b10362-bin-ubuntu-vulkan-x64.tar.gz
tar xzf llama-b10362-bin-ubuntu-vulkan-x64.tar.gz
export BIN=~/llama-b10362    # the tarball unpacks flat into this directory
"$BIN/llama-server" --version
```

**Build from source with CUDA.** The release ships no Linux CUDA
tarball, so CUDA means a build. Pin the commit the tag points at:

```bash
git clone https://github.com/ggml-org/llama.cpp ~/llama.cpp
cd ~/llama.cpp
git fetch --tags origin
git checkout 4801e3c56    # the commit tag b10362 points at
cmake -B build -DGGML_CUDA=ON -DCMAKE_BUILD_TYPE=Release
cmake --build build -j
export BIN=~/llama.cpp/build/bin
"$BIN/llama-server" --version
```

Either way the version line reads `version: 10362 (4801e3c56)`. On
the rented H100 that build took 429 seconds. CUDA is a different
runtime from Vulkan, so treat the boundaries below as the rung to
test first, not a promise. Step 5 shows how.

## 3. Serve text at the measured boundary

Note what is free before you load. The card's ladders ran with
23,629 to 23,631 MiB free on a 24,564 MiB device, under a desktop.

```bash
nvidia-smi --query-gpu=memory.total,memory.free --format=csv
```

Then the command from the card, verbatim:

```bash
M=~/models
"$BIN/llama-server" -m "$M/gemma-4-31B-it-fit24gib.gguf" \
  -c 86016 -ngl 99 -np 1 --port 8991 > server.log 2>&1 &
```

Three flags carry the claim.

- `-c 86016` is the measured text boundary. The next rung, 90,112,
  fails to load.
- `-ngl 99` offloads every layer. Any layer left on the CPU frees
  VRAM and invalidates the comparison.
- `-np 1` is one slot. The b10362 server defaults to four, which on
  this geometry adds about 2,400 MiB of sliding-window cache and
  fails loads that fit at one.

Wait for `model loaded` in the log, then hit the health route. This
build logs `all slots are idle` only at trace verbosity, so do not
wait on it: a check on that line waits forever with the server
healthy.

```bash
while pgrep -x llama-server > /dev/null && ! grep -q "model loaded" server.log; do sleep 2; done
curl -s localhost:8991/health
```

The reply is `{"status":"ok"}`. If the loop returns before
`model loaded` appears, the server exited, and the tail of
`server.log` says why; see "If it does not fit" below.

## 4. Send one request

The server speaks the OpenAI chat shape. One text turn:

```bash
curl -s localhost:8991/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "messages": [{"role": "user", "content": "In one sentence, what is a sliding-window attention layer?"}],
    "max_tokens": 64
  }' | python3 -c 'import json,sys; print(json.load(sys.stdin)["choices"][0]["message"]["content"])'
```

That answers from inside the 86,016-token envelope. It does not tell
you what a full envelope costs to decode: the card's boundary check
decoded five tokens, and throughput at the boundary is unmeasured.
The throughput the card does publish was taken at 8,192 tokens of
context on the same 4090, 47.8 tokens per second for this pack
against 43.3 for Google's Q4_0.

## 5. Read the VRAM numbers back

While the server is up:

```bash
nvidia-smi --query-gpu=memory.used,memory.free --format=csv
```

At the 86,016 boundary on the 4090 the load passed with 143 MiB
free. That is what a fit bar looks like: the card is full, and the
next rung is the one that fails. If you see a few gigabytes free, one
of the three flags above is not doing what you think, most often a
default `-np 4` from a wrapper script.

To confirm the boundary is real on your box, stop the server and load
one rung higher:

```bash
pkill -f llama-server
until ! pgrep -x llama-server > /dev/null; do sleep 1; done
"$BIN/llama-server" -m "$M/gemma-4-31B-it-fit24gib.gguf" -c 90112 -ngl 99 -np 1 --port 8991
```

That load should fail. If it passes, your box idles with more VRAM
free than the card's did, and you have a higher boundary. The card
calls the tuple of box, build, backend, and free VRAM before load the
frame, and it prints the frame beside every boundary, because the
same file served 81,920 for text three days earlier in a frame with
less idle VRAM. Write yours down the same way. It is the only way two
boundaries compare.

## 6. Serve images

Images need the sidecar and two more flags. Stop whichever server is
still holding the card, start the image server from the card, and wait
for `model loaded` the same way as in step 3:

```bash
pkill -f llama-server
until ! pgrep -x llama-server > /dev/null; do sleep 1; done
"$BIN/llama-server" -m "$M/gemma-4-31B-it-fit24gib.gguf" \
  --mmproj "$M/gemma-4-31B-it-mmproj-q4km.gguf" \
  -c 73728 -ngl 99 -np 1 --mtmd-batch-max-tokens 264 \
  --port 8991 > server.log 2>&1 &
while pgrep -x llama-server > /dev/null && ! grep -q "model loaded" server.log; do sleep 2; done
```

- `-c 73728` is the measured one-image boundary. The next rung,
  77,824, loads and then fails at encode time.
- `--mtmd-batch-max-tokens 264` caps the encode batch at one
  1280×720 image, which is 264 image tokens. Without it the server
  packs up to 1,024 image tokens into one encode graph, two images
  share a graph, and the graph asks for 328 MiB against a 150.63 MiB
  one-image reserve. On 2026-09-02 that crashed the server on the
  second image at both configurations. With the cap, the same ladder
  filled the window to a clean context refusal.

Keep about 200 MiB free beyond the load. The image encode allocates at
request time, and this build crashes on that failure instead of
refusing.

An image request is the same chat shape with an `image_url` part
carrying a base64 data URL. Write it to a file first: a base64
screenshot is bigger than the single-argument limit a Linux shell
allows, and an inline `-d` fails with "Argument list too long".

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

One 768×768 image costs 256 decoder tokens on this pack, measured at
the server. One 1280×720 screenshot costs 271 with its wrapper.

## What you should see

The card's serve ladders, measured 2026-08-31, RTX 4090, llama.cpp
b10362 Vulkan, `-ngl 99 -np 1`, KV cache f16, 4,096-token rungs:

| Serving shape | This pack | Google's QAT Q4_0 |
|---|---|---|
| Text only, max load | **86,016** (fails at 90,112) | 65,536 (fails at 69,632) |
| One image aboard, max load | **73,728** (encode fails at 77,824) | 49,152 (encode fails at 53,248) |

The gain is 20,480 tokens of text and 24,576 with an image, on that
frame. Two of the three things that set a boundary, the build and the
box, are yours.

Quality is not the subject of this post. The card's five held-out
benchmarks put this pack at four ties and one win against Google's
build. Read the tables there, not here.

## If it does not fit

Work down this list in order. Each item is a boundary the card
already crossed.

1. **Drop one rung.** The rungs are 4,096 tokens. Try 81,920 for
   text, 69,632 with an image. The 81,920 text rung reproduced on
   2026-08-31 with 465 MiB free at load, so it is the safer first
   stop under a heavier desktop.
2. **Check `-np`.** A wrapper that sets slots for you costs about
   2,400 MiB of sliding-window cache on this geometry. One slot, or
   nothing here holds.
3. **Check what else holds the card.** The ladders ran with
   23,629 to 23,631 MiB free before each load. A rung is about
   320 MiB on this geometry, so a browser or a second model can cost
   one.
4. **Serving images: keep the encode-batch cap.** Every crash on the
   card's multi-image ladder traced to two images sharing one encode
   graph. `--mtmd-batch-max-tokens 264` is the fix, not a tuning
   knob.
5. **A different backend is a different frame.** CUDA, ROCm, or a
   newer llama.cpp allocates differently. Measure your own ladder
   with step 5 and report the frame with the number.

If you have more card than this, the repo has
[a how-to for serving the pack on a rented H100](https://github.com/Alberto-Codes/vramfit/blob/main/docs/how-to/serve-gemma-4-fit24gib-on-a-rented-h100.md).
It is the instrument behind the card's real-GUI campaign: a CUDA
build of the same b10362 tag, the same two files, and context 8,192
for single-image evaluation. The 24 GiB boundaries and the
encode-batch flag belong to the 4090 frame and do not carry over.

What you have at the end is not the card's number. It is a boundary
measured on your own box, with its frame written beside it, which is
the only kind of number the card ever claimed.

## Where the numbers come from

- **The pack and its card:**
  [gemma-4-31B-it-fit24gib-GGUF](https://huggingface.co/Alberto-Codes/gemma-4-31B-it-fit24gib-GGUF).
  The serve commands, the ladders, the reproduction traps, the hashes.
- **The map behind it:**
  [gemma-4-31B-it-sensitivity-maps](https://huggingface.co/datasets/Alberto-Codes/gemma-4-31B-it-sensitivity-maps),
  published 2026-09-04, so `vramfit plan` can re-solve this model for
  a different budget.
- **The baseline:**
  [google/gemma-4-31B-it-qat-q4_0-gguf](https://huggingface.co/google/gemma-4-31B-it-qat-q4_0-gguf),
  16.44 GiB.
- **The tool:** [vramfit](https://github.com/Alberto-Codes/vramfit),
  and its [releases page](https://github.com/Alberto-Codes/vramfit/releases).
- **The argument:**
  [the explanation post](/blog/2026-09-02-googles-4-bit-gemma-already-fit-my-card).
  The pipeline that built the file is
  [fit a model to the GPU you actually have](/blog/2026-08-15-fit-a-model-to-the-gpu-you-actually-have).
