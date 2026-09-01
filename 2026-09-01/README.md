# 2026-09-01: Three-arm reviewer admission exam (ch11)

Chapter 11 of [AI Agent Evaluation](https://github.com/hallieren/ai-agent-evaluation) executed as a subagent admission eval: before wiring a code-review subagent into pico, the reviewer sat an entrance exam over frozen work from the sealed SWE-bench Verified run. One reviewer (deepseek-v4-flash, same model as the implementer), three evidence contracts:

| Arm | Reviewer receives | Tools |
|---|---|---|
| A | issue + the implementing agent's final report | none |
| B | issue + the submitted diff | none |
| C | issue + diff, inside the sealed container with the patch applied | bash, read_file |

Sample: 30 resolved + 30 unresolved instances (unresolved drawn from the agent-side failure modes of [2026-08-20](../2026-08-20/); all 17 M1 and all 5 M5, stratified rest, seed 11), 3 repeats per arm. Plus 5 mismatch probes (issue from X, evidence from Y, same repo, both resolved; expected reject) × 3 arms × 3 repeats.

Headline: bad-fix approval A 75/90, B 77/81, C 69/90; probes rejected 45/45; good fixes wrongly rejected 0/90, 1/87, 3/90. Full numbers in `analysis.txt`.

## Files

| File | What it is |
|---|---|
| `reviews-main-ab.jsonl` | One row per review, arms A and B (verdict, confidence, reason, tool-call counts, usage, cost). Later rows for the same (instance, arm, repeat) supersede earlier ones (retries after empty-turn stalls). |
| `reviews-main-c.jsonl` | Same, arm C (container reviews). |
| `reviews-probes.jsonl` | The 45 mismatch-probe reviews (the arm-C rows with `git apply failed` errors are the abandoned first probe design; the later C rows use the unfixed-container design). |
| `sample-main.json`, `sample-probes.json` | The seeded samples. |
| `review_arms.py` | The experiment runner (lives in pico's repo under `bench/`; needs `swebench_mini.py` beside it, docker, and a model key). |
| `analyze.py`, `analysis.txt` | The analysis script and its output; every number in the article comes from here. |
| `pico-review-traces-20260901.tar.gz` | Full per-review traces (complete reviewer transcripts, including arm C's tool calls and the arm-A attempts to call tools that don't exist). |

## Method notes

- Ground truth is the official harness verdict from the sealed 20260815 run ([2026-08-16](../2026-08-16/)); the reviewer never sees the gold tests, mirroring a production reviewer's position.
- 12 of 540 main cells (all arm B, 7 instances) never produced a verdict: the model returned empty turns until the turn cap across three retry passes. They are excluded from rates and listed in `analysis.txt`.
- `evidence_tool_calls` counts bash/read_file calls in the trace. Arms A and B have no such tools, so nonzero values there are attempted calls that were refused.
- Costs use deepseek-v4-flash prices; the whole experiment (main + probes + pilot) cost about $2.30.
