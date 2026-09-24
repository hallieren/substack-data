# 2026-09-22: the numbers behind "Does Your Judge Need to Explain Itself?"

Companion data for the article [Does Your Judge Need to Explain Itself?](https://hallieren.substack.com/p/does-your-judge-need-to-explain-itself).
This drop has no experiment of ours. The article explains a newly released
inference-only judge model and the independent tests run on it in its first
week, and every number in its figures is transcribed here from those sources
so the figures can be checked and rebuilt without reopening them.

Sources:
- TypeSafe. "Introducing System One Models and Jev." TypeSafe blog, 15
  September 2026. https://typesafe.ai/blog/introducing-system-one-models-and-jev
- TypeSafe. Workflow evals, Agent Trace Observability task.
  https://evals.typesafe.ai/
- TypeSafe. Docs, the Noul and Confidence primitives.
  https://docs.typesafe.ai/primitives/noul and https://docs.typesafe.ai/confidence
- Archer Hume. "Jev's architecture unmasked."
  https://archerhume.com/posts/jevs-architecture-unmasked/
- Hamel Husain and Shreya Shankar. "AI Evals: Everything You Need to Know"
  (evals FAQ). https://hamel.dev/blog/posts/evals-faq/ , cached 2026-09-18.
- Simon Willison. "Jev introduces a new shape of LLM." 21 September 2026.
  https://simonwillison.net/2026/Sep/21/jev/

The worked example is TypeSafe's own Agent Trace Observability task: a
support agent finishes with a customer, and a judge, either your LLM judge or
Jev, reads the whole trace and decides whether a person needs to look and how
soon. TypeSafe graded four judges on this task against reference labels it
averaged from two larger models (GPT-6 Astra and Claude Fable 5.1 at high
reasoning), not from humans, and Archer Hume independently probed Jev's
latency and calibration on three unrelated task sets.

## Layout

- `data/blog02_trace_review_eval.csv`: TypeSafe's workflow-mode results on
  the Agent Trace Observability task, accuracy against the reference labels,
  cost per 1,000 cases, and seconds per case, for Opus 5, Jev, Sonnet 5 and
  Haiku 4.5. Feeds the three-panel bar figure.
- `data/blog04_calibration.csv`: Archer Hume's three calibration checks
  (two-step word problems, three-digit multiplication, a 990-item MMLU
  confidence bin), the rounded values the figure plots and the precise
  values behind them. Feeds the scatter figure.
- `data/blog05_threshold_bands.csv`: the two threshold examples from
  TypeSafe's Noul docs, each split into a pass zone, a queued zone and an
  escalate-now zone. Feeds the two-band figure.
- `data/prose_numbers.csv`: every other number the article states, with its
  section.

## What is not here

No trajectories, no scripts, no model calls. The two-lane mechanism diagram
(blog-01, an LLM judge versus Jev) and the audit-flow diagram (blog-03, both
judges compared against your labels with the paragraph left outside the
check) are original figures rendered from figures/index.html and carry no
data of their own; blog-03's one number, the 50 pass and 50 fail label set,
is captured in prose_numbers.csv instead. All figures are original artwork,
not third-party images.
