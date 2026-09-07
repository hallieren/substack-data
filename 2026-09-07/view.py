"""Compact, human-readable view of one pico trajectory for trace reading.
Prints every assistant text in full, each tool call's head, and each tool
result's head, with message indexes, so a reader can code first_bad_step
without paging through 300 KB of JSON. Read-only.

Usage: python view.py <traj.json> [--result-chars 240] [--call-chars 200]
       [--around <msg> --span 8] [--tail 12]   window instead of the whole run
"""
import json
import sys


def main():
    args = sys.argv[1:]
    rc = int(args[args.index("--result-chars") + 1]) if "--result-chars" in args else 240
    cc = int(args[args.index("--call-chars") + 1]) if "--call-chars" in args else 200
    path = [a for a in args if a.endswith(".json")][0]
    around = int(args[args.index("--around") + 1]) if "--around" in args else None
    span = int(args[args.index("--span") + 1]) if "--span" in args else 8
    tail = int(args[args.index("--tail") + 1]) if "--tail" in args else 0
    t = json.load(open(path))
    n = len(t["messages"])
    keep = set(range(n))
    if around is not None or tail:
        keep = set()
        if around is not None:
            keep |= set(range(max(0, around - span), min(n, around + span + 1)))
        if tail:
            keep |= set(range(max(0, n - tail), n))
    print(f"# {t.get('instance_id')} | exit: {t['info'].get('exit_status')} | messages: {len(t['messages'])}")
    for i, m in enumerate(t["messages"]):
        if m["role"] == "system" or i not in keep:
            continue
        for b in m["content"]:
            k = b["kind"]
            if k == "text":
                txt = b["text"].strip()
                if not txt:
                    continue
                if m["role"] == "user" and i <= 1:
                    print(f"[{i} task] {txt[:600]}...")
                else:
                    print(f"[{i} {m['role']}] {txt}")
            elif k == "tool_call":
                a = b["arguments"]
                if b["name"] == "bash":
                    head = a.get("command", "")
                elif b["name"] in ("write_file", "edit_file"):
                    head = a.get("path", "") + (" | old: " + a.get("old", "")[:80] + " | new: " + a.get("new", "")[:80] if b["name"] == "edit_file" else f" ({len(a.get('content',''))} chars)")
                else:
                    head = json.dumps(a)
                head = head.replace("\n", "⏎")
                print(f"[{i} call] {b['name']}: {head[:cc]}")
            elif k == "tool_result":
                out = str(b["content"]).replace("\n", "⏎")
                flag = " ERROR" if b.get("is_error") else ""
                print(f"[{i} result{flag}] {out[:rc]}")


if __name__ == "__main__":
    main()
