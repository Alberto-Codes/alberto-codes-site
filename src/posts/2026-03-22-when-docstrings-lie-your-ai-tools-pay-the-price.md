---
title: When docstrings lie, your AI tools pay the price
date: 2026-03-22
type: explanation
summary: Wrong documentation hurts AI tools more than missing documentation. docvet 1.14 introduces bidirectional verification — checking both what your docstrings fail to mention and what they wrongly claim.
tags:
  - docstrings
  - code quality
  - python
  - developer tools
  - open source
---

## The problem isn't missing docstrings

Most docstring linters answer one question: does this function have a docstring? That's useful, but it's the wrong question for 2026.

A [2024 study by Macke & Doyle](https://arxiv.org/abs/2404.03114) found that **incorrect documentation degrades LLM task success by 22.6 percentage points** — while missing documentation has no statistically significant effect. Read that again. Your AI coding assistant performs *worse* when your docstrings are wrong than when they don't exist at all.

The reason is straightforward. When a docstring says a function accepts `timeout` but the parameter was renamed to `max_wait` three commits ago, every tool that reads that docstring — Copilot, Claude, your IDE's autocomplete — generates code that passes an argument the function doesn't accept. Missing docs let the model fall back on reading the code. Wrong docs actively mislead it.

docvet 1.14 is built around this insight. Instead of just checking whether docstrings *exist*, it checks whether they *match the code*.

## What bidirectional verification means

![Bidirectional verification: forward checks catch missing documentation, reverse checks catch documented behavior that doesn't exist in code](/bidirectional-verification.svg)

Before 1.14, docvet's enrichment checks worked in one direction: they looked at the code and asked "did the docstring mention this?" If your function raised `ValueError` but the docstring had no `Raises:` section, docvet flagged it. Useful — but only half the picture.

The other half is the reverse question: does the docstring *claim* something the code doesn't actually do?

A docstring that says a function raises `FileNotFoundError` when the function never raises anything isn't just stale — it's a trap. Callers write `try/except FileNotFoundError` blocks that never trigger, or worse, they restructure their error handling around phantom exceptions. AI tools generate defensive code for errors that can't happen.

v1.14 adds three reverse enrichment rules:

- **extra-raises-in-docstring** — documents exceptions the function doesn't raise
- **extra-yields-in-docstring** — documents yields in a non-generator function
- **extra-returns-in-docstring** — documents return values the function never returns

Combined with the existing forward checks, docvet now performs full bidirectional verification: every claim in the docstring has a corresponding behavior in the code, and every behavior in the code has a corresponding claim in the docstring. With this release, docvet reaches 31 rules across six quality layers — and truthfulness is now the central theme.

## Parameter agreement: where drift actually lives

![Parameter drift lifecycle: a refactor renames a parameter, call sites are updated, but the docstring is forgotten — AI reads the stale docstring and generates wrong code. docvet intercepts at the forgotten step.](/param-drift-lifecycle.svg)

The most impactful new feature in 1.14 is parameter agreement checking. Two rules — `missing-param-in-docstring` and `extra-param-in-docstring` — compare the `Args:` section against the function signature, parameter by parameter.

This catches the single most common form of documentation drift: renamed, added, or removed parameters where the docstring wasn't updated. It happens constantly in active codebases. You rename `retries` to `max_retries` across a refactor, update every call site, and forget the one place that still says `retries` — the docstring.

The checks handle real-world Python signatures: positional-only parameters (PEP 570), keyword-only parameters, `self`/`cls` exclusion, and optional `*args`/`**kwargs` filtering. Both Google and Sphinx docstring styles are supported.

Here's what a finding looks like:

```
src/client.py:47: missing-param-in-docstring Function 'connect' has parameters not documented in Args: max_retries [required]
```

That's a one-line signal that would otherwise become a user-filed bug report, or worse, silently wrong AI-generated code.

## Catching docstrings that say nothing

Not all low-quality docstrings are wrong — some are just empty calories. The new `trivial-docstring` rule detects summary lines that restate the symbol name without adding information:

```python
def get_user():
    """Get user."""
```

This docstring technically exists. It passes every presence check. But it tells you nothing you couldn't read from the function name. docvet decomposes both the symbol name and the summary into word sets (handling CamelCase and snake_case), filters stop words, and flags cases where the summary is a subset of the name.

The rule skips `@property` and `@cached_property` — those frequently have legitimate one-line summaries that mirror the attribute name.

## Deprecation and constructor documentation

Two more rules round out the release:

**missing-deprecation** detects functions that use `warnings.warn(DeprecationWarning)` or the `@deprecated` decorator (PEP 702) without mentioning deprecation anywhere in their docstring. The match is intentionally loose — the word "deprecated" anywhere in the docstring satisfies it, because there's no single standard format for deprecation notices.

**undocumented-init-params** catches classes whose `__init__` accepts parameters but neither the class docstring nor the `__init__` docstring has an `Args:` section. This one defaults to off — it's opt-in for teams that want it.

## Design tradeoffs

A few deliberate choices worth calling out:

**Reverse checks use `recommended` severity, not `required`.** Forward checks ("you raise but don't document it") have low false-positive rates because the code is the source of truth. Reverse checks ("you document but don't raise it") have higher false-positive risk — a function might delegate to a helper that raises, or a parent class might document exceptions from subclass overrides. We chose `recommended` to surface these without blocking CI pipelines.

**Two rules default to off.** `missing-return-type` and `undocumented-init-params` are opt-in. Not every team wants to enforce return types in docstrings when they already have type annotations, and not every class needs `__init__` parameter docs in the class body. Progressive adoption matters.

**Parameter agreement checks support both directions simultaneously.** Rather than shipping "check if params are documented" and "check if documented params exist" as a single rule, they're separate rules gated by the same `require-param-agreement` config key. This means you can see exactly which direction the drift went — missing documentation vs. stale documentation — in your CI output.

## Who this is for

If you maintain a Python library that other developers (or AI tools) consume, v1.14 catches the class of documentation bugs that cause the most downstream damage. Parameter mismatches, phantom exceptions, and trivial summaries are the documentation equivalent of type errors — they compile fine but break at runtime.

If you're using docvet in CI already, upgrade and enable the new checks:

```bash
pip install docvet
# or
uv add docvet --dev
```

The param agreement checks are on by default. Reverse enrichment checks are on by default. `missing-return-type` and `undocumented-init-params` are opt-in — enable them in `pyproject.toml` when you're ready:

```toml
[tool.docvet.enrichment]
require-return-type = true
require-init-params = true
```

## What's next

v1.14 brings docvet to 31 rules across six quality layers. The next focus area is expanding what "truthfulness" means — moving beyond structural checks into semantic verification. The question isn't just "did you document the parameters?" but "is what you said about them accurate?"

Every function with a stale `Args:` section is a wrong answer waiting to happen — in your IDE, in your code review, in the pull request your AI assistant is about to generate. docvet 1.14 catches them before they ship.
