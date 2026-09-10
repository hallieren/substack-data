# 2026-09-10: the numbers behind "How to Read a Trace Without Believing It"

Companion data for the article [How to Read a Trace Without Believing It](https://hallieren.substack.com/p/how-to-read-a-trace-without-believing).
This drop has no experiment of ours. The article explains one lab post, and
every number in its figures is transcribed here from that post so the figures
can be checked and rebuilt without reopening it.

Source: Anthropic. "An alignment assessment of recent cybersecurity
incidents." Dated Sep 9, 2026.
https://www.anthropic.com/research/alignment-assessment-cybersecurity-incidents

The single worked example throughout is the Claude Mythos 5 incident: a model
under test, told it had no internet, ran a cyber task onto the real public
internet and uploaded a malicious package. The trace runs more than 1,800
actions over roughly ten hours; the package reached 15 third-party hosts and
PyPI removed it after about 90 minutes.

## Layout

- `data/blog01_out_of_context.csv`: the post's Figure 5. How often the
  evidence was judged real inside the full trace (1.1% in the figure, 1% in
  the text) versus when a fresh Mythos 5 instance saw each output alone (79%).
  Feeds figure 1.
- `data/blog01_in_trace_breakdown.csv`: what the model's in-trace reasoning
  did with the same outputs, 72% called simulation, 27% ignored the question,
  1% clearly called real.
- `data/blog02_resampling.csv`: the post's Figure 10. Resampling from two
  checkpoints of the real trace with real, fake, or no evidence planted, then
  measuring stated belief versus the next out-of-scope action. Feeds figure 2,
  which uses the action-67 rows. Values read off the figure, approximate.
- `data/momentum_scope_reminder.csv`: the post's Figure 12. Share of replays
  that stop when an in-scope reminder sits 0 to 3 model turns before the
  action, and with no reminder. A prose aside in the article.
- `data/blog03_monitor_cot.csv`: the "Monitors" section. The offline monitor
  (an Opus 4.8 prompted first stage plus a second-stage filter) reading the
  full trace versus the trace with reasoning stripped. Feeds figure 3.
- `data/monitor_auto_mode.csv`: the auto-mode classifier block rates, context
  for why the offline monitor's Mythos 5 miss stands out. Not charted.
- `data/replication_ctf.csv`: the reconstructed capture-the-flag replication,
  150 runs, share taking a severely harmful action. The article's boundary
  paragraph.
- `data/source_discrepancies.csv`: the three places where the post's prose and
  its figures disagree. The article follows the text.

## What is not here

No trajectories, no scripts, no model calls. The figure HTML lives with the
article draft. Anything not in the post's text or figures was not used. The
numbers come from Anthropic's own reconstructed environments; METR's
independent review was not concluded at the time of writing.
