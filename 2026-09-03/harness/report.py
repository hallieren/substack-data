"""report — the replay rung's layered report. Zero model calls (no judge this
run: every declared assertion is deterministic).

Usage: cd ~/Documents/pico && uv run python <here>/report.py <run_dir> [--repeats N]"""

import json
import math
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from assertions import check_case  # noqa: E402
from cases import load_cases  # noqa: E402
from traces import load_traj  # noqa: E402

INVALID = ("container failed", "error", "wall clock", "world invalid")


def evaluate_run(case, run_dir, repeat):
    key = f"{case['id']}-r{repeat}"
    traj = load_traj(run_dir / "trajs" / f"{key}.traj.json")
    world = json.loads((run_dir / "world" / f"{key}.json").read_text())
    if world["status"].startswith(INVALID):
        return {"key": key, "case": case["id"], "repeat": repeat, "verdict": "invalid",
                "checks": {}, "status": world["status"]}
    checks = check_case(case, traj, world)
    verdict = "pass" if all(r["verdict"] == "pass" for r in checks.values()) else "fail"
    return {"key": key, "case": case["id"], "repeat": repeat, "verdict": verdict,
            "checks": checks, "status": world["status"]}


def evaluate(run_dir, repeats):
    out = {}
    for case in load_cases():
        runs = [evaluate_run(case, run_dir, r) for r in range(1, repeats + 1)
                if (run_dir / "trajs" / f"{case['id']}-r{r}.traj.json").exists()]
        if runs:
            out[case["id"]] = {"case": case, "runs": runs}
    return out


def wobble(p, n):
    return 1.96 * math.sqrt(max(p * (1 - p), 1e-9) / n) if n else 0.0


def main():
    args = sys.argv[1:]
    repeats = 1
    if "--repeats" in args:
        i = args.index("--repeats")
        repeats = int(args[i + 1])
        del args[i:i + 2]
    run_dir = Path(args[0]).resolve()
    ev = evaluate(run_dir, repeats)
    results = {json.loads(l)["key"]: json.loads(l) for l in (run_dir / "results.jsonl").read_text().splitlines() if l}

    all_runs = [r for e in ev.values() for r in e["runs"]]
    lines = ["# ch13 replay report — pico on 2026 production issues", ""]
    lines.append(f"run: `{run_dir.name}` · {len(ev)} cases · {repeats} run each (production serves "
                 f"every ticket once) · verdict = all declared assertions pass · ! = world invalid, excluded")
    lines.append("")
    fails_total = Counter()
    for kind, title in (("fix", "fix expected (reference = the human fix's tests)"),
                        ("nofix", "no fix expected (maintainers ruled NOT_PLANNED; verdict = escalated)")):
        group = [(cid, e) for cid, e in sorted(ev.items()) if e["case"]["kind"] == kind]
        if not group:
            continue
        valid = [r for _, e in group for r in e["runs"] if r["verdict"] != "invalid"]
        n_pass = sum(r["verdict"] == "pass" for r in valid)
        p = n_pass / len(valid) if valid else 0.0
        lines.append(f"## {title} — {n_pass}/{len(valid)} pass ({p:.0%} ± {wobble(p, len(valid)):.0%})")
        lines.append("")
        lines.append("| case | repo | verdict | F2P green | patch | failing assertions | cost | s |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for cid, e in group:
            for r in e["runs"]:
                row = results.get(r["key"], {})
                fails = [name for name, c in r["checks"].items() if c["verdict"] == "fail"]
                fails_total.update(fails)
                mark = {"pass": "✓", "fail": "✗", "invalid": "!"}[r["verdict"]]
                lines.append(f"| {cid} | {e['case']['repo'].split('/')[1]} | {mark} | "
                             f"{row.get('f2p_green', '?')}/{row.get('f2p_total', '?')} | {row.get('patch_bytes', '?')}B | "
                             f"{', '.join(fails) or '—'} | ${row.get('cost_usd', 0):.3f} | {row.get('seconds', '?')} |")
        lines.append("")
    lines.append("**Failing assertions, tallied**: " + (", ".join(f"{k}×{v}" for k, v in fails_total.most_common()) or "none"))
    lines.append("")
    budget = [r["key"] for r in all_runs if r["status"].startswith("stopped after")]
    if budget:
        lines.append(f"**Budget deaths** ({len(budget)}): " + ", ".join(sorted(budget)))
        lines.append("")
    alarms = [f"{r['key']} ({r['status'][:60]})" for r in all_runs if r["verdict"] == "invalid"]
    if alarms:
        lines.append(f"**Deviation alarms** (excluded): " + "; ".join(alarms))
        lines.append("")
    cost = sum(results[k].get("cost_usd", 0) for k in results)
    lines.append(f"**Cost**: ${cost:.2f} over {len(results)} runs")
    report = "\n".join(lines)
    (run_dir / "report.md").write_text(report + "\n")
    print(report)


if __name__ == "__main__":
    main()
