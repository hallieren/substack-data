# 2026-09-30: the numbers behind "Who Is Your Agent Building For?"

Companion data for the article [Who Is Your Agent Building For?](https://hallieren.substack.com/p/who-is-your-agent-building-for).
This drop has no experiment of ours. The article explains speculative reward
hacking, agents working for a grader they imagine rather than for the user, and
every number in its figures is transcribed here from the audit so the figures
can be checked and rebuilt without reopening it.

Sources:
- Hui Wen Goh, Jonas Mueller. "Coding Agents Build for the Grader They Imagine,
  Not the User: Speculative Reward Hacking in DeepSWE." Handshake AI Research,
  18 September 2026. https://joinhandshake.com/research/ai/deepswe-reward-hacking/
- Sample rollouts: https://github.com/Handshake-AI-Research/deepswe-samples

The worked example is GLM 5.3 on the Helm task helm-unified-manifest-stream,
whose requirement 3 is to keep multiple YAML documents in render order. The
agent tested its own implementation, confirmed the order was wrong, estimated
the expected score of fixing versus leaving it against hidden tests it had
never seen, first favored fixing, then 13 steps later added a risk that fixing
would break something else, kept the bug, and shipped it with a comment that
reads as if the order is preserved.

## Layout

- `data/blog01_render_order.csv`: requested order vs the agent's output on its
  own three-document test. Feeds figure 1, which relabels the documents as
  made 1st, 2nd, 3rd.
- `data/blog02_fix_or_leave.csv`: the two estimates quoted from the trajectory
  and the submitted patch. Feeds figure 2.
- `data/blog03_grader_talk_floors.csv`: per-model lower bounds for two
  different measures with different denominators, all rollouts (black bars)
  and full-reward rollouts only (blue bars). Feeds figure 3. Bars are drawn at
  the stated floor.
- `data/prose_numbers.csv`: every other number the article states, with its
  section in the source.

## What is not here

No trajectories, no scripts, no model calls. Figure 4 is a schematic two by two
grid (tests pass or fail, request done or not) and carries no numbers. The
audit counts speculative reward hacking only among full-reward rollouts and
gives no rate for runs whose guess was wrong. Rates come from manual reading
of reasoning traces; the source reports lower bounds, not exact values, and
gives no number for Claude Opus 5. The source is a company blog post, not a
peer-reviewed paper, and it tests none of its suggested mitigations.
