---
title: The book spells it out at line 1437. Two of my posts said it never did.
date: 2026-09-03
type: explanation
summary: Two earlier posts said Escoffier never spells out that half glaze is a reduction of Espagnole. Entry 23 does, in its first sentence. This is the clause of my own that hid it, the 27 entries that enter when it goes, and the ten derivations the release gives back on purpose.
tags:
  - ai
  - python
  - architecture
  - ai pipelines
  - saucier
  - open source
---

Two earlier posts in this series carry a figure of the same four sauces:
[the one where ice cream got into the catalogue](/blog/2026-08-19-there-is-no-model-in-this-parser),
and [the one where Marrow Sauce finally got a parent](/blog/2026-08-21-marrow-sauce-finally-has-a-parent).
At the top of that figure is Espagnole. A dashed arrow runs from it down to
half glaze, and the arrow is labelled *assumed, not stated* — half glaze, the
caption says, is "a reduction of Espagnole the book never spells out." The
Marrow Sauce post goes further in prose: a *demi-glace* is an Espagnole
reduction, "which every reader of Escoffier knew and the book therefore never
says."

saucier is a parser that reads Escoffier's 1909 *Guide to Modern Cookery*
and records only what the book states. Here is entry 23 of that text, at
line 1437, in the chapter Escoffier titles *The Leading Warm Sauces*:

> **HALF GLAZE.** This is the Espagnole sauce, having reached the limit of
> perfection by final despumation. It is obtained by reducing one quart of
> Espagnole and one quart of first-class brown stock until its volume is
> reduced to nine-tenths of a quart.

The book says it. It says it in the first sentence of a numbered entry, in the
sauce chapter, nine entries before Bordelaise. I published two posts and two
figures asserting the book never says it, because my parser could not see
entry 23, and I believed my parser over the book.

![The chain from brown roux to Marrow Sauce, five sauces, every arrow solid and labelled stated. Brown roux, entry 19 line 1317, states no parent. Espagnole, entry 22 line 1392, opens with "one lb. of brown roux" and records brown-roux. Half glaze, entry 23 line 1437, opens with "This is the Espagnole sauce" and records espagnole. Sauce Bordelaise, entry 32 line 1680, opens with "one-half pint of half-glaze" and records half-glaze. Marrow Sauce, entry 45 line 1895, "only a variety of the Bordelaise", records sauce-bordelaise. A side note says the two earlier figures drew the top two arrows dashed and labelled them assumed, not stated; the book states both, and the parser could not see entries 19 to 23 because a rule of mine required their headings to name a mother.](/saucier-stated-chain-line-1437.svg)

The parser could not see it because the rule that decides what counts as a
sauce had two tests, and the second could overrule the first. This release
deletes the second test. Here is what that does to the census at `v0.4.0`:

```console
$ uv run saucier parse
escoffier-1909  New and Revised Edition, January 1909 (impression: January 1920)
                transcription of Project Gutenberg 71395
                mothers: bechamel, espagnole, hollandaise, tomato, veloute
                151 sauces, 57 derived, 94 unresolved
escoffier-1907  no edition stated, copyright 1907
                ocr of Internet Archive cu31924000610117
                mothers: bechamel, espagnole, hollandaise, tomato, veloute
                140 sauces, 50 derived, 90 unresolved
```

At `v0.3.0` the 1909 line read 124, 50, 74. Twenty-seven sauces entered.
Unresolved rose by twenty, and every one of the twenty is something the
parser could not see before: an entry my rule hid, or an ambiguity that was
invisible while the entry was hidden. The honest number got worse because the
instrument got better. And derived rose by seven, which is the misleading
number, for the best reason in the release.

## The clause that vetoed Escoffier

Escoffier opens the chapter at line 1246 by saying what his sauces are:

> Warm sauces are of two kinds: the leading sauces, also called "mother
> sauces," and the small sauces, which are usually derived from the
> first-named, and are generally only modified forms thereof.

The ice cream post introduced
[ADR-0007](https://github.com/Alberto-Codes/saucier/blob/v0.1.0/docs/adr/0007-the-source-classifies-its-own-contents.md):
the source decides what counts as a sauce, because deciding for ourselves is
what put vanilla ice cream in the catalogue. Under that record an entry
enters on two kinds of evidence. Its heading says "sauce". Or the source
filed it in a chapter Escoffier titles as sauces — *and its heading also
names one of the five mothers.*

That second test has two clauses. The chapter clause reads the source's own
classification. The mother clause adds a test of mine on top of the reading,
and when the two disagree, mine wins. **A second test on a classification the
source has already made is a veto, not a check.**

![Two rows of a decision flow. At v0.3.0: a numbered entry; does the heading say sauce, yes goes into the catalogue; no, is it in a chapter titled as sauces; no goes out; yes reaches a third test drawn in dashed orange, does the heading name a mother; no sends 27 entries out, yes goes in, and the catalogue holds 124. At v0.4.0 the third test is gone: an entry in a chapter titled as sauces goes straight in, and the catalogue holds 151.](/saucier-veto-gate.svg)

I wrote the mother clause to keep `LENTEN ESPAGNOLE` and `VELOUTÉ DE
VOLAILLE`, two derivatives in the sauce chapters whose headings never use the
word. It kept them.
[ADR-0015](https://github.com/Alberto-Codes/saucier/blob/v0.4.0/docs/adr/0015-the-chapter-decides.md)
counts what it cost, in the three sauce chapters of the 1909 text:

| | entries |
| --- | ---: |
| numbered entries in the three sauce chapters | 139 |
| heading lacks the word "sauce" | 29 |
| admitted on the mother clause | 2 |
| vetoed | 27 |

The 27 are the three roux, half glaze, two gravies, a lobster method that
Escoffier numbered as its own entry, whisked mayonnaise, various cullises, and
18 compound butters from the chapter titled *Cold Sauces and Compound
Butters*. Every one of them is an entry the source classified. My rule
classified them again and lost.

Here is what that looked like on screen, at `v0.3.0`:

```console
$ uv run saucier show robert-sauce --chars 260
ROBERT SAUCE
entry 52, line 1994, transcription of escoffier-1909
  term  ROBERT SAUCE  [en]  robert-sauce
  parent  (unresolved)

Finely mince a large onion and put it into a stewpan with butter. Fry
the onion gently and without letting it acquire any colour. Dilute
with one-third pint of white wine, reduce the latter by one-third,
add one pint of half-glaze, and leave to simmer for twen...
[378 more characters, raise --chars to read them]
```

The record and the sentence that contradicts it, four lines apart, for three
releases. Eleven sauces name half glaze in their opening paragraph. Five name
a roux. The book writes the chain in full — brown roux, Espagnole, half
glaze, Robert — and the catalogue had dropped the middle link.

The new rule is one sentence: **an entry inside a sauce chapter qualifies on
the chapter, and an entry outside one qualifies on its heading alone.** The
function that decides admission went from five lines to one:

```python
return names_a_sauce(title) or in_sauce_chapter
```

The mothers are still read, for the catalogue and for resolution, and they
take no part in admission. Nothing is hand-excluded to make the result tidy:
`VARIOUS CULLISES` is entry 144, numbered inside a sauce chapter, and it is in
the catalogue now. An admitted entry that reads oddly as a preparation is a
finding, not a special case in the parser.

## Twelve gained, and one of them was the bar

With half glaze and the roux in the catalogue, the chain resolver from the
Marrow Sauce post has something to resolve against. Twelve sauces now record
the parent Escoffier wrote, and none of them needed a new rule to do it:

| resolves to | sauces |
| --- | --- |
| half glaze | Bordelaise, Brown Chaud-froid, Devilled, Italian, Lyonnaise, Madeira, Piquante, Robert |
| brown roux | Espagnole |
| pale roux | Velouté |
| white roux | Scotch Egg |
| manied butter | Mousseuse |

Bordelaise is on that list, and the Marrow Sauce post made a point of
Bordelaise. Its opening names half a pint of half glaze and never says
Espagnole, so it stayed unresolved — "not a gap in this release," I wrote,
but "the bar the model post will have to clear." The bar is cleared, and no
model cleared it. A chapter test cleared it, by letting the resolver see an
entry that was in the book the whole time.

```console
$ uv run saucier tree espagnole
BROWN SAUCE OR ESPAGNOLE  [espagnole]  derives from brown-roux
├── HALF GLAZE  (en)
│   ├── SAUCE BORDELAISE  (fr)
│   │   └── MARROW SAUCE  (en)
│   ├── BROWN CHAUD-FROID SAUCE  (en)
│   ├── DEVILLED SAUCE  (en)
│   ├── ITALIAN SAUCE  (en)
│   ├── LYONNAISE SAUCE  (en)
│   ├── MADEIRA SAUCE  (en)
│   ├── PIQUANTE SAUCE  (en)
│   └── ROBERT SAUCE  (en)
├── LENTEN ESPAGNOLE  (fr)
│   └── GENEVOISE SAUCE  (en)
├── ORDINARY POIVRADE SAUCE  (en)
└── POIVRADE SAUCE FOR VENISON  (en)
```

That heading line is new. Escoffier names five mothers, and that does not
change. But Espagnole opens with "one lb. of brown roux dissolved in a tall,
thick saucepan with six quarts of brown stock," and the catalogue can now see
the roux, so a mother may state a parent. It cannot see the stock: brown
stock is entry 7, in *Fonds de Cuisine*, a chapter Escoffier does not title
as sauces. The chapter decides, and Chapter I decided stocks.

## Ten lost, and they are the finding

Derived rose from 50 to 57, and seven is three numbers: twelve sauces gained
a parent, five admitted entries state one of their own, and **ten sauces that
were resolved at `v0.3.0` are unresolved now.** Eighteen of the 27 admissions
are compound butters, and seven of the ten losses are sauces that now see a
compound butter beside their old parent. The butters that came in are the
butters that took Cardinal's parent away.

![A waterfall chart. Derived at v0.3.0 is 50. Twelve sauces gained the parent Escoffier wrote, up to 62. Ten lost one to a butter or to half glaze, down to 52, drawn in dashed orange. Five admitted entries state a parent of their own, up to 57. Derived at v0.4.0 is 57. A note reads: net plus seven, read alone, is a gain that hides a loss.](/saucier-derived-waterfall.svg)

Here is Cardinal, which is the shape of all ten, with a line that did not
exist at `v0.3.0`:

```console
$ uv run saucier show cardinal-sauce
CARDINAL SAUCE
entry 69, line 2192, transcription of escoffier-1909
  term  CARDINAL SAUCE  [en]  cardinal-sauce
  parent  (unresolved)
  stated  bechamel, lobster-butter
```

And the paragraph beneath it, with the two verbs the resolver cannot read:

> **Boil** one pint of Béchamel, to which add one-half pint of fish *fumet*
> and a little truffle essence, and reduce by a quarter. **Finish** the
> sauce, when dishing up, with three tablespoonfuls of cream and three oz.
> of very red lobster butter (No. 149).

At `v0.3.0` Cardinal recorded `bechamel`, and that was correct. Lobster
butter was on the page then too, at entry 149, but the mother clause had kept
it out of the catalogue, so as far as the resolver could see it was an
ingredient with no entry. Now it is catalogued, the opening paragraph states
two catalogued names, and
[ADR-0012](https://github.com/Alberto-Codes/saucier/blob/v0.3.0/docs/adr/0012-a-resolver-may-refuse-never-rank.md)
says what happens then: the resolver refuses. It may not rank. So Cardinal is
unresolved, and so are Nantua, Noisette, Diplomate, Joinville, Herb and
Ravigote, each with at least one butter beside its old parent. Périgueux,
Reform and Chasseur lose theirs the same way to half glaze, which now sits
beside the base each of them names.

The refusal is correct under the rule as written, and the rule as written is
wrong about this sentence. The source stated one *base* and one *finish*.
Any cook reading the paragraph knows which is which. The resolver reads
names. It cannot tell a base from a finish, because it has never been asked
to read the verb a name sits inside — and until it can, the honest answer is
the refusal.

I could recover all ten this afternoon. A rule that prefers a mother when one
is stated would put Cardinal back on Béchamel and the derived count back near
67. I am not doing it, and the reason is
[the second-copy post's](/blog/2026-09-01-i-added-a-second-copy-of-the-same-book)
Aurore sauce. The candidate rule is not tuned to save the number. Every
tuning of it that saves Cardinal is a choice made by me rather than a
statement made by the book, and the whole value of the unresolved count is
that it has never contained one of those.

What the release does instead is make the refusal readable. That `stated`
line names every catalogued candidate the opening paragraph states, in the
order the paragraph states them. The adjudication this tool cannot perform
still exists only in me. But the evidence I would adjudicate from is now on
screen next to the refusal, which is the most the parser is entitled to do.

One of the twelve gains belongs in this section too. `MOUSSEUSE SAUCE`
resolves to manied butter, because its opening calls for "one-half lb. of
stiffly-*manied* butter" and manied butter is now a catalogued entry. The
same paragraph continues: "This preparation, though classified as a sauce,
is really a compound butter." Escoffier classified it as a sauce and said in
the same breath that the classification was a courtesy. The catalogue reads
the chapter and records the sauce. The reader reads the sentence and knows
better. It stays as recorded. I would rather carry a visible oddity than an
invisible rule.

## What it did to the scan

The 1907 witness moves from 115 sauces, 36 derived, 79 unresolved to 140, 50,
90. Twenty-five entries entered, not 27. `MONTPELLIER BUTTER` is on the page
at line 3782 of the scan, and `HAZEL-NUT BUTTER` at 3816:

```console
$ sed -n '3782p;3816p' corpus/escoffier-1907.txt
IS3— MONTPELLIER  BUTTER
15s— HAZEL-NUT  BUTTER
```

`IS3` for 153, `15s` for 155. The entry pattern wants digits and never
matches, so both sit inside the 284-entry blind spot the second-copy post
measured. Repairing them means deciding that `S` is `5` from outside the
document, and
[ADR-0013](https://github.com/Alberto-Codes/saucier/blob/v0.3.0/docs/adr/0013-repair-structure-never-content.md)
makes no such decision.

The scan also reads two entry numbers twice, 138 and 63, and until this
release the catalogue used the number as a preparation's identity, so the
later entry's bookkeeping overwrote the earlier one's. A preparation is now
identified by the line its heading sits on, which is unique in both witnesses
and is the field a reader checks by hand.

The diff moves from 9 unmatched, 18 parent-changed, 35 ocr-suspected to 11,
19, 36. Three of the new rows are the Aurore shape again: `HERB`, `RAVIGOTE`
and `PÉRIGUEUX` state two candidates in the proofread text and refuse, the
scan hides one candidate in each, and the scan answers. A damaged witness
confidently resolving what a clean witness honestly cannot was described once
as a finding. It has now happened four times.

## Worse than the scanner, in one specific way

The second-copy post gave this series its second rule, *observed, never
assumed*, and wrote it down as
[ADR-0014](https://github.com/Alberto-Codes/saucier/blob/v0.3.0/docs/adr/0014-a-damaged-witness-cannot-establish-absence.md):
a damaged witness cannot establish absence.

I wrote that record about a scanner. Ten days later the same failure turned up
on the clean witness, in a proofread transcription with no OCR damage
anywhere in it. The blind spot was a clause I wrote, and the absence it
produced went into two posts, two figures, and the published claim that the
book never spells out what it spells out at line 1437. The project had 243
tests when I found it, and every one of them was green.

The scan's blind spot could be measured, because there was a clean witness to
measure it against. The mother clause's blind spot had no second witness to
reveal it, because both copies of the book went through the same rule.

![Two panels. Left, the scan's blind spot: the 1907 scan and the 1909 text both go into saucier diff, which measures 284 entries the scan cannot read, because a clean witness existed and the blind spot had a size. Right, the mother clause's blind spot: both books go into the same is_sauce rule, does the heading name a mother, and both catalogues come out missing the same 27 entries. Identical absences from two witnesses, and nothing left to compare against. Caption: a second copy of the book cannot catch an error in the reader; only a second reader can.](/saucier-two-books-one-reader.svg)

A second copy of the book cannot catch an error in the reader. Only a second
reader can, and the second reader here was a person following the chain
Robert states, by hand, and asking why the middle of it was not in the
catalogue.

Both earlier posts now carry a dated note beside their figure. The figures
are left as printed, because what they show is genuinely what the parser
recorded at those tags. What they say about the book was wrong.

## What I am not claiming

Not one of the ten lost derivations is a finding about Escoffier. Every one
is a finding about a resolver that reads names and not verbs. And the 27
admitted entries are a claim about where Escoffier put them, not about what a
sauce is — if a lobster method numbered as its own entry in the sauce chapter
is not a sauce, the argument is with the book's table of contents.

Everything here reproduces from the tag:

```console
$ git clone https://github.com/Alberto-Codes/saucier
$ cd saucier && git checkout v0.4.0
$ uv sync && uv run saucier parse
$ uv run saucier show cardinal-sauce
$ uv run saucier tree espagnole
```

That prints 151 sauces and 140, the chain from brown roux to Robert that the
book has always written in full, and a `stated` line under Cardinal naming the
two things it says, in the order it says them. If you can tell me a rule that
reads "finish the sauce with" as a finish and not a base, without reading
anything the sentence does not contain,
[the issue template](https://github.com/Alberto-Codes/saucier/issues/new?template=extraction.yml)
asks for the entry number and the source lines. Entry 69, line 2192 is a
good place to start.

**The release:** [saucier v0.4.0](https://github.com/Alberto-Codes/saucier/releases/tag/v0.4.0)
— the mother clause deleted: the second test is the chapter clause alone and
the heading test still stands beside it, the 27 entries
Escoffier filed among his own sauces come back, ten derivations are given up on
purpose, and a preparation is identified by the line its heading sits on rather
than by an entry number the scan reads twice. MIT.
