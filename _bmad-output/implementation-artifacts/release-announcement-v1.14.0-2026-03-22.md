# Release Announcement Drafts: Alberto-Codes/docvet v1.14.0
Generated: 2026-03-22

## Release Context

### What Shipped

docvet v1.14.0 is the largest enrichment expansion since the project's initial release. Six new rules close the gap between "docstring exists" and "docstring tells the truth about parameters, return types, deprecation, and class constructors."

**Parameter agreement checks** — Two new rules (`missing-param-in-docstring`, `extra-param-in-docstring`) compare the function signature against the `Args:` section, parameter by parameter. Supports positional-only, keyword-only, `*args`/`**kwargs` exclusion, and `self`/`cls` filtering. Covers both Google and Sphinx docstring styles.

**Reverse enrichment checks** — Three new rules (`extra-raises-in-docstring`, `extra-yields-in-docstring`, `extra-returns-in-docstring`) detect docstrings that *claim* behavior the code doesn't exhibit — the mirror of existing forward checks. Uses scope-aware AST walking to avoid false positives from nested functions.

**Trivial docstring detection** — The `trivial-docstring` rule flags summaries that restate the symbol name without adding information (e.g., `def get_user` with `"""Get user."""`). Uses CamelCase/snake_case-aware word decomposition with stop-word filtering.

**Missing deprecation notice** — `missing-deprecation` detects functions using `warnings.warn(DeprecationWarning)` or the `@deprecated` decorator (PEP 702) without mentioning deprecation in the docstring.

**Missing return type** — `missing-return-type` flags `Returns:` sections with no type when the function also lacks a return annotation. First opt-in enrichment rule (defaults to `false`).

**Undocumented init params** — `undocumented-init-params` catches classes whose `__init__` takes parameters but documents them nowhere. Also opt-in.

### Key Technical Themes

- **Truthfulness over presence** — v1.14.0 shifts docvet's focus from "does a docstring exist?" to "does it match the code?" Parameter agreement and reverse checks are the core of this shift.
- **Bidirectional verification** — Forward checks (missing sections) + reverse checks (extra sections) = complete docstring-to-code correspondence.
- **Opt-in progressive adoption** — Two rules default to `false`, letting teams enable them when ready.

### Breaking Changes

None.

### Install / Upgrade

```bash
pip install docvet==1.14.1
```

Rule count: 31 total (up from 24 in v1.13.0).

## dev.to

---
title: "Your docstrings are lying — docvet 1.14 catches them"
published: true
tags: [python, documentation, ai, developer-tools]
description: "Wrong documentation degrades AI coding accuracy by 22%. docvet 1.14 adds bidirectional verification to catch docstrings that don't match the code."
canonical_url: https://alberto.codes/blog/2026-03-22-when-docstrings-lie-your-ai-tools-pay-the-price
---

A [2024 study by Macke & Doyle](https://arxiv.org/abs/2404.03114) found that incorrect documentation degrades LLM task success by 22.6 percentage points. Missing documentation? No statistically significant effect. Your AI coding assistant performs *worse* with wrong docs than with no docs at all.

That's the gap docvet fills. And with v1.14, it closes the gap further — checking not just whether your docstrings exist, but whether they *match your code*.

## What Changed

### Parameter Agreement Checks

Two new rules — `missing-param-in-docstring` and `extra-param-in-docstring` — compare function signatures against `Args:` sections, parameter by parameter.

You know the drill: you rename `retries` to `max_retries` across a refactor, update every call site, and forget the docstring. Now docvet catches it:

```
src/client.py:47: missing-param-in-docstring Function 'connect' has parameters not documented in Args: max_retries [required]
```

Handles positional-only params (PEP 570), keyword-only, `self`/`cls` exclusion, and both Google and Sphinx styles.

### Reverse Enrichment Checks

Before 1.14, docvet asked "did the docstring mention this behavior?" Now it also asks the reverse: "does the docstring *claim* behavior the code doesn't exhibit?"

Three new rules:
- `extra-raises-in-docstring` — documents exceptions the function never raises
- `extra-yields-in-docstring` — documents yields in a non-generator
- `extra-returns-in-docstring` — documents returns the function never makes

A docstring that claims `FileNotFoundError` when the function never raises anything is a trap. Callers write `try/except` blocks for phantom exceptions. AI tools generate defensive code for errors that can't happen.

### Trivial Docstring Detection

```python
def get_user():
    """Get user."""
```

This passes every presence check but adds zero information. The `trivial-docstring` rule decomposes symbol names and summaries into word sets, filters stop words, and flags cases where the summary is just an echo of the name.

### Also in This Release

- **missing-deprecation** — catches `warnings.warn(DeprecationWarning)` or `@deprecated` (PEP 702) without a deprecation notice in the docstring
- **missing-return-type** (opt-in) — flags `Returns:` sections with no type when there's no return annotation
- **undocumented-init-params** (opt-in) — catches `__init__` methods with parameters but no `Args:` section

> **Design note:** Reverse checks use `recommended` severity (not `required`) to account for delegation patterns. Two rules are opt-in for progressive adoption. [Full design tradeoffs in the blog post.](https://alberto.codes/blog/2026-03-22-when-docstrings-lie-your-ai-tools-pay-the-price)

## Getting Started

```bash
pip install docvet==1.14.1
```

Param agreement and reverse checks are on by default. Opt-in rules:

```toml
[tool.docvet.enrichment]
require-return-type = true
require-init-params = true
```

Run it:

```bash
docvet check src/ --all --verbose
```

## What's Next

- Semantic verification — not just "did you document the parameters?" but "is what you said about them accurate?"
- Expanding multi-style support across all rule categories

---
*[PyPI](https://pypi.org/project/docvet/) | [Docs](https://alberto-codes.github.io/docvet/) | [GitHub](https://github.com/Alberto-Codes/docvet)*

## Medium

**When docstrings lie, your AI tools pay the price**

Here's something most developers haven't considered: wrong documentation is worse than no documentation — at least when AI tools are involved.

A 2024 study measured what happens when LLMs encounter incorrect docstrings. The result: task success drops by 22.6 percentage points. Missing documentation? No measurable effect. The model just reads the code directly. But a docstring that says one thing while the code does another? That actively misleads every AI tool that touches your codebase.

This matters more than it used to. Two years ago, docstrings were primarily for humans — and humans are pretty good at glancing past a stale one. But today, Copilot reads your docstrings. Claude reads them. Your IDE's autocomplete reads them. They all trust what the docstring says. And when the docstring says a function accepts `timeout` but the parameter was renamed to `max_wait` three commits ago, every suggestion that follows is subtly wrong.

Most docstring linters only check whether a docstring *exists*. That's a solved problem. The unsolved problem is whether the docstring *matches the code*. Does the `Args:` section list the actual parameters? Does the `Raises:` section describe exceptions the function actually throws? Or is the docstring describing a version of the function that no longer exists?

That's what docvet 1.14 addresses. This release introduces what I'm calling bidirectional verification — checking both directions of the docstring-to-code relationship. Forward checks ask "did you document this behavior?" Reverse checks ask "does this documented behavior actually exist in the code?"

The most impactful addition is parameter agreement checking. Two rules compare the function signature against the `Args:` section, parameter by parameter. You rename a parameter during a refactor, update every call site, and forget the docstring. docvet now catches that — for both Google and Sphinx docstring styles, with proper handling of positional-only parameters, keyword-only parameters, and the usual `self`/`cls` exclusions.

There's also a trivial docstring detector. You've seen them: `def get_user` with `"""Get user."""` — a docstring that technically exists but communicates nothing the function name doesn't already say. docvet decomposes both the name and the summary into word sets and flags cases where the summary is just an echo.

One design tradeoff worth mentioning: the reverse checks use `recommended` severity rather than `required`. A function might delegate exception handling to a helper, or a base class might document exceptions that subclasses raise. False positives are higher in the reverse direction, so we surface the issue without blocking CI. Teams can promote to `required` when they're confident in their codebase.

The broader shift here is from documentation *presence* to documentation *truthfulness*. Checking whether a docstring exists is table stakes. Checking whether it's accurate — parameter by parameter, exception by exception — is where the real quality gains live. Especially when AI tools are the primary consumers.

docvet 1.14 is on PyPI — 31 rules across six quality layers. Full technical walkthrough with code examples: https://alberto.codes/blog/2026-03-22-when-docstrings-lie-your-ai-tools-pay-the-price

*Note: Publish via Medium's Import tool (paste blog URL) or copy-paste and set canonical link manually under story settings.*

## LinkedIn

A recipe that lists salt but means sugar doesn't just fail — it ruins the dish. Stale docstrings do the same thing to AI coding tools.

A 2024 study found that incorrect documentation degrades LLM task success by 22.6 percentage points. Missing docs? No measurable effect. The AI reads the code directly. But a docstring describing a parameter renamed three commits ago? Every downstream suggestion is wrong.

Most teams check whether docstrings exist. Almost nobody checks whether they're true.

docvet 1.14 closes that gap. It now verifies both directions — did you document this behavior, and does this documented behavior actually exist in your code? Parameter by parameter, exception by exception.

Six new rules. 31 total across six quality layers. Two are opt-in for progressive adoption.

If your team ships Python libraries that other developers — or AI tools — consume, the docstring accuracy gap is costing you more than you think.

https://alberto.codes/blog/2026-03-22-when-docstrings-lie-your-ai-tools-pay-the-price

#Python #CodeQuality #AIEngineering #DeveloperTools

## X/Twitter

🧵 Wrong documentation degrades AI coding accuracy by 22.6%. Missing documentation? No measurable effect.

And nobody's been checking. Until now.

---

docvet 1.14 now checks both directions:

Forward: "you raise ValueError but didn't document it"
Reverse: "you documented FileNotFoundError but never raise it"

Bidirectional verification. Every claim checked against the code.

---

The param agreement checks are the killer feature.

Rename `retries` → `max_retries` in a refactor. Update every call site. Forget the docstring.

docvet catches it. Parameter by parameter. Google style and Sphinx.

---

Also new: trivial docstring detection.

`def get_user` with `"""Get user."""` — technically exists, communicates nothing. Now flagged.

31 rules. Six quality layers. pip install docvet==1.14.1

https://alberto.codes/blog/2026-03-22-when-docstrings-lie-your-ai-tools-pay-the-price

#Python #CodeQuality #AIEngineering

## GitHub Discussion

**Title:** docvet 1.14: Parameter Agreement, Reverse Checks, and Trivial Docstring Detection

## docvet v1.14.0

Biggest enrichment expansion yet — six new rules focused on docstring *truthfulness*, not just presence.

### Highlights

- **Parameter agreement checks** — `missing-param-in-docstring` and `extra-param-in-docstring` compare signatures against Args sections. Supports Google, Sphinx, positional-only (PEP 570), keyword-only, and `*args`/`**kwargs` exclusion.
- **Reverse enrichment** — `extra-raises-in-docstring`, `extra-yields-in-docstring`, `extra-returns-in-docstring` catch docstrings claiming behavior the code doesn't exhibit. Uses scope-aware AST walking.
- **Trivial docstring** — flags summaries that echo the symbol name without adding information (`def get_user` → `"""Get user."""`).
- **Missing deprecation** — detects `warnings.warn(DeprecationWarning)` or `@deprecated` (PEP 702) without a docstring notice.
- **Missing return type** (opt-in) — flags `Returns:` with no type when there's no return annotation.
- **Undocumented init params** (opt-in) — catches `__init__` with parameters but no `Args:` section.

### Install / Upgrade

```bash
pip install docvet==1.14.1
```

Param agreement and reverse checks are on by default. Opt-in rules:

```toml
[tool.docvet.enrichment]
require-return-type = true
require-init-params = true
```

### What's Next

- Semantic verification: is what the docstring *says* about parameters accurate?
- Expanding multi-style support across all rule categories

**Full changelog:** https://github.com/Alberto-Codes/docvet/releases/tag/v1.14.0
