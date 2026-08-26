"""report — ch02's discipline: layered by sev, verdict sources visible, never
only the average.

Usage: cd ~/Documents/pico && uv run python <here>/report.py <run_dir> [--repeats N]"""

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from stats import evaluate, flips, wobble  # noqa: E402


def main() -> None:
    args = sys.argv[1:]
    repeats = 5
    if "--repeats" in args:
        i = args.index("--repeats")
        repeats = int(args[i + 1])
        del args[i:i + 2]
    run_dir = Path(args[0]).resolve()
    ev = evaluate(run_dir, repeats)

    lines = ["# ch07 harness report — pico seed eval set", ""]
    lines.append(f"run: `{run_dir.name}` · {len(ev)} cases · repeats per case as shown · "
                 "verdict = all declared assertions pass · ! = world invalid, excluded")
    lines.append("")
    for sev in ("sev-1", "sev-2", "sev-3"):
        rows = [(cid, e) for cid, e in sorted(ev.items())
                if e["case"]["severity_if_fail"] == sev]
        if not rows:
            continue
        n_runs = sum(r["verdict"] != "invalid" for _, e in rows for r in e["runs"])
        n_pass = sum(r["verdict"] == "pass" for _, e in rows for r in e["runs"])
        p = n_pass / n_runs if n_runs else 0.0
        lines.append(f"## {sev} — {n_pass}/{n_runs} case-runs pass "
                     f"({p:.0%} ± {wobble(p, n_runs):.0%})")
        lines.append("")
        lines.append("| case | state | verdicts (r1..) | source | failing assertion (mode) |")
        lines.append("|---|---|---|---|---|")
        for cid, e in rows:
            verdicts = " ".join({"pass": "✓", "fail": "✗", "invalid": "!"}[r["verdict"]]
                                for r in e["runs"])
            src = "+judge" if any("judge" in r["sources"] for r in e["runs"]) else "assertions"
            fails = Counter(name for r in e["runs"] for name, c in r["checks"].items()
                            if c["verdict"] == "fail")
            top = ", ".join(f"{k}×{v}" for k, v in fails.most_common(2)) or "—"
            lines.append(f"| {cid} | {e['case']['coverage_state']} | {verdicts} | {src} | {top} |")
        lines.append("")

    fl = flips(ev)
    lines.append(f"**Flip list** ({len(fl)} of {len(ev)} cases change verdict across repeats): "
                 + (", ".join(fl) or "none"))
    lines.append("")
    budget = [r["key"] for e in ev.values() for r in e["runs"]
              if r["status"].startswith("stopped after")]
    if budget:
        lines.append(f"**Budget deaths** ({len(budget)} runs ended by turn/spend cap, "
                     "still judged on their world's final state): " + ", ".join(sorted(budget)))
        lines.append("")
    alarms = [r["key"] for e in ev.values() for r in e["runs"] if r["status"].startswith(
        ("container failed", "error", "wall clock", "world invalid"))]
    if alarms:
        lines.append(f"**Deviation alarms** (world never reached a judgeable state, "
                     "excluded from verdicts): " + ", ".join(sorted(alarms)))
    report = "\n".join(lines)
    (run_dir / "report.md").write_text(report + "\n")
    print(report)


if __name__ == "__main__":
    main()
