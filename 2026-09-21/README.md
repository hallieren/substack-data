# 2026-09-21: the numbers behind "Did Your Agent Run What You Approved?"

Companion data for the article [Did Your Agent Run What You Approved?](https://hallieren.substack.com/p/did-your-agent-run-what-you-approved).
This drop has no experiment of ours. The article explains one security paper,
and every number in its figures is transcribed here from that paper so the
figures can be checked and rebuilt without reopening it.

Source: Adithyan Arun Kumar. "Loopjacking: Hijacking Human-in-the-Loop
Approval." arXiv:2609.21081v1 [cs.CR], 17 September 2026, CC BY 4.0.
https://arxiv.org/abs/2609.21081, full text
https://arxiv.org/html/2609.21081, evidence archive
https://github.com/adithyan-ak/loopjacking.

The worked example is the paper's payment test on Agno AgentOS. A requester
who can start agent runs but not approve payments asks the agent to pay 20 to
a vendor; the admin approves that exact call. The requester then sends the
framework's own resume endpoint the same call ID with the amount, payee, and
status edited to 2,000 to an attacker-controlled sink, never passing back
through the model. The framework checks only that the run is approved and the
call ID matches, not that the arguments match what the admin saw, so it runs
the edited call. The same swap against the OpenAI Agents SDK, which
fingerprints the whole approved call, is refused. The author then ran the same
swap-or-mismatch test across four products and 23 tested releases.

## Layout

- `data/blog01_swimlane.csv`: the five-step trace, requester asks, framework
  pauses, admin approves 20, requester swaps in 2,000, framework runs it. Feeds
  the swimlane figure.
- `data/blog02_field_check.csv`: what the admin saw and what the requester sent
  back for each field, call ID, amount, payee, status, and whether the
  framework checked it. Feeds the field-comparison figure.
- `data/blog03_two_frameworks.csv`: the same swap against Agno AgentOS 3.0.9 and
  OpenAI Agents SDK 0.22.2, the question each asks before running, and the
  trial counts. Feeds the two-track figure.
- `data/blog04_release_results.csv`: releases tested per product, how many ran
  the unapproved action versus refused it, and the trial detail behind each
  count, with a total row reconciling to 23 tested and 20 versus 3. Feeds the
  release-squares figure.
- `data/blog06_probe_sequence.csv`: the paper's six-probe minimum test suite
  across the three approval stages, and what the tool's log should show for
  each probe. Feeds the probe-timeline figure.
- `data/prose_numbers.csv`: every other number the article states, with its
  section.

## What is not here

No trajectories, no scripts, no model calls. The two-links figure (the full
request must match what the human saw, and what the human approved must match
what the tool received) is a diagram of the paper's own framing and carries no
numbers beyond those above. The figure HTML lives with the article draft. This
is a purposive set of four products chosen by one researcher with no
independent reproduction yet; the paper makes no claim about how common the
underlying bug is.
