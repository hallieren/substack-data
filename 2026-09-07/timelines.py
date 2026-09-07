"""Timelines of the runs the hardcoded rule flagged: when the test tree was
first written, whether and when it was restored, how the run ended, and what
was left in the diff. Feeds the reader's coding and the article's evidence
figure. Zero model calls.

Usage: python timelines.py -> analysis/borrow-timelines.json (+ stdout)
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent
sys.path.insert(0, str(HERE))
import testtree  # noqa: E402

RUNS = {"08-26": DATA / "2026-08-26/runs/full", "09-04": DATA / "2026-09-04/runs/variant",
        "09-03": DATA / "2026-09-03/runs/harvest"}


def assistant_steps(traj):
    return [i for i, m in enumerate(traj["messages"]) if m["role"] == "assistant"]


def restore_events(traj, paths, after):
    """Later bash calls that remove or restore any of the written paths."""
    out = []
    for i, m in enumerate(traj["messages"]):
        if i <= after or m["role"] != "assistant":
            continue
        for b in m["content"]:
            if b["kind"] != "tool_call" or b["name"] != "bash":
                continue
            c = b["arguments"].get("command", "")
            for p in paths:
                base = p.split("/")[-1]
                if re.search(rf"\brm\b[^;&|]*{re.escape(base)}", c) or re.search(rf"git (checkout|restore)[^;&|]*{re.escape(base)}", c) \
                        or re.search(rf"\bcp\b\s+/tmp/\S*{re.escape(base)}\S*\s+\S*{re.escape(base)}", c):
                    out.append({"msg": i, "cmd": c[:140].replace("\n", " ")})
                    break
    return out


def main():
    pool = json.loads((HERE / "analysis/pool.json").read_text())
    rows = []
    for r in pool["pool"]:
        if not r["attempts"]:
            continue
        batch, key = r["key"].split("/")
        run_dir = RUNS[batch]
        traj = json.loads((run_dir / "trajs" / f"{key}.traj.json").read_text())
        events = testtree.scan(traj)
        paths = sorted({p for e in events for p in e["paths"] if "__pycache__" not in p})
        steps = assistant_steps(traj)
        first = events[0]["msg"]
        # the assistant text right before the first write, its stated intent
        intent = ""
        for m in reversed(traj["messages"][:first + 1]):
            if m["role"] == "assistant":
                txt = "".join(b["text"] for b in m["content"] if b["kind"] == "text").strip()
                if txt:
                    intent = txt[-400:]
                    break
        restores = restore_events(traj, paths, first)
        rows.append({"run": r["key"], "case": r["case"], "status": r["status"], "verdict": r["verdict"],
                     "steps": len(steps), "first_write_step": steps.index(first) + 1 if first in steps else None,
                     "first_write_msg": first, "writes": len(events), "paths": paths,
                     "restore_steps": [steps.index(e["msg"]) + 1 for e in restores if e["msg"] in steps],
                     "restores": restores, "tests_in_diff": r["tests_in_diff"], "intent_text": intent})
    (HERE / "analysis/borrow-timelines.json").write_text(json.dumps(rows, indent=1))
    for x in rows:
        print(f"\n== {x['run']} | {x['status'][:40]} | verdict {x['verdict']} | steps {x['steps']}")
        print(f"   first write at step {x['first_write_step']} (msg {x['first_write_msg']}), {x['writes']} writes, paths {x['paths']}")
        print(f"   restores at steps {x['restore_steps']}: {[e['cmd'][:90] for e in x['restores']]}")
        print(f"   left in diff: {x['tests_in_diff'] or 'nothing'}")
        print(f"   intent: {x['intent_text'][-250:].replace(chr(10),' ')}")


if __name__ == "__main__":
    main()
