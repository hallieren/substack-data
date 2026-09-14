# 2026-09-14: edit anchors, or does your agent's edit fail loud or silent?

Companion data for the article "Does Your Agent's Edit Fail Loud or Silent?".
The article pairs one paper with one audit of our own.

The paper: Asaad Althoubi, "Look Before You Leap: Pre-Action Verification for
LLM Agents", arXiv 2609.11957. Its Table 4 shows that when a file is shifted
or reindented before an edit is applied, location-anchored formats (line
ranges, whole function by name) misapply silently (99.1% and 12.7%) while
content-anchored formats (search/replace, unified diff) either land or refuse.
The paper's edits are synthesized, and it leaves open how often a real agent
meets a shifted file.

The audit: pico's sealed SWE-bench Verified run of 2026-08-15 (500
trajectories, one model), read back with zero model calls, asking how often
the agent edits a file its own earlier edits have already shifted, and what a
refusal from a content-anchored tool looks like in practice.

## Question

How often does a real coding agent issue an edit against a file whose line
numbers it has itself moved, and when a content-anchored tool refuses an edit,
does the agent recover?

## Method

`edit_anchors.py` walks every `trajs/*.traj.json`, finds every `edit_file`
call, and keeps a per-file running total of the net line-count change from the
agent's own successful edits (a `write_file` resets it). An edit issued while
that total is nonzero is an edit a line-anchored tool would have placed wrong
unless the agent re-read the file first. A refusal is a tool result matching
`not found in` or `appears N times in`, the two errors pico's `edit_file`
raises (it replaces one exact occurrence of `old`).

For each refusal the script records what the agent had done to that file
before, its next call, whether it looked at the file within two calls, and
whether a later `edit_file` on the same path succeeded.

## Results (`data/results.json`)

| Measure | Value |
|---|---|
| Trajectories | 500 (498 use edit_file) |
| edit_file calls | 1,252 |
| On a file the agent had already written | 631 |
| After the agent's own edits changed the file's line count | 473 (37.8%) |
| Median absolute shift at those edits | 6 lines (max 116) |
| Shifted by 5+ lines / 20+ lines | 267 / 77 |
| Refusals | 10 (0.8% per edit): 5 ambiguous, 5 not found |
| Refusals followed by a successful edit_file on the same path | 9 |
| Refusals recovered by any route | 10 |

All 473 shifted edits landed, because pico's tool anchors on content.

## Layout

- `edit_anchors.py`: the audit, no model. `python edit_anchors.py <run_dir>`
  where `<run_dir>` holds `trajs/*.traj.json` (default
  `../2026-08-16/runs/20260815-sealed`, extract the tarball there first).
- `data/results.json`: the totals above.
- `data/refusals.csv`: one row per refusal, with instance, call index, path,
  reason, prior writes and looks at the same file, the agent's own line shift
  at that point, next call, and recovery flags. The article's figure 4 is
  django-12754, calls 35 and 36.
- `data/shifts.csv`: one row per edit issued after an own-edit shift, with the
  net shift in lines.

## Boundary

One model, one benchmark, one run. Ten refusals show what recovery looks like
and do not support a rate with a useful interval. The 473 count is a
counterfactual: a line-anchored tool that returns the updated file after every
edit would force the re-read that makes the shift harmless. The paper's 99.1%
is a stress-test rate, not a field rate.
