# Release Announcement Instructions

Linear script for the SM agent. Read top-to-bottom. Do not skip steps.

> **"Invoke party mode"** means the SM channels the specified agents inline within its response, maintaining their personas per the agent manifest. It is NOT a literal `/bmad-party-mode` invocation. The SM orchestrates; agents contribute per their platform expertise.

---

## Step 0: Load Style Guide

**Prerequisite:** Run `gh auth status` before proceeding. If it fails, display: "gh CLI is not authenticated. Run `gh auth login` first." and halt.

Read {style_guide} in full before proceeding to any other step. All voice rules, platform templates, and anti-patterns are defined there. Do not proceed until the style guide is loaded.

---

## Step 0.5: Verify Input

Check if {gh_repo} is set (non-empty string).

If {gh_repo} is empty, ask the user:

> "Which repo are we announcing? Provide as 'Owner/repo-name' (e.g., Alberto-Codes/docvet)"

HALT and wait for the user's response. Set {gh_repo} to the user's response before continuing.

Do not execute any `gh` CLI commands until {gh_repo} is confirmed.

---

## Step 1: Release Discovery

Run ALL of the following `gh` CLI commands against {gh_repo}. Execute them in sequence.

### Step 1a: Latest Release

```bash
gh release view --repo {gh_repo} --json tagName,body,publishedAt
```

- If the command errors or returns no data: display the following message and halt — do not proceed to any further steps:

  > "No releases found for {gh_repo}. Tag a release first."

  Return control to the user.

- If successful: store the following variables:
  - `tagName` → `release_version`
  - `body` → `release_body`
  - `publishedAt` → `release_date`
  - Derive: `output_file` = `{implementation_artifacts}/release-announcement-{release_version}-{date}.md`

### Step 1b: Previous Release (diff baseline)

```bash
gh release list --repo {gh_repo} --limit 2 --json tagName
```

- If only 1 result: note "initial release — no diff baseline available". Skip Step 1c.
- If 2 results: store `index[1].tagName` as `prev_version`.

### Step 1c: Commit Log Between Tags

Skip this step if Step 1b identified an initial release (no prev_version).

Use {release_version} and {prev_version} as-is (raw tagName values from Step 1a/1b) in the compare URL — do not strip or modify the tag strings (e.g., if tagName is "v1.13.0", use "v1.13.0" exactly).

```bash
gh api repos/{gh_repo}/compare/{prev_version}...{release_version} \
  --jq '.commits[].commit.message'
```

### Step 1d: Recent GitHub Discussions (voice matching)

Derive owner and repo from {gh_repo} by splitting on "/":
- `owner` = first segment
- `repo` = second segment

Substitute the actual owner and repo values into the command string before running:

```bash
gh api graphql -f query='{ repository(owner:"OWNER", name:"REPO") {
  discussions(first:5) { nodes { title body category { name } createdAt } } } }'
```

- If error or empty: use the Sister Project Voice Reference section from the style guide for this repo's category.

### Step 1e: Source Tree Context

```bash
gh api repos/{gh_repo}/git/trees/main --jq '.tree[].path'
```

Limit to first 50 paths.

---

## Step 1.6: Initialize Output File

Create {output_file} with the following header:

```markdown
# Release Announcement Drafts: {gh_repo} {release_version}
Generated: {date}
```

This file will accumulate one H2 section per platform in Steps 4–7. Blog posts are written separately to `src/posts/`.

---

## Step 1.7: Confirm with User

Present a summary to the user and HALT — wait for confirmation before proceeding:

```
Repo: {gh_repo}
Release: {release_version} ({release_date})
Previous: {prev_version or "initial release"}
Features: [count of ### Features items from release_body]
Fixes: [count of ### Bug Fixes items from release_body]
Proceed?
```

Do not continue to Step 2 until the user confirms.

---

## Step 2: Release Context Summary

Synthesize all discovery data from Steps 1a–1e into a structured context block. Write it to {output_file} under a `## Release Context` section:

- What shipped (features and fixes summarized in plain language, not raw changelog)
- Key technical themes
- Breaking changes (if any)
- Install/upgrade command

---

## Step 3: Blog Post (alberto.codes → src/posts/)

Ask the user which Diataxis type(s) fit this release. Present the options with brief rationale based on what shipped, referencing the Diataxis type selection table in the style guide.

For each selected type, in sequence:

1. Draft the full blog post with complete frontmatter (`title`, `date`, `type`, `summary`, `tags`)
2. Invoke party mode using the Blog agent pairing from the Party Mode Agent Selection table in the style guide (varies by Diataxis type)
3. Derive the slug: lowercase the title → replace spaces with hyphens → strip punctuation except hyphens → prepend publish date as `YYYY-MM-DD`. Example: "Why docvet Needed CLI-First Design" → `2026-03-08-why-docvet-needed-cli-first-design`.
4. Before writing: check if `src/posts/{date}-{slug}.md` already exists. If it does, ask:

   > "File already exists — overwrite? (y/n)"

   Wait for user response before writing.

5. Write the final post to: `src/posts/{date}-{slug}.md`
6. Lock the canonical URL: `https://alberto.codes/blog/{date}-{slug}`

Write all selected blog posts before proceeding to Step 4.

---

## Step 4: dev.to Article

Draft a dev.to article (800–1200 words) following the dev.to section of the style guide.

- Include `canonical_url` pointing to the blog post canonical URL locked in Step 3
- Invoke party mode: Dev + Tech Writer
- Write the draft to {output_file} under a `## dev.to` section

---

## Step 5: Medium Article

Check the blog post Diataxis type from Step 3. Only generate a Medium draft if the type is `explanation` or a code-light `how-to`. For `reference` or code-heavy posts, skip this step and note: "Skipping Medium — post type relies on syntax highlighting and tables that Medium doesn't support."

If generating:

- Draft an 800–1200 word adaptation following the Medium section of the style guide
- Adapt code blocks: keep max 1–2 short snippets (under 5 lines), replace longer blocks with plain-language descriptions
- Replace any tables with prose comparisons or bold key/value pairs
- Include the canonical blog URL at the end
- Invoke party mode: PM + Storyteller
- Write the draft to {output_file} under a `## Medium` section
- Note to user: "Publish via Medium's Import tool (paste blog URL) or copy-paste and set canonical link manually under story settings."

---

## Step 6: LinkedIn Post

Draft a LinkedIn post (~1300 characters) following the LinkedIn section of the style guide.

- Invoke party mode: PM + Architect
- Write the draft to {output_file} under a `## LinkedIn` section

---

## Step 7: X/Twitter Thread

Draft a thread of 3–5 tweets following the X/Twitter section of the style guide.

- Invoke party mode: Quick Flow Solo Dev + Storyteller
- Write the draft to {output_file} under a `## X/Twitter` section

---

## Step 8: GitHub Discussion

Draft a GitHub Discussion post (150–400 words) following the GitHub Discussion section of the style guide.

- Match the voice of existing discussions discovered in Step 1d (or use Sister Project Voice Reference if Step 1d returned no results)
- Invoke party mode: SM + PM
- Write the draft to {output_file} under a `## GitHub Discussion` section

---

## Step 9: Review & Finalize

Present a complete output summary to the user:

```
Blog post(s): src/posts/[list files written]
All platform drafts: {output_file}

Review and edit before publishing.
```

Ask if any platform needs revision. If yes, revise the specific section and re-present. Repeat until the user is satisfied or indicates they are done.
