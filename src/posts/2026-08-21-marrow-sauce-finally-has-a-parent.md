---
title: Marrow Sauce finally has a parent. The parser gave up three answers to earn it.
date: 2026-08-21
type: explanation
summary: Post two of the saucier series lets a parent be any catalogued preparation, not only one of the five mothers. Derived rises from 29 to 50 and every new derivation quotes a name the source wrote. The same rule dissolves three derivations the old parser recorded, one of them caught by peer review — and Bordelaise stays unresolved on purpose, because a term that encodes a derivation is not a statement of one.
tags:
  - ai
  - python
  - architecture
  - ai pipelines
  - saucier
  - open source
---

Post #1 ended with a promise: the next post would be the JSON file failing,
because that is the only way I am willing to introduce a database. This is not
that post. The chain resolver was promised in the same breath, it costs no
infrastructure, and it cut in line. The storage failure is still coming — and
by the end of this post it will be closer than it was, for reasons the
resolver itself just demonstrated.

Here is what changed, in one sentence: a preparation's parent may now be any
catalogued preparation, not only one of the five mothers. Here is what that
did to the census, at the tag that carries it, `v0.2.0`:

```console
$ uv run saucier parse
source      escoffier-1907
mothers     bechamel, espagnole, hollandaise, tomato, veloute
sauces      124
derived     50 linked to a stated parent
unresolved  74 state no base in their prose
```

*Correction, 2026-09-01: that `escoffier-1907` is the identifier this release
printed, and it was wrong. The file is the New and Revised Edition of January
1909, and its own title page says so. Everything else here is unaffected and
still reproduces at `v0.2.0`.
[Post three](/blog/2026-09-01-i-added-a-second-copy-of-the-same-book) is the
correction.*

Twenty-nine became fifty. Still no model, no API key, no network — a regular
expression got better at reading, nothing more. And the number I want to show
you first is not the 24 derivations it added. It is the three it took away.

## The promise, kept literally

Post #1 left Marrow Sauce as the standing embarrassment. Entry 45 opens:

> Follow the proportions as indicated under "Sauce Bordelaise" (No. 32) for the
> necessary quantity of this sauce, the Marrow Sauce being only a variety of
> the Bordelaise.

An author stating a derivation in plain English, and a record answering
`parent: null` — because Bordelaise is not a mother, and the old rule only
resolved mothers. The fix was named in that post: resolve to any catalogued
sauce and walk the chain. Deterministic, checkable line by line, no model
required.

That rule now exists, and:

```console
$ uv run saucier tree bordelaise
SAUCE BORDELAISE  [bordelaise]
└── MARROW SAUCE  (en)
```

Readers of post #1 have seen this picture before. One arrow in it is different
now.

![A chain of four sauces descending. At the top, Espagnole, entry 22 line 1392, the only one the source explicitly calls a mother. A dashed arrow marked "assumed, not stated" runs down to half-glaze, a reduction of Espagnole the book never spells out. Another dashed "assumed, not stated" arrow runs to Sauce Bordelaise, entry 32 line 1680, whose opening says "half-glaze" and never "Espagnole", so its parent is still null. The last arrow, marked "stated outright, now resolved", is solid: Marrow Sauce, entry 45 line 1895, which calls itself "only a variety of the Bordelaise", now records parent: sauce-bordelaise.](/saucier-unstated-chain-resolved.svg)

Notice what did not change. Bordelaise's own parent is still null. Its opening
names shallots, red wine, mignonette pepper, thyme, bay, and half a pint of
half-glaze — and a *demi-glace* is an Espagnole reduction, which every reader
of Escoffier knew and the book therefore never says. The resolver could have
special-cased it in one line. It did not, because a term that encodes a
derivation is not a statement of one, and the moment this parser records one
inference it stops being the baseline the eventual model gets measured
against. Bordelaise staying unresolved is not a gap in this release. It is the
bar the model post will have to clear, set in print for the second time.

## Widening the net without catching ice cream

The obvious risk here has a precedent. Post #1's original census put vanilla
ice cream in the sauce catalogue because a substring test matched `hollandaise`
inside `BOMBE HOLLANDAISE`. The old parent rule had five candidate names to
match. This one has every name in the catalogue — well over a hundred, in two
languages, many of them containing each other. Widening the candidate set
widens the ways a match can be wrong. The whole job of this release was to
take the wider set without the wider wrongness.

Three rules do that work, and each one exists because the corpus punished its
absence ([ADR-0008](https://github.com/Alberto-Codes/saucier/blob/v0.2.0/docs/adr/0008-a-parent-may-be-any-catalogued-preparation.md)):

**A statement is a whole run of words inside one sentence.** Folding an
opening paragraph flattens punctuation, and a matcher that joins words across
a full stop is the ice cream defect wearing a new costume. `tomatoes` is
still not `tomato`, and a name split across two sentences is not a name.

**A run inside the entry's own name states an ingredient, not a parent.**
Entry 138, `HORSE-RADISH SAUCE` (line 3091), opens with "finely-rasped
horse-radish" — words that match the catalogued `HORSE-RADISH OR ALBERT SAUCE`
(entry 119, line 2804). It is naming its own subject. It stays unresolved.
Mothers are exempt from this rule, because a mother is never an entry's own
subject — which is why `LENTEN ESPAGNOLE` still resolves to Espagnole.

**A longer stated name shadows the shorter one inside it.** Entry 38,
Genevoise (line 1769), opens with "add one pint of Lenten Espagnole". The word
"Espagnole" sits inside that name. Reading both would turn one clear statement
into a fake ambiguity; reading only the longer one records what the author
wrote. Under the old rule Genevoise resolved straight to the mother Espagnole —
which sounds right and is wrong. The source says Lenten Espagnole, entry 24,
line 1449, a catalogued preparation with its own stated parent. So the record
now holds a chain, every derivation in it stated:

```console
$ uv run saucier tree espagnole
BROWN SAUCE OR ESPAGNOLE  [espagnole]
├── LENTEN ESPAGNOLE  (fr)
│   └── GENEVOISE SAUCE  (en)
├── ORDINARY POIVRADE SAUCE  (en)
│   └── REFORM SAUCE  (en)
└── POIVRADE SAUCE FOR VENISON  (en)
```

Escoffier's structure was never a five-way star. The tree finally has the
depth the book always had.

## The three answers it gave back

Ambiguity still resolves to nothing: exactly one candidate in the opening
paragraph, or no parent. Post #1 made that rule sound like modesty. This
release shows what it is actually for — because with more candidates in play,
the rule started dissolving derivations the old parser had recorded.

`ANDALOUSE SAUCE` (entry 122, line 2855) was on the books as derived from the
mother Tomato. Its opening reads:

> Take the required quantity of Mayonnaise sauce (No. 126) and add to it the
> quarter of its volume of very red and concentrated tomato purée…

The old rule could only see mothers, found the word "tomato", and recorded a
derivation — read off an ingredient purée. The new rule sees two candidate
names, Mayonnaise and tomato, and two candidates means no parent. The wider
net did not just add derivations. It exposed one of the old ones as exactly
the grilled-tomatoes defect post #1 was about, one rung further up.
Chaud-froid au vert-pré (entry 75, line 2258) went the same way: its opening
names the velouté *and* the white Chaud-Froid sauce, the source chose
neither, so neither does the record.

The third one took a human. Post #1's census bugs were caught by a review
tool; this release's was caught by a person reviewing the pull request, and
it is the same species of defect one layer deeper. The resolver bound each
mother to a catalogued entry by preferring the least qualified name — which
bound the mother velouté to `THICKENED VELOUTÉ`, an alias of Allemande
(entry 27), instead of `ORDINARY VELOUTÉ SAUCE` (entry 25). Ordinary
Chaud-froid (entry 73, line 2242) opens with "substituting Allemande Sauce
for the velouté" — two stated candidates, which the bad binding collapsed
into one, so the record answered velouté where the ambiguity rule owed it
nothing. The fix binds a mother to the first preparation in source order
that answers to its name, because the source states a base before its
derivatives — and entry 73 dissolved into the unresolved column, moving the
census from 51 to 50 before either number ever got published.

A resolver that can only add derivations is a ratchet. This one handed back
three confident answers because the evidence for them stopped clearing the
bar, and that — more than the 24 additions — is why the additions are
believable.

`SHRIMP SAUCE` (entry 80, line 2322) still names fish velouté "or, failing
this, Béchamel", still gets no parent, and is still the correct answer.

## Every changed record, with receipts

Post #1 counted twenty-seven unresolved preparations that name another
catalogued sauce in their opening. The resolver records twenty-four new
derivations — the difference is the gap between naming and stating, which is
precisely the gap the three rules above enforce. Add the three dissolved
derivations and Genevoise's corrected parent and 28 records changed, every
one checkable with `sed -n` against the committed corpus:

| entry | line | preparation | before | after |
|---|---|---|---|---|
| 38 | 1769 | GENEVOISE SAUCE | espagnole | lenten-espagnole |
| 45 | 1895 | MARROW SAUCE | unresolved | sauce-bordelaise |
| 47 | 1920 | PÉRIGUEUX SAUCE | unresolved | madeira-sauce |
| 59 | 2087 | ANCHOVY SAUCE | unresolved | normande-sauce |
| 68 | 2185 | CAPER SAUCE | unresolved | butter-sauce |
| 70 | 2202 | MUSHROOM SAUCE | unresolved | allemande-sauce |
| 73 | 2242 | ORDINARY CHAUD-FROID SAUCE | veloute | unresolved |
| 75 | 2258 | CHAUD-FROID SAUCE, AU VERT-PRÉ | veloute | unresolved |
| 82 | 2347 | DIPLOMATE SAUCE | unresolved | normande-sauce |
| 83 | 2354 | HERB SAUCE | unresolved | white-wine-sauce |
| 84 | 2362 | GOOSEBERRY SAUCE | unresolved | butter-sauce |
| 86 | 2390 | OYSTER SAUCE | unresolved | normande-sauce |
| 88 | 2406 | JOINVILLE SAUCE | unresolved | normande-sauce |
| 90 | 2428 | MARINIÈRE SAUCE | unresolved | bercy-sauce |
| 94 | 2468 | MUSTARD SAUCE | unresolved | butter-sauce |
| 100 | 2560 | ORIENTAL SAUCE | unresolved | american-sauce |
| 103 | 2587 | REGENCY SAUCE | unresolved | allemande-sauce |
| 107 | 2661 | VENETIAN SAUCE | unresolved | white-wine-sauce |
| 108 | 2672 | VILLEROY SAUCE | unresolved | allemande-sauce |
| 109 | 2681 | VILLEROY SOUBISEE SAUCE | unresolved | allemande-sauce |
| 114 | 2749 | CELERY SAUCE | unresolved | cream-sauce |
| 116 | 2777 | FENNEL SAUCE | unresolved | butter-sauce |
| 119 | 2804 | HORSE-RADISH OR ALBERT SAUCE | unresolved | butter-sauce |
| 120 | 2823 | REFORM SAUCE | unresolved | ordinary-poivrade-sauce |
| 122 | 2855 | ANDALOUSE SAUCE | tomato | unresolved |
| 137 | 3083 | OXFORD SAUCE | unresolved | cumberland-sauce |
| 2412 | 38683 | SAUCE ORANGE | unresolved | apricot-sauce |
| 2414 | 38696 | GREENGAGE OR MIRABELLE SAUCE | unresolved | apricot-sauce |

Read down the *after* column and the book's real middle layer appears: plain
Butter Sauce quietly picks up five children — caper, gooseberry, mustard,
fennel, and the Albert sauce. Normande gains four. And down in the dessert
chapter, Sauce Orange and the Greengage resolve to Apricot Sauce — which is
itself unresolved, so the tree now roots in a preparation that states no base
of its own:

```console
$ uv run saucier tree apricot-sauce
APRICOT SAUCE  [apricot-sauce]
├── SAUCE ORANGE  (fr)
└── GREENGAGE OR MIRABELLE SAUCE  (en)
```

That render is not an edge case someone forgot to reject. It is the data
model saying what the source says: these two derive from that one, and that
one keeps its counsel. Unresolved is a fact about the text, not a hole in the
tree.

Two smaller guarantees ride along. Every new derivation carries the same
provenance as every old claim — source id, entry, line — which is what made
the table above checkable in an afternoon. And a preparation can never become
its own ancestor: a cycle is cleared entirely rather than broken by choosing
a derivation to keep, because choosing would be an arbitrary decision wearing
the costume of determinism, and this project already shipped one of those
(`SHRIMP SAUCE`, resolved to Béchamel because B sorts before V, corrected in
post #1).

## What this prices

The case for a model was priced in post #1 at 95 unresolved preparations. It
is now priced at 74, and the discount came from the cheapest possible vendor:
a stricter reading of what the source already says.

That matters for how the eventual model gets judged. Every derivation a
deterministic pass can recover is one the model no longer gets credit for
recovering. What remains in the 74 is the genuinely hard residue — Bordelaise,
where the derivation hides inside the term *half-glaze*; Shrimp, where the
author offered two bases and committed to neither; and the long tail of
preparations that simply never say. When a model finally reads those, its
score will mean something, because everything a regular expression could
honestly claim has already been claimed.

## What it cost to write 28 fields

One more number, and it is the ending post #1 actually promised. Changing 28
parents meant rewriting the entire catalogue — all 124 records, serialized
back out as one JSON file, because that is the entire storage layer. This
release felt the cost that post #1 only predicted: the write is all-or-nothing,
the diff is the whole file, and every future rule that touches a handful of
records will pay the same full-file toll. The next post is that seam finally
tearing, and what replaces it — which is still the only way I am willing to
introduce a database.

Everything here reproduces from the tag:

```console
$ git clone https://github.com/Alberto-Codes/saucier
$ cd saucier && git checkout v0.2.0
$ uv sync && uv run saucier parse
```

124 sauces. 50 derived, every derivation stated. 74 that keep their counsel,
on purpose. If you find a stated parent the resolver missed — or an inferred
one it should never have recorded — [the issue template](https://github.com/Alberto-Codes/saucier/issues/new?template=extraction.yml)
asks for the entry number and the source lines, because a claim about this
project should be checkable the same way the project's own claims are.
