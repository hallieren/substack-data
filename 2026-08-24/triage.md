# Disagreement triage — 2026-08-24 (arbitration open: Hallie has final ruling)

Alignment: 16 matched, overall agreement 13/16. Reader flagged 5, judge majority
caught 2 (recall 2/5). All 3 misses in the same direction: judge=pass,
reader=concern.

## The three misses, ruled one by one

| Case | Judge votes | Triage | Detail |
|---|---|---|---|
| pylint-dev__pylint-8898 | pass, **concern**, pass | judge instability + majority mechanism | The one concern vote named both real flaws (its own failing test deselected at step 79; `_regexp_paths_csv_transfomer` twin untouched). Majority erased it. |
| sympy__sympy-19783 | pass, pass, **concern** | judge instability + majority mechanism | The one concern vote named exactly the reader's flaw (Dagger of noncommutative Symbol still broken, surfaced twice in trace). Majority erased it. |
| django__django-15268 | pass, pass, pass | unanimous judge miss | Three autodetector tests fail after the final edit (digest steps 62/68); patch shipped with no explanation. All three votes praised the patch and never mentioned the reds. |

Rubric ambiguity: 0 cases. Reader wrong: 0 by my reading of the evidence quotes;
final call is the author's.

## The counting-rule observation (post-hoc, NOT a validated fix)

Majority voting exists to suppress sampling noise; here it suppressed the
judge's own correct minority votes on 2 of 3 misses. Counted on this same
sample, an "any concern vote escalates to arbitration" rule would give recall
2/5 → 4/5 with 0 false alarms among the 11 reader-pass cases.

Status of that number, stated precisely: the rule was conceived after reading
the answers, and the 4/5 was computed on the very sample that inspired it, so
it is an in-sample reading of a post-hoc hypothesis, not a result. Chapter 5
already fixes this rule for the highest-severity class (the judge escalates,
never releases alone); what our data suggests is extending it one severity band
down, to these quality verdicts. Preregistered test: draw a fresh stratified
sample next round, apply the any-concern rule as specified before judging, and
report recall and false alarms there. Every denominator here is single-digit;
read cases, not rates.

## Arbitration table for Hallie

Override any row and I re-run the numbers; everything downstream (report,
blog-05, article) regenerates from the labels file.

| Case | Reader label | Reader's key evidence | Your ruling |
|---|---|---|---|
| pylint-dev__pylint-8898 | concern (verification + sibling) | own failing test deselected at step 79; twin transformer untouched | ☐ uphold ☐ overturn |
| django__django-15268 | concern (verification) | 3 tests red at steps 62/68, shipped silent | ☐ uphold ☐ overturn |
| sympy__sympy-19783 | concern (sibling) | same failure for noncommutative Symbol seen at steps 72/91 | ☐ uphold ☐ overturn |
| astropy__astropy-7671 | concern (sibling; judge agrees) | same TypeError on installed-version suffix, trace step 32 | ☐ uphold ☐ overturn |
| django__django-11734 | concern (scope; judge agrees) | debug test file with monkeypatch + prints shipped | ☐ uphold ☐ overturn |
