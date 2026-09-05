# Project agent memory

This file is the project's committed home for project-intrinsic agent knowledge: build, test, release, architecture, and sharp-edge notes that should travel with the code.

- Blog rendering decisions live in `docs/adr/0003-blog-infrastructure.md`; body component/style hooks live in `src/alberto_codes_site/pages/blog.py`. Browser scrollbar verification is documented in `docs/validation/site-pre-overflow/README.md`.
- Check `.github/workflows/deploy.yml` before waiting for pull-request CI: deployment runs on pushes to main, not pull requests.
- Convention: a post about a tagged release closes with one link to that release's GitHub page — the post's own tag only, not every inline mention or an earlier tag it references. Copy the shape from the closing bullet of `src/posts/2026-09-02-googles-4-bit-gemma-already-fit-my-card.md`, and write the descriptive clause from what that tag actually carries. The release notes already link back to the post, so the post side is the half that gets forgotten.

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.
