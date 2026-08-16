> **⚠️ RESULT INVALID — CONTAMINATED. DO NOT CITE.**
> Post-hoc audit (2026-08-15) found three leakage channels: git-history
> mining (the official prebuilt images retain future refs; 153 instances
> provably saw gold-patch content in git output before writing it), PyPI
> mining (`pip download` of future fixed releases; 122 of the 441 unsealed
> instances issued network commands), and future-test peeking (109
> instances). 298/500 instances tainted in total (`audit.json` holds the
> hard-evidence subset). The sealed re-run lives in
> `bench/runs/20260815-verified-sealed/`. This directory is retained as
> evidence for the postmortem:
> [docs/benchmarks/contamination-postmortem.md](../../../docs/benchmarks/contamination-postmortem.md).

# pico on SWE-bench Verified (full 500) — 2026-08-14/15

**462/500 resolved (92.4%)** · deepseek-v4-flash (V4-Flash-0731 via API alias) ·
**$5.06 total** ($0.0101/instance) · median 183s/instance · pass@1, no hints ·
graded by the official swebench 4.1.0 evaluation harness.

## Same-model reference points (different harnesses)

| Harness | Model | SWE-bench Verified | Source |
|---|---|---|---|
| **pico (this run)** | deepseek-v4-flash-0731 | **92.4%** | this repo, full artifacts |
| DeepSeek Harness "minimal mode" | V4-Flash-0731 | 79.0% | DeepSeek V4 technical report (vendor-self-reported) |
| mini-swe-agent v2.0.0 (high effort) | DeepSeek **V3.2** | 70.0% | swe-bench/experiments bash-only (different model — context only) |
| mini-swe-agent v1.17.1 | DeepSeek **V3.2** Reasoner | 60.0% | swe-bench/experiments bash-only (different model — context only) |

## Read the score with care

A 2026 model scoring 92.4% on a benchmark built from pre-2024 GitHub issues is
evidence about **model × harness × training data**, not model skill alone.
V4-Flash's training set plausibly contains many of these repos' fix commits;
DeepSeek's own model card dropped SWE-bench Verified in favor of
contamination-resistant benchmarks. We publish the number because it is what
the official evaluation produced under disclosed conditions — and we publish
every trajectory so you can judge what the model actually did.

## Network audit (disclosed in full)

The first pass ran instance containers with default network access. Auditing
our own trajectories caught the model fetching linked GitHub PR diffs / issue
threads on **59/500 instances** (e.g. curl-ing `pull/<n>.diff` for the very PR
that fixes the issue). Those 59 were reset and re-run with `--network none`
(now the runner default, recorded in each traj's `info.config.network`).
Sealed result: **56/59 resolved — identical to the unsealed count.** Sealed-run
network attempts: 2, both returned zero bytes (verified in trajectories). The
`.traj.json.tainted` files from the first pass are retained in the release
artifact for audit.

Clean-subset cross-check before the re-run: excluding all 59 tainted
instances, the remaining 441 resolved at 92.1% — within 0.3pp of the final
score.

## Harness disclosures (pico vs mini-swe-agent conventions)

- Four tools (bash, read_file, write_file, edit_file) vs bash-only
- Patch = `git diff` at loop end; no explicit submit command
- Tool output clip: 30,000 chars tail-keep (mini warns at 10,000)
- step/turn limit 250, bash timeout 60s (matching mini's swebench.yaml)
- Spend ceiling 8M tokens/instance (≈$0.10–0.15 at these prices; stricter than
  mini's $3) — hit by 5 instances; 0 hit the wall-clock stop
- Run-level operations: two DeepSeek API outages were survived by
  pause / drop-in-flight / resume (results ledger); 0 failed instances in the
  final record

## Per-repo results

astropy 18/22 · django 217/231 · matplotlib 32/34 · seaborn 2/2 · flask 1/1 ·
requests 4/8 · xarray 20/22 · pylint 9/10 · pytest 18/19 · scikit-learn 31/32 ·
sphinx 40/44 · sympy 70/75

Weakest: requests (4/8). The 38 unresolved instance ids are in
`report.json`; failure taxonomy from the trajectories is the next analysis
pass.

## Artifacts

- `report.json` — score, cost, per-repo, unresolved ids, statuses
- `eval_report.json` — resolved/unresolved id lists from the official harness
- `preds.jsonl`, `results.jsonl`, `metadata.yaml` — tracked in git
- `trajs/` (500 × `pico-1` format), `usage/` (per-request token log),
  `logs/` (official eval: patch.diff / report.json / test_output.txt per
  instance) — in the GitHub Release tarball (gitignored: too big for git)

Reproduce: [docs/benchmarks/swebench-verified-full.md](../../../docs/benchmarks/swebench-verified-full.md).
