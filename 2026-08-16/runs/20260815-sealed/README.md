# pico on SWE-bench Verified (full 500, sealed) — 2026-08-15

**393/500 resolved (78.6%)** · deepseek-v4-flash (V4-Flash-0731 via API alias) ·
**$7.55 total** ($0.0151/instance) · median 211s/instance · pass@1, no hints ·
**git history sealed + network sealed, audit clean** · graded by the official
swebench 4.1.0 evaluation harness.

## Why this run exists

Our previous run ([20260814-verified](../20260814-verified/)) scored 92.4% —
and our own audit invalidated it: the official prebuilt images retain the
repo's *future* git history, and with network access the model also mined
PyPI for future fixed releases. 298/500 instances were tainted. Full story:
[contamination postmortem](../../../docs/benchmarks/contamination-postmortem.md).

This run seals both channels and re-runs all 500 from scratch:

- **Git seal (timesafe-v1)** — per-container replication of the official
  `git_clone_timesafe` sanitization (keep one branch at HEAD, delete every
  other ref, expire reflog, `git gc --prune=now`, hard-verify ≤1 post-base
  commit). Fail-closed: seal failure ⇒ no agent run. 0 seal failures.
- **Network seal** — `--network none` on every instance container.
- **Automated audit** — `bench/audit_trajs.py` over all 500 trajectories:
  28 flags, **all adjudicated false-positive with ground-truth evidence**
  (upstream-clone `git grep` at base_commit; `merge-base --is-ancestor` for
  cited shas): [audit.json](audit.json),
  [audit_adjudication.json](audit_adjudication.json). **0 genuine leaks.**
  The same detector holds 223/500 sensitivity on the contaminated run.

## Same-model reference points

| Harness | Model | SWE-bench Verified | Source |
|---|---|---|---|
| **pico, sealed (this run)** | deepseek-v4-flash-0731 | **78.6%** | this repo, full artifacts |
| DeepSeek Harness "minimal mode" | V4-Flash-0731 | 79.0 (tech report) / 80.6 (model card, instruct) | vendor-self-reported |
| pico, unsealed | deepseek-v4-flash-0731 | ~~92.4%~~ **invalid** | 298/500 tainted — see postmortem |
| mini-swe-agent v2.0.0 (high effort) | DeepSeek **V3.2** | 70.0% | different model — context only |

The sealed pico number lands within 2pp of DeepSeek's own self-report for the
same model. The 13.8pp gap between our unsealed and sealed runs is the
measured value of runtime oracle access (git future history + PyPI + future
tests) for this model on this benchmark.

## Read the score with care

Weights contamination remains: a 2026 model on pre-2024 GitHub issues has
plausibly trained on many of these fix commits. Sealing removes *runtime*
oracles only; it cannot remove what the model memorized. This caveat applies
equally to every published number on this benchmark. It is why all 500
trajectories ship with the score.

## Harness disclosures (pico vs mini-swe-agent conventions)

- Four tools (bash, read_file, write_file, edit_file) vs bash-only
- Patch = `git add -N . && git diff` at loop end (includes files the model
  created); no explicit submit command; scratch-hygiene prompt rule
- Tool output clip: 30,000 chars tail-keep · step limit 250 · bash timeout 60s
- Spend ceiling 8M tokens/instance — hit by 18 instances; 0 wall-clock stops
- 1 empty-patch instance (django-13513), counted unresolved
- Run ops: 2 transient API ConnectErrors, rows deleted + re-run sealed;
  0 failures in the final ledger

## Per-repo results

astropy 15/22 · django 188/230 · flask 1/1 · matplotlib 25/34 · seaborn 1/2 ·
requests 7/8 · xarray 18/22 · pylint 6/10 · pytest 16/19 · scikit-learn 29/32 ·
sphinx 28/44 · sympy 59/75

Biggest sealed-vs-unsealed drops: sphinx 40→28, sympy 70→59, django 217→188 —
the repos where git archaeology was paying off most.

## Artifacts

- `report.json` / `eval_report.json` / `harness_summary.json` — score, cost,
  statuses, resolved/unresolved ids (incl. `empty_patch_ids`)
- `audit.json` + `audit_adjudication.json` — every flag and its evidence
- `preds.jsonl`, `results.jsonl`, `metadata.yaml` — tracked in git
- `trajs/` (500 × `pico-1`), `usage/` (per-request tokens), `logs/` (official
  eval artifacts per instance) — in the release tarball (gitignored)

Reproduce: [docs/benchmarks/swebench-verified-full.md](../../../docs/benchmarks/swebench-verified-full.md).
