---
title: I cut the last sauce off the file. Every line still parsed.
date: 2026-09-04
type: explanation
summary: saucier now writes both copies of Escoffier as one stream, one record per line, so a shell can read the catalogue without importing my package. The first reader I wrote for it accepted an empty file, then a file missing its last sauce, with every remaining line valid JSON. Then a jq one-liner over the stream found a Périgueux the scan resolved and the text refused.
tags:
  - ai
  - python
  - architecture
  - ai pipelines
  - saucier
  - open source
---

I deleted the last line of a 293-line file and fed the rest to a reader I
had written for it that week. It rebuilt two catalogues, printed a census one
sauce short, and exited zero. Every line it read was valid JSON. The line I
had deleted was the scan's Strawberry Sauce, entry 2417 of the 1907 text, at
line 41807, and nothing in the stream knew it was gone.

The file exists because, after
[the line-1437 post](/blog/2026-09-03-the-book-spells-it-out-at-line-1437),
I wanted one list: every sauce that sits on half glaze, in both copies of the
book, side by side, asked from a shell and not from inside my own package. I
could not ask. The catalogue was two JSON files, one for each copy of the
book the project reads, and their shape was whatever my dataclasses were on
the day they were written. So `v0.5.0` adds two commands. `saucier export`
prints both catalogues to standard output as one stream, one complete JSON
record per line. `saucier import --check` reads that stream back, rebuilds
every catalogue in memory, prints the census, and writes nothing. The JSON
files stay as they were, and `parse`, `show`, `tree`, and `diff` do not know
the stream exists.

## One line, one record

Line 9 of the export is entry 25 of the 1909 text, the sauce Escoffier prints
at line 1467:

![One JSON record laid out with callouts. The envelope: schema saucier/1, type preparation, id escoffier-1909:line:1467, which is the catalogue and the line the heading sits on. Then catalogue escoffier-1909, title ORDINARY VELOUTÉ SAUCE, and a terms list with one entry: surface ORDINARY VELOUTÉ SAUCE, language fr, concept ordinary-veloute-sauce. Then parent pale-roux, with a note that null here means unresolved and never means the sauce has none. Then ref: entry 25, line 1467, fidelity transcription, the address a reader checks by hand. A body field follows, elided. Beneath: 293 lines, 2 catalogue records then 291 preparation records, 271,730 bytes, the same SHA-256 on every run.](/saucier-one-record.svg)

Every line says what schema it follows, what kind of record it is, and which
catalogue it belongs to, so a line can be read on its own. The two catalogue
records come first, and each states how many preparations follow it.

## Every line still parsed

Delete the last line of the export and feed the rest to the reader:

```console
$ uv run saucier export | head -n -1 | uv run saucier import --check
```

The first reader I wrote rebuilt two catalogues, printed the census with the
scan at 139 sauces instead of 140, and exited zero. Every line that survived
was complete JSON, and my reader asked nothing of the stream except that
each line parse.

![A column of 293 numbered lines. Line 1 is the catalogue record for escoffier-1909, stating 151 preparations; line 2 is the catalogue record for escoffier-1907, stating 140. Lines 3 to 292 are preparation records, drawn solid green. Line 293, STRAWBERRY SAUCE of the scan at line 41807, is drawn in dashed orange and struck through, labelled deleted. A note beside the green lines reads: every remaining line is valid JSON. An arrow from line 2 to the reader's verdict reads: line 2: catalogue 'escoffier-1907' states 140 preparations, the stream carries 139, exit 2. Caption: syntax cannot see a missing line; the record that promised a count can.](/saucier-cut-stream.svg)

That is why a catalogue record states how many preparation records belong to
it. The reader counts them in, and the line number in its refusal points at
line 2, the record that made the promise, not at the gap. The count was not
in the stream until a review deleted a line and the reader said nothing. It
was the second of three things a stream of well-formed records could lie
about and the first reader could not see.

| what the stream did | the first reader | the reader at `v0.5.0` |
| --- | --- | --- |
| arrived empty | rebuilt nothing, exit 0 | `interchange carries no catalogues`, exit 2 |
| lost its last line | census one short, exit 0 | `line 2: ... states 140 preparations, the stream carries 139`, exit 2 |
| repeated `parent` on line 9 | Velouté moved to unresolved, exit 0 | `line 9: object repeats a key: ['parent']`, exit 2 |

The empty stream matters because of the pipeline the command exists for,
`saucier export | saucier import --check`. Without `pipefail` a pipeline
reports its last command's exit status. If the export died before writing a
byte, the first reader saw an empty stream, accepted it, and the pipeline
would have finished with exit zero and the failed export behind it.

The repeated key is a property of Python's JSON parser, which keeps the last
value of a duplicated key and says nothing. Append a second `"parent":null`
to line 9 and an ordinary decoder moves Velouté from derived to unresolved
with the census off by one and nothing raised. The reader still uses the
standard parser but gives it a hook that watches the keys arrive and refuses
a repeat. Nobody found that one. I went looking once the first two had taught
me to.

## The one-liner, and the Périgueux row

Now the list I wanted, in one line of `jq` that imports nothing of mine:

```console
$ uv run saucier export \
  | jq -r 'select(.type == "preparation" and .parent == "half-glaze")
           | "\(.catalogue)  line \(.ref.line)  \(.title)"'
```

Arranged into two columns:

| escoffier-1909, the text | escoffier-1907, the scan |
| --- | --- |
| line 1680  SAUCE BORDELAISE | line 2057  SAUCE BORDELAISE |
| line 1708  BROWN CHAUD-FROID SAUCE | line 2085  BROWN CHAUD=FROID SAUCE |
| line 1750  DEVILLED SAUCE | line 2132  DEVILLED SAUCE |
| line 1841  ITALIAN SAUCE | line 2233  ITALIAN SAUCE |
| line 1874  LYONNAISE SAUCE | line 2268  LYONNAISE SAUCE |
| line 1886  MADEIRA SAUCE | line 2280  MADEIRA SAUCE |
| | line 2314  PERIQUEUX SAUCE |
| line 1930  PIQUANTE SAUCE | line 2327  PIQUANTE SAUCE |
| line 1994  ROBERT SAUCE | line 2398  ROBERT SAUCE |

Eight sauces in the text, nine in the scan, and two rows that are findings.
`BROWN CHAUD=FROID` is the scanner reading a hyphen as an equals sign at line
2085, and it stays as recorded:
[ADR-0013](https://github.com/Alberto-Codes/saucier/blob/v0.3.0/docs/adr/0013-repair-structure-never-content.md)
repairs the punctuation that delimits a record, never the characters that
constitute one, and `=` is inside the title.

The unpaired row is the one I care about. In the 1909 text Périgueux refuses
to resolve, because its opening paragraph names two catalogued sauces, half
glaze and Madeira, and
[the resolver may refuse but never rank](https://github.com/Alberto-Codes/saucier/blob/v0.3.0/docs/adr/0012-a-resolver-may-refuse-never-rank.md).
The scan records half glaze, confidently. Same sentence, same two names, and
a page break between them:

![Two panels of the same paragraph, entry 47, Périgueux Sauce. Left, escoffier-1909, the text: heading at line 1920, then one unbroken paragraph in which half-glaze at line 1923 and Madeira Sauce at line 1926 are both highlighted; the resolver reads two catalogued names and the verdict is parent unresolved, stated half-glaze, madeira-sauce. Right, escoffier-1907, the scan: heading at line 2314, half-glaze at line 2317 highlighted, then a blank line 2319 and the running page header 30 GUIDE TO MODERN COOKERY at line 2321, and only beyond them Madeira Sauce at line 2324, greyed out. The resolver reads the opening paragraph only, which ends at the blank line, so it sees one name and the verdict is parent half-glaze. Caption: the scan's paragraph ends at the blank line on 2319; the resolver never reads line 2324.](/saucier-perigueux-page-break.svg)

```console
$ uv run saucier show perigueux-sauce
PÉRIGUEUX SAUCE
entry 47, line 1920, transcription of escoffier-1909
  term  PÉRIGUEUX SAUCE  [fr]  perigueux-sauce
  parent  (unresolved)
  stated  half-glaze, madeira-sauce
```

The resolver reads the opening paragraph only. In the scan that paragraph
ends at the blank line on 2319, the running header sits on 2321, and "per
quart of Madeira Sauce" is on 2324, outside what the resolver reads. One
name left, so it answers. That is the Aurore shape from
[the second-copy post](/blog/2026-09-01-i-added-a-second-copy-of-the-same-book),
where a damaged witness resolves what a clean one honestly cannot, and the
line-1437 post already counted Périgueux among three rows of it. What is new
is where I was standing when I saw it: in a shell, with a stream and `jq`.
`grep -c '"parent":null'` on the same stream says 184, which is the 94
unresolved sauces of the text and the 90 of the scan.

## What I am not claiming

This stream is not a database. It indexes nothing, keeps no history, and
answers no question about the graph of sauces. The JSON snapshot is still
the working store behind every other command, and the stream carries records
between processes and stops there. It is also less of a stream than the word
suggests: the reader consumes one line at a time, but a catalogue is
validated whole, so rebuilding one holds all of its preparations in memory
first.

Two exports cannot be concatenated, because each carries every configured
catalogue and the reader stops at line 294 pointing back to line 1. A
catalogue id is a source id, which names a work and an edition, so two scans
of one printing would collide on every id. `saucier/1` carries one catalogue
per source id and does not pretend the identifiers can tell those texts
apart.
[ADR-0016](https://github.com/Alberto-Codes/saucier/blob/v0.5.0/docs/adr/0016-jsonl-is-the-interchange-not-a-store.md)
records those limits and why the interchange is not the store.

And there is nothing here about what Escoffier changed between 1907 and
1909. The Périgueux row is a fact about a page header and a resolver that
reads one paragraph, surfaced from a shell.

Everything here reproduces from the tag:

```console
$ git clone https://github.com/Alberto-Codes/saucier
$ cd saucier && git checkout v0.5.0
$ uv sync && uv run saucier parse
$ uv run saucier export | uv run saucier import --check
$ uv run saucier export | head -n -1 | uv run saucier import --check
```

The first pipeline prints 151 sauces and 140, then `2 catalogues and 291
preparations rebuilt. Nothing written.` The second stops at line 2. Between
them is a 293-line file that anyone with `jq` can ask about half glaze, and
that lists a Périgueux the scan resolved and the text refused. If you can
find a line in that stream that lies about the book and the reader lets
through,
[the issue template](https://github.com/Alberto-Codes/saucier/issues/new?template=extraction.yml)
asks for the entry number and the source lines. Line 2314 of the scan is
where I would start.
