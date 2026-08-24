"""Coverage matrix for pico's seed eval set: failure mode × severity × coverage_state.

Migrated from the book's labs/ch04/coverage.py; the support world's persona axis
is replaced by the coding world's test-coverage-state axis per the ch04 migration box.
An empty cell is not a sin, an unsigned one is.

Usage: python coverage.py [cases dir, default ./cases]
"""
import glob
import os
import sys

STATES = ["green", "conflicting", "uncovered", "doomed"]


def load(path):
    c = {}
    for line in open(path):
        if line.startswith(("  ", "\t")) or ":" not in line:
            continue
        k, v = line.split(":", 1)
        c[k.strip()] = v.split("#")[0].strip()
    return c


def main(path):
    files = sorted(glob.glob(os.path.join(path, "*.yaml")))
    assert files, f"no case files in {path}"
    rows, holdout = {}, 0
    for f in files:
        c = load(f)
        holdout += c.get("holdout") == "true"
        s = c["coverage_state"]
        for m in c["failure_modes"].strip("[]").split(", "):
            r = rows.setdefault(m, {"sev": set(), "n": {q: 0 for q in STATES}})
            r["sev"].add(c.get("severity_if_fail", "sev-3"))
            r["n"][s] += 1
    print(f"Coverage matrix: {path} ({len(files)} cases, {holdout} holdout; "
          "one case can carry several modes, counts go by mode row)\n")
    w = max(len(m) for m in rows) + 2
    print("  " + "failure mode".ljust(w) + "sev".ljust(13)
          + "".join(s.ljust(13) for s in STATES) + "total")
    for m in sorted(rows, key=lambda m: (min(rows[m]["sev"]), m)):
        r = rows[m]
        print("  " + m.ljust(w) + "/".join(sorted(r["sev"])).ljust(13)
              + "".join(str(r["n"][s]).ljust(13) for s in STATES)
              + str(sum(r["n"].values())))
    empties = [(m, s) for m in sorted(rows) for s in STATES if rows[m]["n"][s] == 0]
    print(f"\nEmpty-cell list ({len(empties)} cells; rule each \"fill\" or "
          "\"reasoned empty\", log in the annotation bar):")
    for m, s in empties:
        print(f"  - {m} × {s}")
    sev1 = sorted(m for m in rows if "sev-1" in rows[m]["sev"])
    print("\nsev-1 check: " + ", ".join(
        f"{m}({sum(rows[m]['n'].values())} cases)" for m in sev1))
    print("Reminder: this table only sees modes with existing cases; a mode in "
          "your atlas that never appears here is an entire missing row.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else
         os.path.join(os.path.dirname(os.path.abspath(__file__)), "cases"))
