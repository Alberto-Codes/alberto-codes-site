---
title: Give Your AI Agent a Docstring Quality Tool
date: 2026-03-04
type: how-to
summary: Wire docvet's MCP server into VS Code, Cursor, or Claude Code — your AI coding agent gets structured docstring quality checks without parsing CLI output.
tags:
  - python
  - mcp
  - vscode
  - ai
  - docstrings
  - developer tools
  - open source
---

Your AI coding agent can read your code, run your tests, and search your repo. But can it check whether your docstrings actually match what the code does?

[In a previous post](/blog/2026-02-25-your-ai-reads-your-docstrings), I made the case that stale docstrings actively mislead AI agents — in controlled tests, incorrect documentation drops LLM task success by 22.6 percentage points. Agents given wrong docstrings performed worse than agents given no docstrings at all. [docvet](https://github.com/Alberto-Codes/docvet) was built to catch those gaps: 19 rules that check whether your docstrings actually match what the code does.

Since v1.8, docvet ships an MCP server. That means any MCP-aware editor — VS Code, Cursor, Claude Code, Windsurf, Claude Desktop — can give its AI agent direct access to docstring quality checks. Structured JSON, not CLI text parsing. One config block, zero install.

---

## What Your Agent Gets

Two tools appear in the agent's toolbox:

**`docvet_check`** — Run checks on any Python file or directory. The agent receives structured findings:

```json
{
  "findings": [
    {
      "file": "src/pipeline/extract.py",
      "line": 42,
      "symbol": "extract_text",
      "rule": "missing-raises",
      "message": "Function 'extract_text' raises ValueError but has no Raises section",
      "category": "required"
    }
  ],
  "summary": {
    "total": 3,
    "by_category": {"required": 2, "recommended": 1},
    "files_checked": 8
  }
}
```

**`docvet_rules`** — List all 19 rules with descriptions and categories. Useful when the agent needs to explain a finding or decide what to fix first.

No CLI output to parse. No regex. The agent gets typed fields it can reason about directly.

---

## Why MCP, Not CLI?

Without MCP, your agent shells out to `docvet check` and has to make sense of this:

```console
src/pipeline/extract.py:42: missing-raises - Function 'extract_text' raises ValueError but has no Raises section
src/pipeline/extract.py:87: missing-param - Parameter 'timeout' not documented
src/utils/cache.py:15: stale-signature - Docstring parameters don't match function signature
```

That works, but the agent is regex-matching strings instead of reasoning about typed data. With MCP, it gets the structured JSON shown above — fields it can filter, sort, and act on directly.

---

## Setup: One Block of JSON

The MCP server runs on stdio via `uvx` — no `pip install` in your project, no virtual environment pollution, no global packages. `uvx` downloads and runs docvet in an isolated environment automatically. You add the config and it just works.

### VS Code

Add to `.vscode/mcp.json` in your project root:

```json
{
  "servers": {
    "docvet": {
      "type": "stdio",
      "command": "uvx",
      "args": ["docvet[mcp]", "mcp"]
    }
  }
}
```

Note: VS Code uses `"servers"` as the top-level key, not `"mcpServers"`.

### Cursor

Add to `.cursor/mcp.json` (project-level) or `~/.cursor/mcp.json` (global):

```json
{
  "mcpServers": {
    "docvet": {
      "command": "uvx",
      "args": ["docvet[mcp]", "mcp"]
    }
  }
}
```

### Claude Code

One command, no JSON editing:

```bash
claude mcp add --transport stdio --scope project docvet -- uvx "docvet[mcp]" mcp
```

Use `--scope user` to make it available across all projects.

### Windsurf / Claude Desktop

Same `mcpServers` pattern — see the [full editor guide](https://alberto-codes.github.io/docvet/editor-integration/#client-configuration) for copy-paste configs. There's also a [dedicated VS Code setup tab](https://alberto-codes.github.io/docvet/editor-integration/#__tabbed_1_3) if you just want the one-click config.

---

## What Happens Next

Once configured, your AI agent can invoke `docvet_check` on any file it's working with. A typical workflow:

1. Agent opens a Python file to modify
2. Agent runs `docvet_check` on the file
3. Findings come back as structured JSON — missing Raises sections, stale signatures, undocumented attributes
4. Agent fixes the docstrings alongside the code change

The feedback loop becomes automatic: the agent checks docstring quality as part of its normal workflow, not as an afterthought.

---

## Try It

If you have VS Code with MCP support enabled:

1. Add the `.vscode/mcp.json` block above
2. Open a Python file with a known docstring gap (a function that raises an exception but has no `Raises:` section)
3. Ask your AI agent to check the file with docvet
4. Watch it get structured findings and fix the docstring

Now your agent can check whether your docstrings actually match what the code does. One config block, zero install.

docvet is on [PyPI](https://pypi.org/project/docvet/), [GitHub](https://github.com/Alberto-Codes/docvet), and the [MCP Registry](https://registry.modelcontextprotocol.io). The full editor setup guide is at [alberto-codes.github.io/docvet/editor-integration](https://alberto-codes.github.io/docvet/editor-integration/).

---

## Further Reading

- [VS Code MCP setup (copy-paste config)](https://alberto-codes.github.io/docvet/editor-integration/#__tabbed_1_3)
- [Full editor integration docs](https://alberto-codes.github.io/docvet/editor-integration/)
- [GitHub announcement: docvet is on the MCP Registry](https://github.com/Alberto-Codes/docvet/discussions) — v1.8 launch post
- [Your AI Reads Your Docstrings. Are They Right?](/blog/2026-02-25-your-ai-reads-your-docstrings) — the problem this solves
- [MCP specification](https://modelcontextprotocol.io/)
- [VS Code MCP support](https://code.visualstudio.com/docs/copilot/chat/mcp-servers)
