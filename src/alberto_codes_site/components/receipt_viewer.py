"""An Astryx Lightbox for the three original receipt photos in the OCR pilot."""

from collections.abc import Iterator

import reflex as rx
from markdown_it import MarkdownIt
from reflex.utils.imports import ImportVar

from alberto_codes_site.figures import split_figures

RECEIPT_POST_SLUG = "2026-10-26-nemotron-ocr-on-a-4090"
_RECEIPTS = {
    f"/nemotron-cord-test-{row:03}.jpg": f"Receipt {row}" for row in (20, 22, 13)
}


class ReceiptPhoto(rx.Component):
    """A locally bundled receipt thumbnail and zoomable, keyboard-accessible dialog."""

    tag = "ReceiptPhoto"
    src: rx.Var[str]
    alt: rx.Var[str]
    label: rx.Var[str]
    lib_dependencies = ["@stylexjs/stylex@0.19.2"]

    def add_imports(self) -> dict:
        """Import the published Lightbox and its scoped theme for this route."""
        return {
            "@astryxdesign/core@0.7.16": [
                ImportVar(tag="Lightbox", package_path="/Lightbox"),
                ImportVar(
                    tag="ThemeContext",
                    alias="ReceiptThemeContext",
                    package_path="/theme",
                ),
            ],
            "@astryxdesign/theme-neutral@0.7.16": [
                ImportVar(tag="neutralTheme", package_path="/built")
            ],
            "": [
                "@astryxdesign/core/astryx.css",
                "@astryxdesign/theme-neutral/theme.css",
            ],
            "react": ["useState"],
        }

    def add_custom_code(self) -> list[str]:
        """Keep viewer state on the client so the static export works offline."""
        return [
            """
// Scope Neutral to the viewer; the site owns the document theme.
const receiptTheme = {theme: neutralTheme, mode: "dark"};
function ReceiptPhoto({src, alt, label}) {
    const [open, setOpen] = useState(false);
    return (
        <figure style={{maxWidth: "40rem", margin: "1rem auto"}}>
            <button type="button" aria-label={"Enlarge " + label.toLowerCase()}
                    aria-haspopup="dialog" onClick={() => setOpen(true)}
                    style={{display: "block", cursor: "zoom-in", padding: 0,
                            border: 0, background: "transparent", color: "inherit"}}>
                <img src={src} alt={alt} width="864" height="1296" loading="lazy"
                     style={{display: "block", maxWidth: "100%", width: "auto",
                             height: "auto", maxHeight: "min(58vh, 32rem)"}} />
                <span style={{display: "block", textAlign: "left",
                              marginTop: ".4rem", textDecoration: "underline"}}>
                    Enlarge {label.toLowerCase()}
                </span>
            </button>
            <a href={src} style={{color: "var(--accent-11)", textDecoration: "underline"}}>
                Open original JPEG
            </a>
            <div data-astryx-theme="neutral" data-theme="dark" style={{colorScheme: "dark"}}>
                <ReceiptThemeContext value={receiptTheme}>
                    <Lightbox isOpen={open} onOpenChange={setOpen} hasZoom
                              media={{src, alt, caption: alt}} />
                </ReceiptThemeContext>
            </div>
        </figure>
    );
}
"""
        ]


def receipt_post_segments(body: str) -> Iterator[tuple[str, str | rx.Component]]:
    """Lift standalone pilot photos while retaining all markdown and themed figures."""
    lines = body.splitlines(keepends=True)
    start = 0
    for token in MarkdownIt().parse(body):
        children = token.children or []
        if token.type != "inline" or not token.map or len(children) != 1:
            continue
        image = children[0]
        src = image.attrGet("src")
        if image.type != "image" or src not in _RECEIPTS:
            continue
        first, last = token.map
        yield from split_figures("".join(lines[start:first]))
        yield (
            "receipt",
            ReceiptPhoto.create(src=src, alt=image.content, label=_RECEIPTS[src]),
        )
        start = last
    yield from split_figures("".join(lines[start:]))
