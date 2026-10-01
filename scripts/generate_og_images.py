"""Generate the 1200x630 link-preview cards under `src/assets/og/`.

Writes one card per published post (`<slug>.png`) plus the site card
(`site.png`) used by every other page. Uses the same post loader as the site,
so `draft-*.md` files are skipped exactly as they are when rendering. The
fonts are bundled in `scripts/fonts/` so the output does not depend on what the
machine has installed.

Usage (from the repository root):

    uv run python scripts/generate_og_images.py           # all missing cards
    uv run python scripts/generate_og_images.py --force   # rewrite every card

Commit the PNGs it writes alongside the post.
"""

import argparse
import sys
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from alberto_codes_site.pages.blog import _load_posts  # noqa: E402
from alberto_codes_site.social import (  # noqa: E402
    OG_ASSET_DIR,
    OG_IMAGE_HEIGHT,
    OG_IMAGE_WIDTH,
    SITE_IMAGE,
    SITE_NAME,
    post_image,
)

FONT_DIR = ROOT / "scripts" / "fonts"
BOLD = FONT_DIR / "NotoSans-Bold.ttf"
REGULAR = FONT_DIR / "NotoSans-Regular.ttf"

BACKGROUND = "#1f2020"
TITLE = "#e8e8e8"
ACCENT = "#7fb069"
MUTED = "#9a9a9a"

MARGIN_X = 80
TITLE_TOP = 170
TITLE_BOTTOM = 500
MAX_LINES = 4
LINE_SPACING = 1.2


def _wrap(text: str, font: ImageFont.FreeTypeFont, width: int) -> list[str]:
    """Greedily wrap ``text`` into lines no wider than ``width`` pixels."""
    lines: list[str] = []
    current = ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if font.getlength(trial) <= width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _fit_title(
    text: str, width: int, height: int
) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    """Pick the largest size that wraps ``text`` into at most four lines."""
    for size in range(72, 39, -2):
        font = ImageFont.truetype(str(BOLD), size)
        lines = _wrap(text, font, width)
        fits_width = all(font.getlength(line) <= width for line in lines)
        if (
            len(lines) <= MAX_LINES
            and fits_width
            and len(lines) * size * LINE_SPACING <= height
        ):
            return font, lines
    # Still too long at the smallest size: keep four lines and ellipsize.
    lines = lines[:MAX_LINES]
    last = lines[-1]
    while font.getlength(last + "…") > width and " " in last:
        last = last.rsplit(" ", 1)[0]
    lines[-1] = last + "…"
    return font, lines


def _canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    """Return a blank card with the accent bar and site name drawn."""
    image = Image.new("RGB", (OG_IMAGE_WIDTH, OG_IMAGE_HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 16, OG_IMAGE_HEIGHT), fill=ACCENT)
    draw.text(
        (MARGIN_X, 70), SITE_NAME, font=ImageFont.truetype(str(BOLD), 34), fill=ACCENT
    )
    return image, draw


def _draw_block(
    draw: ImageDraw.ImageDraw, lines: list[str], font: ImageFont.FreeTypeFont
) -> None:
    """Draw ``lines`` vertically centred in the title band."""
    line_height = font.size * LINE_SPACING
    top = TITLE_TOP + (TITLE_BOTTOM - TITLE_TOP - line_height * len(lines)) / 2
    for i, line in enumerate(lines):
        draw.text((MARGIN_X, top + i * line_height), line, font=font, fill=TITLE)


def _footer(draw: ImageDraw.ImageDraw, text: str) -> None:
    """Draw the muted footer line at the bottom left."""
    draw.text(
        (MARGIN_X, 530), text, font=ImageFont.truetype(str(REGULAR), 30), fill=MUTED
    )


def post_card(title: str, when: str) -> Image.Image:
    """Render the card for one post.

    Args:
        title: The post title.
        when: The post date as `YYYY-MM-DD`.

    Returns:
        The 1200x630 card.
    """
    image, draw = _canvas()
    font, lines = _fit_title(
        title, OG_IMAGE_WIDTH - 2 * MARGIN_X, TITLE_BOTTOM - TITLE_TOP
    )
    _draw_block(draw, lines, font)
    day = date.fromisoformat(when)
    _footer(draw, f"Alberto Nieto  ·  {day:%B} {day.day}, {day.year}")
    return image


def site_card() -> Image.Image:
    """Render the card shared by every non-post page.

    Returns:
        The 1200x630 card.
    """
    image, draw = _canvas()
    name = ImageFont.truetype(str(BOLD), 88)
    role = ImageFont.truetype(str(REGULAR), 46)
    draw.text((MARGIN_X, 220), "Alberto Nieto", font=name, fill=TITLE)
    draw.text(
        (MARGIN_X, 345), "Generative AI Principal Engineer", font=role, fill=ACCENT
    )
    return image


def main() -> None:
    """Write any missing cards (or all of them with ``--force``)."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--force", action="store_true", help="rewrite existing cards")
    args = parser.parse_args()

    OG_ASSET_DIR.mkdir(parents=True, exist_ok=True)
    jobs = [(OG_ASSET_DIR / SITE_IMAGE, site_card)]
    for meta, _ in _load_posts():
        jobs.append(
            (
                OG_ASSET_DIR / post_image(meta["slug"]),
                lambda m=meta: post_card(m["title"], m["date"]),
            )
        )
    for path, render in jobs:
        if path.exists() and not args.force:
            continue
        render().save(path, optimize=True)
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
