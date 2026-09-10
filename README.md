# substack-data

Data, scripts, and full agent trajectories behind the [AI Agent Evaluation](https://hallieren.substack.com) Substack articles. Each dated directory is self-contained: its README explains the experiment, the layout, and how to reproduce the numbers.

## Running the scripts

Analysis scripts are plain `python` from their drop's directory. Scripts that drive pico (runners, judges, world checks) import it, so they run inside pico's environment. Point `PICO` at a checkout of [pico](https://github.com/hallieren/pico) and run them through uv from anywhere:

```
export PICO=/path/to/pico
uv run --project "$PICO" --env-file "$PICO/.env" python <drop>/<script>.py ...
```

`$PICO/.env` holds the model settings (`MODEL_BASE_URL`, `MODEL_API_KEY`, `MODEL_NAME`); scripts marked "no model" do not need `--env-file`. Scripts that read the sealed SWE-bench trajectories expect the tarball in `2026-08-16/trajs/` extracted into `2026-08-16/runs/20260815-sealed/`.

## The series so far

1. [I Killed My Own 92.4%](https://hallieren.substack.com/p/i-killed-my-own-924)
2. [Pocket Eval](https://hallieren.substack.com/p/same-exam-three-times)
3. [What "Good" Looks Like for Your Agent](https://hallieren.substack.com/p/i-wrote-picos-first-spec)
4. [How to Analyze Failure Trajectories](https://hallieren.substack.com/p/how-to-analyze-failing-traces)
5. [How to Build an Eval Set](https://hallieren.substack.com/p/how-to-build-an-eval-set)
6. [How to Judge Without a Gold Answer](https://hallieren.substack.com/p/judging-without-a-gold-answer)
7. [How Many Runs Before You Believe an Eval Number?](https://hallieren.substack.com/p/how-many-runs-before-you-believe)
8. [How to Build an Exam Room Your Agent Can Smash](https://hallieren.substack.com/p/how-to-build-an-exam-room-your-agent)
9. [What Else Did Your Agent Change?](https://hallieren.substack.com/p/what-else-did-your-agent-change)
10. [How Much Does One Agent Task Really Cost?](https://hallieren.substack.com/p/how-much-does-one-agent-task-really)
11. [How to Evaluate Your Agent's Memory](https://hallieren.substack.com/p/how-to-evaluate-your-agents-memory)
12. [How to Evaluate a Subagent](https://hallieren.substack.com/p/how-to-evaluate-a-subagent)
13. [How Many Layers Does Your Agent Really Have?](https://hallieren.substack.com/p/how-many-layers-does-your-agent-really)
14. [How to Let Production Write Your Exam](https://hallieren.substack.com/p/how-to-let-production-write-your)
15. [What to Rerun After a One-Line Prompt Change](https://hallieren.substack.com/p/what-to-rerun-after-a-one-line-prompt)
16. [Which Lever Fixes Your Agent's Worst Failure?](https://hallieren.substack.com/p/which-lever-fixes-your-agents-worst)
17. [How to Run a Postmortem on Your Agent](https://hallieren.substack.com/p/how-to-run-a-postmortem-on-your-agent)
18. [Are You Scoring Your Agent's Brain or Its Shell?](https://hallieren.substack.com/p/are-you-scoring-your-agents-brain-or)

## Data drops

| Date | Article | Contents |
|---|---|---|
| [2026-09-09](2026-09-09/) | [Are You Scoring Your Agent's Brain or Its Shell?](https://hallieren.substack.com/p/are-you-scoring-your-agents-brain-or) | Paper explainer, no experiment of ours: every number behind the four figures transcribed from arXiv 2609.05663 (Table 3 volatility sextiles, capture gap and bracket, harness levers, three-model replay league), with the unit conversions the article uses |
| [2026-09-08](2026-09-08/) | [How to Run a Postmortem on Your Agent](https://hallieren.substack.com/p/how-to-run-a-postmortem-on-your-agent) | Postmortem on the 09-07 gated run that left a test file in its diff: all 116 tool calls of the run classified (zero model calls), first bad step and its secondary, diff list, layered interception tally over the 15 gated runs and the 15-run baseline, seven action items each naming equipment and an owner, the atlas row split, the ownership table and health check |
| [2026-09-07](2026-09-07/) | [Which Lever Fixes Your Agent's Worst Failure?](https://hallieren.substack.com/p/which-lever-fixes-your-agents-worst) | One improvement cycle on pico: failure mining over 169 stored runs (zero model calls, 33 read, atlas rows added), lever table recomputed for a four-tool agent, a test-tree write gate as the one lever, pre-registered rejection rule, paired 3 cases x 5 runs against the old version, gate log, two-part verification with intervals, cycle template and rollback |
| [2026-09-04](2026-09-04/) | [What to Rerun After a One-Line Prompt Change](https://hallieren.substack.com/p/what-to-rerun-after-a-one-line-prompt) | Release gate for the 09-02 system-prompt line: gate thresholds written before the arm ran, baseline 14 cases x 5 re-evaluated from the judge cache (zero new calls) vs variant 14 x 3, paired analysis with intervals, red-line and attack sets, gate config and verdict |
| [2026-09-03](2026-09-03/) | [How to Let Production Write Your Exam](https://hallieren.substack.com/p/how-to-let-production-write-your) | Online eval, replay and shadow rungs: 453 closed 2026 issues fetched from six repos, 24 replayed against the maintainers' merged tests (red-to-green verified worlds) plus 5 NOT_PLANNED issues expecting escalation, world builders, traffic samplers, harvested cases for the seed set |
| [2026-09-02](2026-09-02/) | [How Many Layers Does Your Agent Really Have?](https://hallieren.substack.com/p/how-many-layers-does-your-agent-really) | First red-team round on pico: 8 baits (4 intents x 2 carriers) x 5 runs inside the sealed 08-26 worlds, deterministic red lines, per-run cells (not_seen / breach / seal_stopped / declined), 11/40 breaches listed one by one, anti-injection follow-up round |
| [2026-09-01](2026-09-01/) | [How to Evaluate a Subagent](https://hallieren.substack.com/p/how-to-evaluate-a-subagent) | Three-arm reviewer admission exam over frozen sealed SWE-bench work: 30 resolved + 30 unresolved x 3 repeats per arm (report only / diff / diff in container with tools), 45 mismatch probes, all review rows, full reviewer traces, analysis script and numbers |
| [2026-08-31](2026-08-31/) | [How to Evaluate Your Agent's Memory](https://hallieren.substack.com/p/how-to-evaluate-your-agents-memory) | Cross-session memory eval of Alexa for Shopping: 4 fresh conversations, 29-question ask-and-record protocol, verbatim transcript (identifiers redacted), session-boundary screenshots, mechanism map (miswrite / forgetting / crosstalk / missed recall + consistency) |
| [2026-08-28](2026-08-28/) | [How Much Does One Agent Task Really Cost?](https://hallieren.substack.com/p/how-much-does-one-agent-task-really) | Retrospective cost booking of the sealed 500-task run, no new agent runs: per-trace steps, context tokens and dollars, median / P95 / max, per-repo table, the 130-step dearest trace hand-labeled step by step, figure builder |
| [2026-08-27](2026-08-27/) | [What Else Did Your Agent Change?](https://hallieren.substack.com/p/what-else-did-your-agent-change) | Retroactive side-effect audit of the 08-26 run: differ script over the 70 stored diffs ($0, zero model calls), gold-patch reference frame, 87 file lines / 19 undeclared / hand triage (16 legal, 1 docs rewrite, 2 stowaway files), 1 overturned verdict, new `no_stowaway_files` assertion |
| [2026-08-26](2026-08-26/) | [How to Build an Exam Room Your Agent Can Smash](https://hallieren.substack.com/p/how-to-build-an-exam-room-your-agent) | First full run of the eval set: 6-component harness (614 lines), 14 acceptance bundles derived from issue text only, world reset/seal preflight, 14 cases x 5 repeats ($2.27), 70 trajectories, layered report, fidelity gap register |
| [2026-08-25](2026-08-25/) | [How Many Runs Before You Believe an Eval Number?](https://hallieren.substack.com/p/how-many-runs-before-you-believe) | Judge votes extended from 3 to 5 on the frozen 16-case sample: votes 4 and 5 (identical inputs, same prompt hash), merge script, split-rate results |
| [2026-08-24](2026-08-24/) | [How to Judge Without a Gold Answer](https://hallieren.substack.com/p/judging-without-a-gold-answer) | Judge calibration: deterministic scans over the 393 sealed passes, 4-question rubric, 16-case stratified sample, blind labels, k=3 judge verdicts, alignment report, disagreement triage |
| [2026-08-21](2026-08-21/) | [How to Build an Eval Set](https://hallieren.substack.com/p/how-to-build-an-eval-set) | pico's eval set: 18 case YAMLs reverse-generated from the failure atlas, coverage matrix (9 modes x 4 test-coverage states), annotation bar, policy basis register, build scripts |
| [2026-08-20](2026-08-20/) | [How to Analyze Failure Trajectories](https://hallieren.substack.com/p/how-to-analyze-failing-traces) | Error analysis of the 107 sealed fails: coding protocol, review form, adjudications, control-group rows, final failure atlas |
| [2026-08-18](2026-08-18/) | [Pocket Eval](https://hallieren.substack.com/p/same-exam-three-times) | Pocket eval rerun on Alexa for Shopping: 18 questions x 3 sweeps, raw records, verdicts |
| [2026-08-16](2026-08-16/) | [I Killed My Own 92.4%](https://hallieren.substack.com/p/i-killed-my-own-924) | SWE-bench Verified contamination audit: git-seal SOP, trajectory auditor, ground-truth adjudication method, 1,000 trajectories, both full-run results (92.4% invalidated / 78.6% sealed) |

[What "Good" Looks Like for Your Agent](https://hallieren.substack.com/p/i-wrote-picos-first-spec) has no data drop; its deliverable is pico's spec, quoted in full in the article.

License: see [LICENSE](LICENSE). Trajectories contain excerpts of open-source repositories (their upstream licenses apply).
