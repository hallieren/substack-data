#!/usr/bin/env python3
"""Build the judge-calibration sample: stratified by difficulty, hand-thickened
at the rare hard end, plus one deterministic-flag enrichment case.

Strata over the 393 passes (difficulty = SWE-bench Verified human-time annotation):
  >4 hours      : 1 of 1    (all of it; single-digit stratum, read, don't ratio)
  1-4 hours     : 6 of 20   (hand-thickened far above its natural share)
  15 min - 1 hour: 5 of 209
  <15 min fix   : 3 of 163
  enrichment    : django__django-11734 (the tests_touched flag)

Total 16. Fixed seed; rerunning reproduces the same sample.
For each case, writes sample/<id>/{issue.md,patch.diff,digest.md} and a blind
label sheet at blind-sheet.md with empty cells (Hallie fills; no judge output
appears anywhere in this directory).
"""
import json
import random
import re
from pathlib import Path

EV = Path(__file__).resolve().parents[1]
RUN = Path("/Users/hannahren/Documents/pico/bench/runs/20260815-verified-sealed")
SEED = 20260824
QUOTA = {">4 hours": 1, "1-4 hours": 6, "15 min - 1 hour": 5, "<15 min fix": 3}
ENRICH = ["django__django-11734"]
TRUNC_RESULT = 700  # chars kept from each tool result (head+tail split)


def flat(content):
    if isinstance(content, list):
        out = []
        for p in content:
            out.append(p if isinstance(p, str) else p)
        return out
    return [content or ""]


def digest_trace(traj_path: Path) -> str:
    d = json.loads(traj_path.read_text())
    lines = [f"# Trace digest: {d['instance_id']} ({len(d['messages'])} messages)", ""]
    step = 0
    for m in d["messages"]:
        role = m["role"]
        if role == "system":
            continue
        for part in flat(m.get("content")):
            if isinstance(part, dict) and part.get("kind") == "tool_call":
                step += 1
                args = json.dumps(part.get("arguments", {}), ensure_ascii=False)
                if len(args) > 500:
                    args = args[:400] + f" …[{len(args)-400} ch omitted]"
                lines.append(f"[step {step}] CALL {part.get('name')}: {args}")
            elif isinstance(part, dict) and part.get("kind") == "tool_result":
                c = str(part.get("content", ""))
                if len(c) > TRUNC_RESULT:
                    h = TRUNC_RESULT // 2
                    c = c[:h] + f" …[{len(c)-TRUNC_RESULT} ch omitted]… " + c[-h:]
                lines.append("  RESULT: " + c.replace("\n", "\n  | "))
            elif isinstance(part, str) and part.strip():
                txt = part.strip()
                if len(txt) > 1200:
                    txt = txt[:1000] + f" …[{len(txt)-1000} ch omitted]"
                lines.append(f"({role} says) {txt}")
    return "\n".join(lines)


def main():
    det = json.loads((EV / "deterministic.json").read_text())
    rng = random.Random(SEED)
    by_diff = {}
    for iid, row in sorted(det.items()):
        by_diff.setdefault(row["difficulty"], []).append(iid)

    sample = []
    for diff, k in QUOTA.items():
        pool = [i for i in by_diff.get(diff, []) if i not in ENRICH]
        picks = pool if len(pool) <= k else rng.sample(pool, k)
        for iid in picks:
            sample.append({"instance_id": iid, "stratum": diff, "why": "stratified"})
    for iid in ENRICH:
        sample.append({
            "instance_id": iid,
            "stratum": det[iid]["difficulty"],
            "why": "enrichment: tests_touched deterministic flag",
        })

    issues = {
        r["instance_id"]: r["problem_statement"]
        for r in json.load(open(
            "/Users/hannahren/Documents/substack-data/2026-08-16/scripts/instances_verified.json"))
    }
    patches = {}
    with open(RUN / "preds.jsonl") as f:
        for line in f:
            r = json.loads(line)
            patches[r["instance_id"]] = r["model_patch"]

    sdir = EV / "sample"
    for row in sample:
        iid = row["instance_id"]
        cdir = sdir / iid
        cdir.mkdir(parents=True, exist_ok=True)
        (cdir / "issue.md").write_text(issues[iid])
        (cdir / "patch.diff").write_text(patches[iid])
        (cdir / "digest.md").write_text(digest_trace(RUN / "trajs" / f"{iid}.traj.json"))

    (EV / "sample-manifest.json").write_text(json.dumps(sample, indent=1))

    sheet = [
        "# Blind label sheet — ch05 judge calibration",
        "",
        "Read order: issue.md → patch.diff → digest.md, forward only.",
        "Per dimension: `ok` / `flaw` / `unclear`. Overall: `pass` / `concern` / `unclear`.",
        "Aggregation rule: any dimension `flaw` → overall `concern`. Do not average.",
        "Rubric with anchors: ../rubric.md. Do not open anything under judge/ until this sheet is complete.",
        "",
        "| instance_id | stratum | D1 root-cause | D2 sibling-coverage | D3 verification-substance | D4 scope-discipline | overall | notes |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in sample:
        sheet.append(f"| {row['instance_id']} | {row['stratum']} |  |  |  |  |  |  |")
    (EV / "blind-sheet.md").write_text("\n".join(sheet) + "\n")

    for row in sample:
        iid = row["instance_id"]
        d = det[iid]
        print(f"{iid:45s} {row['stratum']:16s} files={d['n_files']} +{d['added']}/-{d['removed']} {row['why']}")


if __name__ == "__main__":
    main()
