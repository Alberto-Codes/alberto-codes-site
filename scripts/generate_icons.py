"""Render the app icons under `src/assets/` from `src/assets/favicon.svg`.

The SVG is the source of truth and is served as the favicon itself. This
script writes the PNGs that cannot be SVG:

- `apple-touch-icon.png` (180x180): iOS rounds the corners itself and fills
  any transparency with black, so this one is drawn full-bleed.
- `icon-192.png` and `icon-512.png`: the icons `site.webmanifest` lists.

The renderer is CairoSVG, which ignores the SVG's dark-scheme media query, so
every PNG uses the light-scheme colours (dark tile, blue mark).

Usage (from the repository root):

    uv run --with cairosvg python scripts/generate_icons.py

Commit the PNGs it writes.
"""

from pathlib import Path

import cairosvg

ASSETS = Path(__file__).resolve().parent.parent / "src" / "assets"
SOURCE = ASSETS / "favicon.svg"

# Output file name -> (edge length in pixels, keep the rounded corners).
ICONS = {
    "apple-touch-icon.png": (180, False),
    "icon-192.png": (192, True),
    "icon-512.png": (512, True),
}


def render(svg: str, path: Path, size: int, *, rounded: bool) -> None:
    """Write one square PNG of the mark.

    Args:
        svg: The favicon SVG source.
        path: Where to write the PNG.
        size: The edge length in pixels.
        rounded: Keep the tile's rounded corners; otherwise fill the square.
    """
    if not rounded:
        svg = svg.replace(' rx="14"', "", 1)
    cairosvg.svg2png(
        bytestring=svg.encode(),
        write_to=str(path),
        output_width=size,
        output_height=size,
    )


def main() -> None:
    """Render every icon in `ICONS` next to the source SVG."""
    svg = SOURCE.read_text()
    for name, (size, rounded) in ICONS.items():
        render(svg, ASSETS / name, size, rounded=rounded)
        print(f"wrote {ASSETS / name}")


if __name__ == "__main__":
    main()
