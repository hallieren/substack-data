# ch05 demo evidence — judge calibration on the 393 sealed passes

Date: 2026-08-24. Written **before** any judge run and before blind labeling
(preregistration discipline). Data: `pico/bench/runs/20260815-verified-sealed`,
untouched since 8/15.

## Question

The sealed run's gold answer (hidden tests) ruled 393 patches correct. It rules
on exactly one property. "Would this patch survive review" has no gold answer.
This demo builds the chapter's ladder for that property and calibrates the judge
before trusting it. Judge scores are NOT folded into any total (calibrate first,
use later — ch06+ material).

## Pipeline (run order)

1. `scripts/deterministic_layer.py` — sink first: conservative scans over all
   393 pass patches (tests touched, debug leftovers, size stats). Offline,
   deterministic. Result: 1 flag (django-11734 shipped its exploration test
   file), 0 debug leftovers in source, sizes feed sampling.
2. `rubric.md` — 4 dimensions, each pointing at an atlas mode (M1/M2/M3/M5 +
   the 11734 exhibit). Accepted by Hallie before labeling; edits void
   everything downstream.
3. `scripts/make_sample.py` — 16-case sample, stratified by SWE-bench Verified
   human-time difficulty, hand-thickened at the hard end (>4h: 1/1, 1-4h: 6/20,
   15m-1h: 5/209, <15m: 3/163) + 1 enrichment case (the deterministic flag).
   Seeded, reproducible. Emits per-case issue/patch/trace-digest and
   `blind-sheet.md`.
4. Blind labels: per Hallie's instruction, drafted by a second-model reader
   (Claude, different family from the judge; two subagents, 8 cases each,
   evidence quote per dimension, `labels-group{A,B}.json`). Blindness held:
   nothing under `judge/` was read before labels were locked. Hallie arbitrates
   (`triage.md` has the table); any overturned label regenerates everything
   downstream.
5. `scripts/run_judge.py` — judge-patch-rubric, k=3 self-consistency, base =
   deepseek-v4-flash (deliberately the same base that wrote the patches; the
   alignment report is the instrument that measures self-preference, not a
   reason to assume it away).
6. `scripts/align.py` — layered disagreement by difficulty stratum +
   per-class recall + per-dimension disagreement → `alignment-report.md`.
7. Disagreement triage (rubric ambiguity / judge bias / human error) happens in
   the article, case by case.

## Preregistered readings and stop conditions

- Strata with single-digit denominators (>4h has n=1, and every stratum here is
  single-digit) are read case-by-case, never as percentages.
- The informative line is per-class recall, not raw disagreement (class
  imbalance: most passes will be human-`pass`).
- Enrichment caveat: the sample is a constructed distribution; any rate read
  off it answers "can the judge recognize this flaw class," not "how often will
  it miss in production."
- Validity: no human labeler this round; labels come from a second-model blind
  reader, so the report is judge-vs-reader, not judge-vs-human, and the
  human-human ceiling is unmeasured. The report and the article both say so.
  Prompt/rubric/base edits void the calibration.

## Run log

- 2026-08-24 run 1: all outputs empty; deepseek-v4-flash is a reasoning model
  and max_tokens=600 was consumed by thinking. Harness fix, wiped, reran.
- 2026-08-24 run 2: 48/48 calls, 8 outputs empty on hard cases (reasoning burned
  the full 8000). max_tokens raised to 24000; only the 8 empty calls reran. The
  judge prompt itself never changed (prompt_sha constant), so the calibration is
  not voided; this is harness repair, not judge editing.

## Preregistered follow-up (from triage, 2026-08-24)

The any-concern-vote-escalates counting rule is a post-hoc hypothesis born from
this round's disagreement reading (see `triage.md`). Next calibration round:
fresh stratified sample, rule fixed before any judging, report its recall and
false-alarm count out-of-sample. Until then the in-sample 4/5 carries no
evidential weight.

## What this demo does NOT do (parked)

- No judge scores in any aggregate number (ch06 gives intervals first).
- No second judge base, no prompt iteration loop (would need a second
  calibration round).
- No re-run of the 500; the sealed run stays sealed.
