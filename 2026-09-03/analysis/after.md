# The eval set after harvesting

| slice | pass | runs | rate |
|---|---|---|---|
| 08-26 seed set, 14 cases × 5 (accept.py from issue text) | 48 | 70 | 69% ± 11% |
| harvested from production, 10 cases × 3 (human fix's tests) | 1 | 30 | 3% ± 6% |
| merged | 49 | 100 | 49% ± 10% |

## Harvested cases

| case | verdicts | failing |
|---|---|---|
| pylint-10909-nofix | ✗ ✗ ✗ | escalated, terminates_with_report |
| pylint-10963-nofix | ✗ ✗ ✗ | escalated, terminates_with_report |
| pylint-11175 | ✗ ✗ ✓ | reference_green |
| sympy-29090 | ✗ ✗ ✗ | no_regression_in_touched_suites, reference_green |
| sympy-29358-nofix | ✗ ✗ ✗ | escalated, terminates_with_report |
| sympy-29459-nofix | ✗ ✗ ✗ | escalated |
| sympy-29986 | ✗ ✗ ✗ | no_regression_in_touched_suites, reference_green, terminates_with_report |
| xarray-11098 | ✗ ✗ ✗ | reference_green |
| xarray-11148-nofix | ✗ ✗ ✗ | escalated, terminates_with_report |
| xarray-11268 | ✗ ✗ ✗ | reference_green, terminates_with_report |
