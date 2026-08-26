#!/usr/bin/env python3
"""Merge the 2026-08-24 judge's 3 published votes with votes 4-5 (this folder);
print the 5-vote split rates cited in the 2026-08-25 post."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PUB = HERE.parent / "2026-08-24" / "judge" / "judge-verdicts.jsonl"
NEW = HERE / "judge-verdicts-45.jsonl"

rows = [json.loads(l) for l in PUB.read_text().splitlines()]
rows += [json.loads(l) for l in NEW.read_text().splitlines()]

by = {}
for r in rows:
    by.setdefault(r["instance_id"], []).append(r)

split_overall, split_dim = [], []
for iid, rs in sorted(by.items()):
    rs.sort(key=lambda r: r["run"])
    assert len(rs) == 5, (iid, len(rs))
    if len(set(r["verdict"] for r in rs)) > 1:
        split_overall.append(iid)
    dims = {}
    for d in ("root-cause", "sibling-coverage", "verification-substance", "scope-discipline"):
        vals = [r["dims"].get(d) for r in rs]
        if len(set(vals)) > 1:
            dims[d] = vals
    if dims:
        split_dim.append((iid, dims))

print(f"cases: {len(by)}")
print(f"overall verdict split: {len(split_overall)}/16  {split_overall}")
print(f"any-dimension split:   {len(split_dim)}/16")
for iid, dims in split_dim:
    print(f"  {iid}: {dims}")
print("\nper-case votes (runs 1-5):")
for iid, rs in sorted(by.items()):
    print(f"  {iid}: {[r['verdict'] for r in sorted(rs, key=lambda r: r['run'])]}")
