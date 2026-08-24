#!/usr/bin/env python3
"""Sink first: deterministic checks over the 393 sealed pass patches.

Chapter 5 discipline: before writing any judge prompt, chase the judge out of
places it should never stand. Three conservative scans over each pass patch:

  1. tests_touched   - diff modifies a test file (red line: never judge, scan)
  2. debug_leftovers - added lines with print(/breakpoint()/pdb in non-test code
  3. size stats      - files touched, hunks, +/- lines (feeds sampling strata)

Outputs evidence/deterministic.json (per-instance) and prints a summary.
Pure stdlib, offline, deterministic: same inputs, same outputs.
"""
import json
import re
from collections import Counter
from pathlib import Path

RUN = Path("/Users/hannahren/Documents/pico/bench/runs/20260815-verified-sealed")
OUT = Path(__file__).resolve().parents[1] / "deterministic.json"

TEST_PATH = re.compile(r"(^|/)(tests?|testing)(/|_)|(_tests?\.py$)|(^|/)test_")
DEBUG_ADD = re.compile(r"^\+.*\b(print\(|breakpoint\(\)|pdb\.set_trace\(\))")


def patch_stats(patch: str) -> dict:
    files, cur = [], None
    adds = dels = hunks = 0
    test_files, debug_lines = [], []
    for line in patch.splitlines():
        if line.startswith("diff --git"):
            cur = line.split(" b/")[-1]
            files.append(cur)
            if TEST_PATH.search(cur):
                test_files.append(cur)
        elif line.startswith("@@"):
            hunks += 1
        elif line.startswith("+") and not line.startswith("+++"):
            adds += 1
            if cur and not TEST_PATH.search(cur) and DEBUG_ADD.match(line):
                debug_lines.append((cur, line[1:].strip()[:80]))
        elif line.startswith("-") and not line.startswith("---"):
            dels += 1
    return {
        "files": files,
        "n_files": len(files),
        "hunks": hunks,
        "added": adds,
        "removed": dels,
        "tests_touched": test_files,
        "debug_leftovers": debug_lines,
    }


def main():
    resolved = set(
        json.load(open(RUN / "eval_report.json"))["resolved_ids"]
    )
    diff_map = json.load(
        open("/Users/hannahren/Documents/substack-data/2026-08-16/analysis/difficulty.json")
    )
    rows = {}
    with open(RUN / "preds.jsonl") as f:
        for line in f:
            rec = json.loads(line)
            iid = rec["instance_id"]
            if iid not in resolved:
                continue
            st = patch_stats(rec["model_patch"])
            st["difficulty"] = diff_map.get(iid, "unknown")
            rows[iid] = st
    assert len(rows) == len(resolved), (len(rows), len(resolved))

    OUT.write_text(json.dumps(rows, indent=1, sort_keys=True))

    n = len(rows)
    tt = [i for i, r in rows.items() if r["tests_touched"]]
    dbg = [i for i, r in rows.items() if r["debug_leftovers"]]
    single = sum(1 for r in rows.values() if r["n_files"] == 1)
    sizes = sorted(r["added"] + r["removed"] for r in rows.values())
    diff_c = Counter(r["difficulty"] for r in rows.values())
    print(f"passes scanned: {n}")
    print(f"single-file patches: {single} ({single/n:.0%})")
    print(f"diff size lines p50/p90/max: {sizes[n//2]}/{sizes[int(n*0.9)]}/{sizes[-1]}")
    print(f"tests_touched: {len(tt)} -> {tt}")
    print(f"debug_leftovers: {len(dbg)} -> {dbg}")
    print("difficulty:", dict(diff_c))


if __name__ == "__main__":
    main()
