"""Write `resume/resume.json` from the canonical `cv.md`.

The JSON follows the career-ops render payload schema (`modes/pdf.md`,
"JSON Input Schema"), so the same file feeds the DOCX generator here, the
career-ops ATS PDF template, and the site's schema.org `Person`. Every text
field is copied from `cv.md` verbatim, with only markdown markup removed.

The phone number in `cv.md` is deliberately left out: the public site never
shows it.

Usage:
    uv run python scripts/sync_resume.py [--cv PATH] [--out PATH]
"""

import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_CV = Path("/var/home/Alberto-Codes/Projects/career-ops/cv.md")
DEFAULT_OUT = Path(__file__).resolve().parent.parent / "resume" / "resume.json"

TITLE = "Principal Engineer · AI, LLM Evaluation & Agents"
LINKEDIN = {
    "url": "https://www.linkedin.com/in/alberto-codes",
    "display": "linkedin.com/in/alberto-codes",
}
REQUIRED_SECTIONS = (
    "Professional Summary",
    "Areas of Expertise",
    "Open Source",
    "Recognition",
    "Professional Experience",
    "Education",
    "Languages",
)
# A dash between two fields: em dash, en dash, or a spaced hyphen.
DASH = r"\s+[—–-]\s+"
LINK = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")
LEADING_DATE = re.compile(
    r"^((?:(?:January|February|March|April|May|June|July|August|September"
    r"|October|November|December)\s+)?\d{4})" + DASH + r"(.+)$"
)


class CvFormatError(ValueError):
    """Raised when `cv.md` is missing a section or a field this parser needs."""


def strip_markdown(text: str) -> str:
    """Return text with links, emphasis and code markup removed.

    Args:
        text: A line of markdown.

    Returns:
        The plain text a reader sees.
    """
    text = LINK.sub(r"\1", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"(?<!\w)\*(.+?)\*(?!\w)", r"\1", text)
    text = text.replace("`", "")
    return text.strip()


def split_sections(markdown: str) -> tuple[list[str], dict[str, list[str]]]:
    """Split a CV into its preamble and its `##` sections.

    Args:
        markdown: The full `cv.md` text.

    Returns:
        The lines before the first `##` heading, and a map from each heading
        to its lines.
    """
    preamble: list[str] = []
    sections: dict[str, list[str]] = {}
    current = preamble
    for line in markdown.splitlines():
        if line.startswith("## "):
            current = sections.setdefault(line[3:].strip(), [])
        else:
            current.append(line)
    return preamble, sections


def bullets(lines: list[str]) -> list[str]:
    """Return the `- ` bullet texts in a block, markdown left in place.

    Args:
        lines: The lines of one section or role.

    Returns:
        Each bullet's text without its marker.
    """
    return [line[2:].strip() for line in lines if line.startswith("- ")]


def paragraphs(lines: list[str]) -> list[str]:
    """Return the non-bullet, non-heading text lines in a block.

    Args:
        lines: The lines of one section or role.

    Returns:
        The stripped text lines, in order.
    """
    return [
        line.strip()
        for line in lines
        if line.strip() and not line.startswith(("- ", "#"))
    ]


def parse_candidate(preamble: list[str]) -> dict:
    """Build the ``candidate`` block from the name, contact and location lines.

    Args:
        preamble: The lines above the first `##` heading.

    Returns:
        The candidate payload, without a phone number.

    Raises:
        CvFormatError: When the name, contact line, location, email or a
            profile link is missing.
    """
    names = [line[2:].strip() for line in preamble if line.startswith("# ")]
    rest = [
        line.strip() for line in preamble if line.strip() and not line.startswith("#")
    ]
    if not names or len(rest) < 2:
        raise CvFormatError("cv.md needs '# Name', a contact line and a location line")
    contact, location = rest[0], rest[1]
    email = re.search(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", contact)
    links = {url: label for label, url in LINK.findall(contact)}
    github = next((u for u in links if "github.com" in u), None)
    portfolio = next((u for u in links if "github.com" not in u), None)
    if not email or not github or not portfolio:
        raise CvFormatError(
            "contact line needs an email, a portfolio and a GitHub link"
        )
    return {
        "name": names[0],
        "title": TITLE,
        "email": email.group(0),
        "linkedin": dict(LINKEDIN),
        "github": {"url": github, "display": links[github]},
        "portfolio": {"url": portfolio, "display": links[portfolio]},
        "location": location,
    }


def parse_projects(lines: list[str]) -> list[dict]:
    """Parse `- **name** — description ([Link](url) · ...)` bullets.

    Args:
        lines: The Open Source section.

    Returns:
        One project per bullet, with the first link as its url.

    Raises:
        CvFormatError: When a bullet lacks a bold name, a dash or a link.
    """
    projects = []
    for item in bullets(lines):
        match = re.match(r"^\*\*(.+?)\*\*" + DASH + r"(.+)$", item)
        if not match:
            raise CvFormatError(f"Open Source bullet needs '**name** — text': {item}")
        name, body = match.groups()
        paren = body.rfind(" ([")
        link = LINK.search(body[paren:]) if paren != -1 else None
        if not link:
            raise CvFormatError(
                f"Open Source bullet needs a link parenthetical: {name}"
            )
        projects.append(
            {
                "name": name,
                "url": link.group(2),
                "description": strip_markdown(body[:paren]),
            }
        )
    return projects


def parse_awards(lines: list[str]) -> list[dict]:
    """Parse Recognition bullets, lifting a leading year or month-year.

    Args:
        lines: The Recognition section.

    Returns:
        One award per bullet; ``year`` only when the bullet starts with a date.
    """
    awards = []
    for item in bullets(lines):
        text = strip_markdown(item)
        match = LEADING_DATE.match(text)
        if match:
            awards.append({"title": match.group(2), "year": match.group(1)})
        else:
            awards.append({"title": text})
    return awards


def parse_experience(lines: list[str]) -> list[dict]:
    """Parse `### Title — Company, Location` roles.

    The company is the text before the first comma after the dash; the rest is
    the location. The first non-date paragraph under a role is its context.

    Args:
        lines: The Professional Experience section.

    Returns:
        One entry per role, in cv.md order.

    Raises:
        CvFormatError: When a role header or its `*dates*` line is malformed.
    """
    roles: list[tuple[str, list[str]]] = []
    for line in lines:
        if line.startswith("### "):
            roles.append((line[4:].strip(), []))
        elif roles:
            roles[-1][1].append(line)
    experience = []
    for header, body in roles:
        match = re.match(r"^(.+?)" + DASH + r"([^,]+),\s*(.+)$", header)
        if not match:
            raise CvFormatError(
                f"role header needs 'Title — Company, Location': {header}"
            )
        role, company, location = (part.strip() for part in match.groups())
        texts = paragraphs(body)
        if not texts or not re.fullmatch(r"\*[^*]+\*", texts[0]):
            raise CvFormatError(f"role needs a '*dates*' line: {header}")
        entry = {
            "company": company,
            "role": role,
            "location": location,
            "dates": strip_markdown(texts[0]),
        }
        if len(texts) > 1:
            entry["context"] = strip_markdown(texts[1])
        entry["bullets"] = [strip_markdown(b) for b in bullets(body)]
        experience.append(entry)
    return experience


def parse_education(lines: list[str]) -> list[dict]:
    """Parse `**Degree** — School, Location` lines.

    Args:
        lines: The Education section.

    Returns:
        One entry per degree, with no year.

    Raises:
        CvFormatError: When a line does not match the expected shape.
    """
    education = []
    for text in paragraphs(lines):
        match = re.match(r"^\*\*(.+?)\*\*" + DASH + r"([^,]+),\s*(.+)$", text)
        if not match:
            raise CvFormatError(
                f"education line needs '**Degree** — School, Location': {text}"
            )
        title, org, location = (part.strip() for part in match.groups())
        education.append({"title": title, "org": org, "location": location})
    return education


def parse_cv(markdown: str) -> dict:
    """Build the career-ops render payload from `cv.md` text.

    Args:
        markdown: The full `cv.md` text.

    Returns:
        The payload, ready to serialise as `resume/resume.json`.

    Raises:
        CvFormatError: When a required section is missing or empty.
    """
    preamble, sections = split_sections(markdown)
    missing = [
        name
        for name in REQUIRED_SECTIONS
        if not paragraphs(sections.get(name, []))
        and not bullets(sections.get(name, []))
    ]
    if missing:
        raise CvFormatError(f"cv.md is missing section(s): {', '.join(missing)}")
    competencies = " ".join(paragraphs(sections["Areas of Expertise"]))
    return {
        "lang": "en",
        "page_format": "letter",
        "candidate": parse_candidate(preamble),
        "summary": strip_markdown(
            " ".join(paragraphs(sections["Professional Summary"]))
        ),
        "competencies": [strip_markdown(c) for c in competencies.split(" · ")],
        "experience": parse_experience(sections["Professional Experience"]),
        "projects": parse_projects(sections["Open Source"]),
        "education": parse_education(sections["Education"]),
        "awards": parse_awards(sections["Recognition"]),
        "skills": [
            {
                "category": "Languages",
                "items": ", ".join(
                    strip_markdown(b) for b in bullets(sections["Languages"])
                ),
            }
        ],
    }


def main(argv: list[str] | None = None) -> int:
    """Parse the CV and write the JSON payload.

    Args:
        argv: Command-line arguments; ``sys.argv[1:]`` when omitted.

    Returns:
        The process exit code: 0 on success, 1 when cv.md cannot be parsed.
    """
    parser = argparse.ArgumentParser(description="Write resume/resume.json from cv.md.")
    parser.add_argument("--cv", type=Path, default=DEFAULT_CV, help="path to cv.md")
    parser.add_argument(
        "--out", type=Path, default=DEFAULT_OUT, help="JSON output path"
    )
    args = parser.parse_args(argv)
    try:
        payload = parse_cv(args.cv.read_text(encoding="utf-8"))
    except (OSError, CvFormatError) as error:
        print(f"sync_resume: {error}", file=sys.stderr)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
