---
title: Serve compressed VLM inference from a container
date: 2026-03-28
type: how-to
summary: "Build a container image with turboquant-vllm baked in, serve a vision-language model with 3.76x KV cache compression, and verify it works — in under five minutes."
tags:
  - ai
  - quantization
  - gpu
  - vision-language-model
  - inference-optimization
  - vllm
---

The [first turboquant-vllm release](/blog/2026-03-27-paper-to-pypi-in-72-hours-building-the-first-turboquant-vllm-plugin) proved the algorithm works — `pip install`, one flag, 3.76x KV cache compression. But if you've ever set up a GPU inference environment from scratch, you know the real friction isn't the model or the framework. It's the CUDA toolkit version, the driver compatibility matrix, the pip packages that refuse to coexist.

v1.1.0 ships a `Containerfile` that eliminates that entire setup. Build the image once, and every run starts from a known-good state — vLLM, CUDA runtime, and the TQ4 compression plugin verified at build time.

This guide walks through building the container, serving a vision-language model with compressed inference, verifying it works, and optionally running it as a persistent systemd service.

![turboquant-vllm container architecture](/turboquant-container-architecture.svg)

## Prerequisites

- **An NVIDIA GPU** with drivers installed (tested on RTX 4090, 24 GB). AMD ROCm also works — adjust the device flag.
- **Podman or Docker.** Commands below use Podman. For Docker, swap `podman` for `docker`.
- **Enough VRAM.** Molmo2-8B needs ~24 GB at 6K context with `--gpu-memory-utilization 0.90`. Molmo2-4B fits with longer contexts on the same card.

## Build the image

Clone the repo and build:

```bash
git clone https://github.com/Alberto-Codes/turboquant-vllm.git
cd turboquant-vllm
podman build -t vllm-turboquant -f infra/Containerfile.vllm .
```

The `Containerfile` does two things: installs `turboquant-vllm` from PyPI into the official vLLM image, then verifies the plugin entry point registered correctly. If the entry point check fails, the build fails — you won't discover a misconfigured plugin at runtime.

```dockerfile
FROM docker.io/vllm/vllm-openai:v0.18.0
ARG TURBOQUANT_VERSION=1.1.0

RUN pip install --no-cache-dir "turboquant-vllm[vllm]==${TURBOQUANT_VERSION}"

RUN python3 -c "\
import importlib.metadata; \
eps = [e for e in importlib.metadata.entry_points(group='vllm.general_plugins') \
       if e.name == 'tq4_backend']; \
assert len(eps) == 1, 'TQ4 entry point not found'; \
print(f'turboquant-vllm {importlib.metadata.version(\"turboquant-vllm\")} — plugin verified')"
```

The `TURBOQUANT_VERSION` build arg defaults to `1.1.0`. Override it for future versions without touching the file.

## Start the server

```bash
podman run --rm \
  --device nvidia.com/gpu=all \
  --shm-size=8g \
  -v vllm-models:/root/.cache/huggingface \
  -p 8000:8000 \
  vllm-turboquant \
  --model allenai/Molmo2-8B \
  --attention-backend CUSTOM \
  --dtype auto \
  --max-model-len 6144 \
  --max-num-batched-tokens 6144 \
  --enforce-eager \
  --gpu-memory-utilization 0.90
```

One flag does all the work: `--attention-backend CUSTOM`. This tells vLLM to use the TQ4 backend instead of its default attention implementation. Everything else — model loading, tokenization, the OpenAI-compatible API — stays exactly the same.

The named volume (`vllm-models`) caches model weights between container restarts. Multi-gigabyte checkpoints download once.

## Verify compression is active

Watch the container logs for the backend confirmation:

```
INFO [cuda.py:257] Using AttentionBackendEnum.CUSTOM backend.
```

If you see `FLASH_ATTN` or `XFORMERS` instead, the plugin didn't register. Rebuild the image and check the entry point verification passed.

You can also confirm from inside a running container:

```bash
podman exec <container-id> python3 -c "
from turboquant_vllm.vllm import TQ4AttentionBackend
import importlib.metadata
v = importlib.metadata.version('turboquant-vllm')
print(f'turboquant-vllm {v} — plugin loaded')
"
```

## Query the API

The container exposes the standard vLLM OpenAI-compatible API. Nothing changes on the client side:

```bash
curl -s http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "allenai/Molmo2-8B",
    "messages": [{"role": "user", "content": "Describe this scene"}],
    "max_tokens": 256
  }' | python3 -m json.tool
```

Clients don't know — and don't need to know — that the KV cache is 3.76x compressed behind the API.

## Persistent deployment with Quadlet

For production, Quadlet manages the container as a systemd service. Create `~/.config/containers/systemd/vllm-turboquant.container`:

```ini
[Container]
Image=localhost/vllm-turboquant:latest
ContainerName=vllm-tq
SecurityLabelDisable=true
ShmSize=8g
AddDevice=nvidia.com/gpu=all
Exec=allenai/Molmo2-8B \
    --attention-backend CUSTOM \
    --dtype auto \
    --max-model-len 6144 \
    --max-num-batched-tokens 6144 \
    --enforce-eager \
    --gpu-memory-utilization 0.90
Volume=vllm-models.volume:/root/.cache/huggingface
PublishPort=8000:8000
HealthCmd=bash -c 'echo > /dev/tcp/localhost/8000'
HealthInterval=30s
HealthTimeout=10s
HealthRetries=5
HealthStartPeriod=300s

[Service]
Restart=always
TimeoutStartSec=900

[Install]
WantedBy=default.target
```

Reload and start:

```bash
systemctl --user daemon-reload
systemctl --user start vllm-turboquant
```

The health check gives the model up to five minutes to load weights before marking the service unhealthy. `Restart=always` handles crashes and GPU driver hiccups automatically.

## Troubleshooting

**Build fails at entry point verification.** The vLLM base image version may not match turboquant-vllm's requirements. Check [PyPI](https://pypi.org/project/turboquant-vllm/) for supported vLLM versions.

**Container starts but uses FLASH_ATTN instead of CUSTOM.** Confirm `--attention-backend CUSTOM` is in your run command. In Quadlet, it goes in the `Exec=` line after the model name.

**OOM during prefill.** TurboQuant compresses the KV cache, not model weights or activations. Peak memory during prefill is activation-dominated — compression savings appear during generation. Lower `--max-model-len` or use a smaller model variant.

## What you learned

You built a container image with turboquant-vllm baked in, served a vision-language model with 3.76x KV cache compression, verified the plugin was active, and optionally deployed it as a persistent systemd service — all from one `Containerfile` and one CLI flag.

The full API reference and additional usage guides are on the [documentation site](https://alberto-codes.github.io/turboquant-vllm/).
