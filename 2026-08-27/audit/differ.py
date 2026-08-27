"""ch08 loot — the side-effect audit, run retroactively over the 08-26 full run.

The question (ch08): besides what should have changed, what else did?

The evidence was already on disk. runner.py ends every run with
`git add -N . && git diff` and stores the result as world["patch"], a
full-workspace before/after diff. This script replays those 70 stored diffs
with zero model calls and reconciles every changed file against a reference
frame.

Reference frame, registered honestly: the 08-21 cases never declared a file
scope in expect, so strictly every diff line is undeclared. As a triage aid
we borrow the maintainer's own fix (SWE-bench gold patch, fetched into
gold_patches.json) as "the fix's home files". Lines outside that frame are
findings to be triaged by hand, not automatic violations: the accept scripts
derive from issue text only (P1), so a fix living in a different file is
legal. What triage looks for is the other classes: files left behind,
out-of-scope edits, test tampering.

Usage: python differ.py  (from this directory; reads ../../2026-08-26/runs/full)
Writes: audit.json (machine), findings.md (the 19 undeclared lines, for triage)
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = HERE.parents[1] / "2026-08-26" / "runs" / "full"
sys.path.insert(0, str(HERE.parents[1] / "2026-08-26" / "harness"))
from cases import load_cases  # noqa: E402

TEST_PATH = re.compile(r"(^|/)tests?/|(^|/)testing/|(^|/)test_[^/]+$|_test\.py$")


def diff_files(patch: str) -> dict:
    """path -> {new, deleted, plus, minus}, parsed from a unified git diff."""
    files, cur = {}, None
    for line in patch.splitlines():
        m = re.match(r"^diff --git a/(\S+) b/(\S+)", line)
        if m:
            cur = m.group(2)
            files[cur] = {"new": False, "deleted": False, "plus": 0, "minus": 0}
        elif cur:
            if line.startswith("new file mode"):
                files[cur]["new"] = True
            elif line.startswith("deleted file mode"):
                files[cur]["deleted"] = True
            elif line.startswith("+") and not line.startswith("+++"):
                files[cur]["plus"] += 1
            elif line.startswith("-") and not line.startswith("---"):
                files[cur]["minus"] += 1
    return files


def classify(path: str, info: dict, gold_src: set) -> str:
    if path in gold_src:
        return "gold_src"      # the maintainer fix's home files
    if TEST_PATH.search(path):
        return "test"          # test-path files (both hits are NEW files)
    if info["new"]:
        return "new_file"
    if info["deleted"]:
        return "deleted"
    return "other_src"


def main() -> None:
    gold = json.load(open(HERE / "gold_patches.json"))
    cases = {c["id"]: c for c in load_cases()}
    results = {json.loads(l)["key"]: json.loads(l) for l in open(RUN / "results.jsonl")}

    audit, totals = [], Counter()
    for wf in sorted((RUN / "world").glob("*.json")):
        key = wf.name[:-5]
        w = json.load(open(wf))
        case = cases[key.rsplit("-r", 1)[0]]
        gold_src = set(diff_files(gold[case["instance_id"]]["patch"]))
        rec = {"key": key, "case": case["id"], "status": w["status"],
               "accept_post": w["accept_post"],
               "newly_failing": len(results[key]["newly_failing"]), "files": []}
        for path, info in diff_files(w["patch"]).items():
            cat = classify(path, info, gold_src)
            totals[cat] += 1
            rec["files"].append({"path": path, "cat": cat, **info})
        audit.append(rec)

    json.dump(audit, open(HERE / "audit.json", "w"), indent=1)

    lines = ["# The 19 undeclared diff lines, laid out for triage",
             "",
             f"70 traces replayed from disk. {sum(totals.values())} changed-file "
             f"lines total: {dict(totals)}.",
             "Every line below sits outside the maintainer fix's home files.",
             "Dispositions were assigned by hand; see triage.md.", ""]
    for r in audit:
        extra = [f for f in r["files"] if f["cat"] != "gold_src"]
        if not extra:
            continue
        green = (r["status"] == "done" and r["accept_post"] == 0
                 and r["newly_failing"] == 0)
        lines.append(f"## {r['key']}  {'GREEN' if green else r['status']}")
        for f in extra:
            mark = " NEW" if f["new"] else ""
            lines.append(f"- [{f['cat']}] `{f['path']}`{mark} +{f['plus']}/-{f['minus']}")
        lines.append("")
    (HERE / "findings.md").write_text("\n".join(lines))
    print(f"{len(audit)} traces audited, totals {dict(totals)}")


if __name__ == "__main__":
    main()
