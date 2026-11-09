"""The `/llms.txt` index for language models, per https://llmstxt.org.

Like the RSS feed, the file is generated whenever the app module is imported,
before Reflex copies `src/assets/` into the web build, so it is rebuilt on
every deploy and never committed. The output, `src/assets/llms.txt`, is
gitignored.

Every part comes from data the site already renders: the summary repeats the
home and about copy, the projects are the `PROJECTS` cards that have a public
repository (each with the first sentence of its card), and the posts are the
newest published ones (``published_posts``), so nothing here is maintained by
hand.

Examples:
    ```python
    from alberto_codes_site.llms import build_llms_txt
    from alberto_codes_site.pages.blog import _load_posts

    text = build_llms_txt(_load_posts())
    ```
"""

from datetime import date
from pathlib import Path

from alberto_codes_site.pages.blog import published_posts
from alberto_codes_site.pages.projects import PROJECTS
from alberto_codes_site.social import AUTHOR_NAME, absolute_url
from alberto_codes_site.tenure import years_at_wells_fargo

LLMS_FILE = Path(__file__).resolve().parent.parent / "assets" / "llms.txt"
RECENT_POST_COUNT = 10

_PAGES = (
    ("About", "/about", "background, education and open source work"),
    ("Experience", "/experience", "career history at Wells Fargo"),
    ("Projects", "/projects", "open source and enterprise projects"),
    ("Publications", "/publications", "published artifacts with their evidence"),
    ("Blog", "/blog", "all posts, newest first"),
    ("Resume", "/Alberto_Nieto_Resume.pdf", "PDF"),
    ("RSS feed", "/feed.xml", "full-content RSS 2.0 feed of the blog"),
)


def _summary() -> str:
    return (
        f"{AUTHOR_NAME} is a Generative AI Principal Engineer at Wells Fargo, "
        f"with {years_at_wells_fargo()} years at the company. He started as a "
        "teller and taught himself to code. He designs AI systems at work, and "
        "on his own time he builds open source tools that test what models "
        "actually do, then publishes the evidence."
    )


def _first_sentence(text: str) -> str:
    head, _, _ = text.partition(". ")
    return head.rstrip(".") + "."


def build_llms_txt(posts: list[tuple[dict, str]], *, today: date | None = None) -> str:
    """Build the llms.txt document.

    Args:
        posts: ``(meta, body)`` pairs from ``_load_posts``.
        today: The build date; posts dated after it are left out.

    Returns:
        The markdown text: an H1, a summary blockquote and H2 link lists.
    """
    lines = [f"# {AUTHOR_NAME}", "", f"> {_summary()}", "", "## Pages", ""]
    for name, path, note in _PAGES:
        lines.append(f"- [{name}]({absolute_url(path)}): {note}")

    lines += ["", "## Open source projects", ""]
    for project in PROJECTS:
        if "github" not in project:
            continue
        url = project.get("docs") or project.get("link") or project["github"]
        summary = _first_sentence(str(project["description"]))
        lines.append(f"- [{project['title']}]({url}): {summary}")

    lines += ["", "## Selected posts", ""]
    for meta, _ in published_posts(posts, today=today)[:RECENT_POST_COUNT]:
        url = absolute_url(f"/blog/{meta.get('slug', '')}")
        lines.append(f"- [{meta.get('title', 'Untitled')}]({url})")

    return "\n".join(lines) + "\n"


def write_llms_txt(
    posts: list[tuple[dict, str]], path: Path = LLMS_FILE, *, today: date | None = None
) -> Path:
    """Write llms.txt to the assets directory, skipping an unchanged file.

    Args:
        posts: ``(meta, body)`` pairs from ``_load_posts``.
        path: Where to write; `src/assets/llms.txt` by default.
        today: The build date; posts dated after it are left out.

    Returns:
        The path written.
    """
    text = build_llms_txt(posts, today=today)
    if not path.is_file() or path.read_text(encoding="utf-8") != text:
        path.write_text(text, encoding="utf-8")
    return path
