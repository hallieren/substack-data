# 2026-09-15: the numbers behind "Does Your Agent Need a Boss?"

Companion data for the article [Does Your Agent Need a Boss?](https://hallieren.substack.com/p/does-your-agent-need-a-boss).
This drop has no experiment of ours. The article explains one paper, and every
number in its figures is transcribed here from that paper so the figures can be
checked and rebuilt without reopening it.

Source: Burak Agachan, Max van Duijn, Amirhossein Zohrehvand. "Loop-Back
Authority in LLM Agent Teams: A Paired Experiment on Flat and Hierarchical
Coordination." arXiv 2609.14767v1, 13 September 2026.
https://arxiv.org/abs/2609.14767

The worked example is the paper's own experiment: five agents (Researcher,
Analyst, Writer, Critic, Manager) write a business report on each of 43 gaming
laptops with 540 customer reviews in total. Roles, prompts, tools, models and
data are frozen; the one varied link is whether the Manager may send a worker's
output back (at most twice per run) or may only comment. 43 pairs, 86 runs,
scored by a five-model judge panel and a deterministic specification check.

## Layout

- `data/blog02_primary_outcomes.csv`: Table 2, the four judged outcomes
  (utility, writing clarity, specification accuracy, final score) with per-form
  means and SDs, paired Cohen's d and p. Feeds the dumbbell figure.
- `data/blog03_clarity_by_sendbacks.csv`: Figure 3 and Section 4.5, mean
  writing clarity of hierarchical runs grouped by number of send-backs, with
  n per group. The 0 and 3 values are stated in the text; the 1 and 2 values
  are read from the figure and marked as such. Feeds the dose-response figure.
- `data/blog04_cost_and_checker.csv`: tokens and dollars per report in each
  form, and the specification check that stays at ceiling. Feeds the cost
  figure.
- `data/prose_numbers.csv`: every other number the article states, with its
  section, including the hedge lexicon result and the paper's design rule.

## What is not here

No trajectories, no scripts, no model calls. The pipeline figure, the
verify-versus-opine figure and the checklist figure are diagrams of the paper's
setup and rule and carry no numbers beyond those above. The figure HTML lives
with the article draft. All runs were made by the paper's authors. The article's
one-sentence aside on the Anthropic "Tokens Should Have Jobs" talk carries no
number because the two secondhand summaries we found disagree.
