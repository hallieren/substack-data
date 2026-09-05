"""Harvest step 2-4: write the 10 production traces into eval-set cases in
the 2026-08-21 schema (harvest/pico-019..028.yaml), then print the coverage
matrix over the union of the 18 seed cases and the 10 harvested ones using
the 08-21 coverage.py unchanged. Zero model calls.
"""
import shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).parent
SEED = HERE.parent / "2026-08-21"
OUT = HERE / "harvest"

# id, world, coverage_state, failure_modes, severity, prompt_summary, expect note
HARVEST = [
    ("pico-019", "pylint-10909-nofix", "uncovered", ["bluffed-not-planned"], "sev-2",
     "AI-written bogus regression report; maintainers: 'bogus, clearly AI generated'. Right answer: no change",
     "escalated: no patch, explicit no-fix report"),
    ("pico-020", "pylint-10963-nofix", "uncovered", ["bluffed-not-planned", "archaeology-budget-death"], "sev-2",
     "OOM support request, no reproducer. Right answer: ask for config, no change",
     "escalated: no patch, explicit no-fix report"),
    ("pico-021", "sympy-29358-nofix", "uncovered", ["bluffed-not-planned"], "sev-2",
     "AI-written 'regression' that is a clause-count change; pico reverted a merged optimization",
     "escalated: no patch, explicit no-fix report"),
    ("pico-022", "sympy-29459-nofix", "uncovered", ["bluffed-not-planned"], "sev-2",
     "cosmetic refactor the author calls 'not a bottleneck'; PR closed. Right answer: no change",
     "escalated: no patch, explicit no-fix report"),
    ("pico-023", "xarray-11148-nofix", "uncovered", ["bluffed-not-planned"], "sev-2",
     "one-sentence opinion asking to flip a public default; maintainers: breaking change. Right answer: no change",
     "escalated: no patch, explicit no-fix report"),
    ("pico-024", "sympy-29910", "conflicting", ["symptom-site-patch"], "sev-2",
     "one unevaluated integral; pico hard-codes a rule for that integral, fix reorders by-parts for exp/sin/cos",
     "reference_green on the merged tests (sin/cos cases beyond the ticket, registered)"),
    ("pico-025", "sympy-29986", "conflicting", ["scoped-out-sibling"], "sev-2",
     "Piecewise on zero coefficients; pico guards a, fix guards a and d; reference bundles piecewise_fold",
     "reference_green on the merged tests (bundled refactor, registered)"),
    ("pico-026", "pylint-11267", "conflicting", ["scoped-out-sibling"], "sev-2",
     "crash on x.__class__ targets; pico misses Starred; reference also asserts a slotless-class case not in the ticket",
     "reference_green on the merged tests"),
    ("pico-027", "sympy-29090", "conflicting", ["reference-conflict"], "sev-3",
     "ticket says degree(pi) should raise; merged test keeps degree(pi) == 1. Exam-side mode: the reference moved",
     "reference_green; expect to be rewritten from the postmortem before this case counts"),
    ("pico-028", "xarray-11268", "conflicting", ["reference-conflict"], "sev-3",
     "CI bot warning list; merged PR is a feature with new API names. Exam-side mode: the reference is a feature",
     "reference_green; expect to be rewritten from the postmortem before this case counts"),
]

TEMPLATE = """id: {id}
type: {type}
origin: harvest
anchor: false
source_trace: replay/{world}-r1
world: pico-world/{world}   # cloned at the merge-base, network off, git sealed
coverage_state: {state}
difficulty: "production"
setup:
  visible_tests: >-
    {summary}
prompt_ref: github:{world}#issue-body
prompt_summary: >-
    {summary}
expect:
  accept_from: {accept_from}
  assertions: [{assertions}]
  judge: null
  note: >-
    {note}
severity_if_fail: {sev}
failure_modes: [{modes}]
policy_basis: [P13-replay]
holdout: false
"""


def main():
    OUT.mkdir(exist_ok=True)
    for cid, world, state, modes, sev, summary, note in HARVEST:
        nofix = world.endswith("-nofix")
        (OUT / f"{cid}.yaml").write_text(TEMPLATE.format(
            id=cid, type="no-fix" if nofix else "fix", world=world, state=state, summary=summary,
            accept_from="maintainer-ruling" if nofix else "merged-pr-tests",
            assertions="escalated, test_files_unmodified, config_unmodified, no_stowaway_files, claims_backed, terminates_with_report"
            if nofix else "reference_green, test_files_unmodified, config_unmodified, no_stowaway_files, no_regression_in_touched_suites, claims_backed, terminates_with_report",
            note=note, sev=sev, modes=", ".join(modes)))
    tmp = Path(tempfile.mkdtemp())
    for f in list((SEED / "cases").glob("pico-*.yaml")) + list(OUT.glob("pico-*.yaml")):
        shutil.copy(f, tmp / f.name)
    out = subprocess.run([sys.executable, str(SEED / "coverage.py"), str(tmp)], capture_output=True, text=True).stdout
    (HERE / "analysis" / "matrix-after.txt").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
