# 2026-09-17: the numbers behind "Who Graded GitHub's Agents?"

Companion data for the article [Who Graded GitHub's Agents?](https://hallieren.substack.com/p/who-graded-githubs-agents).
This drop has no experiment of ours. The article explains one engineering
retrospective, and every number in its figures is transcribed here from that
post so the figures can be checked and rebuilt without reopening it.

Source: Stephen Toub. "Migrating the GitHub Copilot runtime to Rust, using
Copilot." GitHub Blog, 16 September 2026.
https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot

The worked example is the port itself: one engineer supervising Copilot agents
that rewrote the Copilot agent runtime from about 430,000 lines of TypeScript
into 832,378 lines of production Rust over 14.5 weeks, in place on main, with the
old implementation and its end-to-end tests acting as the oracle.

## Layout

- `data/blog01_compiler_errors.csv`: the four rustc diagnostic families and the
  borrow checker share, of 8,678 logged errors. Feeds the bar figure.
- `data/blog02_port_cadence.csv`: pull requests, releases, window, line counts
  and the temporary interop seam. `data/blog02_prs_by_period.csv`: the post's
  half-month table of port PRs and median changed lines. Feed the swap figure's
  footer.
- `data/blog03_regression_families.csv`: the five families from the post's
  regression taxonomy chart, the plain-language label the figure uses for each,
  and the one example the article quotes.
- `data/blog04_waiver_sequence.csv`: the schema-break-ok episode step by step,
  and the deleted-test aside. Feeds the swimlane figure.
- `data/blog05_judge_layers.csv`: the four checking layers and the engineer
  above them, what each certifies and misses, and the number shown for each.
  Feeds the layers figure.
- `data/prose_numbers.csv`: every other number the article states, with its
  section. The no-agent cost estimate is the article's own arithmetic and is
  marked as such; the post gives only "a whole team, a year or two".

## What is not here

No trajectories, no scripts, no model calls. The post's own charts (line
history, PR and release timeline, interop surface, message intents, session
timelines) were read for their labels but are not reproduced. The figure HTML
lives with the article draft. The permission-matrix figure is a diagram of the
post's "protect the oracle from the agent" lesson and carries no numbers.
