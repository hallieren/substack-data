# 2026-09-03: production writes the exam (ch13 online eval, replay + shadow on pico)

Companion data for the article [How to Let Production Write Your Exam](https://hallieren.substack.com/p/how-to-let-production-write-your). Method: *AI Agent Evaluation* ch13, the evidence
ladder's first two rungs (replay, shadow) applied to pico, the minimal coding
agent of this series, with the 2026-08-26 harness pointed at real 2026
GitHub issues instead of cases we authored.

## Question and design

Last week's seed eval set passed 48/70 case-runs. Chapter 13 asks what that
is worth once the world writes the tickets. "Production traffic" here = every
issue created in 2026 and already closed in sympy, pylint, xarray, seaborn,
requests, flask (n = 453, fetched 2026-09-03, no filter on "looks like a
bug"). Two slices are replayed:

- 24 issues closed by a merged PR that ships a test (seed 13, stratified by
  repo). Reference = the maintainers' merged tests, established red→green on
  each world before pico runs. pico sees only the issue body, in a container
  cloned at the PR's merge-base, network off, git sealed.
- 5 issues the maintainers closed as NOT_PLANNED with a comment. Reference =
  that ruling: no change. Verdict = `escalated` (no patch + explicit no-fix
  report).

One run per issue (production serves each ticket once). Two fix worlds were
excluded before any run (`cases/<id>/reference.json` has the reason).

## Headline numbers

| slice | result |
|---|---|
| fix expected, 22 valid worlds | 15/22 pass the merged tests (68% ± 19%), $0.67 for all 27 runs |
| no fix expected, 5 | 0/5 escalated; 4 shipped a patch, 1 died on budget without a report |
| red lines (test files, config, stowaway files) | 0 hits in 27 runs |
| shadow, 7 disagreements with the human fix | 3 pico wrong, 4 both right / reference moved; all 7 merged tests assert something the ticket never asked |
| register (ch07 fidelity gap), 4 rows | 3 confirmed, 1 refuted (emulated timing) |
| wider suites on the 15 reference-green patches | 0 newly failing (up to 6,203 tests per world) |
| harvest, 10 cases × 3 | 1/30 pass; merged with the 08-26 run 49/100 (69% → 49%), see `analysis/after.md` |

## Layout

| Path | What it is |
|---|---|
| `fetch_issues.py` → `traffic/all.jsonl` | 453 closed 2026 issues with comments and closing PRs (GraphQL `closedByPullRequestsReferences`) |
| `select_traffic.py` → `traffic/selected.jsonl`, `analysis/selection.md` | the exclusion funnel, every reason counted |
| `distribution.py` → `analysis/distribution.md` | drift probe 1: eval set vs the stream, same features |
| `sample_traffic.py`, `sample_nofix.py` → `cases/<id>/` | issue.md (what pico sees), meta.json, test.patch, fix.patch (never shown to pico), ruling.md for no-fix cases |
| `worlds/Dockerfile`, `build_worlds.py` | one image per case, `pico-world:<id>`, repo cloned at the merge-base, test deps via pip |
| `verify_worlds.py` → `cases/<id>/reference.json` | pre-flight: FAIL_TO_PASS / PASS_TO_PASS per world, or the reason it is invalid |
| `harness/` | the 08-26 harness with three changes: image from meta, reference tests instead of accept.py, repeat defaults to 1 |
| `runs/replay/` | 27 runs: results.jsonl, trajs/ (pico-1 trajectories), world/ (patch, baseline/post failures, reference results), report.md |
| `runs/harvest/` | the 10 harvested cases × 3 |
| `shadow.py` → `analysis/shadow.md`, `analysis/shadow/<id>.md` | pico's patch beside the merged fix, per case |
| `analysis/shadow-calls.md` | the three-way postmortem calls |
| `register.py`, `wider.py` → `analysis/register.md`, `analysis/wider.md` | the ch07 register reconciled |
| `harvest_cases.py` → `harvest/pico-019..028.yaml`, `analysis/matrix-after.txt` | the harvested cases in the 08-21 schema, coverage matrix over 28 cases |
| `after.py` → `analysis/after.md` | the merged rate: 08-26's 70 runs + the harvest's 30 |

## Repro

```
python fetch_issues.py && python select_traffic.py && python distribution.py   # gh CLI, no model
python sample_traffic.py && python sample_nofix.py && python build_worlds.py    # docker
export PICO=/path/to/pico   # a pico checkout, see the root README
uv run --project "$PICO" python verify_worlds.py                           # no model
uv run --project "$PICO" --env-file "$PICO/.env" python harness/runner.py runs/replay --repeat 1
uv run --project "$PICO" python harness/report.py runs/replay
python shadow.py && python register.py && uv run --project "$PICO" python wider.py
```

## Registered caveats

- Worlds are `python:3.12-slim` + pip, not the repos' CI matrices. Base commit
  = the PR's merge-base (8 of 24 differed from GitHub's recorded baseRefOid).
- Verdict sources differ between the 08-26 half (accept.py from issue text,
  policy P1) and this half (merged tests, replay-rung policy); the merged rate
  in `after.md` mixes them and says so.
- The no-fix slice is 5 of 92 NOT_PLANNED issues; 0/5 is a reading of those
  five, not a rate for the 92.
- No judge this run: every assertion is deterministic. Model deepseek-v4-flash,
  pico at commit e874ab7, the same code as the 08-26 baseline.
- pylint-11267's reference test fails under the human fix too in this
  environment (CRLF file); it is kept as a fix case because FAIL_TO_PASS was
  still established, and flagged here.
