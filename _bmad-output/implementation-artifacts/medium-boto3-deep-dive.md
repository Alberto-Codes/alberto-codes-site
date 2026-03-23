# Medium Draft: boto3 Deep-Dive

## Images to upload (in order of appearance):
1. **Header**: `/tmp/boto3-architecture-coverage.png` (the blue vs amber coverage comparison)
2. **After event system quote**: `/tmp/boto3-event-system.png` (the flowchart the original agent couldn't produce)
3. **Social preview** (optional, for the card): `/var/home/Alberto-Codes/Projects/docvet/social-preview.png`

## Medium tags (select at publish time):
Python, AI, Software Development, Developer Tools, Open Source

## Canonical URL (set in story settings after publish):
https://alberto.codes/blog/2026-03-23-i-asked-an-ai-to-explain-boto3-then-i-fixed-the-docstrings

---

## Article

# I asked an AI to explain boto3. Then I fixed the docstrings.

boto3 gets 43 million installs a day. It's the Python SDK for AWS — the package every AI coding assistant reads when it helps you write cloud code. I wanted to know: how good are the docstrings, and does it actually matter?

So I ran an experiment. I cloned boto3 twice at the same commit. Left one copy untouched. On the other, I ran docvet — a docstring quality tool I built — which found 336 documentation gaps across 39 files. Half of all public symbols had no docstring at all. Functions that return values didn't say what they return. Functions that raise exceptions didn't document which ones.

I fixed everything docvet flagged. Then I asked a fresh AI agent to generate architecture documentation from each copy — same model, same prompt, no knowledge of what changed. The only variable was docstring quality.

The results weren't close.

---

**[INSERT IMAGE: boto3-architecture-coverage.png]**

*The docvet-fixed agent covered 9 subsystems in 484 lines. The original covered 5 in 618.*

---

The agent working with the original docstrings produced 618 lines with 13 Mermaid diagrams. It went deep on the resource factory, action execution, and collection pagination — the subsystems it could figure out by reading the code. But it missed entire parts of the architecture. The event-driven customization system that wires S3 transfers, DynamoDB transforms, and EC2 tag injection together? Not covered. The CRT transfer backend? Not mentioned. The documentation generation pipeline? Absent.

The agent working with docvet-fixed docstrings produced 484 lines with 15 diagrams. Shorter, broader. It covered everything the first agent covered plus five additional subsystems — in 134 fewer lines.

The difference was clearest in the event system. The original agent noted: "Session._register_default_handlers() has no docstring at all. This is arguably the most architecturally important method in the codebase. I had to read every register() call and trace the lazy_call targets to understand the customization architecture."

The fixed agent didn't complain about that method. It diagrammed it.

---

**[INSERT IMAGE: boto3-event-system.png]**

*The event system diagram the original agent couldn't produce. Every event name, every handler, every injected method — mapped because the docstring said what was there.*

---

Both agents understood the same fundamentals: boto3 wraps botocore, the resource factory dynamically creates classes from JSON, collections handle pagination transparently. They got the same facts right. The difference was in how they got there.

Without docstrings, the agent reverse-engineers. It reads function bodies, traces imports, follows call chains. AI models are remarkably good at this — but it's expensive and narrow. The agent spends its budget understanding how individual functions work and runs out before mapping how modules connect.

With docstrings, the agent comprehends. It reads the module docstring, follows the See Also cross-references, checks the Returns and Raises sections, and moves on. Less time per function, more time on the architecture. Broader coverage in fewer lines.

This tracks with published research. Macke and Doyle (NAACL 2024) found that incorrect documentation degrades LLM task success by 22.6 percentage points — while missing documentation has no statistically significant effect on accuracy. The AI gets the answers right either way. But the path matters.

I tested this further with pop quizzes — the same targeted questions asked across five different models (Claude Opus, Sonnet, Haiku, GPT-4o, GPT-4.1). The cleanest example: I asked what exceptions S3Transfer.upload_file() raises.

Without docvet, the agent said: "The docstring says only 'Upload a file to an S3 object' — zero mention of type validation or failure behavior." It found the right answer by reading the method body.

With docvet, the agent said: "The Raises section names both S3UploadFailedError and ValueError, which is the right starting point." Same correct answer. Found in the documentation instead of the code.

Same pattern across all five models. The answers converged. The sources diverged.

One thing this experiment didn't test: wrong docstrings. I only added documentation where none existed. The more dangerous case is stale documentation — a docstring that used to be correct but drifted after a refactor. docvet catches that too, with freshness rules that compare docstrings against recent code changes. boto3 ships new versions almost daily, so freshness matters as much as presence.

The bottom line: boto3 is maintained by Amazon. It has 50.3% docstring coverage and 336 documentation gaps that measurably affect how AI understands its architecture. Your codebase almost certainly has more.

The fix isn't writing docstrings for coverage metrics. It's writing docstrings that tell AI agents what they actually need — returns, raises, module relationships, and where to look next.

pip install docvet (or uv add docvet --dev)

Full docs: https://alberto-codes.github.io/docvet/

The AI reading your code will find the answers either way. The question is whether it finds them in your documentation or reverse-engineers them from your implementation.

Full technical walkthrough with code examples and comparison data: https://alberto.codes/blog/2026-03-23-i-asked-an-ai-to-explain-boto3-then-i-fixed-the-docstrings
