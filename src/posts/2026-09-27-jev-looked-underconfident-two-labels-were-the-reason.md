---
title: Jev looked underconfident on Banking77. Two of my labels were the reason.
date: 2026-09-27
type: explanation
summary: I asked TypeSafe's Jev one yes-or-no question about a thousand public messages and checked whether its percentages matched what actually happened. On scam text messages they did. On bank support messages they looked far too cautious, until I read the messages themselves. The problem was two of my labels, not Jev.
tags:
  - ai
  - python
  - calibration
  - judgevet
  - open source
---

When a weather forecast says 30 percent chance of rain, it should rain on
about three of every ten days it says that. If it rains on nine of those ten
days, the forecast is too cautious. If it rains on none, it is too alarmed.
Forecasters call this being *calibrated*: the percentages mean what they say.

![Three rows of ten days, each day forecast at a 30 percent chance of rain. Top row, calibrated: it rained on 3 of the 10 days. Middle row, too cautious: it rained on 9 of the 10. Bottom row, too alarmed: it rained on none.](/jev-forecast.svg)

I wanted to know whether that holds for Jev, a model from TypeSafe that
answers yes-or-no questions with a percentage instead of a yes or a no. So I
asked it one question about a thousand public messages and compared its
percentages with what the messages actually were.

On one set of messages, it looked badly miscalibrated. Where Jev said 20 to
50 percent, the real answer turned out to be yes almost nine times in ten.
That looked like a forecaster saying "probably not" before a week of rain.
Then I read the messages, and the mistake was mine.

## What Jev says it does

Jev does not chat, write or explain itself. You give it some text and a
question, and it returns a number. For a yes-or-no question, TypeSafe's
[docs](https://docs.typesafe.ai/primitives/noul) define that number as the
probability that the answer is yes.

When I explain it to people, I say you don't talk to Jev. You write the test
it takes. Think of the fill-in-the-bubble exams from school, the Iowa tests or
an SAT answer sheet. Your job is to write the question and the answer choices.
Jev fills in the bubbles, except that instead of filling in one, it tells you
how likely each choice is. A yes-or-no question is a test with two bubbles.
With Jev, the work is in writing the question, not in a conversation.

![Two cards. Left, labelled you write: the text, I have multiple charges on the same transaction; the question, Does the customer report a transaction they did not authorize?; and two empty bubbles, Yes and No. An arrow leads to the right card, labelled Jev fills in: the same bubbles shaded by how likely each is, Yes 16 percent and No 84 percent.](/jev-bubble-test.svg)

TypeSafe says its models are
["trained for calibrated decisions"](https://docs.typesafe.ai/concepts/system-one),
and it is careful about what that promises: "Calibration is measured across
groups of predictions; it does not guarantee that an individual answer is
correct." One message scored at 30 percent can be yes or no. But across a
large group of messages scored near 30 percent, about 30 percent should be
yes. A group is something I can check.

## The test

I used two free public datasets where people had already labelled every
message.

- **DIFrauD**: text messages, each labelled scam or not. I asked Jev: "Is this
  message a scam, phishing or social-engineering attempt?"
- **Banking77**: short messages people send to a bank's support desk, sorted
  into 77 topics such as "card arrived" or "exchange rate". There is no scam
  label here, so I made one. I picked six topics that sounded like "someone
  took money I did not agree to" and counted them as yes. I asked Jev: "Does
  the customer report a transaction they did not authorize?"

Then I sorted Jev's answers into ten buckets: 0 to 10 percent, 10 to 20, and
so on. For each bucket I compared the average percentage Jev gave with how
often the answer was really yes. The average gap across all buckets is the
*calibration error*. Zero would be perfect. I also measured something simpler:
whether Jev at least scored the yes messages higher than the no messages. Call
that the *sorting score*. 1.0 means every yes message scored above every no
message.

## The scam texts: close to the forecast

On the 500 text messages, Jev behaved like a good forecaster. The average gap
was 7 percentage points, and the sorting score was 0.995.

The extremes were clean. Jev put 369 messages below 20 percent, and not one
of them was a scam. It put 47 messages at 90 percent or above, and 46 of them
were.

![Three charts side by side. Each plots Jev's average percentage in ten buckets against how often the answer was really yes, with a dashed diagonal line where the two would match. Left: scam text messages, 500 messages, average gap 7 points, dots close to the line. Middle: bank messages with my six topics counted as yes, 480 messages, average gap 17 points; between 20 and 50 percent predicted, 87.5 to 93 percent were labelled yes, far above the line. Right: the same 480 answers with two topics recounted as no, average gap 6 points, dots back on the line.](/jev-reliability.svg)

In the chart, Jev's percentage runs along the bottom and the real share of
yes answers runs up the side. A dot on the dashed line means Jev's percentage matched reality
for that bucket. A dot above the line means more yeses than Jev predicted.
The left panel stays close to the line. The small wobbles in the middle come
from small buckets: a few buckets hold only 7 or 8 messages, so one message
moves the result by more than 10 points.

## The bank messages: a forecaster saying "probably not" before the rain

On the 480 bank messages, the sorting score was still excellent at 0.986. Jev
put the yes messages above the no messages almost every time. But the
percentages themselves were off, with an average gap of 17 points, and always
in the same direction. None of the no messages scored 50 percent or more.
But 93 of the 240 yes messages scored below 50 percent. Jev looked too
cautious, as the middle panel shows.

Splitting the yes messages by topic showed where the gap came from. Four
topics matched what I had asked about. Two did not. Each topic had 40
messages:

![Horizontal bars, one per topic of 40 messages, with a dashed line at 50 percent. A card payment I don't recognise, 83 percent, 36 of 40 at 50 percent or more. A direct debit I don't recognise, 82 percent, 35 of 40. A cash withdrawal I don't recognise, 80 percent, 34 of 40. My card may be compromised, 71 percent, 30 of 40. An extra charge on my statement, 36 percent, 8 of 40. A transaction charged twice, 29 percent, 4 of 40. The first four sit well above 50 percent; the last two sit below it.](/jev-topics.svg)

## Reading the messages

Here are six messages from those two topics. My answer key said yes to every
one. Jev's percentage is beside each:

![Six messages from the two topics I counted as yes, each with Jev's percentage and my answer key, which says yes to all six. Charged twice: I have multiple charges on the same transaction, 16 percent. What are my remedies if I think I was charged twice for the same expense, 16 percent. Extra charge: When will the $1 transaction be credited to me, 7 percent. Why are there so many fees on my statement, 8 percent. There is a fee I don't recognize on my statement, 78 percent. I do not remember purchasing anything for 1 pound, and it is on my statement, 87 percent.](/jev-answer-key.svg)

Someone who was charged twice agreed to the purchase. They are reporting a
billing mistake, not a transaction they never made. Jev said "probably not",
and for the question I asked, that is the right answer. My label said yes.

The "extra charge" topic is more mixed, and Jev kept up with it message by
message. The two about a fee or purchase the customer does not recognise
scored high. The two questions about a refund and about fees scored low. My
label treated all 40 the same because they share a topic name.

In test terms, Jev answered the question printed on the page. The answer key I
graded it with was written for a slightly different question.

## The same answers, counted fairly

I kept every one of Jev's 480 answers and changed only my labels, counting
those two topics as no. The average gap fell from 17 points to 6, which is
better than on the scam texts. That is the right-hand panel of the chart.

I owe you one caveat about that 6. I chose to relabel those two topics after
seeing the results, and I checked the fix on the same answers. It is not a
fair new score for Jev. What it does show is that most of the 17-point gap
came from my labels answering a different question from the one I asked Jev.

A third topic is borderline too. A compromised card does not always mean a
transaction the customer did not make, and Jev put 10 of those 40 messages
below 50 percent. I left that topic as yes. If I kept moving topics until the
number looked good, I would be tuning my labels to flatter the model.

## What the two scores told me

The only thing I changed was two topics' labels. Here is what that did to
each score:

![Two small charts. Left, the sorting score, where higher is better: 0.986 with my first labels and 0.972 after relabelling two topics, nearly the same. Right, the average gap, where lower is better: 17 points with my first labels and 6 points after relabelling, about a third. Changing two topics' labels barely moved the sorting score and cut the average gap by about two thirds.](/jev-two-scores.svg)

So the first result was not a measurement of Jev on its own. It measured
Jev's answers against my idea of what the answers should be. On the scam
texts, the labels came from the dataset's authors, answering nearly the same
question I asked. On the bank messages they came from me, answering a
slightly different question: which topics involve a charge the customer
questions.

## What this does not show

- This is two groups of about 500 messages, one run each. Several buckets
  hold fewer than 20 messages, which is small.
- The bank sample is half yes by design. In the full dataset, those six topics
  are 7.8 percent of messages, 240 of 3,080. A more natural mix would give a
  different number.
- DIFrauD has several kinds of text. I used only the text messages.
- The same messages sent three days apart gave nearly the same results: an
  average gap of 17 points both times on the bank messages, and 7 both times
  on the scam texts. A handful of messages moved between buckets.

## For the curious

| What | Detail |
|---|---|
| Model | TypeSafe `jev-1.13.0`, called on 2026-09-27 |
| Client | [judgevet](https://github.com/Alberto-Codes/judgevet) 0.13.0, my Python client for Jev |
| Calls | 980, all successful |
| Scam texts | [DIFrauD](https://huggingface.co/datasets/difraud/difraud), MIT licence: 500 messages from the SMS test split, 98 of them scams |
| Bank messages | [Banking77](https://huggingface.co/datasets/PolyAI/banking77), CC BY 4.0 licence: all 240 test messages from my six topics, plus 240 others chosen with a fixed seed |
| My six topics | `card_payment_not_recognised`, `direct_debit_payment_not_recognised`, `cash_withdrawal_not_recognised`, `compromised_card`, `extra_charge_on_statement`, `transaction_charged_twice` |
| Average gap | Expected calibration error (ECE), ten equal-width buckets weighted by size: 0.073 scam texts; 0.174 bank messages as first labelled; 0.056 relabelled |
| Sorting score | AUROC: 0.995 scam texts; 0.986 bank messages as first labelled; 0.972 relabelled |

TypeSafe calls a yes-or-no question a Noul, so judgevet does too, and the
answer's `.noul` field is Jev's percentage as a number between 0 and 1. One
question is a few lines:

```python
import os

from judgevet import HTTPSystemOneAdapter, Noul

question = Noul(instructions="Does the customer report a transaction they did not authorize?")

with HTTPSystemOneAdapter(api_key=os.environ["JEV_API__KEY"]) as client:
    response = client.system_one(
        state="I have multiple charges on the same transaction.",
        questions={"unauthorized": question},
    )

print(response.nouls["unauthorized"].noul)
```

The 17-point gap came apart when I stopped looking at the chart and read ten
messages from the buckets where it was widest.
