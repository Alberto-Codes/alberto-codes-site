"""`scripts/sync_resume.py` turns cv.md into the career-ops render payload.

The fixture below is a small made-up CV in cv.md's shape, not the real one,
so these tests pin the parser rather than today's resume content.
"""

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "sync_resume", ROOT / "scripts" / "sync_resume.py"
)
assert _spec is not None and _spec.loader is not None
sync_resume = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sync_resume)

CV = """# Jane Doe

jane@example.com · +1 (555) 010-0000 · [jane.dev](https://jane.dev) · [github.com/jdoe](https://github.com/jdoe)
Tucson, Arizona

## Professional Summary

Engineer who ships **evaluated** models.

## Areas of Expertise

Python · Agents (ADK, Pydantic-AI) · CI/CD & DevOps

## Open Source

- **toolkit** — Does *one* thing well. MIT. ([GitHub](https://github.com/jdoe/toolkit) · [PyPI](https://pypi.org/project/toolkit/))
- **lonely** — PyPI only. ([PyPI](https://pypi.org/project/lonely/))

## Recognition

- 2026 — Named co-inventor on a pending patent application
- March 2024 — Spot award
- Top Performer 2018 (Reno) — Recognition for remediation

## Professional Experience

### Staff Engineer (Director) — Acme Corp, Tucson, Arizona
*Jan 2024 – Present*

Builds the evaluation platform.

- Shipped [the eval harness](https://example.com) to **five** teams
- Cut latency by 40%

### Analyst / Operations — Acme Corp / Beta Bank, Tucson, Arizona
*2010 – 2024*

- Ran the `nightly` reports

## Education

**Bachelor of Science, Computer Science** — State University, Tucson, Arizona

## Languages

- English (native)
- Spanish (bilingual)
"""


@pytest.fixture
def payload() -> dict:
    """Return the fixture CV parsed into a payload."""
    return sync_resume.parse_cv(CV)


def test_candidate_from_contact_lines_without_phone(payload: dict) -> None:
    """Name, email, links and location come from the header; the phone stays out."""
    c = payload["candidate"]
    assert c["name"] == "Jane Doe"
    assert c["email"] == "jane@example.com"
    assert c["portfolio"] == {"url": "https://jane.dev", "display": "jane.dev"}
    assert c["github"] == {
        "url": "https://github.com/jdoe",
        "display": "github.com/jdoe",
    }
    assert c["location"] == "Tucson, Arizona"
    assert len(c["title"]) <= 60
    assert "phone" not in c
    assert "555" not in json.dumps(payload)


def test_summary_and_competencies_verbatim(payload: dict) -> None:
    """Summary loses only its markup; competencies split on the middle dot."""
    assert payload["summary"] == "Engineer who ships evaluated models."
    assert payload["competencies"] == [
        "Python",
        "Agents (ADK, Pydantic-AI)",
        "CI/CD & DevOps",
    ]


def test_projects_take_first_link_and_text_before_it(payload: dict) -> None:
    """A project's url is its first link; its description is the first sentence."""
    assert payload["projects"] == [
        {
            "name": "toolkit",
            "url": "https://github.com/jdoe/toolkit",
            "description": "Does one thing well.",
        },
        {
            "name": "lonely",
            "url": "https://pypi.org/project/lonely/",
            "description": "PyPI only.",
        },
    ]


def test_awards_lift_a_leading_date_only(payload: dict) -> None:
    """A leading year or month-year becomes ``year``; a mid-text year does not."""
    assert payload["awards"] == [
        {"title": "Named co-inventor on a pending patent application", "year": "2026"},
        {"title": "Spot award", "year": "March 2024"},
        {"title": "Top Performer 2018 (Reno) — Recognition for remediation"},
    ]


def test_experience_splits_header_on_the_em_dash(payload: dict) -> None:
    """Title, company and location split on the dash and the first comma."""
    first, second = payload["experience"]
    assert first == {
        "company": "Acme Corp",
        "role": "Staff Engineer (Director)",
        "location": "Tucson, Arizona",
        "dates": "Jan 2024 – Present",
        "context": "Builds the evaluation platform.",
        "bullets": ["Shipped the eval harness to five teams", "Cut latency by 40%"],
    }
    assert second["role"] == "Analyst / Operations"
    assert second["company"] == "Acme Corp / Beta Bank"
    assert "context" not in second
    assert second["bullets"] == ["Ran the nightly reports"]


def test_education_and_languages(payload: dict) -> None:
    """Education has no year; Languages becomes one skills entry."""
    assert payload["education"] == [
        {
            "title": "Bachelor of Science, Computer Science",
            "org": "State University",
            "location": "Tucson, Arizona",
        }
    ]
    assert payload["skills"] == [
        {"category": "Languages", "items": "English (native), Spanish (bilingual)"}
    ]
    assert payload["lang"] == "en"
    assert payload["page_format"] == "letter"


@pytest.mark.parametrize("section", sync_resume.REQUIRED_SECTIONS)
def test_missing_section_fails(section: str) -> None:
    """Dropping any expected section raises instead of writing a thin payload."""
    start = CV.index(f"## {section}\n")
    end = CV.find("\n## ", start + 1)
    broken = CV[:start] + (CV[end + 1 :] if end != -1 else "")
    with pytest.raises(sync_resume.CvFormatError, match=section):
        sync_resume.parse_cv(broken)


def test_cli_exits_nonzero_on_bad_cv(tmp_path: Path) -> None:
    """The command reports a malformed CV with exit code 1 and writes nothing."""
    cv = tmp_path / "cv.md"
    cv.write_text("# Jane Doe\n\n## Professional Summary\n\nHi.\n")
    out = tmp_path / "resume.json"
    assert sync_resume.main(["--cv", str(cv), "--out", str(out)]) == 1
    assert not out.exists()


def test_cli_writes_json(tmp_path: Path) -> None:
    """A good CV writes a JSON file that round-trips to the parsed payload."""
    cv = tmp_path / "cv.md"
    cv.write_text(CV)
    out = tmp_path / "resume.json"
    assert sync_resume.main(["--cv", str(cv), "--out", str(out)]) == 0
    assert json.loads(out.read_text()) == sync_resume.parse_cv(CV)


def _role(role: str, company: str, dates: str) -> dict:
    """Return a full experience entry for the public-trim tests."""
    return {
        "company": company,
        "role": role,
        "location": "Tucson, Arizona",
        "dates": dates,
        "context": f"{role} context.",
        "bullets": [f"{role} bullet"],
    }


def test_older_roles_collapse_into_one_entry() -> None:
    """Recent roles stay whole; older ones fold into one titles-and-span entry."""
    roles = [
        _role("Lead", "Acme", "Jan 2022 – Present"),
        _role("Senior", "Acme", "2020 – Jan 2022"),
        _role("Mid", "Acme", "2018 – 2020"),
        _role("Engineer (AVP)", "Acme", "Nov 2016 – 2018"),
        _role("Manager", "Acme", "2006 – Nov 2016"),
        _role("Team Lead / Operations", "Acme / Beta Bank", "1999 – 2006"),
    ]
    trimmed = sync_resume.collapse_older_roles(roles)
    assert sync_resume.FULL_DETAIL_ROLES == 3
    assert trimmed[:3] == roles[:3]
    assert trimmed[3:] == [
        {
            "company": "Acme / Beta Bank",
            "role": "Earlier roles: Engineer (AVP), Manager, Team Lead / Operations",
            "location": "Tucson, Arizona",
            "dates": "1999 – 2018",
            "bullets": [],
        }
    ]


def test_no_older_roles_leaves_experience_unchanged(payload: dict) -> None:
    """A CV with no more than FULL_DETAIL_ROLES roles gets no folded entry."""
    assert [e["role"] for e in payload["experience"]] == [
        "Staff Engineer (Director)",
        "Analyst / Operations",
    ]


def test_projects_drop_in_declared_order(monkeypatch: pytest.MonkeyPatch) -> None:
    """Only the first DROPPED_PROJECT_COUNT names in PROJECT_DROP_ORDER go."""
    projects = [{"name": n} for n in ("keep", "b", "a", "c")]
    monkeypatch.setattr(sync_resume, "PROJECT_DROP_ORDER", ("a", "b", "c"))
    monkeypatch.setattr(sync_resume, "DROPPED_PROJECT_COUNT", 2)
    assert sync_resume.drop_projects(projects) == [{"name": "keep"}, {"name": "c"}]
    monkeypatch.setattr(sync_resume, "DROPPED_PROJECT_COUNT", 0)
    assert sync_resume.drop_projects(projects) == projects


def test_public_resume_drop_order_never_reaches_kept_projects() -> None:
    """The flagship projects are never on the drop list."""
    kept = {"typevet", "judgevet", "vramfit", "saucier", "turboquant-vllm"}
    assert not kept & set(sync_resume.PROJECT_DROP_ORDER)
    assert sync_resume.PROJECT_DROP_ORDER == (
        "adk-secure-sessions",
        "gepa-adk",
        "docvet",
    )


def test_project_description_keeps_first_sentence() -> None:
    """The cut is at the first sentence end followed by space, not inside tokens."""
    first = sync_resume.first_sentence
    assert first("Runs 3.76x faster on llama.cpp (vLLM). Second. MIT.") == (
        "Runs 3.76x faster on llama.cpp (vLLM)."
    )
    assert first("Only one sentence") == "Only one sentence"
