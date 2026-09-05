"""Fetch 2026 closed GitHub issues ("production traffic") + the merged PR that closed them.

Zero model calls. Uses `gh search issues` for the issue list and one GraphQL
query per batch of 20 issues for closing PRs / comments.

Output: traffic/all.jsonl (one row per issue, every closed 2026 issue, no
filtering) — filtering happens in select_traffic.py so exclusion reasons stay
countable.
"""
import json, subprocess, sys, re, time
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "traffic" / "all.jsonl"
REPOS = ["sympy/sympy", "pylint-dev/pylint", "pydata/xarray", "mwaskom/seaborn",
         "psf/requests", "pallets/flask"]
SINCE = "2026-01-01"

def gh(*args):
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=True).stdout

def search(repo):
    out = gh("search", "issues", "--repo", repo, "--state", "closed", "--created", f">={SINCE}",
             "--json", "number,title,body,createdAt,closedAt,commentsCount,labels,url,authorAssociation",
             "--limit", "1000")
    rows = json.loads(out)
    for r in rows:
        r["repo"] = repo
        r["labels"] = [l["name"] for l in r["labels"]]
    return rows

ISSUE_FRAG = """
  i{alias}: repository(owner:"{owner}", name:"{name}") {{
    issue(number:{num}) {{
      number
      stateReason
      comments(first:100) {{ totalCount nodes {{ createdAt author {{ login }} body }} }}
      closedByPullRequestsReferences(first:5, includeClosedPrs:true) {{
        nodes {{
          number merged mergedAt baseRefName baseRefOid headRefOid
          repository {{ nameWithOwner }}
          mergeCommit {{ oid }}
          additions deletions changedFiles
          author {{ login }}
          files(first:100) {{ nodes {{ path additions deletions }} }}
        }}
      }}
    }}
  }}
"""

def enrich(batch):
    q = "query {" + "".join(
        ISSUE_FRAG.format(alias=k, owner=r["repo"].split("/")[0], name=r["repo"].split("/")[1], num=r["number"])
        for k, r in enumerate(batch)) + "}"
    for attempt in range(3):
        try:
            out = gh("api", "graphql", "-f", f"query={q}")
            break
        except subprocess.CalledProcessError as e:
            print("graphql retry", attempt, e.stderr[:200], file=sys.stderr)
            time.sleep(3)
    else:
        raise RuntimeError("graphql failed")
    data = json.loads(out)["data"]
    for k, r in enumerate(batch):
        node = data[f"i{k}"]["issue"]
        r["stateReason"] = node["stateReason"]
        r["comments"] = [{"createdAt": c["createdAt"], "author": (c["author"] or {}).get("login"),
                          "body": c["body"]} for c in node["comments"]["nodes"]]
        r["closing_prs"] = []
        for p in node["closedByPullRequestsReferences"]["nodes"]:
            files = p["files"]["nodes"]
            r["closing_prs"].append({
                "number": p["number"], "repo": p["repository"]["nameWithOwner"], "merged": p["merged"], "mergedAt": p["mergedAt"],
                "baseRefName": p["baseRefName"], "baseRefOid": p["baseRefOid"],
                "headRefOid": p["headRefOid"], "mergeCommit": (p["mergeCommit"] or {}).get("oid"),
                "author": (p["author"] or {}).get("login"),
                "additions": p["additions"], "deletions": p["deletions"], "changedFiles": p["changedFiles"],
                "files": files,
            })
    return batch

CODE_BLOCK = re.compile(r"```")
TRACEBACK = re.compile(r"Traceback \(most recent call last\)|Error:|Exception", re.I)

def features(r):
    body = r.get("body") or ""
    r["has_code_block"] = bool(CODE_BLOCK.search(body))
    r["has_traceback"] = bool(TRACEBACK.search(body))
    r["body_chars"] = len(body)
    return r

def main():
    rows = []
    for repo in REPOS:
        rs = search(repo)
        print(repo, len(rs), file=sys.stderr)
        rows += rs
    for i in range(0, len(rows), 20):
        enrich(rows[i:i+20])
        print(f"enriched {min(i+20, len(rows))}/{len(rows)}", file=sys.stderr)
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as f:
        for r in rows:
            f.write(json.dumps(features(r), ensure_ascii=False) + "\n")
    print("wrote", len(rows), OUT, file=sys.stderr)

if __name__ == "__main__":
    main()
