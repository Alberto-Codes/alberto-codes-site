---
title: My Gemma was 99.96 percent sure the total matched. It had not seen the receipt.
date: 2026-09-29
type: explanation
summary: typevet is a small Python library, public today, that asks an open model typed questions and reads the answer as a probability. I asked Gemma 4 31B, on my own 24 GiB card, whether an expense claim matched a real receipt. Without the photo it said yes to every claim that showed a full number, almost certain every time. With the photo it caught all six wrong totals.
tags:
  - ai
  - python
  - multimodal
  - llm
  - evaluation
  - typevet
  - open source
series: Measuring model confidence
---

The claim said the receipt came to 646,329. The receipt says 664,329. Two
digits swapped, the kind of slip anyone makes typing a number in a hurry.

I asked Gemma 4 31B, running on the graphics card under my desk, whether the
claim matched the receipt. When I sent the claim without the photo, it said
the total matched, 99.96 percent sure. It had never seen the receipt. When I
attached the photo, it said the total did not match, 99.999 percent sure.

![A receipt photo cropped to its total line, which reads 664,329. Beside it, the claim: total 646329. Two answers from the same model below. Claim sent without the photo: matches, 99.96 percent. Claim sent with the photo: does not match, 99.999 percent.](/typevet-receipt-swap.svg)

Both answers came out of typevet, a library I made public today.

In the [Jev calibration post](/blog/2026-09-27-jev-looked-underconfident-two-labels-were-the-reason)
I described a model you do not talk to. You write the test it takes, like a
fill-in-the-bubble sheet, and it tells you how likely each bubble is. Jev is
TypeSafe's hosted model, built for exactly that job. It also reads nothing but
text. TypeSafe's [docs](https://docs.typesafe.ai/concepts/state) say so
plainly: "Jev accepts text only. ... Images, audio, and video are not
supported (yet)."

The questions I wanted to ask were about pictures. So I built typevet to ask
the same kind of question of an open model that can see, running on my own
card. Call it Jev at home. Jev at home can look at a receipt.

## What typevet does

typevet has three question types, the same three shapes Jev answers:

- Yes or no: is this message a scam?
- Pick one label: does the claim match the receipt, not match it, or is
  there not enough to tell?
- Pick one level on a scale: how well does this answer follow the rubric?

typevet does not let the model write an answer and then try to parse it.
Before the model writes anything, typevet reads how likely each allowed answer
is as the very next word. The labels you did not offer get no vote. What
comes back is a label with a probability for every option, or an error. It
is never a paragraph you have to interpret.

Here is the question the receipt test asked, shortened where you see `...`.
It is data, not a prompt I wrote around the model:

```python
Choice(
    instructions=(
        "Look at the claimed amount in the expense claim before you look at "
        "the receipt. ... Compare with the receipt total only when the claim "
        "shows every digit of its amount. Otherwise choose insufficient_evidence."
    ),
    criteria={
        "insufficient_evidence": "The claimed amount is not fully readable ...",
        "mismatch": "The claim shows every digit of its amount and that amount differs from the receipt total.",
        "match": "The claim shows every digit of its amount and that amount equals the receipt total.",
    },
)
```

The photo rides along with the text. The model sees both, and typevet reads
the three probabilities.

## The receipt test

I wanted a test I could check by eye. [CORD](https://huggingface.co/datasets/naver-clova-ix/cord-v2)
is a public set of real shop receipts, photographed and labelled with their
totals. I took six of them and wrote three made-up expense claims for each:

- one that states the receipt's real total,
- one that states a wrong total, with two digits swapped,
- one with digits smudged out, written as `?`, so no total can be read.

That is 18 claims. I sent each one twice: once as text alone, and once with
the receipt photo attached.

| | Claim sent without the photo | Claim sent with the photo |
|---|---|---|
| Right total, said match | 6 of 6 | 6 of 6 |
| **Wrong total, said does not match** | **0 of 6** | **6 of 6** |
| Smudged total, said not enough to tell | 6 of 6 | 6 of 6 |

Without the photo, the model said match to every claim that showed a full
number, twelve of twelve, including all six wrong ones. On the wrong ones it
was at least 99.96 percent sure. With the photo, it caught every swapped total, each
at 99.998 percent or more.

It also refused to guess on the smudged claims in both runs. The question
tells it that a `?` is a lost digit, and it listened.

## Why the photo is the whole point

A probability tells you how sure the model is. It does not tell you what the
model looked at. Without the photo, that 99.96 percent rests on nothing but a
tidy claim. With the photo, the 99.999 percent rests on the total printed on
the receipt. A model that can see is the difference, and a text-only model
cannot give you that.

typevet's tests make sure the photo is really there. In this run, attaching a
receipt added between 228 and 1,108 prompt tokens, and the tests fail if the
count does not grow.

## Why Gemma 4, and why on my own card

[Gemma 4 31B](https://huggingface.co/google/gemma-4-31B-it) reads text and
images. It is released under the Apache 2.0 licence, and it placed third
among open models on [LMArena](https://x.com/arena/status/2039739427715735645)
when it launched. I chose it because it reads pictures, its licence lets me build on it, and it can be
made to fit on one consumer card.

It fits on mine because of the
[24 GiB pack I built for the last vramfit post](/blog/2026-09-02-googles-4-bit-gemma-already-fit-my-card).
The file the receipt test loaded is byte for byte the one published on
[Hugging Face](https://huggingface.co/Alberto-Codes/gemma-4-31B-it-fit24gib-GGUF),
served by llama.cpp on an RTX 4090. Nothing in the test left the machine.

I would rather not send a receipt to somebody else's server to find out
whether two numbers agree.

## The same questions on a rented H100

For hosted work, typevet talks to vLLM. On one rented H100 running the
full-precision Gemma 4 31B, the receipt test got all 18 claims right with the
photo. Reversing the order of the three answer options changed
none of the 18 answers.

For speed, I sent 480 public bank support messages through it, two questions
each. One at a time, a message came back in 0.24 seconds at the median. With
64 in flight, the server answered 39.6 messages a second, with no errors.

## Who else does this

I am not the only person who wanted typed answers about pictures. Jev
launched on 2026-09-15, and open takes on the idea followed fast.

- [TypeLLM](https://github.com/TypeLLM/TypeLLM) is where typevet's text
  side comes from: how a JSON Schema becomes a set of decisions, and how each
  decision is scored from the next-word probabilities. TypeLLM added image
  input on 2026-09-24, on SGLang, tested with Qwen3.8-27B. It returns
  probabilities for yes-or-no and pick-one fields, and its README example
  reads a receipt too. typevet's image path was built separately and shares
  no code with it. I worked it out on llama.cpp's own request format, for
  Gemma 3 first and Gemma 4 the same day.
- [A Jev-like wrapper for LLMs, including vision models](https://allanrbo.blogspot.com/2026/09/a-jev-like-wrapper-for-llms-including.html),
  a blog post from 2026-09-25, rebuilds Jev's three question types over
  webcam images in one script, with Gemma 4 12B on llama.cpp and a 24 GiB
  card.
- [VQAScore](https://linzhiqiu.github.io/papers/vqascore/) has read the
  probability of "Yes" from a vision model since 2024, to score whether an
  image matches a caption.

What typevet brings is a library, not a script. It runs the larger Gemma 4
31B on one 24 GiB card with llama.cpp, and the same code serves a rented H100
through vLLM. And its tests check that each image reached the model before
any answer counts.

## Scope

The receipt test is 18 made-up claims on six real receipts, one run on each
server. It shows the photo reaching the model and deciding the answer. The
probabilities are the model's own confidence, not a calibrated forecast.
Checking calibration, as in the Jev post, takes hundreds of labelled
examples.

## Where it lives

- **The code:** [typevet on GitHub](https://github.com/Alberto-Codes/typevet),
  MIT licence.
- **The docs:** [alberto-codes.github.io/typevet](https://alberto-codes.github.io/typevet/),
  including how the image reaches each server and the public receipt for
  the receipt test's pass.
- **The model:** [gemma-4-31B-it-fit24gib-GGUF](https://huggingface.co/Alberto-Codes/gemma-4-31B-it-fit24gib-GGUF),
  the 24 GiB pack the receipt test ran on.
- **The release:** [typevet v0.1.0](https://github.com/Alberto-Codes/typevet/releases/tag/v0.1.0),
  the first public version: yes-or-no, pick-one-label and scale questions over
  text and images, on llama.cpp and vLLM, plus JSON output checked against a
  schema you supply.

Same model, same claim, the same near-certainty both times. The photo is what
made it right.
