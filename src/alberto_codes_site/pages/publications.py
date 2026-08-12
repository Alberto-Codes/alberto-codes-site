"""Publications page listing published artifacts with their attribution."""

import reflex as rx

PUBLICATIONS = [
    {
        "title": "Llama-3_3-Nemotron-Super-49B-v1_5-fit24gib-GGUF",
        "kind": "Quantized model",
        "date": "2026-08-11",
        "summary": (
            "A 49-billion-parameter model fitted to a single 24 GiB RTX 4090 "
            "by measuring per-layer quantization damage and solving the bit "
            "allocation against the budget, instead of applying a preset. "
            "At the same file size it drifts less from the full-precision "
            "original than the standard community quantization, and ties it "
            "on five capability benchmarks."
        ),
        "base_model": "nvidia/Llama-3_3-Nemotron-Super-49B-v1_5",
        "base_model_url": (
            "https://huggingface.co/nvidia/Llama-3_3-Nemotron-Super-49B-v1_5"
        ),
        "relation": "quantized",
        "license": "NVIDIA Open Model License · Llama 3.3 Community License",
        "contribution": (
            "The sensitivity map, the mixed-precision recipe, the pack, and "
            "the evaluation record. The weights are NVIDIA's. Built with Llama."
        ),
        "links": [
            (
                "Hugging Face",
                "box",
                "https://huggingface.co/Alberto-Codes/"
                "Llama-3_3-Nemotron-Super-49B-v1_5-fit24gib-GGUF",
            ),
            (
                "Sensitivity maps",
                "database",
                "https://huggingface.co/datasets/Alberto-Codes/"
                "Llama-3_3-Nemotron-Super-49B-v1_5-sensitivity-maps",
            ),
            (
                "Evidence",
                "flask-conical",
                "https://github.com/Alberto-Codes/vramfit/blob/main/docs/"
                "explanation/evaluating-packed-models.md",
            ),
            (
                "Writeup",
                "book-open",
                "/blog/2026-08-11-i-couldnt-tell-my-quantized-model-from-the-baseline",
            ),
        ],
    },
]


def _attribution_row(label: str, value: rx.Component | str) -> rx.Component:
    """Render one label/value row in a publication's attribution block.

    Args:
        label: The field name shown in the left column.
        value: The field value, as text or a component.

    Returns:
        An hstack pairing the label with its value.

    Examples:
        ```python
        _attribution_row("Relation", "quantized")
        ```
    """
    return rx.hstack(
        rx.text(
            label,
            size="1",
            color=rx.color("slate", 9),
            weight="medium",
            width="7em",
            flex_shrink="0",
        ),
        rx.box(value, flex="1"),
        spacing="2",
        align="start",
        width="100%",
    )


def _publication_links(links: list[tuple[str, str, str]]) -> rx.Component:
    """Render the row of links for a publication.

    Args:
        links: Tuples of (label, lucide icon name, url).

    Returns:
        A wrapping flex of link components.

    Examples:
        ```python
        _publication_links([("Hugging Face", "box", "https://example.com")])
        ```
    """
    return rx.flex(
        *[
            rx.link(
                rx.hstack(
                    rx.icon(icon, size=14),
                    rx.text(label, size="2"),
                    spacing="1",
                    align="center",
                ),
                href=url,
                is_external=url.startswith("http"),
                color=rx.color("blue", 9),
                underline="hover",
            )
            for label, icon, url in links
        ],
        wrap="wrap",
        spacing="4",
        width="100%",
    )


def publication_card(publication: dict) -> rx.Component:
    """Render one publication with its attribution block and links.

    Args:
        publication: Dict with title, kind, date, summary, base_model,
            base_model_url, relation, license, contribution, and links.

    Returns:
        A card component describing the published artifact.

    Examples:
        ```python
        publication_card(PUBLICATIONS[0])
        ```
    """
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.badge(
                    publication["kind"],
                    variant="surface",
                    size="1",
                    color_scheme="violet",
                ),
                rx.text(publication["date"], size="1", color=rx.color("slate", 9)),
                spacing="2",
                align="center",
            ),
            rx.heading(publication["title"], size="4", weight="bold"),
            rx.text(
                publication["summary"],
                size="2",
                color=rx.color("slate", 11),
                line_height="1.7",
            ),
            rx.separator(size="4"),
            rx.vstack(
                _attribution_row(
                    "Base model",
                    rx.link(
                        rx.text(publication["base_model"], size="2"),
                        href=publication["base_model_url"],
                        is_external=True,
                        color=rx.color("blue", 9),
                        underline="hover",
                    ),
                ),
                _attribution_row(
                    "Relation",
                    rx.text(
                        publication["relation"],
                        size="2",
                        color=rx.color("slate", 11),
                    ),
                ),
                _attribution_row(
                    "License",
                    rx.text(
                        publication["license"],
                        size="2",
                        color=rx.color("slate", 11),
                    ),
                ),
                _attribution_row(
                    "My work",
                    rx.text(
                        publication["contribution"],
                        size="2",
                        color=rx.color("slate", 11),
                        line_height="1.6",
                    ),
                ),
                spacing="2",
                width="100%",
            ),
            rx.separator(size="4"),
            _publication_links(publication["links"]),
            spacing="3",
            align="start",
            width="100%",
        ),
        width="100%",
    )


def publications_page() -> rx.Component:
    """Render the publications page listing published artifacts."""
    return rx.container(
        rx.vstack(
            rx.box(height="4em"),
            rx.heading("Publications", size="8", weight="bold"),
            rx.separator(size="4", color_scheme="blue"),
            rx.text(
                "Artifacts I have published, with what I contributed, what "
                "they derive from, and the evidence behind them. Every entry "
                "names its base model and license, because a derivative work "
                "is not the same as an original one.",
                size="3",
                color=rx.color("slate", 10),
                line_height="1.7",
            ),
            rx.box(height="1em"),
            rx.vstack(
                *[publication_card(p) for p in PUBLICATIONS],
                spacing="4",
                width="100%",
            ),
            spacing="4",
            max_width="48em",
        ),
        size="3",
        padding_y="6",
    )
