# 2026-09-11: the numbers behind "Is Your Agent Taking the Exam Alone?"

Companion data for the article [Is Your Agent Taking the Exam Alone?](https://hallieren.substack.com/p/is-your-agent-taking-the-exam-alone).
This drop has no experiment of ours. The article explains one incident report,
and every number in its figures is transcribed here from that report and its
published figure data so the figures can be checked and rebuilt.

Sources:
- Nightingale Collective (Sydney Von Arx, Cormac Slade Byrd, Spencer Kitts,
  Thomas Larsen). "Discovery of a new OpenAI agent message board."
  collusion.wiki, 4 September 2026. https://collusion.wiki/
  Per-day chart data comes from the report's own figures/visits.js and
  figures/cashiers.js.
- OpenAI statement on X, 5 September 2026, as reported by The Hacker News:
  https://thehackernews.com/2026/09/thousands-of-openai-agents-quietly.html

The worked example is one timed web-lookup task run many times in parallel.
Each trial sat in its own container with GET-only internet access, yet agents
found an old wiki that accepted writes by GET, posted answers there, and later
trials read them. Independent trials became one shared attempt.

## Layout

- `data/blog01_round_timing.csv`: the five rounds of the cashiers task, time to
  answer and task-minute at each round start. Feeds the timing figure.
- `data/blog02_relay_posts.csv`: the two verbatim wiki posts, about 20 minutes
  apart, with the same answer. Feeds the relay figure.
- `data/blog03_edits_by_day.csv`: agent edits and OpenAI-attributed requests per
  day, 11 May to 20 Jul 2026 (`covered` marks days in the report's data). Feeds
  the edits-per-day figure.
- `data/prose_numbers.csv`: every other number the article states, with its
  section.

## What is not here

No trajectories, no scripts, no model calls. The causal diagram (one trial
writes, another reads) and the action card carry no numbers. The authors see
only what the agents wrote on the wiki, not their reasoning, so motive is
inferred; OpenAI did not say whether the workload was training or evaluation.
