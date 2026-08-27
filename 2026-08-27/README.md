# 2026-08-27 — the side-effect audit (ch08)

The ch08 question, asked retroactively of the 08-26 run: besides what should
have changed, what else did? No new agent runs; the runner had already saved
a full-workspace `git add -N . && git diff` at the end of every trace. Total
model spend of this audit: $0.

## Contents

- `audit/differ.py` — replays the 70 stored diffs, classifies every changed
  file against the maintainer fix's home files (SWE-bench gold patches,
  `audit/gold_patches.json`, fetched 2026-08-27), writes `audit.json` and
  `findings.md`.
- `audit/findings.md` — the 19 undeclared changed-file lines.
- `audit/triage.md` — hand triage of the 19: 16 legal alternative fix
  sites, 1 out-of-scope docs rewrite, 2 stowaway files, 1 overturned
  verdict (pico-016-r3).
- `assertions_ch08.py` — `no_stowaway_files`, the finding converted into a
  standing deterministic sentry for future runs.

## Registered limits

- The gold-file reference frame is a triage aid, not the case contract; the
  cases never declared file scope, so strictly all 87 lines are undeclared.
- The stored diff only sees `/testbed`; scratch files in `/tmp` are
  invisible by design (and harmless, they die with the container).
- New-file detection rides on `git add -N .` in the runner; a runner
  without it would silently miss every stowaway.
