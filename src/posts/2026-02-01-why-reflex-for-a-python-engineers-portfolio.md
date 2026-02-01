---
title: Why I Chose Reflex for My Portfolio Site
date: 2026-02-01
type: explanation
summary: A Python engineer's case for building a portfolio site without touching JavaScript.
tags:
  - python
  - reflex
  - web development
---

When I decided to build a personal site, the default answer was obvious: grab a React template, maybe Next.js, throw it on Vercel, and call it a day. That's what most developer portfolios run on. But I'm not a frontend engineer. I'm a Python engineer who works on AI systems, and I wanted my site to reflect that.

So I built it with [Reflex](https://reflex.dev).

## What Is Reflex?

Reflex is a Python framework for building full-stack web applications. You write Python — components, state management, routing, everything — and Reflex compiles it to a React frontend with a FastAPI backend. No JavaScript required (unless you want it).

Here's what a simple page looks like:

```python
import reflex as rx

def hello() -> rx.Component:
    return rx.container(
        rx.heading("Hello, world"),
        rx.text("Built with Python."),
    )
```

That's real, working code. No JSX, no `useState`, no `npm install`. Just Python.

## Why Not Next.js?

There's nothing wrong with Next.js. It's battle-tested, well-documented, and has a massive ecosystem. But for me, it came down to a few things:

**Context switching is expensive.** My day job is Python — agents, pipelines, data engineering. Dropping into TypeScript and the React ecosystem for a side project meant learning (or re-learning) a different set of patterns, tooling, and conventions. With Reflex, I stay in the language I think in.

**I don't need the React ecosystem.** A portfolio site doesn't need server components, incremental static regeneration, or a component library with 200 options. It needs a few pages, some text, and maybe a blog. Reflex handles that without the overhead.

**The site itself is a signal.** If I'm positioning myself as a Python and AI engineer, it makes sense for the site to be built with Python. It's a small thing, but it's consistent.

## What Reflex Gets Right

**Components feel natural.** If you've written Python, you can read Reflex code. Components are functions that return component trees. Styling uses keyword arguments. There's no template language to learn.

**State management is simple.** Reflex uses Python classes for state. You define variables, write event handlers as methods, and bind them to components. It's closer to how you'd think about state in a backend application.

**Deployment is straightforward.** `reflex run --env prod` gives you a production build. You get a FastAPI server you can deploy anywhere Python runs — no Node.js runtime needed in production.

**It includes what you need.** Routing, SEO meta tags, responsive breakpoints, markdown rendering, sitemaps — these come built in or as first-party plugins. I didn't have to research and install ten packages to get a basic site working.

## What to Watch Out For

Reflex isn't perfect, and I'd be doing you a disservice if I didn't mention the tradeoffs:

**Smaller community.** When you hit an issue, there are fewer Stack Overflow answers and blog posts to lean on compared to React or Next.js. The Discord community is active, but you'll sometimes need to read source code.

**Component library is growing but limited.** You won't find the equivalent of every Radix or shadcn component. Reflex wraps Radix Themes and gives you a solid set of primitives, but if you need something niche, you may need to write a custom component or wrap a React library yourself.

**Performance ceiling.** For a portfolio site, performance is fine. For a complex, highly interactive application with thousands of concurrent users, you'd want to evaluate more carefully. The Python backend handles state, which adds a round-trip that a pure client-side React app avoids.

**It's still maturing.** Reflex is under active development. APIs occasionally change between versions. This is improving, but it's worth noting if stability is your top priority.

## Who Should Consider Reflex?

If you're a Python developer building something like:

- A personal site or portfolio
- An internal tool or dashboard
- A prototype or MVP
- A data-driven app where Python is already doing the heavy lifting

Reflex is worth a serious look. You'll ship faster by staying in one language, and the result is a real web app — not a Streamlit dashboard with limitations.

## The Bottom Line

I chose Reflex because it let me build a professional site using the tools I already know, without compromising on the result. The site is fast, responsive, and does everything I need. And when I want to add features — like the blog you're reading right now — I'm writing Python, not context-switching into a different ecosystem.

If you're a Python engineer who's been putting off building a personal site because you don't want to deal with JavaScript tooling, give Reflex a try.
