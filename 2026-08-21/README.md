# 2026-08-21: pico's seed eval set (ch04 follow-along, coding domain)

Companion data for the article "如何建评估集 / How to Build an Eval Set".
Method: *AI Agent Evaluation* ch04, migrated per its migration box from the
support world to a coding agent. Input: the 2026-08-20 failure mode atlas
(8 agent-side modes over 107 sealed SWE-bench Verified failure trajectories,
see `../2026-08-20/` in this repo).

The move in one line: SWE-bench's 500 sealed worlds are kept as setups
(the expensive half of an agent case); its verdict source is replaced.
Every case's accept script derives from the issue text, never from the
maintainer's patch.

## Files

- `cases/pico-*.yaml`: 18 cases. 16 anchored in sealed trajectories
  (reproductions + variants), 2 forward-generated from the red line
  (tests read-only, doomed seed). 4 marked `holdout: true`.
- `build_cases.py`: emits the cases; every world_note cites sealed steps
  from `../2026-08-20/trace_review_form.csv`.
- `coverage.py` / `matrix.txt`: coverage matrix tool (failure mode ×
  severity × test-coverage state) and its output. 15/36 cells non-empty,
  all sev-1 rows non-zero.
- `annotation-bar.md`: rulings on all 21 empty cells ("fill" or
  "reasoned empty"), each awaiting the spec owner's countersign.
- `basis-register.md`: policy ledger P1-P5, per-case basis, and one
  label-expiry drill (loosen P2 → 5 sev-1 cases relabel).

## Axis migration

The book's persona axis (cooperative / angry / vague / multi) does not
travel. The coding equivalent used here is test-coverage state:

| state | the world's pressure |
|---|---|
| green | suite stays green under a correct fix; false comfort available |
| conflicting | a correct fix flips existing tests red; dismissal pressure |
| uncovered | nothing exercises the bug; phantom verification pressure |
| doomed | a seeded test cannot legitimately pass; red-line pressure |

## Status

Design artifact. Cases land on the schema and the matrix; wiring the
assertions into a runnable harness (accept scripts, gate checks, judge
calibration) is ch05/ch07 work and has not run yet. Nothing here is a
pass-rate claim.
