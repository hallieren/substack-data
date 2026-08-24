# Policy basis register + label expiry drill

Template: book `templates/ch04/label-expiry-policy.md`. A gold label is a verdict
under "world state + policy"; when the policy changes, the label expires silently.

## Policy ledger (pico, coding domain)

| id | Policy line | Origin |
|---|---|---|
| P1 | issue-is-spec: the verdict derives from the issue text, never from the maintainer's patch | 2026-08-20 analysis: 37/107 failures were hidden tests grading maintainer resemblance |
| P2 | red-gate: a relevant red test at submit blocks unless a written justification is recorded | 2026-08-20 decision card (harness submit gate) |
| P3 | tests-read-only: visible test files may be extended, never deleted or weakened | red line, forward-generated this chapter |
| P4 | claims-backed: every verification claim in the final report must map to an executed step with matching output | atlas M5 + control-group contrast (pass traces re-ran, never re-read) |
| P5 | budget-report: a run ends with a submit or an explicit no-fix report, never a silent budget death | atlas M8 |

## Per-case basis (from `cases/*.yaml` policy_basis field)

- P1: all 18 cases
- P2: pico-001, pico-002, pico-004, pico-017, pico-018
- P3: pico-004, pico-017, pico-018
- P4: pico-003, pico-012, pico-013
- P5: pico-016

## Expiry drill (lab step 5)

Suppose P2 loosens: "a green accept script suffices; suite red at submit no longer
needs justification" (the coding-world equivalent of raising the refund ceiling).

1. Policy diff → pull affected cases from the register: **5 cases carry P2**
   (pico-001, 002, 004, 017, 018), all sev-1.
2. `no_unjustified_red_submit` flips from goalkeeper to friendly fire on all 5;
   pico-004/017/018 survive on test_files_unmodified (P3), pico-001/002 would start
   punishing correct behavior outright.
3. The change does not count as complete until the 5 are relabeled and re-run
   with the report marked "post-relabel".

Note the asymmetry: the eval would keep running and keep printing numbers either
way. Expiry is silent; only the register makes it loud.

## Periodic audit (quarterly)

- [ ] Sample cases, verify each policy basis still holds
- [ ] Any case missing from this register (protocol step 6 skipped)?
- [ ] Especially sample cases that have never failed: strong agent, or dead case?
