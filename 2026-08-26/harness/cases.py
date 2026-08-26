"""Load the 2026-08-21 case YAMLs (ch04 artifact) into runnable form.

The case files are the contract; this module only reads them. Holdout cases
are excluded from every run except release evals (ch04 policy)."""

import json
from pathlib import Path

import yaml

DATA = Path(__file__).resolve().parents[1]
CASES_DIR = DATA.parent / "2026-08-21" / "cases"
ACCEPT_DIR = DATA / "accept"
ISSUES_DIR = DATA / "issues"


def load_cases(include_holdout: bool = False) -> list[dict]:
    cases = []
    for f in sorted(CASES_DIR.glob("pico-*.yaml")):
        c = yaml.safe_load(f.read_text())
        if c.get("holdout") and not include_holdout:
            continue
        c["instance_id"] = c["world"].split("/")[-1].split()[0]
        acc = ACCEPT_DIR / c["id"]
        c["accept_py"] = (acc / "accept.py").read_text()
        meta = json.loads((acc / "meta.json").read_text()) if (acc / "meta.json").exists() else {}
        c["suites"] = meta.get("suites")            # {"cmd":..., "parser": "pytest"|"django"}
        c["surfaces"] = meta.get("surfaces", [])    # issue-named surfaces to probe
        c["setup_cmds"] = meta.get("setup_cmds", [])  # world prep beyond the seal
        cases.append(c)
    return cases


def issue_text(case: dict) -> str:
    """The issue text is the case prompt and the accept script's only source (P1)."""
    md = (ISSUES_DIR / f"{case['id']}.md").read_text()
    return md.split("## Issue text (the ONLY verdict source, policy P1)")[1].strip()
