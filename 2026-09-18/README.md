# 2026-09-18: the numbers behind "How to Accept Work You Can't Read"

Companion data for the article [How to Accept Work You Can't Read](https://hallieren.substack.com/p/how-to-accept-work-you-cant-read).
This drop has no experiment of ours. The article explains one technical report,
and every number in its figures is transcribed here from that report so the
figures can be checked and rebuilt without reopening it.

Sources:
- Claude Science, R. Shuai, R. Badkundri, V. Fan, K. Fatras, L. Jarosch, A.
  Shanehsazzadeh. "Accelerating open-source biomolecular models with Claude."
  Anthropic technical report, 17 September 2026.
  https://www-cdn.anthropic.com/c03643714397d9d396fa1ce1794f5f9f7863a82c.pdf
- Anthropic. "How Claude is uplifting biomolecular modeling." 17 September 2026.
  https://www.anthropic.com/research/claude-uplifts-biomolecular-modeling
- Code: https://github.com/anthropics/uplifting-biomolecular-modeling

The worked example is the report's own optimization and evaluation setup. Two
supervisors who knew biomolecular modeling but had never written low-level GPU
code had Claude speed up more than 30 open-source protein structure models
along three stacked modes, Exact, Fast, and Big, each allowing one more kind of
change to how the program hands work to the GPU. Every promise gets a
program judge that sees only the two predicted structures, never the code:
a bit comparer for Exact, a spread ruler measured from the original model's own
run-to-run randomness for Fast and Big, and a lab-measured answer key for all
three. One judge did go red once, on a Protenix v1 run split across two GPUs,
and the report's own accuracy numbers show no measurable change across 1,925
test cases.

## Layout

- `data/blog01_speedup_modes.csv`: the three-mode matrix, what each mode may
  change, whether the predicted structure must be identical or only close, the
  average speed-up, and how many models each speed-up is averaged over. Feeds
  the modes-matrix figure.
- `data/blog04_protenix_dockcheck.csv`: the Protenix v1 Big-mode spread-ruler
  checks, structures outside the allowed spread of 40 against the limit of 8,
  across two failed checks and the pass after the fix. Feeds the threshold bar
  figure.
- `data/blog05_dockq_pass_rates.csv`: pass rate against the lab-measured answer
  key for the original and the three modes, over 1,925 test cases pooled across
  13 configurations. Feeds the accuracy bar figure.
- `data/prose_numbers.csv`: every other number the article states, with its
  section.

## What is not here

No trajectories, no scripts, no model calls. The judge-diagram figure (original
program and Claude's version each producing a prediction that only a program
judge reads) and the three-judges figure (what each judge sees and where its
standard comes from) are diagrams and carry no numbers beyond those above. The
figure HTML lives with the article draft. All runs are Anthropic's own
measurements; the report was not independently reproduced.
