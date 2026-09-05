"""Drift probe 1, input distribution: the 18-case eval set (2026-08-21, drawn
from SWE-bench Verified) against the raw 2026 issue stream of the same kind of
repos. Zero model calls. Writes analysis/distribution.md + analysis/distribution.json.
"""
import json, re, statistics, subprocess, sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from fetch_issues import CODE_BLOCK, TRACEBACK  # noqa: E402
from select_traffic import is_test, is_docs_or_meta  # noqa: E402

CASES_0821 = HERE.parent / "2026-08-21" / "cases"
VERIFIED = HERE.parent / "2026-08-16" / "scripts" / "instances_verified.json"
ALL = HERE / "traffic" / "all.jsonl"
SEL = HERE / "traffic" / "selected.jsonl"


def eval_set_rows():
    ids = []
    for f in sorted(CASES_0821.glob("pico-*.yaml")):
        for line in f.read_text().splitlines():
            if line.startswith("world:"):
                ids.append(line.split()[1].split("/")[-1])
    inst = {r["instance_id"]: r for r in json.load(VERIFIED.open())}
    rows = []
    q = "query {"
    for k, iid in enumerate(dict.fromkeys(ids)):
        repo, num = iid.rsplit("-", 1)
        owner, name = repo.split("__")
        q += f'''
  p{k}: repository(owner:"{owner}", name:"{name}") {{ pullRequest(number:{num}) {{
    number createdAt mergedAt additions deletions changedFiles
    files(first:100) {{ nodes {{ path additions deletions }} }}
    closingIssuesReferences(first:3) {{ nodes {{ number createdAt body comments(first:100) {{ totalCount nodes {{ createdAt }} }} }} }}
  }} }}'''
    q += "}"
    data = json.loads(subprocess.run(["gh", "api", "graphql", "-f", f"query={q}"],
                                     capture_output=True, text=True, check=True).stdout)["data"]
    for k, iid in enumerate(dict.fromkeys(ids)):
        pr = data[f"p{k}"]["pullRequest"]
        issues = pr["closingIssuesReferences"]["nodes"]
        body = inst[iid]["problem_statement"]
        files = pr["files"]["nodes"]
        comments_before = None
        if issues:
            iss = issues[0]
            comments_before = sum(c["createdAt"] < pr["mergedAt"] for c in iss["comments"]["nodes"])
        rows.append({"id": iid, "body": body, "files": files, "mergedAt": pr["mergedAt"],
                     "createdAt": issues[0]["createdAt"] if issues else None,
                     "comments_before_fix": comments_before, "has_github_issue": bool(issues)})
    return rows


def stream_rows(path):
    rows = []
    for l in path.open():
        r = json.loads(l)
        prs = [p for p in r["closing_prs"] if p["merged"]]
        p = sorted(prs, key=lambda p: p["mergedAt"])[0] if prs else None
        rows.append({"id": f"{r['repo']}#{r['number']}", "body": r["body"] or "",
                     "files": p["files"] if p else None, "mergedAt": p["mergedAt"] if p else None,
                     "createdAt": r["createdAt"], "closedAt": r["closedAt"], "stateReason": r.get("stateReason"),
                     "comments_before_fix": sum(c["createdAt"] < (p["mergedAt"] if p else r["closedAt"])
                                                for c in r["comments"]),
                     "has_github_issue": True, "labels": r["labels"]})
    return rows


def feats(rows):
    n = len(rows)
    def share(pred):
        xs = [pred(r) for r in rows if pred(r) is not None]
        return f"{sum(xs)/len(xs):.0%}" if xs else "n/a"
    def med(f):
        xs = [f(r) for r in rows if f(r) is not None]
        return f"{statistics.median(xs):.0f}" if xs else "n/a"
    fixed = [r for r in rows if r["files"]]
    def nontest(r):
        return sum(f["additions"] + f["deletions"] for f in r["files"]
                   if not is_test(f["path"]) and not is_docs_or_meta(f["path"]))
    return {
        "n": n,
        "closed by a merged PR": share(lambda r: bool(r["files"])),
        "fix PR ships a test": share(lambda r: any(is_test(f["path"]) for f in r["files"]) if r["files"] else None),
        "body has a code block": share(lambda r: bool(CODE_BLOCK.search(r["body"]))),
        "body has a traceback or error text": share(lambda r: bool(TRACEBACK.search(r["body"]))),
        "median body chars": med(lambda r: len(r["body"])),
        "at least one comment before the fix": share(lambda r: (r["comments_before_fix"] >= 1) if r["comments_before_fix"] is not None else None),
        "median comments before the fix": med(lambda r: r["comments_before_fix"]),
        "median source lines in the fix": med(lambda r: nontest(r) if r["files"] else None),
        "fix touches >= 3 source files": share(lambda r: (sum(1 for f in r["files"] if not is_test(f["path"]) and not is_docs_or_meta(f["path"])) >= 3) if r["files"] else None),
    }


def main():
    A, B, C = eval_set_rows(), stream_rows(ALL), stream_rows(SEL)
    fa, fb, fc = feats(A), feats(B), feats(C)
    reasons = {}
    for r in B:
        if not r["files"]:
            reasons[r["stateReason"] or "unknown"] = reasons.get(r["stateReason"] or "unknown", 0) + 1
    lines = ["# Input distribution: eval set vs the 2026 stream", "",
             "| feature | eval set (SWE-bench Verified draw) | 2026 stream, all closed | 2026 stream, reference-able |",
             "|---|---|---|---|"]
    for k in fa:
        lines.append(f"| {k} | {fa[k]} | {fb[k]} | {fc[k]} |")
    lines += ["", "## How the 2026 stream closed without a merged PR", "", "| stateReason | n |", "|---|---|"]
    for k, v in sorted(reasons.items(), key=lambda kv: -kv[1]):
        lines.append(f"| {k} | {v} |")
    (HERE / "analysis" / "distribution.md").write_text("\n".join(lines) + "\n")
    (HERE / "analysis" / "distribution.json").write_text(json.dumps(
        {"eval_set": fa, "stream_all": fb, "stream_selected": fc, "no_pr_reasons": reasons,
         "eval_set_rows": [{k: v for k, v in r.items() if k != "body"} for r in A]}, indent=1))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
