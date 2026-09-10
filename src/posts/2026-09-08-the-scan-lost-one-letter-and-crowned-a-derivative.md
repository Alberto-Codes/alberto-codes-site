---
title: The scan lost one letter, and a derivative was crowned the mother sauce
date: 2026-09-08
type: explanation
summary: The 1907 scan reads entry 22 as BROWN SAUCE OR ESPAQNOLE, so no name in that witness held the word Espagnole except a derivative's, and saucier crowned LENTEN ESPAGNOLE as a mother with twelve preparations beneath it. The ticket blamed ranking. Measuring that fix is what found the real defect: the lookup checked that a base comes before its derivatives without ever checking that the base was there.
tags:
  - ai
  - python
  - architecture
  - ai pipelines
  - saucier
  - open source
---

Here is what `saucier tree` printed for the Espagnole family in the 1907
scan, before this week:

```console
$ uv run saucier tree espagnole --source escoffier-1907
LENTEN ESPAGNOLE  [espagnole]
├── HALF GLAZE  (en)
│   ├── SAUCE BORDELAISE  (fr)
│   ├── BROWN CHAUD=FROID SAUCE  (en)
│   ├── DEVILLED SAUCE  (en)
│   ├── ITALIAN SAUCE  (en)
│   ├── LYONNAISE SAUCE  (en)
│   ├── MADEIRA SAUCE  (en)
│   ├── PERIQUEUX SAUCE  (en)
│   ├── PIQUANTE SAUCE  (en)
│   └── ROBERT SAUCE  (en)
├── ORDINARY POIVRADE SAUCE  (en)
└── POIVRADE SAUCE FOR VENISON  (en)
```

Twelve preparations, and the sauce at the head of them is a Lenten
variation — the fish-day Espagnole, made when the ordinary one will not do.
Escoffier's entry for it opens by doubting whether it needs to exist at all.
It is a derivative wearing the crown of the base it derives from.

## One letter

The heading it should have taken:

```console
$ sed -n 1730p corpus/escoffier-1907.txt
22— BROWN  SAUCE  OR  ESPAQNOLE
$ sed -n 1392p corpus/escoffier-1909.txt
22—BROWN SAUCE OR ESPAGNOLE
```

`ESPAQNOLE`. The scanner read the G as a Q, which it does all through this
witness: `16— POULTRY QLAZE` at line 1539, `38— QENEVOISE SAUCE` at 2150,
`39— QRAND-VENEUR SAUCE` at 2222, `46— PIQNONS SAUCE` at 2300. Three of
those have been sitting in the `diff` output since the scan was added, as
rows labelled `ocr-suspected`, which is exactly what they are:

```console
  ocr-suspected   piqnons-sauce ~ pignons-sauce           PIQNONS SAUCE / PIGNONS SAUCE
  ocr-suspected   qenevoise-sauce ~ genevoise-sauce       QENEVOISE SAUCE / GENEVOISE SAUCE
  ocr-suspected   qrand-veneur-sauce ~ grand-veneur-sauce QRAND-VENEUR SAUCE / GRAND-VENEUR SAUCE
```

Harmless, and useful: that label is what
[the second-copy post](/blog/2026-09-01-i-added-a-second-copy-of-the-same-book)
added the second witness to produce. `ESPAQNOLE` is not on that list. It is
not anywhere in the diff, because entry 22's heading gives it a second name
and both witnesses key it on that one:

```console
$ uv run saucier show espaqnole --source escoffier-1907
BROWN SAUCE OR ESPAQNOLE
entry 22, line 1730, ocr of escoffier-1907
  term  BROWN SAUCE  [en]  brown-sauce
  term  ESPAQNOLE  [en]  espaqnole
  parent  brown-roux
  procedure  (unrecorded)
```

The base is there, one letter away, catalogued as `brown-sauce` in both
printings and carrying the same `brown-roux` parent in both, which is why
the diff has nothing to say about it. What entry 22 does not have is the word `espagnole`
anywhere among its names. So when the catalogue was asked which preparation
the mother concept `espagnole` names, every exact match failed, and the
search fell back to the rule for partial matches: the concept has to appear
as a whole run of words inside a name. In the 1907 witness exactly one name
satisfies that.

```text
LENTEN ESPAGNOLE   entry 24, line 1795
```

![Two states of the same lookup. Top, the heading of entry 22 as each witness carries it: the 1907 scan reads 22 em-dash BROWN SAUCE OR ESPAQNOLE at line 1730, with the Q drawn in orange, and the 1909 transcription reads ESPAGNOLE at line 1392. Below, two columns. Left, before: the only candidate for the mother espagnole is LENTEN ESPAGNOLE, entry 24 at line 1795, crowned because it is the only run match and there is nothing to rank, and the tree heads on LENTEN ESPAGNOLE with HALF GLAZE and its nine derivatives and the two Poivrade sauces beneath it. Right, after: that candidate is struck out because its opening paragraph states Espagnole, no candidate is left, the mother stays uncatalogued, and the tree heads on the bare concept espagnole with LENTEN ESPAGNOLE demoted to a child alongside the others. Caption: the guard removed one candidate in this witness, the 1907 census moved from 140 / 50 / 90 to 140 / 51 / 89, the 1909 catalogue came out byte-identical, and the heading was never repaired.](/saucier-espaqnole-mother.svg)

## The rule had a premise it never checked

[ADR-0008](https://github.com/Alberto-Codes/saucier/blob/1664e75e95c6806ce604cbab0436e4f1bdaab1e0/docs/adr/0008-a-parent-may-be-any-catalogued-preparation.md)
says a mother binds to the first preparation, in source order, that answers
to its name. The reasoning is a fact about the book: Escoffier presents a
base before its derivatives, so among several names carrying the word, the
earliest one is the base. That is true of this book, and it is the reason
`veloute` reaches `ORDINARY VELOUTÉ SAUCE` at entry 25 rather than
`ALLEMANDE SAUCE OR THICKENED VELOUTÉ` at entry 27.

The premise underneath it is that the base is among the candidates at all.
The lookup sorted the hits by where they appear and returned the first one.
It never asked whether the list it was sorting contained the thing it was
looking for. When the scanner takes the base's only copy of the name, the
list still has entries in it, the ordering rule still fires, and the code
still returns something — with no less confidence than when it is right.

There is a second casualty in the same failure. Entry 24 opens like this:

```console
$ sed -n 1797,1798p corpus/escoffier-1907.txt
Practical  men  are  not  agreed  as  to  the  need  of  Lenten
Espagnole.  The  ordinary  Espagnole  being  really  a  neutral
```

The first sentence states Espagnole on its own, because the run sits inside
`Lenten Espagnole`, and the sentence after it names the ordinary Espagnole
outright. The parent resolver reads exactly that kind of sentence and would
have recorded `espagnole` as this entry's parent. It did not, because it discards a statement that names
the entry doing the stating, and the mother lookup was telling it that
`espagnole` *was* entry 24. So the same defect that gave Lenten Espagnole a
crown also cost it the parent it plainly states. `saucier show` reported
`parent (unresolved)` and `stated no candidate` for an entry whose first
sentence names its base.

## The proposed fix was aimed at ranking

The ticket that opened this proposed that a mother bind only on an exact
name match. If nothing in the witness is named exactly `espagnole`, bind
nothing, and the bad crown disappears.

It does. There are ten mother bindings across the two witnesses: five
mothers — `bechamel`, `espagnole`, `hollandaise`, `tomato`, `veloute` —
resolved once per witness. Exactly one of the ten is an exact name match,
the 1909 `ESPAGNOLE` that Escoffier prints as the second term of entry 22's
heading. The other nine reach their base through the run rule, because what
the book prints is `BÉCHAMEL SAUCE`, `HOLLANDAISE SAUCE`, `TOMATO SAUCE`.
Binding on exact names only removes nine bindings in order to remove one
wrong one.

The census will not tell you that. Run the proposal and both witnesses come
out at the counts they should — 151 / 57 / 94 and 140 / 51 / 89 — and Lenten
Espagnole picks up the parent it states, because the self-reference that
suppressed it is gone either way. What moves is which identity a parent
names:

```diff
  escoffier-1909, binding on exact names only
- mornay-sauce  parent  bechamel
+ mornay-sauce  parent  bechamel-sauce
```

Eight parent values move like that, four in each witness: in 1909, Cream
Sauce and Mornay off `bechamel`, Maltese and Mousseline off `hollandaise`;
in 1907, Cream Sauce off `bechamel`, and Maltese, Mousseline and Noisette
off `hollandaise`. Mornay is the asymmetry — the 1907 scan splits its
heading into `MORN AY SAUCE` and its first input reads `Bdchamel Sauce`,
which reaches no catalogued name, so that witness has no `bechamel` parent
there to move, as
[the parent post](/blog/2026-09-05-the-parent-finally-has-a-verb) worked
through. `saucier tree hollandaise` then prints a bare heading with no
children in either witness, and the family survives only under
`hollandaise-sauce`, which is a heading and not a mother. That is ADR-0008's
coalescing rule — names reaching one preparation coalesce under the mother
concept — quietly reversed, and it is the rule
[the Marrow Sauce post](/blog/2026-08-21-marrow-sauce-finally-has-a-parent)
spent two and a half thousand words getting right. Eight records that were
reading the book correctly would have paid for one that was not.

The rule the proposal was aimed at turns out to decide almost nothing. Ranking by
source order arbitrates two of the ten bindings, and both of them are
velouté, the one mother in this book with three names carrying its word:

```text
veloute, escoffier-1909   ORDINARY VELOUTÉ SAUCE
                          VELOUTÉ DE VOLAILLE
                          ALLEMANDE SAUCE OR THICKENED VELOUTÉ
```

Seven of the other eight bindings have a single candidate each, and the
eighth, the 1909 Espagnole, never reaches the candidate list because its
exact name wins first. Espagnole in 1907 had a single candidate too. Nothing
was ranked, so no ranking rule could have prevented it. Measuring the
proposal is what made that visible, and the measurement is the reason the
actual defect got named: the run-match branch
never tested whether the name it crowned belonged to the base or to a
derivative of the base.

## The sentence a chef would nod at

**A mother does not bind by a name run to a preparation whose opening
paragraph states that mother.** An entry that says it is made from Espagnole
is not Espagnole.

That is
[ADR-0018](https://github.com/Alberto-Codes/saucier/blob/1664e75e95c6806ce604cbab0436e4f1bdaab1e0/docs/adr/0018-a-mother-does-not-bind-to-its-derivative.md),
and the test it applies is not new. It is the statement test ADR-0008
already used to read parents out of prose: a whole run of words, inside one
sentence, of the opening paragraph. Two questions now share it, so it moved
into
[`domain/statement.py`](https://github.com/Alberto-Codes/saucier/blob/1664e75e95c6806ce604cbab0436e4f1bdaab1e0/src/saucier/domain/statement.py)
where neither caller owns it. Resolution asks which preparations an opening
states. The lookup asks whether a candidate states the base it is being
offered as. Same reading, opposite direction.

The opening paragraph is the right place to look because of how Escoffier
writes. The first paragraph of an entry is its ingredient list. A sauce
named there is a sauce this one is built from, not one it is being compared
against — entry 22's own third paragraph, `The time required for the
despumation of an Espagnole` at line 1755, is not a claim of derivation, and
the guard does not read that far.

An exact catalogued name still wins outright, before the guard runs. A base
that names itself exactly in its own heading keeps its own identity; the
guard only ever removes run matches. Ordering is untouched, and the survivors
still rank by source order. When nothing survives, the mother is
uncatalogued in that witness, which is the honest outcome and not a
fallback:

```console
$ uv run saucier show espagnole --source escoffier-1907
no preparation named 'espagnole'
[exit 1]
```

## One line of JSON

```console
$ uv run saucier tree espagnole --source escoffier-1907
espagnole  [espagnole]
├── HALF GLAZE  (en)
│   ├── SAUCE BORDELAISE  (fr)
│   ├── BROWN CHAUD=FROID SAUCE  (en)
│   ├── DEVILLED SAUCE  (en)
│   ├── ITALIAN SAUCE  (en)
│   ├── LYONNAISE SAUCE  (en)
│   ├── MADEIRA SAUCE  (en)
│   ├── PERIQUEUX SAUCE  (en)
│   ├── PIQUANTE SAUCE  (en)
│   └── ROBERT SAUCE  (en)
├── LENTEN ESPAGNOLE  (fr)
├── ORDINARY POIVRADE SAUCE  (en)
└── POIVRADE SAUCE FOR VENISON  (en)
```

The tree heads on the bare concept, because the witness carries the
derivations without carrying a usable name for what they derive from, and
the twelve preparations that were beneath Lenten Espagnole are beside it
now. `tree lenten-espagnole` prints one line, `derives from espagnole`, and
no children.

The whole change to the parsed data is one line:

```diff
  data/escoffier-1907.json, line 126
-       "parent": null,
+       "parent": "espagnole",
```

That is entry 24 recording the base its first sentence names. It is the
only parent value that moves in either witness, and it is the 51st derived
sauce in the 1907 catalogue:

```console
escoffier-1909  151 sauces, 57 derived, 94 unresolved
escoffier-1907  140 sauces, 51 derived, 89 unresolved
```

140 / 50 / 90 became 140 / 51 / 89. The 1909 census does not move, and its
JSON and JSONL come out byte-identical to the previous release — the guard
does remove one 1909 candidate, `VELOUTÉ DE VOLAILLE`, whose opening states
velouté, but it was already losing to entry 25 on source order, so nothing
downstream notices. Two candidates removed across both witnesses, one
binding changed, nine correct bindings untouched. The `diff` summary moves
from `11 unmatched, 19 parent-changed, 36 ocr-suspected` to `11 unmatched,
18 parent-changed, 35 ocr-suspected`. One row leaves and both counters drop,
because that row carried both labels: it is Lenten Espagnole's own, marked
`parent-changed, ocr-suspected` and reading
`lenten-espagnole (none) / espagnole`. The 1909 witness always resolved that
parent, and the two printings now agree on it.

ADR-0008 stays accepted with its mother-binding clause amended, and
everything else in it intact. Its subject, shadow, ambiguity, and cycle
rules behave as before. Names reaching one preparation still coalesce under
the mother concept, so Mornay still reads `parent bechamel` and
[the record of that edge](/blog/2026-08-21-marrow-sauce-finally-has-a-parent)
still stands. A fix that is one sentence long and moves one field is what
you get when the sentence is about the book rather than about the code.

## Where this guard runs out

It reads the witness's opening prose, so it is only as good as that prose
survived. In 1907 the `VELOUTE DE VOLAILLE` opening does not state velouté,
although the 1909 opening does — which is why the guard removes that
candidate in one witness and not the other. Damage to a base's heading *and*
to a derivative's opening paragraph would defeat it exactly the way the
heading alone defeated the old rule.

The guard also reads the true base's own opening, and a base that stated its
own name there would remove itself and hand the heading to the next match in
source order. None do, which is what it means that the eight name-run
bindings survived the test: Escoffier opens a base with its quantities, not
with its name. The ninth, the 1909 `ESPAGNOLE`, is an exact catalogued name
and returns before the guard runs, so it never faced the test at all.

Entry 22 comes within a paragraph of a different trap. It names Espagnole at
line 1755, in its third paragraph, discussing how long despumation takes, and
nothing would hold it back from stating itself: an uncatalogued mother is
keyed by a bare concept that no entry holds, so no entry is held out from
stating it. Had that paragraph opened the entry, though, entry 22 would have
recorded no parent at all. Three lines on, the same paragraph names a second
mother — `the Mirepoix and the tomato are inserted from the first`, at line
1758 — and ADR-0008 takes exactly one stated candidate or no parent, so two
of them resolve to none. What catches the near-miss is a rule that already
refuses to guess, not the cycle check: nothing reaches the cycle check, and
it reads heading lines, so it could not have caught a parent that names no
entry.

And the crown is the only thing that got fixed. The scan still reads
`ESPAQNOLE`, entry 22 is still catalogued as `brown-sauce`, and
`tree brown-sauce --source escoffier-1907` still prints one line with
nothing under it, while thirteen preparations hang off a concept whose
heading the witness cannot supply.
[ADR-0013](https://github.com/Alberto-Codes/saucier/blob/v0.3.0/docs/adr/0013-repair-structure-never-content.md)
repairs the punctuation that delimits a record, never the characters inside
one, and one Q is a character inside one.
[ADR-0014](https://github.com/Alberto-Codes/saucier/blob/v0.3.0/docs/adr/0014-a-damaged-witness-cannot-establish-absence.md)
says a damaged witness cannot establish absence. This says the neighbouring
thing: a damaged witness cannot establish identity by promoting a stated
derivative when the base's name disappears. Neither one repairs anything.
They both decline to conclude.

Everything here reproduces from the tag:

```console
$ git clone https://github.com/Alberto-Codes/saucier
$ cd saucier && git checkout v0.7.0
$ uv sync && uv run saucier parse
$ uv run saucier diff escoffier-1907 escoffier-1909
$ uv run saucier tree espagnole --source escoffier-1907
$ uv run saucier show espaqnole --source escoffier-1907
$ uv run saucier show lenten-espagnole --source escoffier-1907
$ sed -n 1730p corpus/escoffier-1907.txt
$ sed -n 1795,1800p corpus/escoffier-1907.txt
```

If a heading in either witness is being read as something it is not, or if
the guard rejects a candidate you think belongs,
[the issue template](https://github.com/Alberto-Codes/saucier/issues/new?template=extraction.yml)
asks for the entry number and the source lines. Line 1730 is where I would
start.

**The release:** [saucier v0.7.0](https://github.com/Alberto-Codes/saucier/releases/tag/v0.7.0)
— the guard: a mother no longer binds by a name run to a preparation whose
opening paragraph states that mother, with ADR-0008's statement test moved
into the shared `saucier.domain.statement` so both callers apply the same
one. In the 1907 scan the mother stays uncatalogued rather than falling back
to a derivative, `saucier show espagnole --source escoffier-1907` refuses
and exits 1 where it used to print a Lenten sauce, and one field of the
parsed data moves. MIT.
