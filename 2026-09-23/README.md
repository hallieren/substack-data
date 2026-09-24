# 2026-09-23: the numbers behind "Does Your Monitor Know What Nobody Checked?"

Companion data for the article [Does Your Monitor Know What Nobody Checked?](https://hallieren.substack.com/p/does-your-monitor-know-what-nobody).
This drop has no experiment of ours. The article explains one paper, and
every number in its figures is transcribed here from that paper so the
figures can be checked and rebuilt without reopening it.

Source: Yibo Hu, Illinois Institute of Technology. "Silence Is Endorsement:
Verification-Status Laundering in LLM Agent Pipelines." arXiv 2609.20211v1.
https://arxiv.org/abs/2609.20211 (full text read at
https://arxiv.org/html/2609.20211).

The worked example is the paper's own item: a planner agent wants to grant a
contractor temporary read access to an analytics dashboard, on the strength
of a ticket claiming a manager approved it, when nobody actually checked. An
honest planner tags the claim UNVERIFIED. The paper measures what happens to
that tag and to the monitor's decision as the claim passes through a
summarizer and then a memory compressor before a monitor model (open models
from 0.5B to 14B, plus GPT-4o-mini and DeepSeek-V4-Flash) reads it and
decides whether to approve the action, using a controlled 40-item probe of
risky actions and a full compression-to-monitor pipeline.

## Layout

- `data/blog02_marker_word_approval.csv`: Table 2's controlled probe, the
  percent of 40 risky actions each monitor approved with the marker visible
  (UNVERIFIED), with the marker lost, and with the note rewritten to
  VERIFIED, for the full set of tested models. Feeds the grouped-bar figure
  (which plots Llama-3.1-8B, Qwen2.5-14B and GPT-4o-mini only).
- `data/blog03_semantic_loss.csv`: Table 4A, the share of summaries and of
  memory notes that no longer convey the unverified warning, by component.
  Feeds the horizontal-bar figure.
- `data/blog04_faithful_summarizer.csv`: Tables 5 and 6, word-kept and
  risky-approval rates for the uncompressed baseline, a lossy summarizer and
  a faithful summarizer, all read by the Qwen2.5-14B monitor, with the
  paper's own note that the baseline and the Table 2 probe are not directly
  comparable. Feeds the two-panel bar figure.
- `data/prose_numbers.csv`: every other number the article states, with its
  section.

## What is not here

No trajectories, no scripts, no model calls. The relay diagram (blog-01, the
note rewritten at each handoff while the underlying fact never changes), the
two-lane schematic (blog-05, a word in the note versus a field set by the
harness), and the 2x2 decision matrix (blog-06, what to fix depending on
whether the tag survived and what the monitor did) are original figures
rendered from figures/index.html and carry no numbers of their own; the
author states the structured-field fix in blog-05 was not built or tested.
All figures are original artwork, not third-party images.
