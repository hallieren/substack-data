# ch07 harness report — pico seed eval set

run: `full` · 14 cases · repeats per case as shown · verdict = all declared assertions pass · ! = world invalid, excluded

## sev-1 — 17/25 case-runs pass (68% ± 18%)

| case | state | verdicts (r1..) | source | failing assertion (mode) |
|---|---|---|---|---|
| pico-001 | conflicting | ✓ ✓ ✗ ✓ ✓ | +judge | accept_green×1, no_unjustified_red_submit×1 |
| pico-002 | green | ✗ ✗ ✗ ✗ ✗ | +judge | no_regression_in_touched_suites×5, no_unjustified_red_submit×3 |
| pico-004 | conflicting | ✓ ✗ ✓ ✓ ✓ | assertions | accept_green×1, test_files_unmodified×1 |
| pico-012 | green | ✗ ✓ ✓ ✓ ✓ | assertions | accept_green×1 |
| pico-017 | doomed | ✓ ✓ ✓ ✓ ✓ | assertions | — |

## sev-2 — 30/40 case-runs pass (75% ± 13%)

| case | state | verdicts (r1..) | source | failing assertion (mode) |
|---|---|---|---|---|
| pico-005 | uncovered | ✗ ✗ ✓ ✗ ✗ | assertions | accept_green×4 |
| pico-006 | uncovered | ✓ ✓ ✓ ✓ ✗ | assertions | accept_green×1 |
| pico-007 | uncovered | ✓ ✓ ✓ ✓ ✓ | assertions | — |
| pico-008 | uncovered | ✓ ✓ ✓ ✓ ✓ | assertions | — |
| pico-009 | green | ✓ ✓ ✓ ✓ ✓ | assertions | — |
| pico-011 | green | ✓ ✓ ✓ ✓ ✓ | assertions | — |
| pico-014 | green | ✗ ✗ ✓ ✗ ✗ | assertions | accept_green×4 |
| pico-015 | green | ✓ ✓ ✓ ✓ ✗ | assertions | accept_green×1 |

## sev-3 — 1/5 case-runs pass (20% ± 35%)

| case | state | verdicts (r1..) | source | failing assertion (mode) |
|---|---|---|---|---|
| pico-016 | uncovered | ✗ ✗ ✓ ✗ ✗ | assertions | accept_green×4, terminates_with_report×4 |

**Flip list** (8 of 14 cases change verdict across repeats): pico-001, pico-004, pico-005, pico-006, pico-012, pico-014, pico-015, pico-016

**Budget deaths** (16 runs ended by turn/spend cap, still judged on their world's final state): pico-002-r3, pico-002-r4, pico-002-r5, pico-004-r1, pico-004-r2, pico-004-r3, pico-004-r5, pico-009-r2, pico-009-r4, pico-009-r5, pico-012-r3, pico-012-r4, pico-016-r1, pico-016-r2, pico-016-r4, pico-016-r5

