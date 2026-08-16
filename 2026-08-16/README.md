# I Killed My Own 92.4% — SWE-bench Verified contamination audit

Data, scripts, and all 1,000 trajectories behind the article. Everything here is enough to (a) read the evidence yourself and (b) re-run the whole experiment.

Article: (link added after publication)

## TL;DR

| Run | Score | Status |
|---|---|---|
| pico + DeepSeek V4-Flash, unsealed (2026-08-14) | **92.4%** (462/500) | invalidated by my own trajectory audit |
| pico + DeepSeek V4-Flash, sealed (2026-08-15) | **78.6%** (393/500) | official result |
| DeepSeek model card, same model | [80.6%](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) | vendor-reported |

298 of 500 tasks had at least one runtime leak channel open in the default evaluation environment: future git history inside the container, future package versions over the network, or a preview of the grading tests via the same git channel. Sealing all of them moved the score by 13.8 points, and every lost task came from the tainted set (281→217 resolved) while the clean set barely moved (181→176).

## The pitfall is still live

This is not a historical bug report:

- The official **prebuilt Docker images** on Docker Hub predate the upstream sanitization fix (`git_clone_timesafe` in swebench main, `image_builder/docker_utils.py`). Pulling them today gives you containers whose git history still contains the fix commits for the very bugs being evaluated.
- [SWE-bench issue #465](https://github.com/SWE-bench/SWE-bench/issues/465) (repo state leaks the solution) is **still open** at the time of writing.
- **mini-swe-agent's default flow does not sanitize** the container either.

If you run SWE-bench Verified today with default images and no seal, you are running the contaminated experiment, whether or not your model takes the bait.

## SOP 1 — seal the git history (copy-paste ready)

Run this inside each task container before the agent starts, passing the task's `base_commit` as `$1`. Fail closed: if the seal cannot verify, do not run the agent.

```bash
set -euo pipefail
cd /testbed
TARGET_TIMESTAMP=$(git show -s --format=%ct "$1")
git checkout -q -B pico-base
git for-each-ref --format='%(refname)' | grep -v '^refs/heads/pico-base$' \
  | while read -r ref; do git update-ref -d "$ref"; done
for rm in $(git remote); do git remote remove "$rm"; done
rm -f .git/FETCH_HEAD .git/ORIG_HEAD
git reflog expire --expire=now --all
git gc --prune=now --quiet
AFTER=$((TARGET_TIMESTAMP + 1))
FUTURE=$(git rev-list --all --after="@$AFTER" --count)
[ "$FUTURE" -le 1 ] || { echo "SEAL FAILED: $FUTURE post-base commits remain"; exit 1; }
if [ "$FUTURE" -eq 1 ]; then
  [ "$(git rev-list --all --after="@$AFTER")" = "$(git rev-parse HEAD)" ] \
    || { echo "SEAL FAILED: surviving post-base commit is not HEAD"; exit 1; }
fi
echo "sealed: $(git rev-list --all --count) commits reachable"
```

Notes that cost me time:

- Anchor the timestamp to the dataset's `base_commit`, **not** to HEAD: every prebuilt image carries one post-base "SWE-bench" environment-setup commit at HEAD. That is why the gate is `FUTURE <= 1` with an identity check, not `== 0`.
- `git gc` on the big repos (django, sympy) takes minutes under emulation; give it a generous timeout.
- Also run the container with `--network none`. Browsing is not the only network channel: `pip download <pkg>==<future-version>` hands the model the fixed source code.

The seal ships as `GIT_SEAL` in [`scripts/swebench_mini.py`](scripts/swebench_mini.py) (search for `GIT_SEAL`), invoked per container with the verification treated as a hard precondition.

## SOP 2 — audit the trajectories

```bash
python scripts/audit_trajs.py <run_dir>                       # fetches gold/test patches from HF
python scripts/audit_trajs.py <run_dir> gold.json tests.json  # offline, with local patch dumps
```

`<run_dir>` must contain `trajs/*.traj.json`. The auditor writes `<run_dir>/audit.json` and exits 1 if anything is flagged. It looks for:

- git-history mining commands (`log --all`, `show`, `rev-list`, `describe`, `name-rev`, …) and gold-patch content appearing in their output,
- previews of the grading test files before evaluation,
- network fetch commands (curl/wget/pip download).

## SOP 3 — adjudicate flags against ground truth

**A flag is a hypothesis, not a verdict.** Every flag needs a ground-truth check against the real upstream repository:

```bash
# One-time, per repository:
git clone --bare https://github.com/<org>/<repo>.git gt/<repo>.git

# Was the "leaked" line already in the tree at base? (pre-existing code)
git -C gt/<repo>.git grep -F "<flagged added line>" <base_commit> -- .

# Is the suspect commit past, not future? (ancestry check)
git -C gt/<repo>.git merge-base --is-ancestor <suspect_commit> <base_commit> && echo "past: benign"
```

Clone the full repo, not `--filter=blob:none`: a partial clone turns every `git grep` into a network fetch and the adjudication crawls.

## False-positive taxonomy

All 28 flags on my sealed run fell into these four classes (full evidence in [`runs/20260815-sealed/audit_adjudication.json`](runs/20260815-sealed/audit_adjudication.json)):

1. **Pre-existing code.** The gold patch moves or duplicates code that already exists at `base_commit`; the auditor sees "gold content" in git output that was legitimately there all along. Settled by `git grep -F` at base.
2. **The model's own edits echoed back.** `git diff` / `git status` / `git blame` ("Not Committed Yet") replay the model's in-progress patch; if the model independently converged on gold-like lines, they look leaked. Settled by tracking write order: content the model emitted before it appeared in git output is the model's own.
3. **Environment-commit dates.** Each image carries one post-base "SWE-bench" setup commit; its date (2025/2026) trips naive future-date detectors. Settled by learning the env commit hash per container and exempting it.
4. **Revert-style fixes.** The gold patch re-adds code that existed *before* base and was later removed; the "future" line has an ancestor in the past. This is the scariest-looking class and the reason the ancestry check exists.

## Repo layout

```
2026-08-16/
  README.md                  ← you are here
  scripts/
    swebench_mini.py         ← harness incl. GIT_SEAL (timesafe-v1) + submission capture
    audit_trajs.py           ← trajectory auditor (SOP 2)
    fetch_verified.py        ← downloads SWE-bench Verified metadata incl. base_commit
    instances_verified.json  ← the 500 instances as used (with base_commit)
  runs/
    20260814-unsealed/       ← invalidated run: preds, results, eval report, audit, tainted ids
    20260815-sealed/         ← official run: + audit adjudication, harness/token summary
  trajs/
    pico-swebench-verified-20260814.tar.gz          ← 500 trajectories + per-request usage + eval logs
    pico-swebench-verified-sealed-20260815.tar.gz   ← same for the sealed run
    exhibits/                ← unpacked star exhibits (see below)
  analysis/
    tainted_union_ids.json   ← the 298-task tainted set (union of the two files below)
    git_tainted_ids.json     ← 228 instances with the git-history channel open in the container
    deep_audit.json          ← per-instance mining-evidence counts (git/test/network oracles)
    difficulty.json          ← SWE-bench Verified difficulty annotation per instance
    real_suspects.json       ← the 7 scariest sealed-run flags (all adjudicated false positive)
  costs/                     ← DeepSeek billing-console exports for both run days: hourly token
                               amounts by type (cache hit / cache miss / output, with unit prices)
                               and hourly USD cost. Day totals include smoke tests, so they sit
                               slightly above the per-run figures ($5.06 unsealed, $7.55 sealed).
  figures/                   ← the seven article figures
```

### Exhibits

- `pylint-dev__pylint-4551.unsealed.traj.json` — the four-command crime scene from the article: `git log --all -S`, `git show <fix>`, `git merge-base --is-ancestor <fix> HEAD` (the model confirms it is copying from the future), then six edits landing 84 gold lines verbatim.
- `astropy__astropy-13398.unsealed.traj.json`, `django__django-11885.unsealed.traj.json` — the two heaviest git-oracle miners by evidence count.
- `pylint-dev__pylint-4551.sealed.traj.json` — the same task after sealing: the mining attempts return nothing and the model has to work.

## Reproduce from scratch

```bash
python scripts/fetch_verified.py                      # dataset metadata → instances_verified.json
export MODEL_NAME=deepseek-v4-flash                   # plus your provider's API key env var
python scripts/swebench_mini.py                       # runs all 500 sealed tasks → preds.jsonl
python -m swebench.harness.run_evaluation \
  --dataset_name princeton-nlp/SWE-bench_Verified \
  --predictions_path preds.jsonl --run_id my-rerun    # official grading (swebench 4.1.0)
python scripts/audit_trajs.py <run_dir>               # then adjudicate any flags (SOP 3)
```

The harness needs Docker with the SWE-bench Verified images available locally, an arm64/amd64 host, and roughly $8 of API spend at current DeepSeek pricing. Compare your `results.jsonl` against `runs/20260815-sealed/`.

## External references

- SWE-bench repo-state leak: [SWE-bench/SWE-bench#465](https://github.com/SWE-bench/SWE-bench/issues/465) (open at time of writing)
- Upstream fix (not in prebuilt images): `git_clone_timesafe`, swebench main, `image_builder/docker_utils.py`
- DebugML, [Finding Widespread Cheating on Popular Agent Benchmarks](https://debugml.github.io/cheating-agents/) — independent discovery of the same git-mining behavior across scaffolds
- Same class of issue in SWE-bench Pro: [scaleapi/SWE-bench_Pro-os#93](https://github.com/scaleapi/SWE-bench_Pro-os/issues/93)
- Official DeepSeek V4-Flash score: [HF model card](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash)

## One caveat that no seal removes

Weight memory. These bugs and their fixes are public GitHub history and current models likely saw them in training. The seal removes the open-book channels at run time; it cannot remove what the model memorized. That caveat applies equally to every number on every SWE-bench leaderboard, which is why the trajectories are published next to the score.
