# 2026-10-01: the numbers behind "Can Your Agent Pick Its Own Best Idea?"

Companion data for the article [Can Your Agent Pick Its Own Best Idea?](https://hallieren.substack.com/p/can-your-agent-pick-its-own-best-idea).
This drop has no experiment of ours. The article explains a paper on spending
extra compute inside each step of a terminal agent: the model writes several
candidate commands, a judge (the paper's verifier) picks one before anything
runs, and only that one executes. Every number in the figures is transcribed
here from the paper so the figures can be checked and rebuilt without
reopening it.

Source:
- Minki Kang, Ryo Hachiuma, Shaokun Zhang, et al., Byung-Kwan Lee (NVIDIA,
  KAIST). "Mid-Harness: Scaling Actions Between Model and Harness for Terminal
  Agents." arXiv 2609.39982v1, 30 September 2026. https://arxiv.org/abs/2609.39982

The main comparison keeps one generator (TMAX-9B) and varies only the judge:
the generator judging itself with all drafts at once, one by one, or two at a
time; the generator with a LoRA adapter distilled from GPT-5.6 Sol pairwise
comparisons; and GPT-5.6 Sol itself.

## Layout

- `data/blog03_judge_by_draft_count.csv`: Pass@1 and Pass@3 at 4 and 8 drafts
  per step for each judge, plus the base agent and the first-runnable control
  (Table 5). Feeds figure 3.
- `data/blog02_port_9090_pair.csv`: the offline pairwise example where
  candidate B's cleanup script can kill itself, with both judges' scores
  (Appendix D.2.1). Feeds figure 2.
- `data/blog04_gain_intervals.csv`: Pass@1 gain over the base agent with
  95% task-level bootstrap intervals for six generator and judge pairs
  (Table 10). Feeds figure 4.
- `data/prose_numbers.csv`: every other number the article states, with its
  section in the source.

## What is not here

No trajectories, no scripts, no model calls. Figure 1 is a schematic of the
loop and carries no numbers. The paper has no gold labels for single actions,
so every statement that a judge was right or wrong uses GPT-5.6 Sol as the
reference. The paper does not compare against using GPT-5.6 Sol as the
generator. Main results come from one benchmark of 98 tasks with three runs
each. The paper is not peer reviewed.
