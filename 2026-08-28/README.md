# 2026-08-28 — Cost on the books (Chapter 9 demo)

Retrospective cost booking of the 2026-08-15 sealed SWE-bench Verified run
(pico + DeepSeek V4-Flash, 500 tasks). No new agent runs.

Source data: `../2026-08-16/runs/20260815-sealed/` (results.jsonl, report.json,
preds.jsonl, trajectory tarball) and `../2026-08-16/costs/` (billing CSVs).

- `analysis/analyze.py` — distribution (median/P95/max/mean), per-repo table,
  steps and context-token extraction from the trajectories.
- `analysis/steps_tokens.json` — per-trace {steps, ctx, out, cost, sec};
  steps = tool_call count in the stored traj.
- `analysis/sphinx7985_steps.txt` — the 130-step listing of the dearest trace.
- `analysis/sphinx7985_cats.json` — hand labels: locate 50 / verify 50 /
  edit 16 / answer-key hunt 10 (steps 16,21,22,23,31,36,39,48,53,113) / wrap 4.
- `analysis/build_figures.py` — renders the article figures from these files.

Headline numbers: median $0.0098, P95 $0.047, max $0.067; 24 traces above P95
sum $1.32 vs $1.20 for the 250 at/below median; above-P95 failure rate 58%
vs 21% overall; 18 runs killed at max_spend_tokens=8M, 8 of them resolved.
