---
title: Gemma 4 read a love note as a scam. A rewritten question brought it within two messages of Jev.
date: 2026-10-01
type: explanation
summary: I asked Jev and Gemma 4 31B the same scam question about 158 public text messages. Jev got 151 right. Gemma, on my own card, got 131, because it flagged love notes and everyday chat as fraud. Then I let an optimizer rewrite the question once for each model. Gemma climbed to 153, and on calibration its percentages ended closer to reality than Jev's.
tags:
  - ai
  - python
  - calibration
  - evaluation
  - typevet
  - gepa
  - open source
---

"I want to show you the world, princess :) how about europe?"

That is a text message from a public scam dataset, and it is not a scam. I
asked Gemma 4 31B, running on the graphics card under my desk, whether it was
a scam, phishing or social-engineering attempt. It said yes, 99.98 percent
sure.

Then I let an optimizer rewrite that one question. Asked the new way, Gemma
put the same message under 0.001 percent. Across 158 messages it had never
seen, it went from 131 right to 153, two short of Jev's 155.

## The test

In the [Jev calibration post](/blog/2026-09-27-jev-looked-underconfident-two-labels-were-the-reason)
I asked TypeSafe's Jev one yes-or-no question about text messages from
[DIFrauD](https://huggingface.co/datasets/difraud/difraud), a public set
labelled scam or not. In the [last post](/blog/2026-09-29-gemma-was-sure-the-total-matched-it-had-not-seen-the-receipt)
I built typevet, which asks the same kind of question of Gemma 4 on my own
card.

So I put Jev and the Jev at home side by side. Same question, same 158 messages, 36 of them
scams:

> Is this message a scam, phishing or social-engineering attempt?

Jev got 151 right. Gemma got 131. It missed no scams at all, but it flagged
27 ordinary messages as scams. Love notes. "Got meh... When?" "I fetch yun
or u fetch?" Gemma read anything personal and a little cryptic as somebody
working an angle.

## Letting each model rewrite its question

The question is one sentence. Small wording changes move these models a lot,
so I let an optimizer search for a better sentence, once for each model.

The optimizer is [GEPA](https://arxiv.org/abs/2507.19457), run through
[gepa-adk](https://github.com/Alberto-Codes/gepa-adk), my package for it. It
works like an editor with a red pen. The model answers a few practice
messages. A second model, Qwen3.8-27B on the same desk, reads how those
answers scored and proposes a rewrite. The winning rewrite is the one that
scores best on 200 separate messages. Every rewrite had to fit in 94
characters, so it could not grow into an essay.

Each model got its own run with the same settings and data. Gemma's took 34 minutes
on my card. Jev's took 27 minutes. Each run made 2,280 calls. The 158 messages in the
test were never shown to either run.

## The two rewrites went opposite ways

![Two cards. Left, Gemma 4's rewrite: Label 1 only for obvious deceptive scam/phishing/social engineering; ignore personal text. Its example, the message I want to show you the world, princess, how about europe?, labelled not a scam, went from 99.98 percent scam to under 0.001 percent. Right, Jev's rewrite: Predict probability (0-1) that message is scam/phishing/unsolicited promo, offer, call, alert. Its example, a real-estate promotion ending For Best Deal Call, labelled a scam, went from 32 percent to 89 percent.](/typevet-gepa-rewrites.svg)

Gemma's rewrite narrowed the word "scam". Obvious deception only, and ignore
personal text. With that wording, every love note in the test came back as
not a scam.

Jev's rewrite widened it. It added unsolicited promotions, offers, calls and
alerts. DIFrauD counts a lot of spam as scam, and Jev's rewrite suggests its
optimizer picked that up. A real-estate promotion that ends "For Best Deal Call" is labelled a
scam in the dataset. Jev moved it from 32 percent to 89.

## The result

![Two charts, one row per judge, each showing the seed question as a hollow gray dot and the model's own rewrite as a filled green dot. Left, messages right out of 158: Jev 151 to 155, Gemma 4 on my RTX 4090 131 to 153, Gemma 4 on a rented H100 128 to 153. Right, average gap between the stated percentage and what happened, in points, lower is better: Jev 8.9 to 7.1, Gemma 4 on the 4090 17.0 to 3.4, Gemma 4 on the H100 18.5 to 3.4.](/typevet-gepa-results.svg)

| Judge | Right, same question | Right, own rewrite | Average gap, same question | Average gap, own rewrite |
|---|---|---|---|---|
| Jev | 151 of 158 | **155** of 158 | 8.9 points | 7.1 points |
| Gemma 4 31B on my RTX 4090 | 131 of 158 | **153** of 158 | 17.0 points | **3.4** points |
| Gemma 4 31B on a rented H100 | 128 of 158 | **153** of 158 | 18.5 points | **3.4** points |

The average gap is the calibration measure from the Jev post: how far a
model's percentages sit from what actually happened. Zero is perfect.

Jev still gets the most messages right. Gemma's percentages now mean more:
on that measure they sit closer to what actually happened than Jev's do,
an average gap of 3.4 points against 7.1. Jev keeps a small edge on the
other scores in the study, and every gap here is small at this size.

## Learned on my card, worked on the big one

The rewrite was learned on the [24 GiB pack](/blog/2026-09-02-googles-4-bit-gemma-already-fit-my-card)
on my RTX 4090, which stores most weights at 4 bits and some at 2 or 3. I
then ran it on Google's full-precision Gemma 4 31B on a rented H100.

Same answer, scam or not, on all 158 messages. The same 153 right, the same
3.4-point gap. A wording found on a compressed model at home carried over to
the full model on a datacenter card without losing a single message.

The H100 was also the fast one. A message came back in 0.17 seconds at the
median there, 1.1 seconds on my desk, and 0.1 seconds from Jev's hosted
service.

## The five that are left

Two are promotions that DIFrauD calls scams and Gemma's narrower question now
lets through, like the real-estate one above. The other three are these,
labelled *not* a scam in the dataset:

- "Send me your id and password"
- "What's ur pin?"
- "Perhaps * is much easy give your account identification, so i will tomorrow at UNI"

Gemma says scam to all three, and so would I. So did Jev with the original
question.

## Scope

158 messages with 36 scams, one run for each judge. At this size one message
moves accuracy by more than half a point. Each rewrite is tuned to DIFrauD's
idea of a scam, so it describes this dataset, not scams in general.

## Where it lives

- **The study:** [Gemma 4 and Jev on DIFrauD](https://alberto-codes.github.io/typevet/explanation/gemma-and-jev-difraud/),
  with the settings, every number above and the per-message receipts.
- **The optimizer:** [gepa-adk](https://github.com/Alberto-Codes/gepa-adk),
  Apache-2.0 licence.
- **The model:** [gemma-4-31B-it-fit24gib-GGUF](https://huggingface.co/Alberto-Codes/gemma-4-31B-it-fit24gib-GGUF),
  the 24 GiB pack the rewrite was learned on.
- **The release:** [typevet v0.5.0](https://github.com/Alberto-Codes/typevet/releases/tag/v0.5.0),
  the version that shipped this study: the Jev judge option for wording
  evolution, the held-out comparison harness, and native Gemma 4 framing for
  text runs.

One sentence, rewritten once on my own card, took Gemma from 131 to 153. The
princess can go to Europe.
