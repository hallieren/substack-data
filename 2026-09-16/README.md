# 2026-09-16: the numbers behind "What Did You Validate Your Judge Against?"

Companion data for the article [What Did You Validate Your Judge Against?](https://hallieren.substack.com/p/what-did-you-validate-your-judge).
This drop has no experiment of ours. The article explains one paper, and every
number in its figures is transcribed here from that paper so the figures can be
checked and rebuilt without reopening it.

Source: Utsav Bodhwani, Nam Tran, Ting-Kai Wei. "GAUGE: When Not to Trust
LLM-as-a-Judge in User-Simulated Evaluation of Task-Oriented Agents."
arXiv 2609.12191, 10 September 2026, EMNLP 2026 Industry Track.
https://arxiv.org/abs/2609.12191

The worked example is the paper's own setup on tau2-bench retail and airline: a
persona-driven simulated customer talks to a candidate agent, and the same
transcript is read by a blind human panel, a satisfaction-only LLM proxy, a
policy-aware LLM gate, and a non-LLM check of the database end state. 25 agent
configurations from six providers, about 3,700 transcripts.

## Layout

- `data/blog02_fail_given_accepted.csv`: Table 2, failure rate among transcripts
  each signal accepted versus the base failure rate of its pool, with AUC.
  Feeds the paired-bar figure.
- `data/blog03_controlled_degradation.csv`: Appendix C Table 6, the twelve
  Sonnet-4.5 flag-only configurations (eight working, four broken on purpose)
  with verifiable reward and human satisfaction. The figure plots the working
  average and the four broken rows. Feeds the two-column figure.
- `data/blog04_near_equal_disagreement.csv`: Table 9 and Appendix F.1 and G,
  decision-disagreement on wide versus near-equal pairs, per judge, averaged,
  and with calibrated abstention. Feeds the two-big-numbers figure.
- `data/blog06_cadence.csv`: Table 3, cost and rank correlation of the cheap
  completion bit, the LLM judge and the verifiable check, and when each runs.
  Feeds the action figure.
- `data/prose_numbers.csv`: every other number the article states, with its
  section.

## What is not here

No trajectories, no scripts, no model calls. The four-readers figure and the
three-layers figure are diagrams of the paper's setup and carry no numbers
beyond those above. The figure HTML lives with the article draft. All runs
were made by the paper's authors.
