# ADR-0002: Blog Content Strategy Using the Diataxis Framework

## Status

Accepted

## Date

2026-02-01

## Context

The portfolio site has a blog section (currently a "coming soon" placeholder). As a Generative AI Principal Engineer, publishing technical content would establish thought leadership, demonstrate expertise, and provide value to the developer community.

We need a content strategy that:

- Gives structure to blog posts so they are purposeful and well-organized
- Is approachable for someone new to technical writing
- Helps readers find the type of content they need quickly
- Scales as the blog grows over time

The **Diataxis framework** (created by Daniele Procida) is a widely adopted documentation framework used by Cloudflare, Django, LangChain, and many other projects. It organizes content into four distinct types based on the reader's needs.

## Decision

We will adopt the Diataxis framework to categorize and structure all blog content. Each post should clearly fit into one of the four Diataxis quadrants:

### 1. Tutorials (Learning-oriented)

- **Purpose**: Walk a beginner through a hands-on learning experience step by step
- **Audience**: Someone new to the topic who wants to learn by doing
- **Tone**: Encouraging, guided — "follow along with me"
- **Example posts**:
  - "Build Your First AI Agent with Google ADK"
  - "Getting Started with Reflex: A Python Web Framework"
- **Key rule**: The reader should *always succeed* by following the steps. Keep them on the happy path.

### 2. How-to Guides (Task-oriented)

- **Purpose**: Help an already-competent reader solve a specific real-world problem
- **Audience**: Someone who knows the basics and needs to get something done
- **Tone**: Direct, practical — "here's how to do X"
- **Example posts**:
  - "How to Deploy a Reflex App to Cloud Foundry"
  - "How to Add RAG to an Existing LangChain Agent"
- **Key rule**: Stay focused on the goal. Don't teach background concepts — link to tutorials or explanations instead.

### 3. Explanation (Understanding-oriented)

- **Purpose**: Help readers understand the *why* behind a concept, pattern, or decision
- **Audience**: Someone who wants deeper context and reasoning
- **Tone**: Conversational, thoughtful — "here's why this matters"
- **Example posts**:
  - "Why We Chose Reflex Over Next.js for a Python-First Portfolio"
  - "What Enterprise AI Architecture Actually Looks Like"
- **Key rule**: No steps or instructions. Focus on context, background, tradeoffs, and opinions.

### 4. Reference (Information-oriented)

- **Purpose**: Provide accurate, complete technical facts for quick lookup
- **Audience**: Someone actively working who needs specific details
- **Tone**: Precise, factual — "here are the specs"
- **Example posts**:
  - "Reflex Component Cheat Sheet"
  - "ADK Agent Configuration Options"
- **Key rule**: Be exhaustive and accurate. Structure for scanning (tables, lists, code blocks).

### Blog Implementation Guidelines

- Each post should be **tagged with its Diataxis type** (tutorial, how-to, explanation, reference) so readers can filter by what they need
- Posts should be **1000-1500 words** for most types, longer for in-depth
  tutorials and for evidence-backed explanations (see the 2026-08-11
  amendment)
- Use clear **H2/H3 headings** for scannability
- **Cross-link** between types (e.g., a how-to guide links to the relevant tutorial and reference)
- Start with tutorials and explanations — these are the most natural for someone new to writing and the most valuable for building an audience
- Keep a consistent publishing cadence over volume — one quality post per month beats four rushed ones

## Consequences

### Positive

- Provides a clear framework for deciding what to write and how to structure it
- Reduces writer's block — just pick a quadrant and a topic
- Readers can quickly identify if a post matches their need (learning, doing, understanding, or looking up)
- Cross-linking between types creates a cohesive content ecosystem
- Tagging by type improves site navigation and UX
- Well-established framework with proven adoption across the industry

### Negative

- Some posts may not fit neatly into one quadrant — hybrid content requires judgment calls
- Requires discipline to keep post types distinct (e.g., not turning a how-to into a tutorial)
- Reference posts are less engaging to write but important for completeness
- Adds categorization overhead to each post

## Amendment 2026-08-11: length for evidence-backed explanations

The 1000-1500 band was set on 2026-02-01, before this blog published a post
that carried a public evidence trail. It was calibrated on posts that explain
one idea. It does not fit a post that explains an idea *and* publishes the
record behind it.

**Explanation posts that carry an evidence trail may run 2000-2500 words.**
The band still governs everything else.

Two conditions apply, because the extra length has to be earned:

1. **Every added word carries a claim someone could check.** Length bought by
   restatement or hedging gets cut. If a paragraph does not add a fact, a
   limitation, or a step in the argument, it is padding regardless of the
   total.
2. **Scannability scales with length.** Past 1500 words a post needs enough
   headings and figures that a reader can find the argument without reading
   every sentence. Word count is a proxy for reader effort; entry points are
   what actually reduce it.

Prompted by "I couldn't tell my quantized model from the baseline"
(2026-08-11) — 2163 words, 9 headings, 4 figures. A word-economy pass took it
from 2361 to 2163. Cutting to 1500 would have meant dropping the loss ledger,
the per-card budget, or the transparency argument, each of which carries a
claim the post exists to make.

Open question: whether the 2000-2500 ceiling is right, or is itself an
unvalidated heuristic of the kind this blog argues against. Revisit once
there is real completion data.

## References

- [Diataxis Framework - Official Site](https://diataxis.fr/)
- [Diataxis in Five Minutes](https://diataxis.fr/start-here/)
- [I'd Rather Be Writing - What is Diataxis?](https://idratherbewriting.com/blog/what-is-diataxis-documentation-framework)
- [Sequin - We Fixed Our Docs with Diataxis](https://blog.sequinstream.com/we-fixed-our-documentation-with-the-diataxis-framework/)
- [Infrasity - Tech Blog Post Checklist](https://www.infrasity.com/blog/blog-post-checklist)
- [DEV Community - Why Every Developer Needs a Portfolio in 2026](https://dev.to/aureathemes/why-every-developer-needs-a-portfolio-in-2026-40f)
