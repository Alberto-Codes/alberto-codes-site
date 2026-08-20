---
title: There is no model in this parser. It still told me ice cream was a sauce.
date: 2026-08-19
type: explanation
summary: Post one of the saucier series reads a 1907 cookbook with a regular expression — 124 sauces, 29 lineages, 95 that name no base. The first version of that census said 166 and 64, and forty of those were soups, jam, and a vanilla ice cream. Determinism did not catch that. Line numbers did.
tags:
  - ai
  - python
  - architecture
  - ai pipelines
  - saucier
  - open source
---

Here is something I wanted to know. It is 2026, every conversation that starts
with "I have a pile of documents" ends with which model to point at them, and I
had a cookbook from 1907 sitting on my disk. How much of it can a regular
expression read?

Not as a stunt, and not as an argument against models — later posts hand the
same book to one and find out what it does better. Just as a question worth
answering first, because it costs an afternoon.

So: no model, no API key, no GPU, no network. `git clone`, `uv sync`,
`uv run saucier parse`, and you are standing where I am standing. Every post
in this series adds one ingredient and everything runs at every tag — a sauce
should taste like something at every stage of its reduction, and this is the
earliest stage there is.

The useful part of it is not what the parser got right. It is what it got
wrong, how badly, and what caught it — because the thing that caught it is the
one property I would keep if I had to throw away everything else in the repo.

## Reading a book literally

Sauces specifically, rather than the whole book. A sauce is the most
process-dense thing in a kitchen — reductions, emulsions and suspensions, with
temperature and timing and order that genuinely matter — and Escoffier's
mothers-and-derivatives scheme is already a taxonomy of them. The structure is
in the book. The only question is how much of it comes back out.

Quite a lot, because Escoffier structured his own work. Every preparation in
*A Guide to Modern Cookery* is numbered and titled — 2,963 of them — and he
names his five base sauces in a sentence you can point at:

> 7. The basic sauces: Espagnole, Velouté, Béchamel, Tomato, and Hollandaise.

So the five mothers are not in the source code. A regular expression reads them
out of the book:

```python
MOTHERS = re.compile(r"basic sauces?:\s*(.+?)\.", re.IGNORECASE | re.DOTALL)
"""The source names its own base preparations; it is not our place to guess them."""
```

Hardcoding those five strings produces identical output today and a lie the
first time the same code meets Fannie Farmer. Run the whole thing and it
reports:

```console
$ uv run saucier parse
source      escoffier-1907
mothers     bechamel, espagnole, hollandaise, tomato, veloute
sauces      124
derived     29 linked to a mother
unresolved  95 state no base in their prose
```

29 of 124 is a coverage number that would embarrass most extraction demos. Hold
that thought.

## The first census was worse than embarrassing. It was wrong.

Before those numbers, this project published different ones: 166 sauces, 64
derivations. They were in the README, on the landing page, in the CLI output,
and in the argument for why a model comes later. They were also nonsense.

An entry qualified as a sauce if its heading said "sauce", or if the folded
heading contained a mother concept anywhere inside it. That second rule is a
substring test, and two of the five mothers Escoffier names — *tomato*,
*velouté* — are ordinary words in a cookery book. The catalogue filled up
accordingly: 25 velouté **soups** from the soup chapter, eight tomato dishes
and preserves including `TOMATO JAM` and `TOMATO SALAD`, six fish and meat
dishes including `SOLE A LA HOLLANDAISE`, and `BOMBE HOLLANDAISE`, which is
vanilla ice cream in a mould.

Roughly forty of the 166 were not sauces. Thirty of the 64 recorded
derivations belonged to entries that are not sauces. And the record it
produced looked like this:

```json
{ "title": "GRILLED TOMATOES", "parent": "tomato",
  "ref": { "entry": 2263, "line": 36212 } }
```

A grilled tomato, recorded as a derivative of the mother sauce Tomato, because
the word "tomatoes" occurs in its prose. An absence of evidence turned into a
derivation and published with a line number.

There was a second defect underneath it. When an entry's opening paragraph
named two mothers, `resolve_parent` sorted the candidates and took the first
alphabetically. It decided three entries that way and was wrong in all three.
`SHRIMP SAUCE` says "fish velouté or, failing this, Béchamel" — the source
named both and chose neither, and the parser answered Béchamel because B sorts
before V. That is an arbitrary choice wearing the costume of determinism.

## Determinism bought reproducibility, not accuracy

The argument for writing a parser before reaching for a model usually runs like
this: a model asked for JSON returns well-formed JSON, with a plausible parent
for every entry, and those outputs pass validation, read correctly, and are
wrong. Confidently wrong output that validates is the failure mode you cannot
see.

Every word of that is true, and none of it is a property of models. My parser
did it. No weights, no sampling, no temperature. It produced a well-formed,
schema-valid, internally consistent catalogue in which vanilla ice cream was a
sauce and grilled tomatoes descended from a mother sauce. It did so
reproducibly, which meant only that it was wrong the same way every time.

A deterministic system is not a system that cannot be wrong. It is a system
whose wrongness holds still while you look at it. That turns out to be worth a
great deal — but only if something makes you look.

## Who caught it

Not a test. No reasonable test asserts that a cookbook parser hasn't found ice
cream.

Copilot did, reviewing the pull request:

> `is_sauce` treats any title containing a mother concept id as a sauce. In the
> committed corpus this pulls in clear non-sauce entries such as `390—MOCK
> TOMATOES` (folds to `mock-tomatoes`, which matches `tomato`) and dish
> headings like `829—SOLE A LA HOLLANDAISE`. This will inflate the catalogue
> and break the documented/published counts.

It flagged the alphabetical parent bug in the same review, and it was right
about both.

Two separate properties of this release made that review possible, and they are
worth pulling apart, because only one of them is the one people skip.

The first is that the output is legible. The catalogue is a JSON file of
titles a person can read, and `BOMBE HOLLANDAISE` sitting in a list of sauces
is wrong on sight — no line number required. That is why this release writes
JSON files rather than a database: while a human is still verifying a parser,
inspectable by eye is the correct storage format.

The second is provenance, and it is what turned a suspicion into a finding.
Every claim names an entry and a line in a file that ships with the repo:

```console
$ sed -n '1680p' corpus/escoffier-1907.txt
32—SAUCE BORDELAISE
```

Notice what the review quoted: `390—MOCK TOMATOES`, `829—SOLE A LA
HOLLANDAISE`. Entry numbers, because entry numbers were there to quote. That is
the difference between "this rule looks too loose" and a report you can act on
in an afternoon — and it is what made the damage countable afterwards rather
than merely regrettable: forty of 166, thirty of 64.

Neither property has anything to do with determinism. A model that emitted the
same catalogue with the same fields would have been exactly as catchable. One
that emitted bare strings with no references would not have been, and neither
would this parser.

Four things in this release do that job, and they are the four I would keep if
I started over on a different book tomorrow:

| Commitment | Costs | Buys |
| --- | --- | --- |
| Every claim carries source id, entry, and line | Two integers per record | A wrong answer becomes a findable one |
| Terms carry a language tag, never a translation | One field | *Nixtamal* survives as *nixtamal*, not "corn" |
| Unresolved is recorded as unresolved, never as "none" | A worse-looking coverage number | A later stage can fill it without overwriting a fact |
| Ambiguity resolves to nothing | Three fewer derivations | No arbitrary choice is ever recorded as a reading |

None of those require a model to be absent. They are what makes a model
*addable* later without destroying the record — extraction sits behind a port,
so the thing that fills `parent` can change while every guarantee about
traceability holds.

## Who gets to decide what a sauce is

The fix is not a better substring test. It is a rule about authority.

An entry now enters the catalogue on evidence the source supplies. Its heading
uses the singular word "sauce" before any "with" — so `SOUBISE SAUCE WITH RICE`
is a sauce served with something, and `ASPARAGUS WITH VARIOUS SAUCES` is
something served with a sauce. Or its heading names a mother and Escoffier
filed it in one of the three chapters he titled `THE LEADING WARM SAUCES`, `THE
SMALL COMPOUND SAUCES`, and `COLD SAUCES AND COMPOUND BUTTERS`.

Reading those chapter titles is the same move as reading the mothers out of the
text. Deciding for ourselves that a velouté soup is not a sauce would not be,
however obviously true it is. The distinction sounds pedantic until you notice
that the first rule was exactly that kind of self-authored judgment, and it
put ice cream in a sauce catalogue.

That is [ADR-0007](https://github.com/Alberto-Codes/saucier/blob/v0.1.0/docs/adr/0007-the-source-classifies-its-own-contents.md).
The census now lives in one place that the tests and the documentation both
read, so the next time a number moves it cannot move in only three of the four
places that publish it.

## What is left: 95

Which brings back the number that was the point of all this. 95 preparations
name no mother where the parser looks.

Not all of them are silent. Twenty-seven name another catalogued sauce in
their opening paragraph — Allemande, Normande, Bordelaise, Bercy, Madeira,
plain Butter Sauce — just not one of the five. Entry 45, Marrow Sauce, opens:

> Follow the proportions as indicated under "Sauce Bordelaise" (No. 32) for the
> necessary quantity of this sauce, the Marrow Sauce being only a variety of
> the Bordelaise.

An author stating a derivation, in plain English, with a cross-reference
number. `parent: null`, because Bordelaise is not a mother. Escoffier's
structure is not a five-way star; it is a graph with depth, and resolving to
any catalogued sauce and walking the chain is a legitimate next rule —
deterministic, checkable line by line, no model required.

![A chain of four sauces descending. At the top, Espagnole, entry 22 line 1392, the only one the source explicitly calls a mother. A dashed arrow marked "assumed, not stated" runs down to half-glaze, a reduction of Espagnole the book never spells out. Another dashed "assumed, not stated" arrow runs to Sauce Bordelaise, entry 32 line 1680, whose opening says "half-glaze" and never "Espagnole", so its parent is null. A solid arrow marked "stated outright, still unresolved" runs to Marrow Sauce, entry 45 line 1895, which calls itself "only a variety of the Bordelaise" and whose parent is also null.](/saucier-unstated-chain.svg)

Which leaves roughly 68 that genuinely say nothing — and they are the
interesting ones. Bordelaise is among them. Its opening specifies shallots, red
wine, mignonette pepper, thyme, bay, and half a pint of half-glaze, and never
uses the word Espagnole, because a *demi-glace* is an Espagnole reduction and
the reader knew that. The derivation is encoded in a term rather than a
sentence.

Recovering knowledge an author assumed is exactly the work a language model can
do and a regular expression cannot. That is the case for adding one, and it is
now a priced case rather than an assertion: a model here has to beat 29,
against a source where I can tell you precisely which 68 entries it would have
to read correctly and which line each one is on.

## What breaks next

A JSON file. That is the entire storage layer — parse the book, rewrite the
file, read it back to print a tree. It stops working the first time appending
one record means rewriting 124, or a question needs answering without loading
all of it. The next post is that failure and what replaces it, which is the
only way I am willing to introduce a database.

Then one rung per post. A process graph instead of a flat record. NLP over the
68. A local model, then a frontier one, with the cost difference measured
rather than assumed. Video, where this schema has to survive input that cannot
be checked by eye — which is the real reason text came first, because text is
where you can still tell a schema bug from an extraction bug by reading.

Every one of those replaces something in this release. The regex gets replaced.
The line numbers do not.

None of which means a regular expression is the answer to your pile of
documents. It worked here because Escoffier numbered his entries, titled his
chapters, and named his own mothers — and even then it found ice cream. A book
that does none of that gives a parser nothing to read, and the first move there
is a different one.

The repo is [Alberto-Codes/saucier](https://github.com/Alberto-Codes/saucier)
and the parse takes about a second. The
[documentation site](https://alberto-codes.github.io/saucier/) carries the
tutorial, the data model, the glossary, and the seven decision records — the
API reference on it is generated from the docstrings, so it cannot drift from
the code.

If you find an entry the parser should have linked — or another ice cream —
there is
[an issue template for exactly that](https://github.com/Alberto-Codes/saucier/issues/new?template=extraction.yml).
It asks for the entry number and the source lines, because a claim about this
project should be checkable the same way the project's own claims are.
