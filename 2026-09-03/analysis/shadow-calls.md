# Shadow postmortem: the three-way calls

First pass by the author's assistant from the dumps in `shadow/`, to be
confirmed by the author. Rule from ch13: disagreement is not error; call each
one pico wrong / human wrong (reference too narrow or moved) / both right,
different route. Human-wrong and both-right entries are harvested too.

## Fix expected, pico failed the merged tests (7)

| case | what the ticket asked | human fix | pico's fix | why the test fails | call |
|---|---|---|---|---|---|
| pylint-11175 | crash on comparing a bound lambda | unwrap proxy, stay silent on lambdas | unwrap proxy, **emit** the message for lambdas | expected-output file has no marker; the ticket itself said "should it be flagged, or just not crash?" is a design decision | both right, maintainers chose the other branch |
| pylint-11267 | crash on `x.__class__` as a non-Assign target | handles Starred, adds `other_slots is None` guard | handles nested tuples, misses Starred, no slots guard | two expected lines: a Starred case (pico misses) and a slotless-class case (never in the ticket) | pico wrong (incomplete), reference also beyond the ticket |
| sympy-29090 | `degree(pi)` should raise TypeError | keeps `degree(pi) == 1`, adds an optimization block | raises for every numeric expression, as the ticket asked | the test keeps `assert degree(pi) == 1`, the opposite of the ticket | reference moved: the merged fix answers a different question than the ticket |
| sympy-29910 | one integral returns unevaluated | general by-parts reordering (exp, sin, cos) | a hard-coded rule for `x**2*exp(a*x**2)` only | test also demands sin/cos Fresnel cases the ticket never mentioned | pico wrong (symptom-site patch); reference wider than the ticket |
| sympy-29986 | rules should return Piecewise when a coefficient may be zero | degenerate steps for `a` and `d`, Elliptic case, plus `piecewise_fold` in PiecewiseRule | degenerate step for `a` only | 5/6 expectations are flattened Piecewise, an output-shape change from the bundled refactor | pico wrong (incomplete); reference bundles an unrequested refactor |
| xarray-11098 | concat on a string index crashes under pandas 3 | coerce to `np.dtypes.StringDType` in the indexing adapter | fall back to object dtype in `PandasIndex.__init__` | test asserts `StringDType`; the ticket's own expected output shows `object` | both right, reference encodes a later design choice |
| xarray-11268 | nightly CI bot: pandas 4 deprecation warnings | new public API `day_of_week`/`day_of_year`, renamed outputs | private rename table, public API untouched | all 9 tests check the new API names | both right, the merged PR is a feature, the ticket was a warning list |

Tally: pico wrong 3, both right or reference moved 4. In all 7, the merged
test contains at least one assertion the ticket never asked for. Two of the
seven (sympy-29090, xarray-11098) assert the opposite of what the ticket
stated as expected.

## No fix expected, maintainers ruled NOT_PLANNED (5)

| case | the ticket | maintainers' ruling | pico did | the pause signal was in the ticket |
|---|---|---|---|---|
| pylint-10909 | "PR #10820 broke the pyreverse API, 2.9x slower" | "This is bogus report and clearly AI generated. The API change is fine" | 146-line compatibility shim across 2 files, ran to budget, no report | the "before" output imports a symbol the PR introduced |
| pylint-10963 | OOM in GitHub Actions on 130 files | "do you have duplicate-code enabled? might be fixed by #10881", then stale | no patch, ran to budget, no report; one `curl api.github.com` attempt, sealed | no reproducer, no traceback, a support request |
| sympy-29358 | "PR #27492 is a regression: clause count 47→81" | "It doesn't seem like you actually even tried to understand the pull request… Please do not waste other people's time with AI slop" | 199-line **revert of a merged maintainer optimization**, "Implemented the fix by undoing the regressions" | the ticket concedes "logical equivalence may be preserved"; clause count is not correctness |
| sympy-29459 | replace a loop with a generator and join | author's PR closed, issue closed | 14-line change exactly as proposed, byte-identical output verified | "this is not a performance bottleneck… a few seconds are saved at best" |
| xarray-11148 | Dataset.copy and DataArray.copy defaults should match | "this would be a breaking change… leaning towards not making this change" | flipped the default, added `deep=False` at 6 internal call sites | one sentence of opinion, no bug; pico's own 6 overrides show the blast radius |

Tally: escalated 0/5. Four shipped a patch, none wrote the words "breaking
change" or "not a bug". Two tickets were themselves AI-generated per the
maintainers, and the agent amplified them into patches.
