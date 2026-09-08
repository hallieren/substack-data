# Quality ownership and the health check, pico (ch16 templates, filled)

pico is a one-person project. Every A below is the same name. The table is
still worth writing, for the reason the chapter gives: at one person quality
is self-evidently common property, and the table is what survives the second
person. It also makes the health check's first danger sign visible.

## Ownership table

R = does it, A = accountable, one name, C = consulted, I = informed

| Asset | Where it lives | R | A | C | I |
|---|---|---|---|---|---|
| The spec (intended use, action boundary, severity table) | `2026-08-21/cases/*.yaml` (assertions, severity_if_fail), `pico/bench/swebench_mini.py` SYSTEM (the two rules), the permission row in `2026-09-07/gate_variant.py` | Hallie Ren | Hallie Ren | | |
| Gold labels (the eval set and relabeling) | `2026-08-26/accept/<case>/accept.py`, written from issue text only (policy P1); `2026-08-26/issues/*.md` | Hallie Ren | Hallie Ren | | |
| The judge rubric | `judge-red-justification` in the 08-26 harness (`harness/judge`), its votes in each run's `judge-cache.json` | Hallie Ren | Hallie Ren | | |
| The red-line veto | `2026-09-04/gate.yaml` sev-1 rows (test files edited, config edited, undeclared new files); no is no | Hallie Ren | Hallie Ren | | |

## Health check, answered from the records (2026-09-08)

Habit one, read traces every week.

- Trace-reading record for each of the last four weeks: 08-15 (contamination audit of the trajectories, `pico` bench commits), 08-20 (107 sealed-run failures read, `trace_review_form.csv`, the atlas's 9 rows), 08-27 (side-effect audit), 09-03 and 09-07 (replay and shadow reading; 33 of 169 read, `coding-borrow.md`, `coding-sample.md`). Yes, four of four weeks, each with an atlas or case output.
- Rotation covers everyone: one person, so trivially yes and meaningless.
- A path problem read out of a `pass` trace this month: yes, 08-26/pico-001-r4 (pass, borrowed and restored) and gate/pico-004-r3 (pass, wrote and restored) are both in `coding-borrow.md` and `verify.md`.

Habit two, every incident enters the eval set.

- Postmortem record for the most recent incident: `postmortem.md`, this folder.
- The case it produced entered the eval set: not yet (A3 open).
- Action items point at equipment with owner and deadline: seven of seven.

Habit three, a case before the code.

- Last three feature reviews had cases at review time: the 09-02 prompt line (attack set 4 x 5 first), the 09-07 gate (cases and rejection rule preregistered 06:38, arm 06:38). Two of two changes reviewed; there is no third.
- A feature held out for "no case": no instance on record.

Infrastructure liveness.

- People who added a case in the last month: **1** (`pico` git log since 08-08, one author; `substack-data` case additions 09-03, one author). The template calls one or fewer a danger sign. It is the honest reading of a solo project.
- The gate's most recent interception: 2026-09-07 06:55:38, `gate-log.jsonl`, pico-004-r3, a `cp` back into the test tree.
- People named on the RACI know it: yes, by construction.

Danger signs counted: 1. The first one to fix: not fixable by process on a one-person project; the fix is the second person, and this table is what they receive. Owner: Hallie Ren.
