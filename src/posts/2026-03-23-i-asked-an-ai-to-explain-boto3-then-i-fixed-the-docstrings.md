---
title: I asked an AI to explain boto3. Then I fixed the docstrings.
date: 2026-03-23
type: explanation
summary: I cloned the most downloaded Python package twice, fixed the docstrings with docvet, and asked AI to generate architecture documentation from both. The results weren't even close.
tags:
  - docstrings
  - code quality
  - python
  - ai
  - open source
---

## The experiment

boto3 is the most downloaded package on PyPI — 43 million installs a day. Every AI coding assistant that helps you write AWS code reads its docstrings. But how good are those docstrings, and does it matter?

I ran an experiment. Clone boto3 twice at the same commit (`04dfc51`, v1.42.73). Leave one copy untouched. Run [docvet](https://github.com/Alberto-Codes/docvet) on the other — 336 findings across 39 files, 50.3% docstring coverage — and fix every finding. Then ask a fresh AI agent to generate `ARCHITECTURE.md` from each copy, with no knowledge of what changed.

Same codebase. Same model. Same prompt.

The only difference: docstring quality.

## What docvet found

The audit surfaced gaps across every layer of boto3's documentation:

- **147 missing docstrings** — half of all public symbols had no documentation at all
- **82 missing Returns sections** — functions that return values but don't say what
- **27 missing Attributes sections** — classes with undocumented public attributes
- **13 missing Raises sections** — exceptions thrown but never mentioned in docs
- **45 missing Examples** — public classes with no usage examples

After a second pass with strict configuration (`ignore-private = false`, `ignore-magic = false`), docvet also surfaced gaps in private methods like `_register_default_handlers` — the architectural keystone that wires boto3's entire event-driven customization system.

## Two architecture documents, one codebase

![Architecture coverage comparison: the original agent covered 5 subsystems in 618 lines, while the docvet-fixed agent covered 9 subsystems in 484 lines — including the event system, CRT backend, DynamoDB pipeline, and docs generation](/boto3-architecture-coverage.svg)

| | Without docvet | With docvet |
|---|---|---|
| **Lines** | 618 | 484 |
| **Mermaid diagrams** | 13 | 15 |
| **Resource factory** | Covered | Covered |
| **Action execution** | Covered | Covered |
| **Collection pagination** | Covered | Covered |
| **Session lifecycle** | Covered | Covered |
| **Event-driven customization** | Not covered | Full flowchart |
| **CRT transfer backend** | Not mentioned | Dedicated diagram |
| **DynamoDB pipeline** | Basic | 3 diagrams deep |
| **Docs generation system** | Absent | Flowchart |
| **Exception hierarchy** | Not covered | Class diagram |

The untouched agent went deep on the subsystems it could reverse-engineer from code — resource factory internals, action execution flows, collection pagination. But it missed the subsystems that depend on documentation to discover: the event-driven customization wiring, the CRT backend, the documentation generation pipeline.

The docvet-fixed agent covered everything the first agent did, plus five additional subsystems — in 134 fewer lines. It didn't need to spend tokens reverse-engineering what the docstrings already explained.

The difference is clearest in the event system. The agent working with the original docstrings noted: *"Session._register_default_handlers() has no docstring at all. This is arguably the most architecturally important method in the codebase. I had to read every register() call and trace the lazy_call targets to understand the customization architecture."*

The docvet-fixed agent didn't complain about that method. It diagrammed it — because the docstring told it what was there:

![boto3's event-driven customization system: Session._register_default_handlers() wires S3 transfers, DynamoDB transforms, and EC2 tag injection via botocore events. The original agent couldn't produce this diagram.](/boto3-event-system.svg)

## Why docstrings change AI comprehension

The agents got the same facts right. Both understood that boto3 wraps botocore, that the resource factory dynamically generates classes from JSON, that collections handle pagination transparently. The difference was in *how they got there*.

Without docstrings, the agent reverse-engineers. It reads function bodies, traces imports, follows call chains. This works — AI models are remarkably good at it — but it's expensive in tokens and narrow in scope. The agent spends its budget understanding *how* individual functions work and runs out before mapping *how modules connect*.

With docstrings, the agent comprehends. It reads the module docstring, follows the See Also cross-references, checks the Returns and Raises sections, and moves on. It spends less time on each function and more time on the architecture. The result is broader coverage in fewer lines.

This aligns with what the research shows. [Macke & Doyle (NAACL 2024)](https://arxiv.org/abs/2404.03114) found that incorrect documentation degrades LLM task success by 22.6 percentage points — while missing documentation has no statistically significant effect on accuracy. The AI gets the *answers* right either way. But the path matters: reverse-engineering is slower, narrower, and misses the connections between modules that docstrings make explicit.

## The pop quiz

I tested this with targeted questions across multiple models. The cleanest example: I asked Sonnet what exceptions `S3Transfer.upload_file()` raises and how to handle them.

**Without docvet** — the agent reported: *"The docstring says only 'Upload a file to an S3 object' — zero mention of type validation or failure behavior."* It found the right answer (`ValueError` and `S3UploadFailedError`) by reading the method body.

**With docvet** — the agent reported: *"The Raises: section names both S3UploadFailedError and ValueError, which is the right starting point."* Same correct answer, found in the documentation instead of the code.

I saw this pattern across every model I tested — Opus, Sonnet, Haiku, GPT-4o, GPT-4.1. The answers converged. The sources diverged. In my testing, the docvet-fixed sessions consistently finished faster — the agents spent less time searching code for answers the docstrings already provided.

## What about wrong docstrings?

This experiment only tested missing documentation — I added docstrings where none existed. But the more dangerous case is stale documentation: a docstring that *used to be* correct but drifted from the code.

This is where docvet's freshness checks matter. The `stale-signature` rule detects functions whose signatures changed but whose docstrings weren't updated. `stale-body` catches implementation changes without corresponding doc updates. The new `extra-param-in-docstring` and `extra-raises-in-docstring` rules catch docstrings that claim behavior the code no longer exhibits.

boto3 ships new versions almost daily to track AWS API changes. In a codebase that moves that fast, freshness isn't a nice-to-have — it's the difference between documentation that helps your AI tools and documentation that actively misleads them.

## What this means for your codebase

boto3 is maintained by Amazon. It has 50.3% docstring coverage. If the most downloaded Python package has 336 documentation gaps that affect how AI understands its architecture, your codebase almost certainly has more.

The fix isn't writing docstrings for the sake of coverage metrics. It's writing docstrings that tell AI agents what they need to know: what a function returns, what it raises, how modules connect, and where to look next. docvet identifies exactly where those gaps are — and with the right configuration, it catches them in private methods and magic methods too.

```bash
pip install docvet
# or
uv add docvet --dev

docvet check --all --verbose
```

Full documentation: [alberto-codes.github.io/docvet](https://alberto-codes.github.io/docvet/)

The AI reading your code will find the answers either way. The question is whether it finds them in your documentation or reverse-engineers them from your implementation. One path is faster, broader, and produces better results. docvet makes sure the documentation is there when the AI comes looking.

Both architecture documents — [original and docvet-fixed](https://gist.github.com/Alberto-Codes/86bef0f945d6d8e30c31dbb7478c2d6e) — are available for anyone who wants to compare them side by side.
