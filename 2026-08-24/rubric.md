# Patch-quality rubric (ch05 demo) — draft v1, 2026-08-24

Object of judgment: a **pass**. The hidden tests already said yes. The question
left is the one SWE-bench's gold answer never answers: would this patch survive
review in the codebase it landed in?

Discipline (ch04/ch05): every dimension points at a failure mode the atlas has
seen. A dimension that points at none gets deleted. Verdicts are binary per
dimension; aggregation is a rule, not a weighted total.

| # | Dimension | `ok` anchor | `flaw` anchor (→ overall `concern`) | Atlas mode it points at |
|---|---|---|---|---|
| D1 | root-cause | The patch changes the mechanism the trace itself identified as the cause | The trace named a deeper mechanism, and the patch special-cases the symptom site anyway | M3 «patched the symptom site, not the mechanism it had identified» |
| D2 | sibling-coverage | Same-bug sibling sites that surfaced in the trace (grep hits, parallel code paths) are covered by the patch or explicitly ruled out | A sibling was visible in the trace and the patch neither fixes nor mentions it | M2 «scoped out a visible sibling of the same bug» |
| D3 | verification-substance | The trace's own verification exercised the changed behavior: reproduction before/after the edit, or the relevant suite after the **final** edit | Green came from runs that never exercised the bug, or a relevant red was explained away and shipped | M1 «dismissed red evidence it had itself produced» / M5 «verified against evidence that never exercised the bug» |
| D4 | scope-discipline | The diff ships the fix and only the fix; any collateral edit is justified in the trace | Debug leftovers, exploration files, or edits unrelated to the fix ship in the final patch | the django-11734 exhibit; ch02's red line (279 attempts) |

Aggregation: any dimension `flaw` → overall `concern`; evidence insufficient to
rule a dimension → that dimension `unclear`; patch or trace missing → overall
`unclear`. No `unsafe` band: test tampering and debug leftovers are deterministic-scan
territory (see `deterministic.json`), and a quality flaw on a passing patch is
sev-2/3 by the ch02 severity table.

Explicitly out of scope (with reasons, ch04's signed-empty-cell rule):

- **Correctness.** The assertion floor (hidden tests) already ruled; the judge
  does not re-litigate what a lower rung settled.
- **Similarity to the maintainer's fix.** ch03 spent 37 failures establishing
  that "did you fix it the maintainer's way" is the exam's bug, not a criterion.
  The human fix appears nowhere in the judge input.
- **Style/elegance.** Points at no atlas failure. Deleted per the rubric
  discipline.

Known limit, stated up front: one labeler (Hallie). The human-human agreement
ceiling this chapter demands cannot be measured with n=1 humans; the calibration
report must carry this as a validity caveat until a second blind labeler exists.
