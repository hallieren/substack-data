"""Draw the replay sample from traffic/selected.jsonl and materialize one case
directory per issue: cases/<id>/{issue.md, meta.json, test.patch, fix.patch}.

Zero model calls. Seeded, stratified by repo (one issue per closing PR).
The fix.patch is never shown to pico; it exists for the shadow comparison
and for verify_worlds.py.
"""
import json, random, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).parent
SEL = HERE / "traffic" / "selected.jsonl"
CASES = HERE / "cases"
SEED = 13
QUOTA = {"sympy/sympy": 10, "pylint-dev/pylint": 9, "pydata/xarray": 4, "pallets/flask": 1}
SHORT = {"sympy/sympy": "sympy", "pylint-dev/pylint": "pylint", "pydata/xarray": "xarray",
         "pallets/flask": "flask", "mwaskom/seaborn": "seaborn", "psf/requests": "requests"}

sys.path.insert(0, str(HERE))
from select_traffic import is_test  # noqa: E402


def split_patch(diff: str):
    """Split a unified diff into (test part, source part) by file path."""
    chunks = re.split(r"(?m)^(?=diff --git )", diff)
    test, src = [], []
    for ch in chunks:
        if not ch.strip():
            continue
        m = re.match(r"diff --git a/(\S+) b/(\S+)", ch)
        path = m.group(2) if m else ""
        (test if is_test(path) else src).append(ch)
    return "".join(test), "".join(src)


def main():
    rows = [json.loads(l) for l in SEL.open()]
    rng = random.Random(SEED)
    by_repo = {}
    seen_pr = set()
    for r in sorted(rows, key=lambda r: r["createdAt"]):
        key = (r["ref_pr"]["repo"], r["ref_pr"]["number"])
        if key in seen_pr:
            continue
        seen_pr.add(key)
        by_repo.setdefault(r["repo"], []).append(r)
    sample = []
    for repo, n in QUOTA.items():
        pool = by_repo.get(repo, [])
        rng.shuffle(pool)
        sample += pool[:n]
    CASES.mkdir(exist_ok=True)
    index = []
    for r in sample:
        p = r["ref_pr"]
        cid = f"{SHORT[r['repo']]}-{r['number']}"
        d = CASES / cid
        d.mkdir(exist_ok=True)
        diff = subprocess.run(["gh", "pr", "diff", str(p["number"]), "--repo", p["repo"]],
                              capture_output=True, text=True, check=True).stdout
        test_patch, fix_patch = split_patch(diff)
        (d / "test.patch").write_text(test_patch)
        (d / "fix.patch").write_text(fix_patch)
        (d / "issue.md").write_text(f"# {r['title']}\n\n{r['body'] or ''}\n")
        meta = {"id": cid, "repo": r["repo"], "issue": r["number"], "url": r["url"],
                "created": r["createdAt"], "closed": r["closedAt"], "comments": r["commentsCount"],
                "labels": r["labels"], "pr": p["number"], "pr_merged_at": p["mergedAt"],
                "base_sha": p["baseRefOid"], "image": f"pico-world:{cid}",
                "test_files": p["test_files"], "source_files": p["source_files"],
                "nontest_lines": p["nontest_lines"]}
        (d / "meta.json").write_text(json.dumps(meta, indent=1))
        index.append(meta)
        print(cid, p["number"], len(test_patch), len(fix_patch), r["title"][:60])
    (HERE / "traffic" / "sample.json").write_text(json.dumps(index, indent=1))
    print(len(sample), "cases")


if __name__ == "__main__":
    main()
