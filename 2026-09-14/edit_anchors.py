"""Edit-anchor audit over pico's sealed SWE-bench Verified run, zero model calls.

Companion to the article "Does Your Agent's Edit Fail Loud or Silent?".
Walks every stored trajectory, finds every edit_file call, and asks two
questions the paper (arXiv 2609.11957) leaves open:

1. How often does an agent edit a file whose line numbers its own earlier
   edits have already moved?  (the situation where a line-anchored edit
   format would land in the wrong place without an error)
2. How often does pico's content-anchored edit_file refuse an edit, and what
   does the agent do next?

pico's edit_file(path, old, new) replaces one exact occurrence of `old`.
It raises when `old` is absent or ambiguous, so every refusal is visible in
the trajectory as a tool result starting with "ValueError".

Usage:
    python edit_anchors.py [run_dir]
run_dir must contain trajs/*.traj.json (default: the 2026-08-16 sealed run).
Writes data/results.json, data/refusals.csv, data/shifts.csv.
"""
import csv
import glob
import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "2026-08-16" / "runs" / "20260815-sealed"
OUT = HERE / "data"
OUT.mkdir(exist_ok=True)

REFUSAL = re.compile(r"not found in|appears \d+ times in")


def calls_of(traj):
    """Flatten a pico trajectory into an ordered list of tool calls, each with its result."""
    pending = {}
    out = []
    for m in traj["messages"]:
        for c in m.get("content", []):
            kind = c.get("kind")
            if kind == "tool_call":
                args = c["arguments"] if isinstance(c["arguments"], dict) else {}
                rec = {"name": c["name"], "args": args, "id": c["id"], "result": None}
                pending[c["id"]] = rec
                out.append(rec)
            elif kind == "tool_result":
                rec = pending.get(c["call_id"])
                if rec is not None:
                    rec["result"] = str(c.get("content"))
    return out


def mentions(path, args):
    """Did a bash call look at this file (sed/cat/grep/head/tail) or touch it?"""
    cmd = args.get("command", "")
    return Path(path).name in cmd


def main():
    files = sorted(glob.glob(str(RUN / "trajs" / "*.traj.json")))
    if not files:
        sys.exit(f"no trajectories under {RUN}/trajs")

    n_edits = 0
    n_runs_with_edits = 0
    n_on_edited_file = 0
    n_after_own_shift = 0
    shifts = []
    refusals = []

    for f in files:
        traj = json.load(open(f))
        inst = traj["instance_id"]
        calls = calls_of(traj)
        shift = {}       # path -> cumulative line-count change from successful edits
        writes = {}      # path -> number of successful edit_file/write_file so far
        had_edit = False
        for i, c in enumerate(calls):
            if c["name"] == "write_file":
                p = c["args"].get("path")
                if c["result"] and not c["result"].startswith("ValueError"):
                    writes[p] = writes.get(p, 0) + 1
                    shift[p] = 0  # whole file rewritten, old line numbers meaningless anyway
                continue
            if c["name"] != "edit_file":
                continue
            had_edit = True
            n_edits += 1
            p = c["args"].get("path") or ""
            old, new = c["args"].get("old", ""), c["args"].get("new", "")
            if writes.get(p, 0) > 0:
                n_on_edited_file += 1
            if shift.get(p, 0) != 0:
                n_after_own_shift += 1
                shifts.append((inst, p.replace("/testbed/", ""), i, shift[p]))
            refused = c["result"] is not None and REFUSAL.search(c["result"]) is not None
            if refused:
                prior_reads = sum(
                    1 for q in calls[:i]
                    if (q["name"] == "read_file" and q["args"].get("path") == p)
                    or (q["name"] == "bash" and mentions(p, q["args"]))
                )
                nxt = calls[i + 1] if i + 1 < len(calls) else None
                nxt_desc = "end" if nxt is None else nxt["name"]
                # did the agent look at the file within its next two calls?
                reread = any(
                    (q["name"] == "read_file" and q["args"].get("path") == p)
                    or (q["name"] == "bash" and mentions(p, q["args"]) and re.search(r"sed -n|cat |grep|head|tail|python", q["args"].get("command", "")))
                    for q in calls[i + 1:i + 3]
                )
                later_ok = any(
                    q["name"] == "edit_file" and q["args"].get("path") == p
                    and q["result"] and not REFUSAL.search(q["result"])
                    for q in calls[i + 1:]
                )
                later_bash_patch = any(
                    q["name"] == "bash" and mentions(p, q["args"]) and re.search(r"sed -i|python|patch|>", q["args"].get("command", ""))
                    for q in calls[i + 1:]
                )
                refusals.append({
                    "instance": inst,
                    "call_index": i,
                    "path": p.replace("/testbed/", ""),
                    "reason": "ambiguous" if "appears" in c["result"] else "not_found",
                    "prior_writes_same_file": writes.get(p, 0),
                    "prior_looks_same_file": prior_reads,
                    "own_shift_lines": shift.get(p, 0),
                    "next_call": nxt_desc,
                    "reread_within_2": reread,
                    "later_edit_file_ok": later_ok,
                    "later_bash_patch": later_bash_patch,
                    "old_first_line": old.strip().splitlines()[0][:80] if old.strip() else "",
                })
            else:
                writes[p] = writes.get(p, 0) + 1
                shift[p] = shift.get(p, 0) + (new.count("\n") - old.count("\n"))
        if had_edit:
            n_runs_with_edits += 1

    results = {
        "run_dir": str(RUN),
        "trajectories": len(files),
        "trajectories_with_edit_file": n_runs_with_edits,
        "edit_file_calls": n_edits,
        "edits_on_file_agent_already_wrote": n_on_edited_file,
        "edits_after_own_line_shift": n_after_own_shift,
        "share_after_own_line_shift": round(n_after_own_shift / n_edits, 4),
        "own_shift_lines_median": statistics.median(abs(s[3]) for s in shifts) if shifts else None,
        "own_shift_lines_max": max(abs(s[3]) for s in shifts) if shifts else None,
        "refusals": len(refusals),
        "refusal_rate_per_edit": round(len(refusals) / n_edits, 4),
        "refusals_by_reason": dict(Counter(r["reason"] for r in refusals)),
        "refusals_with_prior_write_same_file": sum(1 for r in refusals if r["prior_writes_same_file"] > 0),
        "refusals_next_call": dict(Counter(r["next_call"] for r in refusals)),
        "refusals_reread_within_2": sum(1 for r in refusals if r["reread_within_2"]),
        "refusals_later_edit_file_ok": sum(1 for r in refusals if r["later_edit_file_ok"]),
        "refusals_recovered_any": sum(1 for r in refusals if r["later_edit_file_ok"] or r["later_bash_patch"]),
    }
    json.dump(results, open(OUT / "results.json", "w"), indent=2)
    with open(OUT / "refusals.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(refusals[0].keys()))
        w.writeheader()
        w.writerows(refusals)
    with open(OUT / "shifts.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["instance", "path", "call_index", "net_line_shift_from_own_earlier_edits"])
        w.writerows(shifts)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
