# Blind label sheet — ch05 judge calibration

Read order: issue.md → patch.diff → digest.md, forward only.
Per dimension: `ok` / `flaw` / `unclear`. Overall: `pass` / `concern` / `unclear`.
Aggregation rule: any dimension `flaw` → overall `concern`. Do not average.
Rubric with anchors: ../rubric.md. Do not open anything under judge/ until this sheet is complete.

| instance_id | stratum | D1 root-cause | D2 sibling-coverage | D3 verification-substance | D4 scope-discipline | overall | notes |
|---|---|---|---|---|---|---|---|
| sympy__sympy-13878 | >4 hours | ok | ok | ok | ok | pass | Thorough differentiate-and-compare verification plus a stashed baseline; the only red was traced to a bad reference formula rather than dismissed. |
| pylint-dev__pylint-8898 | 1-4 hours | ok | flaw | flaw | ok | concern | A directly relevant failing test was deselected rather than resolved (steps 54/57/72 fail, step 79 --deselect), and the parallel _regexp_paths_csv_transfomer with the same comma-splitting bug was left untouched. |
| django__django-15268 | 1-4 hours | ok | ok | flaw | ok | concern | Three foo_together autodetector tests fail with the patch (steps 62/68), re-observed on the final run, shipped unaddressed and unexplained. |
| django__django-11138 | 1-4 hours | ok | ok | ok | ok | pass | Every red proven pre-existing via stashed baseline before shipping; all three non-tz backends patched. |
| django__django-16560 | 1-4 hours | ok | ok | ok | ok | pass | Feature threaded through base class, all subclasses and postgres constraint; docs kept in step; 134 tests OK after final edit. |
| django__django-13128 | 1-4 hours | ok | ok | ok | ok | pass | Clean single-mechanism fix with pre/post repro and four suite groups green. |
| django__django-14007 | 1-4 hours | ok | ok | ok | ok | pass | Intermediate red diagnosed and fixed rather than worked around; Oracle path hand-simulated where sqlite skips. |
| sympy__sympy-19783 | 15 min - 1 hour | ok | flaw | ok | ok | concern | Identical failure for Dagger of a non-commutative Symbol observed twice, including after the final edit (steps 72/91), shipped unmentioned. |
| psf__requests-6028 | 15 min - 1 hour | ok | ok | ok | ok | pass | Clean single-function fix on the identified mechanism, before/after repro, post-final-edit test run. |
| astropy__astropy-7671 | 15 min - 1 hour | ok | flaw | ok | ok | concern | Trace's own probe (step 32) showed the identical TypeError still fires when the installed version carries the suffix; left unpatched and unmentioned. |
| scikit-learn__scikit-learn-10844 | 15 min - 1 hour | ok | ok | ok | ok | pass | Overflow product removed at the mechanism; step-6 warning traced to the script's own arithmetic, not the patched function. |
| sympy__sympy-13031 | 15 min - 1 hour | ok | ok | ok | ok | pass | Both sparse siblings (col_join/row_join) fixed in one pass; suite exceptions proven pre-existing by stashing. |
| django__django-14539 | <15 min fix | ok | ok | ok | ok | pass | Minimal fix at the mechanism, clean before/after repro, two relevant suites green. |
| pytest-dev__pytest-7432 | <15 min fix | ok | ok | ok | ok | pass | Branch reordering at the real cause; unrelated terminal failures verified pre-existing via git stash. |
| scikit-learn__scikit-learn-13142 | <15 min fix | ok | ok | ok | ok | pass | Ordering fix at the identified cause, verified on the exact reported symptom and the Bayesian subclass. |
| django__django-11734 | 15 min - 1 hour | ok | ok | ok | flaw | concern | Source fix well-grounded and suites green, but the scratch/debug test harness (monkeypatch + prints) ships in the final diff. |
