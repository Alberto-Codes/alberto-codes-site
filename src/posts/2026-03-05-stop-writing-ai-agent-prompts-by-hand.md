---
title: Stop Writing AI Agent Prompts by Hand
date: 2026-03-05
type: explanation
summary: You write your agent's instructions, test them, tweak a word, test again, and hope the change helped. There's an algorithm that does this better than you do — evolutionary optimization finds prompts you'd never write yourself.
tags:
  - python
  - ai
  - google adk
  - prompt engineering
  - open source
---

You write a prompt. You test it. It's okay but not great — the agent misses edge cases, ignores context, or produces output that's technically correct but tonally wrong. So you tweak a sentence. Test again. Better on one example, worse on another. You rewrite the whole thing. Test again. Repeat until you're tired or the deadline hits, whichever comes first.

This is how most people build AI agents. It's also how most people season food before they learn to taste as they go — a pinch of this, a dash of that, hope for the best. It works, kind of. But it doesn't scale, it doesn't generalize, and it leaves performance on the table that you'll never find through manual iteration.

What if an algorithm could do this loop for you — and do it better?

---

## The Problem With Human Prompt Engineering

Manual prompt engineering has a ceiling. Humans are good at writing instructions that sound clear to other humans, but LLMs don't process text the way we do. The prompt that reads best to you isn't necessarily the prompt that produces the best output from the model.

There are a few specific failure modes:

- **Local optima** — you find a prompt that works well enough and stop iterating, never discovering the dramatically different phrasing that scores higher
- **Narrow testing** — you test against two or three examples, miss the edge cases, and discover them in production
- **Instinct over data** — you change what feels wrong instead of what measurably underperforms
- **Single-objective thinking** — you optimize for one quality (accuracy, tone, format) while degrading others you're not watching

These aren't character flaws. They're the natural limitations of a human trying to search a vast space of possible text through trial and error. The space of possible instructions for even a simple agent is effectively infinite, and your ability to explore it is limited by time, patience, and cognitive bias.

---

## Evolutionary Optimization: The Core Idea

Evolutionary prompt optimization borrows from genetic algorithms. Instead of you guessing at better prompts, an algorithm systematically explores the space:

1. **Evaluate** — run the agent on a batch of examples, score the outputs
2. **Reflect** — analyze what worked and what didn't across all examples
3. **Mutate** — an LLM proposes improved instructions based on the analysis
4. **Select** — if the new instruction scores better, keep it; otherwise, discard it

Repeat until the scores plateau or you hit an iteration limit.

![The evolution loop — training examples flow through the agent, critic, and reflection agents. The mutated instruction is accepted or rejected based on score improvement, then the loop repeats.](/evolution-loop.svg)

The key insight is step 3. The mutation isn't random — it's informed. A reflection model sees the agent's actual outputs, the scores, and the feedback, then proposes specific text changes to address the weaknesses it observed. It's less "random mutation" and more "systematic recipe refinement" — tasting every dish that comes out of the kitchen, identifying exactly what's off, and adjusting the technique accordingly.

This is the approach described in the [GEPA paper](https://arxiv.org/abs/2507.19457) (Genetic-Pareto prompt optimizer). GEPA treats prompt components as evolvable genes and uses LLM-powered reflection instead of random crossover. The result is an optimizer that can improve agent instructions in ways that surprise even the person who wrote the original prompt.

---

## What This Looks Like in Practice

[gepa-adk](https://github.com/Alberto-Codes/gepa-adk) is a Python library that brings evolutionary optimization to Google ADK agents. You give it an agent, training examples, and a critic — it gives you back a better prompt.

Here's the simplest possible example. Start with a greeting agent that has a generic instruction:

```python
from google.adk.agents import LlmAgent
from gepa_adk import evolve_sync, EvolutionConfig, SimpleCriticOutput

# The agent to evolve — starts with a vague instruction
agent = LlmAgent(
    name="greeter",
    model="gemini-2.5-flash",
    instruction="Greet the user appropriately.",
)

# A critic that knows what "good" looks like
critic = LlmAgent(
    name="critic",
    model="gemini-2.5-flash",
    instruction="Score for formal, Dickens-style greetings. 0.0-1.0.",
    output_schema=SimpleCriticOutput,
)

# Training examples covering different social contexts
trainset = [
    {"input": "I am His Majesty, the King."},
    {"input": "I am your mother."},
    {"input": "I am a close friend."},
]

result = evolve_sync(agent, trainset, critic=critic)
print(f"Score: {result.original_score:.2f} -> {result.final_score:.2f}")
print(result.evolved_components["instruction"])
```

The original instruction — "Greet the user appropriately" — is five words. The evolved instruction might be three paragraphs of specific guidance about formality levels, period-appropriate language, honorific handling, and tonal variation. You would never write that prompt yourself. Not because you couldn't, but because you wouldn't think to be that specific in those particular ways.

---

## Why a Critic Changes Everything

The critic is what separates evolutionary optimization from "just running the prompt a bunch of times." Without a critic, you're scoring outputs manually or relying on the agent to self-assess (which is like asking the cook to rate their own soup — helpful but biased).

A critic agent is a separate LLM that evaluates outputs against explicit criteria. It returns a score and feedback:

```python
class SimpleCriticOutput(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    feedback: str
```

The feedback is the ingredient that makes reflection work. The reflection model doesn't just see "this scored 0.4" — it sees "this scored 0.4 because the greeting was too casual for royalty and used modern slang." That specific diagnosis drives specific mutations.

You can also use multi-dimensional scoring — rate outputs on clarity, accuracy, tone, and format independently. GEPA tracks a Pareto frontier across dimensions, so you don't have to collapse everything into a single number and lose information about what's actually improving.

---

## The Evolution Loop, Unpacked

What actually happens inside `evolve()`:

**Iteration 1**: The agent runs on all training examples with its original instruction. The critic scores each output. Average score: 0.35. The reflection model reads every output, every score, every piece of feedback. It proposes a new instruction that addresses the most common failure patterns.

**Iteration 2**: The agent runs again with the proposed instruction. Scores improve to 0.62. The reflection model sees what got better and what's still weak. It proposes another refinement.

**Iteration 3**: Scores hit 0.78. The reflection model notices diminishing returns and makes a smaller, more targeted adjustment.

**Iteration 4**: Scores reach 0.81. No improvement over the previous best after the patience window. Evolution stops.

The `EvolutionConfig` controls this process:

```python
config = EvolutionConfig(
    max_iterations=5,     # Upper bound on iterations
    patience=2,           # Stop if no improvement for N iterations
    reflection_model="gemini-2.5-flash",  # Model for generating mutations
)
```

Each iteration makes multiple LLM calls — the agent runs on every training example, the critic scores every output, and the reflection model analyzes everything. This is why gepa-adk recommends local models via Ollama for development. Evolution is compute-hungry by nature, and local inference keeps the iteration loop fast and free.

---

## What Can Evolve

Instructions are the most common target, but they're not the only evolvable component. gepa-adk can also optimize:

- **Output schemas** — the Pydantic model that structures the agent's response
- **Generation config** — LLM parameters like temperature and top-p
- **Multi-agent systems** — evolve instructions across multiple agents simultaneously, optimizing how they work together

That last one is where things get interesting. In a multi-agent pipeline, the instructions of one agent affect the inputs to the next. Evolving them together means the optimizer can find coordination patterns that no amount of individual prompt tuning would discover — like a kitchen brigade where the saucier and the grill cook learn to time their dishes together instead of each optimizing in isolation.

---

## When to Use This

Evolutionary optimization isn't for every prompt. It shines when:

- **You have measurable quality criteria** — if you can define what "good" looks like in a critic, evolution can optimize for it
- **Your agent runs on diverse inputs** — evolution generalizes across training examples instead of overfitting to one
- **Manual tuning has plateaued** — you've tweaked the prompt as far as your intuition goes
- **You're building for production** — the difference between a 0.65 and a 0.82 score matters when the agent runs thousands of times

It's less useful for one-off prompts, creative tasks without clear quality metrics, or situations where the "right answer" changes too frequently for a training set to be meaningful.

---

## Key Takeaways

- **Manual prompt engineering has a ceiling** — human intuition can't efficiently search the space of possible instructions
- **Evolutionary optimization uses LLM-powered reflection** — not random mutation, but informed analysis of what's working and what isn't
- **A critic agent is the key ingredient** — structured scoring and feedback drive meaningful improvements
- **The evolved prompts are often surprising** — the algorithm finds instruction patterns you wouldn't write yourself
- **Get started now**: `pip install gepa-adk`

---

## Further Reading

- [gepa-adk on GitHub](https://github.com/Alberto-Codes/gepa-adk)
- [gepa-adk on PyPI](https://pypi.org/project/gepa-adk/)
- [gepa-adk Documentation](https://alberto-codes.github.io/gepa-adk/)
- [GEPA Paper](https://arxiv.org/abs/2507.19457) — the research behind the algorithm
- [Google Agent Development Kit](https://google.github.io/adk-docs/)
