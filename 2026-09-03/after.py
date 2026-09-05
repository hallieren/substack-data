"""The receipt: the offline eval set after harvesting. Merges the 08-26 full
run (14 cases × 5, stored verdicts, judge cache reused, zero new model calls)
with the harvested cases' runs (runs/harvest, N × 3) into one layered rate.

Writes analysis/after.md. The two halves have different verdict sources
(accept.py from issue text vs the human fix's tests); the table keeps them
in separate rows before the merged line.

Usage: uv run --project "$PICO" python after.py [runs/harvest] [--repeats 3]
"""
import json, math, sys
from pathlib import Path

HERE = Path(__file__).parent
OLD = HERE.parent / "2026-08-26"
sys.path.insert(0, str(HERE / "harness"))
import report as new_report  # noqa: E402  (this run's evaluate)


def wobble(p, n):
    return 1.96 * math.sqrt(max(p * (1 - p), 1e-9) / n) if n else 0.0


def old_verdicts():
    """Re-read the 08-26 run through its own harness (judge cache on disk)."""
    sys.path.insert(0, str(OLD / "harness"))
    import importlib
    for m in ("cases", "assertions", "stats", "traces", "judge"):
        sys.modules.pop(m, None)
    stats = importlib.import_module("stats")
    ev = stats.evaluate(OLD / "runs" / "full", 5)
    rows = []
    for cid, e in ev.items():
        for r in e["runs"]:
            rows.append((cid, e["case"]["severity_if_fail"], r["verdict"]))
    for m in ("cases", "assertions", "stats", "traces", "judge"):
        sys.modules.pop(m, None)
    sys.path.remove(str(OLD / "harness"))
    return rows


def main():
    args = sys.argv[1:]
    repeats = 3
    if "--repeats" in args:
        i = args.index("--repeats"); repeats = int(args[i + 1]); del args[i:i + 2]
    run_dir = Path(args[0]) if args else HERE / "runs" / "harvest"
    old = old_verdicts()
    new_ev = new_report.evaluate(run_dir, repeats)
    new = [(cid, "sev-2", r["verdict"]) for cid, e in new_ev.items() for r in e["runs"]]

    def rate(rows):
        v = [r for r in rows if r[2] != "invalid"]
        p = sum(r[2] == "pass" for r in v)
        return p, len(v), (p / len(v) if v else 0.0)

    L = ["# The eval set after harvesting", "", "| slice | pass | runs | rate |", "|---|---|---|---|"]
    for name, rows in (("08-26 seed set, 14 cases × 5 (accept.py from issue text)", old),
                       (f"harvested from production, {len(new_ev)} cases × {repeats} (human fix's tests)", new),
                       ("merged", old + new)):
        p, n, q = rate(rows)
        L.append(f"| {name} | {p} | {n} | {q:.0%} ± {wobble(q, n):.0%} |")
    L += ["", "## Harvested cases", "", "| case | verdicts | failing |", "|---|---|---|"]
    for cid, e in sorted(new_ev.items()):
        marks = " ".join({"pass": "✓", "fail": "✗", "invalid": "!"}[r["verdict"]] for r in e["runs"])
        fails = sorted({k for r in e["runs"] for k, c in r["checks"].items() if c["verdict"] == "fail"})
        L.append(f"| {cid} | {marks} | {', '.join(fails) or '—'} |")
    (HERE / "analysis" / "after.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
