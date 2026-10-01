"""Move a post SVG onto the shared figure colour tokens (ADR-0005).

Usage:
    uv run python scripts/theme_figure.py src/assets/NAME.svg \
        --map '#1f2020=bg' --map '#cccccc=ink' [--card]
    uv run python scripts/theme_figure.py --sync

The first form rewrites one figure in place. Every hex colour in a ``fill``,
``stroke`` or ``stop-color`` attribute, in a ``style`` attribute, or in the
figure's own ``<style>`` block must be named in a ``--map``; the script stops
on any colour left unmapped. It also prefixes every id with the file stem and
scopes the figure's own ``<style>`` rules under the root id, because inlined
figures share one document. ``--card`` adds a full-size background rect for a
figure that was transparent. A fill mapped to a ``*-soft`` token drops its
``fill-opacity``: the soft token already is the tint.

Before writing, the script compares the old and new trees element by element
and stops if anything other than colour, ids and the added style and card
changed: no number, label or coordinate may move.

``--sync`` rewrites the token block in every migrated figure after the values
in ``src/alberto_codes_site/figures.py`` change.
"""

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from alberto_codes_site.figures import (  # noqa: E402
    ASSETS_DIR,
    FIGURE_TOKENS,
    TOKEN_BLOCK_MARKER,
    token_style_block,
)

HEX = r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b"
COLOUR_ATTRS = ("fill", "stroke", "stop-color")
TOKEN_BLOCK_RE = re.compile(r"<style>/\* fig-tokens v\d+:.*?</style>", re.S)
CARD = (
    '<rect x="0" y="0" width="100%" height="100%" rx="12" style="fill:var(--fig-bg)"/>'
)


def _token(colour: str, mapping: dict[str, str]) -> str:
    key = colour.lower()
    if key not in mapping:
        raise SystemExit(f"unmapped colour {colour}; add --map '{key}=<token>'")
    return mapping[key]


def _decl(m: re.Match, mapping: dict[str, str]) -> str:
    return f"{m[1]}:{m[2]}var(--fig-{_token(m[3], mapping)})"


def _rewrite_tag(tag: str, mapping: dict[str, str]) -> str:
    if tag.startswith(("<!", "<?", "</")):
        return tag
    decls: list[str] = []
    soft = False
    for attr in COLOUR_ATTRS:
        m = re.search(rf'\s{attr}="({HEX})"', tag)
        if m:
            token = _token(m[1], mapping)
            soft = soft or (attr == "fill" and token.endswith("-soft"))
            decls.append(f"{attr}:var(--fig-{token})")
            tag = tag[: m.start()] + tag[m.end() :]
    style = re.search(r'\sstyle="([^"]*)"', tag)
    if style:
        body = re.sub(
            r"(fill|stroke|stop-color)\s*:(\s*)(" + HEX + ")",
            lambda d: _decl(d, mapping),
            style[1],
        )
        soft = soft or bool(re.search(r"fill:\s*var\(--fig-[\w-]+-soft\)", body))
        if body != style[1] or decls:
            merged = ";".join(x for x in [body.rstrip(";"), *decls] if x)
            tag = tag[: style.start()] + f' style="{merged}"' + tag[style.end() :]
    elif decls:
        end = -2 if tag.endswith("/>") else -1
        tag = tag[:end].rstrip() + f' style="{";".join(decls)}"' + tag[end:]
    if soft:
        tag = re.sub(r'\sfill-opacity="[^"]*"', "", tag)
    return tag


def _scope_figure_style(css: str, scope: str, mapping: dict[str, str]) -> str:
    def rule(m: re.Match) -> str:
        selectors = ", ".join(f"{scope} {s.strip()}" for s in m[2].split(","))
        decls = re.sub(
            r"(fill|stroke|stop-color)\s*:(\s*)(" + HEX + ")",
            lambda d: _decl(d, mapping),
            m[3],
        )
        return f"{m[1]}{selectors} {{{decls}}}"

    return re.sub(r"(\s*)([^{}]+?)\s*\{([^{}]*)\}", rule, css)


def migrate(path: Path, mapping: dict[str, str], card: bool) -> str:
    """Return the migrated text of one figure, after checking nothing but colour moved."""
    old = path.read_text()
    if TOKEN_BLOCK_MARKER in old:
        raise SystemExit(f"{path.name} already carries the token block; use --sync")
    stem = path.stem
    scope = f"#fig-{stem}"
    new = old

    ids = re.findall(r'\sid="([^"]+)"', new)
    for i in ids:
        new = re.sub(rf'(\sid="){re.escape(i)}"', rf'\g<1>{stem}-{i}"', new)
        new = new.replace(f"url(#{i})", f"url(#{stem}-{i})")
        new = new.replace(f'href="#{i}"', f'href="#{stem}-{i}"')
    new = re.sub(
        r'aria-labelledby="([^"]+)"',
        lambda m: 'aria-labelledby="'
        + " ".join(f"{stem}-{x}" for x in m[1].split())
        + '"',
        new,
    )

    new = re.sub(
        r"(<style>)(.*?)(</style>)",
        lambda m: m[1] + _scope_figure_style(m[2], scope, mapping) + m[3],
        new,
        count=1,
        flags=re.S,
    )
    new = re.sub(r"<[^<>]+>", lambda m: _rewrite_tag(m[0], mapping), new)

    root = re.search(r"<svg\b[^>]*>", new)
    root_tag = root[0]
    if re.search(r'\sid="', root_tag):
        raise SystemExit("root <svg> already has an id; handle by hand")
    root_tag = root_tag.replace("<svg ", f'<svg id="fig-{stem}" ', 1)
    new = new[: root.start()] + root_tag + new[root.end() :]

    first_style = new.find("<style>")
    insert_at = (
        first_style if first_style != -1 else new.find(">", new.find("<svg")) + 1
    )
    addition = token_style_block() + "\n  "
    if first_style == -1:
        addition = "\n  " + token_style_block()
    new = new[:insert_at] + addition + new[insert_at:]
    if card:
        style_end = new.rfind("</style>")
        cut = style_end + len("</style>")
        new = new[:cut] + "\n  " + CARD + new[cut:]

    leftover = [
        c
        for c in re.findall(
            r"(?:fill|stroke|stop-color)\s*[:=]\s*\"?(" + HEX + ")", new
        )
    ]
    if leftover:
        raise SystemExit(f"colours left unmapped: {sorted(set(leftover))}")
    _assert_same_geometry(old, new, stem)
    return new


def _normalise(el: ET.Element, stem: str) -> tuple:
    attrs = {}
    for k, v in el.attrib.items():
        name = k.split("}")[-1]
        if name in COLOUR_ATTRS or name in ("fill-opacity", "aria-labelledby"):
            continue
        if name == "id":
            v = v.removeprefix(f"{stem}-")
        if name == "style":
            v = ";".join(
                d.strip()
                for d in v.split(";")
                if d.strip() and not re.match(r"\s*(fill|stroke|stop-color)\s*:", d)
            )
            if not v:
                continue
        v = v.replace(f"#{stem}-", "#")
        attrs[name] = v
    return (el.tag, tuple(sorted(attrs.items())), (el.text or "").strip())


def _assert_same_geometry(old: str, new: str, stem: str) -> None:
    old_root, new_root = ET.fromstring(old), ET.fromstring(new)
    new_root.attrib.pop("id", None)

    def skip(el: ET.Element) -> bool:
        tag = el.tag.split("}")[-1]
        return tag == "style" or (
            tag == "rect"
            and el.attrib.get("style") == "fill:var(--fig-bg)"
            and el.attrib.get("width") == "100%"
            and el.attrib.get("rx") == "12"
            and "id" not in el.attrib
        )

    old_els = [e for e in old_root.iter() if e.tag.split("}")[-1] != "style"]
    new_els = [e for e in new_root.iter() if not skip(e)]
    if len(old_els) != len(new_els):
        raise SystemExit(f"element count changed: {len(old_els)} -> {len(new_els)}")
    for a, b in zip(old_els, new_els, strict=True):
        if _normalise(a, stem) != _normalise(b, stem):
            raise SystemExit(
                f"non-colour change:\n {_normalise(a, stem)}\n {_normalise(b, stem)}"
            )


def sync() -> None:
    """Rewrite the token block in every figure that already carries one."""
    for path in sorted(ASSETS_DIR.glob("*.svg")):
        text = path.read_text()
        if TOKEN_BLOCK_MARKER.split(" v")[0] not in text:
            continue
        updated = TOKEN_BLOCK_RE.sub(lambda _: token_style_block(), text, count=1)
        if updated != text:
            path.write_text(updated)
            print(f"synced {path.name}")


def main() -> None:
    """Parse arguments and migrate one figure or sync all of them."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("svg", nargs="?", type=Path)
    parser.add_argument("--map", action="append", default=[], metavar="HEX=TOKEN")
    parser.add_argument("--card", action="store_true")
    parser.add_argument("--sync", action="store_true")
    args = parser.parse_args()
    if args.sync:
        sync()
        return
    if args.svg is None:
        parser.error("give an SVG path or --sync")
    mapping = {}
    for item in args.map:
        colour, token = item.split("=")
        if token not in FIGURE_TOKENS["light"]:
            parser.error(f"unknown token {token}")
        mapping[colour.lower()] = token
    args.svg.write_text(migrate(args.svg, mapping, args.card))
    print(f"migrated {args.svg.name}")


if __name__ == "__main__":
    main()
