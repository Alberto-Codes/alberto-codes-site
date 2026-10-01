"""Move a post SVG onto the shared figure colour tokens (ADR-0005).

Usage:
    uv run python scripts/theme_figure.py src/assets/NAME.svg \
        --map '#1f2020=bg' --map '#cccccc=ink' [--card]
    uv run python scripts/theme_figure.py src/assets/NAME.svg --recorded
    uv run python scripts/theme_figure.py --sync

The first form rewrites one figure in place. Every colour in a ``fill``,
``stroke`` or ``stop-color`` attribute, or in a colour property (``fill``,
``stroke``, ``color``, ``background``, ``border`` and the like) of a ``style``
attribute or of the figure's own ``<style>`` block, must be named in a
``--map``; the script stops on any colour left unmapped. Colours are matched
after normalising them to ``#rrggbb``, so ``#fff``, ``white``,
``rgb(255, 255, 255)`` and ``hsl(0, 0%, 100%)`` are one key (an alpha channel
is dropped: the token replaces the tint). A key may be qualified by property,
``--map 'color:#ffffff=ink'``, which wins over the bare colour for that
property only; that separates a colour used both as label text and as a fill.

The script also prefixes every id with the file stem and scopes the figure's
own ``<style>`` rules under the root id ``fig-<stem>``, because inlined figures
share one document. A root that already has an id (Mermaid writes
``id="my-svg"``) is renamed, and selectors written against it are rewritten
rather than nested. Mermaid's unused ``@keyframes`` are dropped, after
checking that no element uses an edge-animation class. ``--card`` adds a
full-size background rect for a figure that was transparent. A fill mapped to
a ``*-soft`` token drops its ``fill-opacity``: the soft token already is the
tint.

``--recorded`` takes the map and the card flag from ``scripts/figure_maps.toml``,
which records them for every figure migrated that way. A Mermaid figure
re-rendered from its ``.mmd`` loses the tokens, so run this on the new render.

Before writing, the script compares the old and new trees element by element
and stops if anything other than colour, ids and the added style and card
changed: no number, label or coordinate may move.

``--sync`` rewrites the token block in every migrated figure after the values
in ``src/alberto_codes_site/figures.py`` change.
"""

import argparse
import colorsys
import re
import sys
import tomllib
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

RECORD = ROOT / "scripts" / "figure_maps.toml"
HEX = r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b"
NAMED = {
    "white": "#ffffff",
    "black": "#000000",
    "lightgrey": "#d3d3d3",
    "lightgray": "#d3d3d3",
}
COLOUR = HEX + r"|rgba?\([^)]*\)|hsla?\([^)]*\)|\b(?:" + "|".join(NAMED) + r")\b"
# Named colours the script does not translate; meeting one is an error, not a
# silent leftover.
UNSUPPORTED_NAMED = (
    r"\b[a-z]*(?:red|green|blue|gr[ae]y|orange|yellow|purple|pink|brown|cyan|"
    r"magenta|silver|navy|teal|maroon|olive|lime|aqua|fuchsia|white|black|"
    r"violet|indigo|gold|beige|ivory|khaki|coral|salmon|crimson|orchid|plum|"
    r"lavender|turquoise)[a-z]*\b"
)
COLOUR_ATTRS = ("fill", "stroke", "stop-color", "flood-color", "lighting-color")
COLOUR_PROP = re.compile(
    r"fill|stroke|stop-color|color|flood-color|lighting-color|"
    r"background(?:-color)?|border(?:-(?:top|right|bottom|left))?(?:-color)?|"
    r"outline(?:-color)?"
)
DECL = re.compile(r"([\w-]+)(\s*:\s*)([^;{}]+)")
TOKEN_BLOCK_RE = re.compile(r"<style>/\* fig-tokens v\d+:.*?</style>", re.S)
KEYFRAMES = re.compile(r"@keyframes\s+[\w-]+\s*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}")
CARD = (
    '<rect x="{x}" y="{y}" width="100%" height="100%" rx="12" '
    'style="fill:var(--fig-bg)"/>'
)
LEADING = re.compile(r"\s*<(title|desc|style)\b[^>]*>.*?</\1>", re.S)


def canonical(colour: str) -> str:
    """Return a colour literal as lowercase ``#rrggbb``, dropping any alpha."""
    c = colour.strip().lower()
    if c in NAMED:
        return NAMED[c]
    if c.startswith("#"):
        if len(c) == 4:
            c = "#" + "".join(ch * 2 for ch in c[1:])
        return c
    args = re.split(r"[\s,/]+", c[c.index("(") + 1 : -1].strip())
    nums = [float(x.rstrip("%").removesuffix("deg")) for x in args if x]
    if c.startswith("rgb"):
        rgb = nums[:3]
    else:
        h, s, light = nums[:3]
        rgb = [
            x * 255 for x in colorsys.hls_to_rgb((h % 360) / 360, light / 100, s / 100)
        ]
    return "#" + "".join(f"{round(x):02x}" for x in rgb)


def _token(colour: str, prop: str, mapping: dict[str, str]) -> str:
    key = canonical(colour)
    token = mapping.get(f"{prop}:{key}") or mapping.get(key)
    if token is None:
        raise SystemExit(
            f"unmapped colour {colour} ({prop}); add --map '{key}=<token>'"
        )
    return token


def _recolour_decls(css: str, mapping: dict[str, str]) -> str:
    """Replace every colour literal in the colour properties of a declaration list."""

    def decl(m: re.Match) -> str:
        prop = m[1].lower()
        if not COLOUR_PROP.fullmatch(prop):
            return m[0]
        value = re.sub(
            COLOUR,
            lambda c: f"var(--fig-{_token(c[0], prop, mapping)})",
            m[3],
        )
        return f"{m[1]}{m[2]}{value}"

    return DECL.sub(decl, css)


def _rewrite_tag(tag: str, mapping: dict[str, str]) -> str:
    if tag.startswith(("<!", "<?", "</")):
        return tag
    decls: list[str] = []
    soft = False
    for attr in COLOUR_ATTRS:
        m = re.search(rf'\s{attr}="\s*({COLOUR})\s*"', tag)
        if m:
            token = _token(m[1], attr, mapping)
            soft = soft or (attr == "fill" and token.endswith("-soft"))
            decls.append(f"{attr}:var(--fig-{token})")
            tag = tag[: m.start()] + tag[m.end() :]
    style = re.search(r'\sstyle="([^"]*)"', tag)
    if style:
        body = _recolour_decls(style[1], mapping)
        soft = soft or bool(re.search(r"fill:\s*var\(--fig-[\w-]+-soft\)", body))
        if body != style[1] or decls:
            merged = ";".join(x for x in [body.rstrip().rstrip(";"), *decls] if x)
            tag = tag[: style.start()] + f' style="{merged}"' + tag[style.end() :]
    elif decls:
        end = -2 if tag.endswith("/>") else -1
        tag = tag[:end].rstrip() + f' style="{";".join(decls)}"' + tag[end:]
    if soft:
        tag = re.sub(r'\sfill-opacity="[^"]*"', "", tag)
    return tag


def _scope_figure_style(
    css: str, scope: str, mapping: dict[str, str], own_root: str | None
) -> str:
    """Scope every rule under ``scope`` and map its colours.

    A selector already written against the figure's own root id (``own_root``)
    is rewritten to ``scope`` instead of being nested under it.
    """
    root_sel = re.compile(rf"^#{re.escape(own_root)}(?![\w-])") if own_root else None

    def selector(s: str) -> str:
        s = s.strip()
        if root_sel and root_sel.match(s):
            return root_sel.sub(scope, s)
        return f"{scope} {s}"

    def rule(m: re.Match) -> str:
        selectors = ", ".join(selector(s) for s in m[2].split(","))
        return f"{m[1]}{selectors} {{{_recolour_decls(m[3], mapping)}}}"

    if "@" in KEYFRAMES.sub("", css):
        raise SystemExit("the figure's <style> holds an at-rule; handle by hand")
    return re.sub(r"(\s*)([^{}]+?)\s*\{([^{}]*)\}", rule, css)


def _drop_unused_keyframes(text: str) -> str:
    """Remove Mermaid's ``@keyframes``, which only edge-animation classes use."""
    if not KEYFRAMES.search(text):
        return text
    if re.search(r'\sclass="[^"]*\bedge-animation', text):
        raise SystemExit(
            "an element uses an edge animation; keep its @keyframes by hand"
        )
    return KEYFRAMES.sub("", text)


def _add_card(text: str) -> str:
    """Put the card behind everything the figure paints.

    It goes after the root's leading title, desc and style elements, before
    the first painted element, and starts at the viewBox origin.
    """
    root = re.search(r"<svg\b[^>]*>", text)
    box = re.search(r'viewBox="\s*([-\d.]+)[\s,]+([-\d.]+)', root[0])
    x, y = (box[1], box[2]) if box else ("0", "0")
    cut = root.end()
    while m := LEADING.match(text, cut):
        cut = m.end()
    return text[:cut] + "\n  " + CARD.format(x=x, y=y) + text[cut:]


def _leftover_colours(text: str) -> list[str]:
    """Return colour literals still present outside the token block."""
    text = TOKEN_BLOCK_RE.sub("", text)
    found = []
    for attr in COLOUR_ATTRS:
        found += re.findall(rf'\s{attr}="\s*((?:{COLOUR}|{UNSUPPORTED_NAMED}))', text)
    blocks = re.findall(r'\sstyle="([^"]*)"', text)
    blocks += re.findall(r"<style>(.*?)</style>", text, re.S)
    for block in blocks:
        for prop, _, value in DECL.findall(block):
            if COLOUR_PROP.fullmatch(prop.lower()):
                found += re.findall(f"{COLOUR}|{UNSUPPORTED_NAMED}", value)
    bare = re.sub(r"data:[^\"']+|&#x?[0-9a-fA-F]+;", "", text)
    found += re.findall(HEX, bare)
    return sorted(set(found))


def migrate(path: Path, mapping: dict[str, str], card: bool) -> str:
    """Return the migrated text of one figure, after checking nothing but colour moved."""
    old = path.read_text()
    if TOKEN_BLOCK_MARKER in old:
        raise SystemExit(f"{path.name} already carries the token block; use --sync")
    stem = path.stem
    scope = f"#fig-{stem}"
    new = _drop_unused_keyframes(old)

    root = re.search(r"<svg\b[^>]*>", new)
    own = re.search(r'\sid="([^"]+)"', root[0])
    own_root = own[1] if own else None
    if own_root:
        root_tag = root[0][: own.start()] + root[0][own.end() :]
        new = new[: root.start()] + root_tag + new[root.end() :]

    ids = re.findall(r'\sid="([^"]+)"', new)
    for i in ids:
        new = re.sub(rf'(\sid="){re.escape(i)}"', rf'\g<1>{stem}-{i}"', new)
        new = new.replace(f"url(#{i})", f"url(#{stem}-{i})")
        new = new.replace(f'href="#{i}"', f'href="#{stem}-{i}"')

    def css_ids(m: re.Match) -> str:
        # Mermaid's sequence CSS selects some elements by id (#arrowhead path).
        css = m[2]
        for i in ids:
            if not re.fullmatch(HEX, f"#{i}"):
                css = re.sub(rf"#{re.escape(i)}(?![\w-])", f"#{stem}-{i}", css)
        return m[1] + css + m[3]

    new = re.sub(r"(<style>)(.*?)(</style>)", css_ids, new, count=1, flags=re.S)
    new = re.sub(
        r'(aria-(?:labelledby|describedby))="([^"]+)"',
        lambda m: f'{m[1]}="' + " ".join(f"{stem}-{x}" for x in m[2].split()) + '"',
        new,
    )

    new = re.sub(
        r"(<style>)(.*?)(</style>)",
        lambda m: m[1] + _scope_figure_style(m[2], scope, mapping, own_root) + m[3],
        new,
        count=1,
        flags=re.S,
    )
    new = re.sub(r"<[^<>]+>", lambda m: _rewrite_tag(m[0], mapping), new)

    root = re.search(r"<svg\b[^>]*>", new)
    root_tag = root[0].replace("<svg ", f'<svg id="fig-{stem}" ', 1)
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
        new = _add_card(new)

    leftover = _leftover_colours(new)
    if leftover:
        raise SystemExit(f"colours left unmapped: {leftover}")
    _assert_same_geometry(old, new, stem)
    return new


def _normalise_style(v: str) -> str:
    """Drop fill/stroke/stop-color and blank every colour value in a style attribute."""
    kept = []
    for d in v.split(";"):
        d = d.strip()
        if not d or re.match(
            r"(fill|stroke|stop-color|flood-color|lighting-color)\s*:", d
        ):
            continue
        d = re.sub(r"var\(--fig-[\w-]+\)", "C", d)
        d = re.sub(COLOUR, "C", d)
        kept.append(re.sub(r"\s+", " ", d))
    return ";".join(kept)


def _normalise(el: ET.Element, stem: str) -> tuple:
    attrs = {}
    for k, v in el.attrib.items():
        name = k.split("}")[-1]
        if name in COLOUR_ATTRS or name in ("fill-opacity", "aria-labelledby"):
            continue
        if name == "aria-describedby":
            v = " ".join(x.removeprefix(f"{stem}-") for x in v.split())
        if name == "id":
            v = v.removeprefix(f"{stem}-")
        if name == "style":
            v = _normalise_style(v)
            if not v:
                continue
        v = v.replace(f"#{stem}-", "#")
        attrs[name] = v
    return (el.tag, tuple(sorted(attrs.items())), (el.text or "").strip())


def _assert_same_geometry(old: str, new: str, stem: str) -> None:
    old_root, new_root = ET.fromstring(old), ET.fromstring(new)
    old_root.attrib.pop("id", None)
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
        if (a.tail or "").strip() != (b.tail or "").strip():
            raise SystemExit(f"text changed: {a.tail!r} -> {b.tail!r}")


def parse_map(items: list[str]) -> dict[str, str]:
    """Turn ``[prop:]colour=token`` items into a lookup keyed by canonical colour."""
    mapping = {}
    for item in items:
        key, token = item.rsplit("=", 1)
        if token not in FIGURE_TOKENS["light"]:
            raise SystemExit(f"unknown token {token}")
        prop, _, colour = key.rpartition(":") if ":" in key else ("", "", key)
        if prop and "(" in prop:
            prop, colour = "", key
        mapping[f"{prop}:{canonical(colour)}" if prop else canonical(colour)] = token
    return mapping


def recorded(name: str) -> tuple[dict[str, str], bool]:
    """Return the recorded map and card flag for one figure."""
    record = tomllib.loads(RECORD.read_text())
    if name not in record:
        raise SystemExit(f"{name} has no entry in {RECORD.name}")
    entry = record[name]
    items = [f"{k}={v}" for k, v in entry["map"].items()]
    return parse_map(items), entry.get("card", False)


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
    parser.add_argument(
        "--map", action="append", default=[], metavar="[PROP:]COLOUR=TOKEN"
    )
    parser.add_argument("--card", action="store_true")
    parser.add_argument("--recorded", action="store_true")
    parser.add_argument("--sync", action="store_true")
    args = parser.parse_args()
    if args.sync:
        sync()
        return
    if args.svg is None:
        parser.error("give an SVG path or --sync")
    if args.recorded:
        if args.map or args.card:
            parser.error("--recorded takes the map and card from the record")
        mapping, card = recorded(args.svg.name)
    else:
        mapping, card = parse_map(args.map), args.card
    args.svg.write_text(migrate(args.svg, mapping, card))
    print(f"migrated {args.svg.name}")


if __name__ == "__main__":
    main()
