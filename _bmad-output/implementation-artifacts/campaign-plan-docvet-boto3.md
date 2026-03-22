# Campaign Plan: docvet Release + boto3 Deep-Dive

**Created:** 2026-03-22
**Status:** Awaiting docvet release

---

## Overview

Two-piece content campaign tied to the next docvet release. The release-announcement workflow handles standard multi-platform release content. A separate boto3 deep-dive provides the flagship thought-leadership piece proving docvet at planetary scale.

## Context

- **boto3 stats:** 1.75B monthly downloads, 43M daily, latest v1.42.73, 98.88% Python 3
- **docvet new rules (unreleased):** missing-return-type, missing-param-in-docstring, extra-param-in-docstring, undocumented-init-params, trivial-docstring, missing-deprecation, extra-raises/yields/returns (reverse checks)
- **Key stat for narrative:** "Incorrect documentation degrades LLM task success by 22.6 percentage points — while missing documentation has no statistically significant effect."

## Execution Phases

### Phase 1 — Ship docvet release

- Tag release, confirm on PyPI
- Verify `pip install docvet` works with new rules

### Phase 2 — Run release-announcement workflow

- Input: `Alberto-Codes/docvet`
- Output: Coordinated content for 6 platforms (blog, dev.to, LinkedIn, X, GitHub Discussion, Medium)
- Agent pairings per the workflow's instructions.md
- Review, adjust, publish

### Phase 3 — boto3 deep-dive (premium content)

- Clone boto3, pin to a specific commit SHA for reproducibility
- Run docvet with `--summary` flag, capture raw output
- Key things to measure:
  - Presence layer: docstring coverage percentage
  - Enrichment layer: param mismatches, trivial docstrings, missing Raises sections
  - Freshness layer: stale signatures from daily release cadence
- Generate ARCHITECTURE.md content with Mermaid diagrams:
  - Module dependency graph (boto3 → botocore → jmespath)
  - Client lifecycle flow (Session → ClientCreator → ServiceModel → Endpoint → HTTP)
  - docvet rule coverage heatmap overlaid on modules
- Write blog post — Diataxis type: **explanation**, ~1500 words
- Pre-render Mermaid to SVG in `src/assets/`
- Cross-post to Medium (explanation type qualifies per workflow gate)

### Phase 4 — Amplify

- LinkedIn: credibility transfer angle (if docvet handles boto3, it handles your repo)
- X thread: scorecard screenshot + trivial docstring examples
- dev.to cross-post with canonical URL
- Capture raw docvet output as downloadable gist for data credibility

## Blog Title Candidates (boto3 piece)

- "Is the Most Downloaded Python Package Telling the Truth? We Ran docvet on boto3 to Find Out."
- "We Ran docvet on the Most Downloaded Package in Python. Here's What We Found."

## Narrative Anchors

- **Release announcement narrative:** "Your docstrings are lying to your AI tools, and now there's a way to catch every lie — parameter by parameter."
- **boto3 deep-dive narrative:** "We pointed docvet at the most downloaded Python package. Here's what we found."
- **The hook:** Wrong docs are worse than no docs, and nobody was checking until now. boto3 is the training signal for every AI coding assistant — if its docstrings are stale, every Copilot/Claude suggestion about AWS is potentially affected.

## Risk Mitigation

- **Reproducibility:** Pin boto3 commit SHA in the blog post so readers can verify
- **Daily releases:** Numbers may shift — frame findings at a point-in-time, not absolute truth
- **Multi-style support:** Note that the release also adds NumPy and Sphinx/RST style support (broadens reach beyond Google-style shops)

## UX Consideration

- Blog now has 9 posts, will have 10-11 after campaign. Consider tag-based filtering or series grouping on `/blog` as follow-up.

## Party Mode Agents for Content Generation

| Content | Agent Pair |
|---|---|
| Release blog (explanation) | Winston (Architect) + Paige (Tech Writer) |
| Release blog (how-to/tutorial) | Amelia (Dev) + Paige (Tech Writer) |
| dev.to | Amelia (Dev) + Paige (Tech Writer) |
| LinkedIn | John (PM) + Winston (Architect) |
| X/Twitter thread | Barry (Quick Flow) + Sophia (Storyteller) |
| GitHub Discussion | Bob (SM) + John (PM) |
| Medium | John (PM) + Sophia (Storyteller) |
| boto3 deep-dive blog | Winston (Architect) + Paige (Tech Writer) + Mary (Analyst) |
