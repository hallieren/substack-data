# Trace coding protocol (ch03 error analysis, pico sealed SWE-bench run)

## Context

pico is a minimal coding agent (bash + edit_file/write_file tools, DeepSeek V4 Flash as the model). It ran SWE-bench Verified (500 real GitHub issues) in a sealed harness: one-shot disposable container, no network, git history truncated before the fix exists. 393 passed, 107 failed. You are coding failure trajectories: for each one, find where it actually went wrong.

Each dossier file contains: endpoint evidence (grading result, which tests still fail, regressions), the problem statement, the full trajectory with numbered steps, the submitted patch, and the human maintainer's GOLD patch (answer key; the agent never saw it).

## Method (follow strictly)

1. First read the endpoint block and fix in mind HOW it failed (wrong fix? incomplete fix? regression? nothing submitted? budget stop?). Skim the gold patch to know what the correct fix was.
2. Then go back to step 1 of the trajectory and read FORWARD. At every step ask exactly one question: "given the information available at this step, is this action reasonable?" Judge from the agent's information position, never from the ending, and never from the gold patch (the gold patch tells you what right was, not what was knowable at step N).
3. The first step where the honest answer is "no" is `first_bad_step`. Common shapes: misread a tool result; searched the wrong place and committed to it; formed a fix hypothesis without confirming the mechanism; edited the symptom site instead of the cause; never ran the reproduction; declared success without running tests; wandered until the budget died.
4. Mark ONLY the first bad step. Downstream steps that "reasonably" build on the poisoned premise are NOT new failures. If a genuinely independent second failure exists, log it as `secondary`.
5. If every agent action was reasonable and the failure sits in the task/grading itself (spec underdetermined the expected behavior, test demands an implementation detail the issue never stated, harness budget killed a healthy run), say so via `blame` and put `first_bad_step` at the step where the mismatch became visible (or the last step if it never did).

## Output row per trace (JSON object)

- `trace_id`: instance id.
- `first_bad_step`: integer step number from the dossier.
- `phase`: one of `task_understanding` | `localization` | `root_cause_diagnosis` | `fix_design` | `implementation` | `verification` | `budget_management` | `submission`.
- `one_line`: behavioral, step-anchored, English. "step 41 read the failing assert but patched the formatting branch that never runs for this input" is behavior; "the model is bad at sympy" is speculation. No speculation.
- `mode_hint`: a verb phrase naming the failure mode as you see it (freely worded; clustering happens later). Examples of the FORM (not a taxonomy to fit): "declared success without running the repro", "patched the symptom site, not the cause", "fix hypothesis never validated against the failing test".
- `blame`: `agent` | `harness_or_eval` | `unclear`. `harness_or_eval` = the wrong thing is the exam or the harness, not an agent action (see 5). A max_spend stop is `agent` if the budget died because the agent wandered; `harness_or_eval` only if progress was healthy and the ceiling was simply too low.
- `tests_run_before_submit`: boolean, did it run the relevant failing test (or a reproduction) at least once before finalizing?
- `verified_fix`: boolean, after its final edit, did it re-run the failing test/repro and see it pass? (false = submitted unverified)
- `gave_up`: boolean, did it explicitly settle/submit knowing the fix was unconfirmed, or stop attempting?
- `secondary`: string or null. Only a genuinely independent second failure.
- `evidence_quote`: <=200 chars verbatim from the trajectory that pins the first_bad_step.
- `confidence`: `high` | `med` | `low`.

## Discipline

- Write behavior, not speculation. Anchor every description to a step number.
- One trace, one primary failure.
- Do not force traces into the example phrasings above; let the mode name grow out of the trace.
- Be honest when the trace looks fine and the grading is the problem; that finding is wanted, not embarrassing.
