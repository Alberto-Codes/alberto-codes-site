"""Behavioral checks for the Gemma 4 serve how-to and its publications entry."""

from alberto_codes_site.pages.blog import _load_posts
from alberto_codes_site.pages.publications import PUBLICATIONS, publications_page

SERVE_GUIDE_SLUG = (
    "2026-09-06-serve-gemma-4-31b-on-a-24-gib-card-with-the-context-it-was-packed-for"
)


def _posts_by_slug() -> dict[str, dict]:
    return {meta["slug"]: meta for meta, _body in _load_posts()}


def test_serve_guide_loads_as_a_how_to_and_leads_the_index() -> None:
    posts = _load_posts()
    by_slug = {meta["slug"]: meta for meta, _ in posts}
    meta = by_slug[SERVE_GUIDE_SLUG]
    assert meta["type"] == "how-to"
    assert meta["date"] == "2026-09-06"
    assert meta["title"].startswith("Serve Gemma 4 31B on a 24 GiB card")
    assert "vramfit" in meta["tags"]
    assert meta["reading_time"] >= 5
    # Newest post sorts first, so the how-to leads the blog index.
    assert posts[0][0]["slug"] == SERVE_GUIDE_SLUG


def test_publication_blog_links_resolve_to_published_posts() -> None:
    slugs = _posts_by_slug()
    for pub in PUBLICATIONS:
        for _label, _icon, url in pub["links"]:
            if url.startswith("/blog/"):
                assert url.removeprefix("/blog/") in slugs, (pub["title"], url)


def test_gemma_pack_entry_carries_maps_and_serve_guide_links() -> None:
    gemma = next(p for p in PUBLICATIONS if p["title"] == "gemma-4-31B-it-fit24gib-GGUF")
    links = {label: url for label, _icon, url in gemma["links"]}
    assert links["Sensitivity maps"] == (
        "https://huggingface.co/datasets/Alberto-Codes/gemma-4-31B-it-sensitivity-maps"
    )
    assert links["Serve guide"] == f"/blog/{SERVE_GUIDE_SLUG}"
    # Sibling entries set the pattern: every pack links its maps dataset.
    for pub in PUBLICATIONS:
        if pub["kind"] == "Quantized model":
            labels = {label for label, _icon, _url in pub["links"]}
            assert "Sensitivity maps" in labels, pub["title"]
    # The page component still builds with the two extra links.
    publications_page()
