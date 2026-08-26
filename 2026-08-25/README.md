# 2026-08-25 · The judge's votes, extended from 3 to 5

Companion data for the post published alongside chapter 6 of
[AI Agent Evaluation](https://hallieren.github.io/ai-agent-evaluation/)
(variance, flip rate, confidence intervals).

The 2026-08-24 folder froze 16 coding-agent traces and had a model judge
(deepseek-v4-flash) vote 3 times per case. Chapter 6 sets the minimum readable
convention at 5 runs: 3 votes can only show *whether* a verdict flips, not how
often. This folder adds votes 4 and 5 on the identical frozen inputs.

## Files

- `judge-verdicts-45.jsonl` — votes 4 and 5, one row per case per run.
  Same judge prompt as 2026-08-24 (`prompt_sha 5f85d839c0b4`), same model,
  temperature 1.0, same sample under `../2026-08-24/sample/`.
- `stats_5votes.py` — merges the 3 published votes with these 2 and prints the
  split rates below. Run from anywhere: `python stats_5votes.py`.

## Results (5 votes per case)

- Inputs changed between votes: 0/16 (traces frozen, so every flip is the judge's).
- Overall verdict split: **2/16**, pylint-8898 (p,p,c,p,c) and sympy-19783 (p,p,c,p,c).
- At least one rubric dimension split: **3/16** (adds astropy-7671, whose
  root-cause dimension reads ok,flaw,ok,ok,flaw while its verdict stays concern ×5).
- 13/16 cases are unanimous across all 5 votes.
- Both split cases flip 2 votes in 5: a recurring minority reading, outvoted
  every time, not a one-off wobble.
