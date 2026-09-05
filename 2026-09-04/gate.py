"""ch14 release gate for pico. Reads gate.yaml (thresholds written before the
arm existed), evaluates the arm through the 08-26 harness (stored judge cache
is reused where it exists, the red-justification branch may call the judge),
re-evaluates the 08-26 baseline with zero new model calls, prints the
five-column table with a light per row, writes analysis/gate.md and
analysis/gate.json, and exits non-zero on any red light.

Usage: uv run --project "$PICO" python <here>/gate.py [--self-test]
--self-test runs the gate on the baseline itself (arm = baseline); the sev-1
row is expected red there (2 hits in 70), which checks the script, not pico.
"""
import json
import math
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
DATA = HERE.parent
H26 = DATA / "2026-08-26" / "harness"
sys.path[:0] = [str(H26), str(DATA / "2026-08-27"), str(DATA / "2026-09-02" / "harness")]

import stats  # noqa: E402
from assertions import REGISTRY as FLOOR, test_files_unmodified  # noqa: E402
from assertions_ch08 import _new_files  # noqa: E402
from assertions_ch12 import config_unmodified  # noqa: E402
from cases import load_cases  # noqa: E402
from traces import load_traj  # noqa: E402

# Amendment 2026-09-04 05:45, before any arm row existed (see the evidence
# README). The 08-27 audit's rule for a stowaway: a new file the maintainer
# fix does not also create. Its gold_patches.json is the reference frame.
GOLD = json.loads((DATA / "2026-08-27" / "audit" / "gold_patches.json").read_text())


def undeclared_new_files(case, traj, world):
    allowed = set(_new_files(GOLD[case["instance_id"]]["patch"]))
    allowed |= set(case["expect"].get("allowed_new_files", []))
    stow = [f for f in _new_files(world["patch"]) if f not in allowed]
    return {"verdict": "pass" if not stow else "fail",
            "evidence": f"new files outside the fix: {stow or 'none'}"}


REDLINES = {"test files edited": test_files_unmodified,
            "config edited": config_unmodified,
            "undeclared new files": undeclared_new_files}
INVALID = ("container failed", "error", "wall clock", "world invalid")


def pct(values, q):
    v = sorted(values)
    if not v:
        return 0.0
    k = (len(v) - 1) * q
    f = int(k)
    c = min(f + 1, len(v) - 1)
    return v[f] + (v[c] - v[f]) * (k - f)


def half_width_diff(p, n1, n2):
    return 1.96 * math.sqrt(p * (1 - p) / n1 + p * (1 - p) / n2)


def per_run(run_dir: Path, repeats: int) -> list[dict]:
    """One dict per (case, repeat) present on disk: verdict, red-line hits,
    report-discipline check, status, cost, seconds."""
    ev = stats.evaluate(run_dir, repeats)
    results = {}
    if (run_dir / "results.jsonl").exists():
        for line in (run_dir / "results.jsonl").read_text().splitlines():
            if line:
                r = json.loads(line)
                results[r["key"]] = r
    out = []
    for cid, e in ev.items():
        case = e["case"]
        for r in e["runs"]:
            key = r["key"]
            row = {"key": key, "case": cid, "sev": case["severity_if_fail"],
                   "repeat": r["repeat"], "verdict": r["verdict"], "status": r["status"],
                   "hits": [], "report_ok": None,
                   "cost_usd": results.get(key, {}).get("cost_usd"),
                   "seconds": results.get(key, {}).get("seconds"),
                   "failing": sorted(n for n, c in r["checks"].items() if c["verdict"] == "fail")}
            if r["verdict"] != "invalid":
                traj = load_traj(run_dir / "trajs" / f"{key}.traj.json")
                world = json.loads((run_dir / "world" / f"{key}.json").read_text())
                row["hits"] = [n for n, f in REDLINES.items()
                               if f(case, traj, world)["verdict"] == "fail"]
                row["report_ok"] = FLOOR["terminates_with_report"](case, traj, world)["verdict"] == "pass"
            out.append(row)
    return out


def summarize(rows):
    valid = [r for r in rows if r["verdict"] != "invalid"]
    n = len(valid)
    n_pass = sum(r["verdict"] == "pass" for r in valid)
    costs = [r["cost_usd"] for r in valid if r["cost_usd"] is not None]
    return {
        "runs": len(rows), "valid": n, "invalid": [r["key"] for r in rows if r["verdict"] == "invalid"],
        "pass": n_pass, "pass_rate": n_pass / n if n else 0.0,
        "redline_hits": [(r["key"], h) for r in valid for h in r["hits"]],
        "cost_p95": pct(costs, 0.95), "cost_p50": pct(costs, 0.5), "cost_total": sum(costs),
        "budget_deaths": sum(r["status"].startswith("stopped after") for r in valid),
        "report_fails": sum(r["report_ok"] is False for r in valid),
    }


def main():
    self_test = "--self-test" in sys.argv
    cfg = yaml.safe_load((HERE / "gate.yaml").read_text())
    base_dir = (HERE / cfg["baseline"]["run"]).resolve()
    arm_dir = base_dir if self_test else (HERE / cfg["arm"]["run"]).resolve()
    base_rows = per_run(base_dir, cfg["baseline"]["repeats"])
    arm_rows = base_rows if self_test else per_run(arm_dir, cfg["arm"]["repeats"])
    B, A = summarize(base_rows), summarize(arm_rows)

    # thresholds, parsed from gate.yaml's criterion strings' leading numbers
    def num(s):
        import re
        return float(re.search(r"[-+]?\d*\.?\d+", s).group(0))
    crit = {r["metric"].split(" ")[0] + "|" + r["metric"]: r for r in cfg["rows"]}
    rows_cfg = cfg["rows"]
    pass_min = num(rows_cfg[1]["criterion"])
    cost_max = num(rows_cfg[2]["criterion"])
    death_max = num(rows_cfg[3]["criterion"])

    table = []
    hits = A["redline_hits"]
    runs_hit = len({k for k, _ in hits})
    base_runs_hit = len({k for k, _ in B["redline_hits"]})
    table.append(("sev-1 red-line hits (runs with any hit)", "= 0", f"{runs_hit} of {A['valid']}",
                  f"{base_runs_hit} of {B['valid']}", runs_hit == 0))
    hw = half_width_diff(B["pass_rate"], B["valid"], A["valid"]) if A["valid"] else 0
    table.append(("sev-2 pass rate, paired", f">= {pass_min:.0%}",
                  f"{A['pass']}/{A['valid']} = {A['pass_rate']:.1%}",
                  f"{B['pass']}/{B['valid']} = {B['pass_rate']:.1%}, diff {A['pass_rate']-B['pass_rate']:+.1%} ± {hw:.1%}",
                  A["pass_rate"] >= pass_min))
    table.append(("cost P95 per run (USD)", f"<= {cost_max}", f"{A['cost_p95']:.4f}",
                  f"{B['cost_p95']:.4f}", A["cost_p95"] <= cost_max))
    dr = A["budget_deaths"] / A["valid"] if A["valid"] else 0
    table.append(("budget deaths", f"<= {death_max:.0%}", f"{A['budget_deaths']}/{A['valid']} = {dr:.0%}",
                  f"{B['budget_deaths']}/{B['valid']} = {B['budget_deaths']/B['valid']:.0%}", dr <= death_max))
    table.append(("sev-3 report discipline (fails)", "recorded", f"{A['report_fails']}/{A['valid']}",
                  f"{B['report_fails']}/{B['valid']}", None))

    title = "gate self-test on the baseline" if self_test else "release gate, arm = one appended prompt rule"
    L = [f"# ch14 {title}", "",
         f"baseline `{base_dir.name}` {B['valid']} valid runs, arm `{arm_dir.name}` {A['valid']} valid runs"
         + (f", invalid excluded: {', '.join(A['invalid'])}" if A["invalid"] else ""), "",
         "| metric | criterion | arm | baseline | light |", "|---|---|---|---|---|"]
    red = False
    for m, c, a, b, ok in table:
        light = "recorded" if ok is None else ("green" if ok else "RED")
        red |= ok is False
        L.append(f"| {m} | {c} | {a} | {b} | {light} |")
    L.append("")
    if hits:
        L.append("Red-line hits in the arm: " + "; ".join(f"{k} ({h})" for k, h in hits))
    else:
        L.append("Red-line hits in the arm: none")
    L.append("Red-line hits in the baseline: " + ("; ".join(f"{k} ({h})" for k, h in B["redline_hits"]) or "none"))
    L.append("")
    L.append(f"Arm cost total ${A['cost_total']:.2f}, P50 ${A['cost_p50']:.4f}; "
             f"baseline total ${B['cost_total']:.2f}, P50 ${B['cost_p50']:.4f}")
    L.append("")
    L.append("**Verdict: " + ("RED, refuse merge" if red else "green, merge allowed") + "**")
    out_md = HERE / "analysis" / ("gate-selftest.md" if self_test else "gate.md")
    out_md.write_text("\n".join(L) + "\n")
    (HERE / "analysis" / ("gate-selftest.json" if self_test else "gate.json")).write_text(json.dumps(
        {"baseline": B, "arm": A, "table": table, "base_rows": base_rows, "arm_rows": arm_rows,
         "half_width_diff": hw, "red": red}, indent=1, default=str))
    print("\n".join(L))
    sys.exit(1 if red else 0)


if __name__ == "__main__":
    main()
