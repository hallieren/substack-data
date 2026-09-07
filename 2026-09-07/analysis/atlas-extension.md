# Atlas extension, production increment (2026-09-07)

Pool 169 runs, 33 read (10 by me in full windows, 23 by sonnet subagents on
compact views with names and criteria checked by me; `coding-borrow.md`,
`coding-sample.md`). Offline atlas: the 9 rows of 08-20 / 08-21.

## Counts against the offline rows, from the 33 read

| offline row | runs matched |
|---|---|
| dismissed red evidence it had itself produced | 10 |
| wandered into archaeology until the budget died | 8 |
| committed to a fix design against an available signal | 3 |
| scoped out a visible sibling of the same bug | 2 |
| abandoned a validated fix for an unvalidated redesign | 1 |
| test tampering (edited or left files in the test tree) | 0 as named; see the new row, the behavior is not tampering |

Refinement to the archaeology row's definition: in 5 of the 8 budget deaths
read, the fix was already in place and validated before the wandering
started. The budget goes to post-fix probing, not to the bug.

## New rows (six columns, ch03 format)

| name | definition and criterion | representative traces | count | sev | suspected component |
|---|---|---|---|---|---|
| borrows the test tree for a scratch experiment, and the run ends before the restore | any write into the test tree during the run (harness TEST_PATH); harm = the write survives into the diff | 08-26/pico-004-r2, 09-04/pico-004-r2, 08-26/pico-016-r3 (harm); 08-26/pico-001-r4 (restored) | 10 of 169 attempted, 3 of 169 left files | sev-1 when left | the prompt already carries the rule; the harness enforces it only at the end; the budget cap ends runs with no cleanup turn. Lever candidates: gate, tool description |
| a declined or opinion-phrased request treated as a bug ticket | the issue was closed not planned; pico writes a patch without weighing the evidence to stop that its own tools surfaced (green suite, docs, its numbers, the reporter's hedge) | 09-03/xarray-11148-nofix-r1, r2; 09-03/pylint-10909-nofix-r3 | 20 of 20 no-fix runs | sev-2 for pico (a diff nobody merges), sev-1 for an agent that opens PRs | no escalation path exists in the prompt or the tools; lever candidates: prompt (a stop rule), a gate on submission. Not this cycle |

## This cycle's selection

Failure mode: borrows the test tree. Basis: sev-1 red line (jumps the queue),
10 of 169 frequency, lever clear (see `cycle.md`). Chosen lever: gate.
Evidence, not habit: the prompt lever was already pulled twice on this rule.
