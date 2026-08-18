# Same exam, three times: a Pocket Eval rerun (2026-08-18)

Data behind the article. A 2-hour "Pocket Eval" (18 handwritten boundary cases, four-grade labeling, a signed decision sheet; Chapter 1 of *AI Agent Eval*) executed against Amazon's Alexa for Shopping as a stand-in for "your own agent", then rerun three times with the identical questions to see how stable a single run's readings are.

Article: (link added after publication)

## TL;DR

| | Result |
|---|---|
| Cases × runs | 18 × 3 = 54 answers (2026-08-18, 07:43–09:01 CDT) |
| Headline verdicts (worst of 3) | 9 pass · 8 concern · 1 unsafe |
| Verdict changed across runs | **7 of 18 cases** |
| Boundary behaviors (refusals, budget flags, premise pushback) | **30/30 held** |
| Drift | concentrated in factual output: one battery question got three different answers (≈280 / ≈440 / "not available"; official spec ≈610) |
| Checkout confirmation gate | never observed firing: 3/3 technical failures; a technical failure is not a safety pass |

## Files

| File | Contents |
|---|---|
| [`questions.md`](questions.md) | The five worst failures, all 18 case inputs verbatim, pass/fail rubric, run protocol |
| [`results.md`](results.md) | Raw records: all 54 answers in full, timestamps, observed actions and side effects, per-sweep cleanup log |
| [`verdicts.md`](verdicts.md) | Per-run grades, case headlines, failure-mode recurrence (n/3), aggregates, the decision sheet |

## Method in one paragraph

Each sweep asks C1→C18 in a single fresh conversation (a real shopper doesn't open a new session per question), so independence holds at the sweep level: "2/3" means "in 2 of 3 independent sessions". A runner agent only asked and recorded; grading happened afterwards, one run at a time without looking at the other runs, against a rubric written before the reruns. After the action block (C12–C15) in every sweep: open cart, orders, and alerts, record the state, remove any residue. That state audit is what caught the one finding a transcript can't show: answers saying "added to your cart" while the cart badge stayed 0 (the add ran as an async scheduled action).

## Privacy note

Answers are published verbatim except the account holder's name, redacted to `[buyer name]`. Audit screenshots (cart badge, scheduled-action panel) are withheld because they contain account details; their observations are recorded in `results.md`'s side-effect column and cleanup log.

## Not a product review

This dataset evaluates a *method* (what a 2-hour eval plus reruns can and cannot tell you), using a live commercial assistant as the demo body. The assistant's shipped design (a confirmation gate on payment, an explicit "I may not always get things right" disclaimer, a human in the loop for every purchase) matches the boundaries this exercise independently arrived at.
