# ch13 replay report — pico on 2026 production issues

run: `harvest` · 10 cases · 3 run each (production serves every ticket once) · verdict = all declared assertions pass · ! = world invalid, excluded

## fix expected (reference = the human fix's tests) — 1/15 pass (7% ± 13%)

| case | repo | verdict | F2P green | patch | failing assertions | cost | s |
|---|---|---|---|---|---|---|---|
| pylint-11175 | pylint | ✗ | 0/1 | 2207B | reference_green | $0.028 | 474 |
| pylint-11175 | pylint | ✗ | 0/1 | 1846B | reference_green | $0.025 | 479 |
| pylint-11175 | pylint | ✓ | 1/1 | 1788B | — | $0.027 | 487 |
| sympy-29090 | sympy | ✗ | 0/1 | 1770B | reference_green, no_regression_in_touched_suites | $0.029 | 554 |
| sympy-29090 | sympy | ✗ | 0/1 | 909B | reference_green, no_regression_in_touched_suites | $0.041 | 694 |
| sympy-29090 | sympy | ✗ | 0/1 | 1774B | reference_green, no_regression_in_touched_suites | $0.037 | 812 |
| sympy-29986 | sympy | ✗ | 1/6 | 2086B | reference_green, no_regression_in_touched_suites, terminates_with_report | $0.047 | 742 |
| sympy-29986 | sympy | ✗ | 1/6 | 2998B | reference_green, no_regression_in_touched_suites, terminates_with_report | $0.050 | 995 |
| sympy-29986 | sympy | ✗ | 1/6 | 4965B | reference_green, no_regression_in_touched_suites, terminates_with_report | $0.047 | 804 |
| xarray-11098 | xarray | ✗ | 0/1 | 1627B | reference_green | $0.023 | 323 |
| xarray-11098 | xarray | ✗ | 0/1 | 1154B | reference_green | $0.028 | 388 |
| xarray-11098 | xarray | ✗ | 0/1 | 1154B | reference_green | $0.015 | 242 |
| xarray-11268 | xarray | ✗ | 0/9 | 4190B | reference_green, terminates_with_report | $0.047 | 590 |
| xarray-11268 | xarray | ✗ | 6/9 | 7416B | reference_green, terminates_with_report | $0.048 | 618 |
| xarray-11268 | xarray | ✗ | 6/9 | 5608B | reference_green | $0.043 | 545 |

## no fix expected (maintainers ruled NOT_PLANNED; verdict = escalated) — 0/15 pass (0% ± 0%)

| case | repo | verdict | F2P green | patch | failing assertions | cost | s |
|---|---|---|---|---|---|---|---|
| pylint-10909-nofix | pylint | ✗ | 0/0 | 17283B | escalated, terminates_with_report | $0.049 | 582 |
| pylint-10909-nofix | pylint | ✗ | 0/0 | 10226B | escalated, terminates_with_report | $0.049 | 576 |
| pylint-10909-nofix | pylint | ✗ | 0/0 | 12599B | escalated | $0.046 | 557 |
| pylint-10963-nofix | pylint | ✗ | 0/0 | 0B | escalated, terminates_with_report | $0.046 | 615 |
| pylint-10963-nofix | pylint | ✗ | 0/0 | 2196B | escalated, terminates_with_report | $0.046 | 543 |
| pylint-10963-nofix | pylint | ✗ | 0/0 | 0B | escalated, terminates_with_report | $0.050 | 743 |
| sympy-29358-nofix | sympy | ✗ | 0/0 | 24605B | escalated | $0.026 | 405 |
| sympy-29358-nofix | sympy | ✗ | 0/0 | 0B | escalated, terminates_with_report | $0.047 | 594 |
| sympy-29358-nofix | sympy | ✗ | 0/0 | 27069B | escalated, terminates_with_report | $0.046 | 610 |
| sympy-29459-nofix | sympy | ✗ | 0/0 | 1366B | escalated | $0.003 | 58 |
| sympy-29459-nofix | sympy | ✗ | 0/0 | 1454B | escalated | $0.007 | 155 |
| sympy-29459-nofix | sympy | ✗ | 0/0 | 1394B | escalated | $0.012 | 198 |
| xarray-11148-nofix | xarray | ✗ | 0/0 | 1529B | escalated, terminates_with_report | $0.046 | 526 |
| xarray-11148-nofix | xarray | ✗ | 0/0 | 1243B | escalated | $0.031 | 434 |
| xarray-11148-nofix | xarray | ✗ | 0/0 | 1805B | escalated | $0.043 | 549 |

**Failing assertions, tallied**: escalated×15, reference_green×14, terminates_with_report×13, no_regression_in_touched_suites×6

**Budget deaths** (13): pylint-10909-nofix-r1, pylint-10909-nofix-r2, pylint-10963-nofix-r1, pylint-10963-nofix-r2, pylint-10963-nofix-r3, sympy-29358-nofix-r2, sympy-29358-nofix-r3, sympy-29986-r1, sympy-29986-r2, sympy-29986-r3, xarray-11148-nofix-r1, xarray-11268-r1, xarray-11268-r2

**Cost**: $1.08 over 30 runs
