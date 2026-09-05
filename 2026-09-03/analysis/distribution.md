# Input distribution: eval set vs the 2026 stream

| feature | eval set (SWE-bench Verified draw) | 2026 stream, all closed | 2026 stream, reference-able |
|---|---|---|---|
| n | 18 | 453 | 120 |
| closed by a merged PR | 100% | 38% | 100% |
| fix PR ships a test | 100% | 79% | 100% |
| body has a code block | 56% | 63% | 89% |
| body has a traceback or error text | 17% | 29% | 38% |
| median body chars | 1560 | 1081 | 1406 |
| at least one comment before the fix | 88% | 54% | 54% |
| median comments before the fix | 2 | 1 | 1 |
| median source lines in the fix | 14 | 8 | 9 |
| fix touches >= 3 source files | 6% | 6% | 6% |

## How the 2026 stream closed without a merged PR

| stateReason | n |
|---|---|
| COMPLETED | 155 |
| NOT_PLANNED | 92 |
| DUPLICATE | 32 |
