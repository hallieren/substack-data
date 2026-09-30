# 2026-09-25: the numbers behind "Did Your Agent Misread You or Botch the Job?"

Companion data for the article [Did Your Agent Misread You or Botch the Job?](https://hallieren.substack.com/p/did-your-agent-misread-you-or-botch).
This drop has no experiment of ours. The article explains one Anthropic
experiment, and every number in its figures is transcribed here from the
post and its footnotes so the figures can be checked and rebuilt without
reopening it.

Source:
- Hitzig, Carr, Cotter, Troy, Turman, Massenkoff, McCrory (Anthropic).
  "Project Swap: What happens when agents trade for us?" 24 September 2026.
  https://www.anthropic.com/research/project-swap . Full post and footnotes
  read; appendix not read.

The worked example is the study's own trading floor. 201 Anthropic
employees across six offices each brought in a book to give away. Each
person chatted with Claude for five minutes about what they like to read,
and from that chat Claude ranked every book in the pool on the person's
behalf, a guess the agent then carried onto an open trading floor to haggle
and swap books with other agents. Separately, and unseen by any agent, each
person also hand-ranked 10 books from the pool; that hidden list is the only
thing the study used to score the outcome. Comparing a perfect allocator
working from those hidden lists (the ceiling) against a perfect allocator
working only from the agents' guesses splits the market's shortfall into a
misreading part and a trading part, and a second run of the whole floor,
rankings held fixed and only the negotiating model changed, checks whether
a stronger model closes the gap that matters.

## Layout

- `data/blog02_pairwise_agreement.csv`: the four pairwise-agreement rates
  (coin flip, rank by popularity, rank by similar readers, the agent after
  its chat). Feeds the horizontal-bar figure.
- `data/blog03_allocation_and_shortfall.csv`: the three allocation scores
  (ceiling from people's own lists, perfect allocation from the agents'
  guesses, the agents' own trading) and the misreading/trading split of the
  shortfall between them. Feeds the stepped-bar and split-bar figure.
- `data/blog04_model_score_gain.csv`: the score gain from the smallest
  model (Haiku) to the largest (Opus) as negotiator, scored two ways, on
  the agents' own guesses and on people's own lists. Feeds the two-column
  figure.
- `data/prose_numbers.csv`: every other number the article states
  (participant counts, the scoring scale, the shortfall arithmetic, the
  rerun count, the budget-share figures), with its section.

## What is not here

No trajectories, no chat transcripts, no model calls. The opening figure
(the two-lane diagram of what the agent traded on versus what was used to
score) is a schematic of the study's design; its own two numbers, the
five-minute chat and the 10-book hand ranking, are already in
`prose_numbers.csv`, and the population figures in its caption (188
submitted rankings, the 3-person Dublin office excluded) are there too. An
earlier 2x2 matrix figure pairing agent-guess/true-preference against
agent-execution/perfect-stand-in was drafted (`assets/blog-05.png`,
`figures/index.html`) but is not used in the published article; it is also
schematic, and the study never ran its fourth cell (true preferences, agent
execution). Ranking by other models (footnote 3, 57% to 61%) and the
eight-message count behind the 216-word median (SOURCES.md) are cited in
the source material but not stated in the article, so they are not
transcribed here.
