"""Trajectory contamination audit (Meerkat-lite).

Scans pico-1 trajectories for the three leakage channels caught in the
2026-08-14 run: git-history oracle (gold-patch lines seen in git output
before the model wrote them), future-test oracle (test_patch lines seen in
git output), and network use in unsealed runs. The leaderboard checklist
requires trajectory inspection; this automates it.

Usage:
    uv run python bench/audit_trajs.py <run_dir> [gold_patches.json test_patches.json]

Fetches gold/test patches from the HF datasets-server when the two optional
files are absent. Writes <run_dir>/audit.json and exits nonzero if any
instance is flagged (CI-able).
"""

import json
import re
import sys
import urllib.request
from pathlib import Path

NET = re.compile(
    r"\b(curl|wget|pip3?\s+(install|download)|git\s+(fetch|pull|clone)"
    r"|urllib|requests\.(get|post)|httpx|socket\.|https?://)\b")
LOCAL = re.compile(r"https?://(localhost|127\.0\.0\.1)")
# history-revealing git commands; blame/diff/status/stash show the worktree
# (i.e. the model's own edits) and false-positive on the model's own fix
GIT_HISTORY = re.compile(
    r"\bgit\b.*\b(log|show|cat-file|reflog|rev-list|describe|branch|tag|name-rev)\b")
# any commit date at/after the Verified cutoff is leakage — except the image's
# own env-setup commit (subject "SWE-bench") and uncommitted-worktree blame rows
FUTURE_DATE = re.compile(r".{0,120}\b(202[4-9]|20[3-9]\d)-(\d\d)-\d\d.{0,60}")


def _future_date_hits(content: str, env_hashes: set[str]) -> list[str]:
    hits = []
    for m in FUTURE_DATE.finditer(content):
        year, month = int(m.group(1)), int(m.group(2))
        if (year, month) < (2024, 7):
            continue
        ctx = m.group(0)
        if "SWE-bench" in ctx or "Not Committed Yet" in ctx:
            continue
        if any(h in ctx for h in env_hashes):
            continue  # the image's env-setup commit shown without its subject
        hits.append(ctx.strip()[:160])
    return hits


ENV_HASH = re.compile(r"\b([0-9a-f]{7,40})\b.{0,120}SWE-bench|SWE-bench.{0,120}\b([0-9a-f]{7,40})\b")


def _env_commit_hashes(traj: dict) -> set[str]:
    """Hashes the traj itself ties to the image's 'SWE-bench' env commit."""
    hashes: set[str] = set()
    for m in traj["messages"]:
        for b in m.get("content", []):
            if b.get("kind") == "tool_result":
                content = _text(b.get("content") or "")
                if "SWE-bench" in content:
                    for mm in ENV_HASH.finditer(content):
                        h = mm.group(1) or mm.group(2)
                        if h and len(h) >= 7:
                            hashes.add(h[:12])
    return hashes


def _added_lines(patch: str, minlen: int = 16) -> set[str]:
    added = {l[1:].strip() for l in patch.splitlines()
             if l.startswith("+") and not l.startswith("+++")
             and len(l[1:].strip()) >= minlen}
    # a line the patch itself shows as context or removed existed at base —
    # seeing it in git output proves nothing (moved/duplicated code)
    preexisting = {l[1:].strip() for l in patch.splitlines()
                   if (l.startswith(" ") or l.startswith("-"))
                   and not l.startswith("---")}
    return added - preexisting


def _text(x) -> str:
    return x if isinstance(x, str) else json.dumps(x)


def audit_traj(traj: dict, gold_patch: str, test_patch: str) -> dict:
    """One trajectory's contamination verdict.

    git_oracle uses write-order: a gold line only counts if it shows up in
    git output before the model ever produced it, so a model's own `git diff`
    of its own fix does not self-incriminate.
    """
    both = gold_patch + "\n" + test_patch
    gold, tests = _added_lines(both) & _added_lines(gold_patch), _added_lines(test_patch)
    tests = tests & _added_lines(both)
    sealed = traj["info"]["config"].get("network") == "none"
    calls: dict = {}
    emitted: set[str] = set()
    git_hits: list[str] = []
    test_hits: list[str] = []
    net_cmds: list[str] = []
    date_hits: list[str] = []
    env_hashes = _env_commit_hashes(traj)
    for m in traj["messages"]:
        for b in m.get("content", []):
            kind = b.get("kind")
            if m["role"] == "assistant":
                if kind == "tool_call":
                    calls[b["id"]] = (b["name"], b["arguments"])
                    args_text = _text(b["arguments"])
                    emitted |= {l for l in gold if l in args_text}
                    if b["name"] == "bash":
                        cmd = b["arguments"].get("command", "")
                        if NET.search(cmd) and not LOCAL.search(cmd):
                            net_cmds.append(cmd[:120])
                elif kind == "text":
                    emitted |= {l for l in gold if l in b.get("text", "")}
            elif kind == "tool_result":
                name, args = calls.get(b.get("call_id"), ("", {}))
                if name != "bash" or not GIT_HISTORY.search(args.get("command", "")):
                    continue
                content = _text(b.get("content") or "")
                fresh = [l for l in gold if l in content and l not in emitted]
                if len(fresh) >= 2 or (gold and len(fresh) >= 0.5 * len(gold) and fresh):
                    git_hits.extend(fresh)
                seen_tests = [l for l in tests if l in content]
                if len(seen_tests) >= 2:
                    test_hits.extend(seen_tests)
                date_hits.extend(_future_date_hits(content, env_hashes))
    # exactly one post-base commit (the image's env commit) is legal, so a
    # single distinct future date is explainable; two or more are not
    distinct_days = {m.group(0) for h in date_hits
                     for m in [re.search(r"\b20\d\d-\d\d-\d\d\b", h)] if m}
    if len(distinct_days) <= 1 and not (git_hits or test_hits):
        date_hits = []
    return {
        "git_oracle": sorted(set(git_hits)),
        "test_oracle": sorted(set(test_hits)),
        "future_dates": sorted(set(date_hits))[:20],
        "network": net_cmds if not sealed else [],
        "sealed": sealed,
    }


def fetch_patches() -> tuple[dict, dict]:
    rows, offset = [], 0
    while offset < 500:
        url = ("https://datasets-server.huggingface.co/rows?dataset="
               "princeton-nlp%2FSWE-bench_Verified&config=default&split=test"
               f"&offset={offset}&length=100")
        with urllib.request.urlopen(url, timeout=60) as r:
            rows += [x["row"] for x in json.load(r)["rows"]]
        offset += 100
    return ({r["instance_id"]: r["patch"] for r in rows},
            {r["instance_id"]: r.get("test_patch", "") for r in rows})


def main() -> None:
    run_dir = Path(sys.argv[1])
    if len(sys.argv) > 3:
        gold = json.loads(Path(sys.argv[2]).read_text())
        tests = json.loads(Path(sys.argv[3]).read_text())
    else:
        gold, tests = fetch_patches()
    flagged = {}
    traj_paths = sorted((run_dir / "trajs").glob("*.traj.json"))
    for path in traj_paths:
        traj = json.loads(path.read_text())
        iid = traj["instance_id"]
        r = audit_traj(traj, gold.get(iid, ""), tests.get(iid, ""))
        if r["git_oracle"] or r["test_oracle"] or r["network"] or r["future_dates"]:
            flagged[iid] = r
    out = {"flagged": flagged, "n_flagged": len(flagged), "n_scanned": len(traj_paths)}
    (run_dir / "audit.json").write_text(json.dumps(out, indent=1))
    print(f"{out['n_flagged']}/{out['n_scanned']} flagged -> {run_dir / 'audit.json'}")
    sys.exit(1 if flagged else 0)


if __name__ == "__main__":
    main()
