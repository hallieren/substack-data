"""Select replay candidates from traffic/all.jsonl and count every exclusion reason.

Zero model calls. Writes traffic/selected.jsonl and analysis/selection.md.
Selection is by *buildability of a reference*, never by "looks like a bug".
"""
import json, re, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
ALL = HERE / "traffic" / "all.jsonl"
SEL = HERE / "traffic" / "selected.jsonl"
MD = HERE / "analysis" / "selection.md"
MAX_NONTEST_LINES = 300
DEFAULT_BRANCH = {"sympy/sympy": "master", "pylint-dev/pylint": "main", "pydata/xarray": "main",
                  "mwaskom/seaborn": "master", "psf/requests": "main", "pallets/flask": "main"}

def is_test(path):
    return bool(re.search(r"(^|/)(tests?|testing)(/|$)|(^|/)test_[^/]+\.py$|_test\.py$|conftest\.py$", path))

def is_docs_or_meta(path):
    return bool(re.search(r"\.(md|rst|txt|toml|cfg|ini|yml|yaml)$|^doc/|^docs/|^\.github/|CHANGES|changelog|release", path, re.I))

def classify(r):
    prs = [p for p in r["closing_prs"] if p["merged"]]
    if not prs:
        return "no merged PR closed it", None
    prs = [p for p in prs if p["baseRefName"] == DEFAULT_BRANCH[r["repo"]]]
    if not prs:
        return "PR merged into non-default branch", None
    p = sorted(prs, key=lambda p: p["mergedAt"])[0]
    if p["repo"] != r["repo"]:
        return "fixed in another repo (a dependency)", None
    files = p["files"]
    if len(files) >= 100:
        return "PR too large (>=100 files)", None
    test_files = [f for f in files if is_test(f["path"])]
    nontest = [f for f in files if not is_test(f["path"]) and not is_docs_or_meta(f["path"])]
    if not nontest:
        return "PR changes no source file (docs/meta only)", None
    if not test_files:
        return "PR adds no test (no reference)", None
    nt_lines = sum(f["additions"] + f["deletions"] for f in nontest)
    if nt_lines > MAX_NONTEST_LINES:
        return f"PR source change > {MAX_NONTEST_LINES} lines", None
    p = dict(p, test_files=[f["path"] for f in test_files],
             source_files=[f["path"] for f in nontest], nontest_lines=nt_lines)
    return "selected", p

def main():
    rows = [json.loads(l) for l in ALL.open()]
    reasons = Counter(); per_repo = Counter(); selected = []
    for r in rows:
        reason, p = classify(r)
        reasons[reason] += 1
        r["exclusion"] = None if p else reason
        if p:
            r["ref_pr"] = p
            per_repo[r["repo"]] += 1
            selected.append(r)
    with SEL.open("w") as f:
        for r in selected:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    lines = [f"# Selection from {len(rows)} closed 2026 issues\n", "| reason | n |", "|---|---|"]
    for k, v in reasons.most_common():
        lines.append(f"| {k} | {v} |")
    lines += ["", "| repo | selected |", "|---|---|"]
    for k, v in per_repo.most_common():
        lines.append(f"| {k} | {v} |")
    lines += ["", "| repo | issue | created | comments | code | pr | src lines | src files | test files | title |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in selected:
        p = r["ref_pr"]
        lines.append(f"| {r['repo']} | {r['number']} | {r['createdAt'][:10]} | {r['commentsCount']} | {'y' if r['has_code_block'] else '-'} | {p['number']} | {p['nontest_lines']} | {len(p['source_files'])} | {len(p['test_files'])} | {r['title'][:60]} |")
    MD.write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:len(reasons)+3+len(per_repo)+4]))

if __name__ == "__main__":
    main()
