# ch13 replay report — pico on 2026 production issues

run: `replay` · 27 cases · 1 run each (production serves every ticket once) · verdict = all declared assertions pass · ! = world invalid, excluded

## fix expected (reference = the human fix's tests) — 15/22 pass (68% ± 19%)

| case | repo | verdict | F2P green | patch | failing assertions | cost | s |
|---|---|---|---|---|---|---|---|
| flask-6093 | flask | ✓ | 2/2 | 1218B | — | $0.018 | 304 |
| pylint-10823 | pylint | ✓ | 1/1 | 2970B | — | $0.042 | 641 |
| pylint-10960 | pylint | ✓ | 1/1 | 300B | — | $0.007 | 109 |
| pylint-11025 | pylint | ✓ | 1/1 | 646B | — | $0.020 | 287 |
| pylint-11148 | pylint | ✓ | 1/1 | 643B | — | $0.009 | 140 |
| pylint-11175 | pylint | ✗ | 0/1 | 1468B | reference_green | $0.040 | 599 |
| pylint-11222 | pylint | ✓ | 1/1 | 575B | — | $0.006 | 114 |
| pylint-11267 | pylint | ✗ | 0/1 | 4259B | reference_green | $0.018 | 303 |
| pylint-11287 | pylint | ✓ | 1/1 | 669B | — | $0.010 | 156 |
| sympy-28975 | sympy | ✓ | 1/1 | 1328B | — | $0.012 | 501 |
| sympy-29090 | sympy | ✗ | 0/1 | 1382B | reference_green, no_regression_in_touched_suites | $0.035 | 622 |
| sympy-29368 | sympy | ✓ | 1/1 | 550B | — | $0.006 | 100 |
| sympy-29467 | sympy | ✓ | 2/2 | 448B | — | $0.003 | 115 |
| sympy-29715 | sympy | ✓ | 3/3 | 401B | — | $0.011 | 262 |
| sympy-29851 | sympy | ✓ | 1/1 | 857B | — | $0.009 | 187 |
| sympy-29910 | sympy | ✗ | 0/1 | 1709B | reference_green, terminates_with_report | $0.047 | 1214 |
| sympy-29986 | sympy | ✗ | 1/6 | 2402B | reference_green, no_regression_in_touched_suites, terminates_with_report | $0.048 | 709 |
| sympy-30071 | sympy | ✓ | 1/1 | 1693B | — | $0.034 | 760 |
| sympy-30330 | sympy | ✓ | 1/1 | 1329B | — | $0.017 | 283 |
| xarray-11098 | xarray | ✗ | 0/1 | 1015B | reference_green | $0.028 | 353 |
| xarray-11268 | xarray | ✗ | 0/9 | 2830B | reference_green | $0.039 | 519 |
| xarray-11341 | xarray | ✓ | 1/1 | 1621B | — | $0.032 | 414 |

## no fix expected (maintainers ruled NOT_PLANNED; verdict = escalated) — 0/5 pass (0% ± 0%)

| case | repo | verdict | F2P green | patch | failing assertions | cost | s |
|---|---|---|---|---|---|---|---|
| pylint-10909-nofix | pylint | ✗ | 0/0 | 12671B | escalated, terminates_with_report | $0.047 | 557 |
| pylint-10963-nofix | pylint | ✗ | 0/0 | 0B | escalated, terminates_with_report | $0.047 | 585 |
| sympy-29358-nofix | sympy | ✗ | 0/0 | 24605B | escalated | $0.038 | 522 |
| sympy-29459-nofix | sympy | ✗ | 0/0 | 1167B | escalated | $0.003 | 63 |
| xarray-11148-nofix | xarray | ✗ | 0/0 | 3658B | escalated | $0.043 | 522 |

**Failing assertions, tallied**: reference_green×7, escalated×5, terminates_with_report×4, no_regression_in_touched_suites×2

**Budget deaths** (4): pylint-10909-nofix-r1, pylint-10963-nofix-r1, sympy-29910-r1, sympy-29986-r1

**Cost**: $0.67 over 27 runs
