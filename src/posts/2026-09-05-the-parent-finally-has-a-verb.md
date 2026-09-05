---
title: The parent finally has a verb. The book still will not say how many minutes.
date: 2026-09-05
type: explanation
summary: At v0.5.0 the saucier record for Mornay said it derives from Béchamel and stopped there, two lines above the sentence that says how. v0.6.0 records that sentence for one preparation, by hand, as six operations in the book's own words, with every number the text gives and every one it withholds left empty. The check that refuses a misquote also turned up the first confirmed difference between the 1907 and 1909 printings.
tags:
  - ai
  - python
  - architecture
  - ai pipelines
  - saucier
  - open source
---

Here is what `saucier show mornay` printed at `v0.5.0`, cut to the two lines
that matter:

```console
  parent  bechamel

Boil one pint of Béchamel Sauce with one-quarter pint of the _fumet_
```

The record says Mornay derives from Béchamel. The sentence underneath, at
line 2439 of the 1909 text, two lines below the heading of entry 91, says
what is done with the Béchamel, and the record does not read it. [The Marrow Sauce post](/blog/2026-08-21-marrow-sauce-finally-has-a-parent)
spent two and a half thousand words getting the parent edge right, and the edge it got
right is an input with the operation stripped off. A parent says what a sauce
is built from. It does not say boil, reduce, or finish, and it does not say
how much or how far.

`v0.6.0` reads that sentence, for one preparation, by hand. The census does
not move: 151 sauces, 57 derived, 94 unresolved in the 1909 text, and 140,
50, 90 in the 1907 scan, the same census as
[the stream post](/blog/2026-09-04-i-cut-the-last-sauce-off-the-file), whose
151 and 140 these split. What moves is the record underneath one of them.

## Six operations, in the book's order

```console
$ uv run saucier show mornay
MORNAY SAUCE
entry 91, line 2437, transcription of escoffier-1909
  term  MORNAY SAUCE  [en]  mornay-sauce
  parent  bechamel
  procedure  6 operations, recorded by hand
    Boil      Béchamel Sauce [fr] 1 pint, fumet [fr] 1/4 pint
    Reduce    criterion: by a good quarter (unresolved)
    add       Gruyère [fr] 2 oz., Parmesan [en] 2 oz.
    Put       duration: a few minutes (unresolved), on the fire again
    stirring  instrument: small whisk, criterion: the melting of the cheese (unresolved)
    Finish    butter [en] 2 oz., away from the fire, added by degrees
```

And the eight lines it was read from, lines 2439 to 2446 of the committed
corpus, exactly as Project Gutenberg transcribed them:

> Boil one pint of Béchamel Sauce with one-quarter pint of the _fumet_
> of the fish, poultry, or vegetable, which is to constitute the dish.
> Reduce by a good quarter, and add two oz. of Gruyère and two oz. of
> grated Parmesan.
>
> Put the sauce on the fire again for a few minutes, and ensure the
> melting of the cheese by stirring with a small whisk. Finish the sauce
> away from the fire with two oz. of butter added by degrees.

![The Mornay entry and its procedure side by side. Left, lines 2439 to 2446 of escoffier-1909, the eight lines of the body, with six clauses highlighted in reading order: Boil one pint of Béchamel Sauce with one-quarter pint of the fumet, Reduce by a good quarter, add two oz. of Gruyère and two oz. of grated Parmesan, Put the sauce on the fire again for a few minutes, ensure the melting of the cheese by stirring with a small whisk, and Finish the sauce away from the fire with two oz. of butter added by degrees. Right, the six operations as saucier show prints them, one per row, each joined to its clause by an arrow. Slots that hold a number are drawn solid green: 1 pint, 1/4 pint, 2 oz. three times. Slots the text leaves without a number are drawn in dashed orange and labelled unresolved: by a good quarter, a few minutes, the melting of the cheese. Caption: every word on the right is a run of words on the left, and the command checks that before it prints.](/saucier-mornay-procedure.svg)

Every line on the right is a run of words on the left. `Boil` takes two
inputs, each with the quantity the text gives: one pint, one-quarter pint.
`Reduce` takes nothing and carries a criterion, the words the reduction is
carried to. `add` takes two cheeses at two ounces each. `Put` carries a
duration and a constraint, `on the fire again`. `stirring` carries an
instrument and a criterion. `Finish` takes the butter and two constraints,
`away from the fire` and `added by degrees`. That is the whole entry, and
nothing in it is inferred.
[ADR-0017](https://github.com/Alberto-Codes/saucier/blob/v0.6.0/docs/adr/0017-a-procedure-quotes-its-witness.md)
is the record of the shape, and the glossary gains ten terms for it,
because this project uses one word per thing and this release needed ten
new things: procedure, operation, wording, input, parameter, criterion,
constraint, instrument, recorder, unrecorded.

## Three slots the text left empty

Look at the three `(unresolved)` marks. Béchamel gets `1 pint`. Gruyère
gets `2 oz.`. The reduction gets `by a good quarter`, and no number. The
return to the fire gets `a few minutes`, and no number. The stirring gets
`the melting of the cheese`, which is a criterion with no number in it at
all.

That is deliberate, and it is the same rule this series has applied to
parents since [the first post](/blog/2026-08-19-there-is-no-model-in-this-parser).
A parameter holds the words, the number the words give, and the unit they
name. `one-quarter pint` records the fraction one over four and the unit
pint. `a few minutes` records the unit minutes and no number, because the
text gives none. `by a good quarter` names a degree and not a quantity, so
it records no number either. No code fills the slot. Anyone who has cooked a
Mornay knows roughly how many minutes "a few" is, and a model would happily
write 3. The parser writes nothing, because Escoffier wrote nothing, and
the moment this record holds a number the book does not the record stops
being the baseline a model has to beat.

The stream post argued that `null` in a `parent` field means the source
declined to state one, never that the sauce has none. This is the first
time the same absence is recorded against something other than a parent. A
duration with no number is a fact about the text.

## The record cannot say what the entry does not

The six operations are Python literals in an adapter, written by hand
against lines 2439 to 2446. A hand can misquote. So the command never
prints a procedure it has not first found in the body.

Each operation carries its `wording`, the whole clause it was read from.
Each input, criterion, duration, and constraint carries its own wording, and
the entity refuses an element whose words do not lie inside its operation's
wording.
Then, before `show` prints anything, it collapses whitespace on both sides
and looks for each operation's wording in the body, in order, each one
after the last. An operation the body does not carry, or carries out of
order, is reported, and the command exits 2 with nothing on standard
output:

```console
$ uv run saucier show mornay   # with a hand record that says "by a good half"
saucier: MORNAY SAUCE at line 2437 of escoffier-1909 does not state 'Reduce by a good half'
[exit 2]
```

The first version of this printed the title, the reference, the terms, and
the parent before it ran the check, so a piped reader got half a record and
then a non-zero exit. Review caught it, and the check now runs before the
first byte. The stream post's first reader accepted a file missing its last
line. This release's first `show` printed half a preparation beside a
refusal. Same lesson, one layer up: a check that runs after the output has
started is a comment.

What the check proves is narrow, and the ADR says so. It proves the words
are there and in that order. It does not prove the reader parsed the clause
correctly. Three choices in the Mornay record are the reader's, and they
are written down so a disagreement has something to point at. `ensure the
melting of the cheese by stirring with a small whisk` records the verb as
`stirring`, with the melting as the criterion and the whisk as the
instrument. `the sauce` and `the cheese` name the preparation in progress
and are not inputs. `Put the sauce on the fire again` names no heat, so no
heat is recorded.

## The scan keeps its verb and loses its parent

The 1907 witness carries the same entry at line 2864, and the release
records a second procedure for it, in the scan's words, because a procedure
quotes its witness and the two witnesses do not read alike:

```console
$ uv run saucier show morn-ay-sauce --source escoffier-1907
MORN AY SAUCE
entry 91, line 2864, ocr of escoffier-1907
  term  MORN AY SAUCE  [en]  morn-ay-sauce
  parent  (unresolved)
  stated  no candidate
  procedure  6 operations, recorded by hand
    Boil      Bdchamel Sauce [fr] 1 pint, fumet [fr] 1/4 pint
    Reduce    criterion: by a good quarter (unresolved)
    add       Gruy^re [fr] 2 oz., Parmesan [en] 2 oz.
    Put       duration: a few minutes (unresolved), on the fire again
    stirring  instrument: small whisk, criterion: the melting of the cheese (unresolved)
    Finish    butter [en] 2 oz., away from the fire, added by degrees
```

The heading reads `MORN AY SAUCE`, so `show mornay` finds nothing in the
scan. The first input reads `Bdchamel Sauce`, whose folded form reaches no
catalogued name, so the scan's Mornay has no parent and no candidate. The
text resolves it. The verb is on the record in both. `Gruy^re` stays
`Gruy^re`, and the `Reduce` clause carries the running page header `40 GUIDE
TO MODERN COOKERY` inside its wording, because the scan carries it there
and [ADR-0013](https://github.com/Alberto-Codes/saucier/blob/v0.3.0/docs/adr/0013-repair-structure-never-content.md)
repairs the punctuation that delimits a record, never the characters inside
one. The Périgueux page break from the stream post is the same running header,
ten pages earlier, doing the same damage.

## The one difference that is not the scanner

[The second-copy post](/blog/2026-09-01-i-added-a-second-copy-of-the-same-book)
ended on a sentence I have repeated in every post since: not one confirmed
editorial difference between the 1907 and 1909 printings. Every candidate
was the scanner or the reader. The README said so at `v0.5.0`.

Writing the 1907 procedure by hand meant reading line 2867 of the scan
against line 2440 of the text, word by word, because the check would refuse
anything else. The fumet is `of that fish which is to constitute the dish`
in 1907. It is `of the fish, poultry, or vegetable, which is to constitute
the dish` in 1909. No scanner adds two nouns and three commas. Between the first
printing and the revised edition the sentence widened, from fish to fish,
poultry, or vegetable. Whose hand widened it, the two texts do not say.

That is one difference, confirmed by hand, on two lines anyone can open.
The diff command has still confirmed none, and the README now says exactly
that: the diff has confirmed nothing, and one difference has been confirmed
by a reader with both texts in front of them. It took recording a
procedure to find it, because a procedure quotes the witness and a parent
only names it. `bechamel` is the same concept in both books. `of that
fish` and `of the fish, poultry, or vegetable` are not the same words.

## What I am not claiming

One preparation is recorded, once per witness, and a test pins the count
at one. Two procedures written by hand is not extraction. The rule that
would read a second one out of an entry does not exist yet, and until it
does the count stays where it is. What does exist is the port the hand
record enters through, and the line `recorded by hand` in the output is
the recorder naming itself. A rule reader, or a model, is another
implementation behind the same port, and whatever it records will say who
read it. Cardinal Sauce, entry 69, still boils
Béchamel and finishes with lobster butter and still records no parent,
because two catalogued names sit in its opening paragraph and
[a resolver may refuse, never rank](https://github.com/Alberto-Codes/saucier/blob/v0.3.0/docs/adr/0012-a-resolver-may-refuse-never-rank.md).
The verb that would tell those two names apart, one boiled and one added at
the finish, is exactly what a procedure carries. Reading it by rule is the
record after this one, and the ten sauces
[the line-1437 post](/blog/2026-09-03-the-book-spells-it-out-at-line-1437)
lost to a butter are waiting on it.

The procedure is not stored and the interchange does not carry it. `show`
fetches it beside the preparation, checks it, and prints it. The JSON files
under `data/` did not change, `saucier/1` did not change, and a consumer of
the stream sees no operation.
[ADR-0016](https://github.com/Alberto-Codes/saucier/blob/v0.5.0/docs/adr/0016-jsonl-is-the-interchange-not-a-store.md)
says a new field earns a new schema version, and one preparation does not
earn one.

And the `parent` field is untouched. The procedure sits beside it and never
writes it. Mornay's first operation boils Béchamel, which is its parent, and
that agreement is a check on the resolver, not a replacement for it.

Everything here reproduces from the tag:

```console
$ git clone https://github.com/Alberto-Codes/saucier
$ cd saucier && git checkout v0.6.0
$ uv sync && uv run saucier parse
$ uv run saucier show mornay
$ uv run saucier show morn-ay-sauce --source escoffier-1907
$ sed -n 2437,2446p corpus/escoffier-1909.txt
$ sed -n 2864,2878p corpus/escoffier-1907.txt
```

Six operations, five quantities the book gives, three it withholds, and one
sentence Escoffier changed between two printings. If the record says
something lines 2439 to 2446 do not, or reads one of the three choices
above differently than you would,
[the issue template](https://github.com/Alberto-Codes/saucier/issues/new?template=extraction.yml)
asks for the entry number and the source lines. Line 2440 is where I would
start.
