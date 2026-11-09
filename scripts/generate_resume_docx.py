"""Generate `Alberto_Nieto_Resume.docx` from `resume/resume.json`.

`resume/resume.json` is written from the canonical `cv.md` by
`scripts/sync_resume.py`; this script adds no facts of its own. The PDF the
site serves is rendered from the same JSON by career-ops (see
`scripts/build_resume.sh`).

Layout follows ATS conventions: one column, standard section headings, plain
paragraphs and real bullet lists, everything in the document body (no tables,
text boxes, images, or content in headers and footers). Calibri throughout,
navy accent (#1B3A5C).

Usage:
    uv run python scripts/generate_resume_docx.py [--json PATH] [--out PATH]
"""

import argparse
import json
from pathlib import Path

from docx import Document
from docx.document import Document as DocumentType
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from docx.text.paragraph import Paragraph

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_JSON = PROJECT_ROOT / "resume" / "resume.json"
DEFAULT_OUT = PROJECT_ROOT / "Alberto_Nieto_Resume.docx"

NAVY = RGBColor(0x1B, 0x3A, 0x5C)
DARK_GRAY = RGBColor(0x33, 0x33, 0x33)
MID_GRAY = RGBColor(0x55, 0x55, 0x55)
FONT = "Calibri"


def add_text(
    doc: DocumentType,
    text: str,
    *,
    size: float = 10.5,
    color: RGBColor = DARK_GRAY,
    bold: bool = False,
    before: float = 0,
    after: float = 1,
    style: str | None = None,
) -> Paragraph:
    """Add a paragraph holding one run of text.

    Args:
        doc: The document to append to.
        text: The paragraph text.
        size: Font size in points.
        color: Font color.
        bold: Whether the run is bold.
        before: Space before the paragraph, in points.
        after: Space after the paragraph, in points.
        style: A paragraph style name such as ``List Bullet``.

    Returns:
        The new paragraph.
    """
    p = doc.add_paragraph(style=style)
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    run = p.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)
    run.font.name = FONT
    run.font.color.rgb = color
    return p


def add_heading(doc: DocumentType, text: str) -> None:
    """Add a section heading with a thin navy rule beneath it.

    Args:
        doc: The document to append to.
        text: The heading text, written in capitals.
    """
    p = add_text(doc, text.upper(), size=12, color=NAVY, bold=True, before=10, after=3)
    p.paragraph_format.keep_with_next = True
    border = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    for key, value in (
        ("val", "single"),
        ("sz", "4"),
        ("space", "1"),
        ("color", "1B3A5C"),
    ):
        bottom.set(qn(f"w:{key}"), value)
    border.append(bottom)
    p._p.get_or_add_pPr().append(border)


def add_bullet(doc: DocumentType, text: str) -> None:
    """Add one bullet in the built-in ``List Bullet`` style.

    Args:
        doc: The document to append to.
        text: The bullet text.
    """
    add_text(doc, text, size=10, style="List Bullet")


def add_role(doc: DocumentType, role: dict) -> None:
    """Add a role: title and dates, company and location, context, bullets.

    Args:
        doc: The document to append to.
        role: One ``experience`` entry from the payload.
    """
    p = add_text(doc, role["role"], bold=True, before=6, after=0)
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.tab_stops.add_tab_stop(
        Inches(7.1), alignment=WD_ALIGN_PARAGRAPH.RIGHT
    )
    dates = p.add_run(f"\t{role['dates']}")
    dates.font.size = Pt(9.5)
    dates.font.name = FONT
    dates.font.color.rgb = MID_GRAY
    company = add_text(
        doc, f"{role['company']}, {role['location']}", size=9.5, color=MID_GRAY
    )
    company.paragraph_format.keep_with_next = True
    if role.get("context"):
        add_text(doc, role["context"], size=10)
    for bullet in role["bullets"]:
        add_bullet(doc, bullet)


def build(resume: dict) -> DocumentType:
    """Lay the payload out as a Word document.

    Args:
        resume: The parsed `resume/resume.json`.

    Returns:
        The document, ready to save.
    """
    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.45)
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.7)
    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = DARK_GRAY
    normal.paragraph_format.line_spacing = 1.1

    c = resume["candidate"]
    name = add_text(doc, c["name"].upper(), size=24, color=NAVY, bold=True, after=2)
    name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for line in (
        c["title"],
        "  |  ".join(
            [c["email"]]
            + [c[k]["display"] for k in ("portfolio", "linkedin", "github")]
        ),
        c["location"],
    ):
        add_text(
            doc, line, size=10, color=NAVY, after=0
        ).alignment = WD_ALIGN_PARAGRAPH.CENTER

    add_heading(doc, "Professional Summary")
    add_text(doc, resume["summary"], after=4)

    add_heading(doc, "Core Competencies")
    add_text(doc, ", ".join(resume["competencies"]), after=4)

    add_heading(doc, "Work Experience")
    for role in resume["experience"]:
        add_role(doc, role)

    add_heading(doc, "Projects")
    for project in resume["projects"]:
        p = add_text(doc, f"{project['name']}: ", color=NAVY, bold=True, after=2)
        run = p.add_run(f"{project['description']} {project['url']}")
        run.font.size = Pt(10)
        run.font.name = FONT
        run.font.color.rgb = DARK_GRAY

    add_heading(doc, "Education")
    for degree in resume["education"]:
        add_text(doc, degree["title"], bold=True, before=2, after=0)
        add_text(doc, f"{degree['org']}, {degree['location']}", color=MID_GRAY)

    add_heading(doc, "Awards")
    for award in resume["awards"]:
        add_bullet(
            doc,
            f"{award['year']}: {award['title']}"
            if award.get("year")
            else award["title"],
        )

    for skill in resume["skills"]:
        add_heading(doc, skill["category"])
        add_text(doc, skill["items"])
    return doc


def main(argv: list[str] | None = None) -> None:
    """Read the JSON payload and write the DOCX.

    Args:
        argv: Command-line arguments; ``sys.argv[1:]`` when omitted.
    """
    parser = argparse.ArgumentParser(
        description="Write the resume DOCX from resume/resume.json."
    )
    parser.add_argument(
        "--json", type=Path, default=DEFAULT_JSON, help="resume.json path"
    )
    parser.add_argument(
        "--out", type=Path, default=DEFAULT_OUT, help="DOCX output path"
    )
    args = parser.parse_args(argv)
    resume = json.loads(args.json.read_text(encoding="utf-8"))
    build(resume).save(str(args.out))
    print(f"DOCX saved to: {args.out}")


if __name__ == "__main__":
    main()
