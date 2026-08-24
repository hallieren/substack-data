# substack-data

Data, scripts, and full agent trajectories behind the [AI Agent Evaluation](https://hallieren.substack.com) Substack articles. Each dated directory is self-contained: its README explains the experiment, the layout, and how to reproduce the numbers.

## The series so far

1. [I Killed My Own 92.4%](https://hallieren.substack.com/p/i-killed-my-own-924)
2. [Pocket Eval](https://hallieren.substack.com/p/same-exam-three-times)
3. [What "Good" Looks Like for Your Agent](https://hallieren.substack.com/p/i-wrote-picos-first-spec)
4. [How to Analyze Failure Trajectories](https://hallieren.substack.com/p/how-to-analyze-failing-traces)
5. [How to Build an Eval Set](https://hallieren.substack.com/p/how-to-build-an-eval-set)
6. [How to Judge Without a Gold Answer](https://hallieren.substack.com/p/judging-without-a-gold-answer)

## Data drops

| Date | Article | Contents |
|---|---|---|
| [2026-08-24](2026-08-24/) | [How to Judge Without a Gold Answer](https://hallieren.substack.com/p/judging-without-a-gold-answer) | Judge calibration: deterministic scans over the 393 sealed passes, 4-question rubric, 16-case stratified sample, blind labels, k=3 judge verdicts, alignment report, disagreement triage |
| [2026-08-21](2026-08-21/) | [How to Build an Eval Set](https://hallieren.substack.com/p/how-to-build-an-eval-set) | pico's eval set: 18 case YAMLs reverse-generated from the failure atlas, coverage matrix (9 modes x 4 test-coverage states), annotation bar, policy basis register, build scripts |
| [2026-08-20](2026-08-20/) | [How to Analyze Failure Trajectories](https://hallieren.substack.com/p/how-to-analyze-failing-traces) | Error analysis of the 107 sealed fails: coding protocol, review form, adjudications, control-group rows, final failure atlas |
| [2026-08-18](2026-08-18/) | [Pocket Eval](https://hallieren.substack.com/p/same-exam-three-times) | Pocket eval rerun on Alexa for Shopping: 18 questions x 3 sweeps, raw records, verdicts |
| [2026-08-16](2026-08-16/) | [I Killed My Own 92.4%](https://hallieren.substack.com/p/i-killed-my-own-924) | SWE-bench Verified contamination audit: git-seal SOP, trajectory auditor, ground-truth adjudication method, 1,000 trajectories, both full-run results (92.4% invalidated / 78.6% sealed) |

[What "Good" Looks Like for Your Agent](https://hallieren.substack.com/p/i-wrote-picos-first-spec) has no data drop; its deliverable is pico's spec, quoted in full in the article.

License: see [LICENSE](LICENSE). Trajectories contain excerpts of open-source repositories (their upstream licenses apply).
