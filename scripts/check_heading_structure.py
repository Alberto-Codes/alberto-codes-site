"""Check the heading outline of every route in a static export.

`tests/test_heading_structure.py` holds the same rules without a build; this
script confirms them on the HTML that actually ships. For each route it
requires exactly one `<h1>`, no skipped levels, and, on posts, an `id` on every
`<h2>` to `<h6>` with no id used twice.

Usage (from the repository root, after an export):

    (cd src && uv run reflex export --frontend-only --no-zip --env prod)
    uv run python scripts/check_heading_structure.py

Set `API_URL` and `DEPLOY_URL` for the export as `.github/workflows/deploy.yml`
does.

Exits non-zero when any route breaks a rule.
"""

import argparse
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD_DIR = ROOT / "src" / ".web" / "build" / "client"
SKIP = {"404.html", "__spa-fallback.html"}


class _Headings(HTMLParser):
    """Collect (level, id) for each `<h1>` to `<h6>` in document order."""

    def __init__(self) -> None:
        """Start with an empty outline."""
        super().__init__()
        self.outline: list[tuple[int, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Record a heading's level and id."""
        if len(tag) == 2 and tag[0] == "h" and tag[1] in "123456":
            self.outline.append((int(tag[1]), dict(attrs).get("id")))


def routes(build_dir: Path) -> dict[str, Path]:
    """Map each exported route to its HTML file, one file per route."""
    found: dict[str, Path] = {}
    for path in sorted(build_dir.rglob("*.html")):
        if path.name in SKIP:
            continue
        rel = path.relative_to(build_dir).as_posix()
        route = "/" + rel.removesuffix(".html").removesuffix("index").rstrip("/")
        found.setdefault(route or "/", path)
    return found


def problems(route: str, outline: list[tuple[int, str | None]]) -> list[str]:
    """List every rule a route's outline breaks."""
    found = []
    levels = [level for level, _ in outline]
    if levels.count(1) != 1:
        found.append(f"{levels.count(1)} h1 elements")
    for before, after in zip(levels, levels[1:], strict=False):
        if after > before + 1:
            found.append(f"h{before} followed by h{after}")
    if route.startswith("/blog/"):
        ids = [heading_id for level, heading_id in outline if level > 1]
        if not all(ids):
            found.append(f"{ids.count(None)} body headings without an id")
        if len(set(ids)) != len(ids):
            found.append("duplicate heading ids")
    return found


def main() -> int:
    """Check every route and print a per-route summary."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("build_dir", nargs="?", type=Path, default=BUILD_DIR)
    args = parser.parse_args()

    pages = routes(args.build_dir)
    if not pages:
        print(f"no HTML under {args.build_dir}; run the export first")
        return 1
    failures = 0
    for route, path in pages.items():
        heading_parser = _Headings()
        heading_parser.feed(path.read_text())
        outline = heading_parser.outline
        counts = " ".join(
            f"h{n}={sum(1 for level, _ in outline if level == n)}" for n in range(1, 4)
        )
        issues = problems(route, outline)
        failures += bool(issues)
        status = "FAIL " + "; ".join(issues) if issues else "ok"
        print(f"{status:<6} {counts}  {route}")
    print(f"{len(pages)} routes, {failures} failing")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
