---
title: I added a second copy of the same book. It told me nothing about the book.
date: 2026-09-01
type: explanation
summary: Post three of the saucier series puts a second witness of Escoffier into the corpus — the 1907 first printing, as a scan — and gets back no facts about cookery and four classes of fact about its own instruments. The number of sauces the revision supposedly added went twenty, then eight, then none. Along the way the project discovered it had been citing the wrong edition since its first commit.
tags:
  - ai
  - python
  - architecture
  - ai pipelines
  - saucier
  - open source
---

I put a second copy of Escoffier into the corpus this week. The project had
been reading one text of *A Guide to Modern Cookery* since its first commit,
and there is a second one available — the 1907 first printing, photographed
and machine-read by the Internet Archive. Two witnesses of one book, and a
command that compares them.

Two things came out of it that are worth having. The catalogue now reads its
own edition out of the book's front matter, rather than taking it from the
name of a file on my disk — which is infrastructure the rest of this series
will stand on, and which did not exist a week ago. And the 1907 printing,
which the parser could not read at all when it arrived, now yields 115
sauces.

And then the result, which is the reason for the post: **it told me nothing
about the book.** Not one confirmed editorial difference between the two
printings. Every apparent difference I have found so far has turned out to
be a property of my instruments — a wrapped heading, a broken separator, a
corrupted digit, a gap in my own comparison code. The release produced no
facts about a cookbook and four classes of fact about the tools reading it.

That is a better outcome than it sounds. The failure underneath it has a
shape worth naming before the cookbook details start, because it is not
about cookbooks: **an instrument reported an absence it had no way to
observe, through a blind spot nobody had measured.** It said a book lacked
something the book contains. Then, having been corrected, it did it again,
and the second time the gates were just as green as the first.

If you run anything that compares two versions of a document and reports what
changed, that failure is available to you today, and the question this post is
really asking is whether your pipeline could tell you how much of its input it
could not read.

## First, the label was wrong

Before any of that: this project had been citing an edition it had never
parsed.

The corpus file was called `escoffier-1907`. It is not the 1907 edition. Here
is the printing history, transcribed in the file itself, forty lines above
the first recipe:

```console
$ sed -n '119,126p' corpus/escoffier-1909.txt
        _First Printed, May 1907
     Second Impression, December 1907
  New and Revised Edition, January 1909
 New Impressions, August 1911, May 1913,
        March 1916, January 1920._


_Copyright 1907 by William Heinemann._
```

The book is the New and Revised Edition of January 1909, in its January 1920
impression. The only 1907 on the page is a copyright line and the date of a
first printing this file is not. I named the file after the most
1907-looking thing in view, and thereafter the code read the filename.

The claims survive this. Every entry number, every line number, every
derivation was correct and still reproduces. What was wrong was the label on
the book they cite — which, for a record whose whole pitch is *go and check*,
is not a small field to get wrong. It is also
[ADR-0007](https://github.com/Alberto-Codes/saucier/blob/v0.1.0/docs/adr/0007-the-source-classifies-its-own-contents.md)
broken by the person who wrote it. That rule says the source decides what
counts as a sauce, because deciding for ourselves is what put vanilla ice
cream in the catalogue in post #1. A book states its edition more plainly
than it states anything else. I read the filename anyway, in the same release
that introduced the rule.

So a source now reports the edition it states, and the `source_id` derives
from that reading. Four facts come out of the front matter and are kept
apart, because one string cannot carry four: the edition statement, its year,
the last impression, and the copyright year. With no edition stated, the
copyright year decides — a first printing has no printing history to print. A
source that states neither raises rather than guessing.

```json
{ "source_id": "escoffier-1909", "work": "escoffier",
  "origin": "Project Gutenberg 71395", "fidelity": "transcription",
  "edition": { "statement": "New and Revised Edition, January 1909",
               "stated_year": 1909, "impression": "January 1920",
               "copyright_year": 1907 } }
```

Which frees the name for the real 1907, and both published posts in this
series get a correction: they describe the book as Escoffier's 1907 *Guide to
Modern Cookery*, and it is the 1909 revision. I have corrected the prose in
both, the way [the August 11 post](/blog/2026-08-11-i-couldnt-tell-my-quantized-model-from-the-baseline)
was fixed twice — the canonical post is the one that gets corrected. Each also
carries a dated note beside its console block, because the identifier those
posts printed is genuinely what the code printed, and a reader running their
pinned commands will still see it. The counts, entries and line numbers are
unaffected and reproduce exactly as published.

## Twenty, then eight, then none

Now the second witness, and the arc that is the actual story.

`saucier diff` compares two stored catalogues and puts a cause on every row
where they disagree. The first time it ran, it reported **twenty sauces the
1909 revision had added** — twenty preparations present in the later
catalogue and absent from the earlier one.

All twenty are printed in the 1907 book. I checked every one by hand. They
were invisible to the parser because the entry pattern is
`^(\d{1,4})—(.+)$`, and a photographed page defeats it three ways: the digits
come through as letters, the em dash comes through as something else, or a
space lands in the middle.

Six of them, quoted from `corpus/escoffier-1907.txt` with their line numbers
and arranged into a table:

| line | as the scan has it | line | as the scan has it |
| --- | --- | --- | --- |
| 3003 | `loi— POULETTE  SAUCE` | 2072 | `33- CHASSEUR  SAUCE  (Escoffier's  Method)` |
| 3147 | `Ill— WHITE  WINE  SAUCE` | 3345 | `126-- MAYONNAISE  SAUCE` |
| 2560 | `6s— BERCY  SAUCE` | 3172 | `1 12- APPLE  SAUCE` |

`33- CHASSEUR SAUCE` has perfectly legible digits and an ordinary hyphen. The
parser wanted an em dash, so the sauce did not exist, and the diff reported
that Escoffier had added it in 1909.

Repairing those separators took two rounds and moved the 1907 census from 102
sauces to 113, then to 115. The twenty claimed additions fell to eight — plus
one claimed removal, which had the same cause pointing the other way.

Then the third round, which is the one that matters. Eight was still a claim
of absence, and absence is not a thing this instrument can observe. So the
cause is gone. There is no `added` row against a scanned witness any more:

```console
  9 unmatched, 18 parent-changed, 35 ocr-suspected
  entries read  2679 of escoffier-1907, 2963 of escoffier-1909, a blind spot of 284
  A witness is ocr. An unmatched row says the diff found no
  counterpart, never that the printing lacks one.
  No row is adjudicated. An ocr-suspected row is a suspicion, and
  separating a scan artefact from a revision needs both lines read.
```

Twenty, then eight, then none. Three rounds of being confidently wrong about
the same question, on a project with 223 tests, 100% coverage, and fourteen
decision records — and every one of the three was caught by a person reading
output, never by a test. The gates were green the entire time. They were
green for the twenty, and they are green now.

Two more of the same species turned up alongside, and they are worth a
sentence each because they came from opposite ends of the pipeline. An entry
heading that wrapped onto a second line lost its tail, and since the two
printings are set to different column widths, they wrapped in different
places — so the two witnesses recorded visibly different titles for a heading
Escoffier printed identically, and the diff blamed the scan for a difference
my own regular expression had manufactured. At the other end, the comparison
was intersecting its two indexes, so any preparation whose names had been
matched across the witnesses never had its parent compared at all. Six real
disagreements were invisible. Neither defect failed anything.

## Aurore Sauce, and the failure worth being frightened of

Everything above is an instrument reporting something that is not there. Here
is the other direction, which is worse.

Entry 60 is Aurore Sauce. Here is its opening, as the 1909 transcription
gives it:

> Into one-half pint of boiling velouté put the same quantity of very red
> tomato purée (No. 29), and mix the two.

Two candidates are named there: velouté and tomato. Post #2 built its whole
argument on what the parser does with that situation — two candidates, so the
resolver refuses and records unresolved, because the source named two and
chose neither. In the 1909 transcription that is exactly what happens.

The scan carries the same sentence with two words damaged. `purée` comes
through as `pur^e`, which changes nothing, because `tomato` is the candidate
and it survives intact. And `velouté` comes through as `velout^`.

```console
$ uv run saucier show aurore-sauce --source escoffier-1907
AURORE SAUCE
entry 60, line 2503, ocr of escoffier-1907
  term  AURORE SAUCE  [en]  aurore-sauce
  parent  tomato
```

One candidate becomes unreadable. The other survives. The resolver now sees a
single unambiguous statement and records **tomato** — confidently, and
wrongly.

![Two panels. On the left, escoffier-1909, the transcription, entry 60 line 2095: the sentence reads "boiling velouté ... very red tomato purée", two candidates are stated, velouté and tomato, and the parent is unresolved because the source named two and chose neither. On the right, escoffier-1907, the ocr scan, entry 60 line 2503: the same sentence reads "boiling velout^ ... very red tomato pur^e", only one candidate is stated because velouté is unreadable and tomato survives, and the parent is recorded as tomato — unambiguous, well formed, provenanced, and wrong. Both sides connect to a single note: the scan did not add noise to this record, it removed the ambiguity that was the reason for the honest answer, and nothing downstream can tell.](/saucier-aurore-ambiguity.svg)

The scan did not add noise to that record. **It removed the ambiguity that
was the reason for the honest answer**, and converted a correct refusal into a
confident wrong claim. And nothing downstream can tell: the record is well
formed, it validates, it carries a source id and an entry and a real line
number you can go and read. It is exactly the kind of output post #1 warned
about — plausible, checkable-looking, and false — arriving this time with no
model anywhere near it.

Now notice what I just did to tell you that. I read `velout^` as `velouté`,
and I did it using French orthography and the other witness — evidence from
outside the document being read, which is exactly the evidence this project
forbids its own code to use. I cannot prove from the scan alone that
Escoffier printed `velouté` there in 1907. I am confident he did, and my
confidence is a reader's judgement rather than a record's.

That judgement is the adjudication this post keeps saying the tool cannot
perform. It turns out to exist. It exists in me, it is not written down
anywhere, and nothing in the catalogue is entitled to it.

There is a one-character fix available and the project refuses to make it.
Repairing `velout^` back to `velouté` requires evidence from outside the
document being read: French orthography, or the other witness. The separator
repairs were allowed precisely because their evidence is internal — a line
reading `126-- MAYONNAISE SAUCE` looks exactly like the thousands of
undamaged headings in the same file, and the repair changes no recorded byte, because
the separator never reaches a term. `QRIBICHE SAUCE` is still recorded as
`QRIBICHE SAUCE`. That is
[ADR-0013](https://github.com/Alberto-Codes/saucier/blob/v0.3.0/docs/adr/0013-repair-structure-never-content.md):
**repair the punctuation that delimits a record, never the characters that
constitute one.**

The guard on that rule was measured rather than chosen, which I want to note
because it is the part people skip. Requiring the whole title in capitals was
tried first and held out two real headings, including the Chasseur one above.
Four opening capitals admits 57 lines in the scan, and every one of them is a
heading.

## A second rule, and it is the transferable one

Until this week the series had exactly one epistemic rule: **stated, never
inferred**. The catalogue records what the source says, an unresolved parent
stays unresolved rather than being guessed, and everything in the first two
posts descends from that.

It now has a second one, and it is independent rather than a refinement:
**observed, never assumed.**
[ADR-0014](https://github.com/Alberto-Codes/saucier/blob/v0.3.0/docs/adr/0014-a-damaged-witness-cannot-establish-absence.md)
puts it plainly — absence is only observable through an instrument that can
see everything present, and where the instrument has a measured blind spot,
absence is unobservable and is not reported as observed.

The two rules govern different questions. The first is about what you may
read from a source. The second is about what you may conclude from what you
read. A comparison involving a scanned witness now reports `unmatched`, which
says the diff found no counterpart and says nothing about what either book
contains. Between two proofread texts, `added` and `removed` survive — the
rule is about damage, not about comparison.

And the blind spot is printed beside the counts rather than in a footnote,
so no reader sees how many rows the diff found without also seeing how much
of the source it could not read. Today that is **284 entries** of the 1907
scan that the parser still cannot see, against 2,679 it can.

That number is the honest reason the next release exists, and it is the thing
that has to shrink before an absence claim comes back. Restoring `added` for
a scanned witness is not a matter of a better comparison or a kinder
threshold. It requires reading the entries the parser currently cannot read,
and then measuring what is left.

## What I am not claiming

Eighteen rows report a parent disagreement between the two witnesses. None of
them is a finding. Every one carries `ocr-suspected`, which says a lost
candidate explains it as well as a revision does, and the diff adjudicates
none of them. Adjudicating one means putting a human eye on both lines — and
for the disputed spans, on the photographed page itself, because the question
is what the ink says rather than what the text file says. That capability
does not exist here yet.

So there is no claim in this post about what Escoffier changed between 1907
and 1909. There is a catalogue of two witnesses, a diff that names what it
cannot distinguish, and a measured statement of how much of one witness
remains unread.

## What breaks next

Post #2 promised the storage layer failing, and this is not that post either.
The reason is the same as the reason for everything above: a record that
named the wrong book had to stop naming the wrong book before anything got
built on top of it.

The bill keeps growing while I do not pay it. There are two catalogues now,
`saucier diff` loads both of them in full to compare them, and closing that
284-entry blind spot means reading a witness against its own page images —
which is a third artefact per entry, and the JSON file is still the entire
storage layer.

Everything here reproduces from the tag:

```console
$ git clone https://github.com/Alberto-Codes/saucier
$ cd saucier && git checkout v0.3.0
$ uv sync && uv run saucier parse
$ uv run saucier diff escoffier-1907 escoffier-1909
```

That prints two witnesses of one book — 124 sauces and 115 — twenty-seven
rows where the catalogues disagree, a blind spot of 284 entries, and not one
adjudicated difference between two printings of *A Guide to Modern Cookery*.
If you can read both lines of a disputed row and tell me which is the scanner
and which is Escoffier changing his mind,
[the issue template](https://github.com/Alberto-Codes/saucier/issues/new?template=extraction.yml)
asks for the entry number and the source lines. It is the same thing I would
have needed to catch the twenty, and the eight.
