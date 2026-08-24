# Annotation bar: rulings on all 21 empty cells

Template: book `templates/ch04/coverage-matrix.md`. An empty cell with a reason is a
decision; an empty cell without one is a hole. Signature rule per ch01: only signed
decisions get taken seriously. Rulings drafted by claude from the sealed 2026-08-20
coding sheet; each requires the spec owner's countersign before the set ships.

| Empty cell (mode × coverage_state) | Ruling | Reason | Signature |
|---|---|---|---|
| committed-against-signal × conflicting | **fill** | a conflicting world adds the strongest signal there is, a red test naming the right design; committing against it is exactly how M1 cascades start, and M4 is pico's joint-biggest cluster (17 sealed traces) | claude · countersign: ____ |
| test-tampering × uncovered | reasoned empty | tampering needs a test to tamper with; an uncovered world offers nothing to delete or weaken | claude · countersign: ____ |
| test-tampering × green | reasoned empty | with nothing red at submit time the red line gets no purchase; the tampering temptation begins where a test refuses to go green | claude · countersign: ____ |
| phantom-verification × conflicting | reasoned empty | false verification needs a green mirage to trust; a conflicting suite hands the agent red instead, which is dismissed-red-evidence territory (row already sentried) | claude · countersign: ____ |
| phantom-verification × doomed | reasoned empty | a doomed seed guarantees red at submit; same no-mirage argument as above | claude · countersign: ____ |
| scoped-out-sibling × green | **fill** (queued) | a green covering suite is the punt's native camouflage; worth one variant whose accept adds a sibling surface the visible tests do not name | claude · countersign: ____ |
| scoped-out-sibling × conflicting | reasoned empty | a conflicting test that covers the sibling turns the punt red and files the failure under dismissed-red-evidence; no independent mechanism | claude · countersign: ____ |
| scoped-out-sibling × doomed | reasoned empty | the doomed column exists to stress the test-tampering red line; seeding it here would conflate two rows' jobs | claude · countersign: ____ |
| symptom-site-patch × green | reasoned empty | detection runs through accept probing issue-implied surfaces, identical in green and uncovered worlds; two sentries already stand in the native cell | claude · countersign: ____ |
| symptom-site-patch × conflicting | reasoned empty | a covering test pins behavior, not patch site; whatever it flags files under dismissed-red-evidence | claude · countersign: ____ |
| symptom-site-patch × doomed | reasoned empty | doomed seeds stress the red line, not patch-site choice | claude · countersign: ____ |
| abandoned-validated-fix × conflicting | **fill** (queued) | the abandon reflex fires on a scare; a red conflict is the classic scare (sealed dj-12663 reverted a validated fix after a single error line) | claude · countersign: ____ |
| abandoned-validated-fix × uncovered | reasoned empty | the trigger is the agent's own probe error, available in every world; the axis does not interact, one green-world sentry plus the queued conflicting variant suffice at sev-2 | claude · countersign: ____ |
| abandoned-validated-fix × doomed | reasoned empty | doomed seeds belong to the red-line row | claude · countersign: ____ |
| plan-inversion-slip × conflicting | reasoned empty | the slip is internal to the edit, world-state-independent; one sentry suffices at sev-2 | claude · countersign: ____ |
| plan-inversion-slip × uncovered | reasoned empty | same no-interaction argument | claude · countersign: ____ |
| plan-inversion-slip × doomed | reasoned empty | doomed seeds belong to the red-line row | claude · countersign: ____ |
| archaeology-budget-death × green | reasoned empty | sev-3 row: budget follows severity, not traffic; one sentry on the mode's native world | claude · countersign: ____ |
| archaeology-budget-death × conflicting | reasoned empty | same sev-3 budget ruling | claude · countersign: ____ |
| archaeology-budget-death × doomed | reasoned empty | same sev-3 budget ruling | claude · countersign: ____ |
| committed-against-signal × doomed | reasoned empty | a doomed seed's red says "stop", not a design hint; no distinct mechanism beyond the red-line rows | claude · countersign: ____ |

## Coverage self-check (template checklist)

- [x] All sev-1 rows non-zero: dismissed-red-evidence (6), phantom-verification (2), test-tampering (3)
- [x] Every cell either holds a case or appears above
- [x] Atlas cross-check: all 8 agent-side modes from `agent_modes.json` present as rows; the 2 exam-side modes (E1/E2) are deliberately not rows, they are the reason the verdict source moved to issue text (P1), see basis-register.md

## Missing-row check against the atlas

E1 ("hidden tests grade the maintainer's fix") and E2 ("grading machinery broke") are
exam defects, not agent failure modes; they are retired by construction: every case's
accept script derives from issue text (P1) and carries a validity check
(accept_red_prefix where seeded). They do not get rows because the new exam removes
the mechanism rather than testing for it.
