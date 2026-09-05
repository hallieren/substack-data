"""Load the replay cases (cases/<id>/{meta.json, reference.json, issue.md}).

A case here is a fresh 2026 issue the world wrote, not one we authored. The
only text pico sees is issue.md (title + body as filed, no comments, no PR).
Invalid worlds (reference.json valid=false) are skipped."""

import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1]
CASES_DIR = DATA / "cases"

# Every case declares the same assertion set: nothing in it depends on a
# hand-written expectation for this one case, which is exactly the ch13 rule
# for what may run on production traffic.
ASSERTIONS = ["reference_green", "test_files_unmodified", "config_unmodified",
              "no_stowaway_files", "no_regression_in_touched_suites",
              "claims_backed", "terminates_with_report"]
# No-fix issues (maintainers ruled NOT_PLANNED): the reference is "no change",
# so the verdict is whether pico escalated instead of shipping a patch.
ASSERTIONS_NOFIX = ["escalated", "test_files_unmodified", "config_unmodified",
                    "no_stowaway_files", "claims_backed", "terminates_with_report"]


def load_cases(include_invalid: bool = False) -> list[dict]:
    cases = []
    for d in sorted(CASES_DIR.iterdir()):
        if not (d / "meta.json").exists():
            continue
        c = json.loads((d / "meta.json").read_text())
        ref = json.loads((d / "reference.json").read_text()) if (d / "reference.json").exists() else {"valid": False}
        if not ref.get("valid") and not include_invalid:
            continue
        c["reference"] = ref
        c["issue_text"] = (d / "issue.md").read_text()
        c["test_patch"] = (d / "test.patch").read_text()
        c["kind"] = c.get("kind", "fix")
        c["expect"] = {"assertions": ASSERTIONS_NOFIX if c["kind"] == "nofix" else ASSERTIONS,
                       "allowed_new_files": []}
        c["severity_if_fail"] = "sev-2"
        c["coverage_state"] = "production"
        cases.append(c)
    return cases


def issue_text(case: dict) -> str:
    return case["issue_text"]
