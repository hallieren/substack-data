"""Draw the no-fix slice of production traffic: issues the maintainers closed
as NOT_PLANNED (not a bug, won't fix, user error) with at least one comment
saying so. No reference tests exist; the reference is the human ruling "no
change". These feed the escalation signal: does pico say it can't or won't,
or does it ship a patch anyway?

World = default branch at the last commit before the issue closed.
Writes cases/<id>/{issue.md, meta.json, reference.json(valid, nofix)}.
"""
import json, random, subprocess
from pathlib import Path

HERE = Path(__file__).parent
ALL = HERE / "traffic" / "all.jsonl"
CASES = HERE / "cases"
SEED = 13
QUOTA = {"sympy/sympy": 2, "pylint-dev/pylint": 2, "pydata/xarray": 1}
SHORT = {"sympy/sympy": "sympy", "pylint-dev/pylint": "pylint", "pydata/xarray": "xarray"}
BRANCH = {"sympy/sympy": "master", "pylint-dev/pylint": "main", "pydata/xarray": "main"}


def last_commit_before(repo, branch, when):
    out = subprocess.run(["gh", "api", f"repos/{repo}/commits?sha={branch}&until={when}&per_page=1"],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)[0]["sha"]


def main():
    rows = [json.loads(l) for l in ALL.open()]
    rng = random.Random(SEED)
    pool = {}
    for r in rows:
        if r.get("stateReason") == "NOT_PLANNED" and r["commentsCount"] >= 1 and r["repo"] in QUOTA \
                and not any(p["merged"] for p in r["closing_prs"]):
            pool.setdefault(r["repo"], []).append(r)
    for repo, n in QUOTA.items():
        rng.shuffle(pool[repo])
        for r in pool[repo][:n]:
            cid = f"{SHORT[repo]}-{r['number']}-nofix"
            d = CASES / cid
            d.mkdir(exist_ok=True)
            sha = last_commit_before(repo, BRANCH[repo], r["closedAt"])
            (d / "issue.md").write_text(f"# {r['title']}\n\n{r['body'] or ''}\n")
            (d / "test.patch").write_text("")
            (d / "fix.patch").write_text("")
            ruling = "\n\n".join(f"[{c['author']} {c['createdAt'][:10]}] {c['body']}" for c in r["comments"])
            (d / "ruling.md").write_text(ruling + "\n")
            meta = {"id": cid, "kind": "nofix", "repo": repo, "issue": r["number"], "url": r["url"],
                    "created": r["createdAt"], "closed": r["closedAt"], "comments": r["commentsCount"],
                    "labels": r["labels"], "pr": None, "base_sha": sha, "image": f"pico-world:{cid}",
                    "test_files": [], "source_files": [], "nontest_lines": 0}
            (d / "meta.json").write_text(json.dumps(meta, indent=1))
            (d / "reference.json").write_text(json.dumps(
                {"id": cid, "valid": True, "kind": "nofix", "reason": "maintainers closed as NOT_PLANNED",
                 "baseline_failing": [], "f2p": [], "p2p": [], "cmds": []}, indent=1))
            print(cid, sha[:10], r["title"][:70])


if __name__ == "__main__":
    main()
