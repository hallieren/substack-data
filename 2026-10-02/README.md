# 2026-10-02: the sources behind "Was Your Agent Right About the Wrong Thing?"

Companion data for the article [Was Your Agent Right About the Wrong Thing?](https://hallieren.substack.com/p/was-your-agent-right-about-the-wrong).
This drop has no experiment of ours. The article reads a practitioner's account
of three months of research with Claude and splits accepting agent work into
three gates: is it finished, is it right, and is it worth doing. Every quote,
event, and number in the figures is transcribed here with the source wording so
the figures can be checked without reopening the post.

Source:
- Matthew Schwartz. "Claude-shaped science." Anthropic, 1 October 2026.
  https://www.anthropic.com/research/claude-shaped-science
  Guest post. Schwartz is a visiting researcher at Anthropic; the BootLoops
  harness is his, not an Anthropic project (disclosure in the post).
- BootLoops project site, for the verification standard on amplitudes.
  https://www.bootloops.ai

## Layout

- `data/blog01_done_phrases.csv`: what Claude said when reporting done, what
  Schwartz found it meant, and the source sentence. Feeds figure 1.
- `data/blog02_forest_timeline.csv`: the neutral biodiversity project at Barro
  Colorado Island in order, by who acted, with the source sentence for each
  step. Feeds figure 2.
- `data/blog03_three_gates.csv`: the three gates, who answers each, whether a
  program can, how the forest project fared, and the basis in the source.
  Feeds figure 3.
- `data/prose_numbers.csv`: every other number the article states, with its
  section in the source.

## What is not here

No trajectories, no scripts, no model calls. Figure 3 is our synthesis of the
post, not a table from it. The post is one person's experience and gives no
counts of how often projects stopped at each gate. The 4.5x figure comes from
the Anthropic post; the BootLoops site describes the same project with
different numbers (tree counts per species) and does not repeat it.
