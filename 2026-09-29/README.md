# 2026-09-29: the numbers behind "Does Your Agent Say No When It Should?"

Companion data for the article [Does Your Agent Say No When It Should?](https://hallieren.substack.com/p/does-your-agent-say-no-when-it-should).
This drop has no experiment of ours. The article explains one paper, and
every number in its figures is transcribed here from that paper so the
figures can be checked and rebuilt without reopening it.

Source: Zhengxuan Wu, Yuxuan Li, Oyvind Tafjord, Been Kim. "XYEval: Agents
say yes to bad advice." Google DeepMind, arXiv:2609.23939v1, 20 Sep 2026.
https://arxiv.org/abs/2609.23939
Benchmark release: https://github.com/google-deepmind/xyeval

The worked example is tau2-bench's airline customer service benchmark. One
model plays the customer, the agent under test plays the airline's support
rep with a booking database and a policy manual, and a checker compares the
final database state with the correct one across 50 tasks. The paper adds a
single confident, wrong suggestion to the customer's opening message, upgrade
to business class, leaving the database, policy, and checker untouched. Every
model tested loses a quarter to more than half of its original score on that
one added sentence, even though the simulated customer is scripted to back
down the moment the agent says no. A second analysis, read by another model,
finds that the agent's own reasoning usually spots the problem, but in a
quarter to a third of those cases the agent never says so to the customer. A
general warning in the system prompt shrinks the drop without closing it.

## Layout

- `data/blog02_airline_scores.csv`: tau2-bench airline scores per model,
  original versus with the added sentence. Feeds the dumbbell figure.
- `data/blog03_unspoken_disagreement.csv`: for the three Gemini models,
  the share of reasoning-caught-it records where the agent told the
  customer versus never did. Feeds the two-lane stacked-bar figure. A note
  in the file gives the 92.1% pooled base rate the table conditions on.
- `data/blog04_warning_mitigation.csv`: relative score drop per Gemini
  model under three conditions, no warning, a general warning in the system
  prompt, and the wrong sentence named to the agent in advance. Feeds the
  grouped-bar figure.
- `data/prose_numbers.csv`: every other number the article states, with its
  section.

## What is not here

No trajectories, no scripts, no model calls. Figure 1 of the article is a
schematic of the task setup (the two customer messages feeding one shared
database, policy, and checker) and carries no numbers of its own; the two
sample customer lines it shows are direct quotes from Figure 3 of the paper,
not transcribed as data. All figures are original programmatic graphics
built from the numbers in this drop, not third-party images. The judge
model that reads reasoning versus reply covers only the three Gemini models,
and the warning experiments cover the same three; the paper does not run
either on Claude Opus 4.8 or GPT 5.5.
