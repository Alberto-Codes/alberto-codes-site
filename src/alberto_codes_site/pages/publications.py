"""Publications page listing published artifacts with their attribution."""

import reflex as rx

PUBLICATIONS = [
    {
        "title": "gemma-4-31B-it-fit24gib-GGUF",
        "kind": "Quantized model",
        "date": "2026-08-29",
        "summary": (
            "Google's own 4-bit build of Gemma 4 31B already fits a 24 GiB "
            "card at 16.44 GiB, so fit was never the claim. This 14.92 GiB "
            "pack ties it on four held-out benchmarks and wins one, and the "
            "freed bytes buy served context: 86,016 tokens of text against "
            "65,536, and 73,728 against 49,152 with an image aboard, behind "
            "a measured vision bound and a converted projector sidecar."
        ),
        "base_model": "google/gemma-4-31B-it-qat-q4_0-unquantized",
        "base_model_url": (
            "https://huggingface.co/google/gemma-4-31B-it-qat-q4_0-unquantized"
        ),
        "relation": "quantized",
        "license": "Apache 2.0 · Gemma 4 license note",
        "contribution": (
            "The per-layer sensitivity map, the two-arm solve, the pack, the "
            "projector conversion, the serve ladders, the vision and real-GUI "
            "campaigns, and the evaluation record. The weights and the "
            "projector are Google's."
        ),
        "links": [
            (
                "Hugging Face",
                "box",
                "https://huggingface.co/Alberto-Codes/gemma-4-31B-it-fit24gib-GGUF",
            ),
            (
                "Sensitivity maps",
                "database",
                "https://huggingface.co/datasets/Alberto-Codes/"
                "gemma-4-31B-it-sensitivity-maps",
            ),
            (
                "Evidence",
                "flask-conical",
                "https://github.com/Alberto-Codes/vramfit/blob/v0.4.0/publication/"
                "gemma-4-31b-fit24gib/card-ledger.md",
            ),
            (
                "Policy",
                "scale",
                "https://github.com/Alberto-Codes/vramfit/blob/v0.4.0/docs/adr/"
                "0030-vision-budget-sidecar.md",
            ),
            (
                "Writeup",
                "book-open",
                "/blog/2026-09-02-googles-4-bit-gemma-already-fit-my-card",
            ),
            (
                "Serve guide",
                "terminal",
                "/blog/2026-09-06-serve-gemma-4-31b-on-a-24-gib-card-with-the-context-it-was-packed-for",
            ),
        ],
    },
    {
        "title": "NVIDIA-Nemotron-3.5-Lightning-30B-A3B-fit16gib-GGUF",
        "kind": "Quantized model",
        "date": "2026-08-22",
        "summary": (
            "A 30-billion-parameter mixture-of-experts model solved to serve "
            "entirely on a 16 GiB card at 16k context. llama.cpp's compact "
            "quant types are locked out of the expert stacks that hold 93% "
            "of the parameters, so the shelf's smallest build is 17.54 GiB; "
            "this 15.76 GiB pack beats it on both ruled damage metrics and "
            "holds four leads and a tie on the fixed task slice."
        ),
        "base_model": "nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16",
        "base_model_url": (
            "https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16"
        ),
        "relation": "quantized",
        "license": "OpenMDW 1.1",
        "contribution": (
            "The stack-keyed sensitivity maps, the mixed-precision recipe, "
            "the pack, the serve validation, and the evaluation record. The "
            "weights are NVIDIA's; the importance matrix is bartowski's, "
            "linked at a pinned revision with credit."
        ),
        "links": [
            (
                "Hugging Face",
                "box",
                "https://huggingface.co/Alberto-Codes/"
                "NVIDIA-Nemotron-3.5-Lightning-30B-A3B-fit16gib-GGUF",
            ),
            (
                "Sensitivity maps",
                "database",
                "https://huggingface.co/datasets/Alberto-Codes/"
                "NVIDIA-Nemotron-3.5-Lightning-30B-A3B-sensitivity-maps",
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
                "/blog/2026-08-22-the-2-bit-label-was-4-5-bits-inside",
            ),
        ],
    },
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
