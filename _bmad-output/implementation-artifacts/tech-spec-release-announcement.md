---
title: 'Release Announcement Workflow'
slug: 'release-announcement'
created: '2026-03-11'
status: 'completed'
stepsCompleted: [1, 2, 3, 4]
tech_stack: ['BMAD workflow yaml', 'markdown', 'gh CLI', 'graphql (gh api)']
files_to_modify:
  - '_bmad/_config/workflow-manifest.csv'
  - '_bmad/_config/bmad-help.csv'
files_to_create:
  - '_bmad/bmm/workflows/release-announcement/workflow.yaml'
  - '_bmad/bmm/workflows/release-announcement/instructions.md'
  - '_bmad/bmm/workflows/release-announcement/release-announcement-style-guide.md'
code_patterns:
  - 'workflow.yaml: name/description/config_source/installed_path/instructions/default_output_file'
  - 'single-curly {variable} syntax — no double-curly'
  - 'default_output_file supported in workflow.yaml (confirmed: sprint-planning, qa-generate-e2e-tests)'
  - 'blog posts: title/date/type/summary/tags frontmatter'
test_patterns: []
---

# Tech-Spec: Release Announcement Workflow

**Created:** 2026-03-11

## Overview

### Problem Statement

There is no consistent, repeatable way to produce multi-platform release announcements for Alberto-Codes projects. Each release currently requires manually drafting a blog post, dev.to article, LinkedIn post, X thread, and GitHub Discussion from scratch — with no shared voice guide, no discovery automation, and no canonical template to work from.

### Solution

A BMAD workflow (`_bmad/bmm/workflows/release-announcement/`) that accepts a `gh_repo` URL as its sole input, auto-discovers the latest release via `gh` CLI (no local clone required), and produces a blog post written directly to `src/posts/` plus platform-specific announcement drafts in `_bmad-output/implementation-artifacts/`. The blog is the canonical source; all other platforms link back to it. One workflow serves all Alberto-Codes sister projects.

### Scope

**In Scope:**
- `workflow.yaml` — workflow definition, config, and variable declarations
- `instructions.md` — linear 8-step orchestration script (Steps 0–8)
- `release-announcement-style-guide.md` — self-contained voice/format/template/anti-pattern rules per platform (absorbs announcement-template.md)
- Registration in `_bmad/_config/workflow-manifest.csv` (new row)
- Registration in `_bmad/_config/bmad-help.csv` (new row, phase: anytime)
- Blog post output → `src/posts/YYYY-MM-DD-{slug}.md`
- All other platform drafts → `_bmad-output/implementation-artifacts/release-announcement-{version}-{date}.md` (single multi-section file)

**Out of Scope:**
- Publishing/posting to any platform via API
- New BMAD agents (uses existing SM + party mode with existing agent roster)
- CI/CD integration or automated triggering on release events
- Cross-repo installation of the workflow

## Context for Development

### Codebase Patterns

**workflow.yaml structure** (from `qa-generate-e2e-tests` and `sprint-planning` — best pattern matches):
```yaml
name: release-announcement
description: '...'
config_source: "{project-root}/_bmad/bmm/config.yaml"
# variables from config...
date: system-generated
installed_path: "{project-root}/_bmad/bmm/workflows/release-announcement"
instructions: "{installed_path}/instructions.md"
style_guide: "{installed_path}/release-announcement-style-guide.md"
default_output_file: "{implementation_artifacts}/release-announcement-{release_version}-{date}.md"
```
- Variable syntax is **single-curly only** — `{variable}`. The design brief's `{{release_version}}` double-curly is non-standard and must be corrected to `{release_version}`.
- `default_output_file` IS supported (confirmed in `sprint-planning` and `qa-generate-e2e-tests`). Define as a resolved variable path.
- Companion `instructions.md` is the BMAD pattern for rich step logic (all anytime workflows use it).

**Blog post frontmatter schema** (confirmed from `src/posts/`):
```yaml
---
title: string
date: YYYY-MM-DD
type: explanation|how-to|tutorial|reference
summary: one-line hook
tags:
  - tag1
  - tag2
---
```
All five fields are required. `type` maps directly to Diataxis types in the design brief.

**LinkedIn voice** (from `linkedin_post.txt`):
- Opens with a concrete insight/counter-intuitive statement — no warm-up
- Problem-first: establishes the pain before the solution
- Short paragraphs (2–3 sentences max)
- URL-only CTA (no "click here", just the raw link)
- 4 hashtags, no more
- No food metaphor present in this example — used selectively, not formulaically
- Tone: direct, technical, respects reader's intelligence

**gh CLI real output shape** (confirmed against `Alberto-Codes/docvet`):
```json
// gh release view --repo {gh_repo} --json tagName,body,publishedAt
{"body": "## [1.13.0](...compare/v1.12.1...v1.13.0) (2026-03-08)\n\n### Features\n...\n### Bug Fixes\n...", "publishedAt": "2026-03-08T13:34:47Z", "tagName": "v1.13.0"}

// gh release list --repo {gh_repo} --limit 2 --json tagName,publishedAt
[{"publishedAt": "2026-03-08T...", "tagName": "v1.13.0"}, {"publishedAt": "2026-03-07T...", "tagName": "v1.12.1"}]
```
- `body` is conventional commits markdown with `### Features` / `### Bug Fixes` sections
- Previous tag derived from index [1] of `release list --limit 2`

### Files to Reference

| File | Purpose |
| ---- | ------- |
| `_bmad-output/planning-artifacts/release-announcement-workflow-design.md` | Full design brief — voice guide, platform templates, gh CLI commands, party mode agent table |
| `_bmad/_config/workflow-manifest.csv` | Append new row for release-announcement |
| `_bmad/_config/bmad-help.csv` | Append new row (anytime phase, SM agent, Bob) |
| `_bmad/bmm/workflows/qa-generate-e2e-tests/workflow.yaml` | Primary reference pattern for top-level anytime workflow.yaml structure |
| `_bmad/bmm/workflows/4-implementation/sprint-planning/workflow.yaml` | Reference for `default_output_file` variable pattern |
| `src/posts/2026-03-06-encrypt-adk-sessions-in-five-minutes.md` | Blog post frontmatter schema reference |
| `linkedin_post.txt` | LinkedIn voice reference — extract style characteristics for style guide |

### Technical Decisions

- **Location:** Top-level `_bmad/bmm/workflows/release-announcement/` — `anytime` phase, matches existing top-level pattern. Confirmed.
- **Primary agent:** SM (Bob) orchestrates; party mode brings in platform-specific agents per design brief table.
- **gh CLI only:** All release discovery via `gh` CLI — no local clone of target repo needed.
- **Variable syntax:** Single-curly `{variable}` throughout. Design brief's `{{release_version}}` corrected to `{release_version}`.
- **`default_output_file`:** Supported in workflow.yaml. Define `release_version` as a runtime-resolved var from `gh release view`.
- **instructions.md architecture:** **Linear script** (not step-file). Step-file architecture is for disciplined code spec workflows; this is a content generation workflow where the SM reads top-to-bottom with optional party mode branches per platform.
- **Template consolidation:** **Merge `announcement-template.md` INTO style guide.** Design brief's style guide already contains fuzzy templates per platform. Separate file creates sync risk. Final file count: 3 files (workflow.yaml, instructions.md, release-announcement-style-guide.md).
- **Output structure:** **Single multi-section draft file** (`release-announcement-{version}-{date}.md`) with one H2 section per platform. Blog post is separate — written directly to `src/posts/`.
- **Multi-post Diataxis flow:** Step 3 selects Diataxis types upfront, then writes all selected blog posts in sequence before moving to Step 4 (dev.to).
- **Blog slug → canonical URL:** Blog step locks the slug; canonical URL `https://alberto.codes/blog/{slug}` passed to dev.to step for `canonical_url` frontmatter.
- **bmad-help.csv `agent-command` string:** `bmad:story preparation:agent:sm` — verified exact match against existing SM row.
- **`gh_repo` runtime variable:** Declared in workflow.yaml as `gh_repo: ""  # User-provided`. instructions.md Step 0 checks if empty and prompts user before any discovery runs.
- **`release_version` sequencing:** workflow.yaml declares as placeholder `release_version: ""`; instructions.md resolves it at runtime in Step 1 via `gh release view`, then uses it to name the output draft file.
- **Party mode invocation mechanics:** Per-platform steps (Steps 3–7) invoke party mode as a subprocess with the agents specified in the design brief's platform table. The SM does not free-form select agents — the style guide specifies which agents per platform.
- **instructions.md opening sequence:**
  ```
  Step 0:   Load style guide ({style_guide})
  Step 0.5: Verify gh_repo — if empty, ask user to provide "Alberto-Codes/repo-name"
  Step 1:   Run gh CLI discovery commands
  Step 1.5: Confirm with user: "Repo: {gh_repo} | Release: {tagName} — proceed?"
  ```
- **Style guide is self-contained:** The style guide must contain all voice rules, platform templates, and anti-patterns inline — a fresh agent should not need to read the design brief. `linkedin_post.txt` voice example must be embedded as a confirmed real example.

### Edge Case Handling (captured for instructions.md)

| Scenario | Handling |
|---|---|
| Repo has zero releases | `gh release view` returns error → instructions.md must check and exit gracefully with message |
| First-ever release (no previous tag) | `gh release list --limit 2` returns 1 entry → skip diff step, note "initial release" |
| GitHub Discussions disabled/empty | `gh api graphql` returns null/error → fallback to design brief voice reference for that repo's style |
| Empty release body | `body` field is blank → rely on commit log from `compare` endpoint instead |

## Implementation Plan

### Tasks

Tasks are ordered dependency-first: infrastructure (workflow.yaml) → content files → manifest registration.

- [x] **Task 1: Create workflow directory**
  - File: `_bmad/bmm/workflows/release-announcement/` (directory)
  - Action: Create the directory — no files yet
  - Notes: Top-level under `bmm/workflows/`, not inside a phase subfolder

- [x] **Task 2: Create `workflow.yaml`**
  - File: `_bmad/bmm/workflows/release-announcement/workflow.yaml`
  - Action: Create with the following content exactly:
    ```yaml
    name: release-announcement
    description: 'Draft release announcements across all platforms for any Alberto-Codes project. Use when the user says "create release announcement"'

    # Critical variables from config
    config_source: "{project-root}/_bmad/bmm/config.yaml"
    user_name: "{config_source}:user_name"
    communication_language: "{config_source}:communication_language"
    document_output_language: "{config_source}:document_output_language"
    user_skill_level: "{config_source}:user_skill_level"
    date: system-generated
    implementation_artifacts: "{config_source}:implementation_artifacts"
    planning_artifacts: "{config_source}:planning_artifacts"
    # Workflow components
    installed_path: "{project-root}/_bmad/bmm/workflows/release-announcement"
    instructions: "{installed_path}/instructions.md"
    style_guide: "{installed_path}/release-announcement-style-guide.md"
    # No validation/checklist.md — content generation workflow, not code implementation

    # User-provided runtime input
    gh_repo: ""  # User-provided: e.g., "Alberto-Codes/docvet"

    # Runtime-resolved during Step 1 of instructions.md
    # SM sets output_file = "{implementation_artifacts}/release-announcement-{tagName}-{date}.md"
    # and uses that variable directly for all write operations in Steps 1.9–7
    ```
  - Notes: Single-curly syntax throughout. `gh_repo` is an empty string — instructions.md prompts user if empty. `default_output_file` is intentionally absent — the SM derives and manages the output path at runtime. No `validation` field — content generation workflow, not code implementation.

- [x] **Task 3: Create `release-announcement-style-guide.md`**
  - File: `_bmad/bmm/workflows/release-announcement/release-announcement-style-guide.md`
  - Action: Create a self-contained style guide with these exact H2 section headings in order. A fresh agent running the workflow must find everything here — no design brief reference needed.
    - `## Voice Principles` — the 5 principles from the design brief (lead with the problem, show don't list, honest about tradeoffs, one narrative, end with forward motion)
    - `## LinkedIn` — audience, length (~1300 chars), voice rules, confirmed real example from `linkedin_post.txt` (direct hook, problem-first, short paragraphs, URL CTA, 4 hashtags max, no food metaphor required), fuzzy template, anti-patterns
    - `## X / Twitter` — audience, thread of 3-5 tweets, bold/confident voice, fuzzy template, anti-patterns
    - `## dev.to` — audience, 800-1200 words, `canonical_url` requirement, frontmatter template (title/published/tags/description/canonical_url), section structure, anti-patterns
    - `## GitHub Discussion` — audience, 150-400 words, community-first voice, match target repo's prior discussion voice, fuzzy template, anti-patterns
    - `## alberto.codes Blog` — audience, 1000-1500 words, Diataxis framework, frontmatter schema (title/date/type/summary/tags), Diataxis type selection table, section structure per type, anti-patterns
    - `## Cross-Platform Coordination` — content flow (Blog → dev.to → LinkedIn → X → GitHub Discussion), canonical URL construction (`https://alberto.codes/blog/{slug}`), blog slug derivation rule
    - `## Party Mode Agent Selection` — table: Blog (varies by Diataxis), dev.to (Dev + Tech Writer), LinkedIn (PM + Architect), X (Quick Flow + Storyteller), GitHub Discussion (SM + PM)
    - `## Sister Project Voice Reference` — docvet (discovery & accessibility), adk-secure-sessions (architecture & trust), gepa-adk (concise & technical) patterns from design brief
  - Notes: Templates are fuzzy guides, not rigid scripts. The `linkedin_post.txt` real example is the authoritative LinkedIn voice reference. Derive ALL content from `_bmad-output/planning-artifacts/release-announcement-workflow-design.md` sections: Platform Style Guide, Cross-Platform Coordination, Party Mode Agent Selection Per Platform, Sister Project Discussion Voice Reference.

- [x] **Task 4: Create `instructions.md`**
  - File: `_bmad/bmm/workflows/release-announcement/instructions.md`
  - Action: Create a linear script that the SM agent follows top-to-bottom. Structure:

    ```
    ## Step 0: Load Style Guide
    Read {style_guide} in full before proceeding.

    ## Step 0.5: Verify Input
    If gh_repo is empty, ask: "Which repo are we announcing?
    Provide as 'Owner/repo-name' (e.g., Alberto-Codes/docvet)"
    Set gh_repo to user's response.

    ## Step 1: Release Discovery
    Run ALL of the following gh CLI commands against {gh_repo}:

    1a. Latest release:
        gh release view --repo {gh_repo} --json tagName,body,publishedAt
        → If the command errors or returns no data: display "No releases found for
          {gh_repo}. Tag a release first." then halt — do not proceed further.
          Return control to the user.
        → Store: tagName as release_version, body as release_body, publishedAt as release_date
        → Derive output_file = "{implementation_artifacts}/release-announcement-{release_version}-{date}.md"

    1b. Previous release (diff baseline):
        gh release list --repo {gh_repo} --limit 2 --json tagName
        → If only 1 result: note "initial release — no diff baseline available"
        → If 2 results: store index[1].tagName as prev_version

    1c. Commit log between tags (skip if initial release):
        Use {release_version} and {prev_version} as-is (raw tagName values) in the
        compare URL — do not strip or modify the tag strings.
        gh api repos/{gh_repo}/compare/{prev_version}...{release_version}
          --jq '.commits[].commit.message'

    1d. Recent GitHub Discussions (voice matching):
        Derive owner and repo from {gh_repo} by splitting on "/":
          owner = first segment, repo = second segment
        Substitute actual owner and repo values into the command string before running:
        gh api graphql -f query='{ repository(owner:"OWNER", name:"REPO") {
          discussions(first:5) { nodes { title body category { name } createdAt } } } }'
        → If error or empty: use sister project voice reference from style guide for this repo's category

    1e. Source tree context:
        gh api repos/{gh_repo}/git/trees/main --jq '.tree[].path'
        (limit to first 50 paths)

    ## Step 1.9: Initialize Output File
    Create {output_file} with the following header:
      # Release Announcement Drafts: {gh_repo} {release_version}
      Generated: {date}
    This file will accumulate one H2 section per platform in Steps 4–7.

    ## Step 1.5: Confirm with User
    Present summary:
      "Repo: {gh_repo}
       Release: {release_version} ({release_date})
       Previous: {prev_version or 'initial release'}
       Features: [count from release_body]
       Fixes: [count from release_body]
       Proceed?"
    HALT and wait for confirmation.

    ## Step 2: Release Context Summary
    Synthesize all discovery data into a structured context block and write it
    to {output_file} under a ## Release Context section:
    - What shipped (features/fixes summarized in plain language)
    - Key technical themes
    - Breaking changes (if any)
    - Install/upgrade command

    ## Step 3: Blog Post (alberto.codes → src/posts/)
    Ask: "Which Diataxis type(s) fit this release?"
    Present options with rationale based on what shipped.
    (See style guide: Blog section, Diataxis type selection table)
    For each selected type:
      - Draft post with full frontmatter (title/date/type/summary/tags)
      - Invoke party mode: agents per style guide Platform Agent table for Blog
      - Before writing: check if src/posts/{date}-{slug}.md already exists.
        If it does, ask user: "File already exists — overwrite? (y/n)"
      - Write final post to: src/posts/{date}-{slug}.md
      - Lock canonical URL: https://alberto.codes/blog/{date}-{slug}
    All blog posts written before proceeding to Step 4.

    ## Step 4: dev.to Article
    Draft dev.to article (800-1200 words) per style guide.
    Include canonical_url pointing to blog post from Step 3.
    Invoke party mode: Dev + Tech Writer.
    Write draft to output file under ## dev.to section.

    ## Step 5: LinkedIn Post
    Draft LinkedIn post (~1300 chars) per style guide.
    Invoke party mode: PM + Architect.
    Write draft to output file under ## LinkedIn section.

    ## Step 6: X/Twitter Thread
    Draft thread (3-5 tweets) per style guide.
    Invoke party mode: Quick Flow Solo Dev + Storyteller.
    Write draft to output file under ## X/Twitter section.

    ## Step 7: GitHub Discussion
    Draft discussion post (150-400 words) per style guide.
    Match voice of existing discussions discovered in Step 1d.
    Invoke party mode: SM + PM.
    Write draft to output file under ## GitHub Discussion section.

    ## Step 8: Review & Finalize
    Present complete output summary:
      "Blog post(s): src/posts/[files written]
       All platform drafts: {output_file}
       Review and edit before publishing."
    Ask if any platform needs revision. If yes, revise and re-present.
    ```
  - Notes: "Invoke party mode" means the SM channels the specified agents inline within its response, maintaining their personas per the agent manifest — it is NOT a literal `/bmad-party-mode` invocation. The SM orchestrates; agents contribute per their platform expertise. Output file accumulates H2 sections from Steps 4–7 (blog goes directly to `src/posts/`). The SM derives the actual output filename at Step 1 runtime: `{implementation_artifacts}/release-announcement-{tagName}-{date}.md`.

- [x] **Task 5: Append row to `workflow-manifest.csv`**
  - File: `_bmad/_config/workflow-manifest.csv`
  - Action: Append this exact row at end of file:
    ```
    "release-announcement","Draft release announcements across all platforms (blog dev.to LinkedIn X GitHub Discussion) for any Alberto-Codes project. Input is a gh_repo URL.","bmm","_bmad/bmm/workflows/release-announcement/workflow.yaml"
    ```
  - Notes: Column order is `name,description,module,path` — verified against existing rows. Ensure file ends with a newline before appending.

- [x] **Task 6: Append row to `bmad-help.csv`**
  - File: `_bmad/_config/bmad-help.csv`
  - Action: Append this exact row at end of file:
    ```
    bmm,anytime,Release Announcement,RA,,_bmad/bmm/workflows/release-announcement/workflow.yaml,bmad-bmm-release-announcement,false,sm,bmad:story preparation:agent:sm,Bob,🏃 Scrum Master,Create Mode,Draft release announcements across all platforms (blog dev.to LinkedIn X GitHub Discussion) for any Alberto-Codes project. Input is a gh_repo URL.,implementation_artifacts,release announcement drafts
    ```
  - Notes: `agent-command` string `bmad:story preparation:agent:sm` verified exact match against existing SM row. `sequence` field is empty (anytime phase workflows don't use sequence). Ensure file ends with a newline before appending.

### Acceptance Criteria

- [x] **AC 1:** Given the implementation is complete, when `workflow-manifest.csv` is opened, then a row exists with `name=release-announcement`, `module=bmm`, and `path=_bmad/bmm/workflows/release-announcement/workflow.yaml`.

- [x] **AC 2:** Given the implementation is complete, when `bmad-help.csv` is opened, then a row exists with `phase=anytime`, `command=bmad-bmm-release-announcement`, `agent-name=sm`, `agent-display-name=Bob`, and `output-location=implementation_artifacts`.

- [x] **AC 3:** Given `workflow.yaml` is opened, when reviewed, then `gh_repo: ""` is present with a user-provided comment, `release_version: ""` is declared, and all variable references use single-curly syntax with no double-curly instances.

- [x] **AC 4:** Given `gh_repo` is not set, when the SM agent runs `instructions.md` Step 0.5, then the agent prompts the user to provide a repo in `Owner/repo-name` format before executing any `gh` CLI commands.

- [x] **AC 5:** Given `gh_repo` points to a repo with no releases, when Step 1a discovery runs, then the workflow displays "No releases found for {gh_repo}. Tag a release first.", halts, and returns control to the user without proceeding to any further steps.

- [x] **AC 6:** Given `gh_repo` points to a repo with exactly one release (initial release), when Step 1b runs, then `gh release list --limit 2` returns 1 result and the workflow notes "initial release — no diff baseline" and skips the compare step.

- [x] **AC 7:** Given discovery completes successfully, when Step 1.5 confirmation is displayed, then it shows repo name, release version, publish date, previous version (or "initial release"), and feature/fix counts before halting for user confirmation.

- [x] **AC 8:** Given the user confirms at Step 1.5, when Step 3 (blog) runs, then the user is asked which Diataxis type(s) fit and all selected types are written to `src/posts/YYYY-MM-DD-{slug}.md` with all five required frontmatter fields (`title`, `date`, `type`, `summary`, `tags`).

- [x] **AC 9:** Given a blog post is written in Step 3, when the dev.to draft is generated in Step 4, then it contains `canonical_url: https://alberto.codes/blog/{slug}` matching the slug from Step 3.

- [x] **AC 10:** Given the workflow completes Steps 4–7, when the output draft file is opened, then it contains four H2 sections (`## dev.to`, `## LinkedIn`, `## X/Twitter`, `## GitHub Discussion`) with draft content in each.

- [x] **AC 11:** Given `release-announcement-style-guide.md` is opened by a fresh agent, when reviewed, then it contains all nine H2 sections in order (`## Voice Principles`, `## LinkedIn`, `## X / Twitter`, `## dev.to`, `## GitHub Discussion`, `## alberto.codes Blog`, `## Cross-Platform Coordination`, `## Party Mode Agent Selection`, `## Sister Project Voice Reference`), includes the confirmed LinkedIn real example, and contains no reference requiring the reader to consult the design brief.

- [x] **AC 12:** Given `instructions.md` is opened, when any variable reference is found, then it uses single-curly `{variable}` syntax with no double-curly `{{variable}}` instances anywhere in the file.

## Additional Context

### Dependencies

- `gh` CLI authenticated and available in the environment (`gh auth status` should pass)
- Existing BMAD agent roster available — no new agents needed
- `src/posts/` directory exists (confirmed)
- `_bmad-output/implementation-artifacts/` directory exists (created in this session)

### Testing Strategy

Manual verification steps (no automated tests — workflow files are BMAD configuration/markdown):

1. **Manifest check:** Open both CSV files and confirm new rows are present and correctly formatted
2. **workflow.yaml lint:** Verify single-curly syntax throughout, no double-curly instances
3. **Dry-run discovery:** Run `gh release view --repo Alberto-Codes/docvet --json tagName,body,publishedAt` manually to confirm CLI access
4. **Style guide completeness check:** Open style guide, verify all 8 required sections are present
5. **instructions.md flow check:** Read instructions.md top-to-bottom, verify Step 0 loads style guide and Step 0.5 handles empty `gh_repo` before Step 1
6. **Full smoke run:** Invoke `/bmad-bmm-release-announcement` against `Alberto-Codes/docvet`, confirm it prompts for repo (or uses provided), runs discovery, presents confirmation, and produces output

### Notes

- Design brief source: `_bmad-output/planning-artifacts/release-announcement-workflow-design.md` (party mode session 2026-03-08) — primary reference for style guide content
- `linkedin_post.txt` in repo root is the authoritative LinkedIn voice example — embed it (or its extracted characteristics) in the style guide's LinkedIn section
- The design brief's workflow.yaml sketch used double-curly `{{release_version}}` — this is non-standard; all variables in the implementation use single-curly
- The `announcement-template.md` file from the design brief's 4-file structure is eliminated — its content is absorbed into the style guide

### Step 2 Investigation Checklist (from party mode reviews)

**Structural:**
- [x] **instructions.md architecture** — **Linear script.** Step-file overkill for content workflow.
- [x] **Variable syntax** — **Single-curly only.** Design brief double-curly corrected.
- [x] **`default_output_file` field** — **Supported.** Confirmed in sprint-planning + qa-generate-e2e-tests.
- [x] **Template consolidation decision** — **Merged.** `announcement-template.md` absorbed into style guide. 3 files total.
- [x] **Output structure** — **Single multi-section file** per release + separate blog post(s) to `src/posts/`.
- [x] **Multi-post Diataxis flow** — All selected types written in sequence within Step 3 before proceeding.

**Content/Voice:**
- [x] **`src/posts/` frontmatter schema** — `title`, `date`, `type`, `summary`, `tags[]` — all required.
- [x] **`linkedin_post.txt`** — Direct hook, problem-first, short paragraphs, URL CTA, 4 hashtags max.
- [x] **Real release body audit** — docvet v1.13.0 confirmed: conventional commits markdown, `### Features` / `### Bug Fixes`.

**Edge Cases:**
- [x] **Zero releases** — `gh release view` errors → instructions.md exits with message.
- [x] **First-ever release** — `gh release list --limit 2` returns 1 → skip diff, note "initial release".
- [x] **GitHub Discussions disabled/empty** — fallback to design brief voice reference for that repo.
- [x] **Empty release body** — fall back to commit log from `compare` endpoint.

**Manifest Registration:**
- [x] **`workflow-manifest.csv` new row** — columns: `name,description,module,path`
- [x] **`bmad-help.csv` SM `agent-command` string** — `bmad:story preparation:agent:sm` ✓

## Review Notes
- Adversarial review completed (party mode panel: Wendy, Bob, Barry)
- Findings: 12 total, 7 fixed, 5 skipped
- Resolution approach: auto-fix (panel consensus)
- F1 fixed: GitHub Discussion template backtick escaping (switched to ~~~ outer fence)
- F3 fixed: Added `# format: YYYY-MM-DD` comment to workflow.yaml date variable
- F4 fixed: Renumbered Step 1.9 → Step 1.6 and Step 1.5 → Step 1.7 for logical sequence
- F5 fixed: Added slug derivation rule inline to Step 3 in instructions.md (upgraded to High)
- F6 fixed: Removed unused `planning_artifacts` from workflow.yaml
- F8 fixed: Added explicit "do not consult external docs" statement to style guide opening
- F12 fixed: Added `gh auth status` prerequisite check to Step 0 in instructions.md
- Skipped (noise/out-of-scope): F2, F7, F9, F10, F11
